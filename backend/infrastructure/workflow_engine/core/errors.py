from enum import Enum
from typing import Any


class WorkflowErrorCode(Enum):
    INITIALIZATION_ERROR = "INITIALIZATION_ERROR"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    STATE_TRANSITION_ERROR = "STATE_TRANSITION_ERROR"
    CALLBACK_ERROR = "CALLBACK_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_ERROR = "RESOURCE_ERROR"


class WorkflowError(Exception):
    def __init__(self, code: WorkflowErrorCode, message: str, details: dict[str, Any] | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code.value}] {message}")
