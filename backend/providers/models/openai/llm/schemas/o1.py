from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "o1",
    "label": "o1",
    "model_type": "llm",
    "group": "o1",
    "features": [
        "multi-tool-call",
        "agent-thought",
        "stream-tool-call",
        "vision",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 200000,
    },
    "parameter_rules_schema": {
        "max_tokens": {
            "_template": "max_tokens",
            "default": 50000,
            "minimum": 1,
            "maximum": 50000,
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
    "pricing": [
        {
            "input": "15.00",
            "output": "60.00",
            "unit": "0.000001",
            "currency": "USD",
        },
    ],
}
