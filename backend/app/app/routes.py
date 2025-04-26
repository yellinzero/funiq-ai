from typing import List

from fastapi import APIRouter, Request, status
from fastapi_async_sqlalchemy import db

from app.app.schemas import (
    AppCreate,
    AppListResponse,
    AppPublishRequest,
    AppResponse,
    AppTreeNode,
    AppUpdate,
    AppVersionResponse,
)
from app.app.service.app_service import AppService
from app.core.schemas import ResponseModel

app_router = APIRouter(prefix="/apps", tags=["Apps"])


@app_router.get(
    "",
    response_model=ResponseModel[AppListResponse],
    response_model_exclude_none=True
)
async def list_apps(
    request: Request,
    page: int | None = None,
    page_size: int | None = None,
    search: str | None = None,
) -> ResponseModel[AppListResponse]:
    """
    Get list of apps with pagination and search support.
    
    Args:
        page: Page number (1-based)
        page_size: Number of items per page
        search: Optional search term
    """
    actual_page = page if page is not None else 1
    actual_page_size = page_size if page_size is not None else 20
    
    apps, total = await AppService.get_apps(
        session=db.session,
        request=request,
        page=actual_page,
        page_size=actual_page_size,
        search_term=search,
    )
    return ResponseModel(
        data=AppListResponse(
            items=apps,
            total=total,
        ),
        message="Apps fetched successfully"
    )


@app_router.post(
    "",
    response_model=ResponseModel[AppResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    app_create: AppCreate,
    request: Request,
) -> ResponseModel[AppResponse]:
    """Create a new application"""
    new_app = await AppService.create_application(
        session=db.session,
        app_create=app_create,
        request=request
    )
    return ResponseModel(
        data=new_app,
        message="App created successfully"
    )


@app_router.get(
    "/{app_id}",
    response_model=ResponseModel[AppResponse],
)
async def get_app(
    app_id: str,
    request: Request,
) -> ResponseModel[AppResponse]:
    """Get details of a specific application"""
    app = await AppService.get_app(
        session=db.session,
        app_id=app_id,
        request=request
    )
    return ResponseModel(
        data=app,
        message="App fetched successfully"
    )


@app_router.put(
    "/{app_id}",
    response_model=ResponseModel[AppResponse],
)
async def update_app(
    app_id: str,
    app_update: AppUpdate,
    request: Request,
) -> ResponseModel[AppResponse]:
    """Update an existing application"""
    updated_app = await AppService.update_app(
        session=db.session,
        app_id=app_id,
        app_update=app_update,
        request=request
    )
    return ResponseModel(
        data=updated_app,
        message="App updated successfully"
    )


@app_router.delete(
    "/{app_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_app(
    app_id: str,
    request: Request,
):
    """Delete an application"""
    await AppService.delete_app(
        session=db.session,
        app_id=app_id,
        request=request
    )
    return ResponseModel(message="App deleted successfully")


@app_router.get(
    "/{app_id}/versions",
    response_model=ResponseModel[List[AppVersionResponse]],
)
async def list_app_versions(
    app_id: str,
    request: Request,
) -> ResponseModel[List[AppVersionResponse]]:
    """Get all versions of a specific application"""
    versions = await AppService.get_app_versions(
        session=db.session,
        app_id=app_id,
        request=request
    )
    return ResponseModel(
        data=versions,
        message="App versions fetched successfully"
    )


@app_router.get(
    "/tree",
    response_model=ResponseModel[List[AppTreeNode]],
)
async def get_apps_tree(
    request: Request,
) -> ResponseModel[List[AppTreeNode]]:
    """Get all apps with their version information in a tree structure"""
    apps_tree = await AppService.get_apps_with_versions(
        session=db.session,
        request=request
    )
    return ResponseModel(
        data=apps_tree,
        message="Apps tree fetched successfully"
    )


@app_router.post(
    "/{app_id}/publish",
    response_model=ResponseModel[AppVersionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def publish_app_version(
    app_id: str,
    publish_request: AppPublishRequest,
    request: Request,
) -> ResponseModel[AppVersionResponse]:
    """Publish a new version of an application"""
    version = await AppService.publish_app(
        session=db.session,
        app_id=app_id,
        version=publish_request.version,
        workflow_version=publish_request.workflow_version,
        request=request
    )
    return ResponseModel(
        data=version,
        message="App version published successfully"
    )
