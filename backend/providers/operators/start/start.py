from typing import Dict

from loguru import logger

from ..core.base_operator import BaseOperator


class StartOperator(BaseOperator):
    operator_name = "start"
    """Start operator implementation"""

    async def _execute(self, config: Dict, **kwargs) -> Dict:
        """
        Execute the start operator

        Args:
            config: Contains the initial question for the workflow

        Returns:
            Dict containing the question in the format {"question": str}
        """
        logger.debug(f"Start operator config: {config}")
        result = {"question": config.get("question", "")}
        if not self.validate_output(result):
            raise ValueError("Output validation failed")
        logger.debug(f"Start operator result: {result}")
        return result
