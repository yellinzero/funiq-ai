
from abc import ABC, abstractmethod
from collections.abc import Mapping

from .mixins.error_handling import ErrorHandlingMixin
from .mixins.price_handling import PriceHandling
from .mixins.schema_handling import SchemaHandlingMixin
from .mixins.timing_handling import TimingHandling
from .models.model import (
    ModelType,
)


class AIModel(ErrorHandlingMixin, TimingHandling, SchemaHandlingMixin, PriceHandling, ABC):
    """
    Base class for all AI model providers.
    
    This class provides common functionality for model implementations, including:
    - Model schema management and validation
    - Credential validation
    - Error handling and transformation
    - Price calculation
    - Invocation timing
    - Token counting
    """

    model_type: ModelType
    
    @abstractmethod
    def validate_credentials(self, model: str, credentials: Mapping) -> None:
        """
        Validate model credentials.
        Raises InvokeAuthorizationError if credentials are invalid.

        :param model: Model identifier
        :param credentials: Model-specific credentials
        :raises InvokeAuthorizationError: If credentials are invalid
        """
        raise NotImplementedError