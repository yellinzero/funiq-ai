import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Enum, ForeignKey, Index, Integer, String, Text, and_, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure import (
    DBBase,
    DBUUIDModelMixin,
    WorkflowExecution,
    WorkflowExecutionLog,
)

if TYPE_CHECKING:
    from app.core.models.workflow import Workflow, WorkflowVersion
# ---------- Enums ----------


class AppStatus(str, enum.Enum):
    """Defines the status of an application"""

    ACTIVE = "active"  # Currently active
    INACTIVE = "inactive"  # Inactive
    DEPRECATED = "deprecated"  # Deprecated
    ARCHIVED = "archived"  # Archived


class MessageFrom(str, enum.Enum):
    """Defines the source of a message"""

    USER = "user"
    APP = "app"


class ConversationStatus(str, enum.Enum):
    """Defines the status of a conversation"""

    ACTIVE = "active"  # Normal conversation
    ARCHIVED = "archived"  # Archived conversation


# ---------- Models ----------
class App(DBBase, DBUUIDModelMixin):
    """AI Application model that represents a chatbot application"""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, comment="Reference to the tenant"
    )

    workflow_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True)

    status: Mapped[AppStatus] = mapped_column(
        Enum(AppStatus),
        nullable=False,
        default=AppStatus.ACTIVE,
        comment="Status of the application version",
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Name of the application")
    description: Mapped[str | None] = mapped_column(Text, comment="Description of the application")

    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="app", cascade="all, delete-orphan", lazy="raise"
    )

    workflow: Mapped["Workflow"] = relationship(
        "Workflow",
        uselist=False,
        cascade="all, delete",
        lazy="joined",
        foreign_keys=[workflow_id],
    )

    __table_args__ = (
        # Unique constraint for app name within tenant
        Index("uk_app_tenant_name", tenant_id, name, unique=True),
        # Query indexes
        Index("idx_app_tenant", tenant_id),
        Index("idx_app_workflow", workflow_id),
    )

    def __repr__(self) -> str:
        return f"<App(id={self.id}, name={self.name})>"
    
    @property
    def is_active(self) -> bool:
        return self.status == AppStatus.ACTIVE
    
    @property
    def is_inactive(self) -> bool:
        return self.status == AppStatus.INACTIVE
    
    @property
    def is_deprecated(self) -> bool:
        return self.status == AppStatus.DEPRECATED
    
    @property
    def is_archived(self) -> bool:
        return self.status == AppStatus.ARCHIVED


class Conversation(DBBase, DBUUIDModelMixin):
    """Conversation model that represents a chat session"""

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Conversation name")
    description: Mapped[str | None] = mapped_column(Text, comment="Conversation description")
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, comment="Reference to the tenant"
    )
    app_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("apps.id", ondelete="CASCADE"), nullable=False, comment="Reference to the app"
    )
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus),
        nullable=False,
        default=ConversationStatus.ACTIVE,
        comment="Conversation status",
    )

    message_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Number of messages in the conversation"
    )

    last_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="Last message id"
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at", lazy="raise"
    )
    app: Mapped["App"] = relationship(
        back_populates="conversations", uselist=False, cascade="all, delete", lazy="joined", foreign_keys=[app_id]
    )
    __table_args__ = (
        # Query indexes
        Index("idx_conversation_status", status),
        Index("idx_conversation_user", "created_by"),
        Index("idx_conversation_tenant", tenant_id),
        Index("idx_conversation_app", app_id),
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


class Message(DBBase, DBUUIDModelMixin):
    """Message model that represents individual messages in a conversation"""

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent conversation",
    )

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, comment="Reference to the workflow"
    )
    workflow_version: Mapped[str] = mapped_column(String(50), nullable=False, comment="Workflow version")
    workflow_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="App execution id"
    )

    message_from: Mapped[MessageFrom] = mapped_column(
        Enum(MessageFrom), nullable=False, comment="Message source (user or app)"
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Message content")
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Error message")
    thinking_content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Thinking process")

    images: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True, comment="Images")
    files: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True, comment="Files")
    audios: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True, comment="Audios")
    tools: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True, comment="Tools")

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages", cascade="all, delete", lazy="joined", foreign_keys=[conversation_id]
    )

    __table_args__ = (
        # Query indexes
        Index("idx_message_conversation", conversation_id),
        Index("idx_message_from", message_from),
        Index("idx_message_created", "created_at"),
    )

    @property
    def is_from_user(self) -> bool:
        """Check if the message is from a user"""
        return self.message_from == MessageFrom.USER

    @property
    def is_from_app(self) -> bool:
        """Check if the message is from the bot"""
        return self.message_from == MessageFrom.APP

    async def get_workflow_execution(self, session: AsyncSession) -> "WorkflowExecution":
        """Get the workflow execution"""
        result = await session.execute(select(WorkflowExecution).filter(WorkflowExecution.id == self.workflow_run_id))
        return result.scalar_one_or_none()

    async def get_workflow_execution_logs(self, session: AsyncSession) -> list[WorkflowExecutionLog]:
        """Get the workflow execution logs"""
        result = await session.execute(
            select(WorkflowExecutionLog).filter(WorkflowExecutionLog.run_id == self.workflow_run_id)
        )
        return result.scalars().all()

    async def get_workflow_version(self, session: AsyncSession) -> "WorkflowVersion":
        """Get the workflow version"""
        result = await session.execute(
            select(WorkflowVersion).filter(
                and_(
                    WorkflowVersion.version == self.workflow_version,
                    WorkflowVersion.workflow_id == self.workflow_id,
                )
            )
        )
        workflow_version = result.scalar_one_or_none()
        if not workflow_version:
            raise ValueError("Workflow version not found")
        return workflow_version

    def has_error(self) -> bool:
        """Check if the message has an error"""
        return self.error is not None
    
    def has_thinking(self) -> bool:
        """Check if the message has thinking content"""
        return self.thinking_content is not None
    
    def has_images(self) -> bool:
        """Check if the message has images"""
        return self.images is not None
    
    def has_files(self) -> bool:
        """Check if the message has files"""
        return self.files is not None
    
    def has_audios(self) -> bool:
        """Check if the message has audios"""
        return self.audios is not None
    
    def has_tools(self) -> bool:
        """Check if the message has tools"""
        return self.tools is not None