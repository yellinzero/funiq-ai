from fastapi import APIRouter, Request
from fastapi_async_sqlalchemy import db

from app.app.schemas import (
    AppInfo,
    AppListResponse,
    ConversationInfo,
    ConversationListResponse,
    CreateAppRequest,
    CreateConversationRequest,
    MessageInfo,
    UpdateAppRequest,
    UpdateConversationRequest,
)
from app.app.service.app_service import AppService
from app.app.service.conversation_service import ConversationService
from app.core.schemas import ResponseModel

app_router = APIRouter(prefix="/apps", tags=["Apps"])


@app_router.get("", response_model=ResponseModel[AppListResponse])
async def get_apps(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
) -> ResponseModel[AppListResponse]:
    """
    Get list of apps with pagination and search support.

    Args:
        page: Page number (1-based)
        page_size: Number of items per page
        search: Optional search term
    """
    apps, total = await AppService.get_apps(
        session=db.session,
        request=request,
        page=page,
        page_size=page_size,
        search_term=search,
    )
    return ResponseModel(
        data=AppListResponse(
            apps=apps,
            total=total,
        ),
    )


@app_router.post("", response_model=ResponseModel[AppInfo])
async def create_app(
    payload: CreateAppRequest,
    request: Request,
) -> ResponseModel[AppInfo]:
    """Create a new application"""
    new_app = await AppService.create_app(session=db.session, payload=payload, request=request)
    return ResponseModel(data=new_app)


@app_router.get("/{app_id}", response_model=ResponseModel[AppInfo])
async def get_app(
    app_id: str,
    request: Request,
) -> ResponseModel[AppInfo]:
    """Get details of a specific application"""
    app = await AppService.get_app(session=db.session, app_id=app_id, request=request)
    return ResponseModel(data=AppService.app_to_info(app))


@app_router.put("/{app_id}", response_model=ResponseModel[AppInfo])
async def update_app(
    app_id: str,
    payload: UpdateAppRequest,
    request: Request,
) -> ResponseModel[AppInfo]:
    """Update an existing application"""
    updated_app = await AppService.update_app(session=db.session, app_id=app_id, payload=payload, request=request)
    return ResponseModel(data=updated_app)


@app_router.delete("/{app_id}")
async def delete_app(
    app_id: str,
    request: Request,
):
    """Delete an application"""
    await AppService.delete_app(session=db.session, app_id=app_id, request=request)
    return ResponseModel(data={"status": "success"})


@app_router.get("/{app_id}/conversations", response_model=ResponseModel[ConversationListResponse])
async def get_conversations(
    app_id: str,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
) -> ResponseModel[ConversationListResponse]:
    """
    Get list of conversations with pagination and search support.

    Args:
        app_id: App Id
        page: Page number (1-based)
        page_size: Number of items per page
        search: Optional search term
    """
    return await ConversationService.get_conversations(
        session=db.session,
        app_id=app_id,
        page=page,
        page_size=page_size,
        search_term=search,
    )


@app_router.get("/conversations/{conversation_id}", response_model=ResponseModel[ConversationInfo])
async def get_conversation(
    conversation_id: str,
) -> ResponseModel[ConversationInfo]:
    """Get details of a specific conversation"""
    conversation = await ConversationService.get_conversation(
        session=db.session,
        conversation_id=conversation_id,
    )
    return ResponseModel(data=ConversationService.conversation_to_info(conversation))


@app_router.post("/{app_id}/conversations", response_model=ResponseModel[ConversationInfo])
async def create_conversation(
    app_id: str,
    payload: CreateConversationRequest,
    request: Request,
) -> ResponseModel[ConversationInfo]:
    """Create a new conversation"""
    new_conversation = await ConversationService.create_conversation(
        session=db.session,
        app_id=app_id,
        payload=payload,
        request=request,
    )
    return ResponseModel(data=new_conversation)


@app_router.put("/conversations/{conversation_id}", response_model=ResponseModel[ConversationInfo])
async def update_conversation(
    conversation_id: str,
    payload: UpdateConversationRequest,
    request: Request,
) -> ResponseModel[ConversationInfo]:
    """Update an existing conversation"""
    updated_conversation = await ConversationService.update_conversation(
        session=db.session,
        conversation_id=conversation_id,
        payload=payload,
        request=request,
    )
    return ResponseModel(data=updated_conversation)


@app_router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    request: Request,
) -> ResponseModel[None]:
    """Delete a conversation"""
    await ConversationService.delete_conversation(
        session=db.session,
        conversation_id=conversation_id,
        request=request,
    )
    return ResponseModel(data={"status": "success"})


@app_router.get("/conversations/{conversation_id}/messages", response_model=ResponseModel[list[MessageInfo]])
async def get_messages(
    conversation_id: str,
    request: Request,
) -> ResponseModel[list[MessageInfo]]:
    """Get all messages of a conversation"""
    return await ConversationService.get_messages(session=db.session, conversation_id=conversation_id, request=request)
