from typing import List

from pydantic import BaseModel

from providers.models.core.schemas import AIModelEntity, ProviderEntity


class ProviderInfo(ProviderEntity):
    pass


class GetModelProvidersResponse(BaseModel):
    providers: List[ProviderInfo]
    total: int


class ModelInfo(AIModelEntity):
    """Model info for a provider"""
    provider: str


class GetModelsResponse(BaseModel):
    models: List[ModelInfo]
    total: int


class SaveProviderRequest(BaseModel):
    """Request schema for saving a provider"""
    credentials: dict | None = None
    
    
class ProviderResponse(BaseModel):
    """Response schema for getting a provider"""
    provider: str
    credentials: dict | None = None
    
    
class ActiveModelProviderModelItem(BaseModel):
    model: str
    label: str
    group: str | None = None
    deprecated: bool | None = None
    

class ActiveModelProviderWithModels(BaseModel):
    provider: str
    label: str
    description: str
    models: List[ActiveModelProviderModelItem]