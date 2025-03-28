from typing import Any, Dict

from fastapi import APIRouter, Request
from loguru import logger

from app.errors.base import FuniqAIError
from app.schemas import ResponseModel
from tasks.workflow_tasks import execute_workflow

from .schemas import GetOperatorsResponse
from .service.operator_service import OperatorService

workflows_router = APIRouter(prefix="/workflows", tags=["workflows"])


@workflows_router.get(
    "/operators", response_model=ResponseModel[GetOperatorsResponse], response_model_exclude_none=True
)
async def get_operators(request: Request):
    """
    Get all available operators
    """
    operators = OperatorService.get_all_operators()
    return ResponseModel(data={"operators": operators, "total": len(operators)})


# TODO Test
@workflows_router.post(
    "/{workflow_id}/trigger",
    response_model=ResponseModel[Dict[str, Any]],
    response_model_exclude_none=True
)
async def trigger_workflow(workflow_id: str, request: Request):
    """
    Test trigger workflow
    """
    try:        
        task = execute_workflow.delay(workflow_id, {})
        
        return ResponseModel(data={
            "task_id": task.id,
            "workflow_id": workflow_id,
            "status": "triggered"
        })
        
    except Exception as e:
        logger.error(f"Trigger workflow failed: {e!s}")
        raise FuniqAIError(code="500", msg=str(e)) from e
