# API Gateway — Contrato de API

## Stack

- **Framework**: FastAPI (sobre Starlette) + Uvicorn como servidor ASGI
- **HTTP client downstream**: `httpx.AsyncClient` (instanciado por llamada, sin pooling)
- **Validación**: Pydantic v2 + `pydantic-settings` para cargar `.env`
- **Auth**: `pyjwt` para validar tokens HS256
- **Runtime**: Python 3.11 (imagen base `python:3.11-slim` en `Dockerfile`)
- **Puerto**: `8000` (configurable vía `app_port`; el `Dockerfile` lo fija en `0.0.0.0:8000`)
- **Entrypoint**: `uvicorn api_gateway.main:app` — debe ejecutarse desde el directorio padre porque el módulo usa imports relativos. `run.py` apunta a `src.gateway.app:app` (inexistente) y **no funciona**.

No hay tests, linter, formateador ni `docker-compose.yml` en el repo. La orquestación se hace con comandos `docker run` manuales (ver `../Commands.md`).

## Variables de entorno requeridas

Cargadas desde `api_gateway/.env` por `core/settings.py`. **Todas obligatorias**: la app no arranca si falta alguna (Pydantic Settings no tiene defaults definidos).

| Variable | Descripción | Valor por defecto en `.env` |
|---|---|---|
| `app_name` | Nombre mostrado en docs y en `/` | `"ApiGateway- OnHands"` |
| `app_description` | Descripción para OpenAPI | `"API Gateway para el sistema de gestión de servicios"` |
| `app_version` | Versión OpenAPI | `"1.0.0"` |
| `app_env` | Entorno lógico (no usado en código) | `"development"` |
| `app_host` | Host de bind (no usado por el `uvicorn` del README) | `"127.0.0.1"` |
| `app_port` | Puerto de bind (no usado por el `uvicorn` del README) | `8000` |
| `AUTH_SERVICE_URL` | URL base del servicio de autenticación | `http://localhost:8001` |
| `USERS_SERVICE_URL` | URL base del servicio de usuarios | `http://localhost:8002` |
| `REQUEST_SERVICE_URL` | URL base del ticket-service (NestJS) | `http://localhost:8003` |
| `CORE_SERVICE_URL` | URL base del CoreService (chat) | `http://localhost:8004` |
| `JWT_SECRET_KEY` | Secreto HS256 para validar el token | `"your-super-strong-and-secret-key-here"` (⚠ placeholder) |
| `JWT_ALGORITHM` | Algoritmo JWT esperado | `"HS256"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Declarado pero **no se usa** en el código | `60` |

`REDIS_URL` figura comentada en el `.env` para futuro rate limiting, pero no hay implementación.

## Rutas definidas

> **Nota global sobre montaje**: `main.py` solo monta `service_request_routes` (prefijo `/requests`) y `chat_routes` (prefijo `/chat`). `auth_routes` y `user_routes` están definidos pero **comentados** en `main.py:30-31`, por lo que `/auth/login`, `/users`, `/users/{id}` y `POST /users` **no están expuestos** actualmente. Se documentan abajo por si se reactivan.

---

### GET /

Health check inline (`main.py:34`).

- **Recibe del cliente**:
  - Headers: ninguno obligatorio
  - Body: ninguno
- **Transformaciones**: ninguna
- **Forwarding**: no hay (respuesta local)
- **Respuesta al cliente** (HTTP 200):
```json
{ "status": "ok", "service": "ApiGateway- OnHands" }
```
- **Middlewares**: CORS, AuthMiddleware (lo deja pasar por estar en `public_paths`), Logging

---

### GET /requests/

Listar todas las solicitudes (`api/endpoints/service_request_routes.py:12`).

- **Recibe del cliente**:
  - Headers usados: `x-user-id`, `x-user-role` (opcionales, se leen sin validar)
  - Body: ninguno
- **Transformaciones**: extrae los dos headers y arma un `dict`. Si el header no viene, el valor es `None` y se reenvía como tal (httpx serializa `None` como cadena vacía en algunos casos).
- **Forwarding a**: ticket-service → `GET {REQUEST_SERVICE_URL}/v1/requests/`
- **Body que manda al downstream**: no aplica (GET)
- **Headers que manda al downstream**:
```
x-user-id: <valor recibido o None>
x-user-role: <valor recibido o None>
```
- **Respuesta del downstream esperada**: JSON arbitrario (el gateway no valida la forma).
- **Respuesta que devuelve al cliente**: el JSON del downstream tal cual.
- **Errores**:
  - Si downstream devuelve 4xx/5xx: se propaga el status code y el body se mete en `detail` como texto.
  - Si falla la conexión: HTTP 503 con `detail: "Error al conectar con el servicio de solicitudes: ..."`.
- **Middlewares**: CORS, AuthMiddleware (ver bug en "Observaciones"), Logging

---

### GET /requests/{request_id}

Obtener una solicitud por ID (`api/endpoints/service_request_routes.py:31`).

- **Recibe del cliente**:
  - Headers: ninguno usado
  - Path param: `request_id: int` (FastAPI valida que sea entero, 422 si no lo es)
  - Body: ninguno
- **Transformaciones**: ninguna. **No propaga `x-user-id`/`x-user-role`** (inconsistencia con los otros endpoints de `/requests`).
- **Forwarding a**: ticket-service → `GET {REQUEST_SERVICE_URL}/v1/requests/{request_id}` sin headers personalizados.
- **Respuesta del downstream esperada**: JSON arbitrario.
- **Respuesta que devuelve al cliente**: el JSON del downstream tal cual.
- **Errores**: igual que `GET /requests/`.
- **Middlewares**: CORS, AuthMiddleware, Logging

---

### POST /requests/

Crear una solicitud (`api/endpoints/service_request_routes.py:46`).

- **Recibe del cliente**:
  - Headers usados: `x-user-id`, `x-user-role`
  - Content-Type: `application/json`
  - Body: `Dict[str, Any]` — **forma libre**, no hay modelo Pydantic. Cualquier JSON-object pasa la validación.
```json
{ "title": "string", "description": "string", "status": "pending" }
```
*(forma sugerida por `TEST_ENDPOINTS.md`, no enforced)*
- **Transformaciones**: extrae los dos headers; el body se reenvía sin modificar.
- **Forwarding a**: ticket-service → `POST {REQUEST_SERVICE_URL}/v1/requests/`
- **Body que manda al downstream**: idéntico al recibido del cliente.
- **Headers que manda al downstream**:
```
x-user-id: <valor recibido o None>
x-user-role: <valor recibido o None>
Content-Type: application/json    (lo agrega httpx automáticamente)
```
- **Respuesta del downstream esperada**: JSON arbitrario.
- **Respuesta que devuelve al cliente**: el JSON del downstream tal cual.
- **Errores**: igual que `GET /requests/`.
- **Middlewares**: CORS, AuthMiddleware, Logging

---

### POST /chat/conversations

Iniciar conversación con el asistente (`api/endpoints/chat_routes.py:19`).

- **Recibe del cliente**:
  - Header usado: `x-user-id` (**default `"anonymous"`** si falta — el gateway nunca falla por esto)
  - Content-Type: `application/json`
  - Body (Pydantic `StartConversationBody`):
```json
{ "initial_message": "string" }
```
- **Transformaciones**: toma `x-user-id` del header (o `"anonymous"`) y lo mete al body junto con `initial_message`.
- **Forwarding a**: CoreService → `POST {CORE_SERVICE_URL}/api/v1/conversations`
- **Body que manda al downstream**:
```json
{ "user_id": "<x-user-id o 'anonymous'>", "initial_message": "string" }
```
- **Respuesta del downstream esperada**: JSON arbitrario (el gateway no valida).
- **Respuesta que devuelve al cliente**: el JSON del downstream tal cual.
- **Errores**:
  - 4xx/5xx del downstream: se propaga status code y body en `detail`.
  - Falla de red: HTTP 503 con `detail: "Error al conectar con el CoreService: ..."`.
- **Middlewares**: CORS, AuthMiddleware, Logging

---

### POST /chat/conversations/{conversation_id}/messages

Enviar mensaje a una conversación existente (`api/endpoints/chat_routes.py:30`).

- **Recibe del cliente**:
  - Header usado: `x-user-id` (default `"anonymous"`)
  - Path param: `conversation_id: str`
  - Body (Pydantic `SendMessageBody`):
```json
{ "message": "string" }
```
- **Transformaciones**: misma estrategia que `POST /chat/conversations` — inyecta `user_id` desde header.
- **Forwarding a**: CoreService → `POST {CORE_SERVICE_URL}/api/v1/conversations/{conversation_id}/messages`
- **Body que manda al downstream**:
```json
{ "user_id": "<x-user-id o 'anonymous'>", "message": "string" }
```
- **Respuesta del downstream esperada**: JSON arbitrario.
- **Respuesta que devuelve al cliente**: el JSON del downstream tal cual.
- **Errores**: idéntico a `POST /chat/conversations`.
- **Middlewares**: CORS, AuthMiddleware, Logging

---

### ⚠ Rutas definidas pero NO montadas

Estas existen en código pero `main.py` no las incluye. Si el frontend las consume, fallarán con 404.

#### POST /auth/login *(no montada)*

- Body Pydantic `UserCredentials`:
```json
{ "username": "string", "password": "string" }
```
- Forwarding a: `POST {AUTH_SERVICE_URL}/auth/token` con el mismo body.
- Respuesta esperada y devuelta: JSON arbitrario (presumiblemente `{ "access_token": "...", "token_type": "..." }`).

#### GET /users/ *(no montada)*

- Sin body ni headers especiales.
- Forwarding a: `GET {USERS_SERVICE_URL}/users/`.

#### GET /users/{user_id} *(no montada)*

- Path param `user_id: int`.
- Forwarding a: `GET {USERS_SERVICE_URL}/users/{user_id}`.

#### POST /users/ *(no montada)*

- Body `Dict[str, Any]` (forma libre).
- Forwarding a: `POST {USERS_SERVICE_URL}/users/` con el body sin modificar.

## Servicios downstream configurados

| Servicio | Variable | Puerto local | Host en red Docker | Endpoints invocados |
|---|---|---|---|---|
| Auth (no montado) | `AUTH_SERVICE_URL` | `8001` | — | `POST /auth/token` |
| Users (no montado) | `USERS_SERVICE_URL` | `8002` | — | `GET /users/`, `GET /users/{id}`, `POST /users/` |
| Tickets (NestJS) | `REQUEST_SERVICE_URL` | `8003` | `http://ticket-service:8003` | `GET /v1/requests/`, `GET /v1/requests/{id}`, `POST /v1/requests/` |
| CoreService (chat) | `CORE_SERVICE_URL` | `8004` | — | `POST /api/v1/conversations`, `POST /api/v1/conversations/{id}/messages` |

