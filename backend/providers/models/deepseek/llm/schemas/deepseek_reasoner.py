schema = {
    "model": "deepseek-reasoner",
    "label": "deepseek-reasoner",
    "model_type": "llm",
    "features": [
        "agent-thought",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 128000,
    },
    "parameter_rules_schema": {
        "json_schema": {
            "type": "object",
            "properties": {
                "max_tokens": {
                    "_template": "max_tokens",
                    "minimum": 1,
                    "maximum": 8192,
                    "default": 4096,
                },
            },
        }
    },
    "pricing": [
        {
            "input": "1",
            "output": "16",
            "unit": "0.000001",
            "currency": "CNY",
        },
        {
            "input": "0.25",
            "output": "4",
            "unit": "0.000001",
            "currency": "CNY",
        },
    ],
}
