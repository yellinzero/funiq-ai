from providers.operators.core import OperatorName, OperatorType
from utils.common.i18n import gettext_lazy as _

schema = {
    "name": OperatorName.START.value,
    "label": _("Start Operator", domain="providers"),
    "type": OperatorType.START.value,
    "description": _("Starting point of the workflow", domain="providers"),
    "config_schema": {
        "json_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "title": _("Query"),
                    "description": _("The query to start the workflow", domain="providers"),
                },
                "image_list": {
                    "type": "array",
                    "title": _("Image List"),
                    "description": _("The list of images to send to the LLM", domain="providers"),
                    "items": {"type": "string"},
                },
                "audio_list": {
                    "type": "array",
                    "title": _("Audio List"),
                    "description": _("The list of audio files to send to the LLM", domain="providers"),
                },
                "file_list": {
                    "type": "array",
                    "title": _("File List"),
                    "description": _("The list of files to send to the LLM", domain="providers"),
                    "items": {"type": "string"},
                },
            },
            "required": ["query"],
        },
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "title": _("Query", domain="providers"),
                "description": _("The query to start the workflow", domain="providers"),
            },
            "image_list": {
                "type": "array",
                "title": _("Image List", domain="providers"),
                "description": _("The list of images to send to the LLM", domain="providers"),
                "items": {"type": "string"},
            },
            "audio_list": {
                "type": "array",
                "title": _("Audio List", domain="providers"),
                "description": _("The list of audio files to send to the LLM", domain="providers"),
                "items": {"type": "string"},
            },
            "file_list": {
                "type": "array",
                "title": _("File List", domain="providers"),
                "description": _("The list of files to send to the LLM", domain="providers"),
                "items": {"type": "string"},
            },
        },
        "required": ["query"],
    },
}
