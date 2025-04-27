from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "gpt-4.1-nano-2025-04-14",
    "label": "gpt-4.1-nano-2025-04-14",
    "model_type": "llm",
    "group": "gpt-4.1-nano",
    "features": [
        "multi-tool-call",
        "agent-thought",
        "stream-tool-call",
        "vision",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 1047576,
    },
    "parameter_rules_schema": {
        "json_schema": {
            "type": "object",
            "properties": {
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
                    "use_template": "max_tokens",
                    "default": 512,
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
                        "json_schema",
                    ],
                },
                "json_schema": {
                    "_template": "json_schema",
                },
            },
        },
    },
    "pricing": [
        {
            "input": "0.10",
            "output": "0.40",
            "unit": "0.000001",
            "currency": "USD",
        },
    ],
}
