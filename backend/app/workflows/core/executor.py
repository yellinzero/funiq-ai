from datetime import datetime, timezone
from typing import Any, Dict, Optional

import networkx as nx
from loguru import logger
from prefect import flow, task
from prefect.client.schemas.objects import StateType
from prefect.logging import get_run_logger
from prefect.runtime import flow_run, task_run
from prefect.task_runners import ThreadPoolTaskRunner
from redis.asyncio import Redis
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.workflow import (
    WorkflowDebugExecution,
    WorkflowExecution,
    WorkflowNodeDebugExecution,
    WorkflowNodeExecution,
)
from infrastructure import with_redis, with_session
from providers.operators.core import OperatorFactory, OperatorName
from utils.common.json import json_dumps, json_loads


class WorkflowExecutorBase:
    """Base class for workflow execution."""

    def __init__(
        self,
        workflow_id: str,
        snapshot: Dict[str, Any],
        snapshot_hash: str,
        input_data: Dict[str, Any],
        execution_context: Dict[str, Any],
        cached_expiration: int = 24 * 60 * 60,
    ):
        self.workflow_id = workflow_id
        self.snapshot = snapshot
        self.workflow_name = self.snapshot.get("name")
        self.is_stream = self.snapshot.get("stream_mode", False)
        self.snapshot_hash = snapshot_hash
        self.input_data = input_data
        self.execution_context = execution_context
        self.graph = None
        self.node_levels = None
        self.flow_run_id: Optional[str] = None
        self.node_outputs = {}
        self.cached_expiration = cached_expiration
        self.execution_id: Optional[str] = None
        self.snapshot_timestamp = None
        self.version = None
        self.cached_key = f"workflow:{self.workflow_id}:topology:{self.snapshot_hash}"
        logger.info(f"Initializing WorkflowExecutor for workflow: {self.workflow_name}")

    @with_redis
    async def _get_cached_topology(self, redis: Redis) -> Optional[tuple[Dict[str, list[str]], Dict[str, int]]]:
        """Get cached topology from redis."""
        cached_data = await redis.get(self.cached_key)
        if cached_data:
            data = json_loads(cached_data)
            return data["adjacency"], data["levels"], data["end_node_key"]
        return None

    @with_redis
    async def _cache_topology(
        self, redis: Redis, adjacency: Dict[str, list[str]], levels: Dict[str, int], end_node_key: str
    ) -> None:
        """Cache topology to redis."""
        data = {
            "adjacency": adjacency,  # store node's upstream and downstream nodes
            "levels": levels,
            "end_node_key": end_node_key,
        }
        await redis.setex(self.cached_key, self.cached_expiration, json_dumps(data))

    async def _build_topology(self, snapshot: Dict[str, Any]) -> None:
        """Build workflow topology."""
        # try to get topology from cache
        cached_data = await self._get_cached_topology()
        if cached_data:
            self.adjacency, self.node_levels, self.end_node_key = cached_data
            return

        # build new topology
        g = nx.DiGraph()

        # Find END node while building graph
        self.end_node_key = None
        nodes = snapshot.get("nodes", [])
        for node in nodes:
            g.add_node(node.get("node_key"))
            if node.get("node_type") == OperatorName.END:
                self.end_node_key = node.get("node_key")

        if not self.end_node_key:
            raise ValueError("Workflow must have an END node")

        edges = snapshot.get("edges", [])
        for edge in edges:
            g.add_edge(edge.get("source_node_key"), edge.get("target_node_key"))

        self.node_levels = self._calculate_node_levels(g)

        self.adjacency = {
            node: {"upstream": list(g.predecessors(node)), "downstream": list(g.successors(node))} for node in g.nodes()
        }

        # Cache all topology information
        await self._cache_topology(adjacency=self.adjacency, levels=self.node_levels, end_node_key=self.end_node_key)

    def _calculate_node_levels(self, g: nx.DiGraph) -> list[list[str]]:
        """Calculate topology levels of nodes using networkx's built-in function."""
        # check if the graph is a DAG
        if not nx.is_directed_acyclic_graph(g):
            raise ValueError("Workflow graph must be acyclic")

        # get node levels using networkx's topological_generations
        levels = [list(nodes) for nodes in nx.topological_generations(g)]
        return levels

    def _get_upstream_outputs(self, node_key: str) -> Dict[str, Any]:
        """Get outputs from upstream nodes using adjacency list."""
        prefect_logger = get_run_logger()
        upstream_outputs = {}

        # Get upstream nodes directly from adjacency list
        upstream_nodes = self.adjacency[node_key]["upstream"]
        for upstream_node in upstream_nodes:
            if upstream_node in self.node_outputs:
                upstream_outputs[upstream_node] = self.node_outputs[upstream_node]

        return upstream_outputs

    @with_session
    async def _create_execution_record(self, session: AsyncSession) -> None:
        """Create execution record in database."""
        raise NotImplementedError

    @with_session
    async def _update_execution_status(self, session: AsyncSession, status: StateType) -> None:
        """Update execution status in database."""
        raise NotImplementedError

    @with_session
    async def _create_node_execution_record(
        self, session: AsyncSession, node: Dict[str, Any], task_run_id: str
    ) -> None:
        """Create node execution record in database."""
        raise NotImplementedError

    @with_session
    async def _update_node_execution_status(
        self, session: AsyncSession, node_key: str, task_run_id: str, status: StateType
    ) -> None:
        """Update node execution status in database."""
        raise NotImplementedError

    def _create_task_for_node(self, node: Dict[str, Any]) -> task:
        """Create a Prefect task for a workflow node."""
        node_name = node.get("name")
        node_type = node.get("node_type")
        node_key = node.get("node_key")

        @task(
            name=node_name,
            timeout_seconds=5 * 60,
            tags=[node_type],
        )
        async def node_task(**kwargs):
            task_run_id = task_run.get_id()

            # Create node execution record
            await self._create_node_execution_record(node=node, task_run_id=task_run_id)

            try:
                # Update status to running
                await self._update_node_execution_status(
                    node_key=node_key, task_run_id=task_run_id, status=StateType.RUNNING
                )

                config = node.get("config", {})
                upstream_outputs = self._get_upstream_outputs(node_key)

                operator = OperatorFactory.get_operator_instance(node_type)
                if not operator:
                    raise ValueError(f"No operator found for type: {node_type}")

                input_data = {
                    **self.input_data,
                    **upstream_outputs,
                }

                result = await operator.execute(
                    input_data=input_data,
                    config=config,
                    execution_context={
                        "execution_id": self.execution_id,
                        "flow_run_id": self.flow_run_id,
                        "task_run_id": task_run_id,
                        "node_key": node_key,
                        "version": self.version,
                        "snapshot_timestamp": self.snapshot_timestamp,
                        **self.execution_context,
                    },
                )

                self.node_outputs[node_key] = result

                # Update status to completed
                await self._update_node_execution_status(
                    node_key=node_key, task_run_id=task_run_id, status=StateType.COMPLETED
                )
                return result

            except Exception as e:
                # Update status to failed
                await self._update_node_execution_status(
                    node_key=node_key, task_run_id=task_run_id, status=StateType.FAILED
                )
                raise

        return node_task

    async def initialize(self):
        """Initialize the executor by building the topology."""
        logger.info(f"Starting initialization for workflow: {self.workflow_name}")
        await self._build_topology(self.snapshot)

    def _create_flow(self):
        """Create a normal Prefect flow for non-streaming workflow."""

        @flow(name=self.workflow_name, task_runner=ThreadPoolTaskRunner(max_workers=10))
        async def workflow_flow():
            self.flow_run_id = flow_run.get_id()
            try:
                await self._create_execution_record()
                await self._update_execution_status(status=StateType.RUNNING)

                task_futures = {}
                for level_nodes in self.node_levels:
                    for node_key in level_nodes:
                        nodes = self.snapshot.get("nodes", [])
                        node = next(n for n in nodes if n.get("node_key") == node_key)

                        upstream_futures = []
                        for source, targets in self.adjacency.items():
                            if node_key in targets["downstream"]:
                                upstream_futures.append(task_futures[source])

                        task = self._create_task_for_node(node)
                        future = task.submit(wait_for=upstream_futures)
                        task_futures[node_key] = future

                result = task_futures[self.end_node_key].result()
                await self._update_execution_status(status=StateType.COMPLETED)
                return result

            except Exception as e:
                logger.error(f"Workflow execution failed: {e!s}")
                await self._update_execution_status(status=StateType.FAILED)
                raise

        return workflow_flow

    async def execute(self):
        """Execute the workflow."""
        if self.is_stream:
            raise ValueError(
                f"Workflow '{self.workflow_name}' is configured for streaming execution. "
                "Please use the appropriate stream executor (WorkflowVersionStreamExecutor "
                "or WorkflowDebugStreamExecutor) instead."
            )
        flow = self._create_flow()

        return await flow()


