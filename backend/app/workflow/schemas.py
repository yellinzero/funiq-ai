from datetime import datetime

from pydantic import BaseModel

from app.core.models.workflow import WorkflowStatus, WorkflowVersionStatus


class WorkflowInfo(BaseModel):
    id: str
    app_id: str
    status: WorkflowStatus
    config: dict
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
    version: str | None
    

class GetWorkflowsResponse(BaseModel):
    workflows: list[WorkflowInfo]
    total: int
    

class WorkflowNodeInfo(BaseModel):
    id: str
    workflow_id: str
    node_key: str
    node_type: str
    name: str
    description: str
    meta: dict
    config: dict
    extended_config: dict
    
    
class WorkflowEdgeInfo(BaseModel):
    id: str
    workflow_id: str
    edge_key: str
    source_node_key: str
    target_node_key: str
    meta: dict
    

class WorkflowSnapshotInfoBase(BaseModel):
    id: str
    workflow_id: str
    snapshot: dict
    snapshot_hash: str
    start_node_key: str
    end_node_key: str


class WorkflowVersionInfo(WorkflowSnapshotInfoBase):
    version: str
    status: WorkflowVersionStatus
    description: str
    published_at: datetime
    published_by: str
    

class GetWorkflowVersionsResponse(BaseModel):
    versions: list[WorkflowVersionInfo]
    total: int
    
    
class WorkflowDebugSnapshotInfo(WorkflowSnapshotInfoBase):
    snapshot_timestamp: datetime
    created_by: str
    created_at: datetime
    expires_at: datetime
    

class GetWorkflowDebugSnapshotsResponse(BaseModel):
    snapshots: list[WorkflowDebugSnapshotInfo]
    total: int
    

class WorkflowConfig(BaseModel):
    support_image: bool | None = None
    support_file: bool | None = None
    support_audio: bool | None = None
    support_tool: bool | None = None


class CreateWorkflowRequest(BaseModel):
    app_id: str
    config: WorkflowConfig | None = None
    

class EditWorkflowNodePayloadBase(BaseModel):
    name: str | None = None
    description: str | None = None
    config: dict | None = None
    extended_config: dict | None = None
    meta: dict | None = None


class CreateWorkflowNodePayload(EditWorkflowNodePayloadBase):
    node_type: str
    node_key: str
    name: str


class UpdateWorkflowNodePayload(EditWorkflowNodePayloadBase):
    pass


class EditWorkflowEdgePayloadBase(BaseModel):
    source_node_key: str
    target_node_key: str
    meta: dict | None = None


class CreateWorkflowEdgePayload(EditWorkflowEdgePayloadBase):
    edge_key: str
    

class UpdateWorkflowEdgePayload(EditWorkflowEdgePayloadBase):
    pass

    
class SaveWorkflowRequest(BaseModel):
    update_nodes: list[UpdateWorkflowNodePayload] | None = None
    update_edges: list[UpdateWorkflowEdgePayload] | None = None
    create_nodes: list[CreateWorkflowNodePayload] | None = None
    create_edges: list[CreateWorkflowEdgePayload] | None = None
    delete_nodes: list[str] | None = None
    delete_edges: list[str] | None = None
    config: WorkflowConfig | None = None
    

class EditWorkflowSnapshotBase(BaseModel):
    snapshot: dict
    snapshot_hash: str
    start_node_key: str
    end_node_key: str
    

class CreateWorkflowVersionPayload(EditWorkflowSnapshotBase):
    version: str
    description: str | None = None
    

class CreateWorkflowDebugSnapshotPayload(EditWorkflowSnapshotBase):
    snapshot_timestamp: datetime
    
    
    
    
    
