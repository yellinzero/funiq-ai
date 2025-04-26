
from fastapi import APIRouter, Request
from fastapi_async_sqlalchemy import db

from app.account.service.tenant_service import TenantService
from app.core.schemas import ResponseModel

from .schemas import (
    GetOperatorsResponse,
    PublishWorkflowRequest,
    PublishWorkflowResponse,
    SaveWorkflowRequest,
    SaveWorkflowResponse,
    UpdateWorkflowMetaRequest,
    WorkflowDebugRequest,
    WorkflowDebugResponse,
    WorkflowExecuteRequest,
    WorkflowExecuteResponse,
    WorkflowListResponse,
    WorkflowResponse,
)
from .service.operator_service import OperatorService
from .service.workflow_service import WorkflowService

workflow_router = APIRouter(prefix="/workflows", tags=["Workflows"])


@workflow_router.get(
    "/operators", response_model=ResponseModel[GetOperatorsResponse], response_model_exclude_none=True
)
async def get_operators(request: Request):
    """
    Get all available operators
    """
    operators = OperatorService.get_all_operators()
    return ResponseModel(data={"operators": operators, "total": len(operators)})


@workflow_router.get(
    "",
    response_model=ResponseModel[WorkflowListResponse],
)
async def get_workflow_list(
    request: Request,
    app_id: str,
    page: int | None = None,
    page_size: int | None = None,
    search: str | None = None,
):
    """
    Get paginated list of workflows with optional search.
    
    Args:
        app_id: Application ID to filter workflows
        page: Page number (1-based)
        page_size: Number of items per page
        search: Optional search term to filter workflows by name or description
    """
    
    actual_page = page if page is not None else 1
    actual_page_size = page_size if page_size is not None else 20
    
    workflow_list = await WorkflowService.get_workflow_list(
        session=db.session,
        app_id=app_id,
        page=actual_page,
        page_size=actual_page_size,
        search_term=search,
    )
    return ResponseModel(
        data=workflow_list,
    )


@workflow_router.post(
    "/{workflow_id}/execute",
    response_model=ResponseModel[WorkflowExecuteResponse],
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
    account_id = request.state.account_id   
    user = await TenantService.get_user_by_account_id(db.session, tenant_id, account_id)
    result = WorkflowService.execute_workflow_sync(
        session=db.session,
        workflow_id=workflow_id,
        input_data=execute_request.input_data,
        execution_context={
            "user_id": str(user.id),
            "user_name": user.name,
            "tenant_id": str(tenant_id),
        },
        version=execute_request.version
    )
    
    return ResponseModel(data=result)


@workflow_router.post(
    "/{workflow_id}/debug",
    response_model=ResponseModel[WorkflowDebugResponse],
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
    account_id = request.state.account_id
    user = await TenantService.get_user_by_account_id(db.session, tenant_id, account_id)
    result = await WorkflowService.execute_workflow_async(
        session=db.session,
        workflow_id=workflow_id,
        input_data=debug_request.input_data,
        execution_context={
            "user_id": str(user.id),
            "user_name": user.name,
            "tenant_id": str(tenant_id),
        },
        snapshot_timestamp=debug_request.snapshot_timestamp
    )
    
    return ResponseModel(data=WorkflowDebugResponse(task_id=result["task_id"]))


@workflow_router.post(
    "/{workflow_id}/save-graph",
    response_model=ResponseModel[SaveWorkflowResponse],
)
async def save_workflow(
    request: Request,
    workflow_id: str,
    save_request: SaveWorkflowRequest,
):
    """Save workflow graph data with batch operations."""
    
    # Process batch operations and create snapshot
    result = await WorkflowService.save_workflow(
        session=db.session,
        workflow_id=workflow_id,
        operations=save_request.operations,
        request=request,
    )
    
    return ResponseModel(data=result)


@workflow_router.put(
    "/{workflow_id}/save-meta",
    response_model=ResponseModel[WorkflowResponse],
)
async def update_workflow_meta(
    request: Request,
    workflow_id: str,
    meta_request: UpdateWorkflowMetaRequest,
):
    """Update workflow metadata (name, description)."""    
    workflow = await WorkflowService.update_workflow_meta(
        session=db.session,
        workflow_id=workflow_id,
        name=meta_request.name,
        description=meta_request.description,
        request=request,
    )
    
    return ResponseModel(data=workflow)


@workflow_router.get(
    "/{workflow_id}",
    response_model=ResponseModel[WorkflowResponse],
)
async def get_workflow(
    request: Request,
    workflow_id: str,
):
    """
    Get complete workflow information including nodes and edges.
    
    Args:
        workflow_id: ID of the workflow to retrieve
    """
    workflow = await WorkflowService.get_workflow(
        session=db.session,
        workflow_id=workflow_id,
    )
    
    return ResponseModel(data=workflow)


@workflow_router.post(
    "/{workflow_id}/publish",
    response_model=ResponseModel[PublishWorkflowResponse],
)
async def publish_workflow(
    request: Request,
    workflow_id: str,
    publish_request: PublishWorkflowRequest,
):
    """Publish a workflow with a specific version."""
    workflow = await WorkflowService.publish_workflow(
        session=db.session,
        workflow_id=workflow_id,
        version=publish_request.version,
        description=publish_request.description,
        request=request,
    )
    
    return ResponseModel(data=workflow)