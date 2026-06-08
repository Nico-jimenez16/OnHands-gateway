from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Optional
from services.service_request_service import ServiceRequest
from core.settings import settings
import httpx

router = APIRouter()

# Instancia del servicio de solicitud de servicio.
service_request = ServiceRequest(base_url=settings.REQUEST_SERVICE_URL)

@router.get("/", summary="Obtener todas las solicitudes de servicio")
async def get_all_service_requests(request: Request):
    """
    Endpoint para obtener todas las solicitudes de servicio.
    """
    try:
        headers = {
            "x-user-id": request.headers.get("x-user-id"),
            "x-user-role": request.headers.get("x-user-role"),
        }
        response_data = await service_request.get_all_requests(headers)
        return response_data
    except HTTPException as e:
        # Si el servicio de backend devuelve un error, lo propagamos.
        raise e
    except Exception as e:
        # Manejo genérico de errores de conexión o del servicio.
        raise HTTPException(status_code=503, detail=f"Error al conectar con el servicio de solicitudes: {e}")

@router.get("/{request_id}", summary="Obtener una solicitud de servicio por su ID")
async def get_service_request_by_id(request_id: int):
    """
    Endpoint para obtener una solicitud de servicio por su ID.
    """
    try:
        response_data = await service_request.get_request(request_id)
        return response_data
    except HTTPException as e:
        # Si el servicio de backend devuelve un error, lo propagamos.
        raise e
    except Exception as e:
        # Manejo genérico de errores de conexión o del servicio.
        raise HTTPException(status_code=503, detail=f"Error al conectar con el servicio de solicitudes: {e}")

@router.post("/", summary="Crear una nueva solicitud de servicio")
async def create_new_service_request(request: Request, request_data: Dict[str, Any]):
    """
    Endpoint para crear una nueva solicitud de servicio.
    """
    try:
        # Extraer headers del request original
        headers = {
            "x-user-id": request.headers.get("x-user-id"),
            "x-user-role": request.headers.get("x-user-role"),
        }

        response_data = await service_request.create_request(request_data, headers)
        return response_data

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al conectar con el servicio de solicitudes: {e}")