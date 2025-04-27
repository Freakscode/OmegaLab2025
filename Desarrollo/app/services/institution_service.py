from sqlalchemy.orm import Session
from app.models import Institution, InstitutionCreate, InstitutionResponse
from typing import List, Optional
from fastapi import HTTPException

class InstitutionService:
    def __init__(self, db: Session):
        self.db = db

    def crear_institucion(self, institucion_data: InstitutionCreate) -> InstitutionResponse:
        # Verificar si el código ya existe
        if self.db.query(Institution).filter(Institution.codigo == institucion_data.codigo).first():
            raise HTTPException(status_code=400, detail="El código de institución ya está registrado")

        # Crear institución
        institucion = Institution(
            nombre=institucion_data.nombre,
            codigo=institucion_data.codigo,
            configuracion=institucion_data.configuracion
        )
        self.db.add(institucion)
        self.db.commit()
        self.db.refresh(institucion)

        return institucion

    def obtener_institucion(self, institucion_id: int) -> Optional[InstitutionResponse]:
        return self.db.query(Institution).filter(Institution.id == institucion_id).first()

    def obtener_institucion_por_codigo(self, codigo: str) -> Optional[InstitutionResponse]:
        return self.db.query(Institution).filter(Institution.codigo == codigo).first()

    def listar_instituciones(self) -> List[InstitutionResponse]:
        return self.db.query(Institution).all()

    def actualizar_institucion(self, institucion_id: int, institucion_data: InstitutionCreate) -> Optional[InstitutionResponse]:
        institucion = self.db.query(Institution).filter(Institution.id == institucion_id).first()
        if not institucion:
            return None

        # Verificar si el nuevo código ya existe en otra institución
        if institucion_data.codigo != institucion.codigo:
            if self.db.query(Institution).filter(Institution.codigo == institucion_data.codigo).first():
                raise HTTPException(status_code=400, detail="El código de institución ya está registrado")

        institucion.nombre = institucion_data.nombre
        institucion.codigo = institucion_data.codigo
        institucion.configuracion = institucion_data.configuracion

        self.db.commit()
        self.db.refresh(institucion)

        return institucion

    def eliminar_institucion(self, institucion_id: int) -> bool:
        institucion = self.db.query(Institution).filter(Institution.id == institucion_id).first()
        if not institucion:
            return False

        # Verificar si hay estudiantes o administradores asociados
        if institucion.estudiantes or institucion.admins:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar la institución porque tiene estudiantes o administradores asociados"
            )

        self.db.delete(institucion)
        self.db.commit()

        return True

    def obtener_configuracion(self, institucion_id: int) -> Optional[dict]:
        institucion = self.db.query(Institution).filter(Institution.id == institucion_id).first()
        if not institucion:
            return None
        return institucion.configuracion

    def actualizar_configuracion(self, institucion_id: int, configuracion: dict) -> Optional[InstitutionResponse]:
        institucion = self.db.query(Institution).filter(Institution.id == institucion_id).first()
        if not institucion:
            return None

        institucion.configuracion = configuracion
        self.db.commit()
        self.db.refresh(institucion)

        return institucion 