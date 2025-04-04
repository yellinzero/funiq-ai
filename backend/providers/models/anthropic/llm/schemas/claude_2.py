from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "claude-2",
    "label": "claude-2",
    "model_type": "llm",
    "features": [
        "agent-thought",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 100000,
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
