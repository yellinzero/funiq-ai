
from app.static import app

from .routes import static_router

app.router.include_router(static_router)
