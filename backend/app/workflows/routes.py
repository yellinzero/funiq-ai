import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi_async_sqlalchemy import db
from loguru import logger

from app.account.service.account_service import AccountService
from app.account.service.tenant_service import TenantService
from app.core.schemas import ResponseModel

from .schemas import (
    GetOperatorsResponse,
    WorkflowDebugRequest,
    WorkflowDebugResponse,
    WorkflowExecuteRequest,
    WorkflowExecuteResponse,
    WorkflowStreamRequest,
)
from .service.operator_service import OperatorService
from .service.workflow_service import WorkflowService

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


@workflows_router.post(
    "/{workflow_id}/execute",
    response_model=ResponseModel[WorkflowExecuteResponse],
    response_model_exclude_none=True
)
async def execute_workflow(
    request: Request,
    workflow_id: str,
    execute_request: WorkflowExecuteRequest,
):
    """Execute a workflow synchronously with specific version.
    
    Args:
        workflow_id: Workflow ID
        execute_request: Execution request containing input data and version
    """
    tenant_id = request.state.tenant_id
    account = await AccountService.get_account_info(db.session, request)
    user = await TenantService.get_user_by_account_id(db.session, tenant_id, account.id)
    result = WorkflowService.execute_workflow_sync(
        session=db.session,
        workflow_id=workflow_id,
        input_data=execute_request.input_data,
        execution_context={
            "user_id": str(user.id),
            "tenant_id": tenant_id,
        },
        version=execute_request.version
    )
    
    return ResponseModel(data=WorkflowExecuteResponse(result=result["result"]))


@workflows_router.post(
    "/{workflow_id}/debug",
    response_model=ResponseModel[WorkflowDebugResponse],
    response_model_exclude_none=True
)
async def debug_workflow(
    request: Request,
    workflow_id: str,
    debug_request: WorkflowDebugRequest,
):
    """Debug a workflow asynchronously using a specific snapshot.
    
    Args:
        workflow_id: Workflow ID
        debug_request: Debug request containing input data
    """
    tenant_id = request.state.tenant_id
    account = await AccountService.get_account_info(db.session, request)
    user = await TenantService.get_user_by_account_id(db.session, tenant_id, account.id)
    result = await WorkflowService.execute_workflow_async(
        session=db.session,
        workflow_id=workflow_id,
        input_data=debug_request.input_data,
        execution_context={
            "user_id": str(user.id),
            "tenant_id": tenant_id,
        },
        snapshot_timestamp=debug_request.snapshot_timestamp
    )
    
    return ResponseModel(data=WorkflowDebugResponse(task_id=result["task_id"]))


@workflows_router.post("/{workflow_id}/stream")
async def stream_workflow(
    request: Request,
    workflow_id: str,
    stream_request: WorkflowStreamRequest,
) -> StreamingResponse:
    """Stream workflow execution results.
    
    Args:
        workflow_id: Workflow ID
        stream_request: Stream request containing input data and either version or snapshot_timestamp
        
    Returns:
        StreamingResponse: Server-sent events stream
    """
    tenant_id = request.state.tenant_id
    account = await AccountService.get_account_info(db.session, request)
    user = await TenantService.get_user_by_account_id(db.session, tenant_id, account.id)
    
    stream = await WorkflowService.execute_workflow_stream(
        session=db.session,
        workflow_id=workflow_id,
        input_data=stream_request.input_data,
        execution_context={
            "user_id": str(user.id),
            "tenant_id": tenant_id,
        },
        version=stream_request.version,
        snapshot_timestamp=stream_request.snapshot_timestamp
    )
    
    async def generate():
        try:
            async for chunk in stream:
                yield f"data: {chunk.model_dump_json()}\n\n"
        except Exception as e:
            logger.error(f"Error in stream generation: {e!s}")
            error_message = {"error": str(e)}
            yield f"data: {json.dumps(error_message)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )