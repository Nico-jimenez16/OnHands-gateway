import uvicorn
from .core.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.gateway.app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
