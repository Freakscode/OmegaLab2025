# Contenido inicial para app/services/prediction.py
import joblib
import pandas as pd
from pathlib import Path
from typing import List
import tensorflow as tf

# Variables globales para almacenar los artefactos cargados (RF04)
# Idealmente, la carga se gestiona en el lifespan de FastAPI (main.py)
# Aquí solo definimos las variables para que estén disponibles.
preprocessor = None
model = None

# Define la ruta base relativa al archivo actual
BASE_DIR = Path(__file__).resolve().parent.parent.parent # Sube tres niveles: services -> app -> raíz
ARTIFACTS_DIR = BASE_DIR / "artifacts"
PREPROCESSOR_PATH = ARTIFACTS_DIR / "preprocessor_final.joblib"
MODEL_PATH = ARTIFACTS_DIR / "model_final_pred.keras"

def load_artifacts():
    """Carga el preprocesador y el modelo desde los archivos."""
    global preprocessor, model
    try:
        print(f"Cargando preprocesador desde: {PREPROCESSOR_PATH}")
        preprocessor = joblib.load(PREPROCESSOR_PATH)
        print("Preprocesador cargado.")

        print(f"Cargando modelo desde: {MODEL_PATH}")
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Modelo cargado.")

    except FileNotFoundError as e:
        print(f"Error: Archivo de artefacto no encontrado - {e}")
        raise
    except Exception as e:
        print(f"Error inesperado al cargar artefactos: {e}")
        raise

def make_prediction(input_data: pd.DataFrame) -> List[float]:
    """
    Realiza el preprocesamiento y la predicción para los datos de entrada.
    (RF05, RF06)
    """
    global preprocessor, model

    if preprocessor is None or model is None:
        # Esto no debería ocurrir si el lifespan funciona correctamente,
        # pero es una salvaguarda.
        print("Error: Los artefactos de ML no están cargados.")
        # Considera reintentar la carga o lanzar un error HTTP 503 Service Unavailable
        raise RuntimeError("Los artefactos de Machine Learning no se han cargado correctamente.")

    # Asegúrate de que las columnas estén en el orden correcto si es necesario
    # (depende de cómo se entrenó el preprocesador)
    # expected_cols = [...] # Obtener de alguna forma
    # input_data = input_data[expected_cols]

    try:
        # 1. Aplicar preprocesamiento (RF05)
        print("Aplicando preprocesamiento...")
        processed_data = preprocessor.transform(input_data)
        print("Preprocesamiento completado.")

        # 2. Generar predicción de probabilidad (RF06)
        # Asumimos que el modelo tiene un método predict_proba
        # y que la clase positiva ('1' - estrés) es la segunda columna (índice 1)
        print("Generando predicciones...")
        probabilities = model.predict_proba(processed_data)[:, 1]
        print("Predicciones generadas.")

        # Convertir a lista de floats estándar de Python para la respuesta JSON
        return probabilities.tolist()

    except Exception as e:
        # Captura errores durante la transformación o predicción (RF08)
        print(f"Error durante el preprocesamiento o predicción: {e}")
        # Relanza la excepción para que el endpoint la capture y devuelva un 500
        raise 