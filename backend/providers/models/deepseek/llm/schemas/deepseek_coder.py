schema = {
    "model": "deepseek-coder",
    "label": "deepseek-coder",
    "model_type": "llm",
    "features": [
        "agent-thought",
        "multi-tool-call",
        "stream-tool-call",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 128000,
    },
    "parameter_rules_schema": {
        "temperature": {
            "_template": "temperature",
            "minimum": 0,
            "maximum": 1,
            "default": 0.5,
        },
        "top_p": {
            "_template": "top_p",
            "minimum": 0,
            "maximum": 1,
            "default": 1,
        },
        "max_tokens_to_sample": {
            "_template": "max_tokens",
            "minimum": 1,
            "maximum": 4096,
            "default": 1024,
        },
    },
}
