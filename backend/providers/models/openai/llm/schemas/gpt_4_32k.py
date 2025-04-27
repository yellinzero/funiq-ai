from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "gpt-4-32k",
    "label": "gpt-4-32k",
    "model_type": "llm",
    "group": "gpt-4-32k",
    "features": [
        "multi-tool-call",
        "agent-thought",
        "stream-tool-call",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 32768,
    },
    "parameter_rules_schema": {
        "json_schema": {
            "type": "object",
            "properties": {
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
                    "maximum": 32768,
                },
                "seed": {
                    "title": _("Seed", domain="providers"),
                    "type": "number",
                    "description": _(
                        "If specified, model will make a best effort to sample deterministically, "
                        "such that repeated requests with the same seed and parameters should return the same result."
                        "Determinism is not guaranteed, and you should refer to the "
                        "system_fingerprint response parameter",
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
        },
    },
    "pricing": [
        {
            "input": "60",
            "output": "120",
            "unit": "0.001",
            "currency": "USD",
        }
    ],
}
