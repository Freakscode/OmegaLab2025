# Contenido inicial para app/core/security.py

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

# Placeholder para la lógica de autenticación/autorización (RNF05)

# Ejemplo con API Key (simplificado)
# En una app real, la clave debería compararse con una almacenada de forma segura
# y cargada desde la configuración (ej. app.core.config)
API_KEY_NAME = "X-API-KEY" # Nombre del header esperado
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Valida la API Key proporcionada en el header."""
    if api_key == "tu_clave_secreta_de_ejemplo": # Reemplaza con tu lógica real
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave API inválida o faltante",
        )

# Aquí podrías añadir lógica para JWT u otros mecanismos. 