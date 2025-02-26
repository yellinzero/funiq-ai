

from pydantic import Field
from pydantic_settings import BaseSettings


class CeleryConfig(BaseSettings):
    """
    Configuration for Celery
    """

    CELERY_BROKER_URL: str | None = Field(
        ...,
        description="URL of the message broker for Celery tasks.",
    )
    
    CELERY_RESULT_BACKEND: str = Field(
        ...,
        description="URL of the backend for storing task results. ",
    )