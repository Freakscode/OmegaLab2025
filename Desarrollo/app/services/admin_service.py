from sqlalchemy.orm import Session
from app.models import Admin, User, UserRole
from app.schemas import AdminCreate, AdminResponse
from typing import List, Optional
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def crear_admin(self, admin_data: AdminCreate) -> AdminResponse:
        # Verificar si el email ya existe
        if self.db.query(User).filter(User.email == admin_data.usuario.email).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado")

        # Crear usuario
        hashed_password = pwd_context.hash(admin_data.usuario.password)
        usuario = User(
            email=admin_data.usuario.email,
            hashed_password=hashed_password,
            nombre=admin_data.usuario.nombre,
            rol=UserRole.ADMIN
        )
        self.db.add(usuario)
        self.db.flush()  # Para obtener el ID del usuario

        # Crear admin
        admin = Admin(
            usuario_id=usuario.id,
            departamento=admin_data.departamento,
            permisos=admin_data.permisos
        )
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)

        return AdminResponse(
            id=admin.id,
            usuario_id=admin.usuario_id,
            departamento=admin.departamento,
            permisos=admin.permisos,
            usuario=admin.usuario
        )

    def obtener_admin(self, admin_id: int) -> Optional[AdminResponse]:
        admin = self.db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return None
        return AdminResponse(
            id=admin.id,
            usuario_id=admin.usuario_id,
            departamento=admin.departamento,
            permisos=admin.permisos,
            usuario=admin.usuario
        )

    def obtener_admin_por_email(self, email: str) -> Optional[AdminResponse]:
        admin = self.db.query(Admin).join(User).filter(User.email == email).first()
        if not admin:
            return None
        return AdminResponse(
            id=admin.id,
            usuario_id=admin.usuario_id,
            departamento=admin.departamento,
            permisos=admin.permisos,
            usuario=admin.usuario
        )

    def listar_admins(self) -> List[AdminResponse]:
        admins = self.db.query(Admin).all()
        return [
            AdminResponse(
                id=admin.id,
                usuario_id=admin.usuario_id,
                departamento=admin.departamento,
                permisos=admin.permisos,
                usuario=admin.usuario
            )
            for admin in admins
        ]

    def actualizar_admin(self, admin_id: int, admin_data: AdminCreate) -> Optional[AdminResponse]:
        admin = self.db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return None

        # Actualizar usuario
        usuario = admin.usuario
        if admin_data.usuario.email != usuario.email:
            if self.db.query(User).filter(User.email == admin_data.usuario.email).first():
                raise HTTPException(status_code=400, detail="El email ya está registrado")
            usuario.email = admin_data.usuario.email
        
        if admin_data.usuario.password:
            usuario.hashed_password = pwd_context.hash(admin_data.usuario.password)
        
        usuario.nombre = admin_data.usuario.nombre

        # Actualizar admin
        admin.departamento = admin_data.departamento
        admin.permisos = admin_data.permisos

        self.db.commit()
        self.db.refresh(admin)

        return AdminResponse(
            id=admin.id,
            usuario_id=admin.usuario_id,
            departamento=admin.departamento,
            permisos=admin.permisos,
            usuario=admin.usuario
        )

    def eliminar_admin(self, admin_id: int) -> bool:
        admin = self.db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return False

        # Eliminar usuario asociado
        usuario = admin.usuario
        self.db.delete(admin)
        self.db.delete(usuario)
        self.db.commit()

        return True 