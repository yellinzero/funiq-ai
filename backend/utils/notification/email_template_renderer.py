import pathlib
from functools import cache
from typing import Union

import jinja2

from utils.common.i18n import NullTranslations, get_current_locale_translator, translation_registry


class EmailTemplateRenderer:
    def __init__(self, template_dir: Union[str, pathlib.Path]):
        """
        Initialize the template renderer.

        :param template_dir: Path to the directory containing template files.
        """
        self.template_dir = pathlib.Path(__file__).resolve().parent.parent.parent / template_dir
        self.environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=True,
            extensions=["jinja2.ext.i18n"],
        )

        def get_translations():
            locale_translator = get_current_locale_translator()

            locale_code = locale_translator.language
            if locale_translator.territory:
                locale_code = f"{locale_translator.language}_{locale_translator.territory}"

            return translation_registry.translations.get("templates", {}).get(locale_code, NullTranslations())

        # install translations
        self.environment.install_gettext_callables(
            lambda x: get_translations().ugettext(x),
            lambda s, p, n: get_translations().ungettext(s, p, n),
        )

    def render(self, template_name: str, **context) -> str:
        """
        Render a template file with the given context.

        :param template_name: Name of the template file.
        :param context: Context variables to be passed to the template.
        :return: Rendered template as a string.
        """
        try:
            template = _get_template(self, template_name)
            return template.render(**context)
        except jinja2.TemplateError as e:
            raise RuntimeError(f"Error rendering template '{template_name}': {e}") from e

    def render_string(self, template_string: str, **context) -> str:
        """
        Render a template string with the given context.

        :param template_string: Template content as a string.
        :param context: Context variables to be passed to the template.
        :return: Rendered template as a string.
        """
        try:
            template = jinja2.Template(template_string)
            return template.render(**context)
        except jinja2.TemplateError as e:
            raise RuntimeError(f"Error rendering template string: {e}") from e


@cache
def _get_template(template_renderer: EmailTemplateRenderer, template_name: str) -> jinja2.Template:
    """
    Load and cache the Jinja2 template by name.

    :param template_name: Name of the template file.
    :return: Compiled Jinja2 template.
    """
    try:
        return template_renderer.environment.get_template(template_name)
    except jinja2.TemplateNotFound as err:
        raise FileNotFoundError(f"Template '{template_name}' not found in {template_renderer.template_dir}") from err


email_template_renderer = EmailTemplateRenderer("/infrastructure/email/templates")
