from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import uvicorn
import os
from pathlib import Path

from app.database import get_db, engine, Base
from app.api.routes import admin, students, prediccion, chat, institution, academic_data, auth
from app.utils.logger import RequestLogger, setup_logger
from app.services.ml_model_service import MLModelService

# Crear directorio de logs si no existe
Path("logs").mkdir(exist_ok=True)

# Configurar logger principal
logger = setup_logger("main", "main.log")

# Crear aplicación FastAPI
app = FastAPI(
    title="OmegaLab API",
    description="API para el sistema de predicción de estrés académico",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar middleware de logging
app.add_middleware(RequestLogger)

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar servicio de modelos ML
ml_service = MLModelService()
if not ml_service.load_models():
    logger.error("No se pudieron cargar los modelos de ML")
    # En producción, podrías querer detener la aplicación aquí
    # raise Exception("No se pudieron cargar los modelos de ML")

# Incluir routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(students.router)
app.include_router(prediccion.router)
app.include_router(chat.router)
app.include_router(institution.router)
app.include_router(academic_data.router)

@app.get("/")
async def root():
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {"message": "OmegaLab API está funcionando correctamente"}

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar la salud del sistema.
    """
    health_status = {
        "status": "healthy",
        "ml_models_loaded": ml_service.is_loaded,
        "database": "connected"  # Podrías agregar más verificaciones aquí
    }
    
    if not ml_service.is_loaded:
        health_status["status"] = "degraded"
        health_status["message"] = "Los modelos de ML no están cargados"
        
    return health_status

if __name__ == "__main__":
    # Configuración para desarrollo
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 