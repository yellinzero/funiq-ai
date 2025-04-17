import asyncio
import uuid
from collections.abc import AsyncGenerator, Generator
from typing import Any, Callable, Coroutine

from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.workflow import (
    WorkflowNode,
)
from infrastructure import with_session
from providers.operators.core import OperatorFactory
from providers.operators.core.schemas import OperatorCallbackContext
from utils.common.datetime import utcnow

from .lifecycle import LifecycleMixin
from .logger import WorkflowLogger
from .models import WorkflowNodeDebugExecution, WorkflowNodeExecution
from .schemas import ExecutionStates, LifecycleContext, TaskExecutionCallbackContext, WorkflowContext


class WorkflowTask(LifecycleMixin[TaskExecutionCallbackContext]):
    """Class for workflow tasks."""

    def __init__(
        self,
        node: WorkflowNode,
        workflow_context: WorkflowContext,
        run_id: uuid.UUID,
        is_debug: bool = False,
        on_created: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_pending: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_running: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_completed: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_failed: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_cancelling: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_cancelled: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_paused: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
    ):
        self._node = node
        self._workflow_context = workflow_context
        self._is_stream = node.extended_config.get("stream_mode", False) if node.extended_config else False
        self._run_id = run_id
        self._execution_id = None
        self._is_debug = is_debug
        self._lifecycle_context = LifecycleContext(
            on_created_callbacks=on_created,
            on_pending_callbacks=on_pending,
            on_running_callbacks=on_running,
            on_completed_callbacks=on_completed,
            on_failed_callbacks=on_failed,
            on_cancelling_callbacks=on_cancelling,
            on_cancelled_callbacks=on_cancelled,
            on_paused_callbacks=on_paused,
        )
        self._logger = None
        self._initialized = False
        self._cancelled = False
        self._paused = False
        self._paused_event = asyncio.Event()
        self._paused_event.set()

    async def initialize(self):
        """Async initialization method that must be called before execution."""
        if self._initialized:
            return

        await self.on_created(
            TaskExecutionCallbackContext(
                task=self,
            )
        )
        self._initialized = True

    @property
    def status(self) -> ExecutionStates:
        return self._lifecycle_context.status

    @property
    def is_debug(self) -> bool:
        return self._is_debug

    @property
    def user_id(self) -> str:
        return self._workflow_context.execution_context.get("user_id")

    @property
    def workflow_context(self) -> WorkflowContext:
        return self._workflow_context

    def _initialize_logger(self) -> None:
        """Initialize task logger with execution ID."""
        if not self._execution_id:
            raise ValueError("Cannot initialize logger without execution ID")
        self._logger = WorkflowLogger(
            run_id=self._run_id, 
            node_run_id=self._execution_id, 
            created_by=self.user_id, 
            is_debug=self.is_debug
        )

    def _create_base_execution_context(
        self,
    ) -> dict[str, Any]:
        """Create common execution context."""
        return {
            "run_id": str(self._run_id),
            "node_run_id": str(self._execution_id),
            "node_type": self._node.node_type,
            "node_key": self._node.node_key,
            "stream_mode": self._is_stream,
            **self._workflow_context.execution_context,
        }

    def create_callback_context(self, **kwargs) -> TaskExecutionCallbackContext:
        """Create task execution callback context with optional parameters."""
        context = TaskExecutionCallbackContext(task=self)
        
        if 'result' in kwargs:
            context.result = kwargs['result']
        if 'error' in kwargs:
            context.error = kwargs['error']
        if 'operator_context' in kwargs:
            context.operator_context = kwargs['operator_context']
            
        return context

    async def execute(self, input_data: Any):
        """Execute task with state management."""
        if self.is_cancelled():
            await self.on_cancelled(self.create_callback_context())
            return

        await self.on_pending(self.create_callback_context())
        try:
            operator = OperatorFactory.get_operator_instance(self._node.node_type)
            execution_context = self._create_base_execution_context()
            operator.add_on_running_callback(self.on_operator_running)
            result = await operator.execute(
                input_data=input_data,
                config=self._node.config,
                execution_context=execution_context
            )
            
            if isinstance(result, (AsyncGenerator, Generator)):
                return self._handle_generator_lifecycle(
                    result=result,
                    is_cancelled=self.is_cancelled,
                    is_paused=self.is_paused,
                    wait_for_resume=self.wait_for_resume
                )
            else:
                if self.is_cancelled():
                    await self.on_cancelled(self.create_callback_context())
                    return
                    
                await self.on_completed(self.create_callback_context(result=result))
                return result
                
        except Exception as e:
            await self.on_failed(self.create_callback_context(
                error=e,
                operator_context={'node_type': self._node.node_type}
            ))
            raise e

    async def on_operator_running(self, context: OperatorCallbackContext):
        """Handle operator running callback."""
        await self.on_running(self.create_callback_context(
            operator_context=context
        ))

    async def on_created(self, context: TaskExecutionCallbackContext):
        await self._create_execution_record()
        self._initialize_logger()
        self._logger.info(f"Task {self._node.name}({self._node.node_key}) created")
        await self._trigger_callbacks(self._lifecycle_context.on_created_callbacks, context)

    async def on_pending(self, context: TaskExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.PENDING)
        self._logger.info(f"Task {self._node.name}({self._node.node_key}) pending")
        await self._trigger_callbacks(self._lifecycle_context.on_pending_callbacks, context)

    async def on_running(self, context: TaskExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.RUNNING)
        self._logger.info(f"Task {self._node.name}({self._node.node_key}) running")
        await self._trigger_callbacks(self._lifecycle_context.on_running_callbacks, context)

    async def on_completed(self, context: TaskExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.COMPLETED)
        self._logger.info(f"Task {self._node.name}({self._node.node_key}) completed")
        await self._trigger_callbacks(self._lifecycle_context.on_completed_callbacks, context)

    async def on_failed(self, context: TaskExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.FAILED)
        self._logger.error(f"Task {self._node.name}({self._node.node_key}) failed: {context.error}")
        await self._trigger_callbacks(self._lifecycle_context.on_failed_callbacks, context)

    async def on_cancelling(self, context: TaskExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.CANCELLING)
        self._logger.info(f"Task {self._node.name}({self._node.node_key}) cancelling")
        await self._trigger_callbacks(self._lifecycle_context.on_cancelling_callbacks, context)
        
    async def on_cancelled(self, context: TaskExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.CANCELLED)
        self._logger.info(f"Task {self._node.name}({self._node.node_key}) cancelled")
        await self._trigger_callbacks(self._lifecycle_context.on_cancelled_callbacks, context)

    async def on_paused(self, context: TaskExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.PAUSED)
        self._logger.info(f"Task {self._node.name}({self._node.node_key}) paused")
        await self._trigger_callbacks(self._lifecycle_context.on_paused_callbacks, context)

    @with_session
    async def _create_execution_record(self, session: AsyncSession) -> None:
        """Create workflow execution record."""
        try:
            execution_model = WorkflowNodeExecution if not self.is_debug else WorkflowNodeDebugExecution
            execution = None
            if self.is_debug:
                execution = execution_model(
                    run_id=self._run_id,
                    status=ExecutionStates.CREATED,
                    node_key=self._node.node_key,
                    record_info={},
                    created_by=self.user_id,
                    created_at=utcnow().replace(tzinfo=None),
                )
            else:
                execution = execution_model(
                    run_id=self._run_id,
                    status=ExecutionStates.CREATED,
                    node_key=self._node.node_key,
                    record_info={},
                    created_by=self.user_id,
                    created_at=utcnow().replace(tzinfo=None),
                )
            if not execution:
                raise RuntimeError("Failed to create execution record")
            session.add(execution)
            await session.flush()
            await session.commit()
            self._execution_id = execution.id
            self._lifecycle_context.status = ExecutionStates.CREATED
        except Exception as e:
            logger.error(f"Failed to create execution record: {e}")
            raise e

    @with_session
    async def _update_execution_status(
        self, session: AsyncSession, status: ExecutionStates, record_info: dict[str, Any] = {}
    ) -> None:
        """Update execution status in database."""
        if not self._execution_id:
            raise ValueError("Execution record not created")

        execution_model = WorkflowNodeExecution if not self.is_debug else WorkflowNodeDebugExecution
        now = utcnow().replace(tzinfo=None)
        update_values = {"status": status, "record_info": record_info}

        if status == ExecutionStates.RUNNING:
            update_values["start_time"] = now
        elif status in (ExecutionStates.COMPLETED, ExecutionStates.FAILED, ExecutionStates.CANCELLED):
            update_values["end_time"] = now

        stmt = update(execution_model).where(execution_model.id == self._execution_id).values(**update_values)
        await session.execute(stmt)
        await session.flush()
        await session.commit()
        self._lifecycle_context.status = status

    def is_cancelled(self) -> bool:
        """Get cancellation state."""
        return self._cancelled

    def is_paused(self) -> bool:
        """Get pause state."""
        return self._paused

    async def wait_for_resume(self):
        """Wait for resume signal."""
        await self._paused_event.wait()

    async def cancel(self):
        """Cancel task execution."""
        self._cancelled = True
        await self.on_cancelling(self.create_callback_context())
        await self.on_cancelled(self.create_callback_context())

    async def pause(self):
        """Pause task execution."""
        self._paused = True
        self._paused_event.clear()
        await self.on_paused(self.create_callback_context())

    async def resume(self):
        """Resume task execution."""
        if self.status == ExecutionStates.PAUSED:
            self._paused = False
            self._paused_event.set()
            await self.on_running(self.create_callback_context())
