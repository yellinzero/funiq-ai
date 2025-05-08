from app.core.errors.base import BaseErrorCode


class AccountErrorCode(BaseErrorCode):
    """
    Account related errors (Category B)
    """
    # Authentication & Authorization (01)
    INVALID_EMAIL_PASSWORD = ("B0101", "Invalid email or password")
    ACCOUNT_NOT_ACTIVE = ("B0102", "Account is not active")
    TOKEN_EXPIRED = ("B0103", "Access token has expired")
    REFRESH_TOKEN_EXPIRED = ("B0104", "Refresh token has expired")
    INVALID_INVITE_CODE = ("B0105", "The invite code is invalid or expired")
    CANNOT_REMOVE_LAST_OWNER = ("B0106", "Cannot remove the last owner")
    
    # Input validation (02)
    INVALID_TENANT = ("B0201", "Invalid tenant configuration")
    
    # Resource related (03)
    ACCOUNT_NOT_FOUND = ("B0301", "The account is not found")
    USER_NOT_FOUND = ("B0302", "The user is not found")
    TENANT_NOT_FOUND = ("B0303", "The tenant is not found")
    EMAIL_NOT_REGISTERED = ("B0304", "The email address is not registered")
    USER_NOT_IN_TENANT = ("B0305", "The user is not in the tenant")
    NO_TENANT_ASSOCIATED = ("B0306", "No tenant associated with the account")
    EMAIL_ALREADY_REGISTERED = ("B0307", "The email address is already registered")
    NAME_ALREADY_REGISTERED = ("B0308", "The username is already registered")
    USER_ALREADY_IN_TENANT = ("B0309", "The user is already in the tenant")
    ACCOUNT_ALREADY_ACTIVE = ("B0310", "The account is already active")
    
    # Operation related (04)
    RESET_PASSWORD_EMAIL_FAILED = ("B0401", "Failed to send reset password email")
    ACTIVATE_ACCOUNT_EMAIL_FAILED = ("B0402", "Failed to send activate account email")
    SIGN_UP_EMAIL_FAILED = ("B0403", "Failed to send sign up email")
    
    # External service - OAuth (06)
    OAUTH_INVALID_PROVIDER = ("B0601", "Invalid OAuth provider")
    OAUTH_INVALID_TOKEN = ("B0602", "Invalid OAuth token")
    OAUTH_EMAIL_REQUIRED = ("B0603", "Email is required for OAuth login")