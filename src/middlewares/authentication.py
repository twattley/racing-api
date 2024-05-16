import re
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your-secret-key"


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if re.search(r"/token$", request.url.path):
            return await call_next(request)
        response = Response("Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
        token = request.headers.get("Authorization")
        if not token:
            return response
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("sub")
            if not user_id:
                return response
            request.state.user = user_id
        except JWTError:
            return response

        return await call_next(request)
