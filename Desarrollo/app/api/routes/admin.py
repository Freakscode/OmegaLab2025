from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.admin_service import AdminService
from app.schemas import AdminCreate, AdminResponse

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/", response_model=AdminResponse)
def crear_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    admin_service = AdminService(db)
    return admin_service.crear_admin(admin_data)

@router.get("/{admin_id}", response_model=AdminResponse)
def obtener_admin(admin_id: int, db: Session = Depends(get_db)):
    admin_service = AdminService(db)
    admin = admin_service.obtener_admin(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    return admin

@router.get("/", response_model=List[AdminResponse])
def listar_admins(db: Session = Depends(get_db)):
    admin_service = AdminService(db)
    return admin_service.listar_admins()

@router.put("/{admin_id}", response_model=AdminResponse)
def actualizar_admin(admin_id: int, admin_data: AdminCreate, db: Session = Depends(get_db)):
    admin_service = AdminService(db)
    admin = admin_service.actualizar_admin(admin_id, admin_data)
    if not admin:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    return admin

@router.delete("/{admin_id}")
def eliminar_admin(admin_id: int, db: Session = Depends(get_db)):
    admin_service = AdminService(db)
    if not admin_service.eliminar_admin(admin_id):
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    return {"message": "Administrador eliminado exitosamente"} 