# Contenido inicial para tests/step_defs/test_predict_endpoint.py

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
import json

# Importa la app FastAPI principal
# Necesitamos ajustar la ruta si es necesario dependiendo de cómo corras pytest
try:
    from app.main import app
except ImportError:
    # Si corres pytest desde la raíz, la importación anterior funciona.
    # Si corres desde /tests, podrías necesitar ajustar sys.path, pero es mejor correr desde la raíz.
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from app.main import app

# Importa los modelos para posible referencia
from app.api.models import PredictionRequest, PredictionResponse

# Carga los escenarios definidos en el archivo .feature
scenarios('../features/predict.feature')

# --- Fixtures --- #

@pytest.fixture
def api_client():
    """Fixture para crear un cliente de prueba para la API."""
    # Usamos TestClient que interactúa con la app FastAPI directamente
    client = TestClient(app)
    return client

@pytest.fixture
def context():
    """Fixture para almacenar datos entre pasos (contexto del escenario)."""
    return {}

# --- Given Steps --- #

@given("la API está funcionando")
def api_is_running(api_client):
    """Verifica que la API responde al endpoint de health check."""
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    # Este paso asume que la API ya está iniciada por TestClient

@given("los artefactos de ML (preprocesador y modelo) están cargados correctamente")
def ml_artifacts_are_loaded():
    """
    Este es un paso complicado de verificar directamente en un test de integración.
    Asumimos que el lifespan de FastAPI los cargó correctamente al iniciar TestClient.
    Si la carga fallara y detuviera la app, el TestClient fallaría al iniciarse.
    Si la carga fallara pero la app continuara, necesitaríamos una forma de verificar
    el estado interno (ej. un endpoint de estado de artefactos o chequeando logs).
    Por ahora, lo dejamos como una asunción basada en el flujo normal.
    En tests unitarios del servicio de predicción, sí probaríamos la carga explícitamente.
    """
    # TODO: Considerar añadir un mecanismo para verificar esto si es crítico.
    print("\nAsumiendo que los artefactos ML se cargaron durante el inicio de la app (lifespan).")
    pass

# --- When Steps --- #

@when(parsers.parse('envío una solicitud POST a "{endpoint}" con los siguientes datos de estudiante:\n{payload}'), target_fixture="response")
def send_post_request_with_data(api_client, context, endpoint: str, payload: str):
    """Envía una solicitud POST al endpoint especificado con el payload JSON."""
    try:
        data = json.loads(payload)
        response = api_client.post(endpoint, json=data)
        context['response'] = response
        return response # Devolver para target_fixture
    except json.JSONDecodeError:
        pytest.fail(f"El payload proporcionado no es un JSON válido: {payload}")
    except Exception as e:
        pytest.fail(f"Error al enviar la solicitud POST: {e}")

@when(parsers.parse('envío una solicitud POST a "{endpoint}" con datos de estudiante inválidos:\n{payload}'), target_fixture="response")
def send_post_request_with_invalid_data(api_client, context, endpoint: str, payload: str):
    """Envía una solicitud POST con datos que se espera que fallen la validación Pydantic."""
    # Es la misma implementación que el paso anterior, el resultado se valida en 'Then'
    return send_post_request_with_data(api_client, context, endpoint, payload)

@when(parsers.parse('envío una solicitud POST a "{endpoint}" con un cuerpo JSON malformado:\n{payload}'), target_fixture="response")
def send_post_request_with_malformed_json(api_client, context, endpoint: str, payload: str):
    """Envía una solicitud POST con un string que no es JSON válido."""
    # Aquí no usamos json=data, enviamos el string directamente como content
    # y especificamos el content type para simular un cliente enviando mal el JSON.
    headers = {'Content-Type': 'application/json'}
    response = api_client.post(endpoint, content=payload, headers=headers)
    context['response'] = response
    return response # Devolver para target_fixture

# --- Then Steps --- #

@then(parsers.parse("la respuesta debe tener un código de estado {status_code:d}"))
def check_status_code(context, status_code: int):
    """Verifica que el código de estado de la respuesta es el esperado."""
    response = context.get('response')
    assert response is not None, "No se encontró respuesta en el contexto"
    assert response.status_code == status_code, \
           f"Código de estado esperado {status_code} pero se obtuvo {response.status_code}. Detalle: {response.text}"

@then('la respuesta debe contener un JSON con la clave "probabilities"')
def check_response_contains_probabilities_key(context):
    """Verifica que la respuesta JSON contiene la clave 'probabilities'."""
    response = context.get('response')
    assert response is not None, "No se encontró respuesta en el contexto"
    try:
        response_data = response.json()
        assert "probabilities" in response_data, "La clave 'probabilities' no está en la respuesta JSON"
    except json.JSONDecodeError:
        pytest.fail(f"La respuesta no es un JSON válido: {response.text}")

@then(parsers.parse("el valor de \"probabilities\" debe ser una lista con {count:d} elemento(s)"))
def check_probabilities_list_length(context, count: int):
    """Verifica que la lista 'probabilities' tiene la longitud esperada."""
    response = context.get('response')
    assert response is not None, "No se encontró respuesta en el contexto"
    response_data = response.json()
    probabilities = response_data.get("probabilities")
    assert isinstance(probabilities, list), "El valor de 'probabilities' no es una lista"
    assert len(probabilities) == count, f"Se esperaba una lista con {count} elementos, pero tiene {len(probabilities)}"

@then("cada probabilidad en la lista debe ser un número entre 0.0 y 1.0")
def check_probabilities_values(context):
    """Verifica que cada elemento en la lista 'probabilities' es un float entre 0 y 1."""
    response = context.get('response')
    assert response is not None, "No se encontró respuesta en el contexto"
    response_data = response.json()
    probabilities = response_data.get("probabilities")
    assert all(isinstance(p, float) and 0.0 <= p <= 1.0 for p in probabilities), \
           f"No todas las probabilidades están entre 0.0 y 1.0: {probabilities}" 