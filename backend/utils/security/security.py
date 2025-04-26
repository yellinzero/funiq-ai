import datetime
import re
import secrets
from datetime import timedelta
from typing import Any, Tuple

import bcrypt
from fastapi import Request, Response, status
from jose import JWTError, jwt
from pydantic import BaseModel, field_validator
from redis import Redis

from app.core.errors import AccountErrorCode
from configs import funiq_ai_config
from infrastructure import with_sync_redis
from utils.common.datetime import utcnow

# JWT configuration
ALGORITHM = "HS256"

# -------- Password Hashing --------


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    """
    try:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt).decode()
    except Exception as e:
        raise ValueError("Error during password hashing") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hash.
    """
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except Exception as e:
        raise ValueError("Error during password verification") from e


# -------- JWT Token Handling --------


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None) -> str:
    """
    Create a JSON Web Token (JWT) with an optional expiration time.

    Args:
        data (dict): The payload data to encode into the token.
        expires_delta (datetime.timedelta | None): Optional expiration time.

    Returns:
        str: The encoded JWT.
    """
    to_encode = data.copy()
    expire = utcnow() + (expires_delta or datetime.timedelta(minutes=funiq_ai_config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, funiq_ai_config.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded payload.

    Raises:
        JWTError: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, funiq_ai_config.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token") from JWTError


# -------- Utility Functions --------


def get_account_id_from_token(token: str) -> str:
    """
    Extract the user ID from the JWT payload.

    Args:
        token (str): The JWT token.

    Returns:
        str: The user ID from the token.
    """
    payload = decode_access_token(token)
    return str(payload.get("aid"))  # 'aid' is commonly used to store user ID


def get_account_id_from_request(request: Request) -> str:
    """
    Extract the account ID from the request headers.
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return get_account_id_from_token(token)


@with_sync_redis
def create_token_pair(data: dict, sync_redis: Redis) -> Tuple[str, str]:
    """Create both access and refresh tokens."""
    account_id = data["aid"]

    # Create refresh token (long-lived)
    refresh_token = secrets.token_urlsafe(32)

    # Store in sync_redis
    sync_redis_key = f"refresh_token:{account_id}"
    sync_redis.setex(sync_redis_key, timedelta(days=funiq_ai_config.REFRESH_TOKEN_EXPIRE_DAYS), refresh_token)

    # Add refresh token to access token data
    data["refresh_token"] = refresh_token

    # Create access token (short-lived) with refresh token included
    access_token = create_access_token(
        data=data, expires_delta=timedelta(minutes=funiq_ai_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return access_token, refresh_token


@with_sync_redis
def verify_refresh_token(refresh_token: str, sync_redis: Redis) -> str:
    """Verify refresh token and return account ID."""
    for key in sync_redis.scan_iter("refresh_token:*"):
        stored_token = sync_redis.get(key)
        if stored_token and stored_token.decode() == refresh_token:
            return key.decode().split(":")[1]
    raise AccountErrorCode.REFRESH_TOKEN_EXPIRED.exception(status_code=status.HTTP_401_UNAUTHORIZED)


@with_sync_redis
def invalidate_refresh_token(account_id: str | None = None, refresh_token: str | None = None, sync_redis: Redis = None):
    """Invalidate refresh token either by account_id or by token value."""
    if refresh_token:
        # if provide refresh token
        for key in sync_redis.scan_iter("refresh_token:*"):
            stored_token = sync_redis.get(key)
            if stored_token and stored_token.decode() == refresh_token:
                sync_redis.delete(key)
                return
    elif account_id:
        # if provide account id
        sync_redis_key = f"refresh_token:{account_id}"
        sync_redis.delete(sync_redis_key)


def refresh_access_token(refresh_token: str) -> str:
    """Create new access token from refresh token."""
    account_id = verify_refresh_token(refresh_token)
    return create_access_token({"aid": account_id})


def get_refresh_token_from_cookie(request: Request) -> str:
    return request.cookies.get(funiq_ai_config.REFRESH_TOKEN_COOKIE_NAME)


def set_refresh_token_to_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        funiq_ai_config.REFRESH_TOKEN_COOKIE_NAME,
        refresh_token,
        secure=True,
        samesite="none",
        httponly=True,
        max_age=funiq_ai_config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )


def delete_refresh_token_from_cookie(response: Response):
    response.delete_cookie(funiq_ai_config.REFRESH_TOKEN_COOKIE_NAME)


def validate_password(password: str) -> str:
    """
    Validate password strength requirements:
    - Minimum 8 characters
    - Maximum 64 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if len(password) > 64:
        raise ValueError("Password must not exceed 64 characters")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    return password


class PasswordMixin(BaseModel):
    """A mixin class that adds password validation to a Pydantic model."""

    @field_validator("password", "new_password", check_fields=False)
    @classmethod
    def validate_password_field(cls, v: Any) -> Any:
        return validate_password(v)
