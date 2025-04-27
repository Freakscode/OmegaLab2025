import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuración de directorios de logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configuración de formato de logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Niveles de log
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Configuración de rotación de logs
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configura un logger con manejo de archivos y consola.
    
    Args:
        name: Nombre del logger
        log_file: Nombre del archivo de log (opcional)
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Formato para los handlers
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / log_file,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

# Loggers específicos
api_logger = setup_logger("api", "api.log")
auth_logger = setup_logger("auth", "auth.log")
db_logger = setup_logger("database", "database.log")
ml_logger = setup_logger("ml", "ml.log")
academic_logger = setup_logger("academic", "academic.log")

class RequestLogger:
    """
    Middleware para logging de requests.
    """
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        # Obtener información de la request
        method = scope.get("method", "")
        path = scope.get("path", "")
        client = scope.get("client", ("", 0))
        
        # Registrar inicio de la request
        api_logger.info(f"Request iniciada: {method} {path} desde {client[0]}:{client[1]}")
        
        # Función para enviar la respuesta
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                api_logger.info(f"Response enviada: {method} {path} - Status: {status_code}")
            await send(message)
            
        # Procesar la request
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            api_logger.error(f"Error en request: {method} {path} - {str(e)}")
            raise

class DatabaseLogger:
    """
    Middleware para logging de operaciones de base de datos.
    """
    def __init__(self, session):
        self.session = session
        
    def __enter__(self):
        return self.session
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            db_logger.error(f"Error en operación de base de datos: {str(exc_val)}")
            self.session.rollback()
        else:
            try:
                self.session.commit()
                db_logger.info("Operación de base de datos completada exitosamente")
            except Exception as e:
                db_logger.error(f"Error al commit: {str(e)}")
                self.session.rollback()

def log_academic_event(event_type: str, details: str, student_id: Optional[int] = None):
    """
    Registra un evento académico.
    
    Args:
        event_type: Tipo de evento
        details: Detalles del evento
        student_id: ID del estudiante (opcional)
    """
    student_info = f" - Estudiante ID: {student_id}" if student_id else ""
    academic_logger.info(f"Evento académico: {event_type}{student_info} - {details}")

def log_ml_prediction(student_id: int, prediction: float, features: dict):
    """
    Registra una predicción de ML.
    
    Args:
        student_id: ID del estudiante
        prediction: Valor de la predicción
        features: Características utilizadas
    """
    ml_logger.info(
        f"Predicción ML - Estudiante ID: {student_id} - "
        f"Predicción: {prediction:.4f} - Features: {features}"
    )

def log_auth_event(event_type: str, user_id: Optional[int] = None, details: str = ""):
    """
    Registra un evento de autenticación.
    
    Args:
        event_type: Tipo de evento
        user_id: ID del usuario (opcional)
        details: Detalles adicionales (opcional)
    """
    user_info = f" - Usuario ID: {user_id}" if user_id else ""
    auth_logger.info(f"Evento de autenticación: {event_type}{user_info} - {details}") 