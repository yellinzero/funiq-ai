import enum
import uuid
from datetime import datetime, timezone

from packaging.version import InvalidVersion, Version
from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.attributes import validates

from database import DBBase, DBUUIDIDModelMixin

from .workflows import Workflow


class AppStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class AppType(str, enum.Enum):
    SYSTEM = "system"
    CUSTOM = "custom"


class App(DBBase, DBUUIDIDModelMixin):
    """App table - container for a workflow"""

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    type: Mapped[AppType] = mapped_column(Enum(AppType), default=AppType.CUSTOM)
    status: Mapped[AppStatus] = mapped_column(Enum(AppStatus), default=AppStatus.DRAFT)
    updated_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    version: Mapped[str] = mapped_column(String(255), nullable=False, default="0.0.1")
    published_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    published_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    # One-to-one relationship with Workflow
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), unique=True, nullable=False)
    workflow: Mapped["Workflow"] = relationship("Workflow", uselist=False, backref="app")

    __table_args__ = (UniqueConstraint("tenant_id", "name", name="unique_tenant_app"),)

    def __repr__(self) -> str:
        return f"<App(tenant_id={self.tenant_id}, name={self.name}, type={self.type})>"

    @validates("version")
    def validate_version(self, key: str, version: str) -> str:
        try:
            Version(version)
        except InvalidVersion as e:
            raise ValueError(f"Invalid semantic version: {version}") from e
        return version
