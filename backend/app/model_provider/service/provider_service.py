from typing import List

from fastapi import status
from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ModelProviderErrorCode
from app.core.models.model_provider import ModelProvider as DBModelProvider
from configs import funiq_ai_config
from providers.models.core import ModelProvider, ProviderFactory
from providers.models.core.schemas import AIModelEntity

from ..schemas import ActiveModelProviderWithModels, ModelInfo, ProviderInfo, SaveProviderRequest


class ProviderService:
    @staticmethod
    async def get_all_providers() -> List[ProviderInfo]:
        """
        Get all available providers and their configurations.

        Returns:
            List[ProviderInfo]: List of provider information

        Raises:
            ModelProviderErrorCode: When provider operation fails
        """
        try:
            providers = ProviderFactory.get_all_providers()
            provider_schemas = []

            for provider in providers:
                provider_info = ProviderService._handle_provider_schema(provider)
                provider_schemas.append(provider_info)

            return provider_schemas
        except Exception as e:
            logger.error(f"Error fetching providers: {e}")
            raise ModelProviderErrorCode.FETCH_PROVIDERS_FAILED.exception(
                data={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_models(provider_name: str) -> List[ModelInfo]:
        """
        Get all models for a specific provider, including factory models and customized models.

        Args:
            session: Database session
            tenant_id: ID of the tenant
            provider_name: Name of the provider

        Returns:
            List[ModelInfo]: List of model information

        Raises:
            ModelProviderErrorCode: When provider or model operation fails
        """
        try:
            # Get models from provider factory
            factory_models = ProviderFactory.get_models(provider_name=provider_name)
            if not factory_models:
                logger.error(f"No models found for provider: {provider_name}")
                raise ModelProviderErrorCode.MODEL_NOT_FOUND.exception(
                    data={"provider": provider_name}, status_code=status.HTTP_404_NOT_FOUND
                )

            # Convert factory models to ModelInfo
            model_info_list = [
                ModelInfo(
                    **model.model_dump(),
                    provider=provider_name,
                )
                for model in factory_models
            ]

            return model_info_list
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            raise ModelProviderErrorCode.FETCH_MODELS_FAILED.exception(
                data={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_model(provider_name: str, model_name: str) -> AIModelEntity:
        """
        Get a model by name

        Args:
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            ModelInfo: The model information
        """
        model = ProviderFactory.get_model(model_name=model_name, provider_name=provider_name)

        if not model:
            raise ModelProviderErrorCode.MODEL_NOT_FOUND.exception(
                data={"provider": provider_name, "model": model_name}, status_code=status.HTTP_404_NOT_FOUND
            )

        return model

    @staticmethod
    async def save_provider(
        session: AsyncSession, tenant_id: str, provider_name: str, payload: SaveProviderRequest
    ) -> DBModelProvider:
        """
        Save a provider configuration

        Args:
            session: Database session
            tenant_id: ID of the tenant
            payload: Provider configuration

        Returns:
            DBModelProvider: The saved provider configuration
        """
        logger.info(
            "Saving provider configuration",
            extra={"tenant_id": tenant_id, "provider": provider_name},
        )

        # Check if provider exists
        result = await session.execute(
            select(DBModelProvider).where(
                DBModelProvider.tenant_id == tenant_id, DBModelProvider.provider == provider_name
            )
        )
        provider = result.scalars().first()

        if provider:
            logger.info("Updating existing provider configuration", extra={"provider": provider.provider})
            provider.credentials = payload.credentials
            await provider.save(session)
            return provider

        # Create new provider
        provider_data = {
            "tenant_id": tenant_id,
            "provider": provider_name,
            "credentials": payload.credentials,
        }

        provider = DBModelProvider(**provider_data)
        await provider.save(session)

        await session.commit()
        logger.info("Created new provider configuration", extra={"provider": provider.provider})
        return provider

    @staticmethod
    async def get_provider(session: AsyncSession, tenant_id: str, provider_name: str) -> DBModelProvider:
        """
        Get a provider by name

        Args:
            session: Database session
            tenant_id: ID of the tenant
            provider_name: Name of the provider

        Returns:
            DBModelProvider: The provider configuration
        """
        logger.info("Fetching provider configuration", extra={"tenant_id": tenant_id, "provider": provider_name})

        result = await session.execute(
            select(DBModelProvider).where(
                DBModelProvider.tenant_id == tenant_id, DBModelProvider.provider == provider_name
            )
        )
        provider = result.scalars().first()

        if not provider:
            raise ModelProviderErrorCode.PROVIDER_NOT_FOUND.exception(
                data={"provider": provider_name}, status_code=status.HTTP_404_NOT_FOUND
            )

        return provider

    @staticmethod
    async def get_active_providers(session: AsyncSession, tenant_id: str) -> List[ActiveModelProviderWithModels]:
        """
        Get all active providers and their models.

        Args:
            session: Database session
            tenant_id: ID of the tenant

        Returns:
            List[dict]: List of active providers with their models
        """
        # Get active providers from database
        result = await session.execute(
            select(DBModelProvider).where(
                and_(DBModelProvider.tenant_id == tenant_id, DBModelProvider.credentials.isnot(None))
            )
        )
        active_providers = result.scalars().all()
        providers_with_models = []
        for provider in active_providers:
            # Get provider schema
            provider_instance = ProviderFactory.get_provider_instance(provider.provider)
            if not provider_instance:
                continue

            provider_info = ProviderService._handle_provider_schema(provider=provider_instance)
            # Get models for this provider
            models = await ProviderService.get_models(provider_name=provider.provider)

            providers_with_models.append(
                {
                    "provider": provider_info.provider,
                    "label": provider_info.label,
                    "description": provider_info.description,
                    "models": [
                        {
                            "model": model.model,
                            "label": model.label,
                            "group": model.group,
                            "deprecated": model.deprecated,
                        }
                        for model in models
                    ],
                }
            )
        return providers_with_models

    @staticmethod
    def _handle_provider_schema(provider: ModelProvider) -> ProviderInfo:
        """
        Handle provider schema
        """
        provider_schema = {}
        schema = provider.get_provider_schema()
        # Transform icon paths to full URLs with domain
        if schema.icon:
            base_url = funiq_ai_config.SERVER_URL.rstrip("/")

            if schema.icon.get("small"):
                schema.icon["small"] = f"{base_url}/static/providers/{schema.provider}/icon/small"
            if schema.icon.get("large"):
                schema.icon["large"] = f"{base_url}/static/providers/{schema.provider}/icon/large"
        provider_schema = schema.model_dump()
        return ProviderInfo(**provider_schema)
