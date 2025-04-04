from abc import ABC, abstractmethod
from typing import Dict

from utils.json_schema import JSONSchema

from .mixins.convert_handling import ConvertHandlingMixin
from .mixins.schema_handling import SchemaHandlingMixin
from .mixins.validate_handling import ValidateHandlingMixin


class BaseOperator(SchemaHandlingMixin, ValidateHandlingMixin, ConvertHandlingMixin, ABC):
    """
    Base class for all operators in the system.
    
    This class provides common functionality for operator implementations, including:
    - Operator schema management and validation
    - Input/Output schema validation
    - Configuration management
    - Error handling and transformation
    """
    
    def __init__(self):
        self._config: Dict | None = None
        self._output: Dict | None = None
        self._input: Dict | None = None
        self._config_schema: JSONSchema | None = None
        self._output_schema: JSONSchema | None = None

    @property
    def config(self) -> Dict | None:
        return self._config

    @config.setter
    def config(self, value: Dict) -> None:
        if self.validate_config(value):
            self._config = value

    @property
    def output(self) -> Dict | None:
        return self._output

    @output.setter
    def output(self, value: Dict) -> None:
        if self.validate_output(value):
            self._output = value

    @property
    def input(self) -> Dict | None:
        return self._input

    @input.setter
    def input(self, value: Dict) -> None:
        if self.validate_input(value):
            self._input = value

    @property
    def config_schema(self) -> JSONSchema | None:
        if self._config_schema is None:
            operator_schema = self.get_operator_schema()
            self._config_schema = operator_schema.config_schema
        return self._config_schema

    @property
    def output_schema(self) -> JSONSchema | None:
        if self._output_schema is None:
            operator_schema = self.get_operator_schema()
            self._output_schema = operator_schema.output_schema
        return self._output_schema

    def get_output_schema(self) -> JSONSchema | None:
        return self.output_schema

    def get_config_schema(self) -> JSONSchema | None:
        return self.config_schema
    
    def get_data(self) -> Dict:
        operator_schema = self.get_operator_schema()
        return {
            "name": operator_schema.name,
            "config": self.config,
            "output": self.output,
            "config_schema": self.config_schema,
            "output_schema": self.output_schema
        }

    @abstractmethod
    async def execute(self, input_data: dict, config: dict) -> dict:
        """
        Execute the operator's main functionality
        
        Args:
            input_data: Input data for the operator
            config: Operator configuration
            
        Returns:
            Dict containing the execution results
        """
        raise NotImplementedError 