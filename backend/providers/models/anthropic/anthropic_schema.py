from utils.i18n import gettext_lazy as _

schema = {
    "provider": "anthropic",
    "label": _("Anthropic", domain="providers"),
    "description": _("Anthropic's powerful models, such as Claude 3.", domain="providers"),
    "icon": {"small": "icon_s.svg", "large": "icon_l.svg"},
    "docs": {
        "title": _("Get your API Key from Anthropic", domain="providers"),
        "url": "https://console.anthropic.com/account/keys",
    },
    "supported_model_types": ["llm"],
    "configurate_methods": ["predefined"],
    "credential_schema": {
        "type": "object",
        "properties": {
            "anthropic_api_key": {
                "type": "string",
                "title": _("API Key", domain="providers"),
                "format": "password",
                "minLength": 1,
            },
            "anthropic_api_url": {
                "type": "string",
                "title": _("API URL", domain="providers"),
            },
        },
        "required": ["anthropic_api_key"],
    },
}


ui_schema = {
    "credential_schema": {
        "anthropic_api_key": {
            "ui:placeholder": _("Enter your API Key", domain="providers"),
        },
        "anthropic_api_url": {
            "ui:placeholder": _("Enter your API URL", domain="providers"),
        },
    },
}
