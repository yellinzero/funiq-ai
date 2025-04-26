from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure import DBBase
from providers.models.core.schemas import (
    ModelFeature,
    ModelPropertyKey,
    ModelType,
    PriceConfig,
)


class ModelProvider(DBBase):
    """Model provider model for storing model provider configurations per tenant"""

    provider: Mapped[str] = mapped_column(String(50), nullable=False, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)

    credentials: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (UniqueConstraint("tenant_id", "provider", name="unique_tenant_provider"),)

    @property
    def is_active(self) -> bool:
        """Whether the provider is active (has credentials)"""
        return self.credentials is not None

    def __repr__(self) -> str:
        return f"<ModelProvider(tenant_id={self.tenant_id}, provider={self.provider}, is_active={self.is_active})>"

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_model_provider_tenant",
            ondelete="CASCADE",
        ),
    )


class CustomizedModel(DBBase):
    """Model model for storing customize model configurations per tenant"""

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        primary_key=True,
    )
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model_type: Mapped[ModelType] = mapped_column(String(50), nullable=False, index=True)

    # Model specific configurations
    label: Mapped[str | None] = mapped_column(String(255))
    features: Mapped[list[ModelFeature] | None] = mapped_column(JSON)
    group: Mapped[str | None] = mapped_column(String(50))
    model_properties: Mapped[dict[ModelPropertyKey, Any] | None] = mapped_column(JSON)
    pricing: Mapped[list[PriceConfig] | None] = mapped_column(JSON)
    parameter_rules_ui_schema: Mapped[dict | None] = mapped_column(JSON)
    parameter_rules_schema: Mapped[dict | None] = mapped_column(JSON)
    deprecated: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_customized_model_tenant",
            ondelete="CASCADE",
        ),
    )

    def __repr__(self) -> str:
        return f"<CustomizedModel(tenant_id={self.tenant_id}, provider={self.provider}, model={self.model})>"