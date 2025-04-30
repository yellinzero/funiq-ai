from typing import Any, Callable, Coroutine

from loguru import logger

from .flow import WorkflowFlow
from .schemas import (
    ExecutionStates,
    FlowExecutionCallbackContext,
    TaskExecutionCallbackContext,
    TopologyCacheContext,
    TopologyData,
    TopologyInfo,
    WorkflowContext,
)
from .topology import WorkflowTopologyMixin


class WorkflowEngine(WorkflowTopologyMixin):
    """Base class for workflow execution."""

    def __init__(
        self,
        workflow_id: str,
        snapshot: dict[str, Any],
        snapshot_hash: str,
       
        start_node_key: str,
        end_node_key: str,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] = {},
        topology_cached_expiration: int = 24 * 60 * 60,
        is_debug: bool = False,
        version: str | None = None,
        timestamp: str | None = None,
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
        if not snapshot:
            raise ValueError("Snapshot is required")
        
        self._context = WorkflowContext(
            workflow_id=workflow_id,
            workflow_name=snapshot.get("name"),
            snapshot=snapshot,
            snapshot_hash=snapshot_hash,
            input_data=input_data,
            execution_context=execution_context,
            is_debug=is_debug,
            start_node_key=start_node_key,
            end_node_key=end_node_key,
            version=version,
            timestamp=timestamp,
        )
        
        self._topology_info = TopologyInfo(
            data=TopologyData(
                adjacency={},
                node_levels=[],
            ),
            cache_context=TopologyCacheContext(
                cached_expiration=topology_cached_expiration,
                cached_key=self._generate_cached_key(workflow_id, snapshot_hash),
            ),
        )
        
        self._on_flow_created = on_created
        self._on_flow_pending = on_pending
        self._on_flow_running = on_running
        self._on_flow_completed = on_completed
        self._on_flow_failed = on_failed
        self._on_flow_cancelling = on_cancelling
        self._on_flow_cancelled = on_cancelled
        self._on_flow_paused = on_paused
        self._on_task_created = on_task_created
        self._on_task_pending = on_task_pending
        self._on_task_running = on_task_running
        self._on_task_completed = on_task_completed
        self._on_task_failed = on_task_failed
        self._on_task_cancelling = on_task_cancelling
        self._on_task_cancelled = on_task_cancelled
        self._on_task_paused = on_task_paused
        
        self._flow = None
        self._initialized = False
        
    @property
    def status(self) -> ExecutionStates:
        return self._flow.status

    @property
    def is_debug(self) -> bool:
        return bool(self._context.snapshot_timestamp)
    
    async def initialize(self):
        """Initialize the executor by building the topology."""
        if not self._initialized:
            logger.info(f"Initializing workflow {self._context.workflow_name}")
            self._topology_info.data = await self._build_topology(
                cache_context=self._topology_info.cache_context,
                snapshot=self._context.snapshot,
            )
            self._initialized = True

    async def execute(self):
        """Execute the workflow."""
        logger.info(f"Executing workflow {self._context.workflow_name}")
        self._flow = WorkflowFlow(
            workflow_context=self._context,
            topology_info=self._topology_info,
            is_debug=self.is_debug,
            on_created=self._on_flow_created,
            on_pending=self._on_flow_pending,
            on_running=self._on_flow_running,
            on_completed=self._on_flow_completed,
            on_failed=self._on_flow_failed,
            on_cancelling=self._on_flow_cancelling,
            on_cancelled=self._on_flow_cancelled,
            on_paused=self._on_flow_paused,
            on_task_created=self._on_task_created,
            on_task_pending=self._on_task_pending,
            on_task_running=self._on_task_running,
            on_task_completed=self._on_task_completed,
            on_task_failed=self._on_task_failed,
            on_task_cancelling=self._on_task_cancelling,
            on_task_cancelled=self._on_task_cancelled,
            on_task_paused=self._on_task_paused,
            
        )

        await self._flow.initialize()
        return await self._flow.execute()

    async def cancel(self):
        """Cancel the workflow execution."""
        if self._flow:
            await self._flow.cancel()
            
    async def pause(self):
        """Pause the workflow execution."""
        if self._flow:
            await self._flow.pause()
            
    async def resume(self):
        """Resume the workflow execution."""
        if self._flow:
            await self._flow.resume()
