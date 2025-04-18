"""
Manage global middlewares
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware

from configs import funiq_ai_config
from infrastructure import get_engine
from middleware.auth import TokenRefreshMiddleware
from middleware.i18n import I18nMiddleware
from middleware.request_context import RequestContextMiddleware


def install_global_middlewares(app: FastAPI):
    app.add_middleware(TokenRefreshMiddleware)
    # must be after TokenRefreshMiddleware, ensure return response is correct(including CORS headers)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=funiq_ai_config.CORS_ALLOW_ORIGINS,
        allow_credentials=funiq_ai_config.CORS_ALLOW_CREDENTIALS,
        allow_methods=funiq_ai_config.CORS_ALLOW_METHODS,
        allow_headers=funiq_ai_config.CORS_ALLOW_HEADERS,
        expose_headers=["X-New-Access-Token"],
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(I18nMiddleware)
    app.add_middleware(SQLAlchemyMiddleware, custom_engine=get_engine())
