from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from asgiref.sync import async_to_sync
from celery import Task, shared_task
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.workflow import (
    WorkflowSnapshot,
    WorkflowVersion,
)
from app.workflows.core.executor import WorkflowDebugExecutor, WorkflowVersionExecutor
from infrastructure import with_session


@with_session
async def _get_workflow_version_snapshot(
    session: AsyncSession, 
    workflow_id: str, 
    version: str
) -> Tuple[Dict[str, Any], str]:
    """Get workflow version snapshot data."""
    workflow_result = await session.execute(
        select(WorkflowVersion).where(
            WorkflowVersion.workflow_id == workflow_id,
            WorkflowVersion.version == version,
        )
    )

    workflow_version = workflow_result.scalar_one_or_none()
    if not workflow_version:
        raise ValueError(f"Workflow version {version} not found")

    return workflow_version.snapshot, workflow_version.snapshot_hash


@with_session
async def _get_workflow_debug_snapshot(
    session: AsyncSession, 
    workflow_id: str, 
    snapshot_timestamp: datetime
) -> Tuple[Dict[str, Any], str]:
    """Get workflow debug snapshot data."""
    workflow_result = await session.execute(
        select(WorkflowSnapshot).where(
            WorkflowSnapshot.workflow_id == workflow_id,
            WorkflowSnapshot.snapshot_timestamp == snapshot_timestamp,
        )
    )

    workflow_snapshot = workflow_result.scalar_one_or_none()
    if not workflow_snapshot:
        raise ValueError(f"Workflow snapshot {snapshot_timestamp} not found")

    return workflow_snapshot.snapshot, workflow_snapshot.snapshot_hash


class WorkflowBaseTask(Task):
    """Base task class for workflow execution."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Task {task_id} failed: {exc!s}")


@shared_task(bind=True, base=WorkflowBaseTask, queue="workflow")
def execute_workflow(
    self,
    workflow_id: str,
    input_data: Dict[str, Any],
    execution_context: Dict[str, Any],
    version: Optional[str] = None,
    snapshot_timestamp: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Execute a workflow using Prefect.
    
    Args:
        workflow_id: Workflow ID
        input_data: Input data for workflow
        execution_context: Execution context (user_id, etc.)
        version: Workflow version (for version execution)
        snapshot_timestamp: Snapshot timestamp (for debug execution)
    """
    if not bool(version) ^ bool(snapshot_timestamp):
        raise ValueError("Either version or snapshot_timestamp must be provided, but not both")
        
    return async_to_sync(_execute_workflow_async)(
        workflow_id=workflow_id,
        input_data=input_data,
        execution_context=execution_context,
        version=version,
        snapshot_timestamp=snapshot_timestamp,
    )


async def _execute_workflow_async(
    workflow_id: str,
    input_data: Dict[str, Any],
    execution_context: Dict[str, Any],
    version: Optional[str] = None,
    snapshot_timestamp: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Execute a workflow asynchronously."""
    try:
        # Get snapshot data based on execution type
        if version:
            snapshot_data, snapshot_hash = await _get_workflow_version_snapshot(
                workflow_id=workflow_id,
                version=version,
            )
            is_stream = snapshot_data.get("stream_mode", False)
            if is_stream:
                raise RuntimeError("Task run not supported for stream execution")
            logger.info(f"Starting version workflow execution: {workflow_id} (version: {version})")
            executor = WorkflowVersionExecutor(
                workflow_id=workflow_id,
                version=version,
                snapshot=snapshot_data,
                snapshot_hash=snapshot_hash,
                input_data=input_data,
                execution_context=execution_context,
            )
        else:

            snapshot_data, snapshot_hash = await _get_workflow_debug_snapshot(
                workflow_id=workflow_id,
                snapshot_timestamp=snapshot_timestamp,
            )
            is_stream = snapshot_data.get("stream_mode", False)
            if is_stream:
                raise RuntimeError("Task run not supported for stream execution")
            logger.info(f"Starting debug workflow execution: {workflow_id} (timestamp: {snapshot_timestamp})")
            executor = WorkflowDebugExecutor(
                workflow_id=workflow_id,
                snapshot=snapshot_data,
                snapshot_hash=snapshot_hash,
                input_data=input_data,
                execution_context=execution_context,
                snapshot_timestamp=snapshot_timestamp,
            )
        
        # Initialize and execute
        await executor.initialize()
        result = await executor.execute()
        
        logger.info("Workflow execution completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e!s}", exc_info=True)
        raise