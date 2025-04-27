from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "o1-mini-2024-09-12",
    "label": "o1-mini-2024-09-12",
    "model_type": "llm",
    "group": "o1-mini",
    "features": [
        "agent-thought",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 128000,
    },
    "parameter_rules_schema": {
        "json_schema": {
            "type": "object",
            "properties": {
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
        },
    },
    "pricing": [
        {
            "input": "1.10",
            "output": "4.40",
            "unit": "0.000001",
            "currency": "USD",
        },
    ],
}
