# Instalar todas las dependencias del proyecto
pip install -r requirements.txt

# Crear entorno virtual - cmd
python -m venv .venv

# Activar entorno virtual - cmd
.venv\Scripts\activate

# Ejcutar el proyecto
uvicorn main:app --reload

