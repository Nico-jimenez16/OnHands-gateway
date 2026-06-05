# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos de desarrollo

El servidor se ejecuta como package Python (usa imports relativos), por lo que **debe** lanzarse desde el directorio padre `OnHands-Project/`, no desde dentro de `api_gateway/`:

```powershell
# Desde OnHands-Project/ (un nivel arriba de este directorio)
python -m venv .venv
.venv\Scripts\activate
pip install -r api_gateway/requirements.txt
uvicorn api_gateway.main:app --reload
```

El servidor escucha por defecto en `http://127.0.0.1:8000`. Docs interactivas en `/docs` (Swagger) y `/redoc`.

Nota: `run.py` referencia un módulo inexistente (`src.gateway.app:app`) y no funciona — usar siempre `uvicorn api_gateway.main:app` o el `CMD` del `Dockerfile`. No hay suite de tests ni linter configurados en el repo.

### Docker

Build y ejecución de los tres servicios en una red compartida (ver `../Commands.md` para el flujo completo del monorepo):

```powershell
docker network create on_demand_net
docker build -t onhands-api-gateway ./api_gateway
docker run -d --name api-gateway --network on_demand_net -p 8000:8000 `
  --env-file ./api_gateway/.env `
  -e REQUEST_SERVICE_URL=http://ticket-service:8003 `
  onhands-api-gateway
```

Cuando los servicios corren dentro de la red Docker, los hosts deben ser los nombres de contenedor (`ticket-service`, no `localhost`).

## Variables de entorno

`core/settings.py` usa `pydantic-settings` con `extra="ignore"` no configurado, así que **todas** las variables son obligatorias y la app fallará en el arranque si falta alguna. Se cargan desde `api_gateway/.env`:

- App: `app_name`, `app_description`, `app_version`, `app_env`, `app_host`, `app_port`
- Microservicios: `AUTH_SERVICE_URL`, `USERS_SERVICE_URL`, `REQUEST_SERVICE_URL`, `CORE_SERVICE_URL`
- JWT: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`

## Arquitectura

Este servicio es el **API Gateway** del monorepo OnHands (otros servicios viven en carpetas hermanas: `NestJS-ticketService`, `On-Hands-CoreService`, `Frontend-OnHands`). Su única responsabilidad es reenviar peticiones HTTP a microservicios downstream — no contiene lógica de dominio ni persistencia.

### Flujo de una petición

`main.py` ensambla el pipeline en este orden (importa lo que sigue):

1. **CORS** (`middleware/cors.py`) — orígenes hardcodeados (`localhost:3000`, `localhost:8000`, etc.). Si el frontend corre en otro origen hay que editarlo aquí.
2. **`AuthMiddleware`** (`middleware/authentication.py`) — exige `Authorization: Bearer <jwt>` salvo para rutas que empiecen con `/auth` o `/`. **Importante**: el prefijo `/` deja pasar TODO al usar `startswith("/")`, así que en la práctica el middleware no bloquea ninguna ruta tal como está. Si se necesita protección real, esta lista de `public_paths` debe corregirse.
3. **`LoggingMiddleware`** (`middleware/logging.py`) — log de método, URL, status y duración.
4. **Routers** — montados con prefijos: `/requests` y `/chat` activos; `/auth` y `/users` están comentados en `main.py` pese a existir los archivos.

### Patrón endpoint → service

Cada feature sigue la misma estructura de tres capas:

- `api/endpoints/<feature>_routes.py` — define el `APIRouter`, valida con Pydantic e instancia el cliente del servicio pasando la URL base desde `settings`.
- `services/<feature>_service.py` — clase que envuelve `httpx.AsyncClient` para hacer la llamada al microservicio. Convierte `HTTPStatusError` en `HTTPException` (propaga status code) y `RequestError` en `Exception` genérica.
- El endpoint atrapa `HTTPException` (re-lanza) y cualquier otra `Exception` la convierte en `503`.

`core/http_client.py` define `forward_request()` como helper alternativo pero **no se usa**; los servicios crean su propio `httpx.AsyncClient` por llamada. Si se añade un servicio nuevo, seguir el patrón de clase con `base_url` en el constructor, no usar `forward_request`.

### Convenciones de rutas downstream

Cada microservicio tiene su propio esquema de URLs y el gateway debe respetarlo:

- **ticket-service** (`REQUEST_SERVICE_URL`): prefijo `/v1/requests/`
- **core-service / chat** (`CORE_SERVICE_URL`): prefijo `/api/v1/conversations`
- **users-service** (`USERS_SERVICE_URL`): prefijo `/users/`
- **auth-service** (`AUTH_SERVICE_URL`): endpoint `/auth/token`

### Propagación de identidad

El gateway no decodifica el JWT para extraer el usuario. En su lugar, los endpoints leen los headers `x-user-id` y `x-user-role` del request entrante y los reenvían tal cual al microservicio (ver `service_request_routes.py`). Esto asume que un componente upstream (proxy o el propio cliente) ya los inyectó. Al añadir endpoints que requieran contexto de usuario, replicar este patrón en vez de parsear el token.
