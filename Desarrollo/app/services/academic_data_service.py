import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Student, AcademicHistory, StressPrediction
from app.services.prediccion import PrediccionService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AcademicDataService:
    """
    Servicio para manejar la ingesta y actualización de datos académicos.
    """
    def __init__(self, db: Session):
        """
        Inicializa el servicio de datos académicos.
        
        Args:
            db: Sesión de base de datos
        """
        self.db = db
        self.prediccion_service = PrediccionService(db)
        
    def registrar_evento_academico(
        self,
        estudiante_id: int,
        evento: str,
        detalles: str,
        promedio: Optional[float] = None
    ) -> bool:
        """
        Registra un evento académico para un estudiante.
        
        Args:
            estudiante_id: ID del estudiante
            evento: Tipo de evento (ej. 'CALIFICACION_FINAL', 'RETIRO_CURSO')
            detalles: Detalles del evento
            promedio: Promedio actual del estudiante (opcional)
            
        Returns:
            bool: True si el evento se registró correctamente, False en caso contrario
        """
        try:
            # Verificar que el estudiante existe
            estudiante = self.db.query(Student).filter(Student.id == estudiante_id).first()
            if not estudiante:
                logger.error(f"No se encontró el estudiante con ID {estudiante_id}")
                return False
                
            # Crear nuevo registro de historial académico
            historial = AcademicHistory(
                estudiante_id=estudiante_id,
                fecha=datetime.now(),
                evento=evento,
                detalles=detalles,
                promedio=promedio
            )
            
            self.db.add(historial)
            self.db.commit()
            
            # Actualizar predicción de estrés
            self._actualizar_prediccion_estres(estudiante_id)
            
            logger.info(f"Evento académico registrado para estudiante {estudiante_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al registrar evento académico: {str(e)}")
            self.db.rollback()
            return False
            
    def actualizar_datos_lms(
        self,
        estudiante_id: int,
        horas_actividad_semanal: float
    ) -> bool:
        """
        Actualiza los datos de actividad en el LMS.
        
        Args:
            estudiante_id: ID del estudiante
            horas_actividad_semanal: Horas promedio de actividad semanal en el LMS
            
        Returns:
            bool: True si los datos se actualizaron correctamente, False en caso contrario
        """
        try:
            # Verificar que el estudiante existe
            estudiante = self.db.query(Student).filter(Student.id == estudiante_id).first()
            if not estudiante:
                logger.error(f"No se encontró el estudiante con ID {estudiante_id}")
                return False
                
            # Actualizar datos en la tabla Student o en una tabla específica para datos LMS
            # Aquí asumimos que hay un campo en Student para esto
            estudiante.lms_activity_weekly_hours_avg_last_month = horas_actividad_semanal
            
            self.db.commit()
            
            # Actualizar predicción de estrés
            self._actualizar_prediccion_estres(estudiante_id)
            
            logger.info(f"Datos LMS actualizados para estudiante {estudiante_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al actualizar datos LMS: {str(e)}")
            self.db.rollback()
            return False
            
    def actualizar_uso_servicios_apoyo(
        self,
        estudiante_id: int,
        servicios_utilizados: List[str]
    ) -> bool:
        """
        Actualiza los datos de uso de servicios de apoyo.
        
        Args:
            estudiante_id: ID del estudiante
            servicios_utilizados: Lista de servicios utilizados en el último mes
            
        Returns:
            bool: True si los datos se actualizaron correctamente, False en caso contrario
        """
        try:
            # Verificar que el estudiante existe
            estudiante = self.db.query(Student).filter(Student.id == estudiante_id).first()
            if not estudiante:
                logger.error(f"No se encontró el estudiante con ID {estudiante_id}")
                return False
                
            # Actualizar datos en la tabla Student o en una tabla específica para servicios
            # Aquí asumimos que hay un campo en Student para esto
            estudiante.support_service_use_last_month = servicios_utilizados
            
            self.db.commit()
            
            # Actualizar predicción de estrés
            self._actualizar_prediccion_estres(estudiante_id)
            
            logger.info(f"Datos de servicios de apoyo actualizados para estudiante {estudiante_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al actualizar datos de servicios: {str(e)}")
            self.db.rollback()
            return False
            
    def _actualizar_prediccion_estres(self, estudiante_id: int) -> None:
        """
        Actualiza la predicción de estrés para un estudiante.
        
        Args:
            estudiante_id: ID del estudiante
        """
        try:
            # Obtener datos actualizados del estudiante
            estudiante = self.db.query(Student).filter(Student.id == estudiante_id).first()
            if not estudiante:
                return
                
            # Obtener historial académico reciente
            historial = self.db.query(AcademicHistory).filter(
                AcademicHistory.estudiante_id == estudiante_id
            ).order_by(AcademicHistory.fecha.desc()).limit(10).all()
            
            # Preparar datos para la predicción
            datos_prediccion = {
                "estudiante_id": estudiante_id,
                "institucion_id": estudiante.institucion_id,
                "datos_academicos": {
                    "programa": estudiante.programa,
                    "semestre": estudiante.semestre,
                    "promedio_actual": estudiante.promedio if hasattr(estudiante, 'promedio') else None,
                    "lms_activity": estudiante.lms_activity_weekly_hours_avg_last_month if hasattr(estudiante, 'lms_activity_weekly_hours_avg_last_month') else None,
                    "support_services": estudiante.support_service_use_last_month if hasattr(estudiante, 'support_service_use_last_month') else []
                },
                "historial_academico": [
                    {
                        "fecha": h.fecha.isoformat(),
                        "evento": h.evento,
                        "detalles": h.detalles,
                        "promedio": h.promedio
                    }
                    for h in historial
                ]
            }
            
            # Realizar predicción
            prediccion = self.prediccion_service.predict_stress(datos_prediccion)
            
            if prediccion:
                # Actualizar predicción en la base de datos
                nueva_prediccion = StressPrediction(
                    estudiante_id=estudiante_id,
                    fecha_prediccion=datetime.now(),
                    nivel_estres=prediccion.nivel_estres,
                    probabilidad_abandono=prediccion.probabilidad_abandono,
                    factores_riesgo=prediccion.factores_riesgo
                )
                
                self.db.add(nueva_prediccion)
                
                # Actualizar riesgo en el estudiante
                estudiante.riesgo_estres = prediccion.nivel_estres
                estudiante.riesgo_desercion = prediccion.probabilidad_abandono
                estudiante.factores_estres = prediccion.factores_riesgo
                
                self.db.commit()
                
                logger.info(f"Predicción de estrés actualizada para estudiante {estudiante_id}")
                
        except Exception as e:
            logger.error(f"Error al actualizar predicción de estrés: {str(e)}")
            self.db.rollback() 