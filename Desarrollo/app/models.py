from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import enum

Base = declarative_base()

# Enumeración para el rol del mensaje
class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# Enumeración para el rol de usuario
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"

# Modelos de Base de Datos
class Institution(Base):
    __tablename__ = "institutions"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    configuracion = Column(JSON, nullable=True)  # Para configuraciones específicas
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relaciones
    admins = relationship("Admin", back_populates="institucion")
    estudiantes = relationship("Student", back_populates="institucion")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    nombre = Column(String(100), nullable=False)
    rol = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relaciones
    estudiante = relationship("Student", back_populates="usuario", uselist=False)
    admin = relationship("Admin", back_populates="usuario", uselist=False)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), unique=True)
    institucion_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    departamento = Column(String(100), nullable=True)
    permisos = Column(JSON, nullable=True)  # Para almacenar permisos específicos
    
    # Relaciones
    usuario = relationship("User", back_populates="admin")
    institucion = relationship("Institution", back_populates="admins")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), unique=True)
    institucion_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    programa = Column(String(100), nullable=False)
    semestre = Column(Integer, nullable=False)
    departamento = Column(String(100))
    riesgo_estres = Column(Float, default=0.0)
    riesgo_desercion = Column(Float, default=0.0)
    factores_estres = Column(JSON)
    
    # Relaciones
    usuario = relationship("User", back_populates="estudiante")
    institucion = relationship("Institution", back_populates="estudiantes")
    predicciones = relationship("StressPrediction", back_populates="estudiante")
    historial_academico = relationship("AcademicHistory", back_populates="estudiante")
    conversaciones = relationship("Conversation", back_populates="estudiante")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("students.id"))
    fecha_inicio = Column(DateTime, default=datetime.now)
    fecha_fin = Column(DateTime, nullable=True)
    contexto = Column(Text, nullable=True)
    estado = Column(String(20), default="activa")  # activa, finalizada
    
    estudiante = relationship("Student", back_populates="conversaciones")
    mensajes = relationship("Message", back_populates="conversacion")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversacion_id = Column(Integer, ForeignKey("conversations.id"))
    rol = Column(Enum(MessageRole), nullable=False)
    contenido = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.now)
    mensaje_metadata = Column(JSON, nullable=True)  # Para información adicional como sentimiento, intención, etc.
    
    conversacion = relationship("Conversation", back_populates="mensajes")

class StressPrediction(Base):
    __tablename__ = "stress_predictions"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("students.id"))
    fecha_prediccion = Column(DateTime, default=datetime.now)
    nivel_estres = Column(Float, nullable=False)
    probabilidad_abandono = Column(Float, nullable=False)
    factores_riesgo = Column(JSON)
    
    estudiante = relationship("Student", back_populates="predicciones")

class AcademicHistory(Base):
    __tablename__ = "academic_history"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("students.id"))
    fecha = Column(DateTime, default=datetime.now)
    evento = Column(String(100), nullable=False)
    detalles = Column(Text)
    promedio = Column(Float)
    
    estudiante = relationship("Student", back_populates="historial_academico")

# Modelos Pydantic para la API
class InstitutionBase(BaseModel):
    nombre: str
    codigo: str
    configuracion: Optional[Dict[str, Any]] = None

class InstitutionCreate(InstitutionBase):
    pass

class InstitutionResponse(InstitutionBase):
    id: int
    activa: bool
    fecha_creacion: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: EmailStr
    nombre: str

class UserCreate(UserBase):
    password: str
    rol: UserRole = UserRole.STUDENT

class UserResponse(UserBase):
    id: int
    rol: UserRole
    activo: bool
    fecha_creacion: datetime

    class Config:
        orm_mode = True

class AdminBase(BaseModel):
    departamento: Optional[str] = None
    permisos: Optional[Dict[str, Any]] = None

class AdminCreate(AdminBase):
    usuario: UserCreate

class AdminResponse(AdminBase):
    id: int
    usuario_id: int
    usuario: UserResponse

    class Config:
        orm_mode = True

class StudentPersonalInfo(BaseModel):
    nombre: str
    edad: int = Field(..., ge=0)
    fecha_nacimiento: datetime
    año_inscripcion: int = Field(..., ge=1900)
    carrera: str
    semestre: int = Field(..., ge=1, le=10)
    medio_transporte: str
    situacion_familiar: str
    contacto: ContactInfo

class AcademicHistoryCreate(BaseModel):
    fecha: datetime
    evento: str
    detalles: str
    promedio: Optional[float] = None

class AcademicHistoryResponse(BaseModel):
    id: int
    estudiante_id: int
    fecha: datetime
    evento: str
    detalles: str
    promedio: Optional[float] = None

    class Config:
        orm_mode = True

class Student(BaseModel):
    id: int
    nombre: str
    programa: str
    semestre: int = Field(..., ge=1, le=10)
    departamento: Optional[str] = None
    riesgo_estres: float = Field(..., ge=0, le=100)
    riesgo_desercion: float = Field(..., ge=0, le=100)
    factores_estres: Optional[List[str]] = None

class StudentResponse(BaseModel):
    id: int
    nombre: str
    programa: str
    semestre: int
    departamento: Optional[str] = None
    riesgo_estres: float
    riesgo_desercion: float
    factores_estres: Optional[List[str]] = None

    class Config:
        orm_mode = True

class ContactInfo(BaseModel):
    email: EmailStr
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class StressPredictionResponse(BaseModel):
    id: int
    estudiante_id: int
    fecha_prediccion: datetime
    nivel_estres: float
    probabilidad_abandono: float
    factores_riesgo: List[str]

    class Config:
        orm_mode = True

class MessageResponse(BaseModel):
    id: int
    conversacion_id: int
    rol: MessageRole
    contenido: str
    fecha: datetime
    mensaje_metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class ConversationResponse(BaseModel):
    id: int
    estudiante_id: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    contexto: Optional[str] = None
    estado: str
    mensajes: List[MessageResponse] = []

    class Config:
        orm_mode = True

class PredictionRequest(BaseModel):
    estudiante_id: int
    institucion_id: int
    datos_academicos: dict
    datos_personales: StudentPersonalInfo
    historial_academico: List[AcademicHistory]

class PredictionResponse(BaseModel):
    prediccion: StressPredictionResponse
    probabilidades: List[float] 