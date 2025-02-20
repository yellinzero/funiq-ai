
schema = {
    "model": "gpt-3.5-turbo-0613",
    "label": "gpt-3.5-turbo-0613",
    "model_type": "llm",
    "features": [
        "multi-tool-call",
        "agent-thought",
        "stream-tool-call",
    ],
    "model_properties": {
        "mode": "chat",
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
        "max_tokens_to_sample": {
            "_template": "max_tokens",
            "default": 512,
            "minimum": 1,
            "maximum": 4096,
        },
        "response_format": {
            "_template": "response_format",
        },
    },
    "pricing": {
        "input": "0.0015",
        "output": "0.002",
        "unit": "0.001",
        "currency": "USD",
    },
    "deprecated": True,
}
