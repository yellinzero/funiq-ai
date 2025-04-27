from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure import DBBase, EncryptedJSON


class ModelProvider(DBBase):
    """Model provider model for storing model provider configurations per tenant"""

    provider: Mapped[str] = mapped_column(String(50), nullable=False, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), 
        nullable=False
    )

    credentials: Mapped[dict | None] = mapped_column(MutableDict.as_mutable(EncryptedJSON))

    @property
    def is_active(self) -> bool:
        """Whether the provider is active (has credentials)"""
        return self.credentials is not None

    def __repr__(self) -> str:
        return f"<ModelProvider(tenant_id={self.tenant_id}, provider={self.provider}, is_active={self.is_active})>"

    __table_args__ = (
        UniqueConstraint("tenant_id", "provider", name="unique_tenant_provider"),
    )