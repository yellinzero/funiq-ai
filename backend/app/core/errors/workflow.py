from app.core.errors.base import BaseErrorCode


class WorkflowErrorCode(BaseErrorCode):
    """
    Workflow related error codes
    """

    WORKFLOW_NOT_FOUND = ("E0001", "Workflow not found with the specified ID")
    WORKFLOW_VERSION_NOT_FOUND = ("E0002", "Workflow version not found with the specified version number")
    WORKFLOW_NODE_NOT_FOUND = ("E0003", "Workflow node not found with the specified key")
    WORKFLOW_EDGE_NOT_FOUND = ("E0004", "Workflow edge not found with the specified key")
    WORKFLOW_SNAPSHOT_NOT_FOUND = ("E0005", "Workflow snapshot not found with the specified timestamp")
    WORKFLOW_ALREADY_EXISTS = ("E0101", "A workflow with this name already exists in this tenant")
    WORKFLOW_VERSION_ALREADY_EXISTS = ("E0102", "This version number already exists for the workflow")
    WORKFLOW_NODE_KEY_DUPLICATE = ("E0103", "A node with this key already exists in the workflow")
    WORKFLOW_EDGE_KEY_DUPLICATE = ("E0104", "An edge with this key already exists in the workflow")

    INVALID_WORKFLOW = ("E0201", "Invalid workflow configuration - Please check workflow settings and structure")
    INVALID_WORKFLOW_VERSION = ("E0202", "Invalid workflow version configuration - Please check version settings")
    INVALID_WORKFLOW_NODE = ("E0203", "Invalid workflow node configuration - Please check node settings")
    INVALID_WORKFLOW_EDGE = ("E0204", "Invalid workflow edge configuration - Please check edge connections")
    INVALID_VERSION_FORMAT = ("E0205", "Invalid version format - Must follow semantic versioning (e.g., 1.0.0)")
    INVALID_NODE_TYPE = ("E0206", "Invalid node type specified - Please check supported node types")
    INVALID_NODE_CONFIG = ("E0207", "Invalid node configuration - Please check required parameters")

    WORKFLOW_DISABLED = ("E0301", "The workflow is currently disabled")
    WORKFLOW_VERSION_INACTIVE = ("E0302", "The requested workflow version is not active")
    WORKFLOW_EXECUTION_ERROR = ("E0303", "Error occurred during workflow execution - Please check execution logs")
    WORKFLOW_CYCLE_DETECTED = ("E0304", "Cycle detected in workflow graph - Workflows must be acyclic")

    WORKFLOW_CREATE_ERROR = ("E0401", "Failed to create workflow - Please check the provided configuration")
    WORKFLOW_UPDATE_ERROR = ("E0402", "Failed to update workflow - Please check the provided changes")
    WORKFLOW_VERSION_PUBLISH_ERROR = (
        "E0403",
        "Failed to publish workflow version - Please check version configuration",
    )
    WORKFLOW_DELETE_ERROR = ("E0404", "Failed to delete workflow - Please ensure no active dependencies exist")
    WORKFLOW_SNAPSHOT_ERROR = ("E0405", "Failed to create workflow snapshot - Please check workflow structure")
    WORKFLOW_INPUT_INVALID = ("E0601", "Invalid workflow input data format")
    WORKFLOW_VERSION_NOT_ACTIVE = ("E0602", "Specified workflow version is not active")

    WORKFLOW_TASK_TIMEOUT = ("E0701", "Workflow task execution timed out")
