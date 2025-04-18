import json
import sys

from loguru import logger

from providers.models.core import AIModel
from providers.models.core.callbacks import Callback
from providers.models.core.schemas import LLMResult, LLMResultChunk, PromptMessage, PromptMessageTool


class LoggingCallback(Callback):
    def on_before_invoke(
        self,
        llm_instance: AIModel,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: list[PromptMessageTool] | None = None,
        stop: list[str] | None = None,
        stream: bool = True,
        user: str | None = None,
    ) -> None:
        """
        Before invoke callback

        :param llm_instance: LLM instance
        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        """
        logger.info("\n[on_llm_before_invoke]")
        logger.info(f"Model: {model}")
        logger.info("Parameters:")
        for key, value in model_parameters.items():
            logger.info(f"\t{key}: {value}")

        if stop:
            logger.info(f"\tstop: {stop}")

        if tools:
            logger.info("\tTools:")
            for tool in tools:
                logger.info(f"\t\t{tool.name}")

        logger.info(f"Stream: {stream}")

        if user:
            logger.info(f"User: {user}")

        logger.info("Prompt messages:")
        for prompt_message in prompt_messages:
            if prompt_message.name:
                logger.info(f"\tname: {prompt_message.name}")
            logger.info(f"\trole: {prompt_message.role.value}")
            logger.info(f"\tcontent: {prompt_message.content}")

        if stream:
            logger.info("\n[on_llm_new_chunk]")

    def on_new_chunk(
        self,
        llm_instance: AIModel,
        chunk: LLMResultChunk,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: list[PromptMessageTool] | None = None,
        stop: list[str] | None = None,
        stream: bool = True,
        user: str | None = None,
    ):
        """
        On new chunk callback

        :param llm_instance: LLM instance
        :param chunk: chunk
        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        """
        sys.stdout.write(chunk.delta.message.content)
        sys.stdout.flush()

    def on_after_invoke(
        self,
        llm_instance: AIModel,
        result: LLMResult,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: list[PromptMessageTool] | None = None,
        stop: list[str] | None = None,
        stream: bool = True,
        user: str | None = None,
    ) -> None:
        """
        After invoke callback

        :param llm_instance: LLM instance
        :param result: result
        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        """
        logger.info("\n[on_llm_after_invoke]")
        logger.info(f"Content: {result.message.content}")

        if result.message.tool_calls:
            logger.info("Tool calls:")
            for tool_call in result.message.tool_calls:
                logger.info(f"\t{tool_call.id}")
                logger.info(f"\t{tool_call.function.name}")
                logger.info(f"\t{json.dumps(tool_call.function.arguments)}")

        logger.info(f"Model: {result.model}")
        logger.info(f"Usage: {result.usage}")
        logger.info(f"System Fingerprint: {result.system_fingerprint}")

    def on_invoke_error(
        self,
        llm_instance: AIModel,
        ex: Exception,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: list[PromptMessageTool] | None = None,
        stop: list[str] | None = None,
        stream: bool = True,
        user: str | None = None,
    ) -> None:
        """
        Invoke error callback

        :param llm_instance: LLM instance
        :param ex: exception
        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        """
        logger.error("\n[on_llm_invoke_error]")
        logger.exception(ex)
