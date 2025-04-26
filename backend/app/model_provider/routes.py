from fastapi import APIRouter, Request
from fastapi_async_sqlalchemy import db

from app.core.schemas import ResponseModel

from .schemas import (
    ActiveModelProviderWithModels,
    GetModelProvidersResponse,
    GetModelsResponse,
    ProviderResponse,
    SaveProviderRequest,
)
from .service.provider_service import ProviderService

model_providers_router = APIRouter(prefix="/model-providers", tags=["Model Providers"])


@model_providers_router.get(
    "", response_model=ResponseModel[GetModelProvidersResponse], response_model_exclude_none=True
)
async def get_model_providers(request: Request):
    """
    Get all available model providers and their configurations from provider schema
    """
    providers = await ProviderService.get_all_providers()
    return ResponseModel(data={"providers": providers, "total": len(providers)})


@model_providers_router.get(
    "/{provider_name}/models", response_model=ResponseModel[GetModelsResponse], response_model_exclude_none=True
)
async def get_models(request: Request, provider_name: str):
    """
    Get all available models from a specific provider
    """
    models = await ProviderService.get_models(
        session=db.session, tenant_id=request.state.tenant_id, provider_name=provider_name
    )
    return ResponseModel(data={"models": models, "total": len(models)})


@model_providers_router.get(
    "/active-providers",
    response_model=ResponseModel[list[ActiveModelProviderWithModels]],
    response_model_exclude_none=True,
)
async def get_active_providers(request: Request):
    """
    Get all active model providers with their models
    """
    providers = await ProviderService.get_active_providers(session=db.session, tenant_id=request.state.tenant_id)
    return ResponseModel(data=providers)


@model_providers_router.get("/{provider_name}", response_model=ResponseModel[ProviderResponse])
async def get_provider(request: Request, provider_name: str):
    """
    Get a provider configuration by name
    """
    provider = await ProviderService.get_provider(
        session=db.session, tenant_id=request.state.tenant_id, provider_name=provider_name
    )
    return ResponseModel(
        data={
            "provider": provider.provider,
            "credentials": provider.credentials,
            "is_active": provider.is_active,
        }
    )


@model_providers_router.post("/{provider_name}", response_model=ResponseModel[ProviderResponse])
async def save_provider(request: Request, provider_name: str, payload: SaveProviderRequest):
    """
    Save a provider configuration
    """
    provider = await ProviderService.save_provider(
        session=db.session, tenant_id=request.state.tenant_id, provider_name=provider_name, payload=payload
    )
    return ResponseModel(
        data={
            "provider": provider.provider,
            "credentials": provider.credentials,
            "is_active": provider.is_active,
        }
    )
