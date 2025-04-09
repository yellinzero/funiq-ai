from collections.abc import Generator
from typing import Dict, Union

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.model_provider import Model, ModelProvider
from app.core.models.workflow import WorkflowNodeDebugExecution, WorkflowNodeExecution
from infrastructure import with_session
from providers.models.core.large_language_model import LargeLanguageModel
from providers.models.core.models.llm import LLMResult
from providers.models.core.models.message import UserPromptMessage
from providers.models.core.models.model import ModelType
from providers.models.core.provider_factory import ProviderFactory
from utils.common.json import json_dumps

from ..core.base_operator import BaseOperator


class LLMOperator(BaseOperator):
    """LLM operator implementation"""

    operator_name = "llm"

    @with_session
    async def _execute(self, config: Dict, session: AsyncSession, execution_context: Dict) -> Dict:
        """
        Execute the LLM operator

        Args:
            config: Configuration for the LLM including model_id, prompt, and parameters
            session: Database session (injected by with_session decorator)

        Returns:
            Dict containing the LLM response and metadata
        """
        logger.debug(f"LLM operator config: {config}")
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
            stream=False,
            user=None,
        )

        output = {
            "type": "text",
            "answer": result.message.content,
            "usage": result.usage.model_dump() if result.usage else None,
        }

        # Return regular response
        if not self.validate_output(output):
            raise ValueError("Output validation failed")

        await self._update_node_execution_record(session=session, execution_context=execution_context, output=output)
        logger.debug(f"LLM operator result: {output}")
        return output

    async def _get_model(self, session: AsyncSession, model_id: str) -> Model:
        """Get model info from database"""
        stmt = select(Model).where(Model.id == model_id)
        result = await session.execute(stmt)
        model = result.scalar_one_or_none()
        return model

    async def _update_node_execution_record(self, session: AsyncSession, execution_context: Dict, output: Dict) -> None:
        """Update node execution record with LLM specific information.

        Args:
            session: Database session
            execution_context: Execution context containing execution details
            output: Output from LLM execution
        """
        # Extract the information needed for the execution record
        record_info = json_dumps({"type": output["type"], "usage": output["usage"]})

        # according to whether there is a snapshot_timestamp to determine whether it is a debug execution
        if "snapshot_timestamp" in execution_context:
            # debug execution
            stmt = (
                update(WorkflowNodeDebugExecution)
                .where(
                    WorkflowNodeDebugExecution.execution_id == execution_context["execution_id"],
                    WorkflowNodeDebugExecution.node_key == execution_context["node_key"],
                    WorkflowNodeDebugExecution.task_run_id == execution_context["task_run_id"],
                )
                .values(record_info=record_info)
            )
        else:
            # normal execution record
            stmt = (
                update(WorkflowNodeExecution)
                .where(
                    WorkflowNodeExecution.execution_id == execution_context["execution_id"],
                    WorkflowNodeExecution.node_key == execution_context["node_key"],
                    WorkflowNodeExecution.task_run_id == execution_context["task_run_id"],
                )
                .values(record_info=record_info)
            )

        try:
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to update node execution record: {e}")
            await session.rollback()
            raise
