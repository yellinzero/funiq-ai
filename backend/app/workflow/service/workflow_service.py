import hashlib
from collections.abc import Callable
from datetime import datetime
from typing import Any, Coroutine, Dict, List, Tuple

from fastapi import Request, status
from loguru import logger
from nanoid import generate
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.account.service.tenant_service import TenantService
from app.core.errors import AccountErrorCode, WorkflowErrorCode
from app.core.models.workflow import (
    Workflow,
    WorkflowEdge,
    WorkflowNode,
    WorkflowSnapshot,
    WorkflowStatus,
    WorkflowVersion,
    WorkflowVersionStatus,
)
from infrastructure import WorkflowDebugEngine, WorkflowVersionEngine
from infrastructure.workflow_engine import FlowExecutionCallbackContext
from providers.operators.core import OperatorName
from tasks.workflow_tasks import execute_workflow as celery_execute_workflow
from utils.common.datetime import utcnow
from utils.common.json import json_dumps

from ..schemas import (
    GetWorkflowResponseBase,
    PublishWorkflowResponse,
    SaveWorkflowResponse,
    WorkflowEdgeResponse,
    WorkflowExecuteContext,
    WorkflowExecuteInputData,
    WorkflowListResponse,
    WorkflowNodeResponse,
    WorkflowOperation,
    WorkflowOperationType,
    WorkflowResponse,
)


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
    async def _can_workflow_execute(
        session: AsyncSession,
        workflow_id: str,
        version: str | None = None,
        snapshot_timestamp: datetime | None = None,
    ) -> Tuple[Dict[str, Any], str]:
        """Validate if workflow can be executed and return its snapshot.

        Args:
            session: Database session
            workflow_id: ID of the workflow
            version: Optional version to execute
            snapshot_timestamp: Optional snapshot timestamp for debug mode

        Returns:
            Tuple[Dict, str]: Returns (snapshot, snapshot_hash)

        Raises:
            WorkflowErrorCode: Various validation errors
        """
        # Validate workflow exists
        result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise WorkflowErrorCode.WORKFLOW_NOT_FOUND.exception(
                data={"workflow_id": str(workflow_id)},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Validate version XOR snapshot_timestamp
        if bool(version) == bool(snapshot_timestamp):
            raise WorkflowErrorCode.WORKFLOW_EXECUTION_ERROR.exception(
                data={"message": "Either version or snapshot_timestamp must be provided, but not both"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Get snapshot based on execution mode
        if version:
            # Version mode
            version_result = await session.execute(
                select(WorkflowVersion).where(
                    WorkflowVersion.workflow_id == workflow_id, WorkflowVersion.version == version
                )
            )
            workflow_version = version_result.scalar_one_or_none()
            if not workflow_version:
                raise WorkflowErrorCode.WORKFLOW_VERSION_NOT_FOUND.exception(
                    data={"workflow_id": str(workflow_id), "version": version}
                )
            if workflow_version.status != WorkflowVersionStatus.ACTIVE:
                raise WorkflowErrorCode.WORKFLOW_VERSION_NOT_ACTIVE.exception(
                    data={
                        "workflow_id": str(workflow_id),
                        "version": version,
                        "status": workflow_version.status,
                    }
                )
            return workflow_version.snapshot, workflow_version.snapshot_hash
        else:
            # Debug mode (snapshot)
            snapshot_result = await session.execute(
                select(WorkflowSnapshot).where(
                    WorkflowSnapshot.workflow_id == workflow_id,
                    WorkflowSnapshot.snapshot_timestamp == snapshot_timestamp,
                )
            )
            workflow_snapshot = snapshot_result.scalar_one_or_none()
            if not workflow_snapshot:
                raise WorkflowErrorCode.WORKFLOW_SNAPSHOT_NOT_FOUND.exception(
                    data={"workflow_id": str(workflow_id), "snapshot_timestamp": snapshot_timestamp}
                )
            return workflow_snapshot.snapshot, workflow_snapshot.snapshot_hash

    @staticmethod
    async def execute_workflow_stream(
        session: AsyncSession,
        request: Request,
        workflow_id: str,
        input_data: WorkflowExecuteInputData,
        execution_context: WorkflowExecuteContext,
        version: str | None = None,
        snapshot_timestamp: str | None = None,
        on_created: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_pending: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_running: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_completed: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_failed: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_cancelling: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_cancelled: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_paused: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
    ):
        """Execute workflow in stream mode.

        This method should be used for stream processing instead of Celery tasks.
        """
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(status_code=status.HTTP_404_NOT_FOUND)

        # Validate and get snapshot
        snapshot, snapshot_hash = await WorkflowService._can_workflow_execute(
            session, workflow_id, version, snapshot_timestamp
        )

        # Validate stream mode
        if not snapshot.get("stream_mode"):
            raise WorkflowErrorCode.WORKFLOW_EXECUTION_ERROR.exception(
                data={"message": "Workflow is not configured for streaming"}
            )

        # Create and execute appropriate executor
        if version:
            executor = WorkflowVersionEngine(
                workflow_id=workflow_id,
                version=version,
                snapshot=snapshot,
                snapshot_hash=snapshot_hash,
                input_data=input_data,
                execution_context=execution_context,
                on_created=on_created,
                on_pending=on_pending,
                on_running=on_running,
                on_completed=on_completed,
                on_failed=on_failed,
                on_cancelling=on_cancelling,
                on_cancelled=on_cancelled,
                on_paused=on_paused,
            )
        else:
            executor = WorkflowDebugEngine(
                workflow_id=workflow_id,
                snapshot=snapshot,
                snapshot_hash=snapshot_hash,
                input_data=input_data,
                execution_context=execution_context,
                snapshot_timestamp=snapshot_timestamp,
                on_created=on_created,
                on_pending=on_pending,
                on_running=on_running,
                on_completed=on_completed,
                on_failed=on_failed,
                on_cancelling=on_cancelling,
                on_cancelled=on_cancelled,
                on_paused=on_paused,
            )

        return executor

    @staticmethod
    async def execute_workflow_sync(
        session: AsyncSession,
        request: Request,
        workflow_id: str,
        input_data: WorkflowExecuteInputData,
        execution_context: WorkflowExecuteContext,
        version: str | None = None,
        snapshot_timestamp: datetime | None = None,
    ) -> Dict[str, Any]:
        """Execute workflow synchronously.

        This method should only be used for non-stream workflows.
        """
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(status_code=status.HTTP_404_NOT_FOUND)
        snapshot, _ = await WorkflowService._can_workflow_execute(
            session=session,
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            version=version,
            snapshot_timestamp=snapshot_timestamp,
        )

        # Validate non-stream mode
        if snapshot.get("stream_mode"):
            raise WorkflowErrorCode.WORKFLOW_EXECUTION_ERROR.exception(
                data={"message": "Streaming workflows must use execute_workflow_stream"}
            )

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
                data={"workflow_id": str(workflow_id), "error": str(e)}
            ) from e

        return task.get()

    @staticmethod
    async def execute_workflow_async(
        session: AsyncSession,
        request: Request,
        workflow_id: str,
        input_data: WorkflowExecuteInputData,
        execution_context: WorkflowExecuteContext,
        version: str | None = None,
        snapshot_timestamp: datetime | None = None,
    ) -> Dict[str, Any]:
        """Execute workflow asynchronously using Celery.

        This method should only be used for non-stream workflows.
        """
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(status_code=status.HTTP_404_NOT_FOUND)
        snapshot, _ = await WorkflowService._can_workflow_execute(session, workflow_id, version, snapshot_timestamp)

        # Validate non-stream mode
        if snapshot.get("stream_mode"):
            raise WorkflowErrorCode.WORKFLOW_EXECUTION_ERROR.exception(
                data={"message": "Streaming workflows must use execute_workflow_stream"}
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
                data={"workflow_id": str(workflow_id), "error": str(e)}
            ) from e

        return {"task_id": task.id}

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

        # Check if the workflow is a stream according to the end node's stream mode
        end_node = next((node for node in nodes if node.node_type == OperatorName.END.value), None)
        is_stream = end_node and end_node.extended_config and end_node.extended_config.get("stream_mode", False)
        snapshot = {
            "name": workflow.name,
            "description": workflow.description,
            "stream_mode": is_stream,
            "nodes": [serialize_workflow_node(node) for node in nodes],
            "edges": [serialize_workflow_edge(edge) for edge in edges],
        }
        # Create and return snapshot
        return snapshot

    @staticmethod
    async def get_workflow_snapshot_hash(snapshot: dict[str, Any]) -> str:
        """Get the hash of the workflow snapshot asynchronously."""
        try:
            snapshot_hash = hashlib.sha256(json_dumps(snapshot).encode()).hexdigest()
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
        request: Request,
    ) -> PublishWorkflowResponse:
        """
        Publish a new version of a workflow by creating a snapshot and version record.

        Args:
            session: Database session
            workflow_id: ID of the workflow to publish
            version: Version string (e.g., "1.0.0")
            description: Description of this version
            request: Request object

        Returns:
            PublishWorkflowResponse: Created workflow version object

        Raises:
            WorkflowErrorCode.WORKFLOW_NOT_FOUND: If workflow doesn't exist
            WorkflowErrorCode.VERSION_ALREADY_EXISTS: If version already exists
            WorkflowErrorCode.INVALID_WORKFLOW: If workflow is invalid
        """
        # Validate workflow existence
        tenant_id = request.state.tenant_id
        account_id = request.state.account_id
        user = await TenantService.get_user_by_account_id(session=session, tenant_id=tenant_id, account_id=account_id)

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
                and_(WorkflowVersion.workflow_id == workflow_id, WorkflowVersion.version == version)
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
            start_node_key = ''
            end_node_key = ''
            for node in snapshot["nodes"]:
                if node["node_type"] == OperatorName.START.value:
                    start_node_key = node["node_key"]
                elif node["node_type"] == OperatorName.END.value:
                    end_node_key = node["node_key"]
                    
            # Create new version record
            workflow_version = WorkflowVersion(
                workflow_id=workflow_id,
                version=version,
                status=WorkflowVersionStatus.ACTIVE,
                description=description,
                published_at=utcnow().replace(tzinfo=None),
                published_by=user.id,
                snapshot=snapshot,
                snapshot_hash=snapshot_hash,
                start_node_key=start_node_key,
                end_node_key=end_node_key,
            )
            await workflow_version.save(session)
            
            # Update workflow current version
            workflow.version = version
            workflow.status = WorkflowStatus.PUBLISHED
            await workflow.save(session)

            logger.info(
                f"Published workflow version {version} for workflow {workflow_id} "
                f"with snapshot hash {snapshot_hash[:8]}"
            )

            await session.commit()
            return PublishWorkflowResponse(
                workflow_id=str(workflow_id),
                version=version,
                description=description,
                published_at=workflow_version.published_at,
                published_by=str(user.id),
            )

        except Exception as e:
            # Handle version publishing errors
            await session.rollback()
            logger.error(f"Error publishing workflow version: {e}")
            raise WorkflowErrorCode.WORKFLOW_VERSION_PUBLISH_ERROR.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "version": version,
                    "error": str(e),
                    "message": "Failed to publish workflow version",
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    @staticmethod
    async def create_workflow(
        session: AsyncSession, name: str, description: str, app_id: str, request: Request
    ) -> Workflow:
        """Create a new workflow"""
        try:
            tenant_id = request.state.tenant_id
            if not tenant_id:
                raise AccountErrorCode.TENANT_NOT_FOUND.exception(status_code=status.HTTP_404_NOT_FOUND)

            account_id = request.state.account_id
            user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)

            # Check if the name already exists
            result = await session.execute(
                select(Workflow).where(and_(Workflow.app_id == app_id, Workflow.name == name))
            )
            if result.scalar_one_or_none():
                raise WorkflowErrorCode.WORKFLOW_ALREADY_EXISTS.exception(status_code=status.HTTP_400_BAD_REQUEST)
            workflow = Workflow(
                name=name,
                app_id=app_id,
                description=description,
                status=WorkflowStatus.DRAFT,
                created_by=user.id,
                updated_by=user.id,
            )
            await workflow.save(session)
            session.flush()

            # Create system workflow nodes and edges
            start_node_key = generate_node_or_edge_key()
            end_node_key = generate_node_or_edge_key()
            start_node = WorkflowNode(
                workflow_id=workflow.id,
                name="Start",
                node_key=start_node_key,
                node_type=OperatorName.START.value,
                config={
                    "query": "{{query}}",
                },
                created_by=user.id,
                updated_by=user.id,
            )
            await start_node.save(session)
            end_node = WorkflowNode(
                workflow_id=workflow.id,
                name="End",
                node_key=end_node_key,
                node_type=OperatorName.END.value,
                created_by=user.id,
                updated_by=user.id,
            )
            await end_node.save(session)

            edge = WorkflowEdge(
                workflow_id=workflow.id,
                edge_key=generate_node_or_edge_key(),
                source_node_key=start_node_key,
                target_node_key=end_node_key,
                created_by=user.id,
                updated_by=user.id,
            )
            await edge.save(session)

            return workflow
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_CREATE_ERROR.exception(
                data={
                    "workflow_name": name,
                    "error": str(e),
                    "message": "Failed to create workflow",
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    @staticmethod
    async def get_workflow_version(
        session: AsyncSession,
        workflow_id: str,
        workflow_version: str,
    ) -> WorkflowVersion:
        result = await session.execute(
            select(WorkflowVersion).where(
                and_(WorkflowVersion.workflow_id == workflow_id, WorkflowVersion.version == workflow_version)
            )
        )

        version = result.scalar_one_or_none()
        if not version:
            raise WorkflowErrorCode.WORKFLOW_VERSION_NOT_FOUND.exception(
                data={"workflow_id": workflow_id, "workflow_version": workflow_version}
            )
        return version

    @staticmethod
    async def save_workflow(
        session: AsyncSession,
        workflow_id: str,
        operations: List[WorkflowOperation],
        request: Request,
    ) -> SaveWorkflowResponse:
        """Process batch operations for workflow graph data."""
        try:
            tenant_id = request.state.tenant_id
            if not tenant_id:
                raise AccountErrorCode.TENANT_NOT_FOUND.exception(status_code=status.HTTP_404_NOT_FOUND)
            account_id = request.state.account_id
            user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)

            # Validate workflow exists
            result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
            workflow = result.scalar_one_or_none()
            if not workflow:
                raise WorkflowErrorCode.WORKFLOW_NOT_FOUND.exception(
                    data={"workflow_id": str(workflow_id)},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            result = {
                "added_nodes": [],
                "updated_nodes": [],
                "deleted_nodes": [],
                "added_edges": [],
                "updated_edges": [],
                "deleted_edges": [],
            }

            # Process operations in order
            for operation in operations:
                if operation.operation_type == WorkflowOperationType.ADD_NODE:
                    for node in operation.nodes:
                        new_node = WorkflowNode(
                            workflow_id=workflow_id,
                            node_key=node.node_key,
                            node_type=node.node_type,
                            name=node.name,
                            description=node.description,
                            meta=node.meta,
                            config=node.config,
                            extended_config=node.extended_config,
                            created_by=user.id,
                            updated_by=user.id,
                        )
                        await new_node.save(session)
                        result["added_nodes"].append(node.node_key)

                elif operation.operation_type == WorkflowOperationType.UPDATE_NODE:
                    for node in operation.nodes:
                        node_result = await session.execute(
                            select(WorkflowNode).where(
                                and_(WorkflowNode.workflow_id == workflow_id, WorkflowNode.node_key == node.node_key)
                            )
                        )
                        existing_node = node_result.scalar_one_or_none()
                        if existing_node:
                            if node.name is not None:
                                existing_node.name = node.name
                            if node.description is not None:
                                existing_node.description = node.description
                            if node.meta is not None:
                                existing_node.meta = node.meta
                            if node.config is not None:
                                existing_node.config = node.config
                            if node.extended_config is not None:
                                existing_node.extended_config = node.extended_config
                            existing_node.updated_by = user.id
                            await existing_node.save(session)
                            result["updated_nodes"].append(node.node_key)

                elif operation.operation_type == WorkflowOperationType.DELETE_NODE:
                    for node in operation.nodes:
                        node_result = await session.execute(
                            select(WorkflowNode).where(
                                and_(WorkflowNode.workflow_id == workflow_id, WorkflowNode.node_key == node.node_key)
                            )
                        )
                        existing_node = node_result.scalar_one_or_none()
                        if existing_node:
                            await session.delete(existing_node)
                            result["deleted_nodes"].append(node.node_key)

                elif operation.operation_type == WorkflowOperationType.ADD_EDGE:
                    for edge in operation.edges:
                        new_edge = WorkflowEdge(
                            workflow_id=workflow_id,
                            edge_key=edge.edge_key,
                            source_node_key=edge.source_node_key,
                            target_node_key=edge.target_node_key,
                            meta=edge.meta,
                            created_by=user.id,
                            updated_by=user.id,
                        )
                        await new_edge.save(session)
                        result["added_edges"].append(edge.edge_key)

                elif operation.operation_type == WorkflowOperationType.UPDATE_EDGE:
                    for edge in operation.edges:
                        edge_result = await session.execute(
                            select(WorkflowEdge).where(
                                and_(WorkflowEdge.workflow_id == workflow_id, WorkflowEdge.edge_key == edge.edge_key)
                            )
                        )
                        existing_edge = edge_result.scalar_one_or_none()
                        if existing_edge:
                            if edge.source_node_key is not None:
                                existing_edge.source_node_key = edge.source_node_key
                            if edge.target_node_key is not None:
                                existing_edge.target_node_key = edge.target_node_key
                            if edge.meta is not None:
                                existing_edge.meta = edge.meta
                            existing_edge.updated_by = user.id
                            await existing_edge.save(session)
                            result["updated_edges"].append(edge.edge_key)

                elif operation.operation_type == WorkflowOperationType.DELETE_EDGE:
                    for edge in operation.edges:
                        edge_result = await session.execute(
                            select(WorkflowEdge).where(
                                and_(WorkflowEdge.workflow_id == workflow_id, WorkflowEdge.edge_key == edge.edge_key)
                            )
                        )
                        existing_edge = edge_result.scalar_one_or_none()
                        if existing_edge:
                            await session.delete(existing_edge)
                            result["deleted_edges"].append(edge.edge_key)

            # Create new snapshot after all operations
            snapshot = await WorkflowService.get_workflow_snapshot(session, workflow_id)
            snapshot_hash = await WorkflowService.get_workflow_snapshot_hash(snapshot)

            # Find start and end nodes
            nodes_result = await session.execute(select(WorkflowNode).where(WorkflowNode.workflow_id == workflow_id))
            nodes = nodes_result.scalars().all()
            start_node = next((node for node in nodes if node.node_type == OperatorName.START.value), None)
            end_node = next((node for node in nodes if node.node_type == OperatorName.END.value), None)

            if not start_node or not end_node:
                raise WorkflowErrorCode.INVALID_WORKFLOW.exception(
                    data={"message": "Workflow must have both start and end nodes"}
                )
            workflow.status = WorkflowStatus.DRAFT
            await workflow.save(session)
            await session.commit()
            return SaveWorkflowResponse(
                **result,
                snapshot=snapshot,
                snapshot_hash=snapshot_hash,
                start_node_key=start_node.node_key,
                end_node_key=end_node.node_key,
            )

        except Exception as e:
            logger.error(f"Error saving workflow: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_SAVE_ERROR.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "error": str(e),
                    "message": "Failed to save workflow changes",
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    @staticmethod
    async def update_workflow_meta(
        session: AsyncSession,
        workflow_id: str,
        request: Request,
        name: str | None = None,
        description: str | None = None,
    ) -> WorkflowResponse:
        """Update workflow metadata."""
        try:
            tenant_id = request.state.tenant_id
            if not tenant_id:
                raise AccountErrorCode.TENANT_NOT_FOUND.exception(status_code=status.HTTP_404_NOT_FOUND)
            account_id = request.state.account_id
            user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)

            result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
            workflow = result.scalar_one_or_none()
            if not workflow:
                raise WorkflowErrorCode.WORKFLOW_NOT_FOUND.exception(
                    data={"workflow_id": str(workflow_id)},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            if name is not None:
                # Check name uniqueness within tenant
                name_check = await session.execute(
                    select(Workflow).where(
                        and_(
                            Workflow.tenant_id == workflow.tenant_id, Workflow.name == name, Workflow.id != workflow_id
                        )
                    )
                )
                if name_check.scalar_one_or_none():
                    raise WorkflowErrorCode.WORKFLOW_ALREADY_EXISTS.exception(
                        data={"name": name},
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
                workflow.name = name

            if description is not None:
                workflow.description = description

            workflow.updated_by = user.id
            workflow.status = WorkflowStatus.DRAFT
            await workflow.save(session)

            # Fetch related nodes and edges for response
            nodes_result = await session.execute(select(WorkflowNode).where(WorkflowNode.workflow_id == workflow_id))
            edges_result = await session.execute(select(WorkflowEdge).where(WorkflowEdge.workflow_id == workflow_id))

            await session.commit()

            return WorkflowResponse(
                id=str(workflow.id),
                app_id=str(workflow.app_id),
                status=workflow.status,
                name=workflow.name,
                description=workflow.description,
                version=workflow.version,
                created_by=str(workflow.created_by),
                updated_by=str(workflow.updated_by),
                created_at=workflow.created_at,
                updated_at=workflow.updated_at,
                nodes=[WorkflowNodeResponse(**serialize_workflow_node(node)) for node in nodes_result.scalars().all()],
                edges=[WorkflowEdgeResponse(**serialize_workflow_edge(edge)) for edge in edges_result.scalars().all()],
            )

        except Exception as e:
            logger.error(f"Error updating workflow metadata: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_UPDATE_ERROR.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "error": str(e),
                    "message": "Failed to update workflow metadata",
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    @staticmethod
    async def get_workflow_list(
        session: AsyncSession,
        app_id: str,
        page: int = 1,
        page_size: int = 20,
        search_term: str | None = None,
    ) -> WorkflowListResponse:
        """
        Get paginated list of workflows with optional search.

        Args:
            session: Database session
            app_id: Application ID to filter workflows
            page: Page number (1-based)
            page_size: Number of items per page
            search_term: Optional search term to filter workflows by name or description

        Returns:
            Tuple[List[WorkflowResponse], int]: List of workflows and total count
        """
        # Build base query
        query = select(Workflow).where(Workflow.app_id == app_id)
        count_query = select(func.count()).select_from(Workflow).where(Workflow.app_id == app_id)

        # Add search condition if provided
        if search_term:
            search_filter = or_(Workflow.name.ilike(f"%{search_term}%"), Workflow.description.ilike(f"%{search_term}%"))
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total count
        total_result = await session.execute(count_query)
        total = total_result.scalar_one()

        # Add pagination
        offset = (page - 1) * page_size
        query = query.order_by(Workflow.updated_at.desc()).offset(offset).limit(page_size)

        # Execute query
        result = await session.execute(query)
        workflows = result.scalars().all()

        # Fetch nodes and edges for each workflow
        workflow_responses = []
        for workflow in workflows:
            # Fetch nodes
            workflow_responses.append(
                GetWorkflowResponseBase(
                    id=str(workflow.id),
                    app_id=str(workflow.app_id),
                    status=workflow.status,
                    name=workflow.name,
                    description=workflow.description,
                    version=workflow.version,
                    created_by=str(workflow.created_by),
                    updated_by=str(workflow.updated_by),
                    created_at=workflow.created_at,
                    updated_at=workflow.updated_at,
                )
            )

        return {
            "workflows": workflow_responses,
            "total": total,
        }

    @staticmethod
    async def get_workflow(session: AsyncSession, workflow_id: str) -> WorkflowResponse:
        """
        Get complete workflow information including nodes and edges.

        Args:
            session: Database session
            workflow_id: ID of the workflow to retrieve

        Returns:
            WorkflowResponse: Complete workflow information

        Raises:
            WorkflowErrorCode.WORKFLOW_NOT_FOUND: If workflow doesn't exist
        """
        result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise WorkflowErrorCode.WORKFLOW_NOT_FOUND.exception(
                data={"workflow_id": str(workflow_id)},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Fetch related nodes
        nodes_result = await session.execute(select(WorkflowNode).where(WorkflowNode.workflow_id == workflow_id))
        nodes = nodes_result.scalars().all()

        # Fetch related edges
        edges_result = await session.execute(select(WorkflowEdge).where(WorkflowEdge.workflow_id == workflow_id))
        edges = edges_result.scalars().all()

        return WorkflowResponse(
            id=str(workflow.id),
            app_id=str(workflow.app_id),
            status=workflow.status,
            name=workflow.name,
            description=workflow.description,
            version=workflow.version,
            created_by=str(workflow.created_by),
            updated_by=str(workflow.updated_by),
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            nodes=[WorkflowNodeResponse(**serialize_workflow_node(node)) for node in nodes],
            edges=[WorkflowEdgeResponse(**serialize_workflow_edge(edge)) for edge in edges],
        )
