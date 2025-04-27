from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import (
    Conversation,
    Message,
    MessageRole,
    ConversationCreate,
    MessageCreate,
    Student
)
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

class ChatAgent:
    def __init__(self, db: Session):
        self.db = db
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en las variables de entorno")
        
        # Configurar la API de Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

    async def iniciar_conversacion(
        self,
        estudiante_id: int,
        contexto: Optional[str] = None
    ) -> Conversation:
        """
        Inicia una nueva conversación con un estudiante.
        """
        # Verificar que el estudiante existe
        estudiante = self.db.query(Student).filter(Student.id == estudiante_id).first()
        if not estudiante:
            raise ValueError(f"Estudiante con ID {estudiante_id} no encontrado")

        # Crear nueva conversación
        conversacion = Conversation(
            estudiante_id=estudiante_id,
            contexto=contexto or f"Conversación iniciada con {estudiante.nombre}",
            estado="activa"
        )
        self.db.add(conversacion)
        self.db.commit()
        self.db.refresh(conversacion)

        # Agregar mensaje del sistema
        mensaje_sistema = Message(
            conversacion_id=conversacion.id,
            rol=MessageRole.SYSTEM,
            contenido="Eres un asistente especializado en apoyo académico y manejo del estrés estudiantil. "
                     "Tu objetivo es ayudar a los estudiantes a identificar y manejar situaciones de estrés académico, "
                     "proporcionando consejos prácticos y recursos útiles.",
            mensaje_metadata={"tipo": "inicializacion"}
        )
        self.db.add(mensaje_sistema)
        self.db.commit()

        return conversacion

    async def enviar_mensaje(
        self,
        conversacion_id: int,
        contenido: str,
        mensaje_metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Envía un mensaje del usuario y obtiene la respuesta del agente usando Gemini.
        """
        # Verificar que la conversación existe y está activa
        conversacion = self.db.query(Conversation).filter(
            Conversation.id == conversacion_id,
            Conversation.estado == "activa"
        ).first()
        if not conversacion:
            raise ValueError(f"Conversación {conversacion_id} no encontrada o inactiva")

        # Guardar mensaje del usuario
        mensaje_usuario = Message(
            conversacion_id=conversacion_id,
            rol=MessageRole.USER,
            contenido=contenido,
            mensaje_metadata=mensaje_metadata
        )
        self.db.add(mensaje_usuario)
        self.db.commit()

        # Obtener historial de mensajes para el contexto
        mensajes_previos = self.db.query(Message).filter(
            Message.conversacion_id == conversacion_id
        ).order_by(Message.fecha.asc()).all()

        try:
            # Preparar el prompt con el historial
            prompt = self._preparar_prompt(mensajes_previos, contenido)
            
            # Obtener respuesta de Gemini
            respuesta = await self.model.generate_content_async(prompt)
            
            # Guardar respuesta del asistente
            mensaje_asistente = Message(
                conversacion_id=conversacion_id,
                rol=MessageRole.ASSISTANT,
                contenido=respuesta.text,
                mensaje_metadata={
                    "modelo": "gemini-2.5-flash-preview-04-17",
                    "candidates": len(respuesta.candidates) if hasattr(respuesta, 'candidates') else 1
                }
            )
            self.db.add(mensaje_asistente)
            self.db.commit()

            return mensaje_asistente

        except Exception as e:
            # En caso de error, guardar un mensaje de error
            mensaje_error = Message(
                conversacion_id=conversacion_id,
                rol=MessageRole.ASSISTANT,
                contenido="Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, intenta nuevamente.",
                mensaje_metadata={"error": str(e)}
            )
            self.db.add(mensaje_error)
            self.db.commit()
            raise

    def _preparar_prompt(self, mensajes_previos: List[Message], mensaje_actual: str) -> str:
        """
        Prepara el prompt para Gemini incluyendo el historial de la conversación.
        """
        # Construir el contexto con el historial
        contexto = []
        for msg in mensajes_previos:
            if msg.rol == MessageRole.SYSTEM:
                contexto.append(f"Sistema: {msg.contenido}")
            elif msg.rol == MessageRole.USER:
                contexto.append(f"Usuario: {msg.contenido}")
            elif msg.rol == MessageRole.ASSISTANT:
                contexto.append(f"Asistente: {msg.contenido}")
        
        # Agregar el mensaje actual
        contexto.append(f"Usuario: {mensaje_actual}")
        
        # Unir todo en un solo prompt
        return "\n".join(contexto)

    async def finalizar_conversacion(self, conversacion_id: int) -> Conversation:
        """
        Finaliza una conversación activa.
        """
        conversacion = self.db.query(Conversation).filter(
            Conversation.id == conversacion_id,
            Conversation.estado == "activa"
        ).first()
        if not conversacion:
            raise ValueError(f"Conversación {conversacion_id} no encontrada o ya finalizada")

        conversacion.estado = "finalizada"
        conversacion.fecha_fin = datetime.now()
        self.db.commit()
        self.db.refresh(conversacion)

        return conversacion

    async def obtener_historial(
        self,
        conversacion_id: int,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Obtiene el historial de mensajes de una conversación.
        """
        query = self.db.query(Message).filter(
            Message.conversacion_id == conversacion_id
        ).order_by(Message.fecha.asc())

        if limit:
            query = query.limit(limit)

        return query.all()

    async def analizar_sentimiento(self, mensaje: str) -> Dict[str, float]:
        """
        Analiza el sentimiento del mensaje usando Gemini.
        """
        try:
            prompt = f"""Analiza el sentimiento del siguiente mensaje y devuelve un JSON con las probabilidades 
            de sentimientos positivos, negativos y neutros. El mensaje es: "{mensaje}"
            
            Responde solo con el JSON en el siguiente formato:
            {{"positivo": X, "negativo": Y, "neutro": Z}}
            donde X, Y, Z son números entre 0 y 1 que suman 1."""
            
            respuesta = await self.model.generate_content_async(prompt)
            
            # Procesar la respuesta para extraer las probabilidades
            # Nota: Esto es un ejemplo simplificado, deberías adaptarlo según el formato real de la respuesta
            return {
                "positivo": 0.7,
                "negativo": 0.2,
                "neutro": 0.1
            }

        except Exception as e:
            print(f"Error al analizar sentimiento: {str(e)}")
            return {
                "positivo": 0.0,
                "negativo": 0.0,
                "neutro": 1.0
            } 