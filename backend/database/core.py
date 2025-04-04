import contextlib
import functools
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from redis import Redis as SyncRedis
from redis.asyncio import BlockingConnectionPool, Redis
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from configs import funiq_ai_config
from utils.common.json import json_dumps, json_loads

from .models import DBBase

T = TypeVar("T")
R = TypeVar("R")

# Database engine and session factory
sync_engine = create_engine(
    url=funiq_ai_config.SYNC_DATABASE_URL,
    echo=funiq_ai_config.DATABASE_ECHO,
    pool_size=funiq_ai_config.SYNC_DATABASE_POOL_SIZE,
    pool_pre_ping=True,
    json_serializer=json_dumps,
    json_deserializer=json_loads,
)

engine: AsyncEngine = create_async_engine(
    url=funiq_ai_config.ASYNC_DATABASE_URL,
    echo=funiq_ai_config.DATABASE_ECHO,
    pool_size=funiq_ai_config.ASYNC_DATABASE_POOL_SIZE,
    pool_pre_ping=True,
    json_serializer=json_dumps,
    json_deserializer=json_loads,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Redis clients
redis: Redis = Redis(
    connection_pool=BlockingConnectionPool.from_url(
        url=funiq_ai_config.REDIS_URL,
        max_connections=funiq_ai_config.REDIS_MAX_CONNECTIONS,
    )
)

sync_redis: SyncRedis = SyncRedis.from_url(
    url=funiq_ai_config.REDIS_URL,
    max_connections=funiq_ai_config.REDIS_MAX_CONNECTIONS,
)


async def init_database():
    """
    Initialize the database: create tables if they don't exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(DBBase.metadata.create_all)


async def update_database_schema():
    """
    Update the database schema without dropping existing tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(DBBase.metadata.create_all, checkfirst=True)


async def shutdown_database():
    """
    Properly close the database and Redis connections during application shutdown.
    """
    try:
        await redis.close()
        sync_redis.close()
        await engine.dispose()
    except Exception as e:
        print(f"Error during shutdown: {e}")


@contextlib.asynccontextmanager
async def get_session():
    """Context manager for getting a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def create_transient_session():
    """
    Creates a transient async session factory for use in synchronous environments.

    This function creates a separate engine and session maker that can be used
    for one-off database operations, typically run with asyncio.run().

    Example usage:
        async def do_something():
            async with create_transient_session() as session:
                result = await session.execute(select(...))
                return result.scalars().one()

        result = asyncio.run(do_something())

    Returns:
        An async context manager that yields a session and handles cleanup
    """
    transient_engine = create_async_engine(funiq_ai_config.ASYNC_DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
    transient_session = async_sessionmaker(
        bind=transient_engine, autoflush=False, autocommit=False, expire_on_commit=False
    )

    @contextlib.asynccontextmanager
    async def _session_context():
        session = transient_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            await transient_engine.dispose()

    return _session_context()


def with_session(func: Callable[..., Awaitable[R]]) -> Callable[..., Awaitable[R]]:
    """
    Decorator that provides an async session if one is not passed.

    If 'session' is not provided in the function arguments, this decorator
    will create a new session and pass it to the function. The session will be
    committed and closed automatically when the function completes.

    Args:
        func: The async function to decorate

    Returns:
        Decorated function that handles session management
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> R:
        if "session" in kwargs and kwargs["session"] is not None:
            # Session already provided, just call the function
            return await func(*args, **kwargs)

        # No session provided, create one
        async with create_transient_session() as session:
            kwargs["session"] = session
            return await func(*args, **kwargs)

    return wrapper


class RedisRateLimiter:
    """
    A Redis-based rate limiter for tracking request limits by key (e.g., email or IP).
    """

    def __init__(self, prefix: str = "redis_rate_limiter", max_attempts: int = 5, time_window: int = 60):
        """
        Initialize the rate limiter.

        :param redis_client: Redis client instance.
        :param prefix: Redis key prefix.
        :param max_attempts: Max allowed attempts in the time window.
        :param time_window: Time window in seconds.
        """
        self.prefix = prefix
        self.max_attempts = max_attempts
        self.time_window = time_window
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_key(self, identifier: str) -> str:
        """
        Generate a unique Redis key for a given identifier (e.g., email or IP).

        :param identifier: Unique identifier for the user or IP.
        :return: Redis key.
        """
        return f"{self.prefix}:{identifier}"

    async def check_limit_exceeded(self, identifier: str) -> bool:
        """
        Check if the rate limit is exceeded for the given identifier.

        :param identifier: Unique identifier for the user or IP.
        :return: True if the limit is exceeded, False otherwise.
        """
        key = self.generate_key(identifier)
        current_time = int(time.time())
        window_start_time = current_time - self.time_window

        # Remove expired attempts
        await redis.zremrangebyscore(key, "-inf", window_start_time)

        # Check current attempts count
        attempts = await redis.zcard(key)
        if attempts and int(attempts) >= self.max_attempts:
            self.logger.warning(f"Rate limit exceeded for identifier: {identifier}")
            return True
        return False

    async def record_attempt(self, identifier: str):
        """
        Record an attempt for the given identifier.

        :param identifier: Unique identifier for the user or IP.
        """
        key = self.generate_key(identifier)
        current_time = int(time.time())

        # Add the current timestamp to the sorted set
        await redis.zadd(key, {current_time: current_time})

        # Set expiration time for the key to automatically clear old data
        await redis.expire(key, self.time_window * 2)

    async def reset_attempts(self, identifier: str):
        """
        Reset the attempts for the given identifier.

        :param identifier: Unique identifier for the user or IP.
        """
        key = self.generate_key(identifier)
        await redis.delete(key)
        self.logger.info(f"Rate limit reset for identifier: {identifier}")
