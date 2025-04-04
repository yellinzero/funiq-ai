from app.core.errors.base import BaseErrorCode


class AccountErrorCode(BaseErrorCode):
    """
    User errors (Category B)
    """
    EMAIL_ALREADY_REGISTERED = ("B0001", "The email address is already registered")
    NAME_ALREADY_REGISTERED = ("B0002", "The username is already registered")
    INVALID_EMAIL_PASSWORD = ("B0003", "Invalid email or password")
    ACCOUNT_NOT_ACTIVE = ("B0004", "Account is not active")
    EMAIL_NOT_REGISTERED = (
        "B0005", 
        "The email address is not registered. Please check and try again."
    )
    ACCOUNT_ALREADY_ACTIVE = (
        "B0006", 
        "The account is already active. No further action is required."
    )
    ACCOUNT_NOT_FOUND = (
        "B0007", 
        "The account is not found."
    )
    CANNOT_REMOVE_LAST_OWNER = (
        "B0008", 
        "Cannot remove the last owner."
    )
    USER_NOT_IN_TENANT = (
        "B0009", 
        "The user is not in the tenant."
    )
    TENANT_NOT_FOUND = (
        "B0010", 
        "The tenant is not found."
    )
    USER_ALREADY_IN_TENANT = (
        "B0011", 
        "The user is already in the tenant."
    )
    NO_TENANT_ASSOCIATED = (
        "B0012", 
        "No tenant associated with the account."
    )
    INVALID_INVITE_CODE = (
        "B0013", 
        "The invite code is invalid or expired."
    )
    OAUTH_INVALID_PROVIDER = (
        "B0014",
        "Invalid OAuth provider"
    )
    OAUTH_INVALID_TOKEN = (
        "B0015", 
        "Invalid OAuth token"
    )
    OAUTH_EMAIL_REQUIRED = (
        "B0016",
        "Email is required for OAuth login"
    )
    TOKEN_EXPIRED = (
        "B0017",
        "Access token has expired"
    )
    REFRESH_TOKEN_EXPIRED = (
        "B0020",
        "Refresh token has expired"
    )
    INVALID_TENANT = (
        "B0018",
        "Invalid tenant"
    )
