from typing import AsyncIterator, List

from fastapi import Request, status
from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.account.service.tenant_service import TenantService
from app.app.service.app_service import AppService
from app.conversation.schemas import ConversationCreate, ConversationUpdate
from app.core.errors import AccountErrorCode, AppErrorCode, ConversationErrorCode
from app.core.models.conversation import Conversation, ConversationStatus, Message, MessageFrom
from app.workflow.service.workflow_service import WorkflowService
from infrastructure import StreamHandler
from infrastructure.workflow_engine import FlowExecutionCallbackContext
from providers.operators.end.schema import EndOperatorStreamOutput
from utils.common.datetime import utcnow


class ConversationService:
    @staticmethod
    async def get_conversations(
        session: AsyncSession,
        request: Request
    ) -> List[Conversation]:
        """get all conversations"""
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        account_id = request.state.account_id
        user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)
        
        result = await session.execute(
            select(Conversation)
            .where(and_(Conversation.created_by == user.id, Conversation.tenant_id == tenant_id))
            .order_by(Conversation.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_conversation(
        session: AsyncSession,
        conversation_id: str,
    ) -> Conversation:
        """get a single conversation detail"""        
        result = await session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
        )
        
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise ConversationErrorCode.CONVERSATION_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        return conversation

    @staticmethod
    async def create_conversation(
        session: AsyncSession,
        conversation: ConversationCreate,
        request: Request
    ) -> Conversation:
        """create a new conversation"""
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        account_id = request.state.account_id
        user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)

        try:
            new_conversation = Conversation(
                name=conversation.name,
                tenant_id=tenant_id,
                status=ConversationStatus.ACTIVE,
                created_by=user.id,
                updated_by=user.id,
                message_count=0
            )
            await new_conversation.save(session)
            await session.commit()
            return new_conversation
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            await session.rollback()
            raise ConversationErrorCode.CONVERSATION_CREATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def update_conversation(
        session: AsyncSession,
        conversation_id: str,
        conversation_update: ConversationUpdate,
        request: Request
    ) -> Conversation:
        """update conversation information"""
        conversation = await ConversationService.get_conversation(
            session=session, conversation_id=conversation_id
        )
        
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        account_id = request.state.account_id
        user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)

        try:
            conversation.name = conversation_update.name
            conversation.updated_by = user.id
            conversation.updated_at = utcnow()
            
            return conversation
        except Exception as e:
            logger.error(f"Error updating conversation: {e}")
            await session.rollback()
            raise ConversationErrorCode.CONVERSATION_UPDATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def delete_conversation(
        session: AsyncSession,
        conversation_id: str,
        request: Request
    ) -> None:
        """delete conversation"""
        conversation = await ConversationService.get_conversation(
            session=session, conversation_id=conversation_id
        )
        
        try:
            await session.delete(conversation)
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            await session.rollback()
            raise ConversationErrorCode.CONVERSATION_DELETE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e
    
    @staticmethod
    async def get_messages(
        session: AsyncSession,
        conversation_id: str,
        request: Request
    ) -> List[Message]:
        """get all messages of a conversation"""
        conversation = await ConversationService.get_conversation(
            session=session, conversation_id=conversation_id
        )
        
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def completion(
        session: AsyncSession,
        app_version_id: str,
        conversation_id: str,
        message: str,
        request: Request
    ) -> AsyncIterator[str]:
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        account_id = request.state.account_id
        user = await TenantService.get_user_by_account_id(session, tenant_id, account_id)
        
        """completation"""
        conversation = await ConversationService.get_conversation(
            session=session, conversation_id=conversation_id
        )
        
        if not conversation.is_active:
            raise ConversationErrorCode.CONVERSATION_NOT_ACTIVE.exception(
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        app_version = await AppService.get_app_version(
            session=session, app_version_id=app_version_id
        )
        
        if not app_version.is_active:
            raise AppErrorCode.APP_VERSION_NOT_ACTIVE.exception(
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        snapshot = app_version.snapshot
            
        # Create a new message from the user
        new_message = Message(
            conversation_id=conversation.id,
            app_version_id=app_version.id,
            content=message,
            message_from=MessageFrom.USER,
            created_by=user.id,
        )
        await new_message.save(session)
        
        app_message = Message(
            conversation_id=conversation.id,
            app_version_id=app_version.id,
            content="",
            message_from=MessageFrom.APP,
        )
        await app_message.save(session)
        conversation.last_message_id = app_message.id
        conversation.message_count += 2
        conversation.updated_at = utcnow().replace(tzinfo=None)
        await conversation.save(session)
        await session.flush()
        await session.commit()
        
        async def on_created(context: FlowExecutionCallbackContext):
            app_message.execution_id = context.flow._execution_id
            await app_message.save(session)
            await session.flush()
            await session.commit()
            
        executor = await WorkflowService.execute_workflow_stream(
            session=session,
            request=request,
            workflow_id=str(app_version.workflow_id),
            version=app_version.workflow_version,
            input_data={"query": message},
            execution_context={
                "conversation_id": str(conversation.id),
                "user_id": str(user.id),
                "user_name": user.name,
                "tenant_id": str(tenant_id),
                "support_file": snapshot.get("support_file", False),
                "support_image": snapshot.get("support_image", False),
                "support_audio": snapshot.get("support_audio", False),
                "support_thinking": snapshot.get("support_thinking", False),
                "support_tool": snapshot.get("support_tool", False),
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
            chunk_type=EndOperatorStreamOutput,
            on_chunk=on_chunk,
            on_finish=on_finish,
            on_error=on_error
        )
        
        return handler.process_stream(stream, executor)
        
        
        
        