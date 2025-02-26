from typing import List

from providers.operators.core.operator_factory import OperatorFactory


class OperatorService:
    @staticmethod
    def get_all_operators() -> List[dict]:
        """
        Get all available operators and their schemas
        """
        operators = OperatorFactory.get_all_operators()
        operator_data = []
        
        for operator in operators:
            operator_schema = operator.get_operator_schema()
            operator_data.append(operator_schema.model_dump())
            
        return operator_data