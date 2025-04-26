from typing import List

from fastapi import APIRouter, Request, status
from fastapi.responses import StreamingResponse
from fastapi_async_sqlalchemy import db

from app.conversation.schemas import (
    CompletionRequest,
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    MessageResponse,
)
from app.core.schemas import ResponseModel

from .service.conversation_service import ConversationService

conversation_router = APIRouter(prefix="/conversations", tags=["Conversation"])


# Conversation routes
@conversation_router.get("", response_model=ResponseModel[List[ConversationResponse]])
async def list_conversations(
    request: Request,
) -> List[ConversationResponse]:
    conversations = await ConversationService.get_conversations(session=db.session, request=request)
    conversations_data = [
        {
            "id": str(conversation.id),
            "name": conversation.name,
            "status": conversation.status,
            "message_count": conversation.message_count,
            "created_by": str(conversation.created_by),
            "updated_by": str(conversation.updated_by),
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "last_message_id": str(conversation.last_message_id),
        }
        for conversation in conversations
    ]
    return ResponseModel(data=conversations_data, message="Conversations fetched successfully")


@conversation_router.post("", response_model=ResponseModel[ConversationResponse], status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    request: Request,
) -> ConversationResponse:
    new_conversation = await ConversationService.create_conversation(
        session=db.session, conversation=conversation, request=request
    )

    return ResponseModel(
        data={
            "id": str(new_conversation.id),
            "name": new_conversation.name,
            "status": new_conversation.status,
            "message_count": new_conversation.message_count,
            "created_by": str(new_conversation.created_by),
            "updated_by": str(new_conversation.updated_by),
            "created_at": new_conversation.created_at,
            "updated_at": new_conversation.updated_at,
            "last_message_id": new_conversation.last_message_id,
        },
        message="Conversation created successfully",
    )


@conversation_router.get("/{conversation_id}", response_model=ResponseModel[ConversationResponse])
async def get_conversation(
    conversation_id: str,
    request: Request,
) -> ConversationResponse:
    conversation = await ConversationService.get_conversation(session=db.session, conversation_id=str(conversation_id))
    return ResponseModel(
        data={
            "id": str(conversation.id),
            "name": conversation.name,
            "status": conversation.status,
            "message_count": conversation.message_count,
            "created_by": str(conversation.created_by),
            "updated_by": str(conversation.updated_by),
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "last_message_id": str(conversation.last_message_id),
        },
        message="Conversation fetched successfully",
    )


@conversation_router.put("/{conversation_id}", response_model=ResponseModel[ConversationResponse])
async def update_conversation(
    conversation_id: str,
    conversation: ConversationUpdate,
    request: Request,
) -> ConversationResponse:
    updated_conversation = await ConversationService.update_conversation(
        session=db.session, conversation_id=str(conversation_id), conversation=conversation, request=request
    )
    return ResponseModel(
        data={
            "id": str(updated_conversation.id),
            "name": updated_conversation.name,
            "status": updated_conversation.status,
            "message_count": updated_conversation.message_count,
            "created_by": str(updated_conversation.created_by),
            "updated_by": str(updated_conversation.updated_by),
            "created_at": updated_conversation.created_at,
            "updated_at": updated_conversation.updated_at,
            "last_message_id": str(updated_conversation.last_message_id),
        },
        message="Conversation updated successfully",
    )


@conversation_router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    request: Request,
):
    await ConversationService.delete_conversation(
        session=db.session, conversation_id=str(conversation_id), request=request
    )
    return ResponseModel(message="Conversation deleted successfully")


# Message routes
@conversation_router.get("/{conversation_id}/messages", response_model=ResponseModel[List[MessageResponse]])
async def list_messages(
    conversation_id: str,
    request: Request,
) -> List[MessageResponse]:
    messages = await ConversationService.get_messages(
        session=db.session, conversation_id=str(conversation_id), request=request
    )
    return ResponseModel(data=messages, message="Messages fetched successfully")


# Completion route
@conversation_router.post("/{conversation_id}/completion")
async def completion(
    conversation_id: str,
    app_version_id: str,
    request: Request,
    completion_request: CompletionRequest,
):
    generator = await ConversationService.completion(
        message=completion_request.message,
        session=db.session,
        conversation_id=str(conversation_id),
        app_version_id=str(app_version_id),
        request=request,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
