from utils.i18n import gettext_lazy as _

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
        "required": ["model"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "answer": {
                "type": "string",
                "description": _("The answer from the LLM"),
            },
        },
        "required": ["answer"]
    }
} 