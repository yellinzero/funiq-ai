from typing import Any, Dict

from jinja2 import Environment, select_autoescape
from loguru import logger


class TemplateHandlingMixin:
    """Mixin class for handling template rendering."""
    
    def _init_jinja_env(self):
        # Initialize Jinja2 environment
        self._jinja_env = Environment(
            autoescape=select_autoescape(["html", "xml"]),
            keep_trailing_newline=True,
            # Add useful built-in functions and filters
            extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"],
            # Enable optimization
            optimized=True,
            # Configure flexible syntax
            variable_start_string="{{",
            variable_end_string="}}",
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Add custom filters and global functions
        self._jinja_env.filters.update(
            {
                "int": int,
                "float": float,
                "str": str,
                "bool": bool,
            }
        )
        
    def _render_template(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a template string with the given context.

        Args:
            template_str: The template string to render
            context: The context dictionary containing variables for rendering

        Returns:
            The rendered string
        """
        try:
            if not isinstance(template_str, str):
                return template_str
            if "{{" not in template_str:
                return template_str

            template = self._jinja_env.from_string(template_str.strip())
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template '{template_str}': {e!s}")
            raise ValueError(f"Template rendering error: {e!s}") from e

    def _render_config(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively render all template strings in the config dictionary.

        Args:
            config: The configuration dictionary containing template strings
            context: The context dictionary containing variables for rendering

        Returns:
            The rendered configuration dictionary
        """
        rendered_config = {}
        for key, value in config.items():
            if isinstance(value, dict):
                rendered_config[key] = self._render_config(value, context)
            elif isinstance(value, list):
                rendered_config[key] = [
                    self._render_config(item, context)
                    if isinstance(item, dict)
                    else self._render_template(item, context)
                    for item in value
                ]
            else:
                rendered_config[key] = self._render_template(value, context)
        return rendered_config