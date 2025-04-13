from abc import ABC, abstractmethod
from typing import Type

from ..errors import InvokeAuthorizationError, InvokeError


class ErrorHandlingMixin(ABC):
    """Mixin class for handling provider-specific errors and converting them to unified errors."""
    
    @property
    @abstractmethod
    def _invoke_error_mapping(self) -> dict[Type[InvokeError], list[Type[Exception]]]:
        """Define mapping between provider-specific errors and unified error types."""
        raise NotImplementedError

    def transform_provider_error(self, error: Exception) -> InvokeError:
        """Transform provider-specific error to unified error format."""
        provider_name = self.__class__.__module__.split(".")[-3]

        for invoke_error, provider_errors in self._invoke_error_mapping.items():
            if isinstance(error, tuple(provider_errors)):
                if invoke_error == InvokeAuthorizationError:
                    return invoke_error(
                        description=f"[{provider_name}] Invalid credentials provided"
                    )
                return invoke_error(description=f"[{provider_name}] Error: {error!s}")

        return InvokeError(description=f"[{provider_name}] Error: {error!s}") 