Los endpoints downstream **no son uniformes**: ticket-service usa `/v1/`, CoreService usa `/api/v1/`, users-service y auth-service no usan prefijo de versión. Cualquier endpoint nuevo debe respetar la convención del microservicio destino.

## Middlewares globales

Orden de ejecución según `main.py:18-26` (Starlette aplica los middlewares en orden inverso al `add_middleware`, así que el último agregado se ejecuta primero — el orden efectivo de entrada es: **Logging → Auth → CORS → ruta**):

### 1. CORS (`middleware/cors.py`)

`setup_cors_middleware(app)` con orígenes **hardcodeados**:
```
http://localhost
http://localhost:8000
http://localhost:8000   (sic, duplicado en la lista mental)
http://localhost:3000
http://127.0.0.1:3000
```
- `allow_credentials=True`
- `allow_methods=["*"]`, `allow_headers=["*"]`

No se puede cambiar sin editar código. Cualquier frontend en otro origen (preview deployments, dominios productivos) será bloqueado.

### 2. AuthMiddleware (`middleware/authentication.py`)

- Define `public_paths = ["/auth", "/"]`.
- Compara con `request.url.path.startswith(path) for path in public_paths`.
- Si pasa el chequeo de público → pasa libre.
- Si no, exige header `Authorization: Bearer <jwt>`, decodifica con `JWT_SECRET_KEY` y `JWT_ALGORITHM`.
- En caso de fallo lanza `HTTPException(401, "Token missing")` o `HTTPException(401, "Invalid token")`.
- **No agrega ni quita headers tras validar**. El claim del JWT no se inyecta en el request — los endpoints siguen confiando en `x-user-id`/`x-user-role` que debe poner alguien upstream.

