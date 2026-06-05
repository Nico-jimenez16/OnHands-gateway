import httpx
from typing import Dict, Any, List
from fastapi import HTTPException

class UsersService:
    """
    Clase para interactuar con el microservicio de usuarios.
    """
    def __init__(self, base_url: str):
        """
        Inicializa el servicio con la URL base del microservicio de usuarios.
        """
        self.base_url = base_url

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los usuarios desde el microservicio de backend.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/users/")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
            except httpx.RequestError as e:
                raise Exception(f"Error de red al intentar conectar con el servicio de usuarios: {e}")

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene un usuario por su ID desde el microservicio de backend.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/users/{user_id}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
            except httpx.RequestError as e:
                raise Exception(f"Error de red al intentar conectar con el servicio de usuarios: {e}")

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo usuario en el microservicio de backend.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/users/", json=user_data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
            except httpx.RequestError as e:
                raise Exception(f"Error de red al intentar conectar con el servicio de usuarios: {e}")