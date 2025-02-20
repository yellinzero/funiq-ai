
schema = {
    "model": "text-davinci-003",
    "label": "text-davinci-003",
    "model_type": "llm",
    "features": [],
    "model_properties": {
        "mode": "completion",
        "context_size": 4096,
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
    "pricing": {
        "input": "0.001",
        "output": "0.002",
        "unit": "0.001",
        "currency": "USD",
    },
}