### 3. LoggingMiddleware (`middleware/logging.py`)

- Logger `api_gateway_logger` con `logging.basicConfig(level=INFO)`.
- Loggea `{método} {url}` al entrar y `{método} {url} | Estado: {code} | Tiempo: {s}s` al salir.
- Si la ruta lanza excepción, loggea como error y re-lanza.

## Observaciones y problemas detectados

### 🔴 Bugs críticos

1. **`AuthMiddleware` no protege ninguna ruta** (`middleware/authentication.py:11-13`).
   `public_paths = ["/auth", "/"]` combinado con `startswith()` significa que cualquier path empieza con `"/"`, así que **todas las peticiones se consideran públicas**. El middleware existe pero no aplica. Fix: comparar igualdad para `"/"` o usar lista explícita de prefijos públicos sin el slash solo.

2. **`run.py` está roto** — referencia `src.gateway.app:app` que no existe. Usar `uvicorn api_gateway.main:app` directamente o el `CMD` del `Dockerfile`.

3. **`/auth/login` no está montado** pero el código existe. Si el frontend asume que puede loguearse contra el gateway, recibe 404. Mismo caso para todo `/users`.

### 🟡 Inconsistencias

4. **`GET /requests/{id}` no propaga `x-user-id`/`x-user-role`**, pero `GET /requests/` y `POST /requests/` sí lo hacen. Si el ticket-service usa esos headers para autorización por recurso, este endpoint puede romper o devolver datos de otro usuario.

