import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api_gateway_logger")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Este método se invoca para cada solicitud entrante.
        """
        # 1. Registrar información de la solicitud antes de que se procese
        start_time = time.time()
        logger.info(f"Petición entrante: {request.method} {request.url}")

        try:
            # 2. Procesar la solicitud y obtener la respuesta
            response = await call_next(request)

            # 3. Registrar información de la respuesta después de que se ha generado
            process_time = time.time() - start_time
            response_status = response.status_code
            logger.info(
                f"Petición procesada: {request.method} {request.url} | "
                f"Estado: {response_status} | Tiempo: {process_time:.4f}s"
            )
            return response
        except Exception as e:
            # 4. Manejar excepciones y registrar errores
            process_time = time.time() - start_time
            logger.error(
                f"Error al procesar la petición: {request.method} {request.url} | "
                f"Error: {e} | Tiempo: {process_time:.4f}s"
            )
            raise e