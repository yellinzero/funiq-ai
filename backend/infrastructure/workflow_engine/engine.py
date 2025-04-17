from datetime import datetime
from typing import Any, Dict

from .core import WorkflowEngineBase


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
    ):
        super().__init__(
            workflow_id=workflow_id,
            snapshot=snapshot,
            snapshot_hash=snapshot_hash,
            input_data=input_data,
            execution_context=execution_context,
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
    ):
        super().__init__(
            workflow_id=workflow_id,
            snapshot=snapshot,
            snapshot_hash=snapshot_hash,
            input_data=input_data,
            execution_context=execution_context,
        )
        self._context.snapshot_timestamp = snapshot_timestamp