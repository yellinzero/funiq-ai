from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "o3-mini",
    "label": "o3-mini",
    "model_type": "llm",
    "group": "o3-mini",
    "features": [
        "multi-tool-call",
        "agent-thought",
        "stream-tool-call",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 200000,
    },
    "parameter_rules_schema": {
        "json_schema": {
            "type": "object",
            "properties": {
                "max_tokens": {
                    "use_template": "max_tokens",
                    "default": 100000,
                    "minimum": 1,
                    "maximum": 100000,
                },
                "reasoning": {
                    "title": _("Reasoning Effort", domain="providers"),
                    "type": "string",
                    "description": _("constrains effort on reasoning for reasoning models", domain="providers"),
                    "enum": [
                        "low",
                        "medium",
                        "high",
                    ],
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
                "json_schema": {
                    "_template": "json_schema",
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
