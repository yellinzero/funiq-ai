from utils.i18n import gettext_lazy as _

schema = {
    "model": "o1-mini",
    "label": "o1-mini",
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
            "default": 65536,
            "minimum": 1,
            "maximum": 65536,
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
        "input": "3.00",
        "output": "12.00",
        "unit": "0.000001",
        "currency": "USD",
    },
}

