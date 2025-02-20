
schema = {
    "model": "gpt-3.5-turbo-16k",
    "label": "gpt-3.5-turbo-16k",
    "model_type": "llm",
    "features": [
        "multi-tool-call",
        "agent-thought",
        "stream-tool-call",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 16385,
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
        "max_tokens_to_sample": {
            "_template": "max_tokens",
            "default": 512,
            "minimum": 1,
            "maximum": 16385,
        },
        "response_format": {
            "_template": "response_format",
        },
    },
    "pricing": {
        "input": "0.003",
        "output": "0.004",
        "unit": "0.001",
        "currency": "USD",
    },
}
