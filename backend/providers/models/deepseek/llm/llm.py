from collections.abc import Generator
from typing import Any, Union
from urllib.parse import urlparse

import tiktoken

from providers.models.core.schemas import (
    LLMResult,
    PromptMessage,
    PromptMessageTool,
)
from providers.models.openai.llm.llm import OpenAILargeLanguageModel


class DeepSeekLargeLanguageModel(OpenAILargeLanguageModel):
    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: list[PromptMessageTool] | None = None,
        stop: list[str] | None = None,
        stream: bool = True,
        user: str | None = None,
    ) -> Union[LLMResult, Generator]:
        self._add_custom_parameters(credentials)

        return super()._invoke(model, credentials, prompt_messages, model_parameters, tools, stop, stream, user)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        self._add_custom_parameters(credentials)
        super().validate_credentials(model, credentials)

    # refactored from openai model runtime, use cl100k_base for calculate token number
    def _num_tokens_from_string(self, model: str, text: str, tools: list[PromptMessageTool] | None = None) -> int:
        """
        Calculate num tokens for text completion model with tiktoken package.

        :param model: model name
        :param text: prompt text
        :param tools: tools for tool calling
        :return: number of tokens
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(text))

        if tools:
            num_tokens += self._num_tokens_for_tools(encoding, tools)

        return num_tokens

    # refactored from openai model runtime, use cl100k_base for calculate token number
    def _num_tokens_from_messages(
        self, model: str, messages: list[PromptMessage], tools: list[PromptMessageTool] | None = None
    ) -> int:
        """Calculate num tokens for chat models with tiktoken package."""
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens_per_message = 3
        tokens_per_name = 1

        num_tokens = 0
        messages_dict = [self._convert_prompt_message_to_dict(m) for m in messages]
        for message in messages_dict:
            num_tokens += tokens_per_message
            for key, value in message.items():
                # Handle list type content (e.g., for multi-modal messages)
                if isinstance(value, list):
                    text = "".join(
                        item["text"] for item in value 
                        if isinstance(item, dict) and item["type"] == "text"
                    )
                    value = text

                # Handle tool calls
                if key == "tool_calls":
                    num_tokens += self._calculate_tool_calls_tokens(value, encoding)
                else:
                    num_tokens += len(encoding.encode(str(value)))

                if key == "name":
                    num_tokens += tokens_per_name

        # every reply is primed with <im_start>assistant
        num_tokens += 3

        if tools:
            num_tokens += self._num_tokens_for_tools(encoding, tools)

        return num_tokens

    def _calculate_tool_calls_tokens(self, tool_calls: list, encoding: Any) -> int:
        """Helper method to calculate tokens for tool calls."""
        num_tokens = 0
        for tool_call in tool_calls:
            for t_key, t_value in tool_call.items():
                num_tokens += len(encoding.encode(t_key))
                if t_key == "function":
                    for f_key, f_value in t_value.items():
                        num_tokens += len(encoding.encode(f_key))
                        num_tokens += len(encoding.encode(f_value))
                else:
                    num_tokens += len(encoding.encode(t_key))
                    num_tokens += len(encoding.encode(t_value))
        return num_tokens

    @staticmethod
    def _add_custom_parameters(credentials: dict) -> None:
        credentials["mode"] = "chat"
        credentials["openai_api_key"] = credentials["api_key"]
        if "endpoint_url" not in credentials or not credentials["endpoint_url"]:
            credentials["openai_api_base"] = "https://api.deepseek.com"
        else:
            parsed_url = urlparse(credentials["endpoint_url"])
            credentials["openai_api_base"] = f"{parsed_url.scheme}://{parsed_url.netloc}"
