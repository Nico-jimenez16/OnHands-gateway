from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI # Importamos FastAPI para tipado, aunque en StarletteApp es suficiente

# La función debe tomar la instancia de la aplicación como argumento.
def setup_cors_middleware(app: FastAPI):
    """
    Configura el middleware de CORS para la aplicación.
    """
    # Define tus orígenes permitidos aquí.
    # Usando los orígenes que tienes en tu main.py para ser consistente.
    origins = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000" # Agregado desde main.py
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
        allow_headers=["*"],  # Permite todos los encabezados
    )

    print("Middleware CORS configurado.") # Opcional: para confirmación