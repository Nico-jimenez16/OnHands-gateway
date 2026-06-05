from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from ...services.user_service import UsersService
from ...core.settings import settings
import httpx

router = APIRouter()

# Instancia del servicio de usuarios, inyectando la URL desde la configuración
users_service = UsersService(base_url=settings.USERS_SERVICE_URL)

@router.get("/", summary="Obtener todos los usuarios")
async def get_all_users():
    """
    **Endpoint para obtener una lista de todos los usuarios.**
    """
    try:
        response_data = await users_service.get_all_users()
        return response_data
    except HTTPException as e:
        # Propaga errores HTTP si el servicio de backend los devuelve
        raise e
    except Exception as e:
        # Manejo de errores de conexión o del servicio
        raise HTTPException(status_code=503, detail=f"Error al conectar con el servicio de usuarios: {e}")

@router.get("/{user_id}", summary="Obtener un usuario por su ID")
async def get_user_by_id(user_id: int):
    """
    **Endpoint para obtener un usuario por su ID.**
    """
    try:
        response_data = await users_service.get_user(user_id)
        return response_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al conectar con el servicio de usuarios: {e}")

@router.post("/", summary="Crear un nuevo usuario")
async def create_new_user(user_data: Dict[str, Any]):
    """
    **Endpoint para crear un nuevo usuario.**
    """
    try:
        response_data = await users_service.create_user(user_data)
        return response_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al conectar con el servicio de usuarios: {e}")