from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """
    Database-related configuration
    """

    PGHOST: str = Field(..., description="PostgreSQL host")
    PGUSER: str = Field(..., description="PostgreSQL user")
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQL password")
    POSTGRES_DB: str = Field(..., description="PostgreSQL database name")
    SYNC_DATABASE_URL: str = Field(..., description="Synchronous database URL")
    DATABASE_ECHO: bool = Field(False, description="Enable SQLAlchemy echo mode")
    SYNC_DATABASE_POOL_SIZE: int = Field(5, description="Database connection pool size")
    ASYNC_DATABASE_URL: str = Field(..., description="Asynchronous database URL")
    ASYNC_DATABASE_POOL_SIZE: int = Field(5, description="Async database connection pool size")
    DB_ENCRYPTION_KEY: str = Field(..., description="Database encryption key")


class RedisConfig(BaseSettings):
    """
    Redis-related configuration
    """

    REDIS_URL: str = Field(..., description="Redis server URL")
    REDIS_MAX_CONNECTIONS: int = Field(5, description="Maximum Redis connections")