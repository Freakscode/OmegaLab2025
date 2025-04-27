from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models import (
    Student,
    StressPrediction,
    PredictionRequest,
    PredictionResponse,
    StudentPersonalInfo,
    AcademicHistory
)
from ..services.prediccion import PrediccionService
from ..dependencies import get_prediccion_service

router = APIRouter(prefix="/prediccion", tags=["prediccion"])

@router.post("/estudiante/{estudiante_id}", response_model=PredictionResponse)
async def predecir_estres_estudiante(
    estudiante_id: int,
    request: PredictionRequest,
    prediccion_service: PrediccionService = Depends(get_prediccion_service)
):
    """
    Realiza una predicción de estrés académico para un estudiante específico.
    """
    try:
        prediccion = await prediccion_service.predecir_estres(
            estudiante_id=estudiante_id,
            datos_academicos=request.datos_academicos,
            datos_personales=request.datos_personales,
            historial_academico=request.historial_academico
        )
        return prediccion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/estudiantes", response_model=List[Student])
async def obtener_estudiantes_con_prediccion(
    prediccion_service: PrediccionService = Depends(get_prediccion_service)
):
    """
    Obtiene la lista de estudiantes con sus predicciones de estrés.
    """
    try:
        estudiantes = await prediccion_service.obtener_estudiantes_con_prediccion()
        return estudiantes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/estudiante/{estudiante_id}/historial", response_model=List[AcademicHistory])
async def obtener_historial_academico(
    estudiante_id: int,
    prediccion_service: PrediccionService = Depends(get_prediccion_service)
):
    """
    Obtiene el historial académico de un estudiante.
    """
    try:
        historial = await prediccion_service.obtener_historial_academico(estudiante_id)
        return historial
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 