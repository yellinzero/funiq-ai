import asyncio
from collections.abc import AsyncGenerator, Awaitable, Generator
from typing import Any, AsyncIterator, Callable, TypeVar, Union

from loguru import logger
from pydantic import BaseModel

from infrastructure.workflow_engine import WorkflowEngineBase
from utils.common.json import json_dumps

from .schema import StreamEvent

T = TypeVar('T', bound=BaseModel)
SyncCallback = Callable[[T], None]
AsyncCallback = Callable[[T], Awaitable[None]]
ErrorCallback = Union[Callable[[Exception], None], Callable[[Exception], Awaitable[None]]]
NoArgCallback = Union[Callable[[], None], Callable[[], Awaitable[None]]]


class StreamHandler:
    """Base stream handler for processing stream data with events."""
    
    def __init__(
        self,
        chunk_type: type[T],
        on_chunk: Union[SyncCallback[T], AsyncCallback[T]] | None = None,
        on_finish: NoArgCallback | None = None,
        on_error: ErrorCallback | None = None,
        on_close: NoArgCallback | None = None,
    ):
        self.chunk_type = chunk_type
        self.on_chunk = on_chunk
        self.on_finish = on_finish
        self.on_error = on_error
        self.on_close = on_close
        self._chunks: list[T] = []

    @property
    def chunks(self) -> list[T]:
        """Get all collected chunks."""
        return self._chunks

    async def process_stream(
        self,
        stream: Union[Generator[Any, None, None], AsyncGenerator[Any, None]],
        executor: WorkflowEngineBase | None = None,
    ) -> AsyncIterator[str]:
        """Process stream data and yield SSE formatted events."""
        try:
            if isinstance(stream, Generator):
                for chunk in stream:
                    for event in await self._handle_chunk(chunk):
                        yield event
            elif isinstance(stream, AsyncGenerator):
                async for chunk in stream:
                    for event in await self._handle_chunk(chunk):
                        yield event
        except Exception as e:
            logger.error(f"Error in stream generation: {e!s}")
            if self.on_error:
                await self._call_callback(self.on_error, e)
            yield self._format_event(StreamEvent.ERROR, {"error": str(e)})
        finally:
            try:
                if executor:
                    await executor.cancel()
                if self.on_close:
                    await self._call_callback(self.on_close)
                yield self._format_event(StreamEvent.CLOSE, {})
                logger.info(f"Total chunks collected: {len(self._chunks)}")
            except Exception as e:
                logger.error(f"Error while closing stream: {e}")

    async def _call_callback(self, callback: Any, *args: Any) -> None:
        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)

    async def _handle_chunk(self, chunk: Any) -> list[str]:
        """Handle a single chunk and return formatted events."""
        try:
            if not isinstance(chunk, self.chunk_type):
                chunk = self.chunk_type(**chunk)
            
            self._chunks.append(chunk)
            await self._call_callback(self.on_chunk, chunk)
            
            events = [self._format_event(StreamEvent.MESSAGE, chunk.model_dump())]
            
            if hasattr(chunk, 'finish_reason') and chunk.finish_reason:
                await self._call_callback(self.on_finish)
                events.append(self._format_event(StreamEvent.FINISH, {}))
            
            return events
        except Exception as e:
            logger.error(f"Error handling chunk: {e}")
            await self._call_callback(self.on_error, e)
            return [self._format_event(StreamEvent.ERROR, {"error": str(e)})]

    @staticmethod
    def _format_event(event: StreamEvent, data: Any) -> str:
        """Format an event and data as SSE."""
        return f"event: {event}\ndata: {json_dumps(data)}\n\n"