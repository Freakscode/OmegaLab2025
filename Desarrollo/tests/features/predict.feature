# Archivo BDD para el endpoint de predicción

Feature: Endpoint de Predicción de Estrés Académico
    Para predecir la probabilidad de estrés académico en estudiantes
    Como usuario de la API
    Quiero enviar datos de estudiantes al endpoint /predict y recibir las probabilidades

    Scenario: Predicción exitosa para un solo estudiante
        Given la API está funcionando
        And los artefactos de ML (preprocesador y modelo) están cargados correctamente
        When envío una solicitud POST a "/api/v1/predict" con los siguientes datos de estudiante:
            """
            {
                "students": [
                    {
                        "gender": "Female",
                        "year_of_study": 2,
                        "program_major": "Computer Science",
                        "credit_load": 15,
                        "gpa_previous_semester": 3.5,
                        "gpa_current_semester": 3.2,
                        "number_of_failed_courses_current_semester": 0,
                        "number_of_course_withdrawals_current_semester": 1,
                        "entrance_exam_score_percentile": 85.5,
                        "lms_activity_weekly_hours_avg_last_month": 10.2,
                        "support_service_use_last_month": 1,
                        "edad": 20
                    }
                ]
            }
            """
        Then la respuesta debe tener un código de estado 200
        And la respuesta debe contener un JSON con la clave "probabilities"
        And el valor de "probabilities" debe ser una lista con 1 elemento
        And cada probabilidad en la lista debe ser un número entre 0.0 y 1.0

    Scenario: Solicitud con datos inválidos (ej. tipo incorrecto)
        Given la API está funcionando
        When envío una solicitud POST a "/api/v1/predict" con datos de estudiante inválidos:
            """
            {
                "students": [
                    {
                        "gender": "Other", # Valor no permitido
                        "year_of_study": "two", # Tipo incorrecto
                        "program_major": "Engineering",
                        "credit_load": 18,
                        "gpa_previous_semester": 3.8,
                        "gpa_current_semester": 3.9,
                        "number_of_failed_courses_current_semester": 0,
                        "number_of_course_withdrawals_current_semester": 0,
                        "entrance_exam_score_percentile": 92.0,
                        "lms_activity_weekly_hours_avg_last_month": 8.5,
                        "support_service_use_last_month": 0,
                        "edad": 21
                    }
                ]
            }
            """
        Then la respuesta debe tener un código de estado 422 # Unprocessable Entity (error de validación Pydantic)

    Scenario: Solicitud con cuerpo JSON malformado
        Given la API está funcionando
        When envío una solicitud POST a "/api/v1/predict" con un cuerpo JSON malformado:
            """
            {
                "students": [
                    {
                        "gender": "Male",
                        "year_of_study": 1
                        # Falta cerrar llave y otras propiedades
            """
        Then la respuesta debe tener un código de estado 400 # Bad Request (depende de cómo FastAPI maneje JSON inválido)
        # O podría ser 422 si Pydantic lo captura primero.

    # Puedes añadir más escenarios para: múltiples estudiantes, errores de carga de artefactos (simulados), etc. 