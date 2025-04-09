from app.core.errors.base import BaseErrorCode


class AppErrorCode(BaseErrorCode):
    """
    App related error codes (Category C)
    
    Error code format: Cxxxx
    - C: Category identifier for App errors
    - xxxx: Four digit error code
    """
    # Not Found Errors (C00xx)
    APP_NOT_FOUND = (
        "C0001",
        "App not found with the specified ID"
    )
    APP_VERSION_NOT_FOUND = (
        "C0002",
        "App version not found with the specified version number"
    )

    # Duplicate Errors (C01xx)
    APP_ALREADY_EXISTS = (
        "C0101",
        "An app with this name already exists in the tenant"
    )
    APP_VERSION_ALREADY_EXISTS = (
        "C0102",
        "This version number already exists for the app"
    )

    # Validation Errors (C02xx)
    INVALID_APP = (
        "C0201",
        "Invalid app configuration - Please check app settings and permissions"
    )
    INVALID_APP_VERSION = (
        "C0202",
        "Invalid app version configuration - Please check version settings"
    )
    INVALID_APP_NAME = (
        "C0203",
        "Invalid app name - Name must be 3-64 characters and contain only letters, numbers, and hyphens"
    )
    INVALID_VERSION_FORMAT = (
        "C0204",
        "Invalid version format - Must follow semantic versioning (e.g., 1.0.0)"
    )

    # State Errors (C03xx)
    APP_DISABLED = (
        "C0301",
        "The app is currently disabled"
    )
    APP_VERSION_INACTIVE = (
        "C0302",
        "The requested app version is not active"
    )
    APP_WORKFLOW_MISMATCH = (
        "C0303",
        "The app version's workflow configuration is invalid or incompatible"
    )

    # Permission Errors (C04xx)
    APP_PERMISSION_DENIED = (
        "C0401",
        "You don't have permission to access or modify this app"
    )
    APP_VERSION_PERMISSION_DENIED = (
        "C0402",
        "You don't have permission to publish or modify app versions"
    )

    # Operation Errors (C05xx)
    APP_CREATE_ERROR = (
        "C0501",
        "Failed to create app - Please check the provided configuration"
    )
    APP_UPDATE_ERROR = (
        "C0502",
        "Failed to update app - Please check the provided changes"
    )
    APP_VERSION_PUBLISH_ERROR = (
        "C0503",
        "Failed to publish app version - Please check version configuration and workflow status"
    )
    APP_DELETE_ERROR = (
        "C0504",
        "Failed to delete app - Please ensure no active dependencies exist"
    )