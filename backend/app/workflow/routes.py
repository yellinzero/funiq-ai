from fastapi import APIRouter, Request
from fastapi_async_sqlalchemy import db

from app.core.schemas import ResponseModel
from providers.operators.core import OperatorEntity

from .schemas import (
    CreateWorkflowRequest,
    CreateWorkflowVersionPayload,
    GetWorkflowDebugSnapshotsResponse,
    GetWorkflowsResponse,
    GetWorkflowVersionsResponse,
    SaveWorkflowRequest,
    WorkflowEdgeInfo,
    WorkflowInfo,
    WorkflowNodeInfo,
    WorkflowVersionInfo,
)
from .service.operator_service import OperatorService
from .service.workflow_service import WorkflowService

workflow_router = APIRouter(prefix="/workflows", tags=["Workflows"])


@workflow_router.get("/operators", response_model=ResponseModel[list[OperatorEntity]], response_model_exclude_none=True)
async def get_operators(request: Request):
    """
    Get all available operators
    """
    operators = OperatorService.get_all_operators()
    return ResponseModel(data=operators)


@workflow_router.get(
    "",
    response_model=ResponseModel[GetWorkflowsResponse],
)
async def get_workflows(
    request: Request,
    app_id: str,
):
    workflows = await WorkflowService.get_workflows(
        session=db.session,
        app_id=app_id,
    )
    return ResponseModel(
        data=GetWorkflowsResponse(workflows=workflows, total=len(workflows)),
    )


@workflow_router.post(
    "",
    response_model=ResponseModel[WorkflowInfo],
)
async def create_workflow(
    request: Request,
    payload: CreateWorkflowRequest,
):
    workflow = await WorkflowService.create_workflow(
        session=db.session,
        request=request,
        payload=payload,
    )
    return ResponseModel(data=WorkflowService.serialize_workflow(workflow))


@workflow_router.get(
    "/{workflow_id}",
    response_model=ResponseModel[WorkflowInfo],
)
async def get_workflow(
    request: Request,
    workflow_id: str,
):
    workflow = await WorkflowService.get_workflow(
        session=db.session,
        workflow_id=workflow_id,
    )
    return ResponseModel(data=workflow)


@workflow_router.put(
    "/{workflow_id}",
    response_model=ResponseModel[WorkflowInfo],
)
async def update_workflow(
    request: Request,
    workflow_id: str,
    payload: SaveWorkflowRequest,
):
    workflow = await WorkflowService.save_workflow(
        session=db.session,
        request=request,
        workflow_id=workflow_id,
        payload=payload,
    )
    return ResponseModel(data=workflow)


@workflow_router.delete(
    "/{workflow_id}",
    response_model=ResponseModel[None],
)
async def delete_workflow(
    request: Request,
    workflow_id: str,
):
    workflow = await WorkflowService.delete_workflow(
        session=db.session,
        workflow_id=workflow_id,
    )
    return ResponseModel(data={"status": "success"})


@workflow_router.post(
    "/{workflow_id}/publish",
    response_model=ResponseModel[WorkflowVersionInfo],
)
async def create_workflow_version(
    request: Request,
    workflow_id: str,
    payload: CreateWorkflowVersionPayload,
):
    workflow_version = await WorkflowService.publish_workflow(
        session=db.session,
        request=request,
        workflow_id=workflow_id,
        payload=payload,
    )
    return ResponseModel(data=workflow_version)


@workflow_router.get(
    "/{workflow_id}/versions",
    response_model=ResponseModel[GetWorkflowVersionsResponse],
)
async def get_workflow_versions(
    request: Request,
    workflow_id: str,
):
    workflow_versions = await WorkflowService.get_workflow_versions(
        session=db.session,
        workflow_id=workflow_id,
    )
    return ResponseModel(data=GetWorkflowVersionsResponse(versions=workflow_versions, total=len(workflow_versions)))


@workflow_router.get(
    "/{workflow_id}/debug-snapshots",
    response_model=ResponseModel[GetWorkflowDebugSnapshotsResponse],
)
async def get_workflow_debug_snapshots(
    request: Request,
    workflow_id: str,
):
    workflow_debug_snapshots = await WorkflowService.get_workflow_debug_snapshots(
        session=db.session,
        workflow_id=workflow_id,
    )
    return ResponseModel(
        data=GetWorkflowDebugSnapshotsResponse(snapshots=workflow_debug_snapshots, total=len(workflow_debug_snapshots))
    )


@workflow_router.get(
    "/{workflow_id}/nodes",
    response_model=ResponseModel[list[WorkflowNodeInfo]],
)
async def get_workflow_nodes(
    request: Request,
    workflow_id: str,
):
    workflow_nodes = await WorkflowService.get_workflow_nodes(
        session=db.session,
        workflow_id=workflow_id,
    )
    return ResponseModel(data=workflow_nodes)


@workflow_router.get(
    "/{workflow_id}/edges",
    response_model=ResponseModel[list[WorkflowEdgeInfo]],
)
async def get_workflow_edges(
    request: Request,
    workflow_id: str,
):
    workflow_edges = await WorkflowService.get_workflow_edges(
        session=db.session,
        workflow_id=workflow_id,
    )
    return ResponseModel(data=workflow_edges)
