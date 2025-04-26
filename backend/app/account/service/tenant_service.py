import secrets
from datetime import timedelta

from fastapi import status
from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.account.schemas import TenantResponse, UpdateUserResponse, UserInfo
from app.core.errors import AccountErrorCode, CommonErrorCode
from app.core.models.account import Account, Tenant, TenantInvite, TenantInviteStatus, TenantUserRole, User
from utils.common.datetime import utcnow

from .account_service import AccountService


class TenantService:
    """Service for managing tenants and tenant users"""

    # region Tenant Management
    @staticmethod
    async def create_tenant(
        session: AsyncSession,
        name: str,
        account_id: str,
    ) -> TenantResponse:
        """Create a new tenant and set the creator as owner."""
        logger.info(f"Creating new tenant with name: {name}")

        # Create tenant
        tenant = Tenant(name=name)
        await tenant.save(session)

        # Create user entry for the creator as owner
        user = User(account_id=account_id, tenant_id=tenant.id, role=TenantUserRole.OWNER)
        await user.save(session)

        logger.info(f"Successfully created tenant {tenant.id} with owner {account_id}")
        await session.commit()
        return TenantResponse(id=str(tenant.id), name=tenant.name)

    @staticmethod
    async def get_tenant(session: AsyncSession, tenant_id: str) -> Tenant:
        """Get tenant by ID."""
        result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalars().one_or_none()
        if not tenant:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                data={"tenant_id": tenant_id}, status_code=status.HTTP_404_NOT_FOUND
            )
        return tenant

    @staticmethod
    async def update_tenant(session: AsyncSession, tenant_id: str, account_id: str, name: str) -> TenantResponse:
        """Update tenant details."""
        logger.info(f"Updating tenant {tenant_id} details")

        # Check permissions
        user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)
        if user.role not in [TenantUserRole.OWNER, TenantUserRole.ADMIN]:
            logger.warning(f"Permission denied for user {account_id} to update tenant {tenant_id}")
            raise CommonErrorCode.PERMISSION_DENIED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Update tenant
        tenant = await TenantService.get_tenant(session, tenant_id)
        tenant.name = name
        await tenant.save(session)

        logger.info(f"Successfully updated tenant {tenant_id}")
        await session.commit()
        return TenantResponse(id=str(tenant.id), name=tenant.name)

    @staticmethod
    async def delete_tenant(session: AsyncSession, tenant_id: str, account_id: str) -> None:
        """Delete a tenant."""
        logger.info(f"Attempting to delete tenant {tenant_id}")

        # Only owner can delete tenant
        user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)
        if user.role != TenantUserRole.OWNER:
            logger.warning(f"Permission denied for user {account_id} to delete tenant {tenant_id}")
            raise CommonErrorCode.PERMISSION_DENIED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Delete tenant (cascade will handle users)
        tenant = await TenantService.get_tenant(session, tenant_id)
        await tenant.delete(session)
        await session.commit()

        logger.info(f"Successfully deleted tenant {tenant_id}")

    # endregion

    # region User Management
    @staticmethod
    async def generate_invite_code(
        session: AsyncSession, tenant_id: str, account_id: str, role: TenantUserRole = TenantUserRole.MEMBER
    ) -> str:
        """Generate an invite code for the tenant."""
        logger.info(f"Generating invite code for tenant {tenant_id}")

        # Check if user has permission to generate invite code
        user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)
        if user.role not in [TenantUserRole.OWNER, TenantUserRole.ADMIN]:
            logger.warning(f"Permission denied for user {account_id} to generate invite code")
            raise CommonErrorCode.PERMISSION_DENIED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Only owner can generate admin invite codes
        if role == TenantUserRole.ADMIN and user.role != TenantUserRole.OWNER:
            logger.warning(f"Permission denied for non-owner {account_id} to generate admin invite code")
            raise CommonErrorCode.PERMISSION_DENIED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Generate unique invite code
        code = secrets.token_urlsafe(16)
        exists = await session.execute(select(TenantInvite).where(TenantInvite.code == code))
        if not exists.scalars().one_or_none():
            invite = TenantInvite(
                tenant_id=tenant_id,
                code=code,
                role=role,
                created_by=account_id,
                status=TenantInviteStatus.PENDING,
                expires_at=utcnow().replace(tzinfo=None) + timedelta(days=7),
            )
            await invite.save(session)

            logger.info(f"Successfully generated invite code for tenant {tenant_id}")
            return code

    @staticmethod
    async def get_user_by_account_id(
        session: AsyncSession,
        tenant_id: str,
        account_id: str,
    ) -> UserInfo:
        account = await AccountService.get_account_info(session, account_id)
        result = await session.execute(
            select(User).where(and_(User.tenant_id == tenant_id, User.account_id == account_id))
        )
        user = result.scalars().one_or_none()
        if not user:
            raise AccountErrorCode.USER_NOT_IN_TENANT.exception(
                data={"tenant_id": tenant_id}, status_code=status.HTTP_404_NOT_FOUND
            )
        return UserInfo(
            id=str(user.id),
            email=account.email,
            name=account.name,
            language=account.language,
            status=account.status,
            last_login_at=account.last_login_at.isoformat() if account.last_login_at else None,
            last_login_ip=account.last_login_ip,
            role=user.role,
            avatar=user.avatar,
        )

    @staticmethod
    async def add_user(
        session: AsyncSession,
        tenant_id: str,
        account_id: str,
        new_user_email: str,
        role: TenantUserRole = TenantUserRole.MEMBER,
    ) -> UserInfo:
        """Add a user to tenant."""
        logger.info(f"Adding user {new_user_email} to tenant {tenant_id}")

        # Only owner/admin can add users
        user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)
        if user.role not in [TenantUserRole.OWNER, TenantUserRole.ADMIN]:
            logger.warning(f"Permission denied for user {account_id} to add new user to tenant {tenant_id}")
            raise CommonErrorCode.PERMISSION_DENIED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Only owner can add admin
        if role == TenantUserRole.ADMIN and user.role != TenantUserRole.OWNER:
            logger.warning(f"Permission denied for non-owner {account_id} to add admin to tenant {tenant_id}")
            raise CommonErrorCode.PERMISSION_DENIED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Find account by email
        result = await session.execute(select(Account).where(Account.email == new_user_email))
        account = result.scalars().one_or_none()
        if not account:
            logger.warning(f"Failed to add user - email not registered: {new_user_email}")
            raise AccountErrorCode.EMAIL_NOT_REGISTERED.exception(
                data={"email": new_user_email}, status_code=status.HTTP_404_NOT_FOUND
            )

        # Check if user already exists in tenant
        result = await session.execute(select(User).where(User.tenant_id == tenant_id, User.account_id == account.id))
        if result.scalars().one_or_none():
            logger.warning(f"Failed to add user - already in tenant: {new_user_email}")
            raise AccountErrorCode.USER_ALREADY_IN_TENANT.exception(
                data={"email": new_user_email}, status_code=status.HTTP_400_BAD_REQUEST
            )

        # Create new user
        new_user = User(account_id=account.id, tenant_id=tenant_id, role=role)
        await new_user.save(session)

        logger.info(f"Successfully added user {new_user_email} to tenant {tenant_id} with role {role}")
        await session.commit()
        return UserInfo(
            id=str(new_user.id),
            email=account.email,
            name=account.name,
            language=account.language,
            status=account.status,
            last_login_at=account.last_login_at,
            last_login_ip=account.last_login_ip,
            role=new_user.role,
            avatar=new_user.avatar,
        )

    @staticmethod
    async def update_user_role(
        session: AsyncSession, tenant_id: str, account_id: str, target_user_id: str, new_role: TenantUserRole
    ) -> UpdateUserResponse:
        """Update user's role in tenant."""
        logger.info(f"Updating role for user {target_user_id} in tenant {tenant_id}")

        # Only owner/admin can update roles
        user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)
        if user.role not in [TenantUserRole.OWNER, TenantUserRole.ADMIN]:
            logger.warning(f"Permission denied for user {account_id} to update roles in tenant {tenant_id}")
            raise CommonErrorCode.PERMISSION_DENIED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Get target user
        result = await session.execute(select(User).where(User.tenant_id == tenant_id, User.id == target_user_id))
        target_user = result.scalars().one_or_none()
        if not target_user:
            logger.warning(f"Failed to update role - user not found: {target_user_id}")
            raise AccountErrorCode.USER_NOT_IN_TENANT.exception(
                data={"user_id": target_user_id}, status_code=status.HTTP_404_NOT_FOUND
            )

        # Admin cannot modify owner or other admin roles
        if user.role == TenantUserRole.ADMIN:
            if target_user.role in [TenantUserRole.OWNER, TenantUserRole.ADMIN] or new_role in [
                TenantUserRole.OWNER,
                TenantUserRole.ADMIN,
            ]:
                logger.warning(f"Permission denied for admin {account_id} to modify owner/admin roles")
                raise CommonErrorCode.PERMISSION_DENIED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Update role
        target_user.role = new_role
        await target_user.save(session)

        logger.info(f"Successfully updated role to {new_role} for user {target_user_id} in tenant {tenant_id}")
        await session.commit()
        return UpdateUserResponse(
            id=str(target_user.id),
            account_id=str(target_user.account_id),
            tenant_id=str(target_user.tenant_id),
            role=target_user.role,
        )

    @staticmethod
    async def remove_user(session: AsyncSession, tenant_id: str, account_id: str, target_user_id: str) -> None:
        """Remove a user from tenant."""
        logger.info(f"Attempting to remove user {target_user_id} from tenant {tenant_id}")

        # Only owner/admin can remove users
        user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)
        if user.role not in [TenantUserRole.OWNER, TenantUserRole.ADMIN]:
            logger.warning(f"Permission denied for user {account_id} to remove users from tenant {tenant_id}")
            raise CommonErrorCode.PERMISSION_DENIED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Get target user
        result = await session.execute(select(User).where(User.tenant_id == tenant_id, User.id == target_user_id))
        target_user = result.scalars().one_or_none()
        if not target_user:
            logger.warning(f"Failed to remove user - not found in tenant: {target_user_id}")
            raise AccountErrorCode.USER_NOT_IN_TENANT.exception(
                data={"user_id": target_user_id}, status_code=status.HTTP_404_NOT_FOUND
            )

        # Admin cannot remove owner or other admin
        if user.role == TenantUserRole.ADMIN and target_user.role in [TenantUserRole.OWNER, TenantUserRole.ADMIN]:
            logger.warning(f"Permission denied for admin {account_id} to remove owner/admin user {target_user_id}")
            raise CommonErrorCode.PERMISSION_DENIED.exception(status_code=status.HTTP_403_FORBIDDEN)

        # Cannot remove the last owner
        if target_user.role == TenantUserRole.OWNER:
            result = await session.execute(
                select(User).where(User.tenant_id == tenant_id, User.role == TenantUserRole.OWNER)
            )
            owners = result.scalars().all()
            if len(owners) <= 1:
                logger.warning(f"Cannot remove last owner {target_user_id} from tenant {tenant_id}")
                raise AccountErrorCode.CANNOT_REMOVE_LAST_OWNER.exception(status_code=status.HTTP_400_BAD_REQUEST)

        # Remove user
        await target_user.delete(session)
        await session.commit()

        logger.info(f"Successfully removed user {target_user_id} from tenant {tenant_id}")
        # endregion

    @staticmethod
    async def get_tenant_users(session: AsyncSession, tenant_id: str) -> list[UserInfo]:
        """Get all users in a tenant."""
        result = await session.execute(select(User).where(User.tenant_id == tenant_id))
        users = result.scalars().all()
        
        account_ids = [str(user.account_id) for user in users]
        
        accounts_result = await session.execute(
            select(Account).where(Account.id.in_(account_ids))
        )
        accounts = {str(account.id): account for account in accounts_result.scalars().all()}
        
        return [
            UserInfo(
                id=str(user.id),
                email=accounts[str(user.account_id)].email,
                name=accounts[str(user.account_id)].name,
                language=accounts[str(user.account_id)].language,
                status=accounts[str(user.account_id)].status,
                last_login_at=accounts[str(user.account_id)].last_login_at.isoformat() 
                    if accounts[str(user.account_id)].last_login_at else None,
                last_login_ip=accounts[str(user.account_id)].last_login_ip,
                role=user.role,
                avatar=user.avatar,
            )
            for user in users
        ]
