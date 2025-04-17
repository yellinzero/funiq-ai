# services/account_service.py
import secrets

from fastapi import Request, status
from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.account.schemas import TenantResponse
from app.auth.schemas import (
    ActivateAccountVerifyRequest,
    ForgotPasswordRequest,
    LoginRequest,
    OAuthLoginRequest,
    ResetPasswordRequest,
    SignupRequest,
    SignupVerifyRequest,
)
from app.core.errors import AccountErrorCode, CommonErrorCode, FuniqAIError
from app.core.models.account import (
    Account,
    AccountStatus,
    OAuthProvider,
    Tenant,
    TenantInvite,
    TenantInviteStatus,
    TenantUserRole,
    User,
)
from infrastructure import RedisRateLimiter
from tasks.email_tasks import (
    send_activate_account_email_task,
    send_reset_password_verification_email_task,
    send_signup_verification_email_task,
)
from utils.common.datetime import utcnow
from utils.security import (
    AccountTokenManager,
    AccountTokenType,
    create_token_pair,
    get_account_id_from_request,
    invalidate_refresh_token,
)

token_manager = AccountTokenManager()


class AccountService:
    """Account service for managing user accounts"""

    # Rate limiters
    reset_password_limit = RedisRateLimiter(
        prefix="reset_password_redis_rate_limit", max_attempts=1, time_window=60 * 1
    )
    signup_email_verification_limit = RedisRateLimiter(
        prefix="signup_email_verification_rate_limit", max_attempts=1, time_window=60 * 1
    )
    activate_account_limit = RedisRateLimiter(prefix="activate_account_rate_limit", max_attempts=1, time_window=60 * 1)
    LOGIN_MAX_ERROR_LIMITS = 5

    # region Account Registration
    @staticmethod
    async def signup(session: AsyncSession, payload: SignupRequest, request: Request) -> str:
        """Register a new account."""
        logger.info(f"Starting signup process for email: {payload.email}")

        # Check if the email/name is already registered
        result = await session.execute(
            Account.select().where(or_(Account.email == payload.email, Account.name == payload.name))
        )

        existing_account: Account | None = result.scalars().one_or_none()
        if existing_account:
            if existing_account.email == payload.email:
                logger.warning(f"Signup failed - email already registered: {payload.email}")
                raise AccountErrorCode.EMAIL_ALREADY_REGISTERED.exception(
                    data={"email": payload.email}, status_code=status.HTTP_400_BAD_REQUEST
                )
            elif existing_account.name == payload.name:
                logger.warning(f"Signup failed - name already registered: {payload.name}")
                raise AccountErrorCode.NAME_ALREADY_REGISTERED.exception(
                    data={"name": payload.name}, status_code=status.HTTP_400_BAD_REQUEST
                )

        # Check invite code if provided
        invite = None
        if payload.invite_code:
            result = await session.execute(
                select(TenantInvite).where(
                    TenantInvite.code == payload.invite_code, TenantInvite.status == TenantInviteStatus.PENDING
                )
            )
            invite = result.scalars().one_or_none()
            if not invite or (invite.expires_at and invite.expires_at < utcnow().replace(tzinfo=None)):
                raise AccountErrorCode.INVALID_INVITE_CODE.exception(
                    data={"invite_code": payload.invite_code}, status_code=status.HTTP_400_BAD_REQUEST
                )

        # Create new account with appropriate status
        account = Account(
            name=payload.name,
            email=payload.email,
            language=request.state.language,
            status=AccountStatus.PENDING,
            last_login_ip=request.client.host,
            last_login_tenant_id=invite.tenant_id if invite else None,
        )

        account.set_password(payload.password)
        await account.save(session)

        # If invite exists, create user in tenant and mark invite as used
        if invite:
            user = User(
                account_id=account.id, tenant_id=invite.tenant_id, role=TenantUserRole.MEMBER, invite_code=invite.code
            )
            await user.save(session)

            invite.status = TenantInviteStatus.USED
            invite.used_at = utcnow().replace(tzinfo=None)
            await invite.save(session)

            # Set last login tenant
            account.last_login_tenant_id = invite.tenant_id
            await account.save(session)

        # Commit account creation
        await session.commit()
        logger.info(f"Successfully created new account for: {payload.email}")

        # For normal signup, send verification email
        token = await AccountService.send_sign_up_verification_email(account, request)
        return token

    @staticmethod
    async def sign_up_email_verify(
        session: AsyncSession, payload: SignupVerifyRequest, request: Request
    ) -> tuple[str, str, str]:
        """Verify the email using the provided verification code."""
        # Verify token and code
        token_data = await token_manager.get_signup_email_verification_data(token=payload.token)
        if not token_data:
            raise CommonErrorCode.EMAIL_VERIFICATION_CODE_EXPIRED.exception(status_code=status.HTTP_400_BAD_REQUEST)

        email = token_data.get("email")
        if token_data.get("code") != payload.code:
            raise CommonErrorCode.INVALID_VERIFICATION_CODE.exception(
                data={"email": email}, status_code=status.HTTP_400_BAD_REQUEST
            )

        # Find account
        result = await session.execute(Account.select().where(Account.email == email))
        account: Account | None = result.scalars().one_or_none()

        if not account:
            raise AccountErrorCode.EMAIL_NOT_REGISTERED.exception(
                data={"email": email}, status_code=status.HTTP_404_NOT_FOUND
            )

        # Update account status
        account.status = AccountStatus.ACTIVE
        await account.save(session)

        # Remove the token after successful verification
        await token_manager.revoke_signup_email_verification_token(email=email)

        # Handle authentication
        return await AccountService._handle_successful_auth(session, account, request)

    @staticmethod
    async def send_sign_up_verification_email(account: Account, request: Request) -> str:
        """
        Send a signup verification email with a verification token.
        :param account: Account object
        :return: Verification token
        """
        if await AccountService.signup_email_verification_limit.check_limit_exceeded(identifier=account.email):
            raise CommonErrorCode.EMAIL_VERIFICATION_TOO_FREQUENT.exception(
                data={"email": account.email}, status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        token = await token_manager.generate_signup_email_verification_token(email=account.email, code=code)
        send_signup_verification_email_task.delay(
            language=request.state.language or "en",
            to=account.email,
            code=code,
        )
        await AccountService.signup_email_verification_limit.record_attempt(identifier=account.email)
        return token

    # endregion

    # region Authentication
    @staticmethod
    async def _verify_login_account(session: AsyncSession, email: str, password: str | None = None) -> Account:
        """
        Verify account exists and credentials are valid.

        Args:
            session: Database session
            email: Account email
            password: Optional password (None for OAuth/email verification flows)

        Returns:
            Account: Verified account object
        """
        result = await session.execute(Account.select().where(Account.email == email))
        account: Account | None = result.scalars().one_or_none()

        if not account or (password and not account.verify_password(password)):
            raise AccountErrorCode.INVALID_EMAIL_PASSWORD.exception(status_code=status.HTTP_404_NOT_FOUND)

        if account.status != AccountStatus.ACTIVE:
            raise AccountErrorCode.ACCOUNT_NOT_ACTIVE.exception(status_code=status.HTTP_403_FORBIDDEN)

        return account

    @staticmethod
    async def _handle_successful_auth(
        session: AsyncSession, account: Account, request: Request
    ) -> tuple[str, str, str]:
        """
        Handle successful authentication by updating account info and generating tokens.
        """
        # Check if user belongs to any tenant
        result = await session.execute(select(User).where(User.account_id == account.id))
        user_tenants = result.scalars().all()

        if not user_tenants:
            raise AccountErrorCode.NO_TENANT_ASSOCIATED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Set last login tenant based on X-Tenant-ID header if present
        requested_tenant_id = request.state.tenant_id
        if requested_tenant_id:
            # Verify the requested tenant is valid for this user
            if any(str(user.tenant_id) == requested_tenant_id for user in user_tenants):
                current_tenant_id = requested_tenant_id
            else:
                raise AccountErrorCode.INVALID_TENANT.exception(status_code=status.HTTP_403_FORBIDDEN)
        else:
            # Fall back to last login tenant or first available tenant
            if account.last_login_tenant_id and any(
                user.tenant_id == account.last_login_tenant_id for user in user_tenants
            ):
                current_tenant_id = account.last_login_tenant_id
            else:
                current_tenant_id = user_tenants[0].tenant_id

        # Update account info
        account.last_login_at = utcnow().replace(tzinfo=None)
        account.last_login_ip = request.client.host
        account.last_login_tenant_id = current_tenant_id
        account.language = request.state.language or account.language
        await account.save(session)

        # Generate tokens
        access_token, refresh_token = create_token_pair({"aid": str(account.id)})
        await session.commit()
        return access_token, refresh_token, str(current_tenant_id)

    @staticmethod
    async def login(session: AsyncSession, payload: LoginRequest, request: Request) -> tuple[str, str, str]:
        """Authenticate an account and return JWT tokens."""
        logger.info(f"Login attempt for email: {payload.email}")

        try:
            account = await AccountService._verify_login_account(session, payload.email, payload.password)
            invalidate_refresh_token(account_id=str(account.id))

            tokens = await AccountService._handle_successful_auth(session, account, request)
            logger.info(f"Successful login for email: {payload.email}")
            return tokens

        except FuniqAIError as e:
            raise e
        except Exception as e:
            logger.error(f"Login failed for email: {payload.email} - Error: {e!s}")
            raise

    # endregion

    # region Account Management
    @staticmethod
    async def update_account(session: AsyncSession, account: Account, data: dict):
        """Update account details."""
        for key, value in data.items():
            if hasattr(account, key):
                setattr(account, key, value)
        await session.commit()
        return account

    @staticmethod
    async def send_activate_account_email(account: Account, request: Request) -> str:
        """
        Send an account activation email with a verification code.
        :param account: Account object
        :return: Verification token
        """
        if await AccountService.activate_account_limit.check_limit_exceeded(identifier=account.email):
            raise CommonErrorCode.EMAIL_VERIFICATION_TOO_FREQUENT.exception(
                data={"email": account.email}, status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        token = await token_manager.generate_activate_account_token(email=account.email, code=code)
        send_activate_account_email_task.delay(
            language=request.state.language or account.language or "en",
            to=account.email,
            code=code,
        )
        await AccountService.activate_account_limit.record_attempt(identifier=account.email)
        return token

    @staticmethod
    async def activate_account(session: AsyncSession, payload: SignupRequest, request: Request) -> str:
        """
        Activate an account by verifying email/name and send a verification email.
        :param session: Database session
        :param payload: SignupRequest schema with email and name
        :return: Verification token
        """
        result = await session.execute(Account.select().where(Account.email == payload.email))

        account: Account | None = result.scalars().one_or_none()
        if not account:
            raise AccountErrorCode.EMAIL_NOT_REGISTERED.exception(
                data={"email": payload.email}, status_code=status.HTTP_400_BAD_REQUEST
            )
        elif account.status == AccountStatus.ACTIVE:
            raise AccountErrorCode.ACCOUNT_ALREADY_ACTIVE.exception(
                data={"email": payload.email}, status_code=status.HTTP_400_BAD_REQUEST
            )
        token = await AccountService.send_activate_account_email(account, request)
        return token

    # endregion

    # region Password Management
    @staticmethod
    async def send_reset_password_email(session: AsyncSession, payload: ForgotPasswordRequest, request: Request) -> str:
        """Send password reset email with verification code."""
        # Check rate limiting
        if await AccountService.reset_password_limit.check_limit_exceeded(identifier=payload.email):
            raise CommonErrorCode.EMAIL_VERIFICATION_TOO_FREQUENT.exception(
                data={"email": payload.email}, status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Find account
        result = await session.execute(Account.select().where(Account.email == payload.email))
        account: Account | None = result.scalars().one_or_none()

        if not account:
            raise AccountErrorCode.EMAIL_NOT_REGISTERED.exception(
                data={"email": payload.email}, status_code=status.HTTP_404_NOT_FOUND
            )

        # Generate verification code and token
        code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        token = await token_manager.generate_reset_password_token(email=account.email, code=code)

        # Send email
        send_reset_password_verification_email_task.delay(
            language=request.state.language or account.language or "en",
            to=account.email,
            code=code,
        )

        await AccountService.reset_password_limit.record_attempt(identifier=account.email)
        return token

    @staticmethod
    async def reset_password(session: AsyncSession, payload: ResetPasswordRequest) -> None:
        """Reset password using verification code."""
        logger.info("Starting password reset process")

        # Verify token and code
        token_data = await token_manager.get_reset_password_verification_data(token=payload.token)
        if not token_data:
            logger.warning("Password reset failed - verification code expired")
            raise CommonErrorCode.EMAIL_VERIFICATION_CODE_EXPIRED.exception(status_code=status.HTTP_400_BAD_REQUEST)

        email = token_data.get("email")
        if token_data.get("code") != payload.code:
            logger.warning(f"Password reset failed - invalid verification code for email: {email}")
            raise CommonErrorCode.INVALID_VERIFICATION_CODE.exception(
                data={"email": email}, status_code=status.HTTP_400_BAD_REQUEST
            )

        # Find and update account
        result = await session.execute(Account.select().where(Account.email == email))
        account: Account | None = result.scalars().one_or_none()

        if not account:
            raise AccountErrorCode.EMAIL_NOT_REGISTERED.exception(
                data={"email": email}, status_code=status.HTTP_404_NOT_FOUND
            )

        # Update password
        account.set_password(payload.new_password)
        await account.save(session)
        logger.info(f"Successfully reset password for email: {email}")

        # Invalidate all refresh tokens for this account
        invalidate_refresh_token(account_id=str(account.id))
        logger.warning(f"Invalidated refresh tokens for account: {account.id}")

        # Revoke token and return new access token
        await token_manager.revoke_reset_password_token(email=email)

    # endregion

    @staticmethod
    async def resend_verification_code(
        session: AsyncSession, email: str, code_type: AccountTokenType, request: Request
    ) -> str:
        """
        Resend verification code based on type.
        :param session: Database session
        :param email: Email address
        :param code_type: Type of verification code to send
        :return: New verification token
        """
        # Find account
        result = await session.execute(Account.select().where(Account.email == email))
        account: Account | None = result.scalars().one_or_none()

        if not account:
            raise AccountErrorCode.EMAIL_NOT_REGISTERED.exception(
                data={"email": email}, status_code=status.HTTP_404_NOT_FOUND
            )

        # Send verification code based on type
        if code_type == AccountTokenType.SIGNUP_EMAIL:
            return await AccountService.send_sign_up_verification_email(account, request)
        elif code_type == AccountTokenType.ACTIVATE_ACCOUNT_EMAIL:
            return await AccountService.send_activate_account_email(account, request)
        elif code_type == AccountTokenType.RESET_PASSWORD_EMAIL:
            return await AccountService.send_reset_password_email(session, ForgotPasswordRequest(email=email), request)

    # endregion

    @staticmethod
    async def activate_account_verify(
        session: AsyncSession, payload: ActivateAccountVerifyRequest, request: Request
    ) -> tuple[str, str, str]:
        """Verify account activation using the provided verification code."""
        # Verify token and code
        token_data = await token_manager.get_activate_account_verification_data(token=payload.token)
        if not token_data:
            raise CommonErrorCode.EMAIL_VERIFICATION_CODE_EXPIRED.exception(status_code=status.HTTP_400_BAD_REQUEST)

        email = token_data.get("email")
        if token_data.get("code") != payload.code:
            raise CommonErrorCode.INVALID_VERIFICATION_CODE.exception(
                data={"email": email}, status_code=status.HTTP_400_BAD_REQUEST
            )

        # Find account
        result = await session.execute(Account.select().where(Account.email == email))
        account: Account | None = result.scalars().one_or_none()

        if not account:
            raise AccountErrorCode.EMAIL_NOT_REGISTERED.exception(
                data={"email": email}, status_code=status.HTTP_404_NOT_FOUND
            )

        # Update account status
        account.status = AccountStatus.ACTIVE
        await account.save(session)

        # Revoke token
        await token_manager.revoke_activate_account_token(email=email)

        # Handle authentication
        return await AccountService._handle_successful_auth(session, account, request)

    @staticmethod
    async def get_account_info(session: AsyncSession, request: Request) -> Account:
        """
        Get account information from JWT token.
        :param session: Database session
        :param request: Request object
        :return: Account object
        """
        account_id = get_account_id_from_request(request)
        if not account_id:
            raise AccountErrorCode.ACCOUNT_NOT_FOUND.exception(status_code=status.HTTP_404_NOT_FOUND)
        result = await session.execute(Account.select().where(Account.id == account_id))
        return result.scalars().one_or_none()

    @staticmethod
    async def get_account_tenants(session: AsyncSession, account_id: str) -> list[TenantResponse]:
        """
        Get all tenants and user roles associated with an account.
        :param session: Database session
        :param account_id: Account ID
        :return: List of tenant responses
        """
        result = await session.execute(select(Tenant.id, Tenant.name).join(User).where(User.account_id == account_id))

        return [TenantResponse(id=str(tenant_id), name=tenant_name) for tenant_id, tenant_name in result]

    # TODO finish this
    @staticmethod
    async def oauth_login(session: AsyncSession, payload: OAuthLoginRequest, request: Request) -> tuple[str, str, str]:
        """
        Handle OAuth login/registration flow
        """
        logger.info(f"Starting OAuth login process for provider: {payload.provider}")

        try:
            # Find existing OAuth provider link
            result = await session.execute(
                select(OAuthProvider).where(
                    OAuthProvider.provider_name == payload.provider,
                    OAuthProvider.provider_id == payload.provider_user_id,
                )
            )
            oauth_provider = result.scalars().one_or_none()

            invite = None

            if payload.invite_code:
                result = await session.execute(
                    select(TenantInvite).where(
                        TenantInvite.code == payload.invite_code, TenantInvite.status == TenantInviteStatus.PENDING
                    )
                )
                invite = result.scalars().one_or_none()
                if not invite or (invite.expires_at and invite.expires_at < utcnow().replace(tzinfo=None)):
                    raise AccountErrorCode.INVALID_INVITE_CODE.exception(
                        data={"invite_code": payload.invite_code}, status_code=status.HTTP_400_BAD_REQUEST
                    )

            if oauth_provider:
                logger.info(f"Found existing OAuth provider link for email: {payload.email}")
                oauth_provider.access_token = payload.access_token
                oauth_provider.refresh_token = payload.refresh_token
                oauth_provider.profile_data = payload.profile_data
                await oauth_provider.save(session)

                account = oauth_provider.account
                account.last_login_at = utcnow().replace(tzinfo=None)
                account.last_login_ip = request.client.host

                if invite:
                    result = await session.execute(
                        select(User).where(User.account_id == account.id, User.tenant_id == invite.tenant_id)
                    )
                    existing_user = result.scalars().one_or_none()

                    if not existing_user:
                        user = User(
                            account_id=account.id,
                            tenant_id=invite.tenant_id,
                            role=TenantUserRole.MEMBER,
                            invite_code=invite.code,
                        )
                        session.add(user)

                        invite.status = TenantInviteStatus.USED
                        invite.used_at = utcnow().replace(tzinfo=None)
                        session.add(invite)

                        account.last_login_tenant_id = invite.tenant_id

                await account.save(session)

            else:
                logger.info(f"Creating new OAuth account for email: {payload.email}")
                result = await session.execute(select(Account).where(Account.email == payload.email))
                account = result.scalars().one_or_none()

                if not account:
                    account = Account(
                        email=payload.email,
                        name=payload.name,
                        status=AccountStatus.ACTIVE,
                        last_login_ip=request.client.host,
                        language=payload.language or "en",
                        last_login_tenant_id=invite.tenant_id if invite else None,
                    )
                    await account.save(session)

                    if invite:
                        user = User(
                            account_id=account.id,
                            tenant_id=invite.tenant_id,
                            role=TenantUserRole.MEMBER,
                            invite_code=invite.code,
                        )
                        session.add(user)

                        invite.status = TenantInviteStatus.USED
                        invite.used_at = utcnow().replace(tzinfo=None)
                        session.add(invite)

                oauth_provider = OAuthProvider(
                    provider_name=payload.provider,
                    provider_id=payload.provider_user_id,
                    access_token=payload.access_token,
                    refresh_token=payload.refresh_token,
                    profile_data=payload.profile_data,
                    account_id=account.id,
                )
                await oauth_provider.save(session)

            tokens = await AccountService._handle_successful_auth(session, account, request)
            logger.info(f"Successfully completed OAuth login for email: {payload.email}")
            return tokens

        except FuniqAIError as e:
            raise e
        except Exception as e:
            logger.error(f"OAuth login failed for provider {payload.provider} - Error: {e!s}")
            raise
