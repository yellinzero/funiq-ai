from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import DBBase, DBUUIDIDModelMixin
from utils.json_schemas.base import JSONSchema

if TYPE_CHECKING:
    from .app import App


class Workflow(DBBase, DBUUIDIDModelMixin):
    """Workflow definition model that represents a complete workflow template.

    A workflow is always associated with exactly one App, forming a one-to-one
    relationship where the workflow defines the technical implementation of the app's
    business logic.
    """

    # Basic information
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))

    # One-to-one relationship with App
    app: Mapped["App"] = relationship(
        "App",
        back_populates="workflow",
        uselist=False,
        single_parent=True
    )

    # Workflow components
    nodes: Mapped[list["WorkflowNode"]] = relationship(
        "WorkflowNode", 
        back_populates="workflow", 
        cascade="all, delete-orphan"
    )
    edges: Mapped[list["WorkflowEdge"]] = relationship(
        "WorkflowEdge", 
        back_populates="workflow", 
        cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("tenant_id", "name", name="unique_tenant_workflow"),)

    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, name={self.name})>"


class WorkflowNode(DBBase, DBUUIDIDModelMixin):
    """Node within a workflow that represents a single task or decision point.

    Each node has a specific type (e.g., llm, end, start) and contains
    configuration data that defines its behavior during workflow execution.
    """

    # Reference and identification
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), nullable=False, index=True)
    node_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Node properties
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'llm', 'end', 'start'
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # Display name

    # Configuration and metadata
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # UI metadata (position, size, description)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # Node configuration (parameters, settings)
    output_schema: Mapped[JSONSchema | None] = mapped_column(JSON)  # JSON schema for node output

    # Relationships
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="nodes")
    outgoing_edges: Mapped[list["WorkflowEdge"]] = relationship(
        "WorkflowEdge", back_populates="source_node", foreign_keys="WorkflowEdge.source_node_key"
    )
    incoming_edges: Mapped[list["WorkflowEdge"]] = relationship(
        "WorkflowEdge", back_populates="target_node", foreign_keys="WorkflowEdge.target_node_key"
    )

    __table_args__ = (
        UniqueConstraint("workflow_id", "node_key", name="unique_workflow_node"),
    )

    def __repr__(self) -> str:
        return (
            f"<WorkflowNode(workflow_id={self.workflow_id}, "
            f"name={self.name}, "
            f"key={self.node_key}, "
            f"type={self.node_type})>"
        )


class WorkflowEdge(DBBase, DBUUIDIDModelMixin):
    """Connection between two workflow nodes that defines execution flow.

    Edges represent the transitions between nodes and can contain conditions
    or other logic that determines when and how the workflow proceeds.
    """

    # Reference and identification
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    edge_key: Mapped[str] = mapped_column(String(255), nullable=False)
    
    source_node_key: Mapped[str] = mapped_column(String(255), nullable=False)
    target_node_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Edge properties
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'normal', 'condition', 'error'
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # UI metadata (path, style)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # Edge configuration (conditions, priorities)

    # Relationships
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="edges")
    source_node: Mapped["WorkflowNode"] = relationship(
        "WorkflowNode", back_populates="outgoing_edges", foreign_keys=[source_node_key]
    )
    target_node: Mapped["WorkflowNode"] = relationship(
        "WorkflowNode", back_populates="incoming_edges", foreign_keys=[target_node_key]
    )

    __table_args__ = (
        UniqueConstraint("workflow_id", "edge_key", name="unique_workflow_edge"),
        ForeignKeyConstraint(
            ["workflow_id", "source_node_key"],
            ["workflow_nodes.workflow_id", "workflow_nodes.node_key"],
            name="fk_edge_source_node"
        ),
        ForeignKeyConstraint(
            ["workflow_id", "target_node_key"],
            ["workflow_nodes.workflow_id", "workflow_nodes.node_key"],
            name="fk_edge_target_node"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<WorkflowEdge("
            f"key={self.edge_key}, "
            f"workflow_id={self.workflow_id}, "
            f"source={self.source_node_key}, "
            f"target={self.target_node_key}, "
            f"type={self.edge_type})>"
        )
