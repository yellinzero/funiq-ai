from typing import List

from pydantic import BaseModel

from providers.models.core.models.model import AIModelEntity
from providers.models.core.models.provider import ProviderEntity
from utils.json_schemas.ui_base import UiSchema


class ProviderInfo(ProviderEntity):
    ui_schema: dict[str, dict[str, UiSchema | None] | None] | None = None


class GetModelProvidersResponse(BaseModel):
    providers: List[ProviderInfo]
    total: int


class GetModelsResponse(BaseModel):
    models: List[AIModelEntity]
    total: int
