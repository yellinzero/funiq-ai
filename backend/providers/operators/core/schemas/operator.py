from enum import Enum
from typing import TYPE_CHECKING, Any, Union

from pydantic import BaseModel

from utils.common.i18n import TranslatableText
from utils.json_schema import JSONSchema, UiSchema


class OperatorName(str, Enum):
    """Operator type enum defining supported operator types."""

    LLM = "llm"  # Language Model operation node
    END = "end"  # Terminal node marking workflow completion
    START = "start"  # Entry point node of the workflow
    

class OperatorState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class OperatorType(str, Enum): 
    TASK = "task"
    START = "start"
    END = "end"
    LOGIC = "logic"


class OutputStreamType(str, Enum):
    SELF = "self"
    EXTERNAL = "external"


class OutputStream(BaseModel):
    enabled: bool
    type: OutputStreamType
    response_schema: dict[str, Any] | None = None


class OperatorEntity(BaseModel):
    """Model class for operator schema."""
    name: OperatorName
    label: Union[str, TranslatableText]
    type: OperatorType
    supports_input_stream: bool = False
    output_stream: OutputStream | None = None
    description: Union[str, TranslatableText]
    output_schema: JSONSchema
    config_schema: JSONSchema
    config_ui_schema: UiSchema | None = None 
    

if TYPE_CHECKING:
    from providers.operators.core.base_operator import BaseOperator


class OperatorCallbackContext:
    """Callback context containing operator execution information."""
    def __init__(
        self,
        operator: 'BaseOperator',
        input_data: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
        execution_context: dict[str, Any] | None = None,
        result: Any = None,
        error: Exception | None = None
    ):
        self.operator = operator
        self.input_data = input_data
        self.config = config
        self.execution_context = execution_context
        self.result = result
        self.error = error

    @property
    def state(self) -> 'OperatorState':
        return self.operator.state