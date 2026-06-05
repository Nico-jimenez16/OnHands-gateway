import httpx

async def forward_request(
    method: str, 
    url: str, 
    data=None, 
    headers=None
    ):
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, json=data, headers=headers)
        response.raise_for_status()  # Lanza error si status != 2xx
        return response.json()
