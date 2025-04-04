import importlib
import os
from typing import ClassVar

from loguru import logger

from utils.common.i18n import get_current_locale_code_with_territory

from ..models.operator import OperatorEntity


class SchemaHandlingMixin:
    """Mixin class for handling operator schemas and their configurations."""

    # operator_type -> locale -> schemas
    _operator_schemas: ClassVar[dict[str, dict[str, OperatorEntity]]] = {}

    def load_operator_schema(self) -> OperatorEntity:
        """Load and cache operator schema from Python configuration file."""
        # Get operator type from class module path
        operator_type = self.__class__.__module__.split(".")[-2]
        locale_code = get_current_locale_code_with_territory()

        # Return cached schema if exists
        if operator_type in self._operator_schemas and locale_code in self._operator_schemas[operator_type]:
            return self._operator_schemas[operator_type][locale_code]

        # Construct module path
        schema_path = f"providers.operators.{operator_type}.schema"

        try:
            # Import the schema module
            schema_module = importlib.import_module(schema_path)
            
            if not hasattr(schema_module, "schema"):
                raise Exception(f"No schema found in {schema_path}")

            schema_data = schema_module.schema
            config_ui_schema_data = getattr(schema_module, "config_ui_schema", None)
    
            # Create operator schema
            operator_schema = OperatorEntity(
                **schema_data,
                config_ui_schema=config_ui_schema_data
            )

            # Cache schema
            if operator_type not in self._operator_schemas:
                self._operator_schemas[operator_type] = {}
            self._operator_schemas[operator_type][locale_code] = operator_schema

            return operator_schema

        except ImportError as e:
            logger.error(f"Failed to load schema for operator type {operator_type}: {e}")
            raise

    def get_operator_schema(self) -> OperatorEntity:
        """Get the operator schema."""
        return self.load_operator_schema()

    @classmethod
    def get_available_operator_types(cls) -> list[str]:
        """Get all available operator types by scanning the operators directory."""
        # Get the operators directory path
        current_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Get all operator directories (excluding __pycache__ etc)
        operator_types = [
            d for d in os.listdir(current_path)
            if os.path.isdir(os.path.join(current_path, d))
            and not d.startswith("__")
            and not d.startswith("_")
            and d != "core"
        ]
        
        return operator_types 