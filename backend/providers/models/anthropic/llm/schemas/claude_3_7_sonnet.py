from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "claude-3-7-sonnet-20250219",
    "label": "claude-3-7-sonnet",
    "model_type": "llm",
    "features": [
        "agent-thought",
        "vision",
        "tool-call",
        "stream-tool-call",
        "document",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 200000,
    },
    "parameter_rules_schema": {
        "json_schema": {
            "type": "object",
            "properties": {
                "thinking": {
                    "type": "boolean",
                    "title": _("Thinking", domain="providers"),
                    "description": _(
                        "Controls the model's thinking capability. "
                        "When enabled, temperature, top_p and top_k will be disabled.",
                        domain="providers",
                    ),
                    "default": False,
                },
                "thinking_budget": {
                    "type": "int",
                    "title": _("Thinking Budget", domain="providers"),
                    "description": _(
                        "Budget limit for thinking (minimum 1024), must be less than max_tokens. "
                        "Only available when thinking mode is enabled.",
                        domain="providers",
                    ),
                    "default": 1024,
                    "minimum": 0,
                    "maximum": 128000,
                },
                "temperature": {
                    "_template": "temperature",
                },
                "top_p": {
                    "_template": "top_p",
                },
                "top_k": {
                    "type": "int",
                    "title": _("Top k", domain="providers"),
                    "description": _(
                        "Only sample from the top K options for each subsequent token.", domain="providers"
                    ),
                },
                "max_tokens": {
                    "_template": "max_tokens",
                },
                "response_format": {
                    "_template": "response_format",
                },
            },
        }
    },
    "pricing": [
        {
            "input": "3.00",
            "output": "15.00",
            "unit": "0.000001",
            "currency": "USD",
        },
    ],
}
