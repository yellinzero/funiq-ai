from typing import List

from fastapi import status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.app.service.app_service import AppService
from app.core.errors import ModelProviderErrorCode
from app.core.models.app import App
from app.core.models.model_provider import Model, ModelProvider
from configs import funiq_ai_config
from providers.models.core.models.model import ConfigurateMethod
from providers.models.core.provider_factory import ProviderFactory

from ..schemas import ModelInfo, ProviderInfo, SaveModelRequest, SaveProviderRequest


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
            schema = provider.get_provider_schema()
            ui_schema = provider.get_provider_ui_schema()
            logger.debug(f"Processing provider schema for {schema.provider}")
            # Transform icon paths to full URLs with domain
            if schema.icon:
                base_url = funiq_ai_config.SERVER_URL.rstrip("/")

                if schema.icon.get("small"):
                    schema.icon["small"] = f"{base_url}/static/providers/{schema.provider}/icon/small"
                if schema.icon.get("large"):
                    schema.icon["large"] = f"{base_url}/static/providers/{schema.provider}/icon/large"

            provider_schemas.append({**schema.model_dump(), "ui_schema": ui_schema})

        logger.info(f"Successfully fetched {len(provider_schemas)} providers")
        return provider_schemas

    @staticmethod
    def _merge_system_provider_data(provider: ModelProvider, provider_name: str) -> None:
        """
        Merge system provider data from factory with database provider

        Args:
            provider: Provider instance from database
            provider_name: Name of the provider
        """
        if not provider.is_system:
            return

        provider_instance = ProviderFactory.get_provider_instance(provider_name=provider_name)
        if not provider_instance:
            return

        schema = provider_instance.get_provider_schema()
        fields_to_merge = ["label", "description", "credential_schema", "supported_model_types", "docs", "icon"]

        for field in fields_to_merge:
            if not getattr(provider, field):
                setattr(provider, field, getattr(schema, field))

    @staticmethod
    def _merge_system_model_data(db_model: Model, factory_model_info: dict) -> dict:
        """
        Merge system model data from factory with database model

        Args:
            db_model: Model instance from database
            factory_model_info: Model info from factory

        Returns:
            dict: Merged model data
        """
        fields_to_merge = [
            "label",
            "features",
            "model_properties",
            "pricing",
            "parameter_rules_schema",
            "parameter_rules_ui_schema",
        ]

        merged_data = {
            "id": str(db_model.id),
            "is_enabled": db_model.is_enabled,
            "is_system": db_model.is_system,
            "deprecated": db_model.deprecated
            if db_model.deprecated is not None
            else factory_model_info.get("deprecated"),
        }

        # Merge other fields
        for field in fields_to_merge:
            db_value = getattr(db_model, field)
            logger.debug(
                f"Merging field: {field}, db_value: {db_value}, factory_value: {factory_model_info.get(field)}"
            )
            merged_data[field] = db_value or factory_model_info.get(field)

        return merged_data

    @staticmethod
    async def get_models(session: AsyncSession, tenant_id: str, provider_name: str) -> List[ModelInfo]:
        """
        Get all models for a specific provider.

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

        # Get models from database
        result = await session.execute(
            select(Model).where(Model.tenant_id == tenant_id, Model.provider == provider_name)
        )
        db_models = result.scalars().all()
        db_models_map = {model.model: model for model in db_models}

        # Merge factory and db models
        merged_models = []
        for factory_model in factory_models:
            model_info = factory_model.model_dump()
            model_info.update(
                {
                    "tenant_id": tenant_id,
                    "provider": provider_name,
                    "is_enabled": False,
                    "is_system": True,
                }
            )

            if factory_model.model in db_models_map:
                db_model = db_models_map[factory_model.model]
                model_info.update(ProviderService._merge_system_model_data(db_model, model_info))

            merged_models.append(ModelInfo(**model_info))

        logger.info(f"Successfully fetched and merged {len(merged_models)} models")
        return merged_models

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
            extra={"tenant_id": tenant_id, "provider": provider_name, "is_system": payload.is_system},
        )

        # Check if provider exists
        result = await session.execute(
            select(ModelProvider).where(ModelProvider.tenant_id == tenant_id, ModelProvider.provider == provider_name)
        )
        provider = result.scalars().first()

        if provider:
            logger.info("Updating existing provider configuration", extra={"provider_id": str(provider.id)})
            provider.credentials = payload.credentials
            provider.is_system = payload.is_system
            await provider.save(session)
            return provider

        # Create new provider
        provider_data = {
            "tenant_id": tenant_id,
            "provider": provider_name,
            "credentials": payload.credentials,
            "is_system": payload.is_system,
        }

        provider = ModelProvider(**provider_data)
        await provider.save(session)

        logger.info("Created new provider configuration", extra={"provider_id": str(provider.id)})
        return provider

    @staticmethod
    async def save_model(
        session: AsyncSession, tenant_id: str, provider_name: str, model_name: str, payload: SaveModelRequest
    ) -> Model:
        """
        Save a model configuration

        Args:
            session: Database session
            tenant_id: ID of the tenant
            payload: Model configuration

        Returns:
            Model: The saved model configuration
        """
        logger.info(
            "Saving model configuration", extra={"tenant_id": tenant_id, "provider": provider_name, "model": model_name}
        )

        # Check if model exists
        result = await session.execute(
            select(Model).where(
                Model.tenant_id == tenant_id, Model.provider == provider_name, Model.model == model_name
            )
        )
        model = result.scalars().first()

        if model:
            # Update existing model
            model.is_enabled = payload.is_enabled or False
            await model.save(session)
            return model

        model_schema = ProviderFactory.get_model(model_name=model_name, provider_name=provider_name)
        if not model_schema:
            raise ModelProviderErrorCode.MODEL_NOT_FOUND.exception(
                data={"provider": provider_name, "model": model_name}, status_code=status.HTTP_404_NOT_FOUND
            )

        # Create new model
        model_data = {
            "tenant_id": tenant_id,
            "provider": provider_name,
            "model": model_name,
            "model_type": model_schema.model_type.value,
            "label": model_name,
            "is_system": payload.is_system or False,
            "is_enabled": payload.is_enabled or False,
            "configurate_method": ConfigurateMethod.PREDEFINED.value
            if payload.is_system
            else ConfigurateMethod.CUSTOMIZABLE.value,
        }

        model = Model(**model_data)
        await model.save(session)

        logger.info("Created new model configuration", extra={"model_id": str(model.id)})
        return model

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

        ProviderService._merge_system_provider_data(provider, provider_name)
        return provider

    @staticmethod
    async def get_model(session: AsyncSession, tenant_id: str, provider_name: str, model_name: str) -> Model:
        """
        Get a model by name

        Args:
            session: Database session
            tenant_id: ID of the tenant
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            Model: The model configuration
        """
        logger.info(
            "Fetching model configuration",
            extra={"tenant_id": tenant_id, "provider": provider_name, "model": model_name},
        )

        result = await session.execute(
            select(Model).where(
                Model.tenant_id == tenant_id, Model.provider == provider_name, Model.model == model_name
            )
        )
        model = result.scalars().first()

        if not model:
            raise ModelProviderErrorCode.MODEL_NOT_FOUND.exception(
                data={"provider": provider_name, "model": model_name}, status_code=status.HTTP_404_NOT_FOUND
            )

        return model

    @staticmethod
    async def enable_model(
        session: AsyncSession,
        tenant_id: str,
        provider_name: str,
        model_name: str,
    ) -> Model:
        """
        Enable a model and create its associated system app if it doesn't exist

        Args:
            session: Database session
            tenant_id: ID of the tenant
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            Model: The enabled model
        """
        logger.info("Enabling model", extra={"tenant_id": tenant_id, "provider": provider_name, "model": model_name})

        async with session.begin():
            result = await session.execute(
                select(Model).where(
                    Model.tenant_id == tenant_id,
                    Model.provider == provider_name,
                    Model.model == model_name
                )
            )
            model = result.scalars().first()

            if not model:
                # Create the model if it doesn't exist
                model = await ProviderService.save_model(
                    session=session,
                    tenant_id=tenant_id,
                    provider_name=provider_name,
                    model_name=model_name,
                    payload=SaveModelRequest(is_system=True, is_enabled=True),
                )
            else:
                # Enable the existing model
                model.is_enabled = True
                await model.save(session)

            # Check if system app exists for this model
            result = await session.execute(
                select(App).where(App.tenant_id == tenant_id, App.name == model_name, App.is_system == True)
            )
            app = result.scalars().first()

            if not app:
                await AppService.create_system_app(
                    session=session,
                    tenant_id=tenant_id,
                    model_name=model_name,
                    model_id=str(model.id),
                )

            await session.commit()
            logger.info("Successfully enabled model", extra={"model_id": str(model.id)})
            return model
