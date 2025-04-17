from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator
from typing import Callable, Coroutine, Generic, TypeVar, Union

from .schemas import LifecycleContext

TContext = TypeVar('TContext')


class LifecycleMixin(ABC, Generic[TContext]):
    """
    Generic mixin class that provides lifecycle management functionality.
    Only handles lifecycle methods, not state.
    """
    _lifecycle_context: LifecycleContext[TContext]
    
    def add_on_created_callback(self, callback: Callable[[TContext], Coroutine]):
        """Add a callback to be executed when the entity is created."""
        self._lifecycle_context.on_created_callbacks.append(callback)
        
    def add_on_pending_callback(self, callback: Callable[[TContext], Coroutine]):
        """Add a callback to be executed when the entity is pending."""
        self._lifecycle_context.on_pending_callbacks.append(callback)

    def add_on_running_callback(self, callback: Callable[[TContext], Coroutine]):
        """Add a callback to be executed when the entity starts running."""
        self._lifecycle_context.on_running_callbacks.append(callback)

    def add_on_completed_callback(self, callback: Callable[[TContext], Coroutine]):
        """Add a callback to be executed when the entity completes successfully."""
        self._lifecycle_context.on_completed_callbacks.append(callback)

    def add_on_failed_callback(self, callback: Callable[[TContext], Coroutine]):
        """Add a callback to be executed when the entity fails."""
        self._lifecycle_context.on_failed_callbacks.append(callback)
        
    def add_on_cancelling_callback(self, callback: Callable[[TContext], Coroutine]):
        """Add a callback to be executed when the entity is cancelling."""
        self._lifecycle_context.on_cancelling_callbacks.append(callback)
        
    def add_on_cancelled_callback(self, callback: Callable[[TContext], Coroutine]):
        """Add a callback to be executed when the entity is cancelled."""
        self._lifecycle_context.on_cancelled_callbacks.append(callback)
        
    def add_on_paused_callback(self, callback: Callable[[TContext], Coroutine]):
        """Add a callback to be executed when the entity is paused."""
        self._lifecycle_context.on_paused_callbacks.append(callback)
        
    async def _trigger_callbacks(
        self, 
        callbacks: list[Callable[[TContext], Coroutine]], 
        context: TContext
    ):
        """Helper method to trigger callbacks with context."""
        for callback in callbacks:
            await callback(context)
                
    @abstractmethod
    def create_callback_context(self, **kwargs) -> TContext:
        """Create callback context with optional parameters."""
        pass

    async def _handle_generator_lifecycle(
        self, 
        result: Union[Generator, AsyncGenerator],
        is_cancelled: Callable[[], bool],
        is_paused: Callable[[], bool],
        wait_for_resume: Callable[[], Coroutine]
    ) -> AsyncGenerator:
        """
        Handle generator lifecycle with external state control.
        Creates and manages its own context internally.
        """
        chunks = []  # collect all chunks
        try:
            if isinstance(result, Generator):
                for chunk in result:
                    if is_cancelled():
                        await self.on_cancelled(self.create_callback_context())
                        return
                        
                    if is_paused():
                        await wait_for_resume()
                        
                    chunks.append(chunk)
                    yield chunk
                    
            elif isinstance(result, AsyncGenerator):
                async for chunk in result:
                    if is_cancelled():
                        await self.on_cancelled(self.create_callback_context())
                        return
                        
                    if is_paused():
                        await wait_for_resume()
                        
                    chunks.append(chunk)
                    yield chunk
                    
            # when completed, create a context containing all results
            await self.on_completed(self.create_callback_context(result=chunks))
            
        except Exception as e:
            await self.on_failed(self.create_callback_context(error=e))
            raise

    @abstractmethod
    async def on_created(self, context: TContext):
        """Callback method for when the entity is created."""
        pass

    @abstractmethod
    async def on_pending(self, context: TContext):
        """Callback method for when the entity is pending."""
        pass
    
    @abstractmethod
    async def on_running(self, context: TContext):
        """Callback method for when the entity starts running."""
        pass
    
    @abstractmethod
    async def on_completed(self, context: TContext):
        """Callback method for when the entity completes successfully."""
        pass
    
    @abstractmethod
    async def on_failed(self, context: TContext):
        """Callback method for when the entity fails."""
        pass
    
    @abstractmethod
    async def on_cancelling(self, context: TContext):
        """Callback method for when the entity is cancelling."""
        pass
    
    @abstractmethod
    async def on_cancelled(self, context: TContext):
        """Callback method for when the entity is cancelled."""
        pass
    
    @abstractmethod
    async def on_paused(self, context: TContext):
        """Callback method for when the entity is paused."""
        pass
    
    
    
    
    
    