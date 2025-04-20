from app.core.errors.base import BaseErrorCode


class AppErrorCode(BaseErrorCode):
    """
    App related error codes
    """

    APP_NOT_FOUND = ("D0001", "App not found with the specified ID")
    APP_VERSION_NOT_FOUND = ("D0002", "App version not found with the specified version number")
    APP_WORKFLOW_NOT_FOUND = ("D0003", "App workflow not found")
    APP_ALREADY_EXISTS = ("D0101", "An app with this name already exists in the tenant")
    APP_VERSION_ALREADY_EXISTS = ("D0102", "This version number already exists for the app")

    INVALID_APP = ("D0201", "Invalid app configuration - Please check app settings and permissions")
    INVALID_APP_VERSION = ("D0202", "Invalid app version configuration - Please check version settings")
    INVALID_APP_NAME = (
        "D0203",
        "Invalid app name - Name must be 3-64 characters and contain only letters, numbers, and hyphens",
    )
    INVALID_VERSION_FORMAT = ("D0204", "Invalid version format - Must follow semantic versioning (e.g., 1.0.0)")

    APP_DISABLED = ("D0301", "The app is currently disabled")
    APP_VERSION_INACTIVE = ("D0302", "The requested app version is not active")
    APP_WORKFLOW_MISMATCH = ("D0303", "The app version's workflow configuration is invalid or incompatible")

    APP_PERMISSION_DENIED = ("D0401", "You don't have permission to access or modify this app")
    APP_VERSION_PERMISSION_DENIED = ("D0402", "You don't have permission to publish or modify app versions")

    APP_CREATE_ERROR = ("D0501", "Failed to create app - Please check the provided configuration")
    APP_UPDATE_ERROR = ("D0502", "Failed to update app - Please check the provided changes")
    APP_VERSION_PUBLISH_ERROR = (
        "D0503",
        "Failed to publish app version - Please check version configuration and workflow status",
    )

    APP_VERSION_NOT_ACTIVE = ("D0504", "The requested app version is not active")

    APP_DELETE_ERROR = ("D0505", "Failed to delete app - Please ensure no active dependencies exist")
