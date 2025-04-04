from contextlib import contextmanager

from fastapi import Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import HTTPConnection

from app.core.errors.common import CommonErrorCode
from utils.common.context import ContextStorage
from utils.security.security import (
    decode_access_token,
    get_account_id_from_token,
)


class CurrentUserContext(ContextStorage):
    DEFAULT_VALUE = None
    CONTEXT_KEY_NAME = "current_user_id"


current_user_context = CurrentUserContext()


@contextmanager
def set_current_user_id(user_id: str):
    """Context manager to set current user ID"""
    current_user_context.set(user_id)
    try:
        yield
    finally:
        current_user_context._values.reset(current_user_context._token_id)


def get_current_user_id() -> str | None:
    """Get current user ID from context"""
    return current_user_context.get()


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials = await super().__call__(request)
        if credentials is None:
            raise CommonErrorCode.UNAUTHORIZED.exception(status_code=status.HTTP_401_UNAUTHORIZED)

        await self.validate_token(request, token=credentials.credentials)
        return credentials

    @classmethod
    async def validate_token(cls, request: HTTPConnection, token: str):
        """Validate JWT token and set account in request state"""
        try:
            # Validate token
            payload = decode_access_token(token)
            account_id = get_account_id_from_token(token)

            # Set account ID in request state
            request.state.account_id = account_id
            request.scope["account_id"] = account_id

            # Set user ID in context using the new context storage
            current_user_context.set(account_id)

            return payload

        except ValueError as e:
            raise CommonErrorCode.UNAUTHORIZED.exception(status_code=status.HTTP_401_UNAUTHORIZED) from e

    @staticmethod
    def get_token_from_request(request: Request) -> str | None:
        """Extract token from request header"""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
            
        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bearer":
            return None
            
        return token