"""
Agente Memory Manager - Gestiona memoria semántica RAG
Responsable de almacenar y recuperar conocimiento con embeddings
"""
from typing import List, Dict, Any, Optional, Tuple
import json
import hashlib
from datetime import datetime
import os
import asyncio

from .base import BaseAgent
from ..models import AgentMessage, AgentResponse, MessageStatus
from ..services.embedding_service import EmbeddingService, initialize_embedding_service
from ..services.chunking_service import DocumentChunker, ChunkingStrategy

logger = logging.getLogger(__name__)


class MemoryManagerAgent(BaseAgent):
    """
    Agente Memory Manager: Gestiona memoria semántica de largo plazo
    
    Responsabilidades:
    - Sintetizar y almacenar insights en pgvector
    - Consolidar snapshots de estado
    - Gestionar versionado de contexto
    - Recuperar conocimiento relevante (RAG)
    """
    
    def __init__(self, llm_client: Any = None, vector_store: Any = None):
        super().__init__(
            agent_id="memory_manager",
            llm_client=llm_client
        )
        self.vector_store = vector_store
        self.memory_cache = {}  # Cache temporal
        self.db_engine = None
        self.embedding_service: Optional[EmbeddingService] = None
        self.chunker: Optional[DocumentChunker] = None
        self._init_database_connection()
        self._init_rag_services()
    
    async def _init_rag_services(self):
        """Inicializa servicios de embeddings y chunking para RAG"""
        try:
            self.logger.info("Inicializando servicios RAG...")
            
            # Inicializar servicio de embeddings con HuggingFace
            self.embedding_service = await initialize_embedding_service()
            
            # Inicializar chunker de documentos
            self.chunker = DocumentChunker()
            
            # Obtener información del modelo
            if self.embedding_service:
                model_info = await self.embedding_service.get_model_info()
                self.logger.info(f"Servicio de embeddings inicializado: {model_info.get('model_name')} en {model_info.get('device')}")
            
            self.logger.info("Servicios RAG inicializados correctamente")
            
        except Exception as e:
            self.logger.warning(f"Error inicializando servicios RAG: {str(e)} - usando fallback")
            self.embedding_service = None
            self.chunker = None
    
    def _init_database_connection(self):
        """Inicializa conexión a PostgreSQL con pgvector"""
        try:
            # Importación lazy de sqlalchemy
            try:
                from sqlalchemy import create_engine, text
            except ImportError as ie:
                self.logger.warning(f"SQLAlchemy no disponible: {ie} - usando cache local")
                self.db_engine = None
                return
            
            # Configuración de base de datos usando variables de entorno
            db_host = os.getenv("POSTGRES_HOST", "postgres")
            db_port = os.getenv("POSTGRES_PORT", "5432")
            db_name = os.getenv("POSTGRES_DB", "agente_db")
            db_user = os.getenv("POSTGRES_USER", "postgres")
            db_password = os.getenv("POSTGRES_PASSWORD", "postgres_secure_password")
            
            # Construir URL de conexión
            db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            # Crear engine SQLAlchemy
            self.db_engine = create_engine(db_url)
            
            # Probar conexión
            with self.db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                self.logger.info("Conectado a PostgreSQL exitosamente")
                
                # Crear tabla si no existe
                self._create_memory_tables()
                
        except Exception as e:
            self.logger.warning(f"No se pudo conectar a PostgreSQL: {str(e)} - usando cache local")
            self.db_engine = None