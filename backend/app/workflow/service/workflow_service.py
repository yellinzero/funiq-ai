from collections.abc import Callable
from datetime import datetime
from typing import Coroutine, List

import semver
from fastapi import Request, status
from loguru import logger
from nanoid import generate
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.account.service.tenant_service import TenantService
from app.core.errors import CommonErrorCode, WorkflowErrorCode
from app.core.models.account import User
from app.core.models.workflow import (
    Workflow,
    WorkflowDebugSnapshot,
    WorkflowEdge,
    WorkflowNode,
    WorkflowStatus,
    WorkflowVersion,
    WorkflowVersionStatus,
)
from infrastructure import WorkflowEngine
from infrastructure.workflow_engine import FlowExecutionCallbackContext
from providers.operators.core import OperatorName
from utils.common.datetime import utcnow

from ..schemas import (
    CreateWorkflowEdgePayload,
    CreateWorkflowNodePayload,
    CreateWorkflowRequest,
    CreateWorkflowVersionPayload,
    SaveWorkflowRequest,
    UpdateWorkflowEdgePayload,
    UpdateWorkflowNodePayload,
    WorkflowDebugSnapshotInfo,
    WorkflowEdgeInfo,
    WorkflowInfo,
    WorkflowNodeInfo,
    WorkflowVersionInfo,
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


class WorkflowService:
    @staticmethod
    def serialize_workflow(workflow: Workflow) -> WorkflowInfo:
        return WorkflowInfo(**workflow.to_dict(convert_uuid_to_str=True))

    @staticmethod
    def serialize_workflow_version(workflow_version: WorkflowVersion) -> WorkflowVersionInfo:
        return WorkflowVersionInfo(**workflow_version.to_dict(convert_uuid_to_str=True))

    @staticmethod
    def serialize_workflow_debug_snapshot(workflow_snapshot: WorkflowDebugSnapshot) -> WorkflowDebugSnapshotInfo:
        return WorkflowDebugSnapshotInfo(**workflow_snapshot.to_dict(convert_uuid_to_str=True))

    @staticmethod
    def serialize_workflow_node(node: WorkflowNode) -> WorkflowNodeInfo:
        return WorkflowNodeInfo(**node.to_dict(convert_uuid_to_str=True))

    @staticmethod
    def serialize_workflow_edge(edge: WorkflowEdge) -> WorkflowEdgeInfo:
        return WorkflowEdgeInfo(**edge.to_dict(convert_uuid_to_str=True))

    @staticmethod
    async def get_workflow(session: AsyncSession, workflow_id: str) -> Workflow:
        result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise WorkflowErrorCode.WORKFLOW_NOT_FOUND.exception(
                data={"workflow_id": str(workflow_id)}, status_code=status.HTTP_404_NOT_FOUND
            )
        return workflow

    @staticmethod
    async def get_workflow_version(session: AsyncSession, workflow_id: str, version: str) -> WorkflowVersion:
        result = await session.execute(
            select(WorkflowVersion).where(
                WorkflowVersion.workflow_id == workflow_id, WorkflowVersion.version == version
            )
        )
        workflow_version = result.scalar_one_or_none()
        if not workflow_version:
            raise WorkflowErrorCode.WORKFLOW_VERSION_NOT_FOUND.exception(
                data={"workflow_id": str(workflow_id), "version": version}, status_code=status.HTTP_404_NOT_FOUND
            )
        return workflow_version

    @staticmethod
    async def get_workflow_debug_snapshot(
        session: AsyncSession, workflow_id: str, snapshot_timestamp: datetime
    ) -> WorkflowDebugSnapshot:
        result = await session.execute(
            select(WorkflowDebugSnapshot).where(
                WorkflowDebugSnapshot.workflow_id == workflow_id,
                WorkflowDebugSnapshot.snapshot_timestamp == snapshot_timestamp,
            )
        )
        workflow_debug_snapshot = result.scalar_one_or_none()
        if not workflow_debug_snapshot:
            raise WorkflowErrorCode.WORKFLOW_DEBUG_SNAPSHOT_NOT_FOUND.exception(
                data={"workflow_id": str(workflow_id), "snapshot_timestamp": snapshot_timestamp},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return workflow_debug_snapshot

    @staticmethod
    async def get_workflows(session: AsyncSession, app_id: str) -> List[WorkflowInfo]:
        try:
            result = await session.execute(
                select(Workflow).where(Workflow.app_id == app_id).order_by(Workflow.created_at.desc())
            )
            workflows = result.scalars().all()
            return [WorkflowService.serialize_workflow(workflow) for workflow in workflows]
        except Exception as e:
            logger.error(f"Error getting workflows: {e}")
            raise WorkflowErrorCode.WORKFLOW_FETCH_FAILED.exception(
                data={"app_id": str(app_id)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_workflow_versions(session: AsyncSession, workflow_id: str) -> List[WorkflowVersionInfo]:
        try:
            result = await session.execute(
                select(WorkflowVersion)
                .where(WorkflowVersion.workflow_id == workflow_id)
                .order_by(WorkflowVersion.published_at.desc())
            )
            workflow_versions = result.scalars().all()
            return [
                WorkflowService.serialize_workflow_version(workflow_version) for workflow_version in workflow_versions
            ]
        except Exception as e:
            logger.error(f"Error getting workflow versions: {e}")
            raise WorkflowErrorCode.WORKFLOW_VERSION_FETCH_FAILED.exception(
                data={"workflow_id": str(workflow_id)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_workflow_debug_snapshots(session: AsyncSession, workflow_id: str) -> List[WorkflowDebugSnapshotInfo]:
        try:
            result = await session.execute(
                select(WorkflowDebugSnapshot)
                .where(WorkflowDebugSnapshot.workflow_id == workflow_id)
                .order_by(WorkflowDebugSnapshot.created_at.desc())
            )
            workflow_debug_snapshots = result.scalars().all()
            return [
                WorkflowService.serialize_workflow_debug_snapshot(workflow_debug_snapshot)
                for workflow_debug_snapshot in workflow_debug_snapshots
            ]
        except Exception as e:
            logger.error(f"Error getting workflow debug snapshots: {e}")
            raise WorkflowErrorCode.WORKFLOW_DEBUG_SNAPSHOT_FETCH_FAILED.exception(
                data={"workflow_id": str(workflow_id)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_workflow_nodes(session: AsyncSession, workflow_id: str) -> List[WorkflowNodeInfo]:
        try:
            result = await session.execute(select(WorkflowNode).where(WorkflowNode.workflow_id == workflow_id))
            workflow_nodes = result.scalars().all()
            return [WorkflowService.serialize_workflow_node(workflow_node) for workflow_node in workflow_nodes]
        except Exception as e:
            logger.error(f"Error getting workflow nodes: {e}")
            raise WorkflowErrorCode.WORKFLOW_NODE_FETCH_FAILED.exception(
                data={"workflow_id": str(workflow_id)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_workflow_edges(session: AsyncSession, workflow_id: str) -> List[WorkflowEdgeInfo]:
        try:
            result = await session.execute(select(WorkflowEdge).where(WorkflowEdge.workflow_id == workflow_id))
            workflow_edges = result.scalars().all()
            return [WorkflowService.serialize_workflow_edge(workflow_edge) for workflow_edge in workflow_edges]
        except Exception as e:
            logger.error(f"Error getting workflow edges: {e}")
            raise WorkflowErrorCode.WORKFLOW_EDGE_FETCH_FAILED.exception(
                data={"workflow_id": str(workflow_id)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_workflow_node(session: AsyncSession, workflow_id: str, node_key: str) -> WorkflowNode:
        result = await session.execute(
            select(WorkflowNode).where(and_(WorkflowNode.workflow_id == workflow_id, WorkflowNode.node_key == node_key))
        )
        workflow_node = result.scalar_one_or_none()
        if not workflow_node:
            raise WorkflowErrorCode.WORKFLOW_NODE_NOT_FOUND.exception(
                data={"workflow_id": str(workflow_id), "node_key": node_key}, status_code=status.HTTP_404_NOT_FOUND
            )
        return workflow_node

    @staticmethod
    async def get_workflow_edge(session: AsyncSession, workflow_id: str, edge_key: str) -> WorkflowEdge:
        result = await session.execute(
            select(WorkflowEdge).where(and_(WorkflowEdge.workflow_id == workflow_id, WorkflowEdge.edge_key == edge_key))
        )
        workflow_edge = result.scalar_one_or_none()
        if not workflow_edge:
            raise WorkflowErrorCode.WORKFLOW_EDGE_NOT_FOUND.exception(
                data={"workflow_id": str(workflow_id), "edge_key": edge_key}, status_code=status.HTTP_404_NOT_FOUND
            )
        return workflow_edge

    @staticmethod
    async def create_workflow(
        session: AsyncSession, request: Request, payload: CreateWorkflowRequest, commit: bool = True
    ) -> WorkflowInfo:
        _, _, user = await TenantService.get_tenant_and_user(session=session, request=request)

        try:
            workflow = Workflow(
                app_id=payload.app_id,
                created_by=user.id,
                updated_by=user.id,
                config=payload.config,
            )
            await workflow.save(session)
            start_node = await WorkflowService._create_workflow_node(
                session=session,
                payload=CreateWorkflowNodePayload(
                    node_type=OperatorName.START,
                    node_key=generate_node_or_edge_key(),
                    name="Start",
                ),
                workflow_id=workflow.id,
                user=user,
            )
            end_node = await WorkflowService._create_workflow_node(
                session=session,
                payload=CreateWorkflowNodePayload(
                    node_type=OperatorName.END,
                    node_key=generate_node_or_edge_key(),
                    name="End",
                ),
                workflow_id=workflow.id,
                user=user,
            )
            await WorkflowService._create_workflow_edge(
                session=session,
                payload=CreateWorkflowEdgePayload(
                    edge_key=generate_node_or_edge_key(),
                    source_node_key=start_node.node_key,
                    target_node_key=end_node.node_key,
                ),
                workflow_id=workflow.id,
                user=user,
            )

            if commit:
                await session.commit()
            return WorkflowService.serialize_workflow(workflow)
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_CREATE_ERROR.exception(
                data={"message": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _create_workflow_node(
        session: AsyncSession,
        payload: CreateWorkflowNodePayload,
        workflow_id: str,
        user: User,
        need_commit: bool = False,
    ) -> WorkflowNode:
        try:
            node = WorkflowNode(
                workflow_id=workflow_id,
                node_type=payload.node_type,
                node_key=payload.node_key,
                name=payload.name,
                description=payload.description,
                config=payload.config,
                extended_config=payload.extended_config,
                meta=payload.meta,
                created_by=user.id,
                updated_by=user.id,
            )
            await node.save(session)
            await session.flush()
            if need_commit:
                await session.commit()
            return node
        except Exception as e:
            logger.error(f"Error creating workflow node: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_NODE_CREATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _create_workflow_edge(
        session: AsyncSession,
        payload: CreateWorkflowEdgePayload,
        workflow_id: str,
        user: User,
        need_commit: bool = False,
    ) -> WorkflowEdge:
        try:
            edge = WorkflowEdge(
                workflow_id=workflow_id,
                edge_key=payload.edge_key,
                source_node_key=payload.source_node_key,
                target_node_key=payload.target_node_key,
                meta=payload.meta,
                created_by=user.id,
                updated_by=user.id,
            )
            await edge.save(session)
            await session.flush()
            if need_commit:
                await session.commit()
            return edge
        except Exception as e:
            logger.error(f"Error creating workflow edge: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_EDGE_CREATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _update_workflow_node(
        session: AsyncSession,
        node_key: str,
        payload: UpdateWorkflowNodePayload,
        workflow_id: str,
        user: User,
        need_commit: bool = False,
    ) -> WorkflowNode:
        try:
            node = await WorkflowService.get_workflow_node(session, workflow_id, node_key)
            if payload.name:
                node.name = payload.name
            if payload.description:
                node.description = payload.description
            if payload.config:
                node.config = payload.config
            if payload.extended_config:
                node.extended_config = payload.extended_config
            if payload.meta:
                node.meta = payload.meta
            node.updated_by = user.id
            await node.save(session)
            await session.flush()
            if need_commit:
                await session.commit()
            return node
        except Exception as e:
            logger.error(f"Error updating workflow node: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_NODE_UPDATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _update_workflow_edge(
        session: AsyncSession,
        edge_key: str,
        payload: UpdateWorkflowEdgePayload,
        workflow_id: str,
        user: User,
        need_commit: bool = False,
    ) -> WorkflowEdge:
        try:
            edge = await WorkflowService.get_workflow_edge(session, workflow_id, edge_key)
            if payload.meta:
                edge.meta = payload.meta
            if payload.source_node_key:
                edge.source_node_key = payload.source_node_key
            if payload.target_node_key:
                edge.target_node_key = payload.target_node_key
            edge.updated_by = user.id
            await edge.save(session)
            await session.flush()
            if need_commit:
                await session.commit()
            return edge
        except Exception as e:
            logger.error(f"Error updating workflow edge: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_EDGE_UPDATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _delete_workflow_node(
        session: AsyncSession, node_key: str, workflow_id: str, need_commit: bool = False
    ) -> None:
        try:
            node = await WorkflowService.get_workflow_node(session, workflow_id, node_key)
            await node.delete(session)
            await session.flush()
            if need_commit:
                await session.commit()
        except Exception as e:
            logger.error(f"Error deleting workflow node: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_NODE_DELETE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _delete_workflow_edge(
        session: AsyncSession, edge_key: str, workflow_id: str, need_commit: bool = False
    ) -> None:
        try:
            edge = await WorkflowService.get_workflow_edge(session, workflow_id, edge_key)
            await edge.delete(session)
            await session.flush()
            if need_commit:
                await session.commit()
        except Exception as e:
            logger.error(f"Error deleting workflow edge: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_EDGE_DELETE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _update_workflow_config(
        session: AsyncSession, workflow: Workflow, config: dict, user: User, need_commit: bool = False
    ) -> Workflow:
        try:
            workflow.config = config
            workflow.updated_by = user.id
            await workflow.save(session)
            await session.flush()
            if need_commit:
                await session.commit()
            return workflow
        except Exception as e:
            logger.error(f"Error updating workflow config: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_CONFIG_UPDATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def save_workflow(
        session: AsyncSession, request: Request, workflow_id: str, payload: SaveWorkflowRequest
    ) -> WorkflowInfo:
        _, _, user = await TenantService.get_tenant_and_user(session=session, request=request)

        try:
            workflow = await WorkflowService.get_workflow(session=session, workflow_id=workflow_id)

            if payload.update_nodes:
                for node in payload.update_nodes:
                    await WorkflowService._update_workflow_node(session, node, workflow_id, user)

            if payload.update_edges:
                for edge in payload.update_edges:
                    await WorkflowService._update_workflow_edge(session, edge, workflow_id, user)

            if payload.create_nodes:
                for node in payload.create_nodes:
                    await WorkflowService._create_workflow_node(session, node, workflow_id, user)

            if payload.create_edges:
                for edge in payload.create_edges:
                    await WorkflowService._create_workflow_edge(session, edge, workflow_id, user)

            if payload.delete_nodes:
                for node_key in payload.delete_nodes:
                    await WorkflowService._delete_workflow_node(session, node_key, workflow_id, user)

            if payload.delete_edges:
                for edge_key in payload.delete_edges:
                    await WorkflowService._delete_workflow_edge(session, edge_key, workflow_id, user)
            if payload.config:
                await WorkflowService._update_workflow_config(session, workflow, payload.config, user)

            workflow.updated_by = user.id
            workflow.status = WorkflowStatus.DRAFT
            await workflow.save(session)

            result = WorkflowService.serialize_workflow(workflow)
            await session.commit()
            return result
        except Exception as e:
            logger.error(f"Error saving workflow: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_SAVE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def delete_workflow(session: AsyncSession, workflow_id: str) -> None:
        try:
            workflow = await WorkflowService.get_workflow(session=session, workflow_id=workflow_id)
            await workflow.delete(session)
            await session.commit()
            return None
        except Exception as e:
            logger.error(f"Error deleting workflow: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_DELETE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _validate_workflow_version(
        session: AsyncSession,
        workflow: Workflow,
        version: str,
    ) -> None:
        """
        Validate workflow version number and uniqueness
        """
        try:
            # 1. Validate version format
            ver = semver.VersionInfo.parse(version)

            # 2. Check if version already exists
            existing_version = await session.execute(
                select(WorkflowVersion).where(
                    and_(WorkflowVersion.workflow_id == workflow.id, WorkflowVersion.version == version)
                )
            )
            if existing_version.scalar_one_or_none():
                raise WorkflowErrorCode.WORKFLOW_VERSION_ALREADY_EXISTS.exception(
                    data={
                        "workflow_id": str(workflow.id),
                        "version": version,
                        "message": "This version number already exists",
                    }
                )

            # 3. Get latest version and validate version order
            latest_version = workflow.version

            if latest_version:
                latest_ver = semver.VersionInfo.parse(latest_version)
                if ver <= latest_ver:
                    raise CommonErrorCode.INVALID_VERSION.exception(
                        data={
                            "version": version,
                            "latest_version": latest_version,
                            "message": "New version must be greater than the latest version",
                        }
                    )

        except ValueError as e:
            raise WorkflowErrorCode.INVALID_VERSION_FORMAT.exception(
                data={"version": version, "message": f"Invalid version format: {e!s}"}
            ) from e

    @staticmethod
    async def publish_workflow(
        session: AsyncSession,
        request: Request,
        workflow_id: str,
        payload: CreateWorkflowVersionPayload,
    ) -> WorkflowVersionInfo:
        """
        Publish a new version of a workflow by creating a snapshot and version record.

        Args:
            session: Database session
            payload: CreateWorkflowVersionPayload
            request: Request object

        Returns:
            WorkflowVersionInfo: Created workflow version object

        Raises:
            WorkflowErrorCode.WORKFLOW_NOT_FOUND: If workflow doesn't exist
            WorkflowErrorCode.VERSION_ALREADY_EXISTS: If version already exists
            WorkflowErrorCode.INVALID_WORKFLOW: If workflow is invalid
        """
        # Validate workflow existence
        _, _, user = await TenantService.get_tenant_and_user(session=session, request=request)

        workflow = await WorkflowService.get_workflow(session=session, workflow_id=workflow_id)
        if not workflow:
            raise WorkflowErrorCode.WORKFLOW_NOT_FOUND.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "message": "Cannot publish version for non-existent workflow",
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Check for version
        await WorkflowService._validate_workflow_version(session, workflow, payload.version)

        try:
            # Create snapshot and calculate hash
            snapshot, snapshot_hash = await workflow.get_snapshot(need_hash=True)
            start_node = await workflow.get_start_node(session)
            end_node = await workflow.get_end_node(session)
            start_node_key = start_node.node_key
            end_node_key = end_node.node_key

            # Create new version record
            workflow_version = WorkflowVersion(
                workflow_id=workflow_id,
                version=payload.version,
                status=WorkflowVersionStatus.ACTIVE,
                description=payload.description,
                published_at=utcnow().replace(tzinfo=None),
                published_by=user.id,
                snapshot=snapshot,
                snapshot_hash=snapshot_hash,
                start_node_key=start_node_key,
                end_node_key=end_node_key,
            )
            await workflow_version.save(session)

            # Update workflow current version
            workflow.version = payload.version
            workflow.status = WorkflowStatus.PUBLISHED
            await workflow.save(session)

            result = WorkflowService.serialize_workflow_version(workflow_version)
            await session.commit()
            return result

        except Exception as e:
            # Handle version publishing errors
            await session.rollback()
            logger.error(f"Error publishing workflow version: {e}")
            raise WorkflowErrorCode.WORKFLOW_VERSION_PUBLISH_ERROR.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "version": payload.version,
                    "message": "Failed to publish workflow version",
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    @staticmethod
    async def execute_workflow_stream(
        session: AsyncSession,
        workflow_id: str,
        input_data: dict,
        execution_context: dict,
        is_debug: bool = False,
        version: str | None = None,
        snapshot_timestamp: datetime | None = None,
        on_created: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_pending: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_running: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_completed: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_failed: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_cancelling: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_cancelled: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
        on_paused: Callable[[FlowExecutionCallbackContext], Coroutine] = [],
    ) -> WorkflowEngine:
        """
        Execute workflow in stream mode.

        This method should be used for stream processing instead of Celery tasks.
        """
        workflow = await WorkflowService.get_workflow(session=session, workflow_id=workflow_id)
        if not workflow:
            raise WorkflowErrorCode.WORKFLOW_NOT_FOUND.exception(
                data={
                    "workflow_id": str(workflow_id),
                    "message": "Cannot execute non-existent workflow",
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        snapshot = None
        snapshot_hash = None
        snapshot_timestamp = None
        version = None
        start_node_key = None
        end_node_key = None
        # Create and execute appropriate executor
        if is_debug:
            debug_snapshot = await WorkflowService.get_workflow_debug_snapshot(
                session=session, workflow_id=workflow_id, snapshot_timestamp=snapshot_timestamp
            )
            snapshot = debug_snapshot.snapshot
            snapshot_hash = debug_snapshot.snapshot_hash
            snapshot_timestamp = debug_snapshot.snapshot_timestamp
            start_node_key = debug_snapshot.start_node_key
            end_node_key = debug_snapshot.end_node_key
        else:
            workflow_version = await WorkflowService.get_workflow_version(
                session=session, workflow_id=workflow_id, version=version
            )
            snapshot = workflow_version.snapshot
            snapshot_hash = workflow_version.snapshot_hash
            version = workflow_version.version
            start_node_key = workflow_version.start_node_key
            end_node_key = workflow_version.end_node_key

        executor = WorkflowEngine(
            workflow_id=workflow_id,
            version=version,
            is_debug=is_debug,
            snapshot_timestamp=snapshot_timestamp,
            start_node_key=start_node_key,
            end_node_key=end_node_key,
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

        return executor
