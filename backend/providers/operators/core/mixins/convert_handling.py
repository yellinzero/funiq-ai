

import json
from abc import ABC, abstractmethod
from typing import Dict

import yaml

from ..models.operator import OperatorEntity


class ConvertHandlingMixin(ABC):
    """Mixin class for handling operator schemas and their configurations."""
    
    @abstractmethod
    def get_data(self) -> Dict:
        pass
    
    @abstractmethod
    def get_operator_schema(self) -> OperatorEntity:
        pass

    def to_json(self) -> str:
        """Convert data to JSON string"""
        return json.dumps(self.get_data())

    def to_yaml(self) -> str:
        """Convert data to YAML string"""
        return yaml.dump(self.get_data())

    def from_json(self, json_str: str) -> Dict:
        """Parse JSON string to dictionary"""
        return json.loads(json_str)

    def from_yaml(self, yaml_str: str) -> Dict:
        """Parse YAML string to dictionary"""
        return yaml.safe_load(yaml_str)
