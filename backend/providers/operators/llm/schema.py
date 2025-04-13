from providers.models.core.models import LLMResult, LLMResultChunk
from providers.operators.core import OperatorName, OperatorType, OutputStreamType
from utils.common.i18n import gettext_lazy as _

schema = {
    "name": OperatorName.LLM.value,
    "label": _("LLM Operator"),
    "description": _("Large Language Model operator"),
    "type": OperatorType.TASK.value,
    "output_stream": {
        "enabled": True,
        "type": OutputStreamType.SELF.value,
        "response_schema": LLMResultChunk.model_json_schema(),
    },
    "config_schema": {
        "type": "object",
        "properties": {
            "model_id": {
                "type": "string",
                "title": _("Model"),
                "description": _("The LLM model to use"),
            },
            "prompt": {
                "type": "string",
                "title": _("Prompt"),
                "description": _("The prompt to send to the LLM"),
            },
        },
        "required": ["model_id", "prompt"],
    },
    "output_schema": LLMResult.model_json_schema(),
}
