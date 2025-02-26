from pydantic import Field
from pydantic_settings import BaseSettings


class SentryConfig(BaseSettings):
    """
    Sentry-related configuration
    """
    
    SENTRY_DSN: str | None = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )

    SENTRY_TRACES_SAMPLE_RATE: float = Field(
        default=0.1,
        description="Sentry performance monitoring sample rate (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    SENTRY_SEND_DEFAULT_PII: bool = Field(
        default=False,
        description="Whether to send PII data to Sentry"
    )
    
    SENTRY_MAX_BREADCRUMBS: int = Field(
        default=100,
        description="Maximum number of breadcrumbs to record",
        ge=0
    )
    
    SENTRY_LOG_LEVEL: str = Field(
        default="ERROR",
        description="Minimum log level to send to Sentry"
    )