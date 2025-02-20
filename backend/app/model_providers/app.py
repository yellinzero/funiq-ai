
from app.model_providers import app

from .routes import model_providers_router

app.router.include_router(model_providers_router) 