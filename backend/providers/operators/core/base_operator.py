from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator
from typing import Any, Callable, Coroutine, Dict, List

from .mixins import (
    ConvertHandlingMixin,
    LifecycleHandlingMixin,
    SchemaHandlingMixin,
    StreamHandlingMixin,
    TemplateHandlingMixin,
    ValidateHandlingMixin,
)
from .schemas import OperatorCallbackContext, OperatorConfigSchema, OperatorState


class BaseOperator(
    SchemaHandlingMixin,
    ValidateHandlingMixin,
    ConvertHandlingMixin,
    TemplateHandlingMixin,
    StreamHandlingMixin,
    LifecycleHandlingMixin,
    ABC,
):
    """
    Base class for all operators in the system.

    This class provides common functionality for operator implementations, including:
    - Operator schema management and validation
    - Input/Output schema validation
    - Configuration management
    - Error handling and transformation
    - Lifecycle management with callbacks
    """

    def __init__(self):
        self._config_schema: dict | None = None
        self._output_schema: dict | None = None
        self._execution_context: Dict[str, Any] = {}
        self._config_value_paths_map: Dict[str, List[str]] = {}
        self._stream_node_ids: List[str] = []
        self._init_jinja_env()
        
        self._on_created_callbacks: List[Callable[[OperatorCallbackContext], Coroutine[Any, Any, None]]] = []
        self._on_running_callbacks: List[Callable[[OperatorCallbackContext], Coroutine[Any, Any, None]]] = []
        self._on_completed_callbacks: List[Callable[[OperatorCallbackContext], Coroutine[Any, Any, None]]] = []
        self._on_failed_callbacks: List[Callable[[OperatorCallbackContext], Coroutine[Any, Any, None]]] = []
        self._state: OperatorState = OperatorState.CREATED
        self._initialized = False

    async def initialize(self):
        """Async initialization method that must be called before execution."""
        if self._initialized:
            return
            
        await self.on_created(
            OperatorCallbackContext(
                operator=self,
                execution_context=self._execution_context
            )
        )
        self._initialized = True
        
    @property
    def config_schema(self) -> OperatorConfigSchema | None:
        if self._config_schema is None:
            operator_schema = self.get_operator_schema()
            self._config_schema = operator_schema.config_schema
        return self._config_schema

    @property
    def output_schema(self) -> dict | None:
        if self._output_schema is None:
            operator_schema = self.get_operator_schema()
            self._output_schema = operator_schema.output_schema
        return self._output_schema

    @property
    def execution_context(self) -> Dict[str, Any]:
        return self._execution_context

    @property
    def state(self) -> OperatorState:
        """Get the current state of the operator."""
        return self._state

    async def execute(
        self, input_data: Dict[str, Any], config: Dict[str, Any], execution_context: Dict[str, Any], **kwargs
    ):
        """Execute the operator with lifecycle management and template rendering support."""
        self._execution_context = execution_context
        
        if self.is_stream and not self.supports_output_stream:
            raise ValueError("Operator does not support stream outputs")

        try:
            context = OperatorCallbackContext(
                operator=self,
                input_data=input_data,
                config=config,
                execution_context=execution_context
            )
            await self.on_running(context)

            non_stream_inputs, stream_inputs = self.prepare_stream_handling(input_data=input_data)
            self._analyze_config_paths(config=config)
            non_stream_config = self._filter_non_stream_config(config=config)
            converted_config = None
            if non_stream_config and any(non_stream_config.values()):
                rendered_config = self._render_config(config=non_stream_config, context=non_stream_inputs)
                converted_config = self.convert_config(config=rendered_config)
                if not self.validate_config(config=converted_config):
                    raise ValueError("Configuration validation failed")

            all_inputs = {**non_stream_inputs, **stream_inputs}
            all_config = {**config, **converted_config} if converted_config else config
            result = await self._execute(
                config=all_config, 
                input_data=all_inputs, 
                execution_context=self.execution_context, 
                **kwargs
            )

            if isinstance(result, Generator | AsyncGenerator):
                return self._handle_generator_lifecycle(result, context)
            else:
                context.result = result
                await self.on_completed(context)
                return result
        except Exception as e:
            context.error = e
            await self.on_failed(context)
            raise e

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
