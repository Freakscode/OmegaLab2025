from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.institution_service import InstitutionService
from app.models import InstitutionCreate, InstitutionResponse

router = APIRouter(prefix="/institution", tags=["institution"])

@router.post("/", response_model=InstitutionResponse)
def crear_institucion(institucion_data: InstitutionCreate, db: Session = Depends(get_db)):
    institution_service = InstitutionService(db)
    return institution_service.crear_institucion(institucion_data)

@router.get("/{institucion_id}", response_model=InstitutionResponse)
def obtener_institucion(institucion_id: int, db: Session = Depends(get_db)):
    institution_service = InstitutionService(db)
    institucion = institution_service.obtener_institucion(institucion_id)
    if not institucion:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return institucion

@router.get("/", response_model=List[InstitutionResponse])
def listar_instituciones(db: Session = Depends(get_db)):
    institution_service = InstitutionService(db)
    return institution_service.listar_instituciones()

@router.put("/{institucion_id}", response_model=InstitutionResponse)
def actualizar_institucion(institucion_id: int, institucion_data: InstitutionCreate, db: Session = Depends(get_db)):
    institution_service = InstitutionService(db)
    institucion = institution_service.actualizar_institucion(institucion_id, institucion_data)
    if not institucion:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return institucion

@router.delete("/{institucion_id}")
def eliminar_institucion(institucion_id: int, db: Session = Depends(get_db)):
    institution_service = InstitutionService(db)
    if not institution_service.eliminar_institucion(institucion_id):
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return {"message": "Institución eliminada exitosamente"}

@router.get("/{institucion_id}/configuracion")
def obtener_configuracion(institucion_id: int, db: Session = Depends(get_db)):
    institution_service = InstitutionService(db)
    configuracion = institution_service.obtener_configuracion(institucion_id)
    if not configuracion:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return configuracion

@router.put("/{institucion_id}/configuracion", response_model=InstitutionResponse)
def actualizar_configuracion(institucion_id: int, configuracion: dict, db: Session = Depends(get_db)):
    institution_service = InstitutionService(db)
    institucion = institution_service.actualizar_configuracion(institucion_id, configuracion)
    if not institucion:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return institucion 