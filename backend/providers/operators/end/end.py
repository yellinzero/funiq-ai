from typing import Dict

from ..core.base_operator import BaseOperator


class EndOperator(BaseOperator):
    """End operator implementation"""
    operator_name = "end"
        
    async def execute(self, input_data: Dict, config: Dict) -> Dict:
        """
        Execute the end operator
        
        Args:
            input_data: Input data to be processed
            config: Configuration for output formatting
            
        Returns:
            Dict containing the processed result as a string
        """
        
        # Convert input data to string if it isn't already
        result = str(input_data)
        
        output = {
            "result": result
        }
        
        if self.validate_output(output):
            return output
        return {}