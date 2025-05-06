from typing import Any, Dict, List

import networkx as nx
from loguru import logger
from redis.asyncio import Redis

from infrastructure import with_redis
from utils.common.json import json_loads

from .schemas import TopologyCacheContext, TopologyData, WorkflowContext


class WorkflowTopologyMixin:
    """Mixin for workflow topology management.

    This mixin provides functionality for building, caching, and managing workflow topology,
    including DAG (Directed Acyclic Graph) construction and node level calculation.
    """

    _context: WorkflowContext

    def _generate_cached_key(self, workflow_id: str, snapshot_hash: str) -> str:
        """Generate a unique cache key for the workflow topology.

        Args:
            workflow_id (str): ID of the workflow
            snapshot_hash (str): Hash of the workflow snapshot

        Returns:
            str: Unique cache key for the workflow topology
        """
        return f"workflow:{workflow_id}:topology:{snapshot_hash}"

    @with_redis
    async def _get_cached_topology(self, redis: Redis, cached_key: str) -> TopologyData:
        """Retrieve cached topology information from Redis.

        Args:
            redis (Redis): Redis client for cache operations
            cached_key (str): Key for retrieving cached topology

        Returns:
            WorkflowTopology: Cached topology information if exists, None otherwise
        """
        try:
            cached_data = await redis.get(cached_key)
            if cached_data:
                data = json_loads(cached_data)
                return TopologyData(**data)
        except Exception as e:
            logger.error(f"Error getting cached topology for {cached_key}: {e}")
        return None

    @with_redis
    async def _cache_topology(self, redis: Redis, topology_data: TopologyData, cache_context: TopologyCacheContext):
        """Cache workflow topology information in Redis.

        Args:
            redis (Redis): Redis client for cache operations
            topology_info (WorkflowTopology): Topology information to be cached
            cached_key (str): Key for storing topology in cache
            cached_expiration (int): Cache expiration time in seconds

        Returns:
            WorkflowTopology: Cached topology information
        """
        try:
            await redis.setex(
                cache_context.cached_key, cache_context.cached_expiration, topology_data.model_dump_json()
            )
            return topology_data
        except Exception as e:
            logger.error(f"Error caching topology for {cache_context.cached_key}: {e}")
            raise e

    async def _build_topology(self, cache_context: TopologyCacheContext, snapshot: Dict[str, Any]):
        """Build workflow topology from snapshot.

        This method performs the following:
        1. Attempts to retrieve topology from cache
        2. If not found, constructs new topology using networkx
        3. Identifies the END node
        4. Builds node adjacency and levels
        5. Caches the result

        Args:
            cached_key (str): Key for topology caching
            cached_expiration (int): Cache expiration time in seconds
            snapshot (Dict[str, Any]): Workflow definition containing nodes and edges

        Returns:
            WorkflowTopology: Complete topology information

        Raises:
            ValueError: If workflow does not contain an END node or contains cycles
        """

        try:
            # Try to get topology from cache
            cached_data = await self._get_cached_topology(
                cached_key=cache_context.cached_key,
            )
            if cached_data:
                return cached_data

            topology_data = TopologyData(
                adjacency={},
                node_levels=[],
            )

            # Build new topology
            g = nx.DiGraph()
            # Find END node while building graph
            nodes = snapshot.get("nodes", [])
            for node in nodes:
                node_key = node.get("node_key")
                g.add_node(node_key)

            edges = snapshot.get("edges", [])
            for edge in edges:
                source_node_key = edge.get("source_node_key")
                target_node_key = edge.get("target_node_key")
                g.add_edge(source_node_key, target_node_key)

            topology_data.node_levels = self._calculate_node_levels(g)

            topology_data.adjacency = {
                node: {"upstream": list(g.predecessors(node)), "downstream": list(g.successors(node))}
                for node in g.nodes()
            }

            # Cache all topology information
            return await self._cache_topology(
                topology_data=topology_data,
                cache_context=cache_context,
            )

        except Exception as e:
            logger.error(f"Error building topology for {self._context.workflow_id}: {e}")
            raise e

    def _calculate_node_levels(self, g: nx.DiGraph) -> List[List[str]]:
        """Calculate execution levels for workflow nodes.

        This method performs topological sorting to organize nodes into levels,
        where nodes in the same level can be executed in parallel.

        Args:
            g (nx.DiGraph): Directed graph representing the workflow

        Returns:
            List[List[str]]: List of levels, where each level contains node keys
                           that can be executed in parallel

        Raises:
            ValueError: If the graph contains cycles (not a DAG)
        """
        # Verify the graph is acyclic
        if not nx.is_directed_acyclic_graph(g):
            raise ValueError("Workflow graph must be acyclic")

        # Get node levels using networkx's topological_generations
        levels = [list(nodes) for nodes in nx.topological_generations(g)]
        return levels
