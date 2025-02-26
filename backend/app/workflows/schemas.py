from typing import List

from pydantic import BaseModel

from providers.operators.core.models.operator import OperatorEntity


class GetOperatorsResponse(BaseModel):
    operators: List[OperatorEntity]
    total: int

