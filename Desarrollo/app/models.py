from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Enum
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

# Modelos de Base de Datos
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    programa = Column(String(100), nullable=False)
    semestre = Column(Integer, nullable=False)
    departamento = Column(String(100))
    riesgo_estres = Column(Float, default=0.0)
    riesgo_desercion = Column(Float, default=0.0)
    factores_estres = Column(JSON)
    
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
class ContactInfo(BaseModel):
    email: EmailStr
    telefono: str
    direccion: str

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

class StudentCreate(BaseModel):
    nombre: str
    programa: str
    semestre: int = Field(..., ge=1, le=10)
    departamento: Optional[str] = None

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

class StressPredictionCreate(BaseModel):
    estudiante_id: int
    nivel_estres: float = Field(..., ge=0, le=1)
    probabilidad_abandono: float = Field(..., ge=0, le=1)
    factores_riesgo: List[str]

class StressPredictionResponse(BaseModel):
    id: int
    estudiante_id: int
    fecha_prediccion: datetime
    nivel_estres: float
    probabilidad_abandono: float
    factores_riesgo: List[str]

    class Config:
        orm_mode = True

class PredictionRequest(BaseModel):
    estudiante_id: int
    datos_academicos: Dict[str, Any]
    datos_personales: StudentPersonalInfo
    historial_academico: List[AcademicHistoryCreate]

class PredictionResponse(BaseModel):
    prediccion: StressPredictionResponse
    probabilidades: List[float]

class MessageCreate(BaseModel):
    rol: MessageRole
    contenido: str
    mensaje_metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    id: int
    conversacion_id: int
    rol: MessageRole
    contenido: str
    fecha: datetime
    mensaje_metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class ConversationCreate(BaseModel):
    estudiante_id: int
    contexto: Optional[str] = None

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

class ConversationUpdate(BaseModel):
    estado: Optional[str] = None
    contexto: Optional[str] = None
    fecha_fin: Optional[datetime] = None 