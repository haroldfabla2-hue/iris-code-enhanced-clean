"""
Modelos de datos para proyectos
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.models.base import BaseModel

class Project(BaseModel):
    """Modelo de Proyecto"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(String(100), nullable=True, index=True)  # Para multi-user en el futuro
    project_type = Column(String(100), nullable=True)  # web-app, api, script, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Metadata flexible
    metadata = Column(JSON, default=dict)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relaciones
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class File(BaseModel):
    """Modelo de Archivo"""
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Información del archivo
    name = Column(String(255), nullable=False)
    path = Column(Text, nullable=False)  # Ruta relativa en el sistema de archivos
    size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=True)
    hash_sha256 = Column(String(64), nullable=True, index=True)  # Para deduplicación
    extension = Column(String(20), nullable=True, index=True)
    
    # Metadata flexible
    metadata = Column(JSON, default=dict)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    project = relationship("Project", back_populates="files")
    
    def __repr__(self):
        return f"<File(id={self.id}, name='{self.name}', project_id={self.project_id})>"


class Template(BaseModel):
    """Modelo de Template"""
    __tablename__ = "templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Información del template
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(String(255)[] , default=list)  # Array de strings
    
    # Rutas y archivos
    path = Column(Text, nullable=False)  # Ruta al directorio del template
    preview_image = Column(Text, nullable=True)  # URL o path a imagen preview
    
    # Métricas
    downloads_count = Column(BigInteger, default=0, index=True)
    rating = Column(String(10), nullable=True)  # avg rating, opcional
    
    # Metadata flexible
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', category='{self.category}')>"