from enum import Enum
from typing import Any, Union

from pydantic import BaseModel

from utils.common.i18n import TranslatableText
from utils.json_schema import JSONSchema, UiSchema


class OperatorName(str, Enum):
    """Operator type enum defining supported operator types."""

    LLM = "llm"  # Language Model operation node
    END = "end"  # Terminal node marking workflow completion
    START = "start"  # Entry point node of the workflow
    

class OperatorType(Enum): 
    TASK = "task"
    START = "start"
    END = "end"
    LOGIC = "logic"


class OutputStreamType(Enum):
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