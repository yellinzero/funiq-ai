from typing import List

from fastapi import status
from loguru import logger

from app.core.errors.workflow import WorkflowErrorCode
from providers.operators.core import OperatorEntity, OperatorFactory


class OperatorService:
    @staticmethod
    def get_all_operators() -> List[OperatorEntity]:
        """
        Get all available operators and their schemas
        """
        try:
            operators = OperatorFactory.get_all_operators()
            operator_data = []

            for operator in operators:
                operator_schema = operator.get_operator_schema()
                operator_data.append(operator_schema.model_dump())

            return operator_data
        except Exception as e:
            logger.error(f"Error getting all operators: {e}")
            raise WorkflowErrorCode.OPERATOR_FETCH_FAILED.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e
