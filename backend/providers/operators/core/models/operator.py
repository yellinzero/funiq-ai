from enum import Enum
from typing import Union

from pydantic import BaseModel

from utils.i18n import TranslatableText
from utils.json_schemas.base import JSONSchema
from utils.json_schemas.ui_base import UiSchema


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
    ui_schema: UiSchema | None = None 