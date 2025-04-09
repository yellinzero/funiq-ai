from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: str = "0"
    msg: str = "success"
    data: T
