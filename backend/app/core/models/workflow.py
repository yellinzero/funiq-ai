from __future__ import annotations

import enum
import hashlib
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, ForeignKeyConstraint, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import and_, select

from infrastructure import DBBase, DBUUIDModelMixin
from providers.operators.core import OperatorName
from utils.common.datetime import utcnow
from utils.common.json import json_dumps

# ---------- Enums ----------


class WorkflowStatus(str, enum.Enum):
    """Workflow status enum defining possible states of a workflow."""

    DRAFT = "draft"  # Initial state, workflow is being edited
    PUBLISHED = "published"  # Workflow is finalized and ready for execution


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
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, comment="Reference to the parent tenant"
    )
    app_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("apps.id", ondelete="CASCADE"), nullable=False, comment="Reference to the parent application"
    )
    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus),
        nullable=False,
        default=WorkflowStatus.DRAFT,
        comment="Current status of the workflow",
    )
    version: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Current version number of the workflow"
    )
    config: Mapped[dict | None] = mapped_column(JSON, comment="Workflow configuration")

    nodes: Mapped[list[WorkflowNode]] = relationship(
        "WorkflowNode", back_populates="workflow", cascade="all, delete-orphan", lazy="raise"
    )
    edges: Mapped[list[WorkflowEdge]] = relationship(
        "WorkflowEdge", back_populates="workflow", cascade="all, delete-orphan", lazy="raise"
    )
    versions: Mapped[list[WorkflowVersion]] = relationship(
        "WorkflowVersion", back_populates="workflow", cascade="all, delete-orphan", lazy="raise"
    )
    debug_snapshots: Mapped[list[WorkflowDebugSnapshot]] = relationship(
        "WorkflowDebugSnapshot", back_populates="workflow", cascade="all, delete-orphan", lazy="raise"
    )

    __table_args__ = (
        Index("idx_workflow_tenant", "tenant_id"),
        Index("idx_workflow_status_created", "status", "created_at"),
        Index("idx_workflow_updated", "updated_at"),
    )

    def __repr__(self) -> str:
        return f"<Workflow(app_id={self.app_id}, workflow_id={self.id})>"

    async def get_snapshot(self, session: AsyncSession, need_hash: bool = False) -> tuple[dict, str | None]:
        snapshot_hash = None
        nodes = await self.get_nodes(session)
        edges = await self.get_edges(session)
        snapshot = {
            "nodes": [node.to_dict(convert_uuid_to_str=True) for node in nodes],
            "edges": [edge.to_dict(convert_uuid_to_str=True) for edge in edges],
            "config": self.config,
        }
        if need_hash:
            snapshot_hash = hashlib.sha256(json_dumps(snapshot).encode()).hexdigest()
        return snapshot, snapshot_hash

    async def get_end_node(self, session: AsyncSession) -> WorkflowNode:
        result = await session.execute(
            select(WorkflowNode).where(
                and_(WorkflowNode.node_type == OperatorName.END.value, WorkflowNode.workflow_id == self.id)
            )
        )
        return result.scalar_one_or_none()

    async def get_start_node(self, session: AsyncSession) -> WorkflowNode:
        result = await session.execute(
            select(WorkflowNode).where(
                and_(WorkflowNode.node_type == OperatorName.START.value, WorkflowNode.workflow_id == self.id)
            )
        )
        return result.scalar_one_or_none()

    async def get_nodes(self, session: AsyncSession) -> list[WorkflowNode]:
        result = await session.execute(select(WorkflowNode).where(WorkflowNode.workflow_id == self.id))
        result = result.scalars().all()
        return result

    async def get_edges(self, session: AsyncSession) -> list[WorkflowEdge]:
        result = await session.execute(select(WorkflowEdge).where(WorkflowEdge.workflow_id == self.id))
        result = result.scalars().all()
        return result

    @property
    def is_published(self) -> bool:
        return self.status == WorkflowStatus.PUBLISHED

    @property
    def is_draft(self) -> bool:
        return self.status == WorkflowStatus.DRAFT


