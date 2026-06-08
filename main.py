from fastapi import FastAPI
from core.settings import settings

#! Middlewares - Imports
from middleware.authentication import AuthMiddleware
from middleware.cors import setup_cors_middleware
from middleware.logging import LoggingMiddleware

#! Rutas - Imports
from api.endpoints import auth_routes, user_routes, service_request_routes, chat_routes, match_routes

app = FastAPI(
    title=settings.app_name, 
    description= settings.app_description, 
    version=settings.app_version
    )

#! Middlewares de seguridad de la aplicación
# Agregar middleware CORS
setup_cors_middleware(app)

# Agregar middleware de autenticación
app.add_middleware(AuthMiddleware)

# Agregar middleware de logging
app.add_middleware(LoggingMiddleware)

#!   Incluir rutas
#app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
#app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(service_request_routes.router, prefix="/requests", tags=["Service Requests"])
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])
app.include_router(match_routes.router, prefix="/match", tags=["Matching"])

@app.get("/")
def health_check():
    return {"status": "ok", "service": settings.app_name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=settings.app_port, reload=True)
