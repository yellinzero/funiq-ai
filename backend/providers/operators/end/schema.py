from providers.operators.core import OperatorName, OperatorType, OutputStreamType
from utils.common.i18n import gettext_lazy as _

schema = {
    "name": OperatorName.END.value,
    "label": _("End Operator"),
    "description": _("End operator"),
    "type": OperatorType.END.value,
    "supports_input_stream": True,
    "output_stream": {
        "enabled": True,
        "type": OutputStreamType.EXTERNAL.value,
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "result": {
                "type": "string",
                "description": _("The final processed output"),
            },
        },
        "required": ["result"]
    },
    "config_schema": {
        "type": "object",
        "properties": {
            "result": {
                "type": "string",
                "description": _("The final processed output"),
            },
        },
        "required": ["result"]
    }
}