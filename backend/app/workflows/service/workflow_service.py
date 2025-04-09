import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import status
from loguru import logger
from nanoid import generate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import WorkflowErrorCode
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
from tasks.workflow_tasks import execute_workflow as celery_execute_workflow
from utils.common.json import json_dumps


def generate_node_or_edge_key() -> str:
    """
    Generate a unique key for a node or edge.
    The key will start with a letter and be followed by alphanumeric characters.
    """
    # Separate letters and numbers for first character and rest
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    alphanumeric = "0123456789" + letters

    # Generate first character (letter only) and rest of the key
    first_char = generate(alphabet=letters, size=1)
    rest_of_key = generate(alphabet=alphanumeric, size=9)

    return first_char + rest_of_key


def serialize_workflow_node(node: WorkflowNode) -> dict[str, Any]:
    return {
            **node.to_dict(),
            "workflow_id": str(node.workflow_id),
            "created_by": str(node.created_by),
            "updated_by": str(node.updated_by),
        }


def serialize_workflow_edge(edge: WorkflowEdge) -> dict[str, Any]:
    return {
        **edge.to_dict(),
        "workflow_id": str(edge.workflow_id),
        "created_by": str(edge.created_by),
        "updated_by": str(edge.updated_by),
    }


class WorkflowService:
    @staticmethod
    async def _create_system_workflow_nodes(
        session: AsyncSession, workflow_id: str, model_id: str, created_by: str
    ) -> list[WorkflowNode]:
        """
        Internal method to create default system workflow nodes.

        Args:
            session: Database session
            workflow_id: ID of the workflow
            model_id: ID of the LLM model to use
            created_by: ID of the user creating the nodes

        Returns:
            list: List of WorkflowNode objects in execution order
        """
        # Generate unique keys for nodes
        start_key = generate_node_or_edge_key()
        llm_key = generate_node_or_edge_key()
        end_key = generate_node_or_edge_key()

        # Define nodes in execution order
        nodes = [
            WorkflowNode(
                workflow_id=workflow_id,
                node_key=start_key,
                node_type=WorkflowNodeType.START,
                name="Start",
                config={
                    "question": "{{question}}",
                },
                created_by=created_by,
                updated_by=created_by,
            ),
            WorkflowNode(
                workflow_id=workflow_id,
                node_key=llm_key,
                node_type=WorkflowNodeType.LLM,
                name="LLM",
                config={
                    "model_id": str(model_id),
                    "prompt": f"{{{{{start_key}.question}}}}",
                },
                created_by=created_by,
                updated_by=created_by,
            ),
            WorkflowNode(
                workflow_id=workflow_id,
                node_key=end_key,
                node_type=WorkflowNodeType.END,
                name="End",
                config={"result": f"{{{{{llm_key}.answer}}}}"},
                created_by=created_by,
                updated_by=created_by,
            ),
        ]

        # Save all nodes to database
        for node in nodes:
            await node.save(session)

        return nodes

    @staticmethod
    async def _create_system_workflow_edges(
        session: AsyncSession, workflow_id: str, nodes: list[WorkflowNode], created_by: str
    ) -> list[WorkflowEdge]:
        """
        Internal method to create default system workflow edges.

        Args:
            session: Database session
            workflow_id: ID of the workflow
            nodes: List of nodes in execution order
            created_by: ID of the user creating the edges

        Returns:
            list: List of created WorkflowEdge objects
        """
        # Create edges connecting nodes in sequence
        edges = [
            WorkflowEdge(
                workflow_id=workflow_id,
                edge_key=generate_node_or_edge_key(),
                source_node_key=nodes[0].node_key,  # Start -> LLM
                target_node_key=nodes[1].node_key,
                created_by=created_by,
                updated_by=created_by,
            ),
            WorkflowEdge(
                workflow_id=workflow_id,
                edge_key=generate_node_or_edge_key(),
                source_node_key=nodes[1].node_key,  # LLM -> End
                target_node_key=nodes[2].node_key,
                created_by=created_by,
                updated_by=created_by,
            ),
        ]

        # Save all edges to database
        for edge in edges:
            await edge.save(session)

        return edges

    @staticmethod
    async def create_system_workflow(
        session: AsyncSession, model_id: str, app_id: str, name: str, description: str
    ) -> Workflow:
        """
        Create a system workflow with default nodes and edges.

        Args:
            session: Database session
            model_id: ID of the LLM model to use
            app_id: ID of the app this workflow belongs to
            name: Name of the workflow
            description: Description of the workflow

        Returns:
            Workflow: Created workflow object

        Raises:
            WorkflowErrorCode.WORKFLOW_CREATE_ERROR: If creation fails
        """
        try:
            # Get system account for attribution
            system_account = await Account.get_system_account(session)

            # Create base workflow
            workflow = Workflow(
                app_id=app_id,
                name=name,
                description=description,
                status=WorkflowStatus.PUBLISHED,
                version="1.0.0",
                created_by=system_account.id,
                updated_by=system_account.id,
            )
            await workflow.save(session)

            # Create system workflow nodes and edges
            nodes = await WorkflowService._create_system_workflow_nodes(
                session, str(workflow.id), model_id, str(system_account.id)
            )

            await WorkflowService._create_system_workflow_edges(
                session, str(workflow.id), nodes, str(system_account.id)
            )

            # Publish initial workflow version
            await WorkflowService.publish_workflow(
                session,
                str(workflow.id),
                version="1.0.0",
                description="Initial system workflow version",
                published_by=str(system_account.id),
            )

            return workflow

        except Exception as e:
            # Log error and rollback all changes if any step fails
            logger.error(f"Error creating system workflow: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_CREATE_ERROR.exception(
                data={
                    "app_id": str(app_id),
                    "name": name,
                    "error": str(e),
                    "message": "Failed to create system workflow",
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    @staticmethod
    async def execute_workflow_async(
        session: AsyncSession,
        workflow_id: str,
        input_data: Dict[str, Any],
        execution_context: Dict[str, Any],
        version: Optional[str] = None,
        snapshot_timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Execute a workflow asynchronously using Celery."""
        # Validate workflow exists
        result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise WorkflowErrorCode.WORKFLOW_NOT_FOUND.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "message": "Workflow not found"
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Validate version if specified
        if version:
            version_result = await session.execute(
                select(WorkflowVersion).where(
                    WorkflowVersion.workflow_id == workflow_id,
                    WorkflowVersion.version == version
                )
            )
            workflow_version = version_result.scalar_one_or_none()
            if not workflow_version:
                raise WorkflowErrorCode.WORKFLOW_VERSION_NOT_FOUND.exception(
                    data={
                        "workflow_id": str(workflow_id),
                        "version": version,
                        "message": "Specified version not found"
                    },
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            if workflow_version.status != WorkflowVersionStatus.ACTIVE:
                raise WorkflowErrorCode.WORKFLOW_VERSION_NOT_ACTIVE.exception(
                    data={
                        "workflow_id": str(workflow_id),
                        "version": version,
                        "status": workflow_version.status,
                        "message": "Specified version is not active"
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        # Start async task
        try:
            task = celery_execute_workflow.delay(
                workflow_id=workflow_id,
                input_data=input_data,
                execution_context=execution_context,
                version=version,
                snapshot_timestamp=snapshot_timestamp,
            )
        except Exception as e:
            raise WorkflowErrorCode.WORKFLOW_EXECUTION_ERROR.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "error": str(e),
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

        logger.info(f"Started async workflow execution: {task.id}")
        return {"task_id": task.id}

    @staticmethod
    def execute_workflow_sync(
        session: AsyncSession,
        workflow_id: str,
        input_data: Dict[str, Any],
        execution_context: Dict[str, Any],
        version: Optional[str] = None,
        snapshot_timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Execute a workflow synchronously using Celery."""
        # Start task
        try:
            task = celery_execute_workflow.delay(
                workflow_id=workflow_id,
                input_data=input_data,
                execution_context=execution_context,
                version=version,
                snapshot_timestamp=snapshot_timestamp,
            )
        except Exception as e:
            raise WorkflowErrorCode.WORKFLOW_EXECUTION_ERROR.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "error": str(e),
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

        logger.info(f"Started sync workflow execution: {task.id}")
        
        try:
            result = task.get(timeout=600)  # 10 minutes timeout
            return result
        except TimeoutError as e:
            raise WorkflowErrorCode.WORKFLOW_TASK_TIMEOUT.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "task_id": task.id,
                    "message": "Task execution timed out after 10 minutes"
                },
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            ) from e
        except Exception as task_error:
            error_message = str(task_error)
            raise WorkflowErrorCode.WORKFLOW_EXECUTION_ERROR.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "task_id": task.id,
                    "error": error_message,
                    "message": "Workflow execution failed"
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from task_error
            
    @staticmethod
    async def get_workflow_snapshot(session: AsyncSession, workflow_id: str) -> dict[str, Any]:
        """Get the snapshot of the workflow asynchronously."""
        # Fetch workflow and validate existence
        result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise WorkflowErrorCode.WORKFLOW_NOT_FOUND.exception(
                data={"workflow_id": str(workflow_id), "message": "Workflow not found for snapshot creation"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Fetch workflow nodes
        nodes_result = await session.execute(select(WorkflowNode).where(WorkflowNode.workflow_id == workflow_id))
        nodes = nodes_result.scalars().all()

        # Fetch workflow edges
        edges_result = await session.execute(select(WorkflowEdge).where(WorkflowEdge.workflow_id == workflow_id))
        edges = edges_result.scalars().all()

        # Validate workflow structure
        if not nodes:
            raise WorkflowErrorCode.INVALID_WORKFLOW.exception(
                data={"workflow_id": str(workflow_id), "message": "Workflow has no nodes"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        snapshot = {
            "name": workflow.name,
            "description": workflow.description,
            "nodes": [serialize_workflow_node(node) for node in nodes],
            "edges": [serialize_workflow_edge(edge) for edge in edges],
        }
        logger.debug(f"Snapshot: {snapshot}")
        # Create and return snapshot
        return snapshot

    @staticmethod
    async def get_workflow_snapshot_hash(snapshot: dict[str, Any]) -> str:
        """Get the hash of the workflow snapshot asynchronously."""
        try:
            snapshot_hash = hashlib.sha256(json_dumps(snapshot).encode()).hexdigest()
            logger.debug(f"Generated snapshot hash: {snapshot_hash}")
            return snapshot_hash
        except Exception as e:
            logger.error(f"Error calculating snapshot hash: {e!s}")
            raise WorkflowErrorCode.WORKFLOW_SNAPSHOT_ERROR.exception(
                data={"error": str(e), "message": "Failed to calculate workflow snapshot hash"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    @staticmethod
    async def publish_workflow(
        session: AsyncSession,
        workflow_id: str,
        version: str,
        description: str,
        published_by: str,
    ) -> WorkflowVersion:
        """
        Publish a new version of a workflow by creating a snapshot and version record.

        Args:
            session: Database session
            workflow_id: ID of the workflow to publish
            version: Version string (e.g., "1.0.0")
            description: Description of this version
            published_by: ID of the user publishing the version

        Returns:
            WorkflowVersion: Created workflow version object

        Raises:
            WorkflowErrorCode.WORKFLOW_NOT_FOUND: If workflow doesn't exist
            WorkflowErrorCode.VERSION_ALREADY_EXISTS: If version already exists
            WorkflowErrorCode.INVALID_WORKFLOW: If workflow is invalid
        """
        try:
            # Validate workflow existence
            result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
            workflow = result.scalar_one_or_none()
            if not workflow:
                raise WorkflowErrorCode.WORKFLOW_NOT_FOUND.exception(
                    data={
                        "workflow_id": str(workflow_id),
                        "message": "Cannot publish version for non-existent workflow",
                    },
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            # Check for version conflicts
            version_result = await session.execute(
                select(WorkflowVersion).where(
                    WorkflowVersion.workflow_id == workflow_id, WorkflowVersion.version == version
                )
            )

            if version_result.scalar_one_or_none():
                raise WorkflowErrorCode.WORKFLOW_VERSION_ALREADY_EXISTS.exception(
                    data={
                        "workflow_id": str(workflow_id),
                        "version": version,
                        "message": "This version number is already in use",
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            try:
                # Create snapshot and calculate hash
                snapshot = await WorkflowService.get_workflow_snapshot(session, workflow_id)
                snapshot_hash = await WorkflowService.get_workflow_snapshot_hash(snapshot)
                # Create new version record
                workflow_version = WorkflowVersion(
                    workflow_id=workflow_id,
                    version=version,
                    status=WorkflowVersionStatus.ACTIVE,
                    description=description,
                    published_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    published_by=published_by,
                    snapshot=snapshot,
                    snapshot_hash=snapshot_hash,
                )
                await workflow_version.save(session)

                # Update workflow current version
                workflow.version = version
                await workflow.save(session)

                logger.info(
                    f"Published workflow version {version} for workflow {workflow_id} "
                    f"with snapshot hash {snapshot_hash[:8]}"
                )

                return workflow_version

            except Exception as e:
                # Handle version publishing errors
                await session.rollback()
                raise WorkflowErrorCode.WORKFLOW_VERSION_PUBLISH_ERROR.exception(
                    data={
                        "workflow_id": str(workflow_id),
                        "version": version,
                        "error": str(e),
                        "message": "Failed to publish workflow version",
                    },
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                ) from e

        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Error in workflow version publishing: {e}")
            raise WorkflowErrorCode.WORKFLOW_VERSION_PUBLISH_ERROR.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "version": version,
                    "error": str(e),
                    "message": "Unexpected error during workflow version publishing",
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e
