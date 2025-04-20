
from app.workflow import app

from .routes import workflow_router

app.router.include_router(workflow_router) 