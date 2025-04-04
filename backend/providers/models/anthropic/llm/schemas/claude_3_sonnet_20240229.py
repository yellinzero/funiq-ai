from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "claude-3-sonnet-20240229",
    "label": "claude-3-sonnet-20240229",
    "model_type": "llm",
    "features": [
        "agent-thought",
        "vision",
        "tool-call",
        "stream-tool-call",
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
        "input": "3.00",
        "output": "15.00",
        "unit": "0.000001",
        "currency": "USD",
    },
}
