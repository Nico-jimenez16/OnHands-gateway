# Instalar todas las dependencias del proyecto
pip install -r requirements.txt

# Crear entorno virtual - cmd
python -m venv .venv

# Activar entorno virtual - cmd
.venv\Scripts\activate

# Ejcutar el proyecto
uvicorn api_gateway.main:app --reload



# git Command...
# Subir al Repositorio:
git init
git remote add origin https://github.com/Nico-jimenez16/On-Demand_Api_gateway.git
git add .
git commit -m "Subida inicial del proyecto On-Demand"
git branch -M main
git push -u origin main

# Crear otra Rama:
git checkout -b dev
git push -u origin dev

# Agregar cosas nuevas:
git add .
git commit -m "refactor: Cambios en los componentes y en el codigo"
git push origin dev
git push origin main

# Cambiar de Rama:
git checkout main
git checkout dev
