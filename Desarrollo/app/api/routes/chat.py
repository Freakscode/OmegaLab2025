from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from ...models import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ConversationUpdate
)
from ...services.chat_agent import ChatAgent
from ...database import get_db

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/conversacion", response_model=ConversationResponse)
async def iniciar_conversacion(
    conversacion: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Inicia una nueva conversación con un estudiante.
    """
    try:
        chat_agent = ChatAgent(db)
        nueva_conversacion = await chat_agent.iniciar_conversacion(
            estudiante_id=conversacion.estudiante_id,
            contexto=conversacion.contexto
        )
        return nueva_conversacion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversacion/{conversacion_id}/mensaje", response_model=MessageResponse)
async def enviar_mensaje(
    conversacion_id: int,
    mensaje: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Envía un mensaje en una conversación existente y obtiene la respuesta del agente.
    """
    try:
        chat_agent = ChatAgent(db)
        respuesta = await chat_agent.enviar_mensaje(
            conversacion_id=conversacion_id,
            contenido=mensaje.contenido,
            mensaje_metadata=mensaje.mensaje_metadata
        )
        return respuesta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/conversacion/{conversacion_id}", response_model=ConversationResponse)
async def actualizar_conversacion(
    conversacion_id: int,
    actualizacion: ConversationUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado de una conversación.
    """
    try:
        chat_agent = ChatAgent(db)
        if actualizacion.estado == "finalizada":
            conversacion = await chat_agent.finalizar_conversacion(conversacion_id)
        else:
            # TODO: Implementar actualización de otros campos
            raise HTTPException(status_code=501, detail="Funcionalidad no implementada")
        return conversacion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversacion/{conversacion_id}/historial", response_model=List[MessageResponse])
async def obtener_historial(
    conversacion_id: int,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de mensajes de una conversación.
    """
    try:
        chat_agent = ChatAgent(db)
        historial = await chat_agent.obtener_historial(
            conversacion_id=conversacion_id,
            limit=limit
        )
        return historial
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 