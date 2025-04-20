from datetime import datetime
from typing import Any, Callable, Coroutine, Dict

from .core import (
    FlowExecutionCallbackContext,
    TaskExecutionCallbackContext,
    WorkflowEngineBase,
)


class WorkflowVersionEngine(WorkflowEngineBase):
    """Engine for published workflow versions."""

    def __init__(
        self,
        workflow_id: str,
        version: str,
        snapshot: Dict[str, Any],
        snapshot_hash: str,
        input_data: Dict[str, Any],
        execution_context: Dict[str, Any],
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
        super().__init__(
            workflow_id=workflow_id,
            snapshot=snapshot,
            snapshot_hash=snapshot_hash,
            input_data=input_data,
            execution_context=execution_context,
            on_created=on_created,
            on_pending=on_pending,
            on_running=on_running,
            on_completed=on_completed,
            on_failed=on_failed,
            on_cancelling=on_cancelling,
            on_cancelled=on_cancelled,
            on_paused=on_paused,
            on_task_created=on_task_created,
            on_task_pending=on_task_pending,
            on_task_running=on_task_running,
            on_task_completed=on_task_completed,
            on_task_failed=on_task_failed,
            on_task_cancelling=on_task_cancelling,
            on_task_cancelled=on_task_cancelled,
            on_task_paused=on_task_paused,
        )
        self._context.version = version


class WorkflowDebugEngine(WorkflowEngineBase):
    """Engine for workflow debugging."""

    def __init__(
        self,
        workflow_id: str,
        snapshot: Dict[str, Any],
        snapshot_timestamp: datetime,
        snapshot_hash: str,
        input_data: Dict[str, Any],
        execution_context: Dict[str, Any],
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
        super().__init__(
            workflow_id=workflow_id,
            snapshot=snapshot,
            snapshot_hash=snapshot_hash,
            input_data=input_data,
            execution_context=execution_context,
            on_created=on_created,
            on_pending=on_pending,
            on_running=on_running,
            on_completed=on_completed,
            on_failed=on_failed,
            on_cancelling=on_cancelling,
            on_cancelled=on_cancelled,
            on_paused=on_paused,
            on_task_created=on_task_created,
            on_task_pending=on_task_pending,
            on_task_running=on_task_running,
            on_task_completed=on_task_completed,
            on_task_failed=on_task_failed,
            on_task_cancelling=on_task_cancelling,
            on_task_cancelled=on_task_cancelled,
            on_task_paused=on_task_paused,
        )
        self._context.snapshot_timestamp = snapshot_timestamp
