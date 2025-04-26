from decimal import Decimal
from enum import Enum
from typing import Any, Union

from pydantic import BaseModel

from utils.common.i18n import TranslatableText
from utils.common.i18n import gettext_lazy as _


class ConfigurateMethod(Enum):
    """
    Enum class for configurate method of provider model.
    """

    PREDEFINED = "predefined"
    CUSTOMIZABLE = "customizable"


class ModelType(Enum):
    """
    Enum class for model type.
    """

    LLM = "llm"
    TEXT_EMBEDDING = "text-embedding"
    RERANK = "rerank"
    SPEECH2TEXT = "speech2text"
    MODERATION = "moderation"
    TTS = "tts"
    TEXT2IMG = "text2img"

    @classmethod
    def value_of(cls, origin_model_type: str) -> "ModelType":
        """
        Get model type from origin model type.

        :return: model type
        """
        if origin_model_type in {"text-generation", cls.LLM.value}:
            return cls.LLM
        elif origin_model_type in {"embeddings", cls.TEXT_EMBEDDING.value}:
            return cls.TEXT_EMBEDDING
        elif origin_model_type in {"reranking", cls.RERANK.value}:
            return cls.RERANK
        elif origin_model_type in {"speech2text", cls.SPEECH2TEXT.value}:
            return cls.SPEECH2TEXT
        elif origin_model_type in {"tts", cls.TTS.value}:
            return cls.TTS
        elif origin_model_type in {"text2img", cls.TEXT2IMG.value}:
            return cls.TEXT2IMG
        elif origin_model_type == cls.MODERATION.value:
            return cls.MODERATION
        else:
            raise ValueError(f"invalid origin model type {origin_model_type}")

    def to_origin_model_type(self) -> str:
        """
        Get origin model type from model type.

        :return: origin model type
        """
        if self == self.LLM:
            return "text-generation"
        elif self == self.TEXT_EMBEDDING:
            return "embeddings"
        elif self == self.RERANK:
            return "reranking"
        elif self == self.SPEECH2TEXT:
            return "speech2text"
        elif self == self.TTS:
            return "tts"
        elif self == self.MODERATION:
            return "moderation"
        elif self == self.TEXT2IMG:
            return "text2img"
        else:
            raise ValueError(f"invalid model type {self}")


class ModelFeature(Enum):
    """
    Enum class for llm feature.
    """

    TOOL_CALL = "tool-call"
    MULTI_TOOL_CALL = "multi-tool-call"
    AGENT_THOUGHT = "agent-thought"
    VISION = "vision"
    STREAM_TOOL_CALL = "stream-tool-call"


class ParameterType(Enum):
    """
    Enum class for parameter type.
    """

    FLOAT = "float"
    INT = "int"
    STRING = "string"
    BOOLEAN = "boolean"
    TEXT = "text"


class ModelPropertyKey(Enum):
    """
    Enum class for model property key.
    """

    MODE = "mode"
    CONTEXT_SIZE = "context_size"
    MAX_CHUNKS = "max_chunks"
    FILE_UPLOAD_LIMIT = "file_upload_limit"
    SUPPORTED_FILE_EXTENSIONS = "supported_file_extensions"
    MAX_CHARACTERS_PER_CHUNK = "max_characters_per_chunk"
    DEFAULT_VOICE = "default_voice"
    VOICES = "voices"
    WORD_LIMIT = "word_limit"
    AUDIO_TYPE = "audio_type"
    MAX_WORKERS = "max_workers"


class ProviderModel(BaseModel):
    """
    Model class for provider model.
    """

    model: str
    label: Union[str, TranslatableText]
    model_type: ModelType
    group: str | None = None
    features: list[ModelFeature] | None = None
    model_properties: dict[ModelPropertyKey, Any]
    deprecated: bool = False


class PriceConfig(BaseModel):
    """
    Model class for pricing info.
    """

    input: Decimal
    cached_input: Decimal | None = None
    output: Decimal | None = None
    unit: Decimal
    currency: str


class AIModelEntity(ProviderModel):
    """
    Model class for AI model.
    """

    parameter_rules_ui_schema: dict | None = None
    parameter_rules_schema: dict | None = None
    pricing: list[PriceConfig] | None = None


class ModelUsage(BaseModel):
    pass


class PriceType(Enum):
    """
    Enum class for price type.
    """

    INPUT = "input"
    OUTPUT = "output"


class PriceInfo(BaseModel):
    """
    Model class for price info.
    """

    unit_price: Decimal
    unit: Decimal
    total_amount: Decimal
    currency: str


