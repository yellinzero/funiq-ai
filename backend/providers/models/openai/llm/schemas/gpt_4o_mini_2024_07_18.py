from utils.i18n import gettext_lazy as _

schema = {
    "model": "gpt-4o-mini-2024-07-18",
    "label": "gpt-4o-mini-2024-07-18",
    "model_type": "llm",
    "features": [
        "multi-tool-call",
        "agent-thought",
        "stream-tool-call",
        "vision",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 128000,
    },
    "parameter_rules_schema": {
        "temperature": {
            "_template": "temperature",
        },
        "top_p": {
            "_template": "top_p",
        },
        "presence_penalty": {
            "_template": "presence_penalty",
        },
        "frequency_penalty": {
            "_template": "frequency_penalty",
        },
        "max_tokens": {
            "_template": "max_tokens",
            "default": 512,
            "minimum": 1,
            "maximum": 16384,
        },
        "response_format": {
            "title": _("Response Format", domain="providers"),
            "type": "string",
            "description": _("specifying the format that the model must output", domain="providers"),
            "enum": [
                "text",
                "json_object",
                "json_schema",
            ],
        },
        "json_schema": {
            "_template": "json_schema",
        },
    },
    "pricing": {
        "input": "0.15",
        "output": "0.60",
        "unit": "0.000001",
        "currency": "USD",
    },
}

