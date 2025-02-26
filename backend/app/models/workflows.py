from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import DBBase, DBUUIDIDModelMixin


class Workflow(DBBase, DBUUIDIDModelMixin):
    """Workflow main table"""

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # relationship
    nodes: Mapped[list["WorkflowNode"]] = relationship(
        "WorkflowNode", back_populates="workflow", cascade="all, delete-orphan"
    )
    edges: Mapped[list["WorkflowEdge"]] = relationship(
        "WorkflowEdge", back_populates="workflow", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("tenant_id", "name", name="unique_tenant_workflow"))

    def __repr__(self) -> str:
        return f"<Workflow(tenant_id={self.tenant_id}, name={self.name})>"


class WorkflowNode(DBBase, DBUUIDIDModelMixin):
    """Workflow node table"""

    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    node_key: Mapped[str] = mapped_column(String(255), nullable=False)
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # node meta, like position/description
    config: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # node config, like task parameters

    # relationship
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="nodes")
    source_edges: Mapped[list["WorkflowEdge"]] = relationship(
        "WorkflowEdge", back_populates="source_node", foreign_keys="WorkflowEdge.source_node_id"
    )
    target_edges: Mapped[list["WorkflowEdge"]] = relationship(
        "WorkflowEdge", back_populates="target_node", foreign_keys="WorkflowEdge.target_node_id"
    )

    __table_args__ = (UniqueConstraint("workflow_id", "node_key", name="unique_workflow_node"))

    def __repr__(self) -> str:
        return f"<WorkflowNode(workflow_id={self.workflow_id}, node_key={self.node_key})>"


class WorkflowEdge(DBBase, DBUUIDIDModelMixin):
    """Workflow edge table"""

    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), nullable=False, index=True)
    source_node_key: Mapped[str] = mapped_column(ForeignKey("workflow_nodes.node_key"), nullable=False)
    target_node_key: Mapped[str] = mapped_column(ForeignKey("workflow_nodes.node_key"), nullable=False)
    edge_key: Mapped[str] = mapped_column(String(255), nullable=False)
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # edge meta, like position
    config: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # edge config, like condition/priority
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # relationship
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="edges")
    source_node: Mapped["WorkflowNode"] = relationship(
        "WorkflowNode", back_populates="source_edges", foreign_keys=[source_node_key]
    )
    target_node: Mapped["WorkflowNode"] = relationship(
        "WorkflowNode", back_populates="target_edges", foreign_keys=[target_node_key]
    )

    def __repr__(self) -> str:
        return (
            f"<WorkflowEdge("
            f"workflow_id={self.workflow_id}, "
            f"source={self.source_node_key}, "
            f"target={self.target_node_key})>"
        )
