import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from utils.security import (
    AccountTokenManager,
    AccountTokenType,
    TokenManager,
)


@pytest.fixture
def mock_redis_fixture():
    redis = MagicMock()
    redis.setex = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.exists = AsyncMock(return_value=1)
    redis.delete = AsyncMock(return_value=True)
    redis.expire = AsyncMock(return_value=True)
    redis.close = AsyncMock(return_value=True)
    redis.zadd = AsyncMock(return_value=True)
    redis.zremrangebyscore = AsyncMock(return_value=True)
    redis.zcard = AsyncMock(return_value=0)
    
    return redis


@pytest.mark.asyncio
@patch('utils.token_manager.redis')
async def test_token_lifecycle(mock_redis, mock_redis_fixture):
    mock_redis.setex = mock_redis_fixture.setex
    mock_redis.get = mock_redis_fixture.get
    mock_redis.exists = mock_redis_fixture.exists
    mock_redis.delete = mock_redis_fixture.delete
    
    token_manager = TokenManager()
    
    # Test data
    test_data = {"user_id": "123", "email": "test@example.com"}
    
    # Generate token
    token = await token_manager.generate_token(data=test_data)
    assert token is not None
    
    # Verify setex was called with correct parameters
    mock_redis.setex.assert_called_once()
    args = mock_redis.setex.call_args[0]
    assert args[0].startswith('funiq_ai:token:')  # token key
    assert json.loads(args[2]) == test_data  # stored data
    
    # Setup mock for get_token_data
    mock_redis.get.return_value = json.dumps(test_data)
    
    # Validate token
    is_valid = await token_manager.validate_token(token=token)
    assert is_valid is True
    
    # Get token data
    retrieved_data = await token_manager.get_token_data(token=token)
    assert retrieved_data == test_data
    
    # Revoke token
    await token_manager.revoke_token(token)
    mock_redis.delete.assert_called_once()
    
    # Setup mock for invalid token
    mock_redis.exists.return_value = 0
    
    # Verify token is invalid after revocation
    is_valid = await token_manager.validate_token(token=token)
    assert is_valid is False


@pytest.mark.asyncio
@patch('utils.token_manager.redis')
async def test_account_token_manager(mock_redis, mock_redis_fixture):
    mock_redis.setex = mock_redis_fixture.setex
    mock_redis.get = mock_redis_fixture.get
    mock_redis.exists = mock_redis_fixture.exists
    mock_redis.delete = mock_redis_fixture.delete
    
    account_token_manager = AccountTokenManager()
    
    email = "test@example.com"
    code = "123456"
    
    # Test signup email verification token
    mock_redis.get.return_value = None  # No existing token
    signup_token = await account_token_manager.generate_signup_email_verification_token(
        email, code
    )
    
    # Prepare mock for token retrieval
    expected_signup_data = {
        "email": email,
        "code": code,
        "token_type": AccountTokenType.SIGNUP_EMAIL.value
    }
    mock_redis.get.return_value = json.dumps(expected_signup_data)
    
    signup_data = await account_token_manager.get_signup_email_verification_data(
        signup_token
    )
    assert signup_data["email"] == email
    assert signup_data["code"] == code
    
    # Test activate account token
    mock_redis.get.return_value = None  # Reset mock for new token generation
    activate_token = await account_token_manager.generate_activate_account_token(
        email, code
    )
    
    # Prepare mock for token retrieval
    expected_activate_data = {
        "email": email,
        "code": code,
        "token_type": AccountTokenType.ACTIVATE_ACCOUNT_EMAIL.value
    }
    mock_redis.get.return_value = json.dumps(expected_activate_data)
    
    activate_data = await account_token_manager.get_activate_account_verification_data(
        activate_token
    )
    assert activate_data["email"] == email
    assert activate_data["code"] == code
    
    # Test reset password token
    mock_redis.get.return_value = None  # Reset mock for new token generation
    reset_token = await account_token_manager.generate_reset_password_token(
        email, code
    )
    
    # Prepare mock for token retrieval
    expected_reset_data = {
        "email": email,
        "code": code,
        "token_type": AccountTokenType.RESET_PASSWORD_EMAIL.value
    }
    mock_redis.get.return_value = json.dumps(expected_reset_data)
    
    reset_data = await account_token_manager.get_reset_password_verification_data(
        reset_token
    )
    assert reset_data["email"] == email
    assert reset_data["code"] == code


@pytest.mark.asyncio
@patch('utils.token_manager.redis')
async def test_token_revocation_with_existing_token(mock_redis, mock_redis_fixture):
    mock_redis.setex = mock_redis_fixture.setex
    mock_redis.get = mock_redis_fixture.get
    mock_redis.exists = mock_redis_fixture.exists
    mock_redis.delete = mock_redis_fixture.delete
    
    account_token_manager = AccountTokenManager()
    
    email = "test@example.com"
    token_type = AccountTokenType.SIGNUP_EMAIL.value
    existing_token = "existing-token"  # noqa: S105
    
    # Setup mock to return existing token
    mock_redis.get.return_value = existing_token.encode('utf-8')
    
    # Generate new token (should revoke old token)
    new_token = await account_token_manager.generate_token(
        token_type,
        email,
        {"code": "123456"}
    )
    
    # Verify old token was revoked
    assert mock_redis.delete.called 