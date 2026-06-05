from fastapi import APIRouter, HTTPException
import httpx

from ...core.settings import settings

router = APIRouter()


@router.get("/{request_id}", summary="Estado de matching de una solicitud")
async def get_match(request_id: str):
    url = f"{settings.CORE_SERVICE_URL}/api/v1/requests/{request_id}/status"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail={"error": "Error al obtener estado de matching"})
