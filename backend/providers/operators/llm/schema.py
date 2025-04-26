from providers.models.core.schemas import LLMResult, LLMResultChunk
from providers.operators.core import OperatorName, OperatorType
from utils.common.i18n import gettext_lazy as _

schema = {
    "name": OperatorName.LLM.value,
    "label": _("LLM Operator"),
    "description": _("Large Language Model operator"),
    "type": OperatorType.TASK.value,
    "output_stream": {
        "enabled": True,
        "chunk_schema": LLMResultChunk.model_json_schema(),
    },
    "config_schema": {
        "type": "object",
        "properties": {
            "model": {
                "type": "object",
                "title": _("Model"),
                "description": _("The LLM model to use"),
                "properties": {
                    "provider": {
                        "type": "string",
                        "maxLength": 50
                    },
                    "model": {
                        "type": "string",
                        "maxLength": 50
                    }
                },
                "required": ["provider", "model"]
            },
            "image_list": {
                "type": "array",
                "title": _("Image List"),
                "description": _("The list of images to send to the LLM"),
                "items": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string"
                        },
                        "detail": {
                            "type": "string",
                            "enum": [
                                "low", "high"
                            ]
                        }
                    }
                },
            },
            "audio_list": {
                "type": "array",
                "title": _("Audio List"),
                "description": _("The list of audio files to send to the LLM"),
                "items": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string"
                        },
                        "format": {
                            "type": "string",
                            "enum": [
                                "mp3", "wav"
                            ]
                        }
                    }
                },
            },
            "file_list": {
                "type": "array",
                "title": _("File List"),
                "description": _("The list of files to send to the LLM"),
                "items": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string"
                        },
                        "file_name": {
                            "type": "string"
                        }
                    }
                },
            },
            "tool_list": {
                "type": "array",
                "title": _("Tool List"),
                "description": _("The list of tools to send to the LLM"),
                "items": {
                    "type": "string"
                },
            },
            "stop": {
                "type": "array",
                "title": _("Stop"),
                "description": _("The stop words to send to the LLM"),
                "items": {
                    "type": "string"
                },
            },
            "prompt": {
                "type": "string",
                "title": _("Prompt"),
                "description": _("The prompt to send to the LLM"),
            },
            "query": {
                "type": "string",
                "title": _("Query"),
                "description": _("The query to send to the LLM"),
            },
        },
        "required": ["model", "query"],
    },
    "output_schema": LLMResult.model_json_schema(),
}
