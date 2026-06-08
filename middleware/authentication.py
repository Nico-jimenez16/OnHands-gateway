from fastapi import Request, HTTPException
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from jwt import PyJWTError
from core.settings import settings

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Rutas públicas que no requieren token
        public_paths = ["/auth" , "/"]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Obtener token del header
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Token missing")

        try:
            token = token.replace("Bearer ", "")
            jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        return await call_next(request)

# Lista de middleware para FastAPI
middleware = [Middleware(AuthMiddleware)]
