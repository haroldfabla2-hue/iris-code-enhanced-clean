"""
Configuración de base de datos para IRIS Code
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.core.config import settings

# Variable global para engine de base de datos
engine = None
SessionLocal = None

def init_database():
    """Inicializar conexión a base de datos"""
    global engine, SessionLocal
    
    # Construir URL de base de datos
    database_url = settings.DATABASE_URL or os.getenv(
        "DATABASE_URL", 
        "sqlite:///./iris_code.db"
    )
    
    # Configurar engine según el tipo de base de datos
    if database_url.startswith("postgresql://"):
        # PostgreSQL
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=settings.DEBUG  # Solo en desarrollo
        )
    else:
        # SQLite (para desarrollo)
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.DEBUG
        )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine

def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crear todas las tablas"""
    from app.models import Base  # Importar todos los modelos
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Eliminar todas las tablas (solo para desarrollo/testing)"""
    from app.models import Base
    Base.metadata.drop_all(bind=engine)