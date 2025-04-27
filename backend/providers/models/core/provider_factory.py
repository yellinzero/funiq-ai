import importlib
import os
from typing import ClassVar, Sequence

from loguru import logger

from providers.models.core import ModelProvider
from providers.models.core.schemas import AIModelEntity, ModelType


class ProviderFactory:
    _provider_class_map: ClassVar[dict[str, type[ModelProvider]]] = {}

    @classmethod
    def get_provider_instance(cls, provider_name: str) -> ModelProvider:
        """
        Get provider instance by provider name.
        Creates a new instance each time to avoid concurrency issues.

        :param provider_name: provider name (e.g. 'anthropic', 'deepseek')
        :return: ModelProvider instance
        """
        if provider_name in cls._provider_class_map:
            return cls._provider_class_map[provider_name]()

        try:
            # construct module path
            module_path = f"providers.models.{provider_name}.{provider_name}"
            # import module
            module = importlib.import_module(module_path)

            # find provider class
            provider_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) 
                    and issubclass(attr, ModelProvider) 
                    and getattr(attr, "provider_name", None) == provider_name):
                    provider_class = attr
                    break
            else:
                # if not found, use old naming convention
                class_name = f"{provider_name.capitalize()}Provider"
                provider_class = getattr(module, class_name)

            # cache class definition (not instance)
            cls._provider_class_map[provider_name] = provider_class
            # return new instance
            return provider_class()
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not load provider implementation for {provider_name}: {e!s}") from e

    @classmethod
    def get_all_providers(cls) -> Sequence[ModelProvider]:
        """
        Get all available providers by scanning the providers directory

        :return: List of ModelProvider instances
        """
        # Get the path of current file
        current_path = os.path.abspath(__file__)
        providers_path = os.path.dirname(os.path.dirname(current_path))

        # Get all provider directories (excluding __pycache__ etc)
        provider_dirs = [
            d
            for d in os.listdir(providers_path)
            if os.path.isdir(os.path.join(providers_path, d))
            and not d.startswith("__")
            and not d.startswith("_")
            and d != "core"
        ]

        providers = []
        for provider_name in provider_dirs:
            try:
                provider = cls.get_provider_instance(provider_name)
                providers.append(provider)
            except ValueError:
                logger.warning(f"Could not load provider implementation for {provider_name}")
                continue

        return providers

    @classmethod
    def get_models(
        cls,
        *,
        provider_name: str | None = None,
        model_type: ModelType | None = None,
    ) -> list[AIModelEntity]:
        """
        List all available models, optionally filtered by provider and/or model type.

        :param provider_name: Optional provider name to filter models
        :param model_type: Optional model type to filter models
        :return: List of AIModelEntity instances
        """
        # Get all providers or specific provider
        if provider_name:
            try:
                providers = [cls.get_provider_instance(provider_name)]
            except ValueError:
                return []
        else:
            providers = cls.get_all_providers()

        # Collect models from all providers
        all_models = []
        for provider in providers:
            # If model_type is specified, only get models for that type
            if model_type:
                models = provider.models(model_type=model_type)
                all_models.extend(models)
            else:
                # Get provider schema to find supported model types
                provider_schema = provider.get_provider_schema()
                # Get models for each supported model type
                for model_type in provider_schema.model_types:
                    models = provider.models(model_type=model_type)
                    all_models.extend(models)

        return all_models

    @classmethod
    def get_model(cls, model_name: str, provider_name: str) -> AIModelEntity:
        """
        Get a model by model name and provider name

        :param model_name: The name of the model to retrieve (e.g. 'gpt-4', 'claude-3-opus-20240229')
        :param provider_name: The name of the provider (e.g. 'openai', 'anthropic')
        :return: AIModelEntity instance for the specified model
        :raises ValueError: If the model is not found or provider cannot be loaded
        """
        # Get the specific provider instance
        provider = cls.get_provider_instance(provider_name)

        # Get provider schema to find supported model types
        provider_schema = provider.get_provider_schema()

        # Check each supported model type
        for model_type in provider_schema.model_types:
            # Get models of this type from the provider
            model_instance = provider.get_model_instance(model_type=model_type)

            model_schema = model_instance.get_model_schema(model=model_name)
            if model_schema:
                return model_schema

        raise ValueError(f"Model '{model_name}' not found in provider '{provider_name}'")
