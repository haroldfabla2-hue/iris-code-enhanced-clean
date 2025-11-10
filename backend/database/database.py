"""
Modelos de base de datos PostgreSQL con pgvector para sistema RAG
Soporta embeddings vectoriales para búsqueda semántica
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, CheckConstraint, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import json

Base = declarative_base()

class Conversation(Base):
    """Modelo para conversaciones"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255))
    title = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    metadata = Column(JSON, default={})
    
    # Relaciones
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    agent_messages = relationship("AgentMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id='{self.session_id}', title='{self.title}')>"

class Message(Base):
    """Modelo para mensajes de usuario/asistente"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    tokens = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON, default={})
    # Embedding vector para RAG (1536 dimensiones para OpenAI embeddings)
    embedding = Column(Text)  # Almacenado como string JSON para compatibilidad con SQLAlchemy
    
    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_message_role'),
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role='{self.role}')>"
    
    def set_embedding(self, embedding_list):
        """Convierte lista de embeddings a string JSON para almacenamiento"""
        if embedding_list:
            self.embedding = json.dumps(embedding_list)
    
    def get_embedding(self):
        """Convierte string JSON a lista de embeddings"""
        if self.embedding:
            return json.loads(self.embedding)
        return None

class AgentMessage(Base):
    """Modelo para mensajes de agentes especializados"""
    __tablename__ = 'agent_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    message_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    step_number = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON, default={})
    # Embedding vector para RAG
    embedding = Column(Text)
    
    # Relaciones
    conversation = relationship("Conversation", back_populates="agent_messages")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("message_type IN ('reasoning', 'action', 'result', 'planning')", name='check_agent_message_type'),
    )
    
    def __repr__(self):
        return f"<AgentMessage(id={self.id}, conversation_id={self.conversation_id}, agent_name='{self.agent_name}', type='{self.message_type}')>"
    
    def set_embedding(self, embedding_list):
        """Convierte lista de embeddings a string JSON para almacenamiento"""
        if embedding_list:
            self.embedding = json.dumps(embedding_list)
    
    def get_embedding(self):
        """Convierte string JSON a lista de embeddings"""
        if self.embedding:
            return json.loads(self.embedding)
        return None

class KnowledgeBase(Base):
    """Modelo para base de conocimiento RAG"""
    __tablename__ = 'knowledge_base'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False)
    source_url = Column(String(1000))
    source_file = Column(String(500))
    tags = Column(ARRAY(String))  # Array de tags para categorización
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    metadata = Column(JSON, default={})
    # Embedding vector para búsqueda semántica
    embedding = Column(Text)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("source_type IN ('document', 'web_page', 'manual_entry', 'generated')", name='check_source_type'),
    )
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, title='{self.title}', source_type='{self.source_type}')>"
    
    def set_embedding(self, embedding_list):
        """Convierte lista de embeddings a string JSON para almacenamiento"""
        if embedding_list:
            self.embedding = json.dumps(embedding_list)
    
    def get_embedding(self):
        """Convierte string JSON a lista de embeddings"""
        if self.embedding:
            return json.loads(self.embedding)
        return None