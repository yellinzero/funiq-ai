from typing import List

from fastapi import APIRouter, Request, status
from fastapi_async_sqlalchemy import db

from app.app.schemas import (
    AppCreate,
    AppResponse,
    AppTreeNode,
    AppUpdate,
    AppVersionResponse,
)
from app.app.service.app_service import AppService
from app.core.schemas import ResponseModel

app_router = APIRouter(prefix="/apps", tags=["App"])


# App routes
@app_router.get("", response_model=ResponseModel[List[AppResponse]])
async def list_apps(
    request: Request,
) -> ResponseModel[List[AppResponse]]:
    apps = await AppService.get_apps(session=db.session, request=request)
    return ResponseModel(
        data=apps,
        message="Apps fetched successfully"
    )


@app_router.post("", response_model=ResponseModel[AppResponse], status_code=status.HTTP_201_CREATED)
async def create_app(
    app: AppCreate,
    request: Request,
) -> ResponseModel[AppResponse]:
    new_app = await AppService.create_app(session=db.session, app=app, request=request)
    return ResponseModel(
        data=new_app,
        message="App created successfully"
    )


@app_router.get("/{app_id}", response_model=ResponseModel[AppResponse])
async def get_app(
    app_id: str,
    request: Request,
) -> ResponseModel[AppResponse]:
    return await AppService.get_app(session=db.session, app_id=str(app_id), request=request)


@app_router.put("/{app_id}", response_model=AppResponse)
async def update_app(
    app_id: str,
    app: AppUpdate,
    request: Request,
) -> ResponseModel[AppResponse]:
    updated_app = await AppService.update_app(session=db.session, app_id=str(app_id), app=app, request=request)
    return ResponseModel(
        data=updated_app,
        message="App updated successfully"
    )


@app_router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(
    app_id: str,
    request: Request,
):
    await AppService.delete_app(session=db.session, app_id=str(app_id), request=request)
    return ResponseModel(
        message="App deleted successfully"
    )


@app_router.get("/{app_id}/versions", response_model=List[AppVersionResponse])
async def list_app_versions(
    app_id: str,
    request: Request,
) -> ResponseModel[List[AppVersionResponse]]:
    app_versions = await AppService.get_app_versions(session=db.session, app_id=str(app_id), request=request)
    return ResponseModel(
        data=app_versions,
        message="App versions fetched successfully"
    )


@app_router.get("/with_versions", response_model=List[AppTreeNode])
async def get_apps_versions(
    request: Request,
) -> ResponseModel[List[AppTreeNode]]:
    apps_with_versions = await AppService.get_apps_with_versions(session=db.session, request=request)
    return ResponseModel(
        data=apps_with_versions,
        message="Apps with versions fetched successfully"
    )
