# Contenido inicial para app/core/config.py

# Aquí podrías cargar configuraciones desde variables de entorno,
# archivos .env, etc. usando Pydantic Settings o similar.

# Ejemplo básico (podría expandirse)
ARTIFACTS_PATH = "./artifacts" # Ruta relativa a la raíz del proyecto
MODEL_NAME = "model_final_pred.keras"
PREPROCESSOR_NAME = "preprocessor_final.joblib"

# Configuraciones de seguridad (ejemplo)
# API_KEY = "tu_api_key_secreta" # ¡Mejor cargarla desde el entorno!
# JWT_SECRET = "tu_jwt_secret" # ¡Mejor cargarla desde el entorno! 