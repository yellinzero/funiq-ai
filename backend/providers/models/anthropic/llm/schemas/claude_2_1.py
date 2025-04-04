from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "claude-2.1",
    "label": "claude-2.1",
    "model_type": "llm",
    "features": [
        "agent-thought",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 200000,
    },
    "parameter_rules_schema": {
        "temperature": {
            "_template": "temperature",
        },
        "top_p": {
            "_template": "top_p",
        },
        "top_k": {
            "description": _("Only sample from the top K options for each subsequent token.", domain="providers"),
        },
        "max_tokens_to_sample": {
            "_template": "max_tokens",
            "required": True,
            "default": 4096,
            "minimum": 1,
            "maximum": 4096,
        },
        "response_format": {
            "_template": "response_format",
        },
    },
    "pricing": {
        "input": "8.00",
        "output": "24.00",
        "unit": "0.000001",
        "currency": "USD",
    },
}
