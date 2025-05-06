from typing import AsyncIterator, List

from fastapi import Request, status
from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.account.service.tenant_service import TenantService
from app.app.service.app_service import AppService
from app.core.errors import AppErrorCode, WorkflowErrorCode
from app.core.models.app import Conversation, ConversationStatus, Message, MessageFrom
from app.core.models.workflow import WorkflowVersion, WorkflowVersionStatus
from app.workflow.service.workflow_service import WorkflowService
from infrastructure import StreamHandler
from infrastructure.workflow_engine import FlowExecutionCallbackContext
from providers.operators.end.schema import EndOperatorStreamOutput
from utils.common.datetime import utcnow

from ..schemas import (
    CompletionRequest,
    ConversationInfo,
    ConversationListResponse,
    CreateConversationRequest,
    MessageInfo,
    UpdateConversationRequest,
)


class ConversationService:
    @staticmethod
    def message_to_info(message: Message) -> MessageInfo:
        return MessageInfo(**message.to_dict(convert_uuid_to_str=True))

    @staticmethod
    def conversation_to_info(conversation: Conversation) -> ConversationInfo:
        return ConversationInfo(**conversation.to_dict(convert_uuid_to_str=True))

    @staticmethod
    async def update_conversation_when_message_created(
        session: AsyncSession, conversation: Conversation, new_message: Message
    ) -> Conversation:
        """update conversation when message created"""
        conversation.last_message_id = new_message.id
        conversation.message_count += 1
        await conversation.save(session)
        await session.flush()
        return conversation

    @staticmethod
    async def get_conversations(
        session: AsyncSession,
        app_id: str,
        page: int = 1,
        page_size: int = 20,
        search_term: str | None = None,
    ) -> ConversationListResponse:
        """get all conversations"""

        try:
            query = select(Conversation).where(Conversation.app_id == app_id)
            count_query = select(func.count()).select_from(Conversation).where(Conversation.app_id == app_id)

            # Add search condition if provided
            if search_term:
                search_filter = or_(
                    Conversation.name.ilike(f"%{search_term}%"), Conversation.description.ilike(f"%{search_term}%")
                )
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)

            total_result = await session.execute(count_query)
            total = total_result.scalar_one()
            # Add pagination and ordering
            offset = (page - 1) * page_size
            query = query.order_by(Conversation.created_at.desc()).offset(offset).limit(page_size)

            result = await session.execute(query)
            conversations = result.scalars().all()

            conversations_responses = []
            for conversation in conversations:
                conversations_responses.append(ConversationService.conversation_to_info(conversation))

            return ConversationListResponse(conversations=conversations_responses, total=total)

        except Exception as e:
            logger.error(f"Error fetching conversations: {e}")
            raise AppErrorCode.CONVERSATION_FETCH_FAILED.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_conversation(
        session: AsyncSession,
        conversation_id: str,
    ) -> Conversation:
        """get a single conversation detail"""
        result = await session.execute(select(Conversation).where(Conversation.id == conversation_id))

        conversation = result.scalar_one_or_none()
        if not conversation:
            raise AppErrorCode.CONVERSATION_NOT_FOUND.exception(status_code=status.HTTP_404_NOT_FOUND)

        return conversation

    @staticmethod
    async def create_conversation(
        session: AsyncSession, app_id: str, payload: CreateConversationRequest, request: Request
    ) -> Conversation:
        """create a new conversation"""
        tenant_id, _, user = await TenantService.get_tenant_and_user(session=session, request=request)
        name = payload.name or "New chat"

        app = await AppService.get_app(session=session, app_id=app_id, request=request)
        if app.is_archived:
            raise AppErrorCode.APP_ARCHIVED.exception(status_code=status.HTTP_400_BAD_REQUEST)
        if app.is_inactive:
            raise AppErrorCode.APP_INACTIVE.exception(status_code=status.HTTP_400_BAD_REQUEST)

        try:
            new_conversation = Conversation(
                name=name,
                description=payload.description,
                app_id=app_id,
                tenant_id=tenant_id,
                status=ConversationStatus.ACTIVE,
                created_by=user.id,
                updated_by=user.id,
                message_count=0,
            )
            await new_conversation.save(session)
            await session.flush()
            conversation_info = ConversationService.conversation_to_info(new_conversation)
            await session.commit()
            return conversation_info
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            await session.rollback()
            raise AppErrorCode.CONVERSATION_CREATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}
            ) from e

    @staticmethod
    async def update_conversation(
        session: AsyncSession, conversation_id: str, payload: UpdateConversationRequest, request: Request
    ) -> ConversationInfo:
        """update conversation information"""
        _, _, user = await TenantService.get_tenant_and_user(session=session, request=request)
        conversation = await ConversationService.get_conversation(session=session, conversation_id=conversation_id)

        try:
            if payload.name:
                conversation.name = payload.name
            if payload.description:
                conversation.description = payload.description
            conversation.updated_by = user.id

            await conversation.save(session)
            await session.flush()
            conversation_info = ConversationService.conversation_to_info(conversation)
            await session.commit()

            return conversation_info
        except Exception as e:
            logger.error(f"Error updating conversation: {e}")
            await session.rollback()
            raise AppErrorCode.CONVERSATION_UPDATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}
            ) from e

    @staticmethod
    async def delete_conversation(session: AsyncSession, conversation_id: str, request: Request) -> None:
        """delete conversation"""
        conversation = await ConversationService.get_conversation(session=session, conversation_id=conversation_id)

        try:
            await conversation.delete(session)
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            await session.rollback()
            raise AppErrorCode.CONVERSATION_DELETE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}
            ) from e

    @staticmethod
    async def get_messages(session: AsyncSession, conversation_id: str, request: Request) -> List[MessageInfo]:
        """get all messages of a conversation"""
        try:
            result = await session.execute(
                select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.desc())
            )
            messages = result.scalars().all()
            messages_responses = []
            for message in messages:
                messages_responses.append(ConversationService.message_to_info(message))

            return messages_responses
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            raise AppErrorCode.MESSAGE_FETCH_FAILED.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}
            ) from e

    @staticmethod
    async def completion(
        session: AsyncSession, conversation_id: str, payload: CompletionRequest, request: Request
    ) -> AsyncIterator[str]:
        """completion with streaming response"""
        tenant_id, _, user = await TenantService.get_tenant_and_user(session, request)
        conversation = await ConversationService.get_conversation(session=session, conversation_id=conversation_id)

        if conversation.is_archived:
            raise AppErrorCode.CONVERSATION_ARCHIVED.exception(status_code=status.HTTP_400_BAD_REQUEST)

        version_result = await session.execute(
            select(WorkflowVersion).where(WorkflowVersion.id == payload.workflow_version_id)
        )
        workflow_version = version_result.scalar_one_or_none()
        if not workflow_version:
            raise WorkflowErrorCode.WORKFLOW_VERSION_NOT_FOUND.exception(status_code=status.HTTP_404_NOT_FOUND)

        if workflow_version.status == WorkflowVersionStatus.ARCHIVED:
            raise WorkflowErrorCode.WORKFLOW_VERSION_ARCHIVED.exception(status_code=status.HTTP_400_BAD_REQUEST)

        if workflow_version.status == WorkflowVersionStatus.INACTIVE:
            raise WorkflowErrorCode.WORKFLOW_VERSION_NOT_ACTIVE.exception(status_code=status.HTTP_400_BAD_REQUEST)

        try:
            # Create a new message from the user
            new_message = Message(
                workflow_id=workflow_version.workflow_id,
            workflow_version=workflow_version.version,
            conversation_id=conversation.id,
            content=payload.message,
            message_from=MessageFrom.USER,
            created_by=user.id,
            )
            await new_message.save(session)
            await ConversationService.update_conversation_when_message_created(
                session=session, conversation=conversation, new_message=new_message
            )
            await session.commit()

            app_message = Message(
                conversation_id=conversation.id,
                workflow_id=workflow_version.workflow_id,
                workflow_version=workflow_version.version,
                content="",
                message_from=MessageFrom.APP,
            )

            await app_message.save(session)
            await ConversationService.update_conversation_when_message_created(
                session=session, conversation=conversation, new_message=app_message
            )
            await session.commit()

            async def on_created(context: FlowExecutionCallbackContext):
                app_message.workflow_run_id = context.flow._execution_id
                await app_message.save(session)
                await session.flush()
                await session.commit()
            workflow_config = workflow_version.snapshot.get("config", {}) or {}
            executor = await WorkflowService.execute_workflow_stream(
                session=session,
                workflow_id=workflow_version.workflow_id,
                version=workflow_version.version,
                snapshot=workflow_version.snapshot,
                snapshot_hash=workflow_version.snapshot_hash,
                start_node_key=workflow_version.start_node_key,
                end_node_key=workflow_version.end_node_key,
                input_data={"query": payload.message},
                execution_context={
                    "conversation_id": str(conversation.id),
                    "user_id": str(user.id),
                    "user_name": user.name,
                    "tenant_id": str(tenant_id),
                    **workflow_config,
                },
                on_created=[on_created],
            )

            await executor.initialize()
            stream = await executor.execute()
            content = ""

            def on_chunk(chunk: EndOperatorStreamOutput):
                nonlocal content
                content += chunk.message.content

            async def on_finish():
                app_message.content = content
                conversation.updated_at = utcnow().replace(tzinfo=None)
                await app_message.save(session)
                await conversation.save(session)
                await session.commit()

            async def on_error(e: Exception):
                error_message = {"error": str(e)}
                app_message.content = error_message
                conversation.updated_at = utcnow().replace(tzinfo=None)
                await app_message.save(session)
                await conversation.save(session)
                await session.commit()

            handler = StreamHandler(
                chunk_type=EndOperatorStreamOutput, on_chunk=on_chunk, on_finish=on_finish, on_error=on_error
            )

            return handler.process_stream(stream, executor)
        except Exception as e:
            logger.error(f"Error completing conversation: {e}")
            raise AppErrorCode.CONVERSATION_COMPLETION_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}
            ) from e
