import logging
from typing import Any, Dict

import sentry_sdk
from fastapi.exceptions import HTTPException
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from configs import funiq_ai_config


def before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Custom handler for processing events before sending to Sentry
    
    Args:
        event: The event to be sent
        hint: Contains additional information about the event, including exception info
        
    Returns:
        Modified event or None if event should be discarded
    """
    return event


def setup_sentry() -> None:
    """
    Configure Sentry SDK with FastAPI integration and logging
    """
    if not funiq_ai_config.SENTRY_DSN:
        return

    # Configure Sentry logging integration
    sentry_logging = LoggingIntegration(
        level=getattr(logging, funiq_ai_config.SENTRY_LOG_LEVEL),
        event_level=getattr(logging, funiq_ai_config.SENTRY_LOG_LEVEL),
    )

    # Initialize Sentry SDK
    sentry_sdk.init(
        dsn=funiq_ai_config.SENTRY_DSN,
        environment=funiq_ai_config.DEPLOY_ENVIRONMENT,
        traces_sample_rate=funiq_ai_config.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=funiq_ai_config.SENTRY_SEND_DEFAULT_PII,
        max_breadcrumbs=funiq_ai_config.SENTRY_MAX_BREADCRUMBS,
        before_send=before_send,
        integrations=[
            FastApiIntegration(transaction_style="url"),
            sentry_logging,
        ],
        ignore_errors=[
            HTTPException,
            ValueError, 
        ],
    )

    logging.info("Sentry monitoring system initialized")
