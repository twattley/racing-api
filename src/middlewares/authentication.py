from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ALGORITHM = "HS256"
SECRET_KEY = "your-secret-key"


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if "token" not in request.url.path:
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(
                    {"detail": "Authorization token is missing"}, status_code=401
                )
            try:
                payload = jwt.decode(
                    token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM]
                )
                request.state.user = payload.get("sub")
            except Exception:
                return JSONResponse({"detail": "Invalid token"}, status_code=401)
        return await call_next(request)
