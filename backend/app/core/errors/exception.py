from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.core.errors.base import FuniqAIError
from app.core.errors.common import CommonErrorCode


# Exception handler registration
def register_exception_handlers(app: FastAPI):
    """
    Register exception handlers for standardized error responses.
    :param app: FastAPI application instance.
    """
    @app.exception_handler(FuniqAIError)
    def recurve_exception_handler(request: Request, exc: FuniqAIError):
        """
        Handle FuniqAIError and return a standardized JSON response.
        :param request: Incoming request.
        :param exc: Raised FuniqAIError.
        :return: JSONResponse with error details.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    @app.exception_handler(RequestValidationError)
    def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle FastAPI's RequestValidationError and return a standardized JSON response.
        :param request: Incoming request.
        :param exc: Raised RequestValidationError.
        :return: JSONResponse with validation errors.
        """
        return JSONResponse(
            status_code=400,
            content=CommonErrorCode.INVALID_ARGUMENT.to_dict() | {
                "code": "INVALID_ARGUMENT",
                "message": "Invalid input data",
                "data": jsonable_encoder(exc.errors()),
            },
        )