from decimal import Decimal
from enum import Enum

from pydantic import BaseModel

from providers.models.core.schemas import ModelUsage


class EmbeddingInputType(Enum):
    """
    Enum for embedding input type.
    """

    DOCUMENT = "document"
    QUERY = "query"


class EmbeddingUsage(ModelUsage):
    """
    Model class for embedding usage.
    """

    tokens: int
    total_tokens: int
    unit_price: Decimal
    price_unit: Decimal
    total_price: Decimal
    currency: str
    latency: float


class TextEmbeddingResult(BaseModel):
    """
    Model class for text embedding result.
    """

    model: str
    embeddings: list[list[float]]
    usage: EmbeddingUsage