class WorkflowNode(DBBase, DBUUIDModelMixin):
    """Node within a workflow representing a single task or decision point.

    Each node has a specific type (e.g., llm, end, start) and contains
    configuration data that defines its behavior during workflow execution.
    Nodes are connected via edges to form the workflow graph.
    """

    # Primary key and references
    node_key: Mapped[str] = mapped_column(String(10), comment="Unique identifier for the node within its workflow")
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, comment="Reference to the parent workflow"
    )

    # Node properties
    node_type: Mapped[OperatorName] = mapped_column(
        Enum(OperatorName), nullable=False, comment="Type of operation this node performs"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Display name of the node")
    description: Mapped[str | None] = mapped_column(Text, comment="Optional description of the node's purpose")

    # Configuration and metadata
    meta: Mapped[dict | None] = mapped_column(
        JSON, comment="Node metadata including UI properties (position, style, etc)"
    )

    config: Mapped[dict | None] = mapped_column(
        JSON, comment="Core configuration for node operation (parameters, settings)"
    )

    extended_config: Mapped[dict | None] = mapped_column(
        JSON, comment="Extended configuration specific to node type (e.g., LLM parameters)"
    )

    # Relationships
    workflow: Mapped[Workflow] = relationship(
        "Workflow", back_populates="nodes", lazy="raise", foreign_keys=[workflow_id]
    )

    __table_args__ = (
        UniqueConstraint("workflow_id", "node_key", name="uq_workflow_node"),
        Index("idx_node_workflow", "workflow_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<WorkflowNode(workflow_id={self.workflow_id}, "
            f"name={self.name}, "
            f"key={self.node_key}, "
            f"type={self.node_type})>"
        )

    async def get_incoming_edges(self, session: AsyncSession) -> list[WorkflowEdge]:
        result = await session.execute(select(WorkflowEdge).where(WorkflowEdge.target_node_key == self.node_key))
        return result.scalars().all()

    async def get_outgoing_edges(self, session: AsyncSession) -> list[WorkflowEdge]:
        result = await session.execute(select(WorkflowEdge).where(WorkflowEdge.source_node_key == self.node_key))
        return result.scalars().all()


class WorkflowEdge(DBBase, DBUUIDModelMixin):
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

    # Edge properties
    meta: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, comment="Edge metadata including UI properties (path style, labels)"
    )

    # Relationships
    workflow: Mapped[Workflow] = relationship(
        "Workflow", back_populates="edges", lazy="raise", foreign_keys=[workflow_id]
    )

    __table_args__ = (
        UniqueConstraint("workflow_id", "edge_key", name="uq_workflow_edge"),
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
            f"target={self.target_node_key}"
            f")>"
        )

    async def get_source_node(self, session: AsyncSession) -> WorkflowNode:
        result = await session.execute(select(WorkflowNode).where(WorkflowNode.node_key == self.source_node_key))
        return result.scalar_one_or_none()

    async def get_target_node(self, session: AsyncSession) -> WorkflowNode:
        result = await session.execute(select(WorkflowNode).where(WorkflowNode.node_key == self.target_node_key))
        return result.scalar_one_or_none()


class BaseWorkflowSnapshotModel(DBBase):
    """Base class for workflow snapshot models with common fields and properties."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot: Mapped[dict] = mapped_column(JSON, comment="Snapshot data")
    snapshot_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    start_node_key: Mapped[str] = mapped_column(String(10), nullable=False)
    end_node_key: Mapped[str] = mapped_column(String(10), nullable=False)
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, comment="Reference to the parent workflow"
    )

    __abstract__ = True

    @property
    def nodes(self) -> list[WorkflowNode]:
        if not self.snapshot:
            raise ValueError("Snapshot is not available")
        nodes = self.snapshot.get("nodes", [])
        result = []

        for node in nodes:
            result.append(WorkflowNode(**node))
        return result

    @property
    def edges(self) -> list[WorkflowEdge]:
        if not self.snapshot:
            raise ValueError("Snapshot is not available")

        edges = self.snapshot.get("edges", [])
        result = []

        for edge in edges:
            result.append(WorkflowEdge(**edge))
        return result

    @property
    def snapshot_config(self) -> dict:
        if not self.snapshot:
            raise ValueError("Snapshot is not available")
        return self.snapshot.get("config", {})

    @property
    def end_node(self) -> WorkflowNode:
        if not self.nodes:
            raise ValueError("Nodes are not available")
        node = next((node for node in self.nodes if node.node_key == self.end_node_key), None)
        if not node:
            raise ValueError("End node not found")
        return node

    @property
    def start_node(self) -> WorkflowNode:
        if not self.nodes:
            raise ValueError("Nodes are not available")
        node = next((node for node in self.nodes if node.node_key == self.start_node_key), None)
        if not node:
            raise ValueError("Start node not found")
        return node

    __table_args__ = (Index("idx_workflow_snapshot_workflow", "workflow_id"),)


class WorkflowVersion(BaseWorkflowSnapshotModel):
    version: Mapped[str] = mapped_column(String(50))
    status: Mapped[WorkflowVersionStatus] = mapped_column(
        Enum(WorkflowVersionStatus), nullable=False, default=WorkflowVersionStatus.ACTIVE
    )
    description: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(default=lambda: utcnow().replace(tzinfo=None))
    published_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    workflow: Mapped[Workflow] = relationship("Workflow", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("workflow_id", "version", name="uq_workflow_version"),
        Index("idx_workflow_version_status", "status"),
    )

    @property
    def is_active(self) -> bool:
        return self.status == WorkflowVersionStatus.ACTIVE

    @property
    def is_deprecated(self) -> bool:
        return self.status == WorkflowVersionStatus.DEPRECATED

    @property
    def is_archived(self) -> bool:
        return self.status == WorkflowVersionStatus.ARCHIVED

    @property
    def is_inactive(self) -> bool:
        return self.status == WorkflowVersionStatus.INACTIVE


class WorkflowDebugSnapshot(BaseWorkflowSnapshotModel):
    snapshot_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    workflow: Mapped[Workflow] = relationship("Workflow", back_populates="debug_snapshots")

    __table_args__ = (
        UniqueConstraint("workflow_id", "snapshot_timestamp", name="uq_workflow_debug_snapshots_composite"),
    )
