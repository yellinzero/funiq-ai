import importlib
import os
from typing import ClassVar, Sequence

from loguru import logger

from .base_operator import BaseOperator


class OperatorFactory:
    _operator_class_map: ClassVar[dict[str, type[BaseOperator]]] = {}

    @classmethod
    def get_operator_instance(cls, operator_name: str, **kwargs) -> BaseOperator:
        """
        Get a new operator instance by operator type.
        Creates a new instance each time to avoid concurrency issues.

        :param operator_name: operator type (e.g. 'start', 'llm', 'end')
        :return: BaseOperator instance
        """
        # get from cache
        if operator_name in cls._operator_class_map:
            return cls._operator_class_map[operator_name](**kwargs)

        try:
            # construct module path
            module_path = f"providers.operators.{operator_name}.{operator_name}"
            # import module
            module = importlib.import_module(module_path)
            
            # find operator class
            operator_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseOperator) and 
                    hasattr(attr, 'operator_name') and
                    attr.operator_name == operator_name):
                    operator_class = attr
                    break
            else:
                # if not found, use old naming convention
                class_name = f"{operator_name.capitalize()}Operator"
                operator_class = getattr(module, class_name)
            
            # cache class definition (not instance)
            cls._operator_class_map[operator_name] = operator_class
            # return new instance
            return operator_class(**kwargs)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not load operator implementation for {operator_name}: {e!s}") from e

    @classmethod
    def get_all_operators(cls) -> Sequence[BaseOperator]:
        """
        Get all available operators by scanning the operators directory
        
        :return: List of BaseOperator instances
        """
        # Get the path of current file
        current_path = os.path.abspath(__file__)
        operators_path = os.path.dirname(os.path.dirname(current_path))

        # Get all operator directories (excluding __pycache__ etc)
        operator_dirs = [
            d for d in os.listdir(operators_path)
            if os.path.isdir(os.path.join(operators_path, d))
            and not d.startswith("__")
            and not d.startswith("_")
            and d != "core"
        ]

        operators = []
        for operator_name in operator_dirs:
            try:
                operator = cls.get_operator_instance(operator_name)
                operators.append(operator)
            except ValueError:
                logger.warning(f"Could not load operator implementation for {operator_name}")
                continue

        return operators 