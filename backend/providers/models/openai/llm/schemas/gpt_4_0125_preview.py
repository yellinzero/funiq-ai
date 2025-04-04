from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "gpt-4-0125-preview",
    "label": "gpt-4-0125-preview",
    "model_type": "llm",
    "features": [
        "multi-tool-call",
        "agent-thought",
        "stream-tool-call",
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
        "seed": {
            "title": _("Seed", domain="providers"),
            "type": "number",
            "description": _(
                "If specified, model will make a best effort to sample deterministically, "
                "such that repeated requests with the same seed and parameters should return the same result."
                "Determinism is not guaranteed, and you should refer to the system_fingerprint response parameter",
                "to monitor changes in the backend.",
                domain="providers",
            ),
        },
        "response_format": {
            "title": _("Response Format", domain="providers"),
            "type": "string",
            "description": _("specifying the format that the model must output", domain="providers"),
            "enum": [
                "text",
                "json_object",
            ],
        },
    },
    "pricing": {
        "input": "0.01",
        "output": "0.03",
        "unit": "0.001",
        "currency": "USD",
    },
}
