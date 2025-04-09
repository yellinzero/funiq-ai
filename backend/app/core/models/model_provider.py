from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure import DBBase, DBUUIDModelMixin
from providers.models.core.models.model import ConfigurateMethod, ModelFeature, ModelPropertyKey, ModelType, PriceConfig
from providers.models.core.models.provider import ProviderDocs
from utils.json_schema import JSONSchema, UiSchema


class ModelProvider(DBBase, DBUUIDModelMixin):
    """Model provider model for storing model provider configurations per tenant"""

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    credentials: Mapped[dict | None] = mapped_column(JSON)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # for customizing the provider UI
    label: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000))
    credential_schema: Mapped[dict | None] = mapped_column(JSON)
    supported_model_types: Mapped[list[ModelType] | None] = mapped_column(JSON)
    docs: Mapped[ProviderDocs | None] = mapped_column(JSON)
    icon: Mapped[dict | None] = mapped_column(JSON)

    # Add relationship to Model
    models: Mapped[list["Model"]] = relationship("Model", back_populates="provider_obj", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("tenant_id", "provider", name="unique_tenant_provider"),)

    @property
    def is_active(self) -> bool:
        """Whether the provider is active (has credentials)"""
        return self.credentials is not None

    def __repr__(self) -> str:
        return f"<ModelProvider(tenant_id={self.tenant_id}, provider={self.provider}, is_active={self.is_active})>"


class Model(DBBase, DBUUIDModelMixin):
    """Model model for storing model configurations per tenant"""

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    credentials: Mapped[dict | None] = mapped_column(JSON)
    model: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_type: Mapped[ModelType] = mapped_column(String(50), nullable=False, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(index=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    configurate_method: Mapped[ConfigurateMethod] = mapped_column(String(50), nullable=False, index=True)

    # Model specific configurations
    label: Mapped[str | None] = mapped_column(String(255))
    features: Mapped[list[ModelFeature] | None] = mapped_column(JSON)
    model_properties: Mapped[dict[ModelPropertyKey, Any] | None] = mapped_column(JSON)
    pricing: Mapped[PriceConfig | None] = mapped_column(JSON)  # Store pricing details as JSON
    parameter_rules_ui_schema: Mapped[UiSchema | None] = mapped_column(JSON)
    parameter_rules_schema: Mapped[JSONSchema | None] = mapped_column(JSON)
    deprecated: Mapped[bool] = mapped_column(Boolean, default=False)

    # Add relationship to ModelProvider
    provider_obj: Mapped["ModelProvider"] = relationship("ModelProvider", back_populates="models")

    __table_args__ = (
        UniqueConstraint("tenant_id", "provider", "model", name="unique_tenant_provider_model"),
        ForeignKeyConstraint(
            ["tenant_id", "provider"],
            ["model_providers.tenant_id", "model_providers.provider"],
            name="fk_model_provider",
            ondelete="CASCADE",
        ),
    )

    def __repr__(self) -> str:
        return f"<Model(tenant_id={self.tenant_id}, provider={self.provider}, model={self.model})>"

    @property
    def is_active(self) -> bool:
        """Check if model is enabled, not deprecated and has valid configuration"""
        return self.is_enabled and not self.deprecated
