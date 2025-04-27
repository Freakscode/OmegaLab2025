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
    AcademicHistory,
    Institution
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

    def _obtener_configuracion_institucion(self, institucion_id: int) -> dict:
        """Obtiene la configuración específica de la institución."""
        institucion = self.db.query(Institution).filter(Institution.id == institucion_id).first()
        if not institucion or not institucion.configuracion:
            return {}
        return institucion.configuracion

    async def predecir_estres(
        self,
        estudiante_id: int,
        datos_academicos: dict,
        datos_personales: StudentPersonalInfo,
        historial_academico: List[AcademicHistory],
        institucion_id: int
    ) -> PredictionResponse:
        """
        Realiza la predicción de estrés académico para un estudiante usando el modelo Keras.
        """
        try:
            # Preparar los datos para el modelo
            features = self._preparar_features(datos_academicos, datos_personales, historial_academico, institucion_id)
            
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
                historial_academico,
                institucion_id
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
        historial_academico: List[AcademicHistory],
        institucion_id: int
    ) -> np.ndarray:
        """
        Prepara las características para el modelo a partir de los datos del estudiante.
        Las características deben coincidir exactamente con las usadas en el entrenamiento.
        """
        config = self._obtener_configuracion_institucion(institucion_id)
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

        # Aplicar factores de escala específicos de la institución si existen
        if "factores_escala" in config:
            for i, factor in enumerate(config["factores_escala"]):
                if i < len(features):
                    features[i] *= factor

        return np.array(features)

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
        historial_academico: List[AcademicHistory],
        institucion_id: int
    ) -> List[str]:
        """
        Analiza los factores de riesgo basados en los datos del estudiante
        y las configuraciones específicas de la institución.
        """
        config = self._obtener_configuracion_institucion(institucion_id)
        factores = []
        
        # Umbrales personalizados de la institución
        umbral_carga = config.get("umbral_carga_academica", 18)
        umbral_reprobacion = config.get("umbral_reprobacion", 2)
        
        # Análisis de carga académica
        if datos_academicos.get("creditos_actuales", 0) > umbral_carga:
            factores.append("Alta carga académica")
            
        # Análisis de rendimiento histórico
        if historial_academico:
            materias_reprobadas = sum(1 for h in historial_academico if h.promedio < 6.0)
            if materias_reprobadas > umbral_reprobacion:
                factores.append("Historial de reprobación")
                
        # Análisis de situación personal
        if datos_personales.situacion_familiar == "separados":
            factores.append("Situación familiar compleja")

        # Factores específicos de la institución
        if "factores_adicionales" in config:
            for factor in config["factores_adicionales"]:
                if self._evaluar_factor_adicional(factor, datos_academicos, datos_personales, historial_academico):
                    factores.append(factor["nombre"])

        return factores

    def _evaluar_factor_adicional(
        self,
        factor: dict,
        datos_academicos: dict,
        datos_personales: StudentPersonalInfo,
        historial_academico: List[AcademicHistory]
    ) -> bool:
        """Evalúa un factor adicional definido por la institución."""
        if factor["tipo"] == "academico":
            valor = datos_academicos.get(factor["campo"], 0)
        elif factor["tipo"] == "personal":
            valor = getattr(datos_personales, factor["campo"], None)
        else:
            return False

        if factor["operador"] == ">":
            return valor > factor["valor"]
        elif factor["operador"] == "<":
            return valor < factor["valor"]
        elif factor["operador"] == "==":
            return valor == factor["valor"]
        return False 