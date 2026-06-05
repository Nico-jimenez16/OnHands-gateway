import httpx
from typing import Dict, Any
from fastapi import HTTPException


class ChatService:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def start_conversation(self, user_id: str, initial_message: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/conversations",
                    json={"user_id": user_id, "initial_message": initial_message},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
            except httpx.RequestError as e:
                raise Exception(f"Error de red al conectar con el CoreService: {e}")

    async def send_message(self, conversation_id: str, user_id: str, message: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/conversations/{conversation_id}/messages",
                    json={"user_id": user_id, "message": message},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
            except httpx.RequestError as e:
                raise Exception(f"Error de red al conectar con el CoreService: {e}")
