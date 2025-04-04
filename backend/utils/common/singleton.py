
from __future__ import annotations

from typing import ClassVar, Generic, TypeVar

T = TypeVar("T")


class Singleton(type, Generic[T]):
    """Metaclass that allows to implement singleton pattern."""

    _instances: ClassVar[dict[Singleton[T], T]] = {}

    def __call__(cls: Singleton[T], *args, **kwargs) -> T:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
