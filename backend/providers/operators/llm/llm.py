from collections.abc import Generator
from typing import Dict, Union

from fastapi_async_sqlalchemy import db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_providers import Model
from providers.models.core.large_language_model import LargeLanguageModel
from providers.models.core.models.llm import LLMResult
from providers.models.core.models.message import UserPromptMessage
from providers.models.core.models.model import ModelType
from providers.models.core.provider_factory import ProviderFactory

from ..core.base_operator import BaseOperator


class LLMOperator(BaseOperator):
    """LLM operator implementation"""
    operator_name = "llm"
        
    async def execute(self, input_data: Dict, config: Dict) -> Dict:
        """
        Execute the LLM operator
        
        Args:
            input_data: Input containing prompt and context
            config: Configuration for the LLM including model_id, prompt, and parameters
            
        Returns:
            Dict containing the LLM response and metadata
        """
        # Get model info from database using FastAPI's async SQLAlchemy session
        model = await self._get_model(db.session, config['model'])
        
        if not model:
            raise ValueError(f"Model {config['model']} not found")
            
        if not model.is_active:
            raise ValueError(f"Model {model.model} is not active")

        # Get model provider instance
        provider = ProviderFactory.get_provider_instance(model.provider)
        
        # Get model instance
        model_instance: LargeLanguageModel = provider.get_model_instance(ModelType.LLM)
        
        # Prepare prompt and messages
        prompt = config.get('prompt', '')
        messages = [UserPromptMessage(content=prompt)]
        
        # Extract model parameters from config
        model_parameters = config.get('model_parameters', {})
        
        # Get stream parameter, default to False
        stream = config.get('stream', False)
        
        # Execute model using invoke instead of _invoke
        result: Union[LLMResult, Generator] = await model_instance.invoke(
            model=model.model,
            credentials=model.credentials or model.provider_obj.credentials,
            prompt_messages=messages,
            model_parameters=model_parameters,
            tools=None,
            stop=None,
            stream=stream,
            user=None
        )
        
        # Handle streaming response
        if stream:
            return {
                "type": "stream",
                "generator": result
            }
        
        # Return regular response
        return {
            "type": "text",
            "answer": result.message.content,
            "usage": result.usage.model_dump() if result.usage else None
        }
        
    async def _get_model(self, session: AsyncSession, model_id: str) -> Model:
        """Get model info from database"""
        stmt = select(Model).where(Model.id == model_id)
        result = await session.execute(stmt)
        model = result.scalar_one_or_none()
        return model
        