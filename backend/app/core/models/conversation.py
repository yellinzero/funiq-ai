import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure import DBBase, DBUUIDModelMixin

if TYPE_CHECKING:
    from app.core.models.app import AppVersion

# ---------- Enums ----------


class MessageFrom(str, enum.Enum):
    """Defines the source of a message"""

    USER = "user"
    APP = "app"


class ConversationStatus(str, enum.Enum):
    """Defines the status of a conversation"""

    ACTIVE = "active"  # Normal conversation
    ARCHIVED = "archived"  # Archived conversation


# ---------- Models ----------
class Conversation(DBBase, DBUUIDModelMixin):
    """Conversation model that represents a chat session"""

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Conversation name")
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, comment="Reference to the tenant"
    )
    status: Mapped[ConversationStatus] = mapped_column(
        SQLAlchemyEnum(ConversationStatus),
        nullable=False,
        default=ConversationStatus.ACTIVE,
        comment="Conversation status",
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="User who created the conversation"
    )
    updated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="User who updated the conversation"
    )

    message_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Number of messages in the conversation"
    )

    last_message_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Last message id"
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )

    __table_args__ = (
        # Query indexes
        Index("idx_conversation_status", status),
        Index("idx_conversation_user", created_by),
        Index("idx_conversation_tenant", tenant_id),
    )

    @property
    def is_archived(self) -> bool:
        """Check if the conversation is archived"""
        return self.status == ConversationStatus.ARCHIVED

    @property
    def is_active(self) -> bool:
        """Check if the conversation is active"""
        return self.status == ConversationStatus.ACTIVE

    def archive(self) -> None:
        """Archive the conversation"""
        self.status = ConversationStatus.ARCHIVED

    def unarchive(self) -> None:
        """Unarchive the conversation"""
        self.status = ConversationStatus.ACTIVE


class Message(DBBase):
    """Message model that represents individual messages in a conversation"""

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="Unique identifier for the message"
    )
    app_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("app_versions.id", ondelete="SET NULL"), 
        nullable=True, 
        comment="Reference to the specific app version"
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent conversation",
    )
    execution_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, comment="Execution id")
    message_from: Mapped[MessageFrom] = mapped_column(
        SQLAlchemyEnum(MessageFrom), nullable=False, comment="Message source (user or app)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
        comment="Timestamp when the message was created",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), comment="User who created the message (only for user messages)"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="Message content")
    search_results: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True, comment="Search results")
    thinking_content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Thinking process")
    files: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True, comment="Files")

    # Relationships
    app_version: Mapped["AppVersion"] = relationship("AppVersion")
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    __table_args__ = (
        # Query indexes
        Index("idx_message_app_version", app_version_id),
        Index("idx_message_conversation", conversation_id),
        Index("idx_message_from", message_from),
        Index("idx_message_created", created_at),
    )

    @property
    def is_from_user(self) -> bool:
        """Check if the message is from a user"""
        return self.message_from == MessageFrom.USER

    @property
    def is_from_app(self) -> bool:
        """Check if the message is from the bot"""
        return self.message_from == MessageFrom.APP
