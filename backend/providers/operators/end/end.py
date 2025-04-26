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
        
        if not self.is_stream:
            if not config:
                raise ValueError("Config is required")
            output = {"id": config.get("id"), "message": config.get("message", "")}
            if not self.validate_output(output):
                raise ValueError("Output validation failed")
            return output

        if not self.has_stream_inputs:
            raise ValueError("End operator has no stream inputs")
            
        # use stream handling mixin to handle multiple streams
        stream_inputs = {node_id: input_data[node_id] for node_id in self.stream_node_ids}
        return self.handle_multiple_streams(stream_inputs)
        
