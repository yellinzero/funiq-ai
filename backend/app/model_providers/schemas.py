from datetime import datetime
from typing import List

from pydantic import BaseModel

from providers.models.core.models.model import AIModelEntity, ModelType
from providers.models.core.models.provider import ProviderEntity
from utils.json_schema import UiSchema


class ProviderInfo(ProviderEntity):
    ui_schema: dict[str, dict[str, UiSchema | None] | None] | None = None


class GetModelProvidersResponse(BaseModel):
    providers: List[ProviderInfo]
    total: int


class ModelInfo(AIModelEntity):
    """Model info for a provider"""
    tenant_id: str
    provider: str
    is_enabled: bool
    is_system: bool
    last_used_at: datetime | None = None


class GetModelsResponse(BaseModel):
    models: List[ModelInfo]
    total: int


class SaveProviderRequest(BaseModel):
    """Request schema for saving a provider"""
    is_system: bool
    credentials: dict | None = None
    

class SaveModelRequest(BaseModel):
    """Request schema for saving a model"""
    is_system: bool
    is_enabled: bool | None = None
    
    
class ProviderResponse(BaseModel):
    """Response schema for getting a provider"""
    provider: str
    is_system: bool
    is_active: bool
    credentials: dict | None = None


class ModelResponse(BaseModel):
    """Response schema for getting a model"""
    provider: str
    model: str
    model_type: ModelType
    is_system: bool
    is_enabled: bool
    last_used_at: datetime | None = None
    
    