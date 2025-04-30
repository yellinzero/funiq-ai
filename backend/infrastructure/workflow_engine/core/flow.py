import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any, Callable, Coroutine

from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.workflow import WorkflowNode
from infrastructure import with_session
from utils.common.datetime import utcnow

from .lifecycle import LifecycleMixin
from .logger import WorkflowLogger
from .models import WorkflowDebugExecution, WorkflowExecution
from .schemas import (
    ExecutionStates,
    FlowExecutionCallbackContext,
    LifecycleContext,
    TaskExecutionCallbackContext,
    TopologyInfo,
    WorkflowContext,
)
from .task import WorkflowTask


class WorkflowFlow(LifecycleMixin[FlowExecutionCallbackContext]):
    """Class for workflow execution."""

    def __init__(
        self,
        workflow_context: WorkflowContext,
        topology_info: TopologyInfo,
        is_debug: bool = False,
        on_created: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_pending: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_running: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_completed: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_failed: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_cancelling: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_cancelled: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_paused: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_task_created: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_task_pending: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_task_running: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_task_completed: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_task_failed: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_task_cancelling: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_task_cancelled: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
        on_task_paused: Callable[[TaskExecutionCallbackContext], Coroutine] = [],
    ):
        self._workflow_context = workflow_context
        self._topology_info = topology_info
        self._tasks: list[WorkflowTask] = []
        self._tasks_outputs = {}
        self._logger = None
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
        self._on_task_created = on_task_created
        self._on_task_pending = on_task_pending
        self._on_task_running = on_task_running
        self._on_task_completed = on_task_completed
        self._on_task_failed = on_task_failed
        self._on_task_cancelling = on_task_cancelling
        self._on_task_cancelled = on_task_cancelled
        self._on_task_paused = on_task_paused
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
            FlowExecutionCallbackContext(
                flow=self,
            )
        )
        self._initialized = True
        
    @property
    def status(self) -> ExecutionStates:
        return self._lifecycle_context.status

    @property
    def workflow_context(self) -> WorkflowContext:
        return self._workflow_context

    @property
    def is_debug(self) -> bool:
        return self._is_debug

    @property
    def topology_info(self) -> TopologyInfo:
        return self._topology_info

    @property
    def node_levels(self) -> list[list[str]]:
        return self._topology_info.data.node_levels

    @property
    def adjacency(self) -> dict[str, dict[str, list[str]]]:
        return self._topology_info.data.adjacency

    @property
    def end_node_key(self) -> str:
        return self._workflow_context.end_node_key
    
    @property
    def start_node_key(self) -> str:
        return self._workflow_context.start_node_key

    @property
    def tasks_outputs(self) -> dict[str, Any]:
        return self._tasks_outputs

    @property
    def snapshot(self) -> dict[str, Any]:
        return self._workflow_context.snapshot

    @property
    def input_data(self) -> dict[str, Any]:
        return self._workflow_context.input_data

    @property
    def user_id(self) -> str:
        return self._workflow_context.execution_context.get("user_id")

    def _initialize_logger(self) -> None:
        """Initialize flow logger with execution ID."""
        if not self._execution_id:
            raise ValueError("Cannot initialize logger without execution ID")

        self._logger = WorkflowLogger(run_id=self._execution_id, created_by=self.user_id, is_debug=self.is_debug)

    def _get_upstream_outputs(self, node_key: str) -> dict[str, Any]:
        """Get outputs from upstream nodes using adjacency list."""
        upstream_outputs = {}

        # Get upstream nodes directly from adjacency list
        upstream_nodes = self.adjacency[node_key]["upstream"]
        for upstream_node in upstream_nodes:
            if upstream_node in self.tasks_outputs:
                upstream_outputs[upstream_node] = self.tasks_outputs[upstream_node]

        return upstream_outputs

    def create_callback_context(self, **kwargs) -> FlowExecutionCallbackContext:
        """Create flow execution callback context with optional parameters."""
        context = FlowExecutionCallbackContext(flow=self)
        
        if 'result' in kwargs:
            context.result = kwargs['result']
        if 'error' in kwargs:
            context.error = kwargs['error']
            
        return context

    async def execute(self):
        """Execute workflow with state management."""
        await self.on_pending(self.create_callback_context())
        self._logger.info("Flow pending")
        try:
            await self.on_running(self.create_callback_context())
            self._logger.info("Flow running")
            
            for level in self.node_levels:
                for node_key in level:
                    if self.is_cancelled():
                        return
                        
                    if self.is_paused():
                        await self.wait_for_resume()
                        
                    node = next(n for n in self.snapshot.get("nodes", []) if n.get("node_key") == node_key)
                    input_data = {
                        **self.input_data,
                        **self._get_upstream_outputs(node_key),
                    }

                    task = WorkflowTask(
                        node=WorkflowNode(**node),
                        workflow_context=self.workflow_context,
                        is_debug=self._is_debug,
                        run_id=self._execution_id,
                        on_created=self._on_task_created,
                        on_pending=self._on_task_pending,
                        on_running=self._on_task_running,
                        on_completed=self._on_task_completed,
                        on_failed=self._on_task_failed,
                        on_cancelling=self._on_task_cancelling,
                        on_cancelled=self._on_task_cancelled,
                        on_paused=self._on_task_paused,
                    )
                    self._tasks.append(task)
                    await task.initialize()
                    result = await task.execute(input_data)
                    self.tasks_outputs[node_key] = result

            end_result = self.tasks_outputs[self.end_node_key]
            
            if isinstance(end_result, (AsyncGenerator, Generator)):
                return self._handle_generator_lifecycle(
                    result=end_result,
                    is_cancelled=self.is_cancelled,
                    is_paused=self.is_paused,
                    wait_for_resume=self.wait_for_resume
                )
            else:
                await self.on_completed(self.create_callback_context(result=end_result))
                return end_result
                
        except Exception as e:
            await self.on_failed(self.create_callback_context(error=e))
            raise e

    async def on_created(self, context: FlowExecutionCallbackContext):
        await self._create_execution_record()
        self._initialize_logger()
        self._logger.info(f"Flow {self.workflow_context.workflow_name}({self._execution_id}) created")
        await self._trigger_callbacks(self._lifecycle_context.on_created_callbacks, context)

    async def on_pending(self, context: FlowExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.PENDING)
        self._logger.info(f"Flow {self.workflow_context.workflow_name}({self._execution_id}) pending")
        await self._trigger_callbacks(self._lifecycle_context.on_pending_callbacks, context)

    async def on_running(self, context: FlowExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.RUNNING)
        self._logger.info(f"Flow {self.workflow_context.workflow_name}({self._execution_id}) running")
        await self._trigger_callbacks(self._lifecycle_context.on_running_callbacks, context)

    async def on_completed(self, context: FlowExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.COMPLETED)
        self._logger.info(f"Flow {self.workflow_context.workflow_name}({self._execution_id}) completed")
        await self._trigger_callbacks(self._lifecycle_context.on_completed_callbacks, context)
        await self._logger.archive_logs()

    async def on_failed(self, context: FlowExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.FAILED)
        self._logger.error(f"Flow {self.workflow_context.workflow_name}({self._execution_id}) failed: {context.error}")
        await self._trigger_callbacks(self._lifecycle_context.on_failed_callbacks, context)
        await self._logger.archive_logs()

    async def on_cancelling(self, context: FlowExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.CANCELLING)
        self._logger.info(f"Flow {self.workflow_context.workflow_name}({self._execution_id}) cancelling")
        await self._trigger_callbacks(self._lifecycle_context.on_cancelling_callbacks, context)

    async def on_cancelled(self, context: FlowExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.CANCELLED)
        self._logger.info(f"Flow {self.workflow_context.workflow_name}({self._execution_id}) cancelled")
        await self._trigger_callbacks(self._lifecycle_context.on_cancelled_callbacks, context)
        await self._logger.archive_logs()

    async def on_paused(self, context: FlowExecutionCallbackContext):
        await self._update_execution_status(status=ExecutionStates.PAUSED)
        self._logger.info(f"Flow {self.workflow_context.workflow_name}({self._execution_id}) paused")
        await self._trigger_callbacks(self._lifecycle_context.on_paused_callbacks, context)

    @with_session
    async def _create_execution_record(self, session: AsyncSession) -> None:
        """Create workflow execution record."""
        try:
            execution = None
            if self.is_debug:
                execution = WorkflowDebugExecution(
                    workflow_id=self.workflow_context.workflow_id,
                    snapshot_timestamp=self.workflow_context.timestamp,
                    status=ExecutionStates.CREATED,
                    record_info={},
                    created_by=self.user_id,
                    created_at=utcnow().replace(tzinfo=None),
                )
            else:
                execution = WorkflowExecution(
                    workflow_id=self.workflow_context.workflow_id,
                    version=self.workflow_context.version,
                    status=ExecutionStates.CREATED,
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

        execution_model = WorkflowExecution if not self.is_debug else WorkflowDebugExecution
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

    async def cancel(self):
        """Cancel workflow execution."""
        if self.status in [ExecutionStates.RUNNING, ExecutionStates.PENDING]:
            self._cancelled = True
            await self.on_cancelling(self.create_callback_context())
            
            for task in self._tasks:
                await task.cancel()
                    
            await self.on_cancelled(self.create_callback_context())

    async def pause(self):
        """Pause workflow execution."""
        self._paused = True
        self._paused_event.clear()
        
        for task in self._tasks:
            await task.pause()
               
        await self.on_paused(self.create_callback_context())

    async def resume(self):
        """Resume workflow execution."""
        if self.status == ExecutionStates.PAUSED:
            self._paused = False
            self._paused_event.set()
            
            for task in self._tasks:
                if task.status == ExecutionStates.PAUSED:
                    await task.resume()
                    
            await self.on_running(self.create_callback_context())

    def is_cancelled(self) -> bool:
        """Get cancellation state."""
        return self._cancelled

    def is_paused(self) -> bool:
        """Get pause state."""
        return self._paused

    async def wait_for_resume(self):
        """Wait for resume signal."""
        await self._paused_event.wait()
