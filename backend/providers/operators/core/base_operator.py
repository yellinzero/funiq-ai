from abc import ABC, abstractmethod
from typing import Any, Dict

from jinja2 import Environment, select_autoescape
from loguru import logger

from utils.json_schema import JSONSchema

from .mixins.convert_handling import ConvertHandlingMixin
from .mixins.schema_handling import SchemaHandlingMixin
from .mixins.validate_handling import ValidateHandlingMixin


class BaseOperator(SchemaHandlingMixin, ValidateHandlingMixin, ConvertHandlingMixin, ABC):
    """
    Base class for all operators in the system.

    This class provides common functionality for operator implementations, including:
    - Operator schema management and validation
    - Input/Output schema validation
    - Configuration management
    - Error handling and transformation
    """

    def __init__(self):
        self._config: Dict | None = None
        self._output: Dict | None = None
        self._input: Dict | None = None
        self._config_schema: JSONSchema | None = None
        self._output_schema: JSONSchema | None = None
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

    @property
    def config(self) -> Dict | None:
        return self._config

    @config.setter
    def config(self, value: Dict) -> None:
        if self.validate_config(value):
            self._config = value

    @property
    def output(self) -> Dict | None:
        return self._output

    @output.setter
    def output(self, value: Dict) -> None:
        if self.validate_output(value):
            self._output = value

    @property
    def input(self) -> Dict | None:
        return self._input

    @input.setter
    def input(self, value: Dict) -> None:
        if self.validate_input(value):
            self._input = value

    @property
    def config_schema(self) -> JSONSchema | None:
        if self._config_schema is None:
            operator_schema = self.get_operator_schema()
            self._config_schema = operator_schema.config_schema
        return self._config_schema

    @property
    def output_schema(self) -> JSONSchema | None:
        if self._output_schema is None:
            operator_schema = self.get_operator_schema()
            self._output_schema = operator_schema.output_schema
        return self._output_schema

    def get_output_schema(self) -> JSONSchema | None:
        return self.output_schema

    def get_config_schema(self) -> JSONSchema | None:
        return self.config_schema

    def get_data(self) -> Dict:
        operator_schema = self.get_operator_schema()
        return {
            "name": operator_schema.name,
            "config": self.config,
            "output": self.output,
            "config_schema": self.config_schema,
            "output_schema": self.output_schema,
        }

    def _render_template(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a template string with the given context.

        Args:
            template_str: The template string to render
            context: The context dictionary containing variables for rendering

        Returns:
            The rendered string
        """
        try:
            logger.debug(f"Rendering template: {template_str}, context: {context}")
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

    @abstractmethod
    async def _execute(self, config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Implement the actual operator logic.

        Args:
            config: Rendered and validated operator configuration
            **kwargs: Additional operator-specific arguments

        Returns:
            Dict containing the execution results
        """
        raise NotImplementedError

    async def execute(
        self, input_data: Dict[str, Any], config: Dict[str, Any], execution_context: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Execute the operator with template rendering support."""
        try:
            rendered_config = self._render_config(config=config, context=input_data)
            logger.debug(f"Rendered config: {rendered_config}")
            converted_config = self.convert_config(config=rendered_config)
            logger.debug(f"converted_config: {converted_config}")
            if not self.validate_config(config=converted_config):
                raise ValueError("Configuration validation failed")

            return await self._execute(config=converted_config, execution_context=execution_context, **kwargs)
        except (ValueError, TypeError) as e:
            logger.error(f"Configuration error: {e!s}")
            raise
        except Exception as e:
            logger.error(f"Execution error: {e!s}")
            raise
