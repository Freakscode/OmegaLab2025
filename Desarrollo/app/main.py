from fastapi import FastAPI
from app.api.endpoints import predict
from contextlib import asynccontextmanager
from app.services.prediction import load_artifacts # Importa la función para cargar artefactos

# Función para manejar eventos de lifespan (startup/shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código a ejecutar al inicio de la aplicación
    print("Iniciando aplicación y cargando artefactos...")
    try:
        # Cargar modelos/preprocesadores al inicio (RF04)
        load_artifacts()
        print("Artefactos cargados correctamente.")
    except Exception as e:
        print(f"Error al cargar artefactos: {e}")
        # Decide si quieres detener la aplicación o continuar sin los artefactos
        # raise e # Descomentar para detener la app si la carga falla
    yield
    # Código a ejecutar al apagar la aplicación (si es necesario)
    print("Apagando aplicación...")

# Crea la instancia de la aplicación FastAPI con el lifespan manager
app = FastAPI(
    title="API de Predicción de Estrés Académico",
    description="API para predecir la probabilidad de estrés académico en estudiantes.",
    version="0.1.0",
    lifespan=lifespan # Asocia el manejador de lifespan
)

# Incluye el router para el endpoint de predicción
app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])

@app.get("/health", tags=["Health Check"])
async def health_check():
    """Endpoint simple para verificar que la API está activa."""
    return {"status": "ok"}

# (Opcional) Si necesitas configuración adicional, puedes añadirla aquí.

# Nota: La ejecución real se hace con Uvicorn como se especifica en el Dockerfile o manualmente. 