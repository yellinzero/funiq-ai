
import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import DBBase, DBUUIDIDModelMixin

if TYPE_CHECKING:
    from .workflow import Workflow


class AppType(str, enum.Enum):
    """Application type"""
    MODEL = "model"
    WORKFLOW = "workflow"


class App(DBBase, DBUUIDIDModelMixin):
    """Application model that represents a single workflow container.
    
    Each App has exactly one Workflow (one-to-one relationship). The App entity
    provides business context and metadata around its associated workflow.
    """

    # Basic information
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), 
        nullable=False, 
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        String(1000)
    )
    app_type: Mapped[AppType] = mapped_column(String(50), nullable=False, index=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # One-to-one relationship with Workflow
    workflow_id: Mapped[str] = mapped_column(
        ForeignKey("workflows.id"), 
        unique=True,  # Ensures one-to-one relationship at database level
        nullable=False
    )
    workflow: Mapped["Workflow"] = relationship(
        "Workflow", 
        back_populates="app",
        uselist=False,  # Ensures one-to-one relationship at ORM level
        single_parent=True,  # Indicates exclusive ownership
        cascade="all, delete-orphan"  # Automatically delete workflow when app is deleted
    )
    
    # Audit fields
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))

    __table_args__ = (UniqueConstraint("tenant_id", "name", "is_system", name="unique_tenant_app"),)

    def __repr__(self) -> str:
        return f"<App(id={self.id}, name={self.name}, is_system={self.is_system})>"
