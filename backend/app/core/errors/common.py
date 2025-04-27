from app.core.errors.base import BaseErrorCode


class CommonErrorCode(BaseErrorCode):
    """
    Common errors (Category A)
    """
    # System level errors (00)
    INTERNAL_SERVER_ERROR = ("A0001", "Internal Server Error")
    
    # Authentication & Authorization (01)
    UNAUTHORIZED = ("A0101", "Unauthorized")
    PERMISSION_DENIED = ("A0102", "Permission Denied")
    
    # Input/Parameter validation (02)
    INVALID_ARGUMENT = ("A0201", "Invalid Argument")
    INVALID_VERIFICATION_CODE = ("A0202", "Invalid verification code")
    
    # Resource related (03)
    RESOURCE_NOT_FOUND = ("A0301", "Resource Not Found")
    FILE_NOT_FOUND = ("A0302", "The requested file could not be found")
    
    # Rate limiting (05)
    EMAIL_VERIFICATION_TOO_FREQUENT = (
        "A0501", 
        "Email verification requests are too frequent. Please try again later."
    )
    EMAIL_VERIFICATION_CODE_EXPIRED = (
        "A0502", 
        "The email verification code has expired. Please request a new one."
    )
