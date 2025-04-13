from abc import ABC, abstractmethod
from typing import Any, Dict

from loguru import logger

from utils.json_schema import JSONSchema

from .mixins import (
    ConvertHandlingMixin,
    SchemaHandlingMixin,
    StreamHandlingMixin,
    TemplateHandlingMixin,
    ValidateHandlingMixin,
)


class BaseOperator(
    SchemaHandlingMixin,
    ValidateHandlingMixin,
    ConvertHandlingMixin,
    TemplateHandlingMixin,
    StreamHandlingMixin,
    ABC,
):
    """
    Base class for all operators in the system.

    This class provides common functionality for operator implementations, including:
    - Operator schema management and validation
    - Input/Output schema validation
    - Configuration management
    - Error handling and transformation
    """

    def __init__(self):
        self._config_schema: JSONSchema | None = None
        self._output_schema: JSONSchema | None = None
        self._execution_context: Dict[str, Any] = {}
        self._init_jinja_env()

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

    @property
    def execution_context(self) -> Dict[str, Any]:
        return self._execution_context

    async def execute(
        self, input_data: Dict[str, Any], config: Dict[str, Any], execution_context: Dict[str, Any], **kwargs
    ):
        self._execution_context = execution_context
        """Execute the operator with template rendering support."""
        if self.has_stream_inputs and not self.supports_input_stream:
            raise ValueError("Operator does not support stream inputs")
        if self.is_stream and not self.supports_output_stream:
            raise ValueError("Operator does not support stream outputs")

        non_stream_inputs, stream_inputs = self.prepare_stream_handling(input_data=input_data)
        try:
            converted_config = None
            if config and any(config.values()):
                rendered_config = self._render_config(config=config, context=non_stream_inputs)
                converted_config = self.convert_config(config=rendered_config)
                if not self.validate_config(config=converted_config):
                    raise ValueError("Configuration validation failed")

            all_inputs = {**non_stream_inputs, **stream_inputs}
            return await self._execute(
                config=converted_config, input_data=all_inputs, execution_context=self.execution_context, **kwargs
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Configuration error: {e!s}")
            raise
        except Exception as e:
            logger.error(f"Execution error: {e!s}")
            raise

    @abstractmethod
    async def _execute(
        self, config: Dict[str, Any] | None, **kwargs
    ):
        """Implement the actual operator logic.

        Args:
            config: Rendered and validated operator configuration
            **kwargs: Additional operator-specific arguments

        Returns:
            Dict containing the execution results
        """
        raise NotImplementedError
