from fastapi import APIRouter, Request
from fastapi_async_sqlalchemy import db

from app.core.schemas import ResponseModel

from .schemas import (
    GetModelProvidersResponse,
    GetModelsResponse,
    ModelResponse,
    ProviderResponse,
    SaveModelRequest,
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
            "is_system": provider.is_system,
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
            "is_system": provider.is_system,
            "credentials": provider.credentials,
            "is_active": provider.is_active,
        }
    )


@model_providers_router.get("/{provider_name}/models/{model_name}", response_model=ResponseModel[ModelResponse])
async def get_model(request: Request, provider_name: str, model_name: str):
    """
    Get a model configuration by name
    """
    model = await ProviderService.get_model(
        session=db.session, tenant_id=request.state.tenant_id, provider_name=provider_name, model_name=model_name
    )
    return ResponseModel(
        data={
            "provider": model.provider,
            "model": model.model,
            "model_type": model.model_type,
            "is_system": model.is_system,
            "is_enabled": model.is_enabled,
            "last_used_at": model.last_used_at,
        }
    )


@model_providers_router.post("/{provider_name}/models/{model_name}", response_model=ResponseModel[ModelResponse])
async def save_model(request: Request, provider_name: str, model_name: str, payload: SaveModelRequest):
    """
    Save a model configuration
    """
    model = await ProviderService.save_model(
        session=db.session,
        tenant_id=request.state.tenant_id,
        provider_name=provider_name,
        model_name=model_name,
        payload=payload,
    )
    return ResponseModel(
        data={
            "provider": model.provider,
            "model": model.model,
            "model_type": model.model_type,
            "is_system": model.is_system,
            "is_enabled": model.is_enabled,
            "last_used_at": model.last_used_at,
        }
    )


@model_providers_router.post("/{provider_name}/models/{model_name}/enable", response_model=ResponseModel[ModelResponse])
async def enable_model(request: Request, provider_name: str, model_name: str):
    """
    Enable a model and create its associated system app if it doesn't exist
    """
    model = await ProviderService.enable_model(
        session=db.session,
        tenant_id=request.state.tenant_id,
        provider_name=provider_name,
        model_name=model_name,
        request=request,
    )
    return ResponseModel(
        data={
            "provider": model.provider,
            "model": model.model,
            "model_type": model.model_type,
            "is_system": model.is_system,
            "is_enabled": model.is_enabled,
            "last_used_at": model.last_used_at,
        }
    )
