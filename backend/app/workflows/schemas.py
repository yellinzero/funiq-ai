from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel

from providers.operators.core.models.operator import OperatorEntity


class GetOperatorsResponse(BaseModel):
    operators: List[OperatorEntity]
    total: int


class WorkflowExecuteRequest(BaseModel):
    input_data: Dict[str, Any]
    version: str
    
    
class WorkflowDebugRequest(BaseModel):
    input_data: Dict[str, Any]
    snapshot_timestamp: datetime


class WorkflowExecuteResponse(BaseModel):
    result: str
    

class WorkflowDebugResponse(BaseModel):
    task_id: str