import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import User, UserRole

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de seguridad
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    Servicio para manejar la autenticación y autorización.
    """
    def __init__(self, db: Session):
        """
        Inicializa el servicio de autenticación.
        
        Args:
            db: Sesión de base de datos
        """
        self.db = db
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Hash de la contraseña
            
        Returns:
            bool: True si la contraseña coincide, False en caso contrario
        """
        return pwd_context.verify(plain_password, hashed_password)
        
    def get_password_hash(self, password: str) -> str:
        """
        Genera un hash para una contraseña.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        return pwd_context.hash(password)
        
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Autentica un usuario por email y contraseña.
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
            
        Returns:
            Optional[User]: Usuario autenticado o None si la autenticación falla
        """
        try:
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                return None
                
            if not self.verify_password(password, user.hashed_password):
                return None
                
            return user
            
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            return None
            
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT de acceso.
        
        Args:
            data: Datos a incluir en el token
            expires_delta: Tiempo de expiración del token
            
        Returns:
            str: Token JWT
        """
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Error al crear token: {str(e)}")
            raise
            
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica un token JWT.
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Optional[Dict[str, Any]]: Datos del token o None si la verificación falla
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
            
        except JWTError as e:
            logger.error(f"Error al verificar token: {str(e)}")
            return None
            
    def get_current_user(self, token: str) -> Optional[User]:
        """
        Obtiene el usuario actual a partir de un token JWT.
        
        Args:
            token: Token JWT
            
        Returns:
            Optional[User]: Usuario actual o None si no se encuentra
        """
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
                
            user_id = payload.get("sub")
            if not user_id:
                return None
                
            user = self.db.query(User).filter(User.id == user_id).first()
            return user
            
        except Exception as e:
            logger.error(f"Error al obtener usuario actual: {str(e)}")
            return None
            
    def check_permissions(self, user: User, required_role: UserRole) -> bool:
        """
        Verifica si un usuario tiene los permisos necesarios.
        
        Args:
            user: Usuario a verificar
            required_role: Rol requerido
            
        Returns:
            bool: True si el usuario tiene los permisos necesarios, False en caso contrario
        """
        return user.rol == required_role 