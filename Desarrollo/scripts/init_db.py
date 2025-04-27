import os
import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from app.database import engine, Base
from app.models import Student, Conversation, Message, StressPrediction, AcademicHistory

def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    """
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("¡Tablas creadas exitosamente!")

if __name__ == "__main__":
    init_db() 