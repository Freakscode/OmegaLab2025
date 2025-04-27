import os
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from app.database import SessionLocal
from app.services.student_service import StudentService

def test_crud_operations():
    """
    Prueba las operaciones CRUD para estudiantes.
    """
    db = SessionLocal()
    student_service = StudentService(db)

    try:
        # CREATE
        print("\n1. Creando un nuevo estudiante...")
        new_student = {
            "nombre": "Juan Pérez",
            "programa": "Ingeniería en Sistemas",
            "semestre": 5,
            "departamento": "Ciencias de la Computación",
            "riesgo_estres": 0.0,
            "riesgo_desercion": 0.0,
            "factores_estres": []
        }
        created_student = student_service.create_student(new_student)
        print(f"Estudiante creado con ID: {created_student.id}")

        # READ
        print("\n2. Obteniendo el estudiante creado...")
        retrieved_student = student_service.get_student(created_student.id)
        print(f"Estudiante recuperado: {retrieved_student.nombre}")

        # UPDATE
        print("\n3. Actualizando el estudiante...")
        update_data = {
            "riesgo_estres": 75.5,
            "factores_estres": ["Alta carga académica", "Bajo rendimiento"]
        }
        updated_student = student_service.update_student(created_student.id, update_data)
        print(f"Estudiante actualizado. Nuevo riesgo de estrés: {updated_student.riesgo_estres}")

        # LIST
        print("\n4. Obteniendo lista de estudiantes...")
        students = student_service.get_students()
        print(f"Total de estudiantes: {len(students)}")

        # DELETE
        print("\n5. Eliminando el estudiante...")
        student_service.delete_student(created_student.id)
        print("Estudiante eliminado")

        print("\n¡Todas las operaciones CRUD completadas exitosamente!")

    except Exception as e:
        print(f"\nError durante las pruebas: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_crud_operations() 