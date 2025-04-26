from pydantic import BaseModel, Field

from providers.models.core.schemas import AssistantPromptMessage
from providers.operators.core import OperatorName, OperatorType
from utils.common.i18n import gettext_lazy as _


class EndOperatorStreamOutput(BaseModel):
    message: AssistantPromptMessage
    finish_reason: str | None = Field(None, description=_("The reason the LLM stopped generating", domain="providers"))


class EndOperatorOutput(BaseModel):
    message: AssistantPromptMessage


schema = {
    "name": OperatorName.END.value,
    "label": _("End Operator"),
    "description": _("End operator"),
    "type": OperatorType.END.value,
    "output_stream": {
        "enabled": True,
        "chunk_schema": EndOperatorStreamOutput.model_json_schema(),
    },
    "config_schema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": _("The final processed output", domain="providers"),
            },
        },
        "required": ["message"],
    },
    "output_schema": EndOperatorOutput.model_json_schema(),
}
