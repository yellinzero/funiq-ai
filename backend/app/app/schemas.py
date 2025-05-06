from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.core.models.app import ConversationStatus, MessageFrom


class AppInfo(BaseModel):
    id: str
    name: str
    workflow_id: str | None = None
    description: str | None = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class CreateAppRequest(BaseModel):
    name: str
    description: str | None = None
    

class UpdateAppRequest(BaseModel):
    name: str | None = None
    description: str | None = None


class AppListResponse(BaseModel):
    apps: List[AppInfo]
    total: int


class ConversationInfo(BaseModel):
    id: str
    name: str
    description: str | None = None
    status: ConversationStatus
    message_count: int
    last_message_id: int | None = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime
    

class ConversationListResponse(BaseModel):
    conversations: List[ConversationInfo]
    total: int
    

class CreateConversationRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    

class UpdateConversationRequest(BaseModel):
    name: str | None = None
    description: str | None = None


class MessageInfo(BaseModel):
    id: str
    workflow_id: str | None = None
    workflow_version: str | None = None
    conversation_id: str
    workflow_run_id: str | None = None
    message_from: MessageFrom
    content: str | None = None
    error: str | None = None
    thinking_content: str | None = None
    images: list[dict] | None = None
    files: list[dict] | None = None
    audios: list[dict] | None = None
    tools: list[dict] | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


class CompletionRequest(BaseModel):
    workflow_version_id: str
    message: str
    files: list[dict] | None = None
    images: list[dict] | None = None
    audios: list[dict] | None = None
    