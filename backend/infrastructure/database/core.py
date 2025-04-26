import contextlib
import functools
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from loguru import logger
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from configs import funiq_ai_config
from utils.common.json import json_dumps, json_loads

from .models import DBBase

T = TypeVar("T")
R = TypeVar("R")

# Global engine instance
_engine: AsyncEngine | None = None
_sync_engine: Engine | None = None


def get_engine() -> AsyncEngine:
    """Delay initialization and get the engine"""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            url=funiq_ai_config.ASYNC_DATABASE_URL,
            echo=funiq_ai_config.DATABASE_ECHO,
            pool_size=funiq_ai_config.ASYNC_DATABASE_POOL_SIZE,
            pool_pre_ping=True,
            json_serializer=json_dumps,
            json_deserializer=json_loads,
        )
    return _engine


def get_sync_engine():
    """Delay initialization and get the synchronous engine"""
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = create_engine(
            url=funiq_ai_config.SYNC_DATABASE_URL,
            echo=funiq_ai_config.DATABASE_ECHO,
            pool_size=funiq_ai_config.SYNC_DATABASE_POOL_SIZE,
            pool_pre_ping=True,
            json_serializer=json_dumps,
            json_deserializer=json_loads,
        )
    return _sync_engine


async def init_database():
    """
    Initialize the database: create tables if they don't exist.
    """
    async with get_engine().begin() as conn:
        await conn.run_sync(DBBase.metadata.create_all)


async def update_database_schema():
    """
    Update the database schema without dropping existing tables.
    """
    async with get_engine().begin() as conn:
        await conn.run_sync(DBBase.metadata.create_all, checkfirst=True)


async def shutdown_database():
    """Shutdown the database connection"""
    global _engine, _sync_engine
    try:
        if _engine:
            await _engine.dispose()
        if _sync_engine:
            _sync_engine.dispose()
    except Exception as e:
        logger.exception(f"Error during database shutdown: {e}")
    finally:
        _engine = None
        _sync_engine = None


@contextlib.asynccontextmanager
async def get_session():
    """Context manager for getting a database session"""
    engine = get_engine()
    async_session = async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def create_transient_session():
    """Create a transient session for synchronous operations"""
    transient_engine = create_async_engine(
        funiq_ai_config.ASYNC_DATABASE_URL, 
        pool_pre_ping=True, 
        pool_recycle=3600
    )
    transient_session = async_sessionmaker(
        bind=transient_engine, 
        autoflush=False, 
        autocommit=False, 
        expire_on_commit=False
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