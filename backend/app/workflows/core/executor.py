# TODO implement workflow execution
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

import networkx as nx
from loguru import logger
from prefect import get_client, task
from prefect.client.schemas.actions import ArtifactCreate
from prefect.client.schemas.objects import StateType
from prefect.logging import get_run_logger
from prefect.runtime import task_run
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.workflow import (
    Workflow,
    WorkflowDebugExecution,
    WorkflowEdge,
    WorkflowExecution,
    WorkflowNode,
    WorkflowNodeDebugExecution,
    WorkflowNodeExecution,
    WorkflowSnapshot,
)
from providers.operators.core.operator_factory import OperatorFactory


class WorkflowExecutorBase:
    """Base class for workflow execution."""

    def __init__(self, workflow: Workflow, session: AsyncSession):
        self.workflow = workflow
        self.session = session
        self.graph = None
        self.node_levels = None
        self.task_registry: Dict[str, task] = {}
        self.flow_run_id: Optional[UUID] = None
        logger.info(f"Initializing WorkflowExecutor for workflow: {workflow.name}")

    async def initialize(self):
        """Initialize the executor by building the graph and calculating node levels."""
        logger.info(f"Starting initialization for workflow: {self.workflow.name}")
        self.graph = await self._build_graph()
        self.node_levels = self._calculate_node_levels()
        logger.debug(f"Node levels calculated: {self.node_levels}")

    async def _build_graph(self) -> nx.DiGraph:
        """Build a NetworkX directed graph from workflow nodes and edges."""
        logger.debug(f"Building graph for workflow: {self.workflow.name}")
        g = nx.DiGraph()

        nodes_result = await self.session.execute(
            select(WorkflowNode).where(WorkflowNode.workflow_id == self.workflow.id)
        )
        nodes = nodes_result.scalars().all()
        logger.debug(f"Found {len(nodes)} nodes")

        edges_result = await self.session.execute(
            select(WorkflowEdge).where(WorkflowEdge.workflow_id == self.workflow.id)
        )
        edges = edges_result.scalars().all()
        logger.debug(f"Found {len(edges)} edges")

        for node in nodes:
            g.add_node(node.node_key, node=node)
        for edge in edges:
            g.add_edge(edge.source_node_key, edge.target_node_key, edge=edge)

        logger.debug(f"Graph built with {g.number_of_nodes()} nodes and {g.number_of_edges()} edges")
        return g

    def _calculate_node_levels(self) -> Dict[str, int]:
        """Calculate the level of each node in the workflow graph."""
        levels = {}
        source_nodes = [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]
        if not source_nodes:
            raise ValueError("Workflow graph must have at least one source node")

        for node in self.graph.nodes():
            paths = []
            for source in source_nodes:
                try:
                    paths.extend(nx.all_simple_paths(self.graph, source, node))
                except nx.NetworkXNoPath:
                    continue

            level = max((len(path) - 1 for path in paths), default=0)
            levels[node] = level
        return levels

    def _get_upstream_outputs(self, node_key: str, current_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Get outputs from upstream nodes."""
        prefect_logger = get_run_logger()
        upstream_outputs = {}
        for edge in self.graph.edges(data=True):
            if edge[1] == node_key:
                source_key = edge[0]
                if source_key in current_inputs:
                    upstream_outputs[source_key] = current_inputs[source_key]
        prefect_logger.debug(f"Node {node_key} upstream outputs: {upstream_outputs.keys()}")
        return upstream_outputs

    async def _create_execution_record(self) -> None:
        """Create execution record in database."""
        raise NotImplementedError

    async def _update_execution_status(self, status: StateType) -> None:
        """Update execution status in database."""
        raise NotImplementedError

    async def _create_node_execution_record(self, node: WorkflowNode, task_run_id: UUID) -> None:
        """Create node execution record in database."""
        raise NotImplementedError

    async def _update_node_execution_status(self, node_key: str, task_run_id: UUID, status: StateType) -> None:
        """Update node execution status in database."""
        raise NotImplementedError

    def _create_task_for_node(self, node: WorkflowNode) -> task:
        """Create a Prefect task for a workflow node."""
        logger.debug(f"Creating task for node: {node.name} (type: {node.node_type})")

        @task(name=node.name, timeout_seconds=60, tags=[node.name])
        async def node_task(**kwargs):
            prefect_logger = get_run_logger()
            task_run_id = task_run.get_id()

            # Create node execution record
            await self._create_node_execution_record(node, task_run_id)

            try:
                # Update status to running
                await self._update_node_execution_status(node.node_key, task_run_id, StateType.RUNNING)

                config = node.config or {}
                upstream_outputs = self._get_upstream_outputs(node.node_key, kwargs)

                operator = OperatorFactory.get_operator_instance(node.node_type)
                if not operator:
                    raise ValueError(f"No operator found for type: {node.node_type}")

                result = await operator.execute(input_data=upstream_outputs, config=config)

                # Create artifact
                async with get_client() as client:
                    artifact = await client.create_artifact(
                        artifact=ArtifactCreate(
                            key=f"{node.node_key}-result",
                            data=result,
                            description=f"Result for node {node.name}",
                            task_run_id=task_run_id,
                        )
                    )

                # Update status to completed
                await self._update_node_execution_status(node.node_key, task_run_id, StateType.COMPLETED)
                return result

            except Exception as e:
                # Update status to failed
                await self._update_node_execution_status(node.node_key, task_run_id, StateType.FAILED)
                raise

        return node_task


class WorkflowVersionExecutor(WorkflowExecutorBase):
    """Executor for published workflow versions."""

    def __init__(self, workflow: Workflow, version: str, session: AsyncSession):
        super().__init__(workflow, session)
        self.version = version
        self.execution_id: Optional[UUID] = None

    async def _create_execution_record(self) -> None:
        """Create workflow execution record."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        execution = WorkflowExecution(
            workflow_id=self.workflow.id,
            version=self.version,
            flow_run_id=self.flow_run_id,
            status=StateType.PENDING,
            start_time=now,
            end_time=now,  # Will be updated when execution completes
            record_info={},
        )
        self.session.add(execution)
        await self.session.flush()
        self.execution_id = execution.id

    async def _create_node_execution_record(self, node: WorkflowNode, task_run_id: UUID) -> None:
        """Create node execution record."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        node_execution = WorkflowNodeExecution(
            execution_id=self.execution_id,
            node_key=node.node_key,
            flow_run_id=self.flow_run_id,
            task_run_id=task_run_id,
            status=StateType.PENDING,
            start_time=now,
            end_time=now,  # Will be updated when node execution completes
            record_info={},
        )
        self.session.add(node_execution)
        await self.session.flush()


class WorkflowDebugExecutor(WorkflowExecutorBase):
    """Executor for workflow debugging."""

    def __init__(self, workflow: Workflow, snapshot: WorkflowSnapshot, session: AsyncSession):
        super().__init__(workflow, session)
        self.snapshot = snapshot
        self.debug_execution_id: Optional[UUID] = None

    async def _create_execution_record(self) -> None:
        """Create debug execution record."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        debug_execution = WorkflowDebugExecution(
            workflow_id=self.workflow.id,
            snapshot_timestamp=self.snapshot.snapshot_timestamp,
            flow_run_id=self.flow_run_id,
            status=StateType.PENDING,
            created_by=self.snapshot.created_by,
            start_time=now,
            end_time=now,  # Will be updated when execution completes
            record_info={},
        )
        self.session.add(debug_execution)
        await self.session.flush()
        self.debug_execution_id = debug_execution.id

    async def _create_node_execution_record(self, node: WorkflowNode, task_run_id: UUID) -> None:
        """Create debug node execution record."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        node_execution = WorkflowNodeDebugExecution(
            execution_id=self.debug_execution_id,
            node_key=node.node_key,
            flow_run_id=self.flow_run_id,
            task_run_id=task_run_id,
            status=StateType.PENDING,
            start_time=now,
            end_time=now,  # Will be updated when node execution completes
            record_info={},
        )
        self.session.add(node_execution)
        await self.session.flush()


class WorkflowExecutorFactory:
    """Factory for creating appropriate workflow executors."""

    @staticmethod
    async def create_executor(
        session: AsyncSession,
        workflow_id: UUID,
        version: Optional[str] = None,
        snapshot_timestamp: Optional[datetime] = None,
    ) -> WorkflowExecutorBase:
        """Create appropriate workflow executor based on parameters."""
        # Get workflow
        workflow_result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = workflow_result.scalar_one_or_none()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        if version:
            # Version execution
            return WorkflowVersionExecutor(workflow, version, session)
        elif snapshot_timestamp:
            # Debug execution
            snapshot_result = await session.execute(
                select(WorkflowSnapshot).where(
                    WorkflowSnapshot.workflow_id == workflow_id,
                    WorkflowSnapshot.snapshot_timestamp == snapshot_timestamp,
                )
            )
            snapshot = snapshot_result.scalar_one_or_none()
            if not snapshot:
                raise ValueError(f"Workflow snapshot not found for timestamp {snapshot_timestamp}")
            return WorkflowDebugExecutor(workflow, snapshot, session)
        else:
            raise ValueError("Either version or snapshot_timestamp must be provided")
