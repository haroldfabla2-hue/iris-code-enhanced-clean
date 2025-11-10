"""
Servicio de chat con soporte para streaming
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any, AsyncGenerator
import json
import asyncio
from datetime import datetime

from app.models.chat import Conversation, Message, SystemPrompt
from app.core.llm_router import LLMRouter

class ChatService:
    """Servicio para gestión de chat y conversaciones"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_router: Optional[LLMRouter] = None
        
    def set_llm_router(self, llm_router: LLMRouter):
        """Set LLM router para respuestas"""
        self.llm_router = llm_router
    
    def create_conversation(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> Conversation:
        """Crear nueva conversación"""
        conversation = Conversation(
            user_id=user_id,
            project_id=project_id,
            title=title or "Nueva conversación"
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def send_message(
        self,
        conversation_id: str,
        message_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enviar mensaje y obtener respuesta"""
        conversation = self._get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversación no encontrada")
        
        # Crear mensaje del usuario
        user_message = Message(
            conversation_id=conversation_id,
            role=message_data.get("role", "user"),
            content=message_data.get("content", ""),
            tokens=message_data.get("tokens")
        )
        
        self.db.add(user_message)
        self.db.commit()
        self.db.refresh(user_message)
        
        # Obtener contexto de la conversación
        context = self._get_conversation_context(conversation_id)
        
        # Generar respuesta con LLM
        response_content = self._generate_response(context, message_data.get("content", ""))
        
        # Crear mensaje de respuesta
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_content,
            tokens=len(response_content.split())  # Estimación básica
        )
        
        self.db.add(assistant_message)
        
        # Actualizar conversación
        conversation.message_count += 2
        conversation.last_message_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(assistant_message)
        
        return {
            "user_message": user_message.to_dict(),
            "assistant_message": assistant_message.to_dict(),
            "conversation_id": conversation_id
        }
    
    def stream_chat(
        self,
        conversation_id: str,
        message_data: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Streaming response para chat"""
        async def generate_stream():
            try:
                conversation = self._get_conversation(conversation_id, user_id)
                if not conversation:
                    yield "data: {'error': 'Conversación no encontrada'}\n\n"
                    return
                
                # Crear mensaje del usuario
                user_message = Message(
                    conversation_id=conversation_id,
                    role="user",
                    content=message_data.get("content", ""),
                    is_streaming=True
                )
                
                self.db.add(user_message)
                self.db.commit()
                self.db.refresh(user_message)
                
                # Enviar confirmación del mensaje del usuario
                yield f"data: {json.dumps({'user_message': user_message.to_dict()})}\n\n"
                
                # Generar respuesta con streaming
                context = self._get_conversation_context(conversation_id)
                
                if not self.llm_router:
                    # Respuesta por defecto sin LLM
                    response_content = f"Entiendo tu mensaje: {message_data.get('content', '')}"
                else:
                    # Usar LLM router
                    response_content = self._generate_response_with_streaming(context, message_data.get("content", ""))
                
                # Crear mensaje de respuesta
                assistant_message = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response_content,
                    tokens=len(response_content.split()),
                    is_streaming=False,
                    stream_completed=True
                )
                
                self.db.add(assistant_message)
                conversation.message_count += 2
                conversation.last_message_at = datetime.utcnow()
                self.db.commit()
                
                # Enviar respuesta final
                yield f"data: {json.dumps({'assistant_message': assistant_message.to_dict()})}\n\n"
                yield "data: {'stream_complete': true}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return generate_stream()
    
    def _get_conversation(self, conversation_id: str, user_id: Optional[str] = None) -> Optional[Conversation]:
        """Obtener conversación con validaciones"""
        query = self.db.query(Conversation).filter(Conversation.id == conversation_id)
        
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        
        return query.first()
    
    def _get_conversation_context(self, conversation_id: str) -> List[Dict[str, str]]:
        """Obtener contexto de la conversación"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).limit(20).all()  # Últimos 20 mensajes
        
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    def _generate_response(self, context: List[Dict[str, str]], user_message: str) -> str:
        """Generar respuesta usando LLM"""
        if not self.llm_router:
            return f"Disculpa, el sistema de LLM no está disponible. Mensaje recibido: {user_message}"
        
        # Preparar prompt completo
        system_prompt = "Eres IRIS Code, un asistente AI especializado en desarrollo de software y gestión de proyectos."
        
        messages = [
            {"role": "system", "content": system_prompt},
            *context[-10:],  # Últimos 10 mensajes para contexto
            {"role": "user", "content": user_message}
        ]
        
        try:
            # Usar LLM router (implementación específica depende del router)
            response = self.llm_router.generate(messages)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Error generando respuesta: {str(e)}"
    
    def _generate_response_with_streaming(self, context: List[Dict[str, str]], user_message: str) -> str:
        """Generar respuesta con streaming"""
        # Por ahora, respuesta simple. En implementación completa sería streaming del LLM
        return f"Entiendo tu mensaje sobre '{user_message}'. Puedo ayudarte con tu proyecto de desarrollo."
    
    def delete_conversation(self, conversation_id: str, user_id: Optional[str] = None) -> bool:
        """Eliminar conversación"""
        conversation = self._get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        
        conversation.is_active = False
        self.db.commit()
        return True