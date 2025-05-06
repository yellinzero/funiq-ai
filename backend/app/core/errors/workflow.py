from app.core.errors.base import BaseErrorCode


class WorkflowErrorCode(BaseErrorCode):
    """
    Workflow related errors (Category E)
    """

    # Input/Parameter validation (02)
    INVALID_VERSION_FORMAT = ("E0201", "Invalid version format - Must follow semantic versioning (e.g., 1.0.0)")

    # Resource related (03)
    WORKFLOW_NOT_FOUND = ("E0301", "Workflow not found with the specified ID")
    WORKFLOW_VERSION_NOT_FOUND = ("E0302", "Workflow version not found with the specified version number")
    WORKFLOW_NODE_NOT_FOUND = ("E0303", "Workflow node not found with the specified key")
    WORKFLOW_EDGE_NOT_FOUND = ("E0304", "Workflow edge not found with the specified key")
    WORKFLOW_VERSION_ALREADY_EXISTS = ("E0305", "This version number already exists for the workflow")
    WORKFLOW_NODE_FETCH_FAILED = ("E0306", "Failed to fetch workflow nodes")
    WORKFLOW_EDGE_FETCH_FAILED = ("E0307", "Failed to fetch workflow edges")
    WORKFLOW_VERSION_FETCH_FAILED = ("E0308", "Failed to fetch workflow versions")
    WORKFLOW_DEBUG_SNAPSHOT_FETCH_FAILED = ("E0309", "Failed to fetch workflow debug snapshots")
    WORKFLOW_FETCH_FAILED = ("E0310", "Failed to fetch workflows")
    WORKFLOW_DEBUG_SNAPSHOT_NOT_FOUND = ("E0311", "Workflow debug snapshot not found with the specified timestamp")
    OPERATOR_FETCH_FAILED = ("E0312", "Failed to fetch operators")

    # Operation related (04)
    WORKFLOW_CREATE_ERROR = ("E0401", "Failed to create workflow - Please check the provided configuration")
    WORKFLOW_VERSION_PUBLISH_ERROR = (
        "E0402",
        "Failed to publish workflow version - Please check version configuration",
    )
    WORKFLOW_SAVE_ERROR = ("E0403", "Failed to save workflow - Please check the provided configuration")
    WORKFLOW_NODE_CREATE_ERROR = ("E0404", "Failed to create workflow node - Please check the provided configuration")
    WORKFLOW_EDGE_CREATE_ERROR = ("E0405", "Failed to create workflow edge - Please check the provided configuration")
    WORKFLOW_NODE_UPDATE_ERROR = ("E0406", "Failed to update workflow node - Please check the provided configuration")
    WORKFLOW_EDGE_UPDATE_ERROR = ("E0407", "Failed to update workflow edge - Please check the provided configuration")
    WORKFLOW_NODE_DELETE_ERROR = ("E0408", "Failed to delete workflow node - Please check the provided configuration")
    WORKFLOW_EDGE_DELETE_ERROR = ("E0409", "Failed to delete workflow edge - Please check the provided configuration")
    WORKFLOW_CONFIG_UPDATE_ERROR = (
        "E0410",
        "Failed to update workflow config - Please check the provided configuration",
    )
    WORKFLOW_DELETE_ERROR = ("E0411", "Failed to delete workflow - Please check the provided configuration")
    WORKFLOW_EXECUTION_ERROR = ("E0412", "Failed to execute workflow - Please check the provided configuration")

    # Business logic/Status related (10)
    WORKFLOW_VERSION_NOT_ACTIVE = ("E1001", "Specified workflow version is not active")
    WORKFLOW_VERSION_ARCHIVED = ("E1002", "Specified workflow version is archived")
