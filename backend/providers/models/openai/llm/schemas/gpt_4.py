from utils.common.i18n import gettext_lazy as _

schema = {
    "model": "gpt-4",
    "label": "gpt-4",
    "model_type": "llm",
    "group": "gpt-4",
    "features": [
        "multi-tool-call",
        "agent-thought",
        "stream-tool-call",
    ],
    "model_properties": {
        "mode": "chat",
        "context_size": 8192,
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
                "max_tokens": {
                    "_template": "max_tokens",
                    "default": 512,
                    "minimum": 1,
                    "maximum": 8192,
                },
                "seed": {
                    "title": _("Seed", domain="providers"),
                    "type": "number",
                    "description": _(
                        "If specified, model will make a best effort to sample deterministically, "
                        "such that repeated requests with the same seed and parameters should return the same result."
                        "Determinism is not guaranteed, and you should refer to "
                        "the system_fingerprint response parameter "
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
            "input": "30",
            "output": "60",
            "unit": "0.000001",
            "currency": "USD",
        }
    ],
}
