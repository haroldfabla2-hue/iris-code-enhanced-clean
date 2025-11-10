"""
Agente Memory Manager - Gestiona memoria semántica RAG
Responsable de almacenar y recuperar conocimiento con embeddings
"""
from typing import List, Dict, Any, Optional, Tuple
import json
import hashlib
from datetime import datetime
import os
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        psycopg2 = None
# Importación lazy de sqlalchemy para evitar problemas de importación
import numpy as np
import httpx
import asyncio

from .base import BaseAgent
from ..models import AgentMessage, AgentResponse, MessageStatus
from ..services.embedding_service import EmbeddingService, initialize_embedding_service
from ..services.chunking_service import DocumentChunker, ChunkingStrategy


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
            from sqlalchemy import create_engine, text
            
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
                
        except (ModuleNotFoundError, ImportError) as e:
            self.logger.warning(f"SQLAlchemy no disponible: {str(e)} - usando cache local")
            self.db_engine = None
        except Exception as e:
            self.logger.warning(f"No se pudo conectar a PostgreSQL: {str(e)} - usando cache local")
            self.db_engine = None
    
    def _create_memory_tables(self):
        """Crea tablas necesarias para la memoria si no existen"""
        try:
            from sqlalchemy import text
            with self.db_engine.connect() as conn:
                # Habilitar extensión pgvector
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                
                # Tabla para embeddings
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS memory_embeddings (
                        id VARCHAR(255) PRIMARY KEY,
                        content JSONB NOT NULL,
                        embedding vector(768),
                        metadata JSONB,
                        memory_type VARCHAR(50) DEFAULT 'knowledge',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        version VARCHAR(20) DEFAULT 'v1'
                    )
                """))
                
                # Tabla para snapshots
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS memory_snapshots (
                        id VARCHAR(255) PRIMARY KEY,
                        conversation_id VARCHAR(255),
                        phase VARCHAR(100),
                        state JSONB,
                        checksum VARCHAR(64),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Índices para búsqueda vectorial
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_memory_embeddings_vector 
                    ON memory_embeddings USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_memory_embeddings_type 
                    ON memory_embeddings(memory_type)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_memory_embeddings_created 
                    ON memory_embeddings(created_at)
                """))
                
                conn.commit()
                self.logger.info("Tablas de memoria creadas/verificadas")
                
        except Exception as e:
            self.logger.error(f"Error creando tablas de memoria: {str(e)}")
            raise
    
    def get_capabilities(self) -> List[str]:
        return [
            "knowledge_storage",
            "context_retrieval",
            "snapshot_management",
            "semantic_search",
            "memory_synthesis",
            "insight_storage",
            "working_memory",
            "state_checkpoints"
        ]
    
    async def store_document(
        self,
        content: str,
        source_info: Dict[str, Any],
        strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC,
        max_tokens: int = 500,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Almacena un documento completo con chunking inteligente
        
        Args:
            content: Contenido del documento
            source_info: Información de la fuente (title, url, type, etc.)
            strategy: Estrategia de chunking a usar
            max_tokens: Máximo tokens por chunk
            **kwargs: Argumentos adicionales para chunking
            
        Returns:
            Dict con resultado del almacenamiento
        """
        try:
            if not self.chunker:
                return {
                    "success": False,
                    "error": "Servicio de chunking no disponible",
                    "operation": "store_document"
                }
            
            # Generar chunks del documento
            chunks = self.chunker.chunk_document(
                text=content,
                strategy=strategy,
                max_tokens=max_tokens,
                **kwargs
            )
            
            if not chunks:
                return {
                    "success": False,
                    "error": "No se pudieron generar chunks del documento",
                    "operation": "store_document"
                }
            
            stored_chunks = []
            
            # Almacenar cada chunk
            for i, chunk in enumerate(chunks):
                chunk_content = {
                    "text": chunk.content,
                    "chunk_id": chunk.id,
                    "chunk_index": i,
                    "source_info": source_info,
                    "metadata": {
                        **source_info,
                        "chunk_metadata": chunk.metadata,
                        "total_chunks": len(chunks)
                    }
                }
                
                # Almacenar chunk en memoria
                result = await self._store_memory({
                    "content": chunk_content,
                    "metadata": {
                        "source_type": "document_chunk",
                        "original_source": source_info,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    },
                    "memory_type": "document"
                })
                
                stored_chunks.append(result)
            
            # Obtener estadísticas del chunking
            stats = self.chunker.get_chunking_stats(chunks, content)
            
            self.logger.info(f"Documento almacenado: {source_info.get('title', 'Sin título')} en {len(chunks)} chunks")
            
            return {
                "success": True,
                "operation": "store_document",
                "source_info": source_info,
                "total_chunks": len(chunks),
                "chunks": stored_chunks,
                "chunking_stats": stats,
                "strategy_used": strategy.value,
                "stored_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.exception(f"Error almacenando documento: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "operation": "store_document",
                "source_info": source_info
            }

    async def search_in_memory(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        source_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Búsqueda avanzada en memoria con filtros semánticos
        
        Args:
            query: Consulta de búsqueda
            limit: Número máximo de resultados
            filters: Filtros adicionales
            source_type: Filtrar por tipo de fuente
            
        Returns:
            Dict con resultados de búsqueda
        """
        try:
            search_filters = filters or {}
            if source_type:
                search_filters["source_type"] = source_type
            
            # Realizar búsqueda semántica
            results = await self.retrieve_relevant(
                query=query,
                limit=limit,
                memory_type=search_filters.get("memory_type"),
                conversation_id=search_filters.get("conversation_id")
            )
            
            if not results.get("success"):
                return results
            
            # Filtrar y rerankear resultados
            filtered_results = self._filter_search_results(results.get("results", []), search_filters)
            
            # Reranking avanzado si hay suficientes resultados
            if len(filtered_results) > limit:
                filtered_results = self._rerank_search_results(filtered_results, query)[:limit]
            
            return {
                "success": True,
                "query": query,
                "total_results": len(filtered_results),
                "results": filtered_results,
                "search_metadata": {
                    "filters_applied": search_filters,
                    "search_type": "semantic",
                    "reranking_applied": len(filtered_results) > limit
                },
                "search_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.exception(f"Error en búsqueda avanzada: {str(e)}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "results": []
            }

    async def get_memory_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas detalladas de la memoria
        
        Returns:
            Dict con estadísticas de memoria
        """
        try:
            stats = {
                "total_memories": 0,
                "memories_by_type": {},
                "memories_by_source": {},
                "embedding_stats": {},
                "cache_stats": {},
                "database_stats": {}
            }
            
            # Estadísticas del cache local
            if self.memory_cache:
                stats["cache_stats"] = {
                    "cached_items": len(self.memory_cache),
                    "memory_types": {}
                }
                
                for item in self.memory_cache.values():
                    mem_type = item.get("metadata", {}).get("memory_type", "unknown")
                    stats["cache_stats"]["memory_types"][mem_type] = \
                        stats["cache_stats"]["memory_types"].get(mem_type, 0) + 1
            
            # Estadísticas del servicio de embeddings
            if self.embedding_service:
                stats["embedding_stats"] = await self.embedding_service.get_model_info()
            
            # Estadísticas de base de datos si está disponible
            if self.db_engine:
                stats["database_stats"] = await self._get_database_stats()
            
            return {
                "success": True,
                "stats": stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de memoria: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stats": {}
            }

    async def store_insight(
        self, 
        insight: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Almacena un insight en memoria vectorial
        
        Args:
            insight: Texto del insight a almacenar
            metadata: Metadatos adicionales (tags, source, context, etc.)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            content = {
                "text": insight,
                "type": "insight"
            }
            
            if metadata:
                content.update(metadata)
            
            result = await self._store_memory({
                "content": content,
                "metadata": metadata or {},
                "memory_type": "insight"
            })
            
            self.logger.info(f"Insight almacenado: {result.get('memory_id')}")
            return result
            
        except Exception as e:
            self.logger.exception(f"Error almacenando insight: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "operation": "store_insight"
            }
    
    async def retrieve_relevant(
        self, 
        query: str, 
        limit: int = 5,
        memory_type: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Recupera conocimiento relevante usando búsqueda semántica
        
        Args:
            query: Consulta para buscar
            limit: Número máximo de resultados
            memory_type: Filtrar por tipo de memoria
            conversation_id: Filtrar por ID de conversación
            
        Returns:
            Dict con resultados de la búsqueda
        """
        try:
            filters = {}
            if memory_type:
                filters["memory_type"] = memory_type
            if conversation_id:
                filters["conversation_id"] = conversation_id
            
            result = await self._retrieve_memory({
                "query": query,
                "filters": filters,
                "top_k": limit
            })
            
            self.logger.info(f"Búsqueda completada: {result.get('num_results')} resultados")
            return result
            
        except Exception as e:
            self.logger.exception(f"Error en búsqueda semántica: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": [],
                "num_results": 0
            }
    
    async def update_working_memory(
        self, 
        session_id: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza el contexto de memoria de trabajo
        
        Args:
            session_id: ID de la sesión
            context: Contexto actual de la conversación
            
        Returns:
            Dict con resultado de la actualización
        """
        try:
            # Almacenar contexto como memoria temporal
            memory_id = f"working_{session_id}"
            
            # Generar embedding del contexto
            embedding = await self._generate_embedding(context)
            
            # Preparar entrada de memoria de trabajo
            memory_entry = {
                "id": memory_id,
                "content": context,
                "embedding": embedding,
                "metadata": {
                    "session_id": session_id,
                    "memory_type": "working_memory",
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "v1"
                }
            }
            
            # Actualizar en base de datos si está disponible
            if self.db_engine:
                await self._store_in_database(memory_entry)
                storage_location = "database"
            else:
                # Actualizar en cache
                self.memory_cache[memory_id] = memory_entry
                storage_location = "cache"
            
            self.logger.info(f"Memoria de trabajo actualizada: {memory_id} en {storage_location}")
            
            return {
                "success": True,
                "session_id": session_id,
                "storage_location": storage_location,
                "memory_id": memory_id,
                "updated_at": memory_entry["metadata"]["created_at"],
                "operation": "update_working_memory"
            }
            
        except Exception as e:
            self.logger.exception(f"Error actualizando memoria de trabajo: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "operation": "update_working_memory"
            }
    
    async def checkpoint_state(
        self, 
        agent_id: str, 
        state: Dict[str, Any],
        conversation_id: Optional[str] = None,
        phase: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Guarda un checkpoint del estado del agente
        
        Args:
            agent_id: ID del agente
            state: Estado actual del agente
            conversation_id: ID de la conversación (opcional)
            phase: Fase actual de ejecución (opcional)
            
        Returns:
            Dict con resultado del checkpoint
        """
        try:
            # Crear snapshot del estado
            checkpoint_payload = {
                "state": {
                    "agent_id": agent_id,
                    "state": state,
                    "conversation_id": conversation_id,
                    "phase": phase or "unknown",
                    "timestamp": datetime.utcnow().isoformat()
                },
                "conversation_id": conversation_id or "unknown",
                "phase": phase or "unknown"
            }
            
            result = await self._create_snapshot(checkpoint_payload)
            
            self.logger.info(f"Checkpoint creado: {result.get('snapshot_id')} para agente {agent_id}")
            return result
            
        except Exception as e:
            self.logger.exception(f"Error creando checkpoint: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "operation": "checkpoint_state"
            }
    
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """
        Procesa mensaje gestionando memoria
        """
        self.log_trace("memory_manager_start", {
            "message_id": message.message_id
        })
        
        try:
            operation = message.payload.get("operation", "store")
            
            if operation == "store":
                result = await self._store_memory(message.payload)
            elif operation == "retrieve":
                result = await self._retrieve_memory(message.payload)
            elif operation == "snapshot":
                result = await self._create_snapshot(message.payload)
            elif operation == "synthesis":
                result = await self._synthesize_knowledge(message.payload)
            else:
                raise ValueError(f"Operación no soportada: {operation}")
            
            self.log_trace("memory_manager_complete", {
                "message_id": message.message_id,
                "operation": operation
            })
            
            return AgentResponse(
                message_id=f"resp_{message.message_id}",
                original_message_id=message.message_id,
                agent_id=self.agent_id,
                status=MessageStatus.DONE,
                result=result
            )
            
        except Exception as e:
            self.logger.exception("Error en Memory Manager")
            raise
    
    async def _store_memory(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Almacena conocimiento en memoria vectorial"""
        
        content = payload.get("content", {})
        metadata = payload.get("metadata", {})
        memory_type = payload.get("memory_type", "knowledge")
        
        # Generar ID único
        memory_id = self._generate_memory_id(content)
        
        try:
            # Generar embedding del contenido
            embedding = await self._generate_embedding(content)
            
            # Crear entrada de memoria
            memory_entry = {
                "id": memory_id,
                "content": content,
                "embedding": embedding,
                "metadata": {
                    **metadata,
                    "memory_type": memory_type,
                    "created_at": datetime.utcnow().isoformat(),
                    "version": payload.get("context_version", "v1")
                }
            }
            
            # Almacenar en base de datos si está disponible
            if self.db_engine:
                await self._store_in_database(memory_entry)
                stored_location = "database"
            else:
                # Fallback a cache local
                self.memory_cache[memory_id] = memory_entry
                stored_location = "cache"
            
            self.logger.info(f"Memoria almacenada: {memory_id} en {stored_location}")
            
            return {
                "operation": "store",
                "memory_id": memory_id,
                "memory_type": memory_type,
                "success": True,
                "stored_at": memory_entry["metadata"]["created_at"],
                "storage_location": stored_location
            }
            
        except Exception as e:
            self.logger.exception(f"Error almacenando memoria {memory_id}: {str(e)}")
            return {
                "operation": "store",
                "memory_id": memory_id,
                "memory_type": memory_type,
                "success": False,
                "error": str(e)
            }
    
    async def _store_in_database(self, memory_entry: Dict[str, Any]):
        """Almacena entrada de memoria en PostgreSQL"""
        try:
            with self.db_engine.connect() as conn:
                # Convertir embedding a string para PostgreSQL
                embedding_str = "[" + ",".join(map(str, memory_entry["embedding"])) + "]"
                
                conn.execute(text("""
                    INSERT INTO memory_embeddings 
                    (id, content, embedding, metadata, memory_type, created_at, version)
                    VALUES (:id, :content, :embedding, :metadata, :memory_type, :created_at, :version)
                    ON CONFLICT (id) 
                    DO UPDATE SET 
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                """), {
                    "id": memory_entry["id"],
                    "content": json.dumps(memory_entry["content"]),
                    "embedding": embedding_str,
                    "metadata": json.dumps(memory_entry["metadata"]),
                    "memory_type": memory_entry["metadata"].get("memory_type", "knowledge"),
                    "created_at": memory_entry["metadata"]["created_at"],
                    "version": memory_entry["metadata"].get("version", "v1")
                })
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error almacenando en base de datos: {str(e)}")
            raise
    
    async def _retrieve_memory(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recupera conocimiento relevante (RAG)"""
        
        query = payload.get("query", "")
        filters = payload.get("filters", {})
        top_k = payload.get("top_k", 5)
        
        try:
            # Generar embedding de la query
            query_embedding = await self._generate_embedding(query)
            
            # Buscar en vector store
            if self.db_engine:
                results = await self._semantic_search_database(
                    query_embedding,
                    filters,
                    top_k
                )
            else:
                # Fallback a búsqueda en cache
                results = await self._semantic_search_cache(
                    query_embedding,
                    filters,
                    top_k
                )
            
            # Reranking ligero si hay muchos resultados
            if len(results) > top_k:
                results = self._rerank_results(results, query)[:top_k]
            
            return {
                "operation": "retrieve",
                "query": query,
                "num_results": len(results),
                "results": results,
                "relevance_scores": [r.get("score", 0.0) for r in results],
                "search_type": "database" if self.db_engine else "cache"
            }
            
        except Exception as e:
            self.logger.exception(f"Error recuperando memoria: {str(e)}")
            return {
                "operation": "retrieve",
                "query": query,
                "num_results": 0,
                "results": [],
                "relevance_scores": [],
                "error": str(e)
            }
    
    async def _semantic_search_database(
        self,
        query_embedding: List[float],
        filters: Dict[str, Any],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Búsqueda semántica en PostgreSQL usando pgvector"""
        try:
            from sqlalchemy import text
            with self.db_engine.connect() as conn:
                # Construir query SQL para búsqueda vectorial
                embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
                
                # Construir filtros WHERE
                where_clause = "WHERE 1=1"
                params = {"embedding": embedding_str, "limit": top_k}
                
                if filters:
                    if filters.get("memory_type"):
                        where_clause += " AND memory_type = :memory_type"
                        params["memory_type"] = filters["memory_type"]
                    
                    if filters.get("conversation_id"):
                        where_clause += " AND metadata->>'conversation_id' = :conversation_id"
                        params["conversation_id"] = filters["conversation_id"]
                
                # Query de búsqueda vectorial con pgvector
                query_sql = f"""
                    SELECT 
                        id,
                        content,
                        metadata,
                        memory_type,
                        created_at,
                        1 - (embedding <=> :embedding) as similarity
                    FROM memory_embeddings
                    {where_clause}
                    ORDER BY embedding <=> :embedding
                    LIMIT :limit
                """
                
                result = conn.execute(text(query_sql), params)
                rows = result.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        "memory_id": row.id,
                        "content": json.loads(row.content) if isinstance(row.content, str) else row.content,
                        "metadata": json.loads(row.metadata) if isinstance(row.metadata, str) else row.metadata,
                        "memory_type": row.memory_type,
                        "created_at": row.created_at.isoformat() if hasattr(row.created_at, 'isoformat') else str(row.created_at),
                        "score": float(row.similarity)
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Error en búsqueda vectorial: {str(e)}")
            return []
    
    async def _semantic_search_cache(
        self,
        query_embedding: List[float],
        filters: Dict[str, Any],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Búsqueda semántica en cache local (fallback)"""
        results = []
        
        for memory_id, memory_entry in self.memory_cache.items():
            if memory_id.startswith("snapshot_"):
                continue
            
            # Aplicar filtros
            if filters:
                metadata = memory_entry.get("metadata", {})
                if not all(metadata.get(k) == v for k, v in filters.items()):
                    continue
            
            # Calcular similitud (mock - cosine similarity)
            try:
                query_vec = np.array(query_embedding)
                memory_vec = np.array(memory_entry["embedding"])
                
                # Cosine similarity
                similarity = np.dot(query_vec, memory_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(memory_vec))
                similarity = float(similarity)
                
            except Exception:
                similarity = 0.5  # Score neutro en caso de error
            
            results.append({
                "memory_id": memory_id,
                "content": memory_entry["content"],
                "metadata": memory_entry["metadata"],
                "score": similarity
            })
        
        # Ordenar por score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
    
    async def _create_snapshot(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crea snapshot del estado actual"""
        
        state = payload.get("state", {})
        conversation_id = payload.get("conversation_id", "unknown")
        phase = payload.get("phase", "unknown")
        
        snapshot_id = f"snap_{hashlib.md5(str(state).encode()).hexdigest()[:12]}"
        checksum = self._compute_checksum(state)
        timestamp = datetime.utcnow().isoformat()
        
        snapshot = {
            "snapshot_id": snapshot_id,
            "conversation_id": conversation_id,
            "phase": phase,
            "state": state,
            "timestamp": timestamp,
            "checksum": checksum
        }
        
        try:
            # Almacenar snapshot
            if self.db_engine:
                await self._store_snapshot_in_database(snapshot)
                storage_location = "database"
            else:
                # Fallback a cache local
                self.memory_cache[f"snapshot_{snapshot_id}"] = snapshot
                storage_location = "cache"
            
            self.logger.info(f"Snapshot creado: {snapshot_id} en {storage_location}")
            
            return {
                "operation": "snapshot",
                "snapshot_id": snapshot_id,
                "phase": phase,
                "success": True,
                "storage_location": storage_location,
                "timestamp": timestamp
            }
            
        except Exception as e:
            self.logger.exception(f"Error creando snapshot {snapshot_id}: {str(e)}")
            return {
                "operation": "snapshot",
                "snapshot_id": snapshot_id,
                "phase": phase,
                "success": False,
                "error": str(e)
            }
    
    async def _store_snapshot_in_database(self, snapshot: Dict[str, Any]):
        """Almacena snapshot en PostgreSQL"""
        try:
            with self.db_engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO memory_snapshots 
                    (id, conversation_id, phase, state, checksum, created_at)
                    VALUES (:id, :conversation_id, :phase, :state, :checksum, :created_at)
                    ON CONFLICT (id) 
                    DO UPDATE SET 
                        state = EXCLUDED.state,
                        checksum = EXCLUDED.checksum,
                        created_at = EXCLUDED.created_at
                """), {
                    "id": snapshot["snapshot_id"],
                    "conversation_id": snapshot["conversation_id"],
                    "phase": snapshot["phase"],
                    "state": json.dumps(snapshot["state"]),
                    "checksum": snapshot["checksum"],
                    "created_at": snapshot["timestamp"]
                })
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error almacenando snapshot en base de datos: {str(e)}")
            raise
    
    async def _synthesize_knowledge(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sintetiza conocimiento de múltiples fuentes"""
        
        inputs = payload.get("inputs", [])
        synthesis_type = payload.get("synthesis_type", "summary")
        
        if synthesis_type == "summary":
            result = await self._synthesize_summary(inputs)
        elif synthesis_type == "insights":
            result = await self._synthesize_insights(inputs)
        else:
            result = await self._synthesize_generic(inputs)
        
        # Almacenar síntesis como nueva memoria
        if result.get("content"):
            await self._store_memory({
                "content": result["content"],
                "metadata": {
                    "synthesis_type": synthesis_type,
                    "num_sources": len(inputs)
                },
                "memory_type": "synthesis"
            })
        
        return result
    
    async def _synthesize_summary(
        self,
        inputs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Sintetiza un resumen de múltiples inputs"""
        
        # Construir prompt para LLM
        combined_content = "\n\n".join([
            f"Fuente {i+1}: {json.dumps(inp, ensure_ascii=False)}"
            for i, inp in enumerate(inputs)
        ])
        
        prompt = f"""Sintetiza la siguiente información en un resumen coherente:

{combined_content}

Proporciona:
1. Resumen ejecutivo (2-3 frases)
2. Puntos clave (máximo 5)
3. Conclusiones principales
"""
        
        synthesis = await self.call_llm(prompt, temperature=0.5)
        
        return {
            "synthesis_type": "summary",
            "content": synthesis,
            "num_sources": len(inputs),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _synthesize_insights(
        self,
        inputs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extrae insights de múltiples fuentes"""
        
        prompt = f"""Extrae los insights más valiosos de esta información:

{json.dumps(inputs, indent=2, ensure_ascii=False)}

Para cada insight:
1. Descripción concisa
2. Nivel de confianza (0-1)
3. Fuentes que lo respaldan
"""
        
        insights_text = await self.call_llm(prompt, temperature=0.6)
        
        return {
            "synthesis_type": "insights",
            "content": insights_text,
            "num_sources": len(inputs),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _synthesize_generic(
        self,
        inputs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Síntesis genérica"""
        
        return {
            "synthesis_type": "generic",
            "content": json.dumps(inputs, indent=2, ensure_ascii=False),
            "num_sources": len(inputs),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _generate_embedding(
        self,
        content: Any
    ) -> List[float]:
        """Genera embedding vectorial del contenido usando HuggingFace embeddings"""
        
        text = json.dumps(content) if isinstance(content, dict) else str(content)
        
        # Intentar usar servicio de embeddings de HuggingFace
        if self.embedding_service:
            try:
                embedding = await self.embedding_service.generate_embedding(text)
                self.logger.debug(f"Embedding generado con HuggingFace ({len(embedding)} dims)")
                return embedding
            except Exception as e:
                self.logger.warning(f"Error generando embedding con HuggingFace: {str(e)}")
        
        # Fallback a OpenRouter si está disponible
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://agente.minimax.io",
                    "X-Title": "Memory Manager"
                }
                
                payload = {
                    "model": "openai/text-embedding-ada-002",
                    "input": text[:8000]  # Limitar longitud
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/embeddings",
                        headers=headers,
                        json=payload
                    )
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    if "data" in data and len(data["data"]) > 0:
                        embedding = data["data"][0]["embedding"]
                        self.logger.debug(f"Embedding generado con OpenRouter ({len(embedding)} dims)")
                        return embedding
                        
        except Exception as e:
            self.logger.warning(f"Error generando embedding con OpenRouter: {str(e)}")
        
        # Último fallback: embedding mock determinístico
        self.logger.warning("Usando embedding mock como último recurso")
        return self._generate_mock_embedding(text)
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Genera embedding mock determinístico basado en hash"""
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        
        # Generar embedding pseudo-aleatorio determinístico
        np.random.seed(seed)
        embedding = np.random.normal(0, 1, 768).tolist()
        
        # Normalizar para que tenga norma 1
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = (embedding / norm).tolist()
        
        return embedding
    
    def _rerank_results(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """Reranking ligero de resultados usando similitud textual"""
        
        if not results:
            return results
        
        try:
            # Calcular score de relevancia textual
            query_words = set(query.lower().split())
            
            for result in results:
                content_text = ""
                if isinstance(result.get("content"), dict):
                    # Extraer texto del contenido JSON
                    content_text = json.dumps(result["content"])
                else:
                    content_text = str(result.get("content", ""))
                
                content_words = set(content_text.lower().split())
                
                # Calcular overlap de palabras
                overlap = len(query_words.intersection(content_words))
                query_len = len(query_words)
                content_len = len(content_words)
                
                if query_len > 0 and content_len > 0:
                    # Score de relevancia textual
                    text_score = (overlap / query_len) * (overlap / content_len) * 2
                else:
                    text_score = 0.0
                
                # Combinar con score de similitud vectorial
                vector_score = result.get("score", 0.0)
                combined_score = (vector_score * 0.7) + (text_score * 0.3)
                
                result["rerank_score"] = combined_score
            
            # Reordenar por score combinado
            reranked = sorted(results, key=lambda x: x.get("rerank_score", x.get("score", 0.0)), reverse=True)
            
            self.logger.debug(f"Reranking completado: {len(reranked)} resultados reordenados")
            return reranked
            
        except Exception as e:
            self.logger.warning(f"Error en reranking: {str(e)} - retornando resultados originales")
            return results
    
    def _generate_memory_id(self, content: Any) -> str:
        """Genera ID único para memoria"""
        
        content_str = json.dumps(content, sort_keys=True)
        hash_val = hashlib.md5(content_str.encode()).hexdigest()[:12]
        
        return f"mem_{hash_val}"
    
    def _filter_search_results(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filtra resultados de búsqueda según criterios específicos"""
        
        filtered = []
        
        for result in results:
            metadata = result.get("metadata", {})
            
            # Aplicar filtros
            include = True
            
            # Filtro por tipo de fuente
            if filters.get("source_type"):
                result_source_type = metadata.get("source_type")
                if result_source_type != filters["source_type"]:
                    include = False
            
            # Filtro por usuario
            if filters.get("user_id"):
                result_user_id = metadata.get("user_id")
                if result_user_id != filters["user_id"]:
                    include = False
            
            # Filtro por conversación
            if filters.get("conversation_id"):
                result_conv_id = metadata.get("conversation_id")
                if result_conv_id != filters["conversation_id"]:
                    include = False
            
            # Filtro por tags
            if filters.get("tags"):
                result_tags = set(metadata.get("tags", []))
                filter_tags = set(filters["tags"])
                if not result_tags.intersection(filter_tags):
                    include = False
            
            if include:
                filtered.append(result)
        
        return filtered
    
    def _rerank_search_results(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """Reranking avanzado de resultados de búsqueda"""
        
        if not results:
            return results
        
        try:
            query_words = set(query.lower().split())
            
            for result in results:
                content = result.get("content", {})
                
                # Extraer texto del contenido
                if isinstance(content, dict):
                    text = content.get("text", json.dumps(content))
                else:
                    text = str(content)
                
                content_words = set(text.lower().split())
                
                # Calcular scores múltiples
                vector_score = result.get("score", 0.0)
                
                # Score de similitud textual
                if query_words and content_words:
                    overlap = len(query_words.intersection(content_words))
                    text_score = overlap / len(query_words.union(content_words))
                else:
                    text_score = 0.0
                
                # Score de novedad (evitar contenido muy similar)
                novelty_score = self._calculate_novelty_score(result, results)
                
                # Score de autoridad (basado en metadatos)
                authority_score = self._calculate_authority_score(result)
                
                # Combinar scores con pesos
                combined_score = (
                    vector_score * 0.4 +      # Similitud vectorial
                    text_score * 0.3 +       # Similitud textual
                    novelty_score * 0.2 +    # Novedad
                    authority_score * 0.1    # Autoridad
                )
                
                result["combined_score"] = combined_score
                result["score_breakdown"] = {
                    "vector_score": vector_score,
                    "text_score": text_score,
                    "novelty_score": novelty_score,
                    "authority_score": authority_score
                }
            
            # Reordenar por score combinado
            reranked = sorted(
                results, 
                key=lambda x: x.get("combined_score", 0.0), 
                reverse=True
            )
            
            self.logger.debug(f"Reranking completado: {len(reranked)} resultados reordenados")
            return reranked
            
        except Exception as e:
            self.logger.warning(f"Error en reranking avanzado: {str(e)} - retornando resultados originales")
            return results
    
    def _calculate_novelty_score(self, result: Dict[str, Any], all_results: List[Dict[str, Any]]) -> float:
        """Calcula score de novedad para evitar contenido muy similar"""
        
        try:
            content = result.get("content", {})
            if isinstance(content, dict):
                text = content.get("text", "")
            else:
                text = str(content)
            
            if not text:
                return 0.0
            
            # Contar cuántas veces aparece contenido similar
            similarity_count = 0
            text_lower = text.lower()
            
            for other_result in all_results:
                if other_result == result:
                    continue
                
                other_content = other_result.get("content", {})
                if isinstance(other_content, dict):
                    other_text = other_content.get("text", "")
                else:
                    other_text = str(other_content)
                
                if not other_text:
                    continue
                
                other_text_lower = other_text.lower()
                
                # Verificar superposición significativa de palabras
                words_text = set(text_lower.split())
                words_other = set(other_text_lower.split())
                
                if len(words_text) > 0:
                    overlap_ratio = len(words_text.intersection(words_other)) / len(words_text)
                    if overlap_ratio > 0.5:  # 50% de superposición
                        similarity_count += 1
            
            # Score de novedad: inversamente proporcional a similitudes
            novelty_score = 1.0 / (1.0 + similarity_count)
            return novelty_score
            
        except Exception:
            return 0.5  # Score neutro en caso de error
    
    def _calculate_authority_score(self, result: Dict[str, Any]) -> float:
        """Calcula score de autoridad basado en metadatos"""
        
        score = 0.5  # Score base
        
        try:
            metadata = result.get("metadata", {})
            
            # Bonus por fuente confiable
            source_type = metadata.get("source_type")
            if source_type == "document":
                score += 0.2
            elif source_type == "manual_entry":
                score += 0.1
            
            # Bonus por metadatos ricos
            has_tags = bool(metadata.get("tags"))
            has_source_info = bool(metadata.get("source_info"))
            
            if has_tags:
                score += 0.1
            if has_source_info:
                score += 0.1
            
            # Bonus por ser un insight
            if "insight" in metadata.get("memory_type", ""):
                score += 0.1
            
            # Penalización por metadata escasa
            if not has_tags and not has_source_info:
                score -= 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5
    
    async def _get_database_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la base de datos"""
        try:
            from sqlalchemy import text
            with self.db_engine.connect() as conn:
                # Contar memorias por tipo
                result = conn.execute(text("""
                    SELECT memory_type, COUNT(*) as count
                    FROM memory_embeddings
                    GROUP BY memory_type
                """))
                
                memories_by_type = {row.memory_type: row.count for row in result}
                
                # Contar total de memorias
                result = conn.execute(text("SELECT COUNT(*) as total FROM memory_embeddings"))
                total_memories = result.fetchone().total
                
                # Estadísticas de snapshots
                result = conn.execute(text("SELECT COUNT(*) as total FROM memory_snapshots"))
                total_snapshots = result.fetchone().total
                
                return {
                    "total_memories": total_memories,
                    "total_snapshots": total_snapshots,
                    "memories_by_type": memories_by_type,
                    "database_connected": True
                }
                
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de base de datos: {str(e)}")
            return {
                "database_connected": False,
                "error": str(e)
            }

    def _compute_checksum(self, state: Dict[str, Any]) -> str:
        """Computa checksum del estado"""
        
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]
