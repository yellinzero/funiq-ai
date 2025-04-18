from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.core.errors import register_exception_handlers
from app_manager import app_manager
from configs import funiq_ai_config
from infrastructure import (
    init_celery,
    init_email_service,
    setup_loguru,
    setup_sentry,
    shutdown_database,
    shutdown_redis,
)
from middleware import install_global_middlewares
from utils.common.i18n import register_all_translation_domains


# Define the FastAPI application with essential configurations
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    
    # Initialize logging and Sentry
    setup_loguru()
    
    app = FastAPI(
        title="FuniqAI",  # Title for the API documentation
        default_response_class=ORJSONResponse,  # Use ORJSON for faster JSON serialization
        lifespan=lifespan,  # Register lifecycle hooks
    )
    
    # Register i18n
    register_all_translation_domains()
    setup_sentry()

    # Register exception handlers
    register_exception_handlers(app)
    
    # Install middleware
    install_global_middlewares(app)

    # Use INSTALLED_APPS from config
    app_manager.install_apps(funiq_ai_config.INSTALLED_APPS)
    app_manager.apply_modules_to_fastapi(app)

    # Register routes
    register_routes(app)

    # Initialize services
    init_email_service(app)  # Email service
    init_celery(app)        # Celery task queue

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await shutdown_database()
    await shutdown_redis()


# Define a health check route
def register_routes(app: FastAPI):
    """
    Register API routes.
    """

    @app.get("/health", tags=["Health Check"])
    def health_check():
        return {"status": "healthy"}


app = create_app()
celery = app.state.celery
