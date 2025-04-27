from collections.abc import Sequence
from typing import Literal, Union

from pydantic import BaseModel

from utils.common.i18n import TranslatableText

from .model import ModelType


class ProviderDoc(BaseModel):
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
    model_types: Sequence[ModelType]
    docs: list[ProviderDoc] | None


class ProviderConfigSchema(BaseModel):
    json_schema: dict | None
    ui_schema: dict | None


class ProviderEntity(SimpleProviderEntity):
    """
    Model class for provider.
    """
    description: Union[str, TranslatableText] | None = None
    config_schema: ProviderConfigSchema | None
