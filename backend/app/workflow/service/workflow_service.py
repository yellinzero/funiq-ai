from collections.abc import Callable
from datetime import datetime
from typing import Coroutine, List

import semver
from fastapi import Request, status
from loguru import logger
from nanoid import generate
from sqlalchemy import and_, delete, select
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
    CreateWorkflowRequest,
    CreateWorkflowVersionPayload,
    SaveWorkflowEdgePayload,
    SaveWorkflowNodePayload,
    SaveWorkflowRequest,
    SaveWorkflowResponse,
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
            logger.error(f"Workflow version not found: {workflow_id} {version}")
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
        tenant_id, _, user = await TenantService.get_tenant_and_user(session=session, request=request)

        try:
            workflow = Workflow(
                tenant_id=tenant_id,
                app_id=payload.app_id,
                created_by=user.id,
                updated_by=user.id,
                config=payload.config,
            )
            await workflow.save(session)
            start_node = await WorkflowService._create_workflow_node(
                session=session,
                payload=SaveWorkflowNodePayload(
                    node_type=OperatorName.START,
                    node_key=generate_node_or_edge_key(),
                    name="Start",
                ),
                workflow_id=workflow.id,
                user=user,
            )
            end_node = await WorkflowService._create_workflow_node(
                session=session,
                payload=SaveWorkflowNodePayload(
                    node_type=OperatorName.END,
                    node_key=generate_node_or_edge_key(),
                    name="End",
                ),
                workflow_id=workflow.id,
                user=user,
            )
            await WorkflowService._create_workflow_edge(
                session=session,
                payload=SaveWorkflowEdgePayload(
                    edge_key=generate_node_or_edge_key(),
                    source_node_key=start_node.node_key,
                    target_node_key=end_node.node_key,
                ),
                workflow_id=workflow.id,
                user=user,
            )

            result = WorkflowService.serialize_workflow(workflow)
            if commit:
                await session.commit()
            return result
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_CREATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _create_workflow_node(
        session: AsyncSession,
        payload: SaveWorkflowNodePayload,
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
        payload: SaveWorkflowEdgePayload,
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
        payload: SaveWorkflowNodePayload,
        workflow_id: str,
        user: User,
        need_commit: bool = False,
    ) -> WorkflowNode:
        try:
            node = await WorkflowService.get_workflow_node(session, workflow_id, payload.node_key)
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
        payload: SaveWorkflowEdgePayload,
        workflow_id: str,
        user: User,
        need_commit: bool = False,
    ) -> WorkflowEdge:
        try:
            edge = await WorkflowService.get_workflow_edge(session, workflow_id, payload.edge_key)
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
    async def _batch_create_workflow_nodes(
        session: AsyncSession,
        payloads: list[SaveWorkflowNodePayload],
        workflow_id: str,
        user: User,
    ) -> list[WorkflowNode]:
        try:
            nodes = [
                WorkflowNode(
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
                for payload in payloads
            ]
            session.add_all(nodes)
            await session.flush()
            return nodes
        except Exception as e:
            logger.error(f"Error batch creating workflow nodes: {e}")
            raise WorkflowErrorCode.WORKFLOW_NODE_CREATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _batch_create_workflow_edges(
        session: AsyncSession,
        payloads: list[SaveWorkflowEdgePayload],
        workflow_id: str,
        user: User,
    ) -> list[WorkflowEdge]:
        try:
            edges = [
                WorkflowEdge(
                    workflow_id=workflow_id,
                    edge_key=payload.edge_key,
                    source_node_key=payload.source_node_key,
                    target_node_key=payload.target_node_key,
                    meta=payload.meta,
                    created_by=user.id,
                    updated_by=user.id,
                )
                for payload in payloads
            ]
            session.add_all(edges)
            await session.flush()
            return edges
        except Exception as e:
            logger.error(f"Error batch creating workflow edges: {e}")
            raise WorkflowErrorCode.WORKFLOW_EDGE_CREATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _batch_update_workflow_nodes(
        session: AsyncSession,
        payloads: list[SaveWorkflowNodePayload],
        workflow_id: str,
        user: User,
    ) -> list[WorkflowNode]:
        try:
            node_keys = [payload.node_key for payload in payloads]
            result = await session.execute(
                select(WorkflowNode).where(
                    and_(WorkflowNode.workflow_id == workflow_id, WorkflowNode.node_key.in_(node_keys))
                )
            )
            nodes = result.scalars().all()

            payloads_map = {payload.node_key: payload for payload in payloads}

            for node in nodes:
                payload = payloads_map[node.node_key]
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

            await session.flush()
            return nodes
        except Exception as e:
            logger.error(f"Error batch updating workflow nodes: {e}")
            raise WorkflowErrorCode.WORKFLOW_NODE_UPDATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _batch_update_workflow_edges(
        session: AsyncSession,
        payloads: list[SaveWorkflowEdgePayload],
        workflow_id: str,
        user: User,
    ) -> list[WorkflowEdge]:
        try:
            edge_keys = [payload.edge_key for payload in payloads]
            result = await session.execute(
                select(WorkflowEdge).where(
                    and_(WorkflowEdge.workflow_id == workflow_id, WorkflowEdge.edge_key.in_(edge_keys))
                )
            )
            edges = result.scalars().all()

            payloads_map = {payload.edge_key: payload for payload in payloads}

            for edge in edges:
                payload = payloads_map[edge.edge_key]
                if payload.meta:
                    edge.meta = payload.meta
                if payload.source_node_key:
                    edge.source_node_key = payload.source_node_key
                if payload.target_node_key:
                    edge.target_node_key = payload.target_node_key
                edge.updated_by = user.id

            await session.flush()
            return edges
        except Exception as e:
            logger.error(f"Error batch updating workflow edges: {e}")
            raise WorkflowErrorCode.WORKFLOW_EDGE_UPDATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _batch_delete_workflow_nodes(
        session: AsyncSession,
        node_keys: list[str],
        workflow_id: str,
    ) -> list[str]:
        try:
            result = await session.execute(
                select(WorkflowNode.node_key).where(
                    and_(WorkflowNode.workflow_id == workflow_id, WorkflowNode.node_key.in_(node_keys))
                )
            )
            found_keys = result.scalars().all()

            if len(found_keys) != len(node_keys):
                missing_keys = set(node_keys) - set(found_keys)
                raise WorkflowErrorCode.WORKFLOW_NODE_NOT_FOUND.exception(
                    data={"missing_node_keys": list(missing_keys)}, status_code=status.HTTP_404_NOT_FOUND
                )

            await session.execute(
                delete(WorkflowNode).where(
                    and_(WorkflowNode.workflow_id == workflow_id, WorkflowNode.node_key.in_(node_keys))
                )
            )
            await session.flush()
            return node_keys
        except Exception as e:
            logger.error(f"Error batch deleting workflow nodes: {e}")
            raise WorkflowErrorCode.WORKFLOW_NODE_DELETE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def _batch_delete_workflow_edges(
        session: AsyncSession,
        edge_keys: list[str],
        workflow_id: str,
    ) -> list[str]:
        try:
            result = await session.execute(
                select(WorkflowEdge.edge_key).where(
                    and_(WorkflowEdge.workflow_id == workflow_id, WorkflowEdge.edge_key.in_(edge_keys))
                )
            )
            found_keys = result.scalars().all()

            if len(found_keys) != len(edge_keys):
                missing_keys = set(edge_keys) - set(found_keys)
                raise WorkflowErrorCode.WORKFLOW_EDGE_NOT_FOUND.exception(
                    data={"missing_edge_keys": list(missing_keys)}, status_code=status.HTTP_404_NOT_FOUND
                )

            await session.execute(
                delete(WorkflowEdge).where(
                    and_(WorkflowEdge.workflow_id == workflow_id, WorkflowEdge.edge_key.in_(edge_keys))
                )
            )
            await session.flush()
            return edge_keys
        except Exception as e:
            logger.error(f"Error batch deleting workflow edges: {e}")
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
    ) -> SaveWorkflowResponse:
        _, _, user = await TenantService.get_tenant_and_user(session=session, request=request)

        try:
            workflow = await WorkflowService.get_workflow(session=session, workflow_id=workflow_id)

            updated_nodes = []
            updated_edges = []
            deleted_nodes = []
            deleted_edges = []

            if payload.update_nodes:
                node_keys = [node.node_key for node in payload.update_nodes]
                existing_result = await session.execute(
                    select(WorkflowNode).where(
                        and_(WorkflowNode.workflow_id == workflow_id, WorkflowNode.node_key.in_(node_keys))
                    )
                )
                existing_nodes = existing_result.scalars().all()
                existing_keys = {node.node_key for node in existing_nodes}

                nodes_to_create = [node for node in payload.update_nodes if node.node_key not in existing_keys]
                nodes_to_update = [node for node in payload.update_nodes if node.node_key in existing_keys]

                if nodes_to_create:
                    created_nodes = await WorkflowService._batch_create_workflow_nodes(
                        session=session, payloads=nodes_to_create, workflow_id=workflow_id, user=user
                    )
                    updated_nodes.extend([WorkflowService.serialize_workflow_node(node) for node in created_nodes])

                if nodes_to_update:
                    updated_existing_nodes = await WorkflowService._batch_update_workflow_nodes(
                        session=session, payloads=nodes_to_update, workflow_id=workflow_id, user=user
                    )
                    updated_nodes.extend(
                        [WorkflowService.serialize_workflow_node(node) for node in updated_existing_nodes]
                    )

            if payload.update_edges:
                edge_keys = [edge.edge_key for edge in payload.update_edges]
                existing_result = await session.execute(
                    select(WorkflowEdge).where(
                        and_(WorkflowEdge.workflow_id == workflow_id, WorkflowEdge.edge_key.in_(edge_keys))
                    )
                )
                existing_edges = existing_result.scalars().all()
                existing_keys = {edge.edge_key for edge in existing_edges}

                edges_to_create = [edge for edge in payload.update_edges if edge.edge_key not in existing_keys]
                edges_to_update = [edge for edge in payload.update_edges if edge.edge_key in existing_keys]

                if edges_to_create:
                    created_edges = await WorkflowService._batch_create_workflow_edges(
                        session=session, payloads=edges_to_create, workflow_id=workflow_id, user=user
                    )
                    updated_edges.extend([WorkflowService.serialize_workflow_edge(edge) for edge in created_edges])

                if edges_to_update:
                    updated_existing_edges = await WorkflowService._batch_update_workflow_edges(
                        session=session, payloads=edges_to_update, workflow_id=workflow_id, user=user
                    )
                    updated_edges.extend(
                        [WorkflowService.serialize_workflow_edge(edge) for edge in updated_existing_edges]
                    )

            if payload.delete_nodes:
                deleted_nodes = await WorkflowService._batch_delete_workflow_nodes(
                    session=session, node_keys=payload.delete_nodes, workflow_id=workflow_id
                )

            if payload.delete_edges:
                deleted_edges = await WorkflowService._batch_delete_workflow_edges(
                    session=session, edge_keys=payload.delete_edges, workflow_id=workflow_id
                )

            if payload.config:
                workflow.config = payload.config

            workflow.updated_by = user.id
            workflow.status = WorkflowStatus.DRAFT
            await workflow.save(session)

            result = SaveWorkflowResponse(
                update_nodes=updated_nodes or None,
                update_edges=updated_edges or None,
                delete_nodes=deleted_nodes or None,
                delete_edges=deleted_edges or None,
                config=workflow.config,
                updated_at=workflow.updated_at,
                updated_by=workflow.updated_by,
            )
            await session.commit()
            return result
        except Exception as e:
            logger.error(f"Error saving workflow: {e}")
            await session.rollback()
            raise WorkflowErrorCode.WORKFLOW_SAVE_ERROR.exception(
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
            snapshot, snapshot_hash = await workflow.get_snapshot(session=session, need_hash=True)
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
        snapshot: dict,
        snapshot_hash: str,
        start_node_key: str,
        end_node_key: str,
        input_data: dict,
        execution_context: dict,
        version: str | None = None,
        snapshot_timestamp: datetime | None = None,
        is_debug: bool = False,
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

        try:
            executor = WorkflowEngine(
                workflow_id=str(workflow_id),
                version=version,
                is_debug=is_debug,
                timestamp=snapshot_timestamp,
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
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            raise WorkflowErrorCode.WORKFLOW_EXECUTION_ERROR.exception(
                data={"workflow_id": str(workflow_id), "message": "Failed to execute workflow"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e
