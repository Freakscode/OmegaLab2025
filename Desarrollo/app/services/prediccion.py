from typing import List, Optional
import numpy as np
from datetime import datetime
import tensorflow as tf
import joblib
import os
from ..models import (
    Student,
    StressPrediction,
    PredictionRequest,
    PredictionResponse,
    StudentPersonalInfo,
    AcademicHistory
)
from ..database import get_db
from sqlalchemy.orm import Session

class PrediccionService:
    def __init__(self, db: Session):
        self.db = db
        self.model = None
        self.preprocessor = None
        self._load_model()

    def _load_model(self):
        """
        Carga el modelo Keras y el preprocesador desde los archivos guardados.
        """
        try:
            model_path = os.path.join("artifacts", "model_final_pred.keras")
            preprocessor_path = os.path.join("artifacts", "preprocessor_final.joblib")
            
            if os.path.exists(model_path) and os.path.exists(preprocessor_path):
                self.model = tf.keras.models.load_model(model_path)
                self.preprocessor = joblib.load(preprocessor_path)
            else:
                raise FileNotFoundError("No se encontraron los archivos del modelo o preprocesador")
        except Exception as e:
            print(f"Error al cargar el modelo: {str(e)}")
            raise

    async def predecir_estres(
        self,
        estudiante_id: int,
        datos_academicos: dict,
        datos_personales: StudentPersonalInfo,
        historial_academico: List[AcademicHistory]
    ) -> PredictionResponse:
        """
        Realiza la predicción de estrés académico para un estudiante usando el modelo Keras.
        """
        try:
            # Preparar los datos para el modelo
            features = self._preparar_features(datos_academicos, datos_personales, historial_academico)
            
            # Preprocesar los datos
            features_procesadas = self.preprocessor.transform(features)
            
            # Realizar la predicción
            prediccion = self.model.predict(features_procesadas)
            
            # Calcular probabilidades
            probabilidad_estres = float(prediccion[0][0])
            probabilidad_abandono = float(prediccion[0][1])
            
            # Analizar factores de riesgo
            factores_riesgo = self._analizar_factores_riesgo(
                datos_academicos,
                datos_personales,
                historial_academico
            )
            
            # Crear objeto de predicción
            prediccion_obj = StressPrediction(
                estudiante_id=estudiante_id,
                fecha_prediccion=datetime.now(),
                nivel_estres=probabilidad_estres,
                probabilidad_abandono=probabilidad_abandono,
                factores_riesgo=factores_riesgo
            )
            
            # Guardar la predicción en la base de datos
            self.db.add(prediccion_obj)
            self.db.commit()
            
            return PredictionResponse(
                prediccion=prediccion_obj,
                probabilidades=[probabilidad_estres, probabilidad_abandono]
            )
            
        except Exception as e:
            print(f"Error en la predicción: {str(e)}")
            raise

    def _preparar_features(
        self,
        datos_academicos: dict,
        datos_personales: StudentPersonalInfo,
        historial_academico: List[AcademicHistory]
    ) -> np.ndarray:
        """
        Prepara las características para el modelo a partir de los datos del estudiante.
        Las características deben coincidir exactamente con las usadas en el entrenamiento.
        """
        features = []
        
        # Características académicas
        features.extend([
            float(datos_academicos.get("creditos_actuales", 0)),  # Carga académica actual
            float(datos_academicos.get("promedio_actual", 0)),    # Promedio actual
            float(datos_academicos.get("materias_reprobadas", 0)), # Materias reprobadas
            float(datos_academicos.get("materias_retiradas", 0)),  # Materias retiradas
            float(datos_academicos.get("asistencia_promedio", 0)), # Asistencia promedio
            float(datos_academicos.get("horas_estudio_semanal", 0)) # Horas de estudio semanal
        ])
        
        # Características personales
        features.extend([
            float(datos_personales.edad),  # Edad
            1.0 if datos_personales.situacion_familiar == "separados" else 0.0,  # Situación familiar
            1.0 if datos_personales.medio_transporte == "publico" else 0.0,  # Medio de transporte
            float(datos_personales.año_inscripcion)  # Año de inscripción
        ])
        
        # Características del historial académico
        if historial_academico:
            # Calcular estadísticas del historial
            promedios = [h.promedio for h in historial_academico if h.promedio is not None]
            eventos_negativos = sum(1 for h in historial_academico if "reprobado" in h.evento.lower())
            eventos_positivos = sum(1 for h in historial_academico if "aprobado" in h.evento.lower())
            
            features.extend([
                float(np.mean(promedios)) if promedios else 0.0,  # Promedio histórico
                float(np.std(promedios)) if promedios else 0.0,   # Desviación estándar del promedio
                float(eventos_negativos),  # Eventos negativos
                float(eventos_positivos)   # Eventos positivos
            ])
        else:
            features.extend([0.0, 0.0, 0.0, 0.0])  # Valores por defecto si no hay historial
        
        # Convertir a array numpy y asegurar el formato correcto
        features_array = np.array(features, dtype=np.float32)
        
        # Verificar que no haya valores NaN o infinitos
        if np.any(np.isnan(features_array)) or np.any(np.isinf(features_array)):
            raise ValueError("Se detectaron valores NaN o infinitos en las características")
        
        # Reshape para el formato esperado por el modelo (1, n_features)
        return features_array.reshape(1, -1)

    async def obtener_estudiantes_con_prediccion(self) -> List[Student]:
        """
        Obtiene la lista de estudiantes con sus predicciones más recientes.
        """
        # TODO: Implementar la consulta real a la base de datos
        return []

    async def obtener_historial_academico(self, estudiante_id: int) -> List[AcademicHistory]:
        """
        Obtiene el historial académico de un estudiante.
        """
        # TODO: Implementar la consulta real a la base de datos
        return []

    def _analizar_factores_riesgo(
        self,
        datos_academicos: dict,
        datos_personales: StudentPersonalInfo,
        historial_academico: List[AcademicHistory]
    ) -> List[str]:
        """
        Analiza los factores de riesgo basados en los datos del estudiante.
        """
        factores = []
        
        # Análisis de carga académica
        if datos_academicos.get("creditos_actuales", 0) > 18:
            factores.append("Alta carga académica")
            
        # Análisis de rendimiento histórico
        if historial_academico:
            materias_reprobadas = sum(1 for h in historial_academico if h.promedio < 6.0)
            if materias_reprobadas > 2:
                factores.append("Historial de reprobación")
                
        # Análisis de situación personal
        if datos_personales.situacion_familiar == "separados":
            factores.append("Situación familiar compleja")
            
        return factores 