from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
from ...services.auth_service import AuthService
from ...core.settings import settings

router = APIRouter()

# Definición del modelo para las credenciales de usuario
class UserCredentials(BaseModel):
    username: str
    password: str

# Instancia del servicio de autenticación
auth_service = AuthService(base_url=settings.AUTH_SERVICE_URL)

@router.post("/login", summary="Login de usuario y obtención de token JWT")
async def login(credentials: UserCredentials = Body(...)) -> Dict[str, Any]:
    """
    **Endpoint de login.**

    Recibe las credenciales de un usuario y las envía al microservicio de autenticación.
    Si las credenciales son válidas, devuelve un token JWT.
    """
    try:
        # Llama al servicio de autenticación para validar las credenciales
        auth_token = await auth_service.authenticate_user(
            username=credentials.username,
            password=credentials.password
        )
        return auth_token
    except HTTPException as e:
        # Si el servicio de autenticación devuelve un error, lo propagamos
        raise e
    except Exception as e:
        # Manejo genérico de errores de conexión o del servicio
        raise HTTPException(status_code=503, detail=f"Error al conectar con el servicio de autenticación: {e}")