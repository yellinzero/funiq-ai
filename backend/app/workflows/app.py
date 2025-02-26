
from app.workflows import app

from .routes import workflows_router

app.router.include_router(workflows_router) 