from utils.common.i18n import gettext_lazy as _

schema = {
    "name": "llm",
    "label": _("LLM Operator"),
    "description": _("Large Language Model operator"),
    "type": 'ai',
    "config_schema": {
        "type": "object",
        "properties": {
            "model_id": {
                "type": "string",
                "title": _("Model"),
                "description": _("The LLM model to use"),
            },
            "prompt": {
                "type": "string",
                "title": _("Prompt"),
                "description": _("The prompt to send to the LLM"),
            },
        },
        "required": ["model_id", "prompt"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "description": _("The type of the LLM result"),
            },
            "answer": {
                "type": "string",
                "description": _("The answer from the LLM"),
            },
            "usage": {
                "type": "object",
                "description": _("The usage information from the LLM"),
            },
        },
        "required": ["type", "answer", "usage"]
    }
} 