from abc import ABC
from typing import Dict

from jsonschema import ValidationError, validate

from utils.common.i18n import translate_data


class ValidateHandlingMixin(ABC):
    """Mixin class for handling operator schemas and their configurations."""
    config_schema: dict | None
    output_schema: dict | None

    def validate_output(self, data: Dict) -> bool:
        """Validate output data against output schema"""
        if self.output_schema is None:
            return True
        try:
            schema = translate_data(self.output_schema)
            validate(instance=data, schema=schema)
            return True
        except ValidationError:
            return False

    def validate_config(self, config: Dict) -> bool:
        """Validate configuration data against config schema"""
        if self.config_schema is None:
            return True
            
        try:
            schema = translate_data(self.config_schema)
            validate(instance=config, schema=schema)
            return True
        except ValidationError:
            return False
