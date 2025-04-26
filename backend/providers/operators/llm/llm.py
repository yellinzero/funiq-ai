from collections.abc import Generator
from typing import Dict, Union

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.model_provider import ModelProvider
from infrastructure import with_session
from providers.models.core import LargeLanguageModel, ProviderFactory
from providers.models.core.schemas import (
    AudioPromptMessageContent,
    FilePromptMessageContent,
    ImagePromptMessageContent,
    LLMResult,
    ModelType,
    PromptMessage,
    PromptMessageContent,
    PromptMessageContentType,
    SystemPromptMessage,
    UserPromptMessage,
)

from ..core import OperatorName
from ..core.base_operator import BaseOperator


class LLMOperator(BaseOperator):
    """LLM operator implementation"""

    operator_name = OperatorName.LLM.value

    @with_session
    async def _execute(self, config: Dict | None, session: AsyncSession, execution_context: Dict, **kwargs):
        """
        Execute the LLM operator

        Args:
            config: Configuration for the LLM including model_id, prompt, and parameters
            session: Database session (injected by with_session decorator)

        Returns:
            Dict containing the LLM response and metadata
        """
        if not config:
            raise ValueError("Config is required")

        # Get model info from database using provided session
        model = config["model"]
        provider_name = model.get("provider")
        model_name = model.get("model")
        tenant_id = execution_context.get("tenant_id")

        if not tenant_id:
            raise ValueError("Tenant ID is required")

        # Get model provider instance
        provider_instance = ProviderFactory.get_provider_instance(provider_name=provider_name)
        credentials = await self._get_provider_credentials(
            session=session, provider_name=provider_name, tenant_id=tenant_id
        )

        user_name = execution_context.get("user_name")

        # Get model instance
        model_instance: LargeLanguageModel = provider_instance.get_model_instance(ModelType.LLM)

        tool_list = config.get("tool_list")
        tools = []
        if tool_list:
            # TODO support tool calling
            pass
        
        # Extract model parameters from config
        model_parameters = config.get("model_parameters", {})
        # Execute model using invoke instead of _invoke
        result: Union[LLMResult, Generator] = model_instance.invoke(
            model=model_name,
            credentials=credentials,
            prompt_messages=self._handle_message(config),
            model_parameters=model_parameters,
            tools=tools,
            stop=config.get("stop"),
            stream=self.is_stream,
            user=user_name,
        )

        if self.is_stream:
            if not isinstance(result, Generator):
                raise ValueError("LLM operator stream result is not a generator")

            def generator():
                yield from result

            return generator()
        else:
            # Return regular response
            if not self.validate_output(result):
                raise ValueError("Output validation failed")

            return result

    @with_session
    async def _get_provider_credentials(self, session: AsyncSession, provider_name: str, tenant_id: str):
        """
        Get the provider credentials from the LLM result
        """
        provider = await session.execute(
            select(ModelProvider).where(
                and_(ModelProvider.provider == provider_name, ModelProvider.tenant_id == tenant_id)
            )
        )
        provider = provider.scalar_one_or_none()

        if not provider:
            raise ValueError("Provider not found")

        if not provider.is_active:
            raise ValueError("Provider is not active")

        return provider.credentials
    
    def _handle_message(self, config: Dict) -> list[PromptMessage]:
        # Prepare query and messages
        query = config.get("query", "")
        user_messages = [PromptMessageContent(type=PromptMessageContentType.TEXT, data=query)]

        messages = []

        prompt = config.get("prompt", "")
        if prompt:
            messages.append(SystemPromptMessage(content=prompt))

        image_list = config.get("image_list")
        if image_list:
            for image in image_list:
                data = image.get("data")
                detail = image.get("detail")
                user_messages.append(
                    ImagePromptMessageContent(data=data, detail=detail)
                )

        audio_list = config.get("audio_list")
        if audio_list:
            for audio in audio_list:
                data = audio.get("data")
                format = audio.get("format")
                user_messages.append(AudioPromptMessageContent(data=data, format=format))

        file_list = config.get("file_list")
        if file_list:
            for file in file_list:
                data = file.get("data")
                file_name = file.get("file_name")
                user_messages.append(FilePromptMessageContent(data=data, file_name=file_name))

        if len(user_messages) > 1:
            messages.append(UserPromptMessage(content=user_messages))
        else:
            user_message_data = user_messages[0].data
            messages.append(UserPromptMessage(content=user_message_data))
            
        return messages
