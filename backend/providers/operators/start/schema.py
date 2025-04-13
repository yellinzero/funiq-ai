from providers.operators.core import OperatorName, OperatorType
from utils.common.i18n import gettext_lazy as _

schema = {
    "name": OperatorName.START.value,
    "label": _("Start Operator"),
    "type": OperatorType.START.value,
    "description": _("Starting point of the workflow"),
    "output_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "title": _("Question"),
                "description": _("The question to start the workflow"),
            },
        },
        "required": ["question"]
    },
    "config_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "title": _("Question"),
                "description": _("The question to start the workflow"),
            },
        },
        "required": ["question"]
    }
}
