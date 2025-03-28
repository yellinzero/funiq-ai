from celery import Celery
from fastapi import FastAPI
from loguru import logger

from configs import funiq_ai_config


def create_celery_app(app: FastAPI) -> Celery:
    """
    Initialize and configure Celery with FastAPI.

    :param app: FastAPI application instance.
    :return: Configured Celery app instance.
    """

    celery_app = Celery(
        app.title,
        broker=funiq_ai_config.CELERY_BROKER_URL,
        backend=funiq_ai_config.CELERY_RESULT_BACKEND,
        broker_connection_retry_on_startup=True,
    )

    # Configure Celery
    celery_app.conf.task_serializer = "json"
    celery_app.conf.result_serializer = "json"
    celery_app.conf.accept_content = ["json"]
    celery_app.conf.result_expires = 60 * 60 * 24  # 1 day
    celery_app.conf.timezone = "UTC"

    # Set up task priority
    celery_app.conf.broker_transport_options = {
        "priority_steps": list(range(10)),
        "sep": ":",
        "queue_order_strategy": "priority",
    }
    celery_app.conf.task_queue_max_priority = 10
    celery_app.conf.task_default_priority = 5

    # Enable task cancellation
    celery_app.conf.task_track_started = True

    celery_app.conf.broker_connection_retry_on_startup = True

    logger.info("Celery app configured")

    return celery_app


# Initialize Celery with FastAPI
def init_celery(app: FastAPI):
    """
    Attach Celery instance to FastAPI app.

    :param app: FastAPI instance.
    """
    celery_app = create_celery_app(app)
    app.state.celery = celery_app
