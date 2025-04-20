
from app.conversation import app

from .routes import conversation_router

app.router.include_router(conversation_router) 