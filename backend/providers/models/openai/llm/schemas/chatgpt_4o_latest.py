from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "chatgpt-4o-latest",
    "label": "chatgpt-4o-latest",
    "model_type": "llm",
    "group": "gpt-4o",
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
                "max_tokens_to_sample": {
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
                    ],
                },
            },
        }
    },
    "pricing": [
        {
            "input": "5",
            "output": "15",
            "unit": "0.000001",
            "currency": "USD",
        }
    ],
}
