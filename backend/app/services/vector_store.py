"""
VectorStore Service con PostgreSQL + pgvector
Implementa almacenamiento y búsqueda de embeddings vectoriales
"""
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import logging
import json
import hashlib
from datetime import datetime
import numpy as np
from sqlalchemy import text, create_engine
from sqlalchemy.pool import StaticPool
import psycopg2
from psycopg2.extras import RealDictCursor

from .embedding_service import EmbeddingService
from .chunking_service import DocumentChunker, Chunk

logger = logging.getLogger(__name__)


class VectorStore:
    """
    VectorStore usando PostgreSQL + pgvector para almacenamiento vectorial
    
    Características:
    - Almacenamiento de embeddings en pgvector
    - Búsqueda semántica con similitud coseno
    - Índices HNSW para búsqueda rápida
    - Filtrado por metadatos
    - Cache de embeddings frecuentes
    """
    
    def __init__(self, db_url: str, embedding_service: EmbeddingService):
        """
        Inicializa VectorStore
        
        Args:
            db_url: URL de conexión a PostgreSQL
            embedding_service: Servicio de embeddings ya inicializado
        """
        self.db_url = db_url
        self.embedding_service = embedding_service
        self.engine = None
        self.chunker = DocumentChunker()
        self.embedding_cache = {}  # Cache de embeddings por hash de texto
        self.cache_size_limit = 5000
        
    async def initialize(self) -> Dict[str, Any]:
        """
        Inicializa VectorStore y crea tablas necesarias
        
        Returns:
            Dict con información de inicialización
        """
        try:
            # Crear engine de SQLAlchemy
            self.engine = create_engine(
                self.db_url,
                poolclass=StaticPool
            )
            
            # Probar conexión primero
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Crear tablas si no existen
            await self._create_tables()
            
            # Crear índices para optimización
            await self._create_indexes()
            
            logger.info("VectorStore inicializado exitosamente")
            return {
                "status": "initialized",
                "database_url": self.db_url,
                "embedding_dimensions": 384,
                "cache_size_limit": self.cache_size_limit
            }
            
        except Exception as e:
            logger.error(f"Error inicializando VectorStore: {e}")
            raise
    
    async def _create_tables(self):
        """Crea las tablas necesarias para vector storage"""
        with self.engine.connect() as conn:
            # Tabla principal de documentos
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_type VARCHAR(50) DEFAULT 'text',
                    user_id VARCHAR(100),
                    conversation_id VARCHAR(100),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT,
                    file_size INTEGER,
                    mime_type VARCHAR(100)
                )
            """))
            
            # Tabla de chunks con embeddings
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    start_position INTEGER NOT NULL,
                    end_position INTEGER NOT NULL,
                    token_count INTEGER,
                    metadata JSONB DEFAULT '{}',
                    embedding vector(384),  -- Dimensión del modelo all-MiniLM-L6-v2
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Tabla de conversaciones para memoria
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id VARCHAR(100) NOT NULL,
                    session_id VARCHAR(100),
                    title TEXT,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Tabla de mensajes con embeddings
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS messages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
                    content TEXT NOT NULL,
                    agent_id VARCHAR(50),
                    metadata JSONB DEFAULT '{}',
                    embedding vector(384),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.commit()
            logger.info("Tablas de VectorStore creadas exitosamente")
    
    async def _create_indexes(self):
        """Crea índices para optimizar búsquedas"""
        with self.engine.connect() as conn:
            # Índice HNSW para búsqueda vectorial rápida
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
                ON document_chunks USING hnsw (embedding vector_cosine_ops)
            """))
            
            # Índices para filtros
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_documents_conversation_id ON documents(conversation_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_documents_content_type ON documents(content_type)"))
            
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)"))
            
            conn.commit()
            logger.info("Índices de VectorStore creados exitosamente")
    
    async def store_document(
        self, 
        title: str, 
        content: str, 
        content_type: str = "text",
        user_id: str = None, 
        conversation_id: str = None,
        metadata: Dict[str, Any] = None,
        chunk_strategy: str = "recursive"
    ) -> str:
        """
        Almacena un documento completo con chunking y embeddings
        
        Args:
            title: Título del documento
            content: Contenido del documento
            content_type: Tipo de contenido ('text', 'pdf', 'docx', etc.)
            user_id: ID del usuario
            conversation_id: ID de conversación
            metadata: Metadatos adicionales
            chunk_strategy: Estrategia de chunking
            
        Returns:
            ID del documento almacenado
        """
        try:
            # Generar chunks usando DocumentChunker
            chunks = await self._chunk_document(content, chunk_strategy)
            
            # Almacenar documento y chunks en transacción
            with self.engine.connect() as conn:
                trans = conn.begin()
                
                try:
                    # Insertar documento
                    doc_result = conn.execute(text("""
                        INSERT INTO documents (title, content, content_type, user_id, conversation_id, metadata)
                        VALUES (:title, :content, :content_type, :user_id, :conversation_id, :metadata)
                        RETURNING id
                    """), {
                        "title": title,
                        "content": content,
                        "content_type": content_type,
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "metadata": json.dumps(metadata or {})
                    })
                    
                    document_id = doc_result.fetchone()[0]
                    
                    # Generar embeddings y almacenar chunks
                    for i, chunk in enumerate(chunks):
                        embedding = await self._get_or_generate_embedding(chunk.content)
                        
                        conn.execute(text("""
                            INSERT INTO document_chunks 
                            (document_id, chunk_index, content, start_position, end_position, token_count, metadata, embedding)
                            VALUES (:document_id, :chunk_index, :content, :start_position, :end_position, :token_count, :metadata, :embedding)
                        """), {
                            "document_id": document_id,
                            "chunk_index": i,
                            "content": chunk.content,
                            "start_position": chunk.start_position,
                            "end_position": chunk.end_position,
                            "token_count": chunk.token_count,
                            "metadata": json.dumps(chunk.metadata),
                            "embedding": f"[{','.join(map(str, embedding))}]"
                        })
                    
                    trans.commit()
                    logger.info(f"Documento almacenado exitosamente: {document_id}")
                    return str(document_id)
                    
                except Exception as e:
                    trans.rollback()
                    raise e
                    
        except Exception as e:
            logger.error(f"Error almacenando documento: {e}")
            raise
    
    async def store_conversation_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        agent_id: str = None,
        user_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Almacena un mensaje de conversación con embedding
        
        Args:
            conversation_id: ID de conversación
            role: Rol del mensaje ('user', 'assistant', 'system')
            content: Contenido del mensaje
            agent_id: ID del agente (si es mensaje de asistente)
            user_id: ID del usuario
            metadata: Metadatos adicionales
            
        Returns:
            ID del mensaje almacenado
        """
        try:
            # Generar embedding del mensaje
            embedding = await self._get_or_generate_embedding(content)
            
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    INSERT INTO messages (conversation_id, role, content, agent_id, metadata, embedding)
                    VALUES (:conversation_id, :role, :content, :agent_id, :metadata, :embedding)
                    RETURNING id
                """), {
                    "conversation_id": conversation_id,
                    "role": role,
                    "content": content,
                    "agent_id": agent_id,
                    "metadata": json.dumps(metadata or {}),
                    "embedding": f"[{','.join(map(str, embedding))}]"
                })
                
                message_id = result.fetchone()[0]
                logger.info(f"Mensaje almacenado: {message_id}")
                return str(message_id)
                
        except Exception as e:
            logger.error(f"Error almacenando mensaje: {e}")
            raise
    
    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        user_id: str = None,
        conversation_id: str = None,
        content_type: str = None,
        time_range: str = None
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda semántica en documentos y mensajes
        
        Args:
            query: Consulta de búsqueda
            limit: Número máximo de resultados
            user_id: Filtrar por usuario
            conversation_id: Filtrar por conversación
            content_type: Filtrar por tipo de contenido
            time_range: Rango temporal ('1h', '1d', '1w', '1m', 'all')
            
        Returns:
            Lista de resultados con scores de similitud
        """
        try:
            # Generar embedding de la consulta
            query_embedding = await self._get_or_generate_embedding(query)
            
            # Construir query con filtros
            base_query = """
                SELECT 
                    'chunk' as result_type,
                    dc.id,
                    dc.content,
                    d.title as document_title,
                    d.content_type,
                    dc.metadata,
                    1 - (dc.embedding <=> :query_embedding) as similarity_score,
                    dc.created_at
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE 1=1
            """
            
            filters = []
            params = {
                "query_embedding": f"[{','.join(map(str, query_embedding))}]",
                "limit": limit
            }
            
            # Aplicar filtros
            if user_id:
                filters.append("d.user_id = :user_id")
                params["user_id"] = user_id
            
            if conversation_id:
                filters.append("d.conversation_id = :conversation_id")
                params["conversation_id"] = conversation_id
            
            if content_type:
                filters.append("d.content_type = :content_type")
                params["content_type"] = content_type
            
            if time_range and time_range != "all":
                time_filter = self._get_time_filter(time_range)
                if time_filter:
                    filters.append(f"dc.created_at >= {time_filter}")
            
            # Aplicar filtros a la query
            if filters:
                base_query += " AND " + " AND ".join(filters)
            
            # Ordenar por similitud y limitar
            base_query += """
                ORDER BY dc.embedding <=> :query_embedding
                LIMIT :limit
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(base_query), params)
                results = []
                
                for row in result.fetchall():
                    results.append({
                        "id": str(row[1]),
                        "content": row[2],
                        "title": row[3],
                        "content_type": row[4],
                        "metadata": json.loads(row[5]) if row[5] else {},
                        "similarity_score": float(row[6]),
                        "created_at": row[7].isoformat() if row[7] else None,
                        "result_type": "document_chunk"
                    })
                
                logger.info(f"Búsqueda semántica completada: {len(results)} resultados")
                return results
                
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            raise
    
    async def _chunk_document(self, content: str, strategy: str) -> List[Chunk]:
        """Genera chunks de un documento usando DocumentChunker"""
        # Usar el chunker existente
        if strategy == "recursive":
            chunks = self.chunker.chunk_recursive(content, chunk_size=500, chunk_overlap=50)
        elif strategy == "paragraph":
            chunks = self.chunker.chunk_by_paragraphs(content)
        elif strategy == "sentence":
            chunks = self.chunker.chunk_by_sentences(content)
        else:
            # Fallback a recursive
            chunks = self.chunker.chunk_recursive(content, chunk_size=500, chunk_overlap=50)
        
        # Convertir a objetos Chunk
        chunk_objects = []
        for i, chunk in enumerate(chunks):
            chunk_obj = Chunk(
                id=f"chunk_{i}",
                content=chunk["content"],
                start_position=chunk["start_position"],
                end_position=chunk["end_position"],
                token_count=chunk.get("token_count", len(chunk["content"].split())),
                metadata=chunk.get("metadata", {})
            )
            chunk_objects.append(chunk_obj)
        
        return chunk_objects
    
    async def _get_or_generate_embedding(self, content: str) -> List[float]:
        """
        Obtiene embedding del cache o genera uno nuevo
        
        Args:
            content: Contenido para generar embedding
            
        Returns:
            Lista de embeddings (384 dimensiones)
        """
        # Verificar cache
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self.embedding_cache:
            return self.embedding_cache[content_hash]
        
        # Generar nuevo embedding
        try:
            embedding = await self.embedding_service.generate_embeddings([content])
            if embedding and len(embedding) > 0:
                vector = embedding[0]
                
                # Agregar al cache
                if len(self.embedding_cache) < self.cache_size_limit:
                    self.embedding_cache[content_hash] = vector
                
                return vector
            else:
                # Fallback a embedding determinístico
                logger.warning("Embedding service falló, usando embedding determinístico")
                return self._generate_fallback_embedding(content)
                
        except Exception as e:
            logger.warning(f"Error generando embedding real: {e}, usando fallback")
            return self._generate_fallback_embedding(content)
    
    def _generate_fallback_embedding(self, content: str) -> List[float]:
        """Genera embedding determinístico como fallback"""
        seed = int(hashlib.md5(content.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(seed)
        embedding = np.random.normal(0, 1, 384).tolist()
        
        # Normalizar
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = (embedding / norm).tolist()
        
        return embedding
    
    def _get_time_filter(self, time_range: str) -> str:
        """Convierte rango temporal a filtro SQL"""
        if time_range == "1h":
            return "CURRENT_TIMESTAMP - INTERVAL '1 hour'"
        elif time_range == "1d":
            return "CURRENT_TIMESTAMP - INTERVAL '1 day'"
        elif time_range == "1w":
            return "CURRENT_TIMESTAMP - INTERVAL '1 week'"
        elif time_range == "1m":
            return "CURRENT_TIMESTAMP - INTERVAL '1 month'"
        else:
            return None
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del VectorStore"""
        try:
            with self.engine.connect() as conn:
                # Contar documentos y chunks
                doc_count = conn.execute(text("SELECT COUNT(*) FROM documents")).fetchone()[0]
                chunk_count = conn.execute(text("SELECT COUNT(*) FROM document_chunks")).fetchone()[0]
                message_count = conn.execute(text("SELECT COUNT(*) FROM messages")).fetchone()[0]
                
                # Espacio usado (aproximado)
                size_result = conn.execute(text("""
                    SELECT 
                        pg_size_pretty(pg_total_relation_size('documents')) as docs_size,
                        pg_size_pretty(pg_total_relation_size('document_chunks')) as chunks_size,
                        pg_size_pretty(pg_total_relation_size('messages')) as messages_size
                """)).fetchone()
                
                return {
                    "total_documents": doc_count,
                    "total_chunks": chunk_count,
                    "total_messages": message_count,
                    "cache_size": len(self.embedding_cache),
                    "database_size": {
                        "documents": size_result[0] if size_result else "N/A",
                        "chunks": size_result[1] if size_result else "N/A", 
                        "messages": size_result[2] if size_result else "N/A"
                    },
                    "status": "healthy"
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"status": "error", "error": str(e)}
    
    async def close(self):
        """Cierra conexiones del VectorStore"""
        if self.engine:
            self.engine.dispose()
            logger.info("VectorStore cerrado")