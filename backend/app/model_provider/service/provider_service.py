from typing import List

from fastapi import status
from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ModelProviderErrorCode
from app.core.models.model_provider import CustomizedModel, ModelProvider
from configs import funiq_ai_config
from providers.models.core import ModelProvider as CoreModelProvider
from providers.models.core import ProviderFactory

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
        logger.info("Fetching all providers")
        providers = ProviderFactory.get_all_providers()
        provider_schemas = []

        for provider in providers:
            provider_info = ProviderService._handle_provider_schema(provider)
            provider_schemas.append(provider_info)

        logger.info(f"Successfully fetched {len(provider_schemas)} providers")
        return provider_schemas

    @staticmethod
    async def get_models(session: AsyncSession, tenant_id: str, provider_name: str) -> List[ModelInfo]:
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
        logger.info(f"Fetching models for provider: {provider_name}", extra={"tenant_id": tenant_id})

        # Get models from provider factory
        factory_models = ProviderFactory.get_models(provider_name=provider_name)
        if not factory_models:
            logger.warning(f"No models found for provider: {provider_name}")
            raise ModelProviderErrorCode.MODEL_NOT_FOUND.exception(
                data={"provider": provider_name}, status_code=status.HTTP_404_NOT_FOUND
            )

        # Get customized models from database
        result = await session.execute(
            select(CustomizedModel).where(
                CustomizedModel.tenant_id == tenant_id, CustomizedModel.provider == provider_name
            )
        )
        custom_models = result.scalars().all()

        # Convert factory models to ModelInfo
        model_info_list = [ModelInfo(
            **model.model_dump(),
            tenant_id=tenant_id,
            provider=provider_name,
        ) for model in factory_models]

        # Add customized models
        for custom_model in custom_models:
            model_info = ModelInfo(
                tenant_id=custom_model.tenant_id,
                provider=custom_model.provider,
                model=custom_model.model,
                model_type=custom_model.model_type,
                label=custom_model.label,
                features=custom_model.features,
                group=custom_model.group,
                model_properties=custom_model.model_properties,
                pricing=custom_model.pricing,
                parameter_rules_ui_schema=custom_model.parameter_rules_ui_schema,
                parameter_rules_schema=custom_model.parameter_rules_schema,
                deprecated=custom_model.deprecated,
            )
            model_info_list.append(model_info)

        logger.info(f"Successfully fetched {len(model_info_list)} models")
        return model_info_list

    @staticmethod
    async def get_model(session: AsyncSession, tenant_id: str, provider_name: str, model_name: str) -> ModelInfo:
        """
        Get a model by name

        Args:
            session: Database session
            tenant_id: ID of the tenant
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            ModelInfo: The model information
        """
        logger.info(f"Fetching model: {model_name} for provider: {provider_name}", extra={"tenant_id": tenant_id})

        model = ProviderFactory.get_model(model_name=model_name, provider_name=provider_name)

        if not model:
            # Get model from database
            result = await session.execute(
                select(CustomizedModel).where(
                    CustomizedModel.tenant_id == tenant_id,
                    CustomizedModel.provider == provider_name,
                    CustomizedModel.model == model_name,
                )
            )
            model = result.scalar_one_or_none()

        if not model:
            raise ModelProviderErrorCode.MODEL_NOT_FOUND.exception(
                data={"provider": provider_name, "model": model_name}, status_code=status.HTTP_404_NOT_FOUND
            )

        return model

    @staticmethod
    async def save_provider(
        session: AsyncSession, tenant_id: str, provider_name: str, payload: SaveProviderRequest
    ) -> ModelProvider:
        """
        Save a provider configuration

        Args:
            session: Database session
            tenant_id: ID of the tenant
            payload: Provider configuration

        Returns:
            ModelProvider: The saved provider configuration
        """
        logger.info(
            "Saving provider configuration",
            extra={"tenant_id": tenant_id, "provider": provider_name},
        )

        # Check if provider exists
        result = await session.execute(
            select(ModelProvider).where(ModelProvider.tenant_id == tenant_id, ModelProvider.provider == provider_name)
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

        provider = ModelProvider(**provider_data)
        await provider.save(session)

        await session.commit()
        logger.info("Created new provider configuration", extra={"provider": provider.provider})
        return provider

    @staticmethod
    async def get_provider(session: AsyncSession, tenant_id: str, provider_name: str) -> ModelProvider:
        """
        Get a provider by name

        Args:
            session: Database session
            tenant_id: ID of the tenant
            provider_name: Name of the provider

        Returns:
            ModelProvider: The provider configuration
        """
        logger.info("Fetching provider configuration", extra={"tenant_id": tenant_id, "provider": provider_name})

        result = await session.execute(
            select(ModelProvider).where(ModelProvider.tenant_id == tenant_id, ModelProvider.provider == provider_name)
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
        logger.info("Fetching active providers", extra={"tenant_id": tenant_id})

        # Get active providers from database
        result = await session.execute(
            select(ModelProvider).where(
                and_(ModelProvider.tenant_id == tenant_id, ModelProvider.credentials.isnot(None))
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
            models = await ProviderService.get_models(
                session=session, tenant_id=tenant_id, provider_name=provider.provider
            )

            providers_with_models.append(
                {
                    "provider": provider_info,
                    "models": [model.model_dump() for model in models],
                }
            )

        logger.info(f"Successfully fetched {len(providers_with_models)} active providers")
        return providers_with_models

    @staticmethod
    def _handle_provider_schema(provider: CoreModelProvider) -> ProviderInfo:
        """
        Handle provider schema
        """
        provider_schema = {}
        schema = provider.get_provider_schema()
        ui_schema = provider.get_provider_ui_schema()
        # Transform icon paths to full URLs with domain
        if schema.icon:
            base_url = funiq_ai_config.SERVER_URL.rstrip("/")

            if schema.icon.get("small"):
                schema.icon["small"] = f"{base_url}/static/providers/{schema.provider}/icon/small"
            if schema.icon.get("large"):
                schema.icon["large"] = f"{base_url}/static/providers/{schema.provider}/icon/large"
        provider_schema = {
            **schema.model_dump(),
            "ui_schema": ui_schema,
        }
        return provider_schema
