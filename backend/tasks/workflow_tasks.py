# from typing import Any, Dict

# from asgiref.sync import async_to_sync
# from celery import Task, shared_task
# from loguru import logger
# from sqlalchemy.ext.asyncio import AsyncSession

# from database import with_session
# from infrastructure.workflow_service import WorkflowService


# class WorkflowBaseTask(Task):
#     """Base task class for workflow execution."""
    
#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         """Handle task failure."""
#         logger.error(f"Task {task_id} failed: {exc!s}")


# @shared_task(bind=True, base=WorkflowBaseTask, queue="workflow", pydantic=True)
# def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
#     """Execute a workflow using Prefect v3."""
#     return async_to_sync(_execute_workflow_async)(
#         workflow_id=workflow_id,
#         inputs=inputs,
#     )


# @with_session
# async def _execute_workflow_async(
#     session: AsyncSession,
#     workflow_id: str,
#     inputs: Dict[str, Any]
# ) -> Dict[str, Any]:
#     """Execute a workflow asynchronously."""
#     logger.info(f"Starting workflow execution: {workflow_id} with inputs: {inputs}")
    
#     # Create workflow service and execute
#     service = WorkflowService(workflow_id)
#     await service.initialize(session)
#     result = service.execute(initial_inputs=inputs)
#     logger.info(f"Workflow execution completed with result: {result}")
    
#     return result 