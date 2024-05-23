from typing import Awaitable, Callable

from ..helpers.logging_config import logger

from .session_manager import get_current_session, get_db_session_context


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
