"""
Endpoints API para chat con streaming
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio
from datetime import datetime

from app.core.database import get_db
from app.services.chat_service import ChatService
from app.models.chat import Conversation, Message
from app.core.llm_router import LLMRouter

# Router con prefijo único para evitar conflictos
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

def get_chat_service(db: Session = Depends(get_db), llm_router: LLMRouter = None) -> ChatService:
    """Dependency para ChatService"""
    service = ChatService(db)
    if llm_router:
        service.set_llm_router(llm_router)
    return service

@router.post("/", response_model=Conversation)
async def create_conversation(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    title: Optional[str] = None,
    service: ChatService = Depends(get_chat_service)
):
    """Crear nueva conversación"""
    try:
        conversation = service.create_conversation(
            user_id=user_id,
            project_id=project_id,
            title=title
        )
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando conversación: {str(e)}")

@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message: dict,  # {content, role}
    user_id: Optional[str] = None,
    stream: bool = False,
    service: ChatService = Depends(get_chat_service)
):
    """Enviar mensaje y obtener respuesta"""
    try:
        if stream:
            # Streaming response
            return StreamingResponse(
                service.stream_chat(conversation_id, message, user_id),
                media_type="text/event-stream"
            )
        else:
            # Respuesta normal
            response = service.send_message(conversation_id, message, user_id)
            return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando mensaje: {str(e)}")

@router.get("/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(
    conversation_id: str,
    user_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener mensajes de una conversación"""
    try:
        query = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())
        
        if user_id:
            # Verificar que el usuario tenga acceso
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        messages = query.limit(limit).all()
        return messages
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo mensajes: {str(e)}")

@router.get("/conversations", response_model=List[Conversation])
async def list_conversations(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Listar conversaciones"""
    try:
        query = db.query(Conversation).filter(Conversation.is_active == True)
        
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        
        if project_id:
            query = query.filter(Conversation.project_id == project_id)
        
        conversations = query.order_by(Conversation.last_message_at.desc()).limit(limit).all()
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo conversaciones: {str(e)}")

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: Optional[str] = None,
    service: ChatService = Depends(get_chat_service)
):
    """Eliminar conversación"""
    success = service.delete_conversation(conversation_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return {"message": "Conversación eliminada exitosamente"}