from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError
from loguru import logger
from redis import RedisError
from starlette.middleware.base import BaseHTTPMiddleware

from app.errors.base import FuniqAIError
from app_manager import app_manager
from utils.security import (
    decode_access_token,
    get_refresh_token_from_cookie,
    refresh_access_token,
    verify_refresh_token,
)


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Get all public app paths from app_manager
        self.public_paths = [f"/{app.name}/" for app in app_manager.apps.values() if app.public]
        # Add other essential public paths
        self.public_paths.extend(["/health", "/openapi.json", "/docs", "/redoc"])

    async def dispatch(self, request: Request, call_next):
        try:
            # Skip authentication for OPTIONS requests and public paths
            if request.method == "OPTIONS" or any(
                request.url.path.startswith(prefix) for prefix in self.public_paths
            ):
                return await call_next(request)

            auth_header = request.headers.get("Authorization")
            refresh_token = get_refresh_token_from_cookie(request)

            # If no tokens present, let the route handler's JWTBearer dependency handle it
            if not auth_header or not refresh_token:
                return await call_next(request)

            access_token = auth_header.replace("Bearer ", "")

            try:
                # Try to decode the access token
                decode_access_token(access_token)
                # If successful, continue with the request
                return await call_next(request)
            except (JWTError, ValueError):
                # Only handle token refresh if the refresh token is valid
                try:
                    verify_refresh_token(refresh_token)
                    new_access_token = refresh_access_token(refresh_token)
                    
                    # Update request headers with new access token
                    headers = request.scope["headers"]
                    headers_dict = dict(headers)
                    headers_dict[b"authorization"] = f"Bearer {new_access_token}".encode()
                    request.scope["headers"] = list(headers_dict.items())

                    # Process request with new token
                    response = await call_next(request)
                    response.headers["X-New-Access-Token"] = new_access_token
                    return response
                except (FuniqAIError, RedisError) as e:
                    # Let JWTBearer handle the authentication failure
                    return await call_next(request)

        except Exception as e:
            logger.error(f"Unexpected error in token refresh: {e!s}")
            return await call_next(request)

    def handle_error(self, exc: FuniqAIError):
        logger.error(f"Handling authentication error: {exc!s}")
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )
