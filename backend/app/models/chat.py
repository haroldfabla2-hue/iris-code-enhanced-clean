"""
Modelos de datos para chat y conversaciones
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.models.base import BaseModel

class Conversation(BaseModel):
    """Modelo de Conversación"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(String(100), nullable=True, index=True)  # Para multi-user
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Información de la conversación
    title = Column(String(255), nullable=True)  # Auto-generado del primer mensaje
    context_summary = Column(Text, nullable=True)  # Resumen de contexto generado por IA
    
    # Estado
    is_active = Column(Boolean, default=True, index=True)
    message_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Metadata flexible
    metadata = Column(JSON, default=dict)
    
    # Relaciones
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    project = relationship("Project", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', project_id={self.project_id})>"


class Message(BaseModel):
    """Modelo de Mensaje"""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Contenido del mensaje
    role = Column(String(20), nullable=False, index=True)  # user, assistant, system
    content = Column(Text, nullable=False)
    tokens = Column(Integer, nullable=True)  # Numero de tokens del mensaje
    
    # Estado de streaming
    is_streaming = Column(Boolean, default=False)
    stream_completed = Column(Boolean, default=False)
    
    # Metadata flexible
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")
    
    # Validación
    __table_args__ = (
        {'check_constraint': "role IN ('user', 'assistant', 'system')"},
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"


class SystemPrompt(BaseModel):
    """Modelo de Prompts del Sistema"""
    __tablename__ = "system_prompts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Contenido del prompt
    prompt_content = Column(Text, nullable=False)
    
    # Configuración
    is_active = Column(Boolean, default=True, index=True)
    is_default = Column(Boolean, default=False, index=True)
    
    # Metadata
    tags = Column(String(255)[], default=list)
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SystemPrompt(id={self.id}, name='{self.name}', is_default={self.is_default})>"