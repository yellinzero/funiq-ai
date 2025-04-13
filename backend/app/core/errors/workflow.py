from app.core.errors.base import BaseErrorCode


class WorkflowErrorCode(BaseErrorCode):
    """
    Workflow related error codes (Category W)

    Error code format: Wxxxx
    - W: Category identifier for Workflow errors
    - xxxx: Four digit error code
    """

    # Not Found Errors (W00xx)
    WORKFLOW_NOT_FOUND = ("W0001", "Workflow not found with the specified ID")
    WORKFLOW_VERSION_NOT_FOUND = ("W0002", "Workflow version not found with the specified version number")
    WORKFLOW_NODE_NOT_FOUND = ("W0003", "Workflow node not found with the specified key")
    WORKFLOW_EDGE_NOT_FOUND = ("W0004", "Workflow edge not found with the specified key")
    WORKFLOW_SNAPSHOT_NOT_FOUND = ("W0005", "Workflow snapshot not found with the specified timestamp")
    # Duplicate Errors (W01xx)
    WORKFLOW_ALREADY_EXISTS = ("W0101", "A workflow with this name already exists in this tenant")
    WORKFLOW_VERSION_ALREADY_EXISTS = ("W0102", "This version number already exists for the workflow")
    WORKFLOW_NODE_KEY_DUPLICATE = ("W0103", "A node with this key already exists in the workflow")
    WORKFLOW_EDGE_KEY_DUPLICATE = ("W0104", "An edge with this key already exists in the workflow")

    # Validation Errors (W02xx)
    INVALID_WORKFLOW = ("W0201", "Invalid workflow configuration - Please check workflow settings and structure")
    INVALID_WORKFLOW_VERSION = ("W0202", "Invalid workflow version configuration - Please check version settings")
    INVALID_WORKFLOW_NODE = ("W0203", "Invalid workflow node configuration - Please check node settings")
    INVALID_WORKFLOW_EDGE = ("W0204", "Invalid workflow edge configuration - Please check edge connections")
    INVALID_VERSION_FORMAT = ("W0205", "Invalid version format - Must follow semantic versioning (e.g., 1.0.0)")
    INVALID_NODE_TYPE = ("W0206", "Invalid node type specified - Please check supported node types")
    INVALID_NODE_CONFIG = ("W0207", "Invalid node configuration - Please check required parameters")

    # State Errors (W03xx)
    WORKFLOW_DISABLED = ("W0301", "The workflow is currently disabled")
    WORKFLOW_VERSION_INACTIVE = ("W0302", "The requested workflow version is not active")
    WORKFLOW_EXECUTION_ERROR = ("W0303", "Error occurred during workflow execution - Please check execution logs")
    WORKFLOW_CYCLE_DETECTED = ("W0304", "Cycle detected in workflow graph - Workflows must be acyclic")

    # Operation Errors (W04xx)
    WORKFLOW_CREATE_ERROR = ("W0401", "Failed to create workflow - Please check the provided configuration")
    WORKFLOW_UPDATE_ERROR = ("W0402", "Failed to update workflow - Please check the provided changes")
    WORKFLOW_VERSION_PUBLISH_ERROR = (
        "W0403",
        "Failed to publish workflow version - Please check version configuration",
    )
    WORKFLOW_DELETE_ERROR = ("W0404", "Failed to delete workflow - Please ensure no active dependencies exist")
    WORKFLOW_SNAPSHOT_ERROR = ("W0405", "Failed to create workflow snapshot - Please check workflow structure")
    # Input Validation Errors (W06xx)
    WORKFLOW_INPUT_INVALID = ("W0601", "Invalid workflow input data format")
    WORKFLOW_VERSION_NOT_ACTIVE = ("W0602", "Specified workflow version is not active")

    # Execution Errors (W07xx)
    WORKFLOW_TASK_TIMEOUT = ("W0701", "Workflow task execution timed out")
