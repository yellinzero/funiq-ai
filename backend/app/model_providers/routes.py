from fastapi import APIRouter, Request

from app.schemas import ResponseModel

from .schemas import GetModelProvidersResponse, GetModelsResponse
from .service.provider_service import ProviderService

model_providers_router = APIRouter(prefix="/model-providers", tags=["Model Providers"])


@model_providers_router.get(
    "", response_model=ResponseModel[GetModelProvidersResponse], response_model_exclude_none=True
)
async def get_model_providers(request: Request):
    """
    Get all available model providers and their configurations from provider schema
    """
    providers = ProviderService.get_all_providers()
    return ResponseModel(data={"providers": providers, "total": len(providers)})


@model_providers_router.get(
    "/{provider_name}/models", response_model=ResponseModel[GetModelsResponse], response_model_exclude_none=True
)
async def get_models(request: Request, provider_name: str):
    """
    Get all available models from a specific provider
    """
    models = ProviderService.get_models(provider_name=provider_name)
    return ResponseModel(data={"models": models, "total": len(models)})