class ParameterPropertyName(str, Enum):
    """
    Enum class for parameter template variable.
    """

    TEMPERATURE = "temperature"
    TOP_P = "top_p"
    TOP_K = "top_k"
    PRESENCE_PENALTY = "presence_penalty"
    FREQUENCY_PENALTY = "frequency_penalty"
    MAX_TOKENS = "max_tokens"
    RESPONSE_FORMAT = "response_format"
    JSON_SCHEMA = "json_schema"

    @classmethod
    def value_of(cls, value: Any) -> "ParameterPropertyName":
        """
        Get parameter name from value.

        :param value: parameter value
        :return: parameter name
        """
        for name in cls:
            if name.value == value:
                return name
        raise ValueError(f"invalid parameter name {value}")


# Keep this function lazy to avoid evaluating the translations prematurely
def get_parameter_template(name: ParameterPropertyName) -> dict:
    """Lazy initialization of parameter templates"""
    templates = {
        ParameterPropertyName.TEMPERATURE: lambda: {
            "type": "number",
            "title": _("Temperature", domain="providers"),
            "description": _(
                "Controls randomness. Lower temperature results in less random completions. "
                "As the temperature approaches zero, the model will become deterministic and repetitive. "
                "Higher temperature results in more random completions.",
                domain="providers",
            ),
            "default": 0.0,
            "minimum": 0.0,
            "maximum": 1.0,
            "multipleOf": 0.01,
        },
        ParameterPropertyName.TOP_P: lambda: {
            "type": "number",
            "title": _("Top P", domain="providers"),
            "description": _(
                "Controls diversity via nucleus sampling: 0.5 means half of all likelihood-weighted options "
                "are considered.",
                domain="providers",
            ),
            "default": 1.0,
            "minimum": 0.0,
            "maximum": 1.0,
            "multipleOf": 0.01,
        },
        ParameterPropertyName.TOP_K: lambda: {
            "type": "number",
            "title": _("Top K", domain="providers"),
            "description": _(
                "Limits the number of tokens to consider for each step by keeping only the k most likely tokens.",
                domain="providers",
            ),
            "default": 50,
            "minimum": 1,
            "maximum": 100,
        },
        ParameterPropertyName.PRESENCE_PENALTY: lambda: {
            "type": "number",
            "title": _("Presence Penalty", domain="providers"),
            "description": _(
                "Applies a penalty to the log-probability of tokens already in the text.",
                domain="providers"
            ),
            "default": 0.0,
            "minimum": 0.0,
            "maximum": 1.0,
            "multipleOf": 0.01,
        },
        ParameterPropertyName.FREQUENCY_PENALTY: lambda: {
            "type": "number",
            "title": _("Frequency Penalty", domain="providers"),
            "description": _(
                "Applies a penalty to the log-probability of tokens that appear in the text.",
                domain="providers"
            ),
            "default": 0.0,
            "minimum": 0.0,
            "maximum": 1.0,
            "multipleOf": 0.01,
        },
        ParameterPropertyName.MAX_TOKENS: lambda: {
            "type": "number",
            "title": _("Max Tokens", domain="providers"),
            "description": _(
                "Specifies the upper limit on the length of generated results. "
                "If the generated results are truncated, you can increase this parameter.",
                domain="providers",
            ),
            "default": 64,
            "minimum": 1,
            "maximum": 2048,
        },
        ParameterPropertyName.RESPONSE_FORMAT: lambda: {
            "type": "string",
            "title": _("Response Format", domain="providers"),
            "description": _(
                "Set a response format, ensure the output from llm is a valid code block as possible, "
                "such as JSON, XML, etc.",
                domain="providers",
            ),
            "enum": ["JSON", "XML"],
        },
        ParameterPropertyName.JSON_SCHEMA: lambda: {
            "type": "string",
            "title": _("JSON Schema", domain="providers"),
            "description": _(
                "Define a JSON schema to structure and validate the LLM's response. "
                "The schema should follow JSON Schema specification format.",
                domain="providers",
            ),
            "default": "{}",
        },
    }

    template_factory = templates.get(name)
    if not template_factory:
        raise ValueError(f"Invalid parameter name {name}")

    return template_factory()


class ParameterRuleTemplate:
    def __getitem__(self, name: ParameterPropertyName) -> dict:
        return get_parameter_template(name)

    def get(self, name: ParameterPropertyName) -> dict:
        return get_parameter_template(name)


PARAMETER_RULE_TEMPLATE = ParameterRuleTemplate()
