# OmegaLab - Sistema de Predicción de Estrés Académico

OmegaLab es un sistema integral para la predicción y gestión del estrés académico en estudiantes universitarios. Utiliza técnicas de aprendizaje automático para predecir niveles de estrés y riesgo de deserción, y proporciona herramientas para administradores y estudiantes.

## Características

- **Predicción de Estrés**: Modelo de ML para predecir niveles de estrés y riesgo de deserción.
- **Gestión de Instituciones**: Soporte para múltiples instituciones educativas con configuraciones personalizadas.
- **Gestión de Usuarios**: Sistema de autenticación y autorización con roles (ADMIN, STUDENT).
- **Datos Académicos**: Registro y seguimiento de eventos académicos, actividad en LMS y uso de servicios de apoyo.
- **Chat Asistente**: Agente conversacional para apoyo a estudiantes.
- **API RESTful**: Interfaz de programación completa para integración con otros sistemas.

## Requisitos

- Python 3.11+
- PostgreSQL 15+
- Docker y Docker Compose (opcional, para despliegue)

## Instalación

### Desarrollo Local

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/omegalab.git
   cd omegalab
   ```

2. Crear un entorno virtual e instalar dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

4. Inicializar la base de datos:
   ```bash
   alembic upgrade head
   ```

5. Ejecutar la aplicación:
   ```bash
   uvicorn app.main:app --reload
   ```

### Despliegue con Docker

1. Construir y ejecutar los contenedores:
   ```bash
   docker-compose up -d
   ```

2. Acceder a la aplicación:
   - API: http://localhost:8000
   - PgAdmin: http://localhost:5050

## Estructura del Proyecto

```
omegalab/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── models/
│   ├── services/
│   └── utils/
├── artifacts/
├── logs/
├── migrations/
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## API Endpoints

### Autenticación
- `POST /auth/token`: Obtener token de acceso
- `POST /auth/login`: Iniciar sesión

### Instituciones
- `GET /institution`: Listar instituciones
- `POST /institution`: Crear institución
- `GET /institution/{id}`: Obtener institución
- `PUT /institution/{id}`: Actualizar institución
- `DELETE /institution/{id}`: Eliminar institución

### Estudiantes
- `GET /students`: Listar estudiantes
- `POST /students`: Crear estudiante
- `GET /students/{id}`: Obtener estudiante
- `PUT /students/{id}`: Actualizar estudiante
- `DELETE /students/{id}`: Eliminar estudiante

### Predicciones
- `POST /prediccion/estudiante/{id}`: Predecir estrés para un estudiante
- `GET /prediccion/estudiantes`: Obtener predicciones para todos los estudiantes
- `GET /prediccion/estudiante/{id}/historial`: Obtener historial de predicciones

### Datos Académicos
- `POST /academic-data/evento-academico`: Registrar evento académico
- `POST /academic-data/datos-lms`: Actualizar datos de LMS
- `POST /academic-data/servicios-apoyo`: Actualizar datos de servicios de apoyo
- `GET /academic-data/historial/{estudiante_id}`: Obtener historial académico

### Chat
- `POST /chat/conversacion`: Iniciar conversación
- `POST /chat/conversacion/{id}/mensaje`: Enviar mensaje
- `PUT /chat/conversacion/{id}`: Actualizar estado de conversación
- `GET /chat/conversacion/{id}/historial`: Obtener historial de mensajes

## Contribución

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Tu Nombre - [@tutwitter](https://twitter.com/tutwitter) - email@example.com

Link del Proyecto: [https://github.com/tu-usuario/omegalab](https://github.com/tu-usuario/omegalab)