class WorkflowVersionExecutor(WorkflowExecutorBase):
    """Executor for published workflow versions."""

    def __init__(
        self,
        workflow_id: str,
        version: str,
        snapshot: Dict[str, Any],
        snapshot_hash: str,
        input_data: Dict[str, Any],
        execution_context: Dict[str, Any],
    ):
        super().__init__(
            workflow_id=workflow_id,
            snapshot=snapshot,
            snapshot_hash=snapshot_hash,
            input_data=input_data,
            execution_context=execution_context,
        )
        self.version = version
        self.execution_id: Optional[str] = None

    @with_session
    async def _create_execution_record(self, session: AsyncSession) -> None:
        """Create workflow execution record."""
        execution = WorkflowExecution(
            workflow_id=self.workflow_id,
            version=self.version,
            flow_run_id=self.flow_run_id,
            status=StateType.PENDING,
            record_info={},
            created_by=self.execution_context.get("user_id"),
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        session.add(execution)
        await session.flush()
        await session.commit()
        self.execution_id = execution.id

    @with_session
    async def _update_execution_status(self, session: AsyncSession, status: StateType) -> None:
        """Update execution status in database."""
        if not self.execution_id:
            raise ValueError("Execution record not created")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        update_values = {"status": status}

        if status == StateType.RUNNING:
            update_values["start_time"] = now
        elif status in (StateType.COMPLETED, StateType.FAILED):
            update_values["end_time"] = now

        stmt = update(WorkflowExecution).where(WorkflowExecution.id == self.execution_id).values(**update_values)
        await session.execute(stmt)
        await session.flush()
        await session.commit()

    @with_session
    async def _create_node_execution_record(
        self, session: AsyncSession, node: Dict[str, Any], task_run_id: str
    ) -> None:
        """Create node execution record."""
        node_execution = WorkflowNodeExecution(
            execution_id=self.execution_id,
            node_key=node.get("node_key"),
            flow_run_id=self.flow_run_id,
            task_run_id=task_run_id,
            status=StateType.PENDING,
            record_info={},
            created_by=self.execution_context.get("user_id"),
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        session.add(node_execution)
        await session.flush()
        await session.commit()

    @with_session
    async def _update_node_execution_status(
        self, session: AsyncSession, node_key: str, task_run_id: str, status: StateType
    ) -> None:
        """Update node execution status in database."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        update_values = {"status": status}

        if status == StateType.RUNNING:
            update_values["start_time"] = now
        elif status in (StateType.COMPLETED, StateType.FAILED):
            update_values["end_time"] = now

        stmt = (
            update(WorkflowNodeExecution)
            .where(
                WorkflowNodeExecution.execution_id == self.execution_id,
                WorkflowNodeExecution.node_key == node_key,
                WorkflowNodeExecution.task_run_id == task_run_id,
            )
            .values(**update_values)
        )
        await session.execute(stmt)
        await session.flush()
        await session.commit()


class WorkflowDebugExecutor(WorkflowExecutorBase):
    """Executor for workflow debugging."""

    def __init__(
        self,
        workflow_id: str,
        snapshot: Dict[str, Any],
        snapshot_timestamp: datetime,
        snapshot_hash: str,
        input_data: Dict[str, Any],
        execution_context: Dict[str, Any],
    ):
        super().__init__(
            workflow_id=workflow_id,
            snapshot=snapshot,
            snapshot_hash=snapshot_hash,
            input_data=input_data,
            execution_context=execution_context,
        )
        self.snapshot_timestamp = snapshot_timestamp
        self.debug_execution_id: Optional[str] = None

    @with_session
    async def _create_execution_record(self, session: AsyncSession) -> None:
        """Create debug execution record."""
        debug_execution = WorkflowDebugExecution(
            workflow_id=self.workflow_id,
            snapshot_timestamp=self.snapshot_timestamp,
            flow_run_id=self.flow_run_id,
            status=StateType.PENDING,
            created_by=self.execution_context.get("user_id"),
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            record_info={},
        )
        session.add(debug_execution)
        await session.flush()
        await session.commit()
        self.debug_execution_id = debug_execution.id

    @with_session
    async def _update_execution_status(self, session: AsyncSession, status: StateType) -> None:
        """Update execution status in database."""
        if not self.debug_execution_id:
            raise ValueError("Debug execution record not created")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        update_values = {"status": status}

        if status == StateType.RUNNING:
            update_values["start_time"] = now
        elif status in (StateType.COMPLETED, StateType.FAILED):
            update_values["end_time"] = now
        stmt = (
            update(WorkflowDebugExecution)
            .where(WorkflowDebugExecution.id == self.debug_execution_id)
            .values(**update_values)
        )
        await session.execute(stmt)
        await session.flush()
        await session.commit()

    @with_session
    async def _create_node_execution_record(
        self, session: AsyncSession, node: Dict[str, Any], task_run_id: str
    ) -> None:
        """Create debug node execution record."""
        node_execution = WorkflowNodeDebugExecution(
            execution_id=self.debug_execution_id,
            node_key=node.get("node_key"),
            flow_run_id=self.flow_run_id,
            task_run_id=task_run_id,
            status=StateType.PENDING,
            record_info={},
            created_by=self.execution_context.get("user_id"),
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        session.add(node_execution)
        await session.flush()
        await session.commit()

    @with_session
    async def _update_node_execution_status(
        self, session: AsyncSession, node_key: str, task_run_id: str, status: StateType
    ) -> None:
        """Update node execution status in database."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        update_values = {"status": status}

        if status == StateType.RUNNING:
            update_values["start_time"] = now
        elif status in (StateType.COMPLETED, StateType.FAILED):
            update_values["end_time"] = now
        stmt = (
            update(WorkflowNodeDebugExecution)
            .where(
                WorkflowNodeDebugExecution.execution_id == self.debug_execution_id,
                WorkflowNodeDebugExecution.node_key == node_key,
                WorkflowNodeDebugExecution.task_run_id == task_run_id,
            )
            .values(**update_values)
        )
        await session.execute(stmt)
        await session.flush()
        await session.commit()
