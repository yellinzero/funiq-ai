import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure import DBBase, DBUUIDModelMixin

if TYPE_CHECKING:
    from app.core.models.conversation import Message
    from app.core.models.workflow import Workflow
# ---------- Enums ----------


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
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="Reference to the parent workflow"
    )
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
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="app_version", viewonly=True)

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

    @property
    def is_deprecated(self) -> bool:
        """Check if this version is deprecated"""
        return self.status == AppVersionStatus.DEPRECATED

    @property
    def is_inactive(self) -> bool:
        """Check if this version is currently inactive"""
        return self.status == AppVersionStatus.INACTIVE

    @property
    def is_archived(self) -> bool:
        """Check if this version is archived"""
        return self.status == AppVersionStatus.ARCHIVED

    def deprecate(self) -> None:
        """Mark this version as deprecated"""
        self.status = AppVersionStatus.DEPRECATED
