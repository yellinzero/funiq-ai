from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, BigInteger, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.core import DBBase
from utils.common.datetime import utcnow

from .schemas import ExecutionStates


class BaseWorkflowExecution(DBBase):
    """Base class for workflow executions with common fields."""
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    status: Mapped[ExecutionStates] = mapped_column(
        Enum(ExecutionStates), nullable=False
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    record_info: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: utcnow().replace(tzinfo=None)
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    __abstract__ = True

    @property
    def is_terminated(self) -> bool:
        """
        check if the workflow is terminated (including normal completion and abnormal termination)
        terminal states include: COMPLETED, FAILED, CANCELLED
        """
        terminal_states = {
            ExecutionStates.COMPLETED,
            ExecutionStates.FAILED,
            ExecutionStates.CANCELLED
        }
        return self.status in terminal_states

    @property
    def is_active(self) -> bool:
        """
        check if the workflow is active
        active states include: PENDING, RUNNING, PAUSED, CANCELLING
        """
        active_states = {
            ExecutionStates.PENDING,
            ExecutionStates.RUNNING,
            ExecutionStates.PAUSED,
            ExecutionStates.CANCELLING
        }
        return self.status in active_states


class BaseWorkflowNodeExecution(DBBase):
    """Base class for workflow node executions with common fields."""
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    node_key: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[ExecutionStates] = mapped_column(
        Enum(ExecutionStates), nullable=False
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    record_info: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: utcnow().replace(tzinfo=None)
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    __abstract__ = True

    @property
    def is_terminated(self) -> bool:
        """
        check if the node is terminated (including normal completion and abnormal termination)
        terminal states include: COMPLETED, FAILED, CANCELLED
        """
        terminal_states = {
            ExecutionStates.COMPLETED,
            ExecutionStates.FAILED,
            ExecutionStates.CANCELLED
        }
        return self.status in terminal_states

    @property
    def is_active(self) -> bool:
        """
        check if the node is active
        active states include: PENDING, RUNNING, PAUSED, CANCELLING
        """
        active_states = {
            ExecutionStates.PENDING,
            ExecutionStates.RUNNING,
            ExecutionStates.PAUSED,
            ExecutionStates.CANCELLING
        }
        return self.status in active_states


class WorkflowExecution(BaseWorkflowExecution):
    """Workflow execution tracking model."""
    
    version: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Version of the workflow that was executed"
    )

    __table_args__ = (
        Index("idx_execution_workflow_status", "workflow_id", "status"),
        Index("idx_execution_start_time", "start_time"),
        Index("idx_execution_version", "workflow_id", "version"),
        Index("idx_execution_created_at", "created_at"),
        Index("idx_execution_status_time", "status", "start_time", "end_time"),
    )


class WorkflowNodeExecution(BaseWorkflowNodeExecution):
    """Individual node execution tracking model."""
    
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent workflow execution",
    )
    workflow_execution: Mapped[WorkflowExecution] = relationship(
        "WorkflowExecution", backref="node_executions"
    )

    __table_args__ = (
        Index("idx_node_execution_status", "status"),
        Index("idx_node_execution_workflow", "run_id"),
        Index("idx_node_execution_time", "start_time", "end_time"),
        Index("idx_node_execution_node", "node_key"),
    )


class WorkflowDebugExecution(BaseWorkflowExecution):
    """Workflow debug execution model."""
    
    snapshot_timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Timestamp of the workflow snapshot used for debugging"
    )

    __table_args__ = (
        Index("idx_debug_execution_workflow", "workflow_id"),
        Index("idx_debug_execution_snapshot", "workflow_id", "snapshot_timestamp"),
    )


class WorkflowNodeDebugExecution(BaseWorkflowNodeExecution):
    """Workflow node debug execution model."""
    
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_debug_executions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent workflow debug execution",
    )
    workflow_debug_execution: Mapped[WorkflowDebugExecution] = relationship(
        "WorkflowDebugExecution", backref="node_executions"
    )

    __table_args__ = (
        Index("idx_node_debug_execution_workflow", "run_id"),
    )


class BaseExecutionLog(DBBase):
    """Base log model with common fields."""
    
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True,
        comment="Auto-incrementing log entry ID"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=lambda: utcnow().replace(tzinfo=None),
        comment="When the log entry was created"
    )
    level: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        comment="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    message: Mapped[str] = mapped_column(
        Text, 
        nullable=False,
        comment="Log message content"
    )
    context: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        comment="Additional contextual information"
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        nullable=False,
        comment="User who created this log entry"
    )

    __abstract__ = True


class WorkflowExecutionLog(BaseExecutionLog):
    """Workflow execution log."""

    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the workflow execution"
    )
    
    # Relationships
    workflow_execution: Mapped[WorkflowExecution] = relationship(
        "WorkflowExecution", backref="logs"
    )

    __table_args__ = (
        Index("idx_wf_log_run", "run_id"),
        Index("idx_wf_log_timestamp", "timestamp"),
        Index("idx_wf_log_level", "level"),
        Index("idx_wf_log_run_time", "run_id", "timestamp"),
    )


class WorkflowDebugLog(BaseExecutionLog):
    """Debug workflow execution log."""

    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_debug_executions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the debug workflow execution"
    )
    
    # Relationships
    debug_execution: Mapped[WorkflowDebugExecution] = relationship(
        "WorkflowDebugExecution", backref="logs"
    )

    __table_args__ = (
        Index("idx_wf_debug_log_run", "run_id"),
        Index("idx_wf_debug_log_timestamp", "timestamp"),
        Index("idx_wf_debug_log_level", "level"),
        Index("idx_wf_debug_log_run_time", "run_id", "timestamp"),
    )
