from collections.abc import Sequence
from typing import Literal, Union

from pydantic import BaseModel

from utils.i18n import TranslatableText
from utils.json_schemas.base import JSONSchema

from .model import ConfigurateMethod, ModelType


class ProviderDocs(BaseModel):
    """
    Model class for provider docs.
    """

    title: Union[str, TranslatableText]
    url: str
    

class SimpleProviderEntity(BaseModel):
    """
    Simple model class for provider.
    """

    provider: str
    label: Union[str, TranslatableText]
    icon: dict[Literal["small", "large"], str | None] | None
    supported_model_types: Sequence[ModelType]
    docs: ProviderDocs | None


class ProviderEntity(SimpleProviderEntity):
    """
    Model class for provider.
    """
    description: Union[str, TranslatableText] | None = None
    configurate_methods: list[ConfigurateMethod]
    credential_schema: JSONSchema | None
