from typing import Dict

from loguru import logger

from ..core.base_operator import BaseOperator


class EndOperator(BaseOperator):
    """End operator implementation"""

    operator_name = "end"

    async def _execute(self, config: Dict, **kwargs) -> Dict:
        """
        Execute the end operator

        Args:
            config: Configuration for output formatting

        Returns:
            Dict containing the processed result as a string
        """

        # Convert input data to string if it isn't already
        logger.debug(f"End operator config: {config}")

        output = {"result": config.get("result", "")}

        if not self.validate_output(output):
            raise ValueError("Output validation failed")
        
        logger.debug(f"End operator result: {output}")

        return output
