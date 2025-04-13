import importlib
import os
from collections.abc import Mapping
from typing import ClassVar

from loguru import logger

from utils.common.i18n import get_current_locale_code_with_territory
from utils.json_schema import JSONSchema

from ..models import (
    PARAMETER_RULE_TEMPLATE,
    AIModelEntity,
    ConfigurateMethod,
    ParameterPropertyName,
)


class SchemaHandlingMixin:
    """Mixin class for handling model schemas and their configurations."""

    # provider -> model_type -> locale -> schemas
    _provider_model_schemas: ClassVar[
        dict[str, dict[str, dict[str, list[AIModelEntity]]]]
    ] = {}  

    def load_predefined_model_schemas(self) -> list[AIModelEntity]:
        """Load and cache all predefined model schemas from Python configuration files."""
        # Get provider and model type names
        model_type = self.__class__.__module__.split(".")[-1]
        provider_name = self.__class__.__module__.split(".")[-3]

        # Get current locale
        locale_code = get_current_locale_code_with_territory()

        # Initialize provider and model_type dicts if not exists
        if provider_name not in self._provider_model_schemas:
            self._provider_model_schemas[provider_name] = {}
        if model_type not in self._provider_model_schemas[provider_name]:
            self._provider_model_schemas[provider_name][model_type] = {}

        # Return cached schemas if exists
        if locale_code in self._provider_model_schemas[provider_name][model_type]:
            return self._provider_model_schemas[provider_name][model_type][locale_code]

        model_schemas = []

        # Construct module path similar to model_provider.py's approach
        model_type_name = model_type.replace("-", "_")
        parent_module = f"providers.models.{provider_name}.{model_type_name}"
        schema_base_path = f"{parent_module}.schemas"

        # Process each schema file
        try:
            # Import the schemas package to get its path
            schemas_module = importlib.import_module(schema_base_path)
            schema_dir = os.path.dirname(schemas_module.__file__)

            # Get all valid schema files
            schema_files = [
                f
                for f in os.listdir(schema_dir)
                if (
                    os.path.isfile(os.path.join(schema_dir, f))
                    and not f.startswith("__")
                    and not f.startswith("_")
                    and f.endswith(".py")
                )
            ]

            for schema_file in schema_files:
                schema_module_name = schema_file.rstrip(".py")
                schema_module_path = f"{schema_base_path}.{schema_module_name}"
                logger.info(f"Loading model schema from {schema_module_path}")

                try:
                    schema_module = importlib.import_module(schema_module_path)
                    if not hasattr(schema_module, "schema"):
                        raise Exception(f"No schema found in {schema_module_path}")
                    schema_data = schema_module.schema
                    ui_schema_data = schema_module.ui_schema if hasattr(schema_module, "ui_schema") else None
                    new_schema_data = schema_data.copy()

                    # Process parameter rules schema
                    parameter_rules_schema = new_schema_data.pop("parameter_rules_schema", {})
                    processed_rules_schema = self._process_parameter_rules(parameter_rules_schema)

                    if ui_schema_data:
                        new_schema_data["parameter_rules_ui_schema"] = ui_schema_data.get("parameter_rules")
                    new_schema_data["parameter_rules_schema"] = processed_rules_schema
                    new_schema_data["configurate_method"] = ConfigurateMethod.PREDEFINED.value

                    model_schema = AIModelEntity(**new_schema_data)
                    model_schemas.append(model_schema)

                except Exception as e:
                    raise Exception(f"Invalid model schema for {schema_module_path}: {e!s}") from e

        except ImportError as e:
            logger.warning(f"No schemas found for {schema_base_path}: {e}")
            return []

        # Cache schemas for this locale and model type
        self._provider_model_schemas[provider_name][model_type][locale_code] = model_schemas
        return model_schemas

    def get_model_schema(self, model: str, credentials: Mapping | None = None) -> AIModelEntity | None:
        """Get model schema by model name."""
        # Check predefined schemas first
        models = self.load_predefined_model_schemas()

        model_map = {model.model: model for model in models}
        if model in model_map:
            return model_map[model]

        # Try to create custom schema from credentials
        if credentials:
            return self.create_custom_model_schema(model, credentials)

        return None

    def create_custom_model_schema(self, model: str, credentials: Mapping) -> AIModelEntity | None:
        """Create a custom model schema from credentials."""
        return self._create_custom_model_schema(model, credentials)

    def _process_parameter_rules(self, parameter_rules: dict) -> JSONSchema:
        """Process parameter rules and return a JSONSchema."""
        parameter_rules_schema = JSONSchema(properties={})
        required_fields = []

        for param_name, rule in parameter_rules.items():
            try:
                processed_rule = rule.copy()

                # Handle template-based rules
                if "_template" in rule:
                    template_name = ParameterPropertyName(rule["_template"])
                    template_rule = PARAMETER_RULE_TEMPLATE[template_name]
                    processed_rule = template_rule

                    # Update template with custom configurations
                    custom_fields = {k: v for k, v in rule.items() if k not in ("_template", "required")}
                    for key, value in custom_fields.items():
                        setattr(processed_rule, key, value)
                else:
                    # Remove required field from the rule
                    processed_rule.pop("required", None)

                # Add to schema using the parameter name as the property key
                parameter_rules_schema.properties[param_name] = processed_rule

                # Check if the field is required
                if rule.get("required", False):
                    required_fields.append(param_name)

            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to process parameter rule for {param_name}: {e}")
                continue

        # Set required fields in schema
        if required_fields:
            parameter_rules_schema.required = required_fields

        return parameter_rules_schema.model_dump()

    def _create_custom_model_schema(self, model: str, credentials: Mapping) -> AIModelEntity | None:
        """Internal method to create and customize a model schema using templates."""
        schema = self.get_customizable_model_schema(model, credentials)
        if not schema:
            return None

        # Process parameter rules
        processed_rules_schema = self._process_parameter_rules(schema.parameter_rules_schema)
        schema.parameter_rules_schema = processed_rules_schema

        return schema

    def get_customizable_model_schema(self, model: str, credentials: Mapping) -> AIModelEntity | None:
        """Get customizable model schema. To be implemented by subclasses if needed."""
        return None

    def _get_default_parameter_rule_variable_map(self, name: ParameterPropertyName) -> dict:
        """Get default parameter rule for given name."""
        default_parameter_rule = PARAMETER_RULE_TEMPLATE.get(name)

        if not default_parameter_rule:
            raise Exception(f"Invalid model parameter rule name {name}")

        return default_parameter_rule

    def get_parameter_rules_schema(self, model: str, credentials: dict) -> JSONSchema:
        """Get parameter rules schema for the model.

        :param model: model name
        :param credentials: model credentials
        :return: JSONSchema instance
        """
        model_schema = self.get_model_schema(model, credentials)
        if not model_schema:
            return JSONSchema(properties={})

        return model_schema.parameter_rules_schema

    def get_model_ui_schema(self, model: str) -> dict | None:
        """Get UI schema for the specified model in current locale.

        :param model: model name
        :return: UI schema dict or None if not found
        """
        model_schema = self.get_model_schema(model)
        if not model_schema:
            return None

        return model_schema.ui_schema
