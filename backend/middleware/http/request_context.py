from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from configs import funiq_ai_config


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.language = request.headers.get(
            funiq_ai_config.LANGUAGE_HEADER_NAME, funiq_ai_config.DEFAULT_LOCALE
        )
        request.state.tenant_id = request.headers.get(
            funiq_ai_config.TENANT_HEADER_NAME, None
        )

        response = await call_next(request)
        return response
