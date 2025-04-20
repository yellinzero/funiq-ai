from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel

from providers.operators.core import OperatorEntity


class GetOperatorsResponse(BaseModel):
    operators: List[OperatorEntity]
    total: int


class WorkflowExecuteRequest(BaseModel):
    input_data: Dict[str, Any]
    version: str
    
    
class WorkflowDebugRequest(BaseModel):
    input_data: Dict[str, Any]
    snapshot_timestamp: datetime


class WorkflowStreamRequest(BaseModel):
    """Request model for streaming workflow execution"""
    input_data: Dict[str, Any]
    version: str | None = None
    snapshot_timestamp: datetime | None = None


class WorkflowExecuteResponse(BaseModel):
    result: str
    

class WorkflowDebugResponse(BaseModel):
    task_id: str
    