import importlib
from abc import ABC, abstractmethod
from typing import ClassVar

from providers.models.core import AIModel
from providers.models.core.models import AIModelEntity, ModelType, ProviderEntity
from utils.common.i18n import get_current_locale_code_with_territory
from utils.json_schema import UiSchema


class ModelProvider(ABC):
    _provider_schemas: ClassVar[dict[str, dict[str, ProviderEntity]]] = {}  # provider -> locale -> schema
    _provider_ui_schemas: ClassVar[dict[str, dict[str, dict]]] = {}  # provider -> locale -> ui_schema
    model_instance_map: ClassVar[dict[str, AIModel]] = {}

    @abstractmethod
    def validate_provider_credentials(self, credentials: dict) -> None:
        """
        Validate provider credentials
        You can choose any validate_credentials method of model type or implement validate method by yourself,
        such as: get model list api

        if validate failed, raise exception

        :param credentials: provider credentials, credentials form defined in `provider_credential_schema`.
        """
        raise NotImplementedError

    def get_provider_schema(self) -> ProviderEntity:
        """
        Get provider schema

        :return: provider schema
        """
        # Get provider name
        provider_name = self.__class__.__module__.split(".")[-1]

        # Get current locale
        locale_code = get_current_locale_code_with_territory()

        # Initialize provider dict if not exists
        if provider_name not in self._provider_schemas:
            self._provider_schemas[provider_name] = {}
            self._provider_ui_schemas[provider_name] = {}

        # Return cached schema if exists
        if locale_code in self._provider_schemas[provider_name]:
            return self._provider_schemas[provider_name][locale_code]

        # Load schema from module
        try:
            parent_module = ".".join(self.__class__.__module__.split(".")[:-1])
            module_path = f"{parent_module}.{provider_name}_schema"
            schema_module = importlib.import_module(module_path)
            if not hasattr(schema_module, "schema"):
                raise AttributeError(f"No provider_schema found in {module_path}")

            provider_schema = ProviderEntity(**schema_module.schema)

            # Load and cache UI schema if available
            if hasattr(schema_module, "ui_schema"):
                self._provider_ui_schemas[provider_name][locale_code] = UiSchema(**schema_module.ui_schema).model_dump(
                    by_alias=True,
                    exclude_none=True
                )

        except Exception as e:
            raise Exception(f"Invalid provider schema for {provider_name}: {e!s}") from e

        # Cache schema
        self._provider_schemas[provider_name][locale_code] = provider_schema
        return provider_schema

    def get_provider_ui_schema(self) -> dict | None:
        """
        Get provider UI schema for current locale

        :return: provider UI schema
        """
        provider_name = self.__class__.__module__.split(".")[-1]
        locale_code = get_current_locale_code_with_territory()

        return self._provider_ui_schemas.get(provider_name, {}).get(locale_code, None)

    def models(self, model_type: ModelType) -> list[AIModelEntity]:
        """
        Get all models for given model type

        :param model_type: model type defined in `ModelType`
        :return: list of models
        """
        provider_schema = self.get_provider_schema()
        if model_type not in provider_schema.supported_model_types:
            return []

        # get model instance of the model type
        model_instance = self.get_model_instance(model_type)

        models = model_instance.load_predefined_model_schemas()

        # return models
        return models

    def get_model_instance(self, model_type: ModelType) -> AIModel:
        """
        Get model instance

        :param model_type: model type defined in `ModelType`
        :return: AIModel instance
        """
        # get provider name
        provider_name = self.__class__.__module__.split(".")[-1]

        # check cache first
        cache_key = f"{provider_name}.{model_type.value}"
        if cache_key in self.model_instance_map:
            return self.model_instance_map[cache_key]

        try:
            # construct module path
            model_type_name = model_type.value.replace("-", "_")
            parent_module = ".".join(self.__class__.__module__.split(".")[:-1])
            module_path = f"{parent_module}.{model_type_name}.{model_type_name}"
            # import module
            module = importlib.import_module(module_path)

            # find the concrete AIModel implementation
            model_class = next(
                (
                    cls
                    for cls in module.__dict__.values()
                    if isinstance(cls, type)
                    and issubclass(cls, AIModel)
                    and cls.__module__ == module.__name__
                    and not cls.__abstractmethods__
                ),
                None,
            )

            if not model_class:
                raise ValueError(f"No concrete AIModel implementation found in {module_path}")

            # create instance and cache it
            model_instance = model_class()
            self.model_instance_map[cache_key] = model_instance

            return model_instance

        except (ImportError, AttributeError) as e:
            raise Exception(f"Failed to load model type {model_type} for provider {provider_name}: {e!s}") from e
