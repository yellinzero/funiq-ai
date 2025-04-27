from app.core.errors.base import BaseErrorCode


class WorkflowErrorCode(BaseErrorCode):
    """
    Workflow related errors (Category E)
    """
    # Input/Parameter validation (02)
    INVALID_VERSION_FORMAT = ("E0201", "Invalid version format - Must follow semantic versioning (e.g., 1.0.0)")
    INVALID_NODE_TYPE = ("E0202", "Invalid node type specified - Please check supported node types")
    WORKFLOW_INPUT_INVALID = ("E0203", "Invalid workflow input data format")
    
    # Resource related (03)
    WORKFLOW_NOT_FOUND = ("E0301", "Workflow not found with the specified ID")
    WORKFLOW_VERSION_NOT_FOUND = ("E0302", "Workflow version not found with the specified version number")
    WORKFLOW_NODE_NOT_FOUND = ("E0303", "Workflow node not found with the specified key")
    WORKFLOW_EDGE_NOT_FOUND = ("E0304", "Workflow edge not found with the specified key")
    WORKFLOW_SNAPSHOT_NOT_FOUND = ("E0305", "Workflow snapshot not found with the specified timestamp")
    WORKFLOW_ALREADY_EXISTS = ("E0306", "A workflow with this name already exists in this tenant")
    WORKFLOW_VERSION_ALREADY_EXISTS = ("E0307", "This version number already exists for the workflow")
    WORKFLOW_NODE_KEY_DUPLICATE = ("E0308", "A node with this key already exists in the workflow")
    WORKFLOW_EDGE_KEY_DUPLICATE = ("E0309", "An edge with this key already exists in the workflow")
    
    # Operation related (04)
    WORKFLOW_CREATE_ERROR = ("E0401", "Failed to create workflow - Please check the provided configuration")
    WORKFLOW_UPDATE_ERROR = ("E0402", "Failed to update workflow - Please check the provided changes")
    WORKFLOW_DELETE_ERROR = ("E0403", "Failed to delete workflow - Please ensure no active dependencies exist")
    WORKFLOW_VERSION_PUBLISH_ERROR = (
        "E0404",
        "Failed to publish workflow version - Please check version configuration"
    )
    WORKFLOW_SAVE_ERROR = ("E0405", "Failed to save workflow - Please check the provided configuration")
    WORKFLOW_SNAPSHOT_ERROR = ("E0406", "Failed to create workflow snapshot - Please check workflow structure")
    
    # Data processing & validation (07)
    WORKFLOW_EXECUTION_ERROR = ("E0701", "Error occurred during workflow execution - Please check execution logs")
    WORKFLOW_TASK_TIMEOUT = ("E0702", "Workflow task execution timed out")
    
    # Configuration related (08)
    INVALID_WORKFLOW = ("E0801", "Invalid workflow configuration - Please check workflow settings and structure")
    INVALID_WORKFLOW_VERSION = ("E0802", "Invalid workflow version configuration - Please check version settings")
    INVALID_WORKFLOW_NODE = ("E0803", "Invalid workflow node configuration - Please check node settings")
    INVALID_WORKFLOW_EDGE = ("E0804", "Invalid workflow edge configuration - Please check edge connections")
    INVALID_NODE_CONFIG = ("E0805", "Invalid node configuration - Please check required parameters")
    
    # Business logic/Status related (10)
    WORKFLOW_DISABLED = ("E1001", "The workflow is currently disabled")
    WORKFLOW_VERSION_INACTIVE = ("E1002", "The requested workflow version is not active")
    WORKFLOW_VERSION_NOT_ACTIVE = ("E1003", "Specified workflow version is not active")
    WORKFLOW_CYCLE_DETECTED = ("E1004", "Cycle detected in workflow graph - Workflows must be acyclic")