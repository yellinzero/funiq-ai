from collections.abc import Generator
from typing import Dict, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.model_provider import Model, ModelProvider
from infrastructure import with_session
from providers.models.core import LargeLanguageModel, ProviderFactory
from providers.models.core.schemas import LLMResult, ModelType, UserPromptMessage

from ..core import OperatorName
from ..core.base_operator import BaseOperator


class LLMOperator(BaseOperator):
    """LLM operator implementation"""

    operator_name = OperatorName.LLM.value

    @with_session
    async def _execute(self, config: Dict | None, session: AsyncSession, **kwargs):
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
        model = await self._get_model(session, config["model_id"])

        if not model:
            raise ValueError(f"Model {config['model_id']} not found")

        if not model.is_active:
            raise ValueError(f"Model {model.model} is not active")

        # Get credentials - first try model credentials, if None then get provider credentials
        credentials = model.credentials
        if credentials is None:
            # Modify the query to get the full provider object
            provider_stmt = select(ModelProvider).join(Model).where(Model.id == model.id)
            provider_result = await session.execute(provider_stmt)
            provider_obj = provider_result.scalar_one()
            credentials = provider_obj.credentials

        # Get model provider instance
        provider = ProviderFactory.get_provider_instance(model.provider)

        # Get model instance
        model_instance: LargeLanguageModel = provider.get_model_instance(ModelType.LLM)

        # Prepare prompt and messages
        prompt = config.get("prompt", "")
        messages = [UserPromptMessage(content=prompt)]

        # Extract model parameters from config
        model_parameters = config.get("model_parameters", {})
        # Execute model using invoke instead of _invoke
        result: Union[LLMResult, Generator] = model_instance.invoke(
            model=model.model,
            credentials=credentials,
            prompt_messages=messages,
            model_parameters=model_parameters,
            tools=None,
            stop=None,
            stream=self.is_stream,
            user=None,
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

    async def _get_model(self, session: AsyncSession, model_id: str) -> Model:
        """Get model info from database"""
        stmt = select(Model).where(Model.id == model_id)
        result = await session.execute(stmt)
        model = result.scalar_one_or_none()
        return model