import enum
from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import DBBase, DBUUIDIDModelMixin
from providers.models.core.models.model import ModelFeature, ModelType, PriceConfig
from providers.models.core.models.provider import ProviderDocs


class ProviderType(str, enum.Enum):
    system = "system"
    custom = "custom"


class ModelProvider(DBBase, DBUUIDIDModelMixin):
    """Model provider model for storing model provider configurations per tenant"""

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    credentials: Mapped[dict | None] = mapped_column(JSON)
    provider_type: Mapped[ProviderType] = mapped_column(String(50), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(index=True)

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

    def __repr__(self) -> str:
        return (
            f"<ModelProvider(tenant_id={self.tenant_id}, provider={self.provider}, provider_type={self.provider_type})>"
        )

    @property
    def is_active(self) -> bool:
        """Check if provider is enabled and has valid credentials"""
        return self.is_enabled and bool(self.credentials)


class Model(DBBase, DBUUIDIDModelMixin):
    """Model model for storing model configurations per tenant"""

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(ForeignKey("model_providers.provider"), nullable=False, index=True)
    credentials: Mapped[dict | None] = mapped_column(JSON)
    model: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_type: Mapped[ModelType] = mapped_column(String(50), nullable=False, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Model specific configurations
    label: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000))
    features: Mapped[list[ModelFeature] | None] = mapped_column(JSON)
    mode: Mapped[str | None] = mapped_column(String(50))
    context_size: Mapped[int | None] = mapped_column()
    pricing: Mapped[PriceConfig | None] = mapped_column(JSON)  # Store pricing details as JSON
    parameter_rules_schema: Mapped[dict | None] = mapped_column(JSON)
    deprecated: Mapped[bool] = mapped_column(Boolean, default=False)

    # Add relationship to ModelProvider
    provider_obj: Mapped["ModelProvider"] = relationship("ModelProvider", back_populates="models")

    __table_args__ = (UniqueConstraint("tenant_id", "provider", "model", name="unique_tenant_provider_model"),)

    def __repr__(self) -> str:
        return f"<Model(tenant_id={self.tenant_id}, provider={self.provider}, model={self.model})>"

    @property
    def is_active(self) -> bool:
        """Check if model is enabled, not deprecated and has valid configuration"""
        return self.is_enabled and not self.deprecated and bool(self.provider_obj.is_active)
