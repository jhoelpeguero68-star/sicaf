"""
SICAF - Script de Inicio del Servidor
Ejecuta uvicorn en el puerto asignado por Render ($PORT) o 8000 por defecto
"""
import os
import uvicorn
from backend.seed_data import seed_all

if __name__ == "__main__":
    seed_all()
    port = int(os.environ.get("PORT", 8000))
    print(f"Iniciando SICAF en el puerto {port} ...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)

