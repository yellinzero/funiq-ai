import contextlib
import logging
import threading
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, Optional, TypeVar

from redis import ConnectionPool as SyncConnectionPool
from redis import Redis as SyncRedis
from redis.asyncio import BlockingConnectionPool, Redis

from configs import funiq_ai_config

R = TypeVar("R")
T = TypeVar("T")

# Thread-local storage
_local = threading.local()

# Global connection pools
_async_pool: Optional[BlockingConnectionPool] = None
_sync_pool: Optional[SyncConnectionPool] = None


def get_redis_connection_pool() -> BlockingConnectionPool:
    """Get the global async connection pool."""
    global _async_pool
    if _async_pool is None:
        _async_pool = BlockingConnectionPool.from_url(
            url=funiq_ai_config.REDIS_URL,
            max_connections=funiq_ai_config.REDIS_MAX_CONNECTIONS,
        )
    return _async_pool


def get_sync_redis_connection_pool() -> SyncConnectionPool:
    """Get the global sync connection pool."""
    global _sync_pool
    if _sync_pool is None:
        _sync_pool = SyncConnectionPool.from_url(
            url=funiq_ai_config.REDIS_URL,
            max_connections=funiq_ai_config.REDIS_MAX_CONNECTIONS,
        )
    return _sync_pool


def get_redis_client() -> Redis:
    """Get a Redis client from the global connection pool."""
    return Redis(connection_pool=get_redis_connection_pool())


def get_sync_redis_client() -> SyncRedis:
    """Get a synchronous Redis client from the global connection pool."""
    return SyncRedis(connection_pool=get_sync_redis_connection_pool())


@contextlib.asynccontextmanager
async def redis_context():
    """Context manager for Redis operations that ensures proper cleanup."""
    client = get_redis_client()
    try:
        yield client
    finally:
        await client.close()


def with_redis(func: Callable[..., Awaitable[R]]) -> Callable[..., Awaitable[R]]:
    """Decorator that provides a Redis client and ensures proper cleanup."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if "redis" in kwargs and kwargs["redis"] is not None:
            return await func(*args, **kwargs)

        async with redis_context() as redis:
            kwargs["redis"] = redis
            return await func(*args, **kwargs)

    return wrapper


async def execute_redis_operation(operation_func, *args, **kwargs):
    """Execute a Redis operation with proper connection handling."""
    async with redis_context() as redis:
        return await operation_func(redis, *args, **kwargs)


async def shutdown_redis():
    """Properly close all Redis connections and pools during application shutdown."""
    global _async_pool, _sync_pool
    try:
        # Close async pool if exists
        if _async_pool is not None:
            await _async_pool.disconnect()
            _async_pool = None

        # Close sync pool if exists
        if _sync_pool is not None:
            _sync_pool.disconnect()
            _sync_pool = None

    except Exception as e:
        logging.error(f"Error during Redis shutdown: {e}")
        raise


@contextlib.contextmanager
def sync_redis_context():
    """Context manager for synchronous Redis operations that ensures proper cleanup."""
    client = get_sync_redis_client()
    try:
        yield client
    finally:
        client.close()


def with_sync_redis(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that provides a synchronous Redis client and ensures proper cleanup."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        if "sync_redis" in kwargs and kwargs["sync_redis"] is not None:
            return func(*args, **kwargs)

        with sync_redis_context() as redis:
            kwargs["sync_redis"] = redis
            return func(*args, **kwargs)

    return wrapper


def execute_sync_redis_operation(operation_func: Callable, *args: Any, **kwargs: Any) -> Any:
    """Execute a synchronous Redis operation with proper connection handling."""
    with sync_redis_context() as redis:
        return operation_func(redis, *args, **kwargs)
    

class RedisRateLimiter:
    """
    A Redis-based rate limiter for tracking request limits by key (e.g., email or IP).
    """

    def __init__(self, prefix: str = "redis_rate_limiter", max_attempts: int = 5, time_window: int = 60):
        """
        Initialize the rate limiter.

        Args:
            prefix: Redis key prefix
            max_attempts: Max allowed attempts in the time window
            time_window: Time window in seconds
        """
        self.prefix = prefix
        self.max_attempts = max_attempts
        self.time_window = time_window
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_key(self, identifier: str) -> str:
        """
        Generate a unique Redis key for a given identifier (e.g., email or IP).

        Args:
            identifier: Unique identifier for the user or IP
        Returns:
            Redis key
        """
        return f"{self.prefix}:{identifier}"

    @with_redis
    async def check_limit_exceeded(self, identifier: str, redis: Redis = None) -> bool:
        """
        Check if the rate limit is exceeded for the given identifier.

        Args:
            identifier: Unique identifier for the user or IP
            redis: Redis client (injected by decorator)
        Returns:
            True if the limit is exceeded, False otherwise
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

    @with_redis
    async def record_attempt(self, identifier: str, redis: Redis = None):
        """
        Record an attempt for the given identifier.

        Args:
            identifier: Unique identifier for the user or IP
            redis: Redis client (injected by decorator)
        """
        key = self.generate_key(identifier)
        current_time = int(time.time())

        # Add the current timestamp to the sorted set
        await redis.zadd(key, {current_time: current_time})

        # Set expiration time for the key to automatically clear old data
        await redis.expire(key, self.time_window * 2)

    @with_redis
    async def reset_attempts(self, identifier: str, redis: Redis = None):
        """
        Reset the attempts for the given identifier.

        Args:
            identifier: Unique identifier for the user or IP
            redis: Redis client (injected by decorator)
        """
        key = self.generate_key(identifier)
        await redis.delete(key)
        self.logger.info(f"Rate limit reset for identifier: {identifier}")