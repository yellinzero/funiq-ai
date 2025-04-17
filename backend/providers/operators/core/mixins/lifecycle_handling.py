from collections.abc import AsyncGenerator, Generator
from typing import Callable, Coroutine, Union

from loguru import logger

from ..schemas import OperatorCallbackContext, OperatorName, OperatorState


class LifecycleHandlingMixin:
    """Mixin class that provides lifecycle management functionality for operators."""
    
    _on_created_callbacks: list[Callable[[OperatorCallbackContext], Coroutine]]
    _on_running_callbacks: list[Callable[[OperatorCallbackContext], Coroutine]]
    _on_completed_callbacks: list[Callable[[OperatorCallbackContext], Coroutine]]
    _on_failed_callbacks: list[Callable[[OperatorCallbackContext], Coroutine]]
    _state: OperatorState
    operator_name: OperatorName
    
    def add_on_created_callback(self, callback: Callable[[OperatorCallbackContext], Coroutine]):
        """Add a callback to be executed when the operator is created."""
        self._on_created_callbacks.append(callback)

    def add_on_running_callback(self, callback: Callable[[OperatorCallbackContext], Coroutine]):
        """Add a callback to be executed when the operator starts running."""
        self._on_running_callbacks.append(callback)

    def add_on_completed_callback(self, callback: Callable[[OperatorCallbackContext], Coroutine]):
        """Add a callback to be executed when the operator completes successfully."""
        self._on_completed_callbacks.append(callback)

    def add_on_failed_callback(self, callback: Callable[[OperatorCallbackContext], Coroutine]):
        """Add a callback to be executed when the operator fails."""
        self._on_failed_callbacks.append(callback)
        
    async def _trigger_callbacks(
        self, 
        callbacks: list[Callable[[OperatorCallbackContext], Coroutine]], 
        context: OperatorCallbackContext
    ):
        """Helper method to trigger callbacks with context."""
        for callback in callbacks:
            try:
                await callback(context=context)
            except Exception as e:
                logger.error(f"Error in callback execution: {e}")
                
    async def _handle_generator_lifecycle(
        self, 
        result: Union[Generator, AsyncGenerator],
        context: OperatorCallbackContext
    ):
        """Handle both sync and async generator results with lifecycle management."""
        context.result = []
        try: 
            if isinstance(result, Generator):
                for chunk in result:
                    context.result.append(chunk)
                    yield chunk
                await self.on_completed(context)
                    
            elif isinstance(result, AsyncGenerator):
                async for chunk in result:
                    context.result.append(chunk)
                    yield chunk
                await self.on_completed(context)            
            
        except Exception as e:
            context.error = e
            await self.on_failed(context)
            raise
                
    async def on_created(self, context: OperatorCallbackContext):
        """Callback method for when the operator is created."""
        node_key = context.execution_context.get("node_key")
        logger.info(f"Operator {self.operator_name}{f'-{node_key}' if node_key else ''} created")
        self._state = OperatorState.CREATED
        await self._trigger_callbacks(self._on_created_callbacks, context)
    
    async def on_running(self, context: OperatorCallbackContext):
        """Callback method for when the operator starts running."""
        node_key = context.execution_context.get("node_key")
        logger.info(f"Operator {self.operator_name}{f'-{node_key}' if node_key else ''} running")
        self._state = OperatorState.RUNNING
        await self._trigger_callbacks(self._on_running_callbacks, context)
    
    async def on_completed(self, context: OperatorCallbackContext):
        """Callback method for when the operator completes successfully."""
        node_key = context.execution_context.get("node_key")
        logger.info(f"Operator {self.operator_name}{f'-{node_key}' if node_key else ''} completed")
        self._state = OperatorState.COMPLETED
        await self._trigger_callbacks(self._on_completed_callbacks, context)
    
    async def on_failed(self, context: OperatorCallbackContext):
        """Callback method for when the operator fails."""
        node_key = context.execution_context.get("node_key")
        logger.error(f"Operator {self.operator_name}{f'-{node_key}' if node_key else ''} failed: {context.error}")
        self._state = OperatorState.FAILED
        await self._trigger_callbacks(self._on_failed_callbacks, context)