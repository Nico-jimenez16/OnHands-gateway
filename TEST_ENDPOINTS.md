# Guía de Pruebas - API Gateway

## Endpoints Disponibles

### 1. Health Check
**Endpoint:** `GET /`  
**Descripción:** Verifica que el API Gateway esté funcionando correctamente.

```bash
curl http://localhost:8000/
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "service": "MiApp"
}
```

---

### 2. Obtener Todas las Solicitudes
**Endpoint:** `GET /requests/`  
**Descripción:** Obtiene todas las solicitudes de servicio desde el microservicio de backend.

```bash
curl http://localhost:8000/requests/
```

**Con PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/requests/" -Method GET | Select-Object -ExpandProperty Content
```

---

### 3. Obtener Solicitud por ID
**Endpoint:** `GET /requests/{request_id}`  
**Descripción:** Obtiene una solicitud específica por su ID.

```bash
curl http://localhost:8000/requests/1
```

**Con PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/requests/1" -Method GET | Select-Object -ExpandProperty Content
```

---

### 4. Crear Nueva Solicitud
**Endpoint:** `POST /requests/`  
**Descripción:** Crea una nueva solicitud de servicio.

```bash
curl -X POST http://localhost:8000/requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nueva solicitud",
    "description": "Descripción de la solicitud",
    "status": "pending"
  }'
```

**Con PowerShell:**
```powershell
$body = @{
    title = "Nueva solicitud"
    description = "Descripción de la solicitud"
    status = "pending"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/requests/" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

---

## Documentación Interactiva

FastAPI genera automáticamente documentación interactiva. Accede a:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Desde Swagger UI puedes probar todos los endpoints directamente desde el navegador.

---

## Requisitos Previos

1. **Microservicio de Requests debe estar corriendo:**
   - Verifica que el microservicio esté disponible en la URL configurada en `.env`
   - Por defecto: `http://localhost:8001`

2. **Variables de entorno configuradas:**
   ```env
   REQUEST_SERVICE_URL="http://localhost:8001"
   ```

3. **Iniciar el API Gateway:**
   ```bash
   uvicorn api_gateway.main:app --reload
   ```

---

## Pruebas con Postman

1. Importa la colección de endpoints
2. Configura la variable de entorno `base_url` como `http://localhost:8000`
3. Ejecuta las peticiones en el siguiente orden:
   - Health Check
   - GET todas las solicitudes
   - GET solicitud por ID
   - POST crear nueva solicitud

---

## Solución de Problemas

### Error 503 - Service Unavailable
- Verifica que el microservicio de requests esté corriendo
- Revisa la URL en el archivo `.env`

### Error 401 - Unauthorized
- Algunos endpoints pueden requerir autenticación
- Verifica que el token JWT esté incluido en el header `Authorization: Bearer <token>`

### Error 404 - Not Found
- Verifica que la ruta sea correcta: `/requests/` (con el prefijo)
- Asegúrate de que el ID de la solicitud exista en el microservicio
