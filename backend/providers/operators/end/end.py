from typing import Dict

from ..core import OperatorName
from ..core.base_operator import BaseOperator


class EndOperator(BaseOperator):
    """End operator implementation"""

    operator_name = OperatorName.END.value

    async def _execute(self, config: Dict | None, input_data: Dict, **kwargs):
        """
        Execute the end operator

        Args:
            config: Configuration for output formatting

        Returns:
            Dict containing the processed result as a string
        """
        
        if len(self.stream_node_ids) > 1:
            raise ValueError("End operator can only have one input stream")

        if self.is_stream:
            if not self.has_stream_inputs:
                raise ValueError("End operator has no stream inputs")
            
            async def generator():
                async for chunk in input_data[self.stream_node_ids[0]]:
                    yield chunk
            return generator()
        
        if not self.is_stream:
            if not config:
                raise ValueError("Config is required")

            # Convert input data to string if it isn't already
            output = {"result": config.get("result", "")}
            if not self.validate_output(output):
                raise ValueError("Output validation failed")
               
        return output
