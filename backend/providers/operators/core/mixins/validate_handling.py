from abc import ABC, abstractmethod
from typing import Dict

from jsonschema import ValidationError, validate

from utils.json_schema import JSONSchema


class ValidateHandlingMixin(ABC):
    """Mixin class for handling operator schemas and their configurations."""

    def validate_input(self, data: Dict) -> bool:
        """
        Default implementation of validate_input that always returns True.
        Child classes can override this method to implement specific validation logic.
        """
        return True

    @abstractmethod
    def get_output_schema(self) -> JSONSchema | None:
        """Get the output schema for validation"""
        pass

    @abstractmethod
    def get_config_schema(self) -> JSONSchema | None:
        """Get the config schema for validation"""
        pass

    def validate_output(self, data: Dict) -> bool:
        """Validate output data against output schema"""
        schema = self.get_output_schema().model_dump(exclude_none=True)
        if schema is None:
            return True
            
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError:
            return False

    def validate_config(self, config: Dict) -> bool:
        """Validate configuration data against config schema"""
        schema = self.get_config_schema().model_dump(exclude_none=True)
        if schema is None:
            return True
            
        try:
            validate(instance=config, schema=schema)
            return True
        except ValidationError:
            return False
