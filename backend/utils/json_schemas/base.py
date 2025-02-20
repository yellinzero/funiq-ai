from typing import Any, Dict, Union

from pydantic import BaseModel, Field

from utils.i18n import TranslatableText


class JSONSchemaPropertyBase(BaseModel):
    """Base JSON Schema type definition"""
    type: str
    title: Union[str, TranslatableText] | None = None
    description: Union[str, TranslatableText] | None = None
    default: Any | None = None
    enum: list[Any] | None = None
    const: Any | None = None


class StringProperty(JSONSchemaPropertyBase):
    """String type schema"""
    type: str = "string"
    min_length: int | None = Field(None, alias="minLength")
    max_length: int | None = Field(None, alias="maxLength")
    pattern: str | None = None
    format: str | None = None


class NumberProperty(JSONSchemaPropertyBase):
    """Number type schema"""
    type: str = "number"
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None
    multiple_of: float | None = None


class JSONSchema(BaseModel):
    """Generic JSON Schema definition"""
    type: str = "object"
    properties: dict[str, Union[StringProperty, NumberProperty, Dict[str, Any]]]
    required: list[str] | None = None

    class Config:
        arbitrary_types_allowed = True
        
        
        
