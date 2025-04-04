from utils.common.i18n import gettext_lazy as _

schema = {
  "provider": "deepseek",
  "label": _("DeepSeek", domain="providers"),
  "description": _("Models provided by deepseek, such as deepseek-chat、deepseek-coder.", domain="providers"),
  "icon": {
    "small": "icon_s.svg",
    "large": "icon_l.svg"
  },
  "docs": {
    "title": _("Get your API Key from deepseek", domain="providers"),
    "url": "https://platform.deepseek.com/api_keys"
  },
  "supported_model_types": [
    "llm"
  ],
  "configurate_methods": [
    "predefined"
  ],
  "credential_schema": {
    "type": "object",
    "properties": {
      "api_key": {
        "type": "string",
        "title": _("API Key", domain="providers"),
        "format": "password",
      },
      "endpoint_url": {
        "type": "string",
        "format": "uri",
        "title": _("Custom API endpoint URL", domain="providers"),
        "description": _("Base URL, e.g. https://api.deepseek.com/v1 or https://api.deepseek.com", domain="providers")
      }
    },
    "required": [
      "api_key"
    ]
  }
}

ui_schema = {
  "credential_schema": {
    "api_key": {
      "ui:placeholder": _("Enter your API Key", domain="providers"),
    },
  },
}
