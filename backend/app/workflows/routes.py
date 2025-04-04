
from fastapi import APIRouter, Request

from app.core.schemas import ResponseModel

from .schemas import GetOperatorsResponse
from .service.operator_service import OperatorService

workflows_router = APIRouter(prefix="/workflows", tags=["workflows"])


@workflows_router.get(
    "/operators", response_model=ResponseModel[GetOperatorsResponse], response_model_exclude_none=True
)
async def get_operators(request: Request):
    """
    Get all available operators
    """
    operators = OperatorService.get_all_operators()
    return ResponseModel(data={"operators": operators, "total": len(operators)})
