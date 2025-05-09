from typing import List

from fastapi import status
from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ModelProviderErrorCode
from app.core.models.model_provider import ModelProvider as DBModelProvider
from configs import funiq_ai_config
from providers.models.core import ModelProvider, ProviderFactory
from providers.models.core.errors import CredentialsValidateFailedError
from providers.models.core.schemas import AIModelEntity

from ..schemas import ActiveModelProviderWithModels, ModelInfo, ProviderInfo, SaveProviderRequest


class ProviderService:
    @staticmethod
    async def get_all_providers() -> List[ProviderInfo]:
        """Retrieves all available model providers and their configurations.

        Returns:
            List[ProviderInfo]: A list of provider information including their configurations.

        Raises:
            ModelProviderErrorCode: If there's an error during provider retrieval.
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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_models(provider_name: str) -> List[ModelInfo]:
        """Retrieves all available models for a specific provider.

        Args:
            provider_name: The name of the provider to fetch models from.

        Returns:
            List[ModelInfo]: A list of model information for the specified provider.

        Raises:
            ModelProviderErrorCode: If models cannot be found or if there's an error during retrieval.
        """
        try:
            factory_models = ProviderFactory.get_models(provider_name=provider_name)
            if not factory_models:
                logger.error(f"No models found for provider: {provider_name}")
                raise ModelProviderErrorCode.MODEL_NOT_FOUND.exception(
                    data={"provider": provider_name}, status_code=status.HTTP_404_NOT_FOUND
                )

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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_model(provider_name: str, model_name: str) -> AIModelEntity:
        """Retrieves a specific model by its name and provider.

        Args:
            provider_name: The name of the provider.
            model_name: The name of the model to retrieve.

        Returns:
            AIModelEntity: The requested model's information.

        Raises:
            ModelProviderErrorCode: If the specified model cannot be found.
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
        """Saves or updates a provider configuration for a specific tenant.

        Args:
            session: The database session.
            tenant_id: The ID of the tenant.
            provider_name: The name of the provider.
            payload: The provider configuration data.

        Returns:
            DBModelProvider: The saved or updated provider configuration.

        Raises:
            CredentialsValidateFailedError: If the provider credentials validation fails.
        """
        logger.info(
            "Saving provider configuration",
            extra={"tenant_id": tenant_id, "provider": provider_name},
        )

        # Get provider instance and validate credentials
        try:
            provider_instance = ProviderFactory.get_provider_instance(provider_name)
            provider_instance.validate_provider_credentials(payload.credentials)
        except CredentialsValidateFailedError as e:
            raise ModelProviderErrorCode.CREDENTIALS_VALIDATE_FAILED.exception(
                status_code=status.HTTP_403_FORBIDDEN
            ) from e
        except Exception as e:
            raise ModelProviderErrorCode.CREDENTIALS_VALIDATE_FAILED.exception(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={"error": str(e)},
            ) from e

        try:
            # Check for existing provider configuration
            result = await session.execute(
                select(DBModelProvider).where(
                    DBModelProvider.tenant_id == tenant_id, DBModelProvider.provider == provider_name
                )
            )
            provider = result.scalars().first()

            if provider:
                provider.credentials = payload.credentials
                await provider.save(session)
                return provider

            # Create new provider configuration
            provider_data = {
                "tenant_id": tenant_id,
                "provider": provider_name,
                "credentials": payload.credentials,
            }

            provider = DBModelProvider(**provider_data)
            await provider.save(session)

            await session.commit()
            return provider
        except Exception as e:
            logger.error(f"Error saving provider configuration: {e}")
            raise ModelProviderErrorCode.SAVE_PROVIDER_FAILED.exception(
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from e

    @staticmethod
    async def get_provider(session: AsyncSession, tenant_id: str, provider_name: str) -> DBModelProvider:
        """Retrieves a provider configuration for a specific tenant.

        Args:
            session: The database session.
            tenant_id: The ID of the tenant.
            provider_name: The name of the provider to retrieve.

        Returns:
            DBModelProvider: The provider configuration.

        Raises:
            ModelProviderErrorCode: If the provider configuration cannot be found.
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
        """Retrieves all active providers and their available models for a specific tenant.

        Args:
            session: The database session.
            tenant_id: The ID of the tenant.

        Returns:
            List[ActiveModelProviderWithModels]: A list of active providers with their available models.
        """
        # Fetch active providers from database
        result = await session.execute(
            select(DBModelProvider).where(
                and_(DBModelProvider.tenant_id == tenant_id, DBModelProvider.credentials.isnot(None))
            )
        )
        active_providers = result.scalars().all()
        providers_with_models = []

        for provider in active_providers:
            provider_instance = ProviderFactory.get_provider_instance(provider.provider)
            if not provider_instance:
                continue

            provider_info = ProviderService._handle_provider_schema(provider=provider_instance)
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
        """Processes and transforms the provider schema, including icon URL generation.

        Args:
            provider: The provider instance to process.

        Returns:
            ProviderInfo: The processed provider information with complete icon URLs.
        """
        schema = provider.get_provider_schema()

        # Transform icon paths to full URLs
        if schema.icon:
            base_url = funiq_ai_config.SERVER_URL.rstrip("/")

            if schema.icon.get("small"):
                schema.icon["small"] = f"{base_url}/static/providers/{schema.provider}/icon/small"
            if schema.icon.get("large"):
                schema.icon["large"] = f"{base_url}/static/providers/{schema.provider}/icon/large"

        return ProviderInfo(**schema.model_dump())
