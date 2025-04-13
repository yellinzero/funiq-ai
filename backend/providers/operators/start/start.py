from typing import Dict

from providers.operators.core import OperatorName

from ..core.base_operator import BaseOperator


class StartOperator(BaseOperator):
    operator_name = OperatorName.START.value
    """Start operator implementation"""

    async def _execute(self, config: Dict | None, **kwargs) -> Dict:
        """
        Execute the start operator

        Args:
            config: Contains the initial question for the workflow

        Returns:
            Dict containing the question in the format {"question": str}
        """
        if not config:
            raise ValueError("Config is required")

        result = {"question": config.get("question", "")}
        if not self.validate_output(result):
            raise ValueError("Output validation failed")
        return result
