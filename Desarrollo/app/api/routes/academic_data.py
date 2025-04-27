from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.academic_data_service import AcademicDataService
from app.models import AcademicHistory
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/academic-data", tags=["academic-data"])

class EventoAcademicoCreate(BaseModel):
    estudiante_id: int
    evento: str
    detalles: str
    promedio: Optional[float] = None

class DatosLMSCreate(BaseModel):
    estudiante_id: int
    horas_actividad_semanal: float

class ServiciosApoyoCreate(BaseModel):
    estudiante_id: int
    servicios_utilizados: List[str]

@router.post("/evento-academico", response_model=dict)
def registrar_evento_academico(
    evento: EventoAcademicoCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un evento académico para un estudiante.
    """
    try:
        service = AcademicDataService(db)
        success = service.registrar_evento_academico(
            estudiante_id=evento.estudiante_id,
            evento=evento.evento,
            detalles=evento.detalles,
            promedio=evento.promedio
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo registrar el evento académico")
            
        return {"message": "Evento académico registrado correctamente"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/datos-lms", response_model=dict)
def actualizar_datos_lms(
    datos: DatosLMSCreate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de actividad en el LMS para un estudiante.
    """
    try:
        service = AcademicDataService(db)
        success = service.actualizar_datos_lms(
            estudiante_id=datos.estudiante_id,
            horas_actividad_semanal=datos.horas_actividad_semanal
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="No se pudieron actualizar los datos LMS")
            
        return {"message": "Datos LMS actualizados correctamente"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/servicios-apoyo", response_model=dict)
def actualizar_servicios_apoyo(
    datos: ServiciosApoyoCreate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de uso de servicios de apoyo para un estudiante.
    """
    try:
        service = AcademicDataService(db)
        success = service.actualizar_uso_servicios_apoyo(
            estudiante_id=datos.estudiante_id,
            servicios_utilizados=datos.servicios_utilizados
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="No se pudieron actualizar los datos de servicios")
            
        return {"message": "Datos de servicios de apoyo actualizados correctamente"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historial/{estudiante_id}", response_model=List[dict])
def obtener_historial_academico(
    estudiante_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial académico de un estudiante.
    """
    try:
        historial = db.query(AcademicHistory).filter(
            AcademicHistory.estudiante_id == estudiante_id
        ).order_by(AcademicHistory.fecha.desc()).all()
        
        return [
            {
                "id": h.id,
                "fecha": h.fecha.isoformat(),
                "evento": h.evento,
                "detalles": h.detalles,
                "promedio": h.promedio
            }
            for h in historial
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 