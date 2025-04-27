from utils.common.i18n import gettext_lazy as _

schema = {
    "provider": "openai",
    "label": _("OpenAI", domain="providers"),
    "description": _("Models provided by OpenAI.", domain="providers"),
    "icon": {"small": "icon_s.svg", "large": "icon_l.svg"},
    "docs": [{
        "title": _("Get your API Key from OpenAI", domain="providers"),
        "url": "https://platform.openai.com/account/api-keys",
    }],
    "model_types": ["llm", "text-embedding", "speech2text", "moderation", "tts"],
    "config_schema": {
        "json_schema": {
            "type": "object",
            "properties": {
                "openai_api_key": {
                    "type": "string",
                    "title": _("API Key", domain="providers"),
                    "format": "password",
                },
                "openai_organization": {
                    "type": "string",
                    "title": _("Organization ID", domain="providers"),
                },
                "openai_api_base": {
                    "type": "string",
                    "format": "uri",
                    "title": _("API Base", domain="providers"),
                    "description": _("Enter your API Base, e.g. https://api.openai.com", domain="providers"),
                },
            },
            "required": ["openai_api_key"],
        },
        "ui_schema": {
            "openai_api_key": {
                "ui:placeholder": _("Enter your API Key", domain="providers"),
            },
            "openai_organization": {
                "ui:placeholder": _("Enter your Organization ID", domain="providers"),
            },
        },
    },
}
