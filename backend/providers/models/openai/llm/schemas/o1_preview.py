from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "o1-preview",
    "label": "o1-preview",
    "model_type": "llm",
    "features": [
        "agent-thought",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 128000,
    },
    "parameter_rules_schema": {
        "max_tokens": {
            "_template": "max_tokens",
            "default": 32768,
            "minimum": 1,
            "maximum": 32768,
        },
        "response_format": {
            "title": _("Response Format", domain="providers"),
            "type": "string",
            "description": _("specifying the format that the model must output", domain="providers"),
            "enum": [
                "text",
                "json_object",
            ],
        },
    },
    "pricing": {
        "input": "15.00",
        "output": "60.00",
        "unit": "0.000001",
        "currency": "USD",
    },
}
