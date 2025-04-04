from utils.common.i18n import gettext_lazy as _

schema = {
    "name": "end",
    "label": _("End Operator"),
    "description": _("End operator"),
    "type": 'end',
    "output_schema": {
        "type": "object",
        "properties": {
            "result": {
                "type": "string",
                "description": _("The final processed output"),
            },
        },
        "required": ["result"]
    },
    "config_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}