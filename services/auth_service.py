from fastapi import HTTPException
import httpx
from typing import Dict, Any

class AuthService:
    def __init__(self, base_url: str):
        """
        Inicializa el servicio con la URL base del microservicio de autenticación.
        """
        self.base_url = base_url

    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        payload = {
            "username": username,
            "password": password
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/auth/token", json=payload)
                response.raise_for_status()  # Lanza una excepción si la respuesta es un error 4xx/5xx
                return response.json()
            except httpx.HTTPStatusError as e:
                # Si el microservicio de autenticación devuelve un error, lo reenvía
                # Por ejemplo, un 401 si las credenciales son incorrectas
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Credenciales de autenticación inválidas: {e.response.text}"
                )
            except httpx.RequestError as e:
                # Maneja errores de conexión o de solicitud
                raise Exception(f"Error de red al intentar conectar con el servicio de autenticación: {e}")