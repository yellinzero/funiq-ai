from utils.i18n import gettext_lazy as _

schema = {
    "name": "start",
    "label": _("Start Operator"),
    "type": 'start',
    "description": _("Starting point of the workflow"),
    "output_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "title": _("Question"),
                "description": _("The question to start the workflow"),
            },
        },
        "required": ["question"]
    },
    "config_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
