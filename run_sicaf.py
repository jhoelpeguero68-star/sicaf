"""
SICAF - Script de Inicio del Servidor
Ejecuta uvicorn en el puerto 8000
"""
import uvicorn
from backend.seed_data import seed_all

if __name__ == "__main__":
    seed_all()
    print("Iniciando SICAF en http://localhost:8000 ...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
