from abc import ABC
from typing import Dict

from jsonschema import ValidationError, validate

from utils.json_schema import JSONSchema


class ValidateHandlingMixin(ABC):
    """Mixin class for handling operator schemas and their configurations."""
    config_schema: JSONSchema | None
    output_schema: JSONSchema | None

    def validate_output(self, data: Dict) -> bool:
        """Validate output data against output schema"""
        schema = self.output_schema.model_dump(exclude_none=True)
        if schema is None:
            return True
            
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError:
            return False

    def validate_config(self, config: Dict) -> bool:
        """Validate configuration data against config schema"""
        schema = self.config_schema.model_dump(exclude_none=True)
        if schema is None:
            return True
            
        try:
            validate(instance=config, schema=schema)
            return True
        except ValidationError:
            return False
