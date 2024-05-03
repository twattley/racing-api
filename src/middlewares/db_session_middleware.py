from typing import Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from src.helpers.postgres import AsyncScopedSession, set_db_session_context


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        response = Response(
            "Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        try:
            set_db_session_context(session_id=hash(request))
            response = await call_next(request)

        finally:
            await AsyncScopedSession.remove()  # this includes closing the session as well
            set_db_session_context(session_id=None)

        return response