5. **Endpoints aceptan `Dict[str, Any]`** (`POST /requests/`, `POST /users/`): cualquier JSON-object pasa. No hay validación de campos requeridos, tipos ni rangos — el contrato se delega al downstream, lo que produce errores 4xx ambiguos en vez de 422 informativos.

6. **`x-user-id` con default `"anonymous"`** en `/chat/...`: si nadie inyecta el header, todas las conversaciones se atribuyen al mismo "usuario". Probable fuente de cross-talk si el CoreService no lo valida.

### 🟠 Riesgos de configuración

7. **`JWT_SECRET_KEY` con valor placeholder** en `.env` (`"your-super-strong-and-secret-key-here"`). Aun cuando el `AuthMiddleware` se arregle (punto 1), este secreto debe rotarse antes de producción.

8. **`ACCESS_TOKEN_EXPIRE_MINUTES` declarado pero no usado** en ningún lado: el gateway no emite tokens, solo los valida. Si la intención era emitirlos, falta implementación.

9. **CORS hardcoded** — no se puede mover entre entornos sin recompilar la imagen.

10. **Sin pooling de httpx**: cada llamada crea un `AsyncClient` nuevo (`async with`). Bajo carga, esto añade latencia y consume puertos. Mover a un cliente compartido por servicio (singleton) sería el patrón habitual.

### 🟢 Limpieza pendiente

11. **`core/http_client.py::forward_request`** está definido pero **ningún servicio lo usa**. Las cuatro clases en `services/` reimplementan su propio bloque `try/except` con `httpx.AsyncClient`. O bien se adopta el helper, o se borra.

12. **Comentarios de Rate Limiting (Redis)** en `.env` sin implementación correspondiente — debería marcarse como TODO o eliminarse.

13. **`TEST_ENDPOINTS.md` describe contratos** (`title`/`description`/`status`) que el código no valida: documenta un contrato aspiracional, no el real.

### Inconsistencias con lo que probablemente espera el frontend

- El frontend del monorepo (`Frontend-OnHands`) usa `BACKEND_URL=http://api-gateway:8000` y `BACKEND_API_KEY=dev-key` (ver `../Commands.md`). **El gateway no valida ningún `BACKEND_API_KEY`** — esa autenticación inter-servicio no existe en este código.
- Si el frontend espera hacer `POST /auth/login` contra el gateway, fallará: la ruta no está montada.
- Si el frontend espera que el gateway extraiga `user_id` del JWT y lo inyecte, fallará silenciosamente: el gateway exige que el header `x-user-id` venga ya puesto (y cuando no viene, usa `"anonymous"` en chat o `None` en requests).
