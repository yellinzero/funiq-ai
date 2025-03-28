from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .apps import AppsConfig
from .celery import CeleryConfig
from .cors import CorsConfig
from .database import DatabaseConfig, RedisConfig
from .language import LanguageConfig
from .log_config import LogConfig
from .mail import MailConfig
from .package import PackageInfo
from .sentry_config import SentryConfig
from .token import TokenConfig


class FuniqAIConfigSettings(
    PackageInfo,
    MailConfig,
    DatabaseConfig,
    RedisConfig,
    TokenConfig,
    CeleryConfig,
    AppsConfig,
    CorsConfig,
    LogConfig,
    SentryConfig,
    LanguageConfig,
):
    DEBUG: bool
    SECRET_KEY: str
    CSRF_SECRET_KEY: str
    REFRESH_TOKEN_COOKIE_NAME: str
    SERVER_URL: str
    DEPLOY_ENVIRONMENT: str = Field(
        default="development",
        description="Environment name for Sentry (development, staging, production)"
    )
    TENANT_HEADER_NAME: str = Field(
        default="X-Tenant-ID",
        description="Tenant header name",
    )
    
    model_config = SettingsConfigDict(
        # read from dotenv format config file
        env_file=".env",
        env_file_encoding="utf-8",
        frozen=True,
        # ignore extra attributes
        extra="ignore",
    )
