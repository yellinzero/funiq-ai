from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from prefect.client.schemas.objects import StateType
from sqlalchemy import JSON, DateTime, Enum, ForeignKey, ForeignKeyConstraint, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure import DBAuditFieldsMixin, DBBase, DBUUIDModelMixin

if TYPE_CHECKING:
    from .app import App


# ---------- Enums ----------


class WorkflowStatus(str, enum.Enum):
    """Workflow status enum defining possible states of a workflow."""

    DRAFT = "draft"  # Initial state, workflow is being edited
    PUBLISHED = "published"  # Workflow is finalized and ready for execution


class WorkflowNodeType(str, enum.Enum):
    """Workflow node type enum defining supported node types."""

    LLM = "llm"  # Language Model operation node
    END = "end"  # Terminal node marking workflow completion
    START = "start"  # Entry point node of the workflow


class WorkflowVersionStatus(str, enum.Enum):
    """Workflow version status enum defining possible states of a workflow version."""

    DEPRECATED = "deprecated"  # workflow version is deprecated
    ARCHIVED = "archived"  # workflow version is archived
    INACTIVE = "inactive"  # workflow version is inactive
    ACTIVE = "active"  # workflow version is active


# ---------- Models ----------
class Workflow(DBBase, DBUUIDModelMixin):
    """Workflow definition model representing a complete workflow template.

    A workflow is always associated with exactly one App, forming a one-to-one
    relationship where the workflow defines the technical implementation of the app's
    business logic. Each workflow can have multiple versions and maintains its execution
    history.
    """

    # Basic information
    app_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("apps.id", ondelete="CASCADE"), nullable=False, comment="Reference to the parent application"
    )
    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus),
        nullable=False,
        default=WorkflowStatus.DRAFT,
        comment="Current status of the workflow",
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Display name of the workflow")
    description: Mapped[str | None] = mapped_column(
        String(255), comment="Optional description of the workflow's purpose"
    )
    version: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Current version number of the workflow"
    )

    # Relationships
    app: Mapped[App] = relationship("App", back_populates="workflow", uselist=False, single_parent=True)
    nodes: Mapped[list[WorkflowNode]] = relationship(
        "WorkflowNode", back_populates="workflow", cascade="all, delete-orphan"
    )
    edges: Mapped[list[WorkflowEdge]] = relationship(
        "WorkflowEdge", back_populates="workflow", cascade="all, delete-orphan"
    )
    versions: Mapped[list[WorkflowVersion]] = relationship(
        "WorkflowVersion", back_populates="workflow", cascade="all, delete-orphan"
    )
    snapshots: Mapped[list[WorkflowSnapshot]] = relationship(
        "WorkflowSnapshot", back_populates="workflow", cascade="all, delete-orphan"
    )

    # Audit fields with default values
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("app_id", "name", name="uq_workflow_app_name"),
        Index("idx_workflow_status_created", "status", "created_at"),
        Index("idx_workflow_updated", "updated_at"),
    )

    def __repr__(self) -> str:
        return f"<Workflow(app_id={self.app_id}, workflow_id={self.id}, name={self.name})>"


class WorkflowNode(DBBase, DBAuditFieldsMixin):
    """Node within a workflow representing a single task or decision point.

    Each node has a specific type (e.g., llm, end, start) and contains
    configuration data that defines its behavior during workflow execution.
    Nodes are connected via edges to form the workflow graph.
    """

    # Primary key and references
    node_key: Mapped[str] = mapped_column(
        String(10), primary_key=True, comment="Unique identifier for the node within its workflow"
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, comment="Reference to the parent workflow"
    )

    # Node properties
    node_type: Mapped[WorkflowNodeType] = mapped_column(
        Enum(WorkflowNodeType), nullable=False, comment="Type of operation this node performs"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Display name of the node")
    description: Mapped[str | None] = mapped_column(String(255), comment="Optional description of the node's purpose")

    # Configuration and metadata
    meta: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, comment="Node metadata including UI properties (position, style, etc)"
    )

    config: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, comment="Core configuration for node operation (parameters, settings)"
    )

    extended_config: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, comment="Extended configuration specific to node type (e.g., LLM parameters)"
    )

    # Audit fields with default values
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Relationships
    workflow: Mapped[Workflow] = relationship("Workflow", back_populates="nodes")
    outgoing_edges: Mapped[list[WorkflowEdge]] = relationship(
        "WorkflowEdge",
        back_populates="source_node",
        foreign_keys="WorkflowEdge.source_node_key",
        cascade="all, delete-orphan",
    )
    incoming_edges: Mapped[list[WorkflowEdge]] = relationship(
        "WorkflowEdge",
        back_populates="target_node",
        foreign_keys="WorkflowEdge.target_node_key",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("workflow_id", "node_key", name="uq_workflow_node"),
        UniqueConstraint("workflow_id", "name", name="uq_workflow_node_name"),
        Index("idx_node_workflow", "workflow_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<WorkflowNode(workflow_id={self.workflow_id}, "
            f"name={self.name}, "
            f"key={self.node_key}, "
            f"type={self.node_type})>"
        )


class WorkflowEdge(DBBase, DBAuditFieldsMixin):
    """Connection between two workflow nodes defining execution flow.

    Edges represent the transitions between nodes and can contain conditions
    or other logic that determines when and how the workflow proceeds from
    one node to another.
    """

    # Primary key and references
    edge_key: Mapped[str] = mapped_column(
        String(10), primary_key=True, comment="Unique identifier for the edge within its workflow"
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, comment="Reference to the parent workflow"
    )
    source_node_key: Mapped[str] = mapped_column(String(10), nullable=False, comment="Reference to the source node")
    target_node_key: Mapped[str] = mapped_column(String(10), nullable=False, comment="Reference to the target node")

    # Audit fields
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Edge properties
    meta: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, comment="Edge metadata including UI properties (path style, labels)"
    )

    # Relationships
    workflow: Mapped[Workflow] = relationship("Workflow", back_populates="edges")
    source_node: Mapped[WorkflowNode] = relationship(
        "WorkflowNode", back_populates="outgoing_edges", foreign_keys=[source_node_key]
    )
    target_node: Mapped[WorkflowNode] = relationship(
        "WorkflowNode", back_populates="incoming_edges", foreign_keys=[target_node_key]
    )

    __table_args__ = (
        UniqueConstraint("workflow_id", "edge_key", name="uq_workflow_edge"),
        UniqueConstraint("workflow_id", "source_node_key", "target_node_key", name="uq_workflow_edge_nodes"),
        ForeignKeyConstraint(
            ["workflow_id", "source_node_key"],
            ["workflow_nodes.workflow_id", "workflow_nodes.node_key"],
            name="fk_edge_source_node",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["workflow_id", "target_node_key"],
            ["workflow_nodes.workflow_id", "workflow_nodes.node_key"],
            name="fk_edge_target_node",
            ondelete="CASCADE",
        ),
        Index("idx_edge_workflow_source", "workflow_id", "source_node_key"),
        Index("idx_edge_workflow_target", "workflow_id", "target_node_key"),
    )

    def __repr__(self) -> str:
        return (
            f"<WorkflowEdge("
            f"key={self.edge_key}, "
            f"workflow_id={self.workflow_id}, "
            f"source={self.source_node_key}, "
            f"target={self.target_node_key}, "
        )


class WorkflowVersion(DBBase):
    """Workflow version history tracking model.

    Maintains a record of all published versions of a workflow, including
    metadata about when and by whom the version was published.
    """

    version: Mapped[str] = mapped_column(String(50), primary_key=True, comment="Version identifier (e.g., v1.0.0)")
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, comment="Reference to the parent workflow"
    )
    status: Mapped[WorkflowVersionStatus] = mapped_column(
        Enum(WorkflowVersionStatus),
        nullable=False,
        default=WorkflowVersionStatus.ACTIVE,
        comment="Current status of the workflow version",
    )

    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, comment="Snapshot of the workflow version")
    snapshot_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(String(255), comment="Description of changes in this version")
    published_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        comment="Timestamp when this version was published",
    )
    published_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="User ID who published this version"
    )

    workflow: Mapped[Workflow] = relationship("Workflow", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("workflow_id", "version", name="uq_workflow_version"),
        Index("idx_workflow_version_workflow", "workflow_id"),
        Index("idx_workflow_version_status", "status"),
    )


