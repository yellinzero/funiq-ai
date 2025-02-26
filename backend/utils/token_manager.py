import json
import uuid
from datetime import timedelta
from enum import Enum

from configs import funiq_ai_config
from database import redis


class TokenManager:
    def _get_token_key(self, token: str, namespace: str = 'funiq_ai') -> str:
        """Generate a Redis key for the token."""
        return f"{namespace}:token:{token}"

    async def generate_token(self, data: dict, namespace: str = 'funiq_ai', expiry_seconds: int = 10 * 60) -> str:
        """
        Generate a unique token, store data in Redis, and set expiration.

        :param data: The data to associate with the token
        :param expiry_seconds: Token expiration time in seconds
        :return: Generated token
        """
        token = str(uuid.uuid4())  # Generate a unique UUID as token
        token_key = self._get_token_key(token, namespace)

        # Set the token data in Redis with an expiration time
        await redis.setex(token_key, timedelta(seconds=expiry_seconds), json.dumps(data))
        return token

    async def revoke_token(self, token: str, namespace: str = 'funiq_ai'):
        """
        Revoke (delete) a token.

        :param token: Token to be revoked
        """
        token_key = self._get_token_key(token, namespace)
        await redis.delete(token_key)

    async def get_token_data(self, token: str, namespace: str = 'funiq_ai') -> dict | None:
        """
        Retrieve the data associated with a token.

        :param token: Token to fetch data for
        :return: Token data if valid, else None
        """
        token_key = self._get_token_key(token, namespace)
        token_data = await redis.get(token_key)
        if token_data:
            return json.loads(token_data)
        return None

    async def validate_token(self, token: str, namespace: str = 'funiq_ai') -> bool:
        """
        Check if a token is still valid.

        :param token: Token to validate
        :return: True if valid, False otherwise
        """
        token_key = self._get_token_key(token, namespace)
        return await redis.exists(token_key) == 1


class AccountTokenType(Enum):
    SIGNUP_EMAIL = "signup_email"
    ACTIVATE_ACCOUNT_EMAIL = "activate_account_email"
    RESET_PASSWORD_EMAIL = "reset_password_email"  # noqa: S105


class AccountTokenManager(TokenManager):
    async def generate_token(
        self, 
        token_type: str,
        email: str,
        additional_data: dict | None
    ):
        old_token = await self._get_current_token_for_account(email, token_type)
        if old_token:
            if isinstance(old_token, bytes):
                old_token = old_token.decode("utf-8")
            await self.revoke_token(old_token, token_type)
            
        token_data = {"email": email, "token_type": token_type}
        if additional_data:
            token_data.update(additional_data)

        expiry_seconds = funiq_ai_config.model_dump().get(f"{token_type.upper()}_TOKEN_EXPIRY_MINUTES") * 60
        token = await super().generate_token(token_data, token_type, expiry_seconds)

        await self._set_current_token_for_account(email, token, token_type, expiry_seconds)
            
        return token

    async def generate_signup_email_verification_token(self, email: str, code: str) -> str:
        """
        Generate a registration token for email verification.

        :param email: Account email
        :return: Generated token
        """
        return await self.generate_token(AccountTokenType.SIGNUP_EMAIL.value, email, {"code": code})
    
    async def get_signup_email_verification_data(self, token: str) -> dict | None:
        return await self.get_token_data(token, AccountTokenType.SIGNUP_EMAIL.value)
    
    async def revoke_signup_email_verification_token(self, email: str) -> None:
        await self.revoke_token(email, AccountTokenType.SIGNUP_EMAIL.value)

    async def generate_activate_account_token(self, email: str, code: str) -> str:
        """
        Generate a token for account activation.
        
        :param email: Account email
        :param code: Verification code
        :return: Generated token
        """
        return await self.generate_token(
            AccountTokenType.ACTIVATE_ACCOUNT_EMAIL.value,
            email,
            {"code": code}
        )

    async def get_activate_account_verification_data(self, token: str) -> dict | None:
        """
        Get verification data for account activation.
        
        :param token: Activation token
        :return: Token data if valid, else None
        """
        return await self.get_token_data(token, AccountTokenType.ACTIVATE_ACCOUNT_EMAIL.value)

    async def revoke_activate_account_token(self, email: str) -> None:
        """
        Revoke account activation token.
        
        :param email: Account email
        """
        await self.revoke_token(email, AccountTokenType.ACTIVATE_ACCOUNT_EMAIL.value)
        
    async def generate_reset_password_token(self, email: str, code: str) -> str:
        """
        Generate a token for password reset verification.
        
        :param email: Account email
        :param code: Verification code
        :return: Generated token
        """
        return await self.generate_token(
            AccountTokenType.RESET_PASSWORD_EMAIL.value,
            email,
            {"code": code}
        )

    async def get_reset_password_verification_data(self, token: str) -> dict | None:
        """
        Get verification data for password reset.
        
        :param token: Reset password token
        :return: Token data if valid, else None
        """
        return await self.get_token_data(token, AccountTokenType.RESET_PASSWORD_EMAIL.value)

    async def revoke_reset_password_token(self, email: str) -> None:
        """
        Revoke password reset token.
        
        :param email: Account email
        """
        await self.revoke_token(email, AccountTokenType.RESET_PASSWORD_EMAIL.value)
                    
    async def _get_current_token_for_account(self, email: str, token_type: str) -> str | None:
        key = self._get_account_token_key(email, token_type)
        current_token = await redis.get(key)
        return current_token

    async def _set_current_token_for_account(
        self, account_id: str, token: str, token_type: str, expiry_seconds: int
    ):
        key = self._get_account_token_key(account_id, token_type)
        await redis.setex(key, expiry_seconds, token)

    def _get_account_token_key(self, email: str, token_type: str) -> str:
        return f"{token_type}:account:{email}"
    
    async def revoke_token(self, email: str, token_type: str):
        """
        Revoke the current token for a given account and token type.

        :param email: Account email
        :param token_type: Type of token to revoke
        """
        key = self._get_account_token_key(email, token_type)
        old_token = await redis.get(key)

        if old_token:
            await super().revoke_token(old_token.decode("utf-8"), token_type)  # Remove token from storage
            await redis.delete(key)  # Remove reference to the token
