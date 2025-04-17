from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Generic, TypeVar

from pydantic import BaseModel


class ExecutionStates(str, Enum):
    """States of a workflow execution."""
    CREATED = "CREATED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"
    CANCELLING = "CANCELLING"
  
    
class WorkflowContext(BaseModel):
    """Context of the workflow."""
    workflow_id: str
    workflow_name: str
    snapshot: dict[str, Any]
    snapshot_hash: str
    input_data: dict[str, Any]
    execution_context: dict[str, Any]
    is_stream: bool
    snapshot_timestamp: str | None = None
    version: str | None = None
    
    
class TopologyData(BaseModel):
    """Topology of the workflow."""
    adjacency: dict[str, Any]
    node_levels: list[list[str]]
    end_node_key: str


class TopologyCacheContext(BaseModel):
    """Context of the workflow topology cache."""
    cached_expiration: int
    cached_key: str
    

class TopologyInfo(BaseModel):
    """Info of the workflow topology."""
    data: TopologyData
    cache_context: TopologyCacheContext
    

class WorkflowLog(BaseModel):
    """Log of the workflow."""
    timestamp: str
    level: str
    message: str
    context: dict[str, Any]


if TYPE_CHECKING:
    from .flow import WorkflowFlow
    from .task import WorkflowTask


class FlowExecutionCallbackContext:
    """Callback context containing flow execution information."""
    def __init__(
        self,
        flow: 'WorkflowFlow',
        result: Any = None,
        error: Exception | None = None
    ):
        self.flow = flow
        self.result = result
        self.error = error

    @property
    def status(self) -> ExecutionStates:
        return self.flow.status
    

class TaskExecutionCallbackContext:
    """Callback context containing task execution information."""
    def __init__(
        self,
        task: 'WorkflowTask',
        result: Any = None,
        error: Exception | None = None,
        operator_context: Any | None = None
    ):
        self.task = task
        self.result = result
        self.error = error
        self.operator_context = operator_context

    @property
    def status(self) -> ExecutionStates:
        return self.task.status
    

TContext = TypeVar('TContext')


class LifecycleContext(BaseModel, Generic[TContext]):
    """Context of the lifecycle."""
    status: ExecutionStates = ExecutionStates.CREATED
    on_created_callbacks: list[Callable[[TContext], Coroutine[Any, Any, None]]] = []
    on_pending_callbacks: list[Callable[[TContext], Coroutine[Any, Any, None]]] = []
    on_running_callbacks: list[Callable[[TContext], Coroutine[Any, Any, None]]] = []
    on_completed_callbacks: list[Callable[[TContext], Coroutine[Any, Any, None]]] = []
    on_failed_callbacks: list[Callable[[TContext], Coroutine[Any, Any, None]]] = []
    on_cancelling_callbacks: list[Callable[[TContext], Coroutine[Any, Any, None]]] = []
    on_cancelled_callbacks: list[Callable[[TContext], Coroutine[Any, Any, None]]] = []
    on_paused_callbacks: list[Callable[[TContext], Coroutine[Any, Any, None]]] = []
    
    
    
    
    
