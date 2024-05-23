from contextvars import ContextVar
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
)

from ..configs.settings import db_url, settings
from ..helpers.sql_db import get_engine

engine = get_engine(db_url, settings)
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


AsyncScopedSession = async_scoped_session(
    session_factory=async_sessionmaker(bind=engine, autoflush=False, autocommit=False),
    scopefunc=get_db_session_context,
)


def get_current_session() -> AsyncSession:
    return AsyncScopedSession()
