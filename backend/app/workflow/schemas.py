from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.core.models.workflow import WorkflowStatus
from providers.operators.core import OperatorEntity, OperatorName
from providers.operators.end.schema import EndOperatorOutput, EndOperatorStreamOutput


class GetOperatorsResponse(BaseModel):
    operators: List[OperatorEntity]
    total: int


class WorkflowExecuteContext(BaseModel):
    tenant_id: str
    user_id: str
    user_name: str
    
    
class WorkflowExecuteInputData(BaseModel):
    query: str
    image_list: List[str] | None = None
    file_list: List[str] | None = None
    audio_list: List[str] | None = None


class BaseWorkflowExecuteRequest(BaseModel):
    input_data: WorkflowExecuteInputData


class WorkflowExecuteRequest(BaseWorkflowExecuteRequest):
    version: str
    
    
class WorkflowDebugRequest(BaseWorkflowExecuteRequest):
    snapshot_timestamp: datetime


class WorkflowStreamRequest(BaseWorkflowExecuteRequest):
    """Request model for streaming workflow execution"""
    version: str | None = None
    snapshot_timestamp: datetime | None = None


class WorkflowExecuteResponse(EndOperatorOutput):
    pass


class WorkflowStreamResponse(EndOperatorStreamOutput):
    pass


class WorkflowDebugResponse(BaseModel):
    task_id: str


class WorkflowNodeOperation(BaseModel):
    node_key: str
    node_type: OperatorName | None = None
    name: str | None = None
    description: str | None = None
    meta: Dict[str, Any] | None = None
    config: Dict[str, Any] | None = None
    extended_config: Dict[str, Any] | None = None


class WorkflowEdgeOperation(BaseModel):
    edge_key: str
    source_node_key: str | None = None
    target_node_key: str | None = None
    meta: Dict[str, Any] | None = None


class WorkflowOperationType(str, Enum):
    ADD_NODE = "add_node"
    UPDATE_NODE = "update_node"
    DELETE_NODE = "delete_node"
    ADD_EDGE = "add_edge"
    UPDATE_EDGE = "update_edge"
    DELETE_EDGE = "delete_edge"


class WorkflowOperation(BaseModel):
    operation_type: WorkflowOperationType
    nodes: List[WorkflowNodeOperation] = Field(default_factory=list)
    edges: List[WorkflowEdgeOperation] = Field(default_factory=list)


class SaveWorkflowRequest(BaseModel):
    operations: List[WorkflowOperation]


class SaveWorkflowResponse(BaseModel):
    added_nodes: List[str] = Field(default_factory=list)
    updated_nodes: List[str] = Field(default_factory=list)
    deleted_nodes: List[str] = Field(default_factory=list)
    added_edges: List[str] = Field(default_factory=list)
    updated_edges: List[str] = Field(default_factory=list)
    deleted_edges: List[str] = Field(default_factory=list)
    snapshot: Dict[str, Any]
    snapshot_hash: str
    start_node_key: str
    end_node_key: str


class WorkflowNodeResponse(BaseModel):
    node_key: str
    node_type: OperatorName
    name: str
    description: str | None = None
    meta: Dict[str, Any] | None = None
    config: Dict[str, Any] | None = None
    extended_config: Dict[str, Any] | None = None
    workflow_id: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class WorkflowEdgeResponse(BaseModel):
    edge_key: str
    workflow_id: str
    source_node_key: str
    target_node_key: str
    meta: Dict[str, Any] | None = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class GetWorkflowResponseBase(BaseModel):   
    id: str
    app_id: str
    status: WorkflowStatus
    name: str
    description: str | None = None
    version: str | None = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class WorkflowResponse(GetWorkflowResponseBase):
    nodes: List[WorkflowNodeResponse]
    edges: List[WorkflowEdgeResponse]
    
    
class WorkflowListResponse(BaseModel):
    workflows: List[GetWorkflowResponseBase]
    total: int


class UpdateWorkflowMetaRequest(BaseModel):
    """Request model for updating workflow metadata."""
    name: str | None = None
    description: str | None = None
    
    
class PublishWorkflowRequest(BaseModel):
    version: str
    description: str | None = None
    

class PublishWorkflowResponse(BaseModel):
    workflow_id: str
    version: str
    description: str
    published_at: datetime
    published_by: str
    
    
