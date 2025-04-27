from pydantic import BaseModel, Field, conlist, EmailStr
from typing import List, Union, Literal, Optional
from datetime import date

# Modelo para los datos de entrada de un estudiante (RF02)
class StudentDataInput(BaseModel):
    gender: Literal['Male', 'Female'] = Field(..., description="Género del estudiante")
    year_of_study: int = Field(..., ge=1, description="Año de estudio")
    program_major: str = Field(..., description="Programa/Carrera principal")
    credit_load: int = Field(..., ge=0, description="Carga de créditos actual")
    gpa_previous_semester: float = Field(..., ge=0.0, le=4.0, description="Promedio GPA semestre anterior (escala 0-4)")
    gpa_current_semester: float = Field(..., ge=0.0, le=4.0, description="Promedio GPA semestre actual (escala 0-4)")
    number_of_failed_courses_current_semester: int = Field(..., ge=0, description="Número de cursos reprobados semestre actual")
    number_of_course_withdrawals_current_semester: int = Field(..., ge=0, description="Número de cursos retirados semestre actual")
    entrance_exam_score_percentile: float = Field(..., ge=0.0, le=100.0, description="Percentil examen de ingreso")
    lms_activity_weekly_hours_avg_last_month: float = Field(..., ge=0.0, description="Promedio horas semanales actividad LMS último mes")
    support_service_use_last_month: int = Field(..., ge=0, description="Número de veces que usó servicios de apoyo el último mes")
    edad: int = Field(..., ge=15, le=100, description="Edad del estudiante")

    class Config:
        # Ejemplo para la documentación de OpenAPI / Swagger
        json_schema_extra = {
            "example": {
                "gender": "Female",
                "year_of_study": 2,
                "program_major": "Computer Science",
                "credit_load": 15,
                "gpa_previous_semester": 3.5,
                "gpa_current_semester": 3.2,
                "number_of_failed_courses_current_semester": 0,
                "number_of_course_withdrawals_current_semester": 1,
                "entrance_exam_score_percentile": 85.5,
                "lms_activity_weekly_hours_avg_last_month": 10.2,
                "support_service_use_last_month": 1,
                "edad": 20
            }
        }

# Modelo para la solicitud completa, que es una lista de estudiantes (RF02)
# Usamos conlist para asegurar que la lista no esté vacía
class PredictionRequest(BaseModel):
    students: conlist(StudentDataInput, min_length=1)

# Modelo para la respuesta de predicción (RF07)
class PredictionResponse(BaseModel):
    probabilities: List[float] = Field(..., description="Lista de probabilidades de estrés académico (clase '1')")

class ContactInfo(BaseModel):
    email: EmailStr
    telefono: str
    direccion: str

class StudentPersonalInfo(BaseModel):
    nombre: str
    edad: int = Field(..., ge=0)
    fecha_nacimiento: date
    año_inscripcion: int = Field(..., ge=1900)
    carrera: str
    semestre: int = Field(..., ge=1, le=10)
    medio_transporte: str
    contacto: ContactInfo

class AcademicHistory(BaseModel):
    fecha: str
    evento: str
    detalles: str

class Student(BaseModel):
    id: int
    nombre: str
    programa: str
    semestre: int = Field(..., ge=1, le=10)
    departamento: Optional[str] = None
    riesgo_estres: float = Field(..., ge=0, le=100)
    riesgo_desercion: float = Field(..., ge=0, le=100)
    factores_estres: Optional[List[str]] = None

class StressPrediction(BaseModel):
    riesgo_estres: float = Field(..., ge=0, le=100)
    riesgo_desercion: float = Field(..., ge=0, le=100)
    factores_estres: List[str]

class PredictionRequest(BaseModel):
    estudiante_id: int
    datos_academicos: dict
    datos_personales: dict
    historial_academico: List[AcademicHistory]

class PredictionResponse(BaseModel):
    prediccion: StressPrediction
    mensaje: str
    recomendaciones: List[str] 