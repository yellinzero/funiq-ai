import asyncio
from typing import Any, Dict

import networkx as nx
from loguru import logger
from prefect import flow, task
from prefect.utilities.asyncutils import sync_compatible
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow, WorkflowEdge, WorkflowNode
from providers.operators.core.operator_factory import OperatorFactory


# TODO implement correct workflow service
class WorkflowService:
    """Service for executing workflows using Prefect v3 and NetworkX."""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.workflow = None
        self.graph = None
        self.node_levels = None
        self.task_registry: Dict[str, task] = {}
        logger.info(f"Initializing WorkflowService for workflow_id: {workflow_id}")
        
    async def initialize(self, session: AsyncSession):
        """Initialize the workflow service by building the graph and calculating node levels."""
        logger.info(f"Starting initialization for workflow: {self.workflow_id}")
        
        # Fetch workflow from database
        workflow_result = await session.execute(
            select(Workflow).where(Workflow.id == self.workflow_id)
        )
        self.workflow = workflow_result.scalar_one_or_none()
        if not self.workflow:
            logger.error(f"Workflow {self.workflow_id} not found")
            raise ValueError(f"Workflow {self.workflow_id} not found")
            
        logger.info(f"Found workflow: {self.workflow.name} (ID: {self.workflow_id})")
        self.graph = await self._build_graph(session)
        self.node_levels = self._calculate_node_levels()
        logger.debug(f"Node levels calculated: {self.node_levels}")
        
    async def _build_graph(self, session: AsyncSession) -> nx.DiGraph:
        """Build a NetworkX directed graph from workflow nodes and edges."""
        logger.debug(f"Building graph for workflow: {self.workflow_id}")
        g = nx.DiGraph()
        
        # Query nodes using the session
        nodes_result = await session.execute(
            select(WorkflowNode).where(WorkflowNode.workflow_id == self.workflow.id)
        )
        nodes = nodes_result.scalars().all()
        logger.debug(f"Found {len(nodes)} nodes")
        
        # Query edges using the session
        edges_result = await session.execute(
            select(WorkflowEdge).where(WorkflowEdge.workflow_id == self.workflow.id)
        )
        edges = edges_result.scalars().all()
        logger.debug(f"Found {len(edges)} edges")
        
        # Add nodes and edges
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
            raise ValueError("Workflow graph must have at least one source node (node with no incoming edges)")
        
        for node in self.graph.nodes():
            # Use longest path from any source node to this node
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
        upstream_outputs = {}
        for edge in self.graph.edges(data=True):
            if edge[1] == node_key:  # If this edge points to our node
                source_key = edge[0]
                if source_key in current_inputs:
                    upstream_outputs[source_key] = current_inputs[source_key]
        logger.debug(f"Node {node_key} upstream outputs: {upstream_outputs.keys()}")
        return upstream_outputs
    
    def _create_task_for_node(self, node: WorkflowNode) -> task:
        """Create a Prefect task for a workflow node."""
        logger.debug(f"Creating task for node: {node.name} (type: {node.node_type})")
        
        @task(name=node.name)
        def node_task(**kwargs):
            logger.info(f"Executing node: {node.name} (type: {node.node_type})")
            # Get the node's configuration and upstream outputs
            config = node.config or {}
            upstream_outputs = self._get_upstream_outputs(node.node_key, kwargs)
            
            # Get operator instance using factory
            operator = OperatorFactory.get_operator_instance(node.node_type)
            if not operator:
                logger.error(f"No operator found for type: {node.node_type}")
                raise ValueError(f"No operator found for type: {node.node_type}")
            
            # Execute the operator with config and upstream outputs
            logger.debug(f"Executing operator for node {node.name} with config: {config}")
            result = operator.execute(input_data=upstream_outputs, config=config)
            logger.debug(f"Node {node.name} execution completed")
            return result
                
        return node_task
    
    @sync_compatible
    async def _execute_level(self, level: int, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all tasks at a specific level in parallel."""
        level_nodes = [node for node, lvl in self.node_levels.items() if lvl == level]
        logger.info(f"Executing level {level} with {len(level_nodes)} nodes")
        logger.debug(f"Level {level} nodes: {level_nodes}")
        
        tasks = []
        for node_key in level_nodes:
            node = self.graph.nodes[node_key]["node"]
            if node_key not in self.task_registry:
                self.task_registry[node_key] = self._create_task_for_node(node)
            
            task = self.task_registry[node_key]
            tasks.append(task(**inputs))
        
        # Execute all tasks at this level in parallel
        results = await asyncio.gather(*tasks)
        result_dict = dict(zip(level_nodes, results))
        logger.debug(f"Level {level} execution completed with results: {result_dict}")
        return result_dict
    
    async def execute(self, initial_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow using Prefect v3 flows."""
        logger.info(f"Starting workflow execution: {self.workflow.name}")
        logger.debug(f"Initial inputs: {initial_inputs}")
        
        @flow(name=f"workflow_{self.workflow.name}")
        async def _execute_flow():
            max_level = max(self.node_levels.values())
            logger.info(f"Workflow has {max_level + 1} levels")
            current_inputs = initial_inputs
            
            for level in range(max_level + 1):
                level_results = await self._execute_level(level, current_inputs)
                current_inputs.update(level_results)
                
            logger.info(f"Workflow {self.workflow.name} execution completed")
            return current_inputs
            
        return await _execute_flow() 