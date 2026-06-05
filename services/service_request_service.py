import httpx
from typing import Dict, Any
from fastapi import HTTPException

class ServiceRequest:
    """
    Clase para interactuar con el microservicio de solicitudes de servicio.
    """
    def __init__(self, base_url: str):
        """
        Inicializa el servicio con la URL base del microservicio de solicitudes.
        """
        self.base_url = base_url

    async def get_all_requests(self, headers: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Obtiene todas las solicitudes de servicio desde el microservicio de backend.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/v1/requests/",
                    headers=headers or {}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
            except httpx.RequestError as e:
                raise Exception(f"Error de red al intentar conectar con el requestTransitionService: {e}")

    async def get_request(self, request_id: int) -> Dict[str, Any]:
        """
        Obtiene una solicitud de servicio por su ID desde el microservicio de backend.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/v1/requests/{request_id}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
            except httpx.RequestError as e:
                raise Exception(f"Error de red al intentar conectar con el requestTransitionService: {e}")

    async def create_request(self, request_data: Dict[str, Any], headers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una nueva solicitud de servicio en el microservicio de backend.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/requests/",
                    json=request_data,
                    headers=headers   # 🔑 ahora pasa los headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
            except httpx.RequestError as e:
                raise Exception(f"Error de red al intentar conectar con el requestTransitionService: {e}")