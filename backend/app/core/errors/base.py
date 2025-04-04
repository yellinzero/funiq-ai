from enum import Enum
from typing import ClassVar, Dict, List, Tuple


class ErrorRegistry:
    """
    Global error code registry for managing and validating error codes.
    """

    _error_codes: ClassVar[Dict[str, str]] = {}

    @classmethod
    def register(cls, code: str, message: str):
        """
        Register an error code.
        :param code: The error code (e.g., 'A0001').
        :param message: The error message.
        :raises ValueError: If the error code is duplicated or invalid.
        """
        cls.validate_code(code)
        if code in cls._error_codes:
            raise ValueError(f"Error code '{code}' is already registered: {cls._error_codes[code]}")
        cls._error_codes[code] = message

    @classmethod
    def get_all_error_codes(cls) -> List[Tuple[str, str]]:
        """Retrieve all registered error codes as a sorted list."""
        return sorted(cls._error_codes.items())

    @classmethod
    def validate_code(cls, code: str):
        """Validate the format of an error code (5 characters: 1 prefix and 4 digits)."""
        if len(code) != 5 or not code[1:].isdigit():
            raise ValueError(f"Invalid error code format: '{code}'")


class BaseErrorCode(Enum):
    """
    Base class for error codes.
    Automatically determines the category based on the first registered error code.
    """
    def __new__(cls, code: str, message: str):
        # Validate and register the error code
        ErrorRegistry.register(code, message)

        # Create Enum value
        obj = object.__new__(cls)
        obj._value_ = (code, message)
        return obj

    @property
    def code(self):
        """Return the error code."""
        return self.value[0]

    @property
    def message(self):
        """Return the error message."""
        return self.value[1]

    def to_dict(self):
        """Convert the error code to a dictionary."""
        return {"code": self.code, "message": self.message}
    
    def exception(self, data: dict | str | None = None, status_code: int = 500):
        return FuniqAIError(code=self.code, message=self.message, data=data, status_code=status_code)
    

class FuniqAIError(Exception):
    """
    Base exception for the application.
    Allows for standardized error handling with error codes and optional data.
    """
    _default_code: str = "A0000"  # Fallback code if no specific error is provided
    _default_message: str = "An unknown error occurred."  # Default message
    _default_status_code: int = 500  # Default HTTP status code

    def __init__(
        self, 
        code: str | None = None,
        message: str | None = None, 
        data: dict | str | None = None, 
        status_code: int | None = None
    ):
        """
        Initialize the exception with optional parameters.
        :param code: Error code identifier.
        :param message: Error message.
        :param data: Additional data to include in the error response.
        :param status_code: HTTP status code for the error.
        """
        self.code = code or self._default_code
        self.message = message or self._default_message
        self.data = data
        self.status_code = status_code or self._default_status_code

    def to_dict(self) -> dict:
        """
        Convert the exception to a dictionary representation.
        :return: A dictionary with the error code, message, and optional data.
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data,
        }
        