from utils.i18n import gettext_lazy as _

schema = {
    "model": "deepseek-chat",
    "label": "deepseek-chat",
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
            "default": 1,
            "minimum": 0.0,
            "maximum": 2.0,
            "description": _(
                "Control the diversity and randomness of generated results. "
                "The smaller the value, the more rigorous it is; "
                "the larger the value, the more divergent it is.",
                domain="providers",
            ),
        },
        "max_tokens_to_sample": {
            "_template": "max_tokens",
            "default": 4096,
            "minimum": 1,
            "maximum": 8192,
            "description": _(
                "Specifies the upper limit on the length of generated results. "
                "If the generated results are truncated, you can increase this parameter.",
                domain="providers",
            ),
        },
        "top_p": {
            "_template": "top_p",
            "default": 1,
            "minimum": 0.01,
            "maximum": 1.00,
            "description": _(
                "Control the randomness of generated results. "
                "The smaller the value, the weaker the randomness; "
                "the larger the value, the stronger the randomness. "
                "Generally speaking, you can adjust one of the two parameters top_p and temperature.",
                domain="providers",
            ),
        },
        "logprobs": {
            "title": _("Log Probabilities", domain="providers"),
            "type": "boolean",
            "description": _(
                "Whether to return the log probability of the output token. "
                "If true, returns the log probability of each output token in the content of message.",
                domain="providers",
            ),
        },
        "top_logprobs": {
            "title": _("Top Log Probabilities", domain="providers"),
            "type": "number",
            "default": 0,
            "minimum": 0,
            "maximum": 20,
            "description": _(
                "An integer N between 0 and 20, specifying that each output position returns the top N tokens"
                "with output probability, and returns the logarithmic probability of these tokens. "
                "When specifying this parameter, logprobs must be true.",
                domain="providers",
            ),
        },
        "frequency_penalty": {
            "_template": "frequency_penalty",
            "default": 0,
            "minimum": -2.0,
            "maximum": 2.0,
            "description": _(
                "A number between -2.0 and 2.0. "
                "If the value is positive, new tokens are penalized based"
                "on their frequency of occurrence in existing text,"
                "reducing the likelihood that the model will repeat the same content.",
                domain="providers",
            ),
        },
        "response_format": {
            "title": _("Response Format", domain="providers"),
            "type": "string",
            "description": _(
                "specifying the format that the model must output",
                domain="providers",
            ),
        },
    },
    "pricing": {
        "input": "1",
        "output": "2",
        "unit": "0.000001",
        "currency": "RMB",
    },
}