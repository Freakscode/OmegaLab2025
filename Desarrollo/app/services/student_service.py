from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import Student, StudentResponse
from fastapi import HTTPException, status

class StudentService:
    def __init__(self, db: Session):
        self.db = db

    def create_student(self, student_data: dict) -> Student:
        """
        Crea un nuevo estudiante en la base de datos.
        """
        try:
            student = Student(**student_data)
            self.db.add(student)
            self.db.commit()
            self.db.refresh(student)
            return student
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear estudiante: {str(e)}"
            )

    def get_student(self, student_id: int) -> Optional[Student]:
        """
        Obtiene un estudiante por su ID.
        """
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante con ID {student_id} no encontrado"
            )
        return student

    def get_students(
        self,
        skip: int = 0,
        limit: int = 100,
        programa: Optional[str] = None,
        semestre: Optional[int] = None
    ) -> List[Student]:
        """
        Obtiene una lista de estudiantes con filtros opcionales.
        """
        query = self.db.query(Student)
        
        if programa:
            query = query.filter(Student.programa == programa)
        if semestre:
            query = query.filter(Student.semestre == semestre)
            
        return query.offset(skip).limit(limit).all()

    def update_student(self, student_id: int, student_data: dict) -> Student:
        """
        Actualiza los datos de un estudiante.
        """
        student = self.get_student(student_id)
        
        try:
            for key, value in student_data.items():
                setattr(student, key, value)
            
            self.db.commit()
            self.db.refresh(student)
            return student
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al actualizar estudiante: {str(e)}"
            )

    def delete_student(self, student_id: int) -> bool:
        """
        Elimina un estudiante de la base de datos.
        """
        student = self.get_student(student_id)
        
        try:
            self.db.delete(student)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al eliminar estudiante: {str(e)}"
            ) 