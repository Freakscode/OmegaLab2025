from fastapi import APIRouter, HTTPException, status
from app.api.models import PredictionRequest, PredictionResponse
# Importaremos el servicio de predicción más adelante
from app.services.prediction import make_prediction
import pandas as pd

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_stress(request: PredictionRequest):
    """
    Recibe datos de estudiantes, realiza el preprocesamiento y la predicción,
    y devuelve la probabilidad de estrés académico para cada estudiante.

    - **request**: Cuerpo de la solicitud con la lista de estudiantes (PredictionRequest).
    - **returns**: Respuesta con la lista de probabilidades (PredictionResponse).
    """
    try:
        # Convertir los datos de entrada Pydantic a un DataFrame de Pandas
        # que es el formato esperado por muchos pipelines de scikit-learn.
        input_data = pd.DataFrame([student.model_dump() for student in request.students])

        # Llamar al servicio de predicción (RF05, RF06)
        # Esta función contendrá la lógica de preprocesamiento y predicción.
        probabilities = make_prediction(input_data)

        # Formatear la respuesta (RF07)
        return PredictionResponse(probabilities=probabilities)

    except ValueError as ve:
        # Captura errores específicos que podrían surgir en la conversión o preprocesamiento
        # Aquí podrías añadir logging más detallado
        print(f"Error de validación o preprocesamiento: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en los datos de entrada: {ve}"
        )
    except Exception as e:
        # Manejo genérico de errores de inferencia (RF08)
        # Aquí deberías loggear el error completo para depuración
        print(f"Error inesperado durante la predicción: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno al procesar la solicitud."
        )

# Nota: Necesitaremos implementar la función make_prediction en app/services/prediction.py 