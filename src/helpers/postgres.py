import json
import logging
from contextvars import ContextVar
from typing import Callable, Awaitable, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
    async_sessionmaker,
)
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

import pydantic.json
from src.configs.settings import create_db_url, get_settings

# Setting up the logger
logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s [%(filename)s:%(lineno)s] - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger(__name__)

# Fetching settings and creating the database engine
settings = get_settings()
engine = create_async_engine(
    create_db_url(settings),
    json_serializer=lambda *args, **kwargs: json.dumps(
        *args, default=pydantic.json.pydantic_encoder, **kwargs
    ),
    pool_size=settings.postgresql_pool_size,
    max_overflow=0,
    connect_args={
        "command_timeout": settings.postgresql_query_timeout,
        "timeout": settings.postgresql_conn_timeout,
    },
)

# Context variable for session management
db_session_context: ContextVar[Optional[int]] = ContextVar(
    "db_session_context", default=None
)


def get_db_session_context() -> int:
    session_id = db_session_context.get()
    if session_id is None:
        raise ValueError("Currently no session is available")
    return session_id


def set_db_session_context(session_id: int) -> None:
    db_session_context.set(session_id)


# Scoped session for handling database transactions
AsyncScopedSession = async_scoped_session(
    session_factory=async_sessionmaker(bind=engine, autoflush=False, autocommit=False),
    scopefunc=get_db_session_context,
)


def get_current_session() -> AsyncSession:
    return AsyncScopedSession()


# Transactional decorator for handling database operations
def transactional(func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
    async def wrapper(*args, **kwargs) -> Awaitable:
        try:
            db_session = get_current_session()
            if db_session.in_transaction():
                return await func(*args, **kwargs)
            async with db_session.begin():
                return await func(*args, **kwargs)
        except Exception as error:
            logger.info(f"request hash: {get_db_session_context()}")
            logger.exception(error)
            raise

    return wrapper


# Health check function to test database connectivity
async def health_check(async_session: AsyncSession) -> bool:
    try:
        await async_session.execute(text("SELECT 1"))
        return True
    except (SQLAlchemyError, OSError):
        return False
