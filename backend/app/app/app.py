
from app.workflows import app

from .routes import app_router

app.router.include_router(app_router) 