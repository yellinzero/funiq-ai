from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.core.models.conversation import MessageFrom


class ConversationBase(BaseModel):
    name: str


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: str
    status: str
    message_count: int
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class MessageBase(BaseModel):
    content: str
    app_version_id: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    conversation_id: str
    execution_id: str | None
    message_from: MessageFrom
    created_at: datetime
    created_by: str | None
    search_results: List[dict] | None
    thinking_content: str | None
    files: List[dict] | None
    

class CompletionRequest(BaseModel):
    message: str