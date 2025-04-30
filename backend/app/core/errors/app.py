from app.core.errors.base import BaseErrorCode


class AppErrorCode(BaseErrorCode):
    """
    Application related errors (Category D)
    """
    
    # Authentication & Authorization (01)
    APP_PERMISSION_DENIED = ("D0101", "You don't have permission to access or modify this app")
    APP_VERSION_PERMISSION_DENIED = ("D0102", "You don't have permission to publish or modify app versions")
    
    # Input/Parameter validation (02)
    INVALID_APP_NAME = (
        "D0201",
        "Invalid app name - Name must be 3-64 characters and contain only letters, numbers, and hyphens"
    )
    INVALID_VERSION_FORMAT = ("D0202", "Invalid version format - Must follow semantic versioning (e.g., 1.0.0)")
    
    # Resource related (03)
    APP_NOT_FOUND = ("D0301", "App not found with the specified ID")
    APP_VERSION_NOT_FOUND = ("D0302", "App version not found with the specified version number")
    APP_WORKFLOW_NOT_FOUND = ("D0303", "App workflow not found")
    APP_ALREADY_EXISTS = ("D0304", "An app with this name already exists in the tenant")
    APP_VERSION_ALREADY_EXISTS = ("D0305", "This version number already exists for the app")
    APP_FETCH_FAILED = ("D0306", "Failed to fetch apps")
    CONVERSATION_NOT_FOUND = ("D0307", "Conversation not found with the specified ID")
    CONVERSATION_FETCH_FAILED = ("D0308", "Failed to fetch conversations")
    MESSAGE_FETCH_FAILED = ("D0309", "Failed to fetch messages")
    
    # Operation related (04)
    APP_CREATE_ERROR = ("D0401", "Failed to create app - Please check the provided configuration")
    APP_UPDATE_ERROR = ("D0402", "Failed to update app - Please check the provided changes")
    APP_DELETE_ERROR = ("D0403", "Failed to delete app - Please ensure no active dependencies exist")
    APP_VERSION_PUBLISH_ERROR = (
        "D0404",
        "Failed to publish app version - Please check version configuration and workflow status"
    )
    CONVERSATION_CREATE_ERROR = ("D0405", "Failed to create conversation - Please check the provided configuration")
    CONVERSATION_UPDATE_ERROR = ("D0406", "Failed to update conversation - Please check the provided changes")
    CONVERSATION_DELETE_ERROR = ("D0407", "Failed to delete conversation - Please ensure no active dependencies exist")
    APP_ARCHIVED = ("D0408", "The app is currently archived")
    APP_INACTIVE = ("D0409", "The app is currently inactive")

    # Configuration related (08)
    INVALID_APP = ("D0801", "Invalid app configuration - Please check app settings and permissions")
    INVALID_APP_VERSION = ("D0802", "Invalid app version configuration - Please check version settings")
    APP_WORKFLOW_MISMATCH = ("D0803", "The app version's workflow configuration is invalid or incompatible")
    
    # Business logic/Status related (10)
    APP_DISABLED = ("D1001", "The app is currently disabled")
    APP_VERSION_INACTIVE = ("D1002", "The requested app version is not active")
    APP_VERSION_NOT_ACTIVE = ("D1003", "The requested app version is not active")
    CONVERSATION_ARCHIVED = ("D1004", "The requested conversation is archived")

