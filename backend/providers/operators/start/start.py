from typing import Dict

from ..core.base_operator import BaseOperator


class StartOperator(BaseOperator):
    operator_name = "start"
    """Start operator implementation"""
        
    async def execute(self, input_data: Dict, config: Dict) -> Dict:
        """
        Execute the start operator
        
        Args:
            input_data: Contains the initial question for the workflow
            config: Not used in start operator as per schema
            
        Returns:
            Dict containing the question in the format {"question": str}
        """
        return {"question": input_data.get("question", "")} 