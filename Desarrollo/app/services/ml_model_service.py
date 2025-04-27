import os
import logging
from pathlib import Path
import joblib
import tensorflow as tf
from typing import Dict, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModelService:
    """
    Servicio para cargar y gestionar modelos de ML.
    """
    def __init__(self, models_dir: str = "artifacts"):
        """
        Inicializa el servicio de modelos ML.
        
        Args:
            models_dir: Directorio donde se almacenan los artefactos de ML
        """
        self.models_dir = Path(models_dir)
        self.preprocessor = None
        self.model = None
        self.is_loaded = False
        
    def load_models(self) -> bool:
        """
        Carga los modelos de ML desde el almacenamiento.
        
        Returns:
            bool: True si los modelos se cargaron correctamente, False en caso contrario
        """
        try:
            # Verificar que el directorio existe
            if not self.models_dir.exists():
                logger.error(f"El directorio de modelos {self.models_dir} no existe")
                return False
                
            # Cargar el preprocesador
            preprocessor_path = self.models_dir / "preprocessor_final.joblib"
            if not preprocessor_path.exists():
                logger.error(f"No se encontró el preprocesador en {preprocessor_path}")
                return False
                
            self.preprocessor = joblib.load(preprocessor_path)
            logger.info("Preprocesador cargado correctamente")
            
            # Cargar el modelo Keras
            model_path = self.models_dir / "model_final_pred.keras"
            if not model_path.exists():
                logger.error(f"No se encontró el modelo en {model_path}")
                return False
                
            self.model = tf.keras.models.load_model(str(model_path))
            logger.info("Modelo Keras cargado correctamente")
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar los modelos: {str(e)}")
            return False
            
    def predict(self, features: Dict[str, Any]) -> Optional[float]:
        """
        Realiza una predicción usando los modelos cargados.
        
        Args:
            features: Diccionario con las características para la predicción
            
        Returns:
            float: Probabilidad de estrés predicha, o None si hay error
        """
        if not self.is_loaded:
            logger.error("Los modelos no están cargados")
            return None
            
        try:
            # Preprocesar las características
            processed_features = self.preprocessor.transform([features])
            
            # Realizar la predicción
            prediction = self.model.predict(processed_features)[0][0]
            
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Error al realizar la predicción: {str(e)}")
            return None
            
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Obtiene la importancia de las características del modelo.
        
        Returns:
            Dict[str, float]: Diccionario con la importancia de cada característica
        """
        if not self.is_loaded:
            logger.error("Los modelos no están cargados")
            return {}
            
        try:
            # Obtener nombres de características del preprocesador
            feature_names = self.preprocessor.get_feature_names_out()
            
            # Obtener importancia de características del modelo
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
            else:
                # Para modelos que no tienen feature_importances_ directamente
                # Podríamos implementar SHAP o LIME aquí
                return {}
                
            # Crear diccionario de importancia
            importance_dict = {
                name: float(importance)
                for name, importance in zip(feature_names, importances)
            }
            
            return importance_dict
            
        except Exception as e:
            logger.error(f"Error al obtener importancia de características: {str(e)}")
            return {} 