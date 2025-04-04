from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.account import Account
from app.core.models.workflow import (
    Workflow,
    WorkflowEdge,
    WorkflowNode,
    WorkflowNodeType,
    WorkflowStatus,
    WorkflowVersion,
    WorkflowVersionStatus,
)
from app.workflows.core.executor import WorkflowVersionExecutor


class WorkflowService:
    @staticmethod
    async def create_system_workflow(
        session: AsyncSession, model_id: str, app_id: str, name: str, description: str
    ) -> Workflow:
        """Create a workflow for an app."""
        system_account = await Account.get_system_account(session)
        workflow = Workflow(
            app_id=app_id,
            name=name,
            description=description,
            status=WorkflowStatus.PUBLISHED,
            version="1.0.0",
            created_by=system_account.id,
            updated_by=system_account.id,
        )
        workflow.save(session)
        await session.flush()  # Flush to get workflow.id

        # Create workflow version
        workflow_version = WorkflowVersion(
            workflow_id=workflow.id,
            version="1.0.0",
            status=WorkflowVersionStatus.ACTIVE,
            description="Initial system workflow version",
            published_at=datetime.now(timezone.utc).replace(tzinfo=None),
            published_by=system_account.id,
            snapshot=workflow.snapshot,
        )
        workflow_version.save(session)

        # Create nodes
        nodes = {
            "start": WorkflowNode(
                workflow_id=workflow.id,
                node_key="start",
                node_type=WorkflowNodeType.START,
                name="Start",
                config={},
                created_by=system_account.id,
                updated_by=system_account.id,
            ),
            "llm": WorkflowNode(
                workflow_id=workflow.id,
                node_key="llm",
                node_type=WorkflowNodeType.LLM,
                name="LLM",
                config={"model_id": str(model_id), "prompt": None},
                created_by=system_account.id,
                updated_by=system_account.id,
            ),
            "end": WorkflowNode(
                workflow_id=workflow.id,
                node_key="end",
                node_type=WorkflowNodeType.END,
                name="End",
                config={},
                created_by=system_account.id,
                updated_by=system_account.id,
            ),
        }

        for node in nodes.values():
            node.save(session)

        # Create edges
        edges = [
            WorkflowEdge(
                workflow_id=workflow.id,
                edge_key="start_to_llm",
                source_node_key="start",
                target_node_key="llm",
                created_by=system_account.id,
                updated_by=system_account.id,
            ),
            WorkflowEdge(
                workflow_id=workflow.id,
                edge_key="llm_to_end",
                source_node_key="llm",
                target_node_key="end",
                created_by=system_account.id,
                updated_by=system_account.id,
            ),
        ]

        for edge in edges:
            edge.save(session)

        return workflow

    @staticmethod
    async def execute_workflow(
        session: AsyncSession, workflow_id: str, version: str, initial_inputs: Dict[str, Any]
    ) -> str:
        """Execute a workflow with the given inputs."""
        # Get the workflow
        
        workflow_result = await session.execute(
            select(WorkflowVersion).where(
                WorkflowVersion.workflow_id == workflow_id,
                WorkflowVersion.version == version,
            )
        )
        workflow = workflow_result.scalar_one_or_none()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Create and initialize the executor
        executor = WorkflowVersionExecutor(workflow)
        await executor.initialize(session)

        # Execute the workflow
        return executor.execute(initial_inputs)
