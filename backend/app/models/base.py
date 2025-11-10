"""
Base model para todos los modelos SQLAlchemy
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
from typing import Optional

# Base para todos los modelos SQLAlchemy
Base = declarative_base()

class BaseModel(Base):
    """Clase base para todos los modelos"""
    __abstract__ = True
    
    # Campos comunes que todos los modelos herederán
    id = Column(String, primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Manejar objetos datetime
            if hasattr(value, 'isoformat'):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    def __repr__(self):
        """Representación del objeto"""
        return f"<{self.__class__.__name__}(id={self.id})>"