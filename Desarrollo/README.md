l# 💻 Desarrollo – OmegaLab 2025

## ¡Bienvenidos a la carpeta de Desarrollo!

Aquí se debe subir **todo el material y avances técnicos** que el área de Desarrollo genere durante el reto OmegaLab 2025.

---

## 🛠️ ¿Qué tipo de contenidos pueden ir aquí?

- Código fuente del proyecto
- Documentación técnica
- Pruebas y prototipos funcionales
- Avances de desarrollo y mejoras
- Cualquier otro recurso relacionado con la parte técnica o de programación

> ℹ️ **Nota:** No es necesario seguir un formato exacto, pero es importante mantener el contenido organizado, claro y actualizado para facilitar su revisión.

---

¡Mucho éxito programando y creando cosas increíbles! 🚀

# API de Predicción de Estrés Académico

Este proyecto implementa una API RESTful usando FastAPI para predecir la probabilidad de estrés académico en estudiantes, basado en un modelo de Machine Learning pre-entrenado.

## Estructura del Proyecto

```
.
├── app/                  # Código fuente de la aplicación FastAPI
│   ├── api/              # Módulos relacionados con la API (endpoints, modelos)
│   ├── core/             # Configuración central, seguridad
│   ├── services/         # Lógica de negocio (predicción, carga de modelos)
│   └── main.py           # Punto de entrada de la aplicación FastAPI
├── artifacts/            # Artefactos de ML (preprocesador, modelo) - ¡Asegúrate de poner los reales aquí!
├── tests/                # Tests (unitarios, integración, BDD)
│   ├── features/         # Archivos .feature (BDD)
│   └── step_defs/        # Implementación de los steps BDD
├── .gitignore            # Archivos a ignorar por Git
├── Dockerfile            # Definición para construir la imagen Docker
├── README.md             # Este archivo
└── requirements.txt      # Dependencias Python
```

## Requisitos Previos

*   Python 3.10+
*   Docker (recomendado para ejecución y despliegue consistentes)
*   Los artefactos `preprocessor_final.joblib` y `model_final_pred.keras` deben existir en el directorio `artifacts/` (los archivos actuales son placeholders).

## Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-directorio>
    ```

2.  **Crear y activar un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows (Git Bash/WSL)
    source venv/bin/activate
    # En Windows (Command Prompt)
    # venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Ejecución (Local)

Desde la raíz del proyecto, ejecuta:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

*   `--reload`: Recarga automáticamente la aplicación cuando detecta cambios en el código (útil para desarrollo).
*   `--host 0.0.0.0`: Permite acceder a la API desde otras máquinas en la red local.
*   `--port 8000`: Puerto en el que correrá la API.

La API estará disponible en `http://localhost:8000` (o la IP de tu máquina en el puerto 8000).
La documentación interactiva (Swagger UI) estará en `http://localhost:8000/docs`.

## Ejecución (Docker)

1.  **Construir la imagen Docker:**
    ```bash
    docker build -t api-estres-academico .
    ```

2.  **Ejecutar el contenedor:**
    ```bash
    docker run -d -p 8000:8000 --name api_estres api-estres-academico
    ```
    *   `-d`: Ejecuta el contenedor en segundo plano.
    *   `-p 8000:8000`: Mapea el puerto 8000 del host al puerto 8000 del contenedor.
    *   `--name api_estres`: Asigna un nombre al contenedor.

La API estará disponible igual que en la ejecución local.

## Ejecución de Tests (BDD)

Asegúrate de tener las dependencias de desarrollo instaladas (`pytest`, `pytest-bdd`, etc., incluidas en `requirements.txt`).

Desde la raíz del proyecto, ejecuta:

```bash
pytest
```

Pytest descubrirá y ejecutará los tests definidos en `tests/step_defs/` basados en los features de `tests/features/`.

## Endpoints API

*   `GET /health`: Verifica el estado de la API. Devuelve `{"status": "ok"}`.
*   `POST /api/v1/predict`: Endpoint principal para obtener predicciones.
    *   **Request Body:** JSON con una clave `students` que contiene una lista de objetos, cada uno representando un estudiante con sus características (ver `app/api/models.py` para el esquema exacto).
    *   **Response Body (Éxito - 200 OK):** JSON con una clave `probabilities` que contiene una lista de floats (probabilidad de estrés para cada estudiante en el orden de entrada).
    *   **Response Body (Error - 400/422/500):** JSON con detalles del error.

## Próximos Pasos / Mejoras

*   Implementar la lógica real de carga de artefactos si se usa S3 u otro almacenamiento.
*   Implementar la autenticación/autorización (RNF05) en `app/core/security.py` y aplicarla al endpoint `/predict`.
*   Refinar el manejo de errores y logging (RNF08).
*   Añadir tests unitarios para `app/services/prediction.py`.
*   Configurar monitorización (RNF08).
*   Optimizar el rendimiento y escalabilidad si es necesario (RNF01, RNF02, RNF03).
*   Configurar HTTPS (RNF05).
