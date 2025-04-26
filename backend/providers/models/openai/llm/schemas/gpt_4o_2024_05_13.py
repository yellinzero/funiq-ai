schema = {
    "model": "gpt-4o-2024-05-13",
    "label": "gpt-4o-2024-05-13",
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
            "_template": "max_tokens",
            "default": 512,
            "minimum": 1,
            "maximum": 4096,
        },
    },
    "pricing": [{
        "input": "5",
        "output": "15",
        "unit": "0.000001",
        "currency": "USD",
    }],
}
