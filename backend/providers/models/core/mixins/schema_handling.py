import importlib
import os
from typing import ClassVar

from loguru import logger

from utils.common.i18n import get_current_locale_code_with_territory, translate_data

from ..schemas import (
    PARAMETER_RULE_TEMPLATES,
    AIModelEntity,
    ParameterPropertyName,
)


class SchemaHandlingMixin:
    """Mixin class for handling model schemas and their configurations."""

    # provider -> model_type -> locale -> schemas
    _provider_model_schemas: ClassVar[dict[str, dict[str, dict[str, list[AIModelEntity]]]]] = {}

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

                try:
                    schema_module = importlib.import_module(schema_module_path)
                    if not hasattr(schema_module, "schema"):
                        raise Exception(f"No schema found in {schema_module_path}")
                    schema_data = schema_module.schema
                    new_schema_data = schema_data.copy()

                    # Process parameter rules schema
                    parameter_rules_schema = new_schema_data.pop("parameter_rules_schema", {})
                    parameter_rules_json_schema = self._handle_parameter_rules_json_schema(parameter_rules_schema)
                    new_schema_data["parameter_rules_schema"] = {
                        **parameter_rules_schema,
                        "json_schema": parameter_rules_json_schema,
                    }

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

    def get_model_schema(self, model: str) -> AIModelEntity | None:
        """Get model schema by model name."""
        # Check predefined schemas first
        models = self.load_predefined_model_schemas()

        model_map = {model.model: model for model in models}
        if model in model_map:
            return model_map[model]

        return None

    def _handle_parameter_rules_json_schema(self, parameter_rules: dict) -> dict:
        """Process parameter rules and return a json schema."""
        parameter_rules_json_schema = parameter_rules.get("json_schema", {})
        properties = parameter_rules_json_schema.get("properties", {})

        def _handle_template_rule(rule: dict) -> dict:
            """Helper function to process template-based rules."""
            template_name = ParameterPropertyName(rule["_template"])
            template_rule = PARAMETER_RULE_TEMPLATES[template_name].copy()

            # Update template with custom configurations
            custom_fields = {k: v for k, v in rule.items() if k != "_template"}
            template_rule.update(custom_fields)
            return template_rule

        for param_name, rule in properties.items():
            try:
                processed_rule = _handle_template_rule(rule) if "_template" in rule else rule.copy()
                properties[param_name] = processed_rule

            except Exception as e:
                raise ValueError(f"Failed to process parameter rule for {param_name}: {e}") from e

        return translate_data(
            {
                **parameter_rules_json_schema,
                "properties": properties,
            }
        )

    def _get_default_parameter_rule_variable_map(self, name: ParameterPropertyName) -> dict:
        """Get default parameter rule for given name."""
        default_parameter_rule = PARAMETER_RULE_TEMPLATES[name]

        if not default_parameter_rule:
            raise Exception(f"Invalid model parameter rule name {name}")

        return default_parameter_rule

    def get_parameter_rules_schema(self, model: str) -> dict:
        """Get parameter rules schema for the model.

        :param model: model name
        :param credentials: model credentials
        :return: json schema
        """
        model_schema = self.get_model_schema(model)
        if not model_schema:
            return {
                "type": "object",
                "properties": {},
            }

        return model_schema.parameter_rules_schema