class WorkflowExecution(DBBase):
    """Workflow execution tracking model.

    Records details about each execution of a workflow, including timing,
    status, and execution results.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="Unique identifier for this execution"
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, comment="Reference to the executed workflow"
    )
    version: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("workflow_versions.version", ondelete="CASCADE"),
        nullable=False,
        comment="Version of the workflow that was executed",
    )

    flow_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="Prefect flow run identifier"
    )
    status: Mapped[StateType] = mapped_column(
        Enum(StateType), nullable=False, comment="Current status of the execution"
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="When the execution started")
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="When the execution completed")
    record_info: Mapped[dict[str, Any]] = mapped_column(JSON, comment="Additional execution metadata and results")

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Relationships
    workflow_version: Mapped[WorkflowVersion] = relationship(
        "WorkflowVersion", foreign_keys=[workflow_id, version], backref="executions"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["workflow_id", "version"],
            ["workflow_versions.workflow_id", "workflow_versions.version"],
            name="fk_execution_version",
            ondelete="CASCADE",
        ),
        Index("idx_execution_workflow_status", "workflow_id", "status"),
        Index("idx_execution_start_time", "start_time"),
        Index("idx_execution_version", "workflow_id", "version"),
    )


class WorkflowNodeExecution(DBBase):
    """Individual node execution tracking model.

    Records details about the execution of each node within a workflow run,
    including timing, status, and execution results.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="Unique identifier for this node execution"
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent workflow execution",
    )
    node_key: Mapped[str] = mapped_column(String(10), nullable=False, comment="Reference to the executed node")
    flow_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="Prefect flow run identifier"
    )
    task_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="Prefect task run identifier"
    )
    status: Mapped[StateType] = mapped_column(
        Enum(StateType), nullable=False, comment="Current status of the node execution"
    )
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="When the node execution started"
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="When the node execution completed"
    )
    record_info: Mapped[dict[str, Any]] = mapped_column(JSON, comment="Additional node execution metadata and results")

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    # Relationships
    workflow_execution: Mapped[WorkflowExecution] = relationship("WorkflowExecution", backref="node_executions")

    __table_args__ = (
        Index("idx_node_execution_flow", "flow_run_id", "status"),
        Index("idx_node_execution_workflow", "execution_id"),
    )


class WorkflowSnapshot(DBBase):
    """Workflow snapshot model."""

    snapshot_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, primary_key=True)
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, comment="Reference to the parent workflow"
    )
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    snapshot_hash: Mapped[str] = mapped_column(String(256), nullable=False)

    # relationship
    workflow: Mapped[Workflow] = relationship(
        "Workflow",
        back_populates="snapshots",
    )

    __table_args__ = (
        UniqueConstraint("workflow_id", "snapshot_timestamp", name="uq_workflow_snapshots_composite"),
        Index("idx_workflow_snapshot_workflow", "workflow_id"),
    )


class WorkflowDebugExecution(DBBase):
    """Workflow debug execution model."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Timestamp of the workflow snapshot used for debugging"
    )
    flow_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[StateType] = mapped_column(Enum(StateType), nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    record_info: Mapped[dict[str, Any]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    
    # Relationships
    workflow_snapshot: Mapped[WorkflowSnapshot] = relationship(
        "WorkflowSnapshot", foreign_keys=[workflow_id, snapshot_timestamp]
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["workflow_id", "snapshot_timestamp"],
            ["workflow_snapshots.workflow_id", "workflow_snapshots.snapshot_timestamp"],
            name="fk_debug_execution_snapshot",
            ondelete="CASCADE",
        ),
        Index("idx_debug_execution_workflow", "workflow_id"),
        Index("idx_debug_execution_snapshot", "workflow_id", "snapshot_timestamp"),
    )


class WorkflowNodeDebugExecution(DBBase):
    """Workflow node debug execution model."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_debug_executions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent workflow debug execution",
    )
    node_key: Mapped[str] = mapped_column(String(10), nullable=False)
    flow_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    task_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[StateType] = mapped_column(Enum(StateType), nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    record_info: Mapped[dict[str, Any]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Relationships
    workflow_debug_execution: Mapped[WorkflowDebugExecution] = relationship(
        "WorkflowDebugExecution", backref="node_executions"
    )

    __table_args__ = (Index("idx_node_debug_execution_workflow", "execution_id"),)
