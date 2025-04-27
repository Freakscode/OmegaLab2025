from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database import get_db
from ...services.student_service import StudentService
from ..models import Student, StudentResponse

router = APIRouter(
    prefix="/students",
    tags=["students"]
)

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: Student, db: Session = Depends(get_db)):
    """
    Crea un nuevo estudiante.
    """
    student_service = StudentService(db)
    return student_service.create_student(student.model_dump())

@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un estudiante por su ID.
    """
    student_service = StudentService(db)
    return student_service.get_student(student_id)

@router.get("/", response_model=List[StudentResponse])
def get_students(
    skip: int = 0,
    limit: int = 100,
    programa: Optional[str] = None,
    semestre: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de estudiantes con filtros opcionales.
    """
    student_service = StudentService(db)
    return student_service.get_students(skip, limit, programa, semestre)

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: Student,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un estudiante.
    """
    student_service = StudentService(db)
    return student_service.update_student(student_id, student.model_dump())

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    Elimina un estudiante.
    """
    student_service = StudentService(db)
    student_service.delete_student(student_id)
    return None 