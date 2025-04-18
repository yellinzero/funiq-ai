import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure import DBBase, DBUUIDModelMixin

if TYPE_CHECKING:
    from app.core.models.workflow import Workflow

# ---------- Enums ----------


class MessageFrom(str, enum.Enum):
    """Defines the source of a message"""

    USER = "user"
    APP = "app"


class ConversationStatus(str, enum.Enum):
    """Defines the status of a conversation"""

    ACTIVE = "active"  # Normal conversation
    ARCHIVED = "archived"  # Archived conversation


class AppVersionStatus(str, enum.Enum):
    """Defines the status of an application version"""

    ACTIVE = "active"  # Currently active version
    INACTIVE = "inactive"  # Inactive version
    DEPRECATED = "deprecated"  # Deprecated version
    ARCHIVED = "archived"  # Archived version


# ---------- Models ----------


class App(DBBase, DBUUIDModelMixin):
    """AI Application model that represents a chatbot application"""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, comment="Reference to the tenant"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Name of the application")
    description: Mapped[str | None] = mapped_column(String(1000), comment="Description of the application")
    is_system: Mapped[bool] = mapped_column(default=False, comment="Whether this is a system application")
    version: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Current version number")
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, comment="Last execution timestamp")

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="User who created the application"
    )
    updated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="User who updated the application"
    )

    versions: Mapped[list["AppVersion"]] = relationship(back_populates="app", cascade="all, delete-orphan")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="app", cascade="all, delete-orphan")

    workflow: Mapped["Workflow"] = relationship(
        "Workflow",
        back_populates="app",
        uselist=False,
        cascade="all, delete-orphan",
    )
    __table_args__ = (
        # Unique constraint for app name within tenant
        Index("uk_app_tenant_name", tenant_id, name, unique=True),
        # Query indexes
        Index("idx_app_tenant", tenant_id),
        Index("idx_app_system", is_system),
        Index("idx_app_version", version),
    )

    def __repr__(self) -> str:
        return f"<App(id={self.id}, name={self.name}, is_system={self.is_system})>"

    @property
    def snapshot(self) -> dict[str, Any]:
        """Get the snapshot of the app."""
        return {
            "name": self.name,
            "description": self.description,
        }


class AppVersion(DBBase, DBUUIDModelMixin):
    """Application version model that tracks different versions of an application"""

    app_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("apps.id", ondelete="CASCADE"), nullable=False, comment="Reference to the parent application"
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False, comment="Version number")
    workflow_version: Mapped[str] = mapped_column(String(50), nullable=False, comment="Associated workflow version")
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="Publication timestamp")
    published_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="User who published this version"
    )
    status: Mapped[AppVersionStatus] = mapped_column(
        SQLAlchemyEnum(AppVersionStatus), nullable=False, default=AppVersionStatus.INACTIVE, comment="Version status"
    )
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, comment="Version snapshot data")

    # Relationships
    app: Mapped["App"] = relationship(back_populates="versions")

    __table_args__ = (
        # Unique constraint for version within app
        Index("uk_app_version", app_id, version, unique=True),
        # Query indexes
        Index("idx_version_status", status),
        Index("idx_version_published", published_at),
    )

    @property
    def is_active(self) -> bool:
        """Check if this version is currently active"""
        return self.status == AppVersionStatus.ACTIVE

    def deprecate(self) -> None:
        """Mark this version as deprecated"""
        self.status = AppVersionStatus.DEPRECATED


class Conversation(DBBase, DBUUIDModelMixin):
    """Conversation model that represents a chat session"""

    app_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("apps.id", ondelete="CASCADE"), nullable=False, comment="Reference to the application"
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False, comment="Application version used")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Conversation name")
    summary: Mapped[str | None] = mapped_column(String(500), comment="Conversation summary")
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

    last_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="Last message id"
    )

    # Relationships
    app: Mapped["App"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        # Query indexes
        Index("idx_conversation_app", app_id),
        Index("idx_conversation_status", status),
        Index("idx_conversation_user", created_by),
    )

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
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent conversation",
    )
    execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="Execution id"
    )
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
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    __table_args__ = (
        # Query indexes
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
