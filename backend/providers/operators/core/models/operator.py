from enum import Enum
from typing import Union

from pydantic import BaseModel

from utils.common.i18n import TranslatableText
from utils.json_schema import JSONSchema, UiSchema


class OperatorType(Enum): 
    TASK = "ai"
    START = "start"
    END = "end"
    LOGIC = "logic"
    

class OperatorStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"
    WARNING = "warning"
    

class OperatorEntity(BaseModel):
    """Model class for operator schema."""
    name: str
    label: Union[str, TranslatableText]
    type: OperatorType
    status: OperatorStatus | None = None
    description: Union[str, TranslatableText]
    output_schema: JSONSchema
    config_schema: JSONSchema
    config_ui_schema: UiSchema | None = None 