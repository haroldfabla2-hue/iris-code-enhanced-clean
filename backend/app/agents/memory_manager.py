"""
Agente Memory Manager con VectorStore Real para RAG
Integra con PostgreSQL + pgvector para almacenamiento vectorial
"""
from typing import List, Dict, Any, Optional
import json
import hashlib
from datetime import datetime
import logging
import numpy as np
from sqlalchemy import text

from .base import BaseAgent
from ..models import AgentMessage, AgentResponse, MessageStatus
from ..services.vector_store import VectorStore
from ..services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class MemoryManagerAgent(BaseAgent):
    """
    Agente Memory Manager: Gestión de memoria semántica con VectorStore real
    
    Funcionalidades:
    - Almacenamiento de documentos y conversaciones
    - Búsqueda semántica con pgvector
    - Gestión de contexto para agentes
    - Cache de embeddings frecuentes
    """
    
    def __init__(self, llm_client: Any = None, vector_store: VectorStore = None, embedding_service: EmbeddingService = None):
        super().__init__(
            agent_id="memory_manager",
            llm_client=llm_client
        )
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.memory_cache = {}  # Cache temporal de conversaciones
        self.conversation_cache = {}  # Cache de mensajes por conversación
        self.max_cache_size = 1000
        
    def get_capabilities(self) -> List[str]:
        return [
            "knowledge_storage",
            "context_retrieval", 
            "semantic_search",
            "memory_synthesis",
            "conversation_management",
            "document_indexing"
        ]
    
    async def store_knowledge(
        self,
        title: str,
        content: str,
        content_type: str = "text",
        user_id: str = None,
        conversation_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Almacena conocimiento en el VectorStore
        
        Args:
            title: Título del documento/conocimiento
            content: Contenido del conocimiento
            content_type: Tipo de contenido
            user_id: ID del usuario
            conversation_id: ID de conversación
            metadata: Metadatos adicionales
            
        Returns:
            ID del documento almacenado
        """
        try:
            if not self.vector_store:
                raise ValueError("VectorStore no inicializado")
            
            document_id = await self.vector_store.store_document(
                title=title,
                content=content,
                content_type=content_type,
                user_id=user_id,
                conversation_id=conversation_id,
                metadata=metadata
            )
            
            logger.info(f"Conocimiento almacenado: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error almacenando conocimiento: {e}")
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
        Almacena mensaje de conversación con embedding
        
        Args:
            conversation_id: ID de conversación
            role: Rol del mensaje ('user', 'assistant', 'system')
            content: Contenido del mensaje
            agent_id: ID del agente
            user_id: ID del usuario
            metadata: Metadatos adicionales
            
        Returns:
            ID del mensaje almacenado
        """
        try:
            if not self.vector_store:
                raise ValueError("VectorStore no inicializado")
            
            message_id = await self.vector_store.store_conversation_message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                agent_id=agent_id,
                user_id=user_id,
                metadata=metadata
            )
            
            # Actualizar cache de conversación
            if conversation_id not in self.conversation_cache:
                self.conversation_cache[conversation_id] = []
            self.conversation_cache[conversation_id].append({
                "id": message_id,
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Mensaje almacenado: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Error almacenando mensaje: {e}")
            raise
    
    async def search_knowledge(
        self,
        query: str,
        limit: int = 10,
        user_id: str = None,
        conversation_id: str = None,
        content_type: str = None,
        time_range: str = None
    ) -> List[Dict[str, Any]]:
        """
        Busca conocimiento relevante usando búsqueda semántica
        
        Args:
            query: Consulta de búsqueda
            limit: Número máximo de resultados
            user_id: Filtrar por usuario
            conversation_id: Filtrar por conversación
            content_type: Filtrar por tipo de contenido
            time_range: Rango temporal
            
        Returns:
            Lista de resultados relevantes
        """
        try:
            if not self.vector_store:
                raise ValueError("VectorStore no inicializado")
            
            results = await self.vector_store.semantic_search(
                query=query,
                limit=limit,
                user_id=user_id,
                conversation_id=conversation_id,
                content_type=content_type,
                time_range=time_range
            )
            
            logger.info(f"Búsqueda completada: {len(results)} resultados para '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            raise
    
    async def get_conversation_context(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Obtiene contexto de conversación reciente
        
        Args:
            conversation_id: ID de conversación
            limit: Número máximo de mensajes
            
        Returns:
            Lista de mensajes de la conversación
        """
        try:
            # Verificar cache primero
            if conversation_id in self.conversation_cache:
                cached_messages = self.conversation_cache[conversation_id]
                if len(cached_messages) >= limit:
                    return cached_messages[-limit:]
            
            # Si no está en cache o necesita más, consultar VectorStore
            if self.vector_store:
                with self.vector_store.engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT role, content, agent_id, created_at, metadata
                        FROM messages 
                        WHERE conversation_id = :conversation_id
                        ORDER BY created_at DESC
                        LIMIT :limit
                    """), {
                        "conversation_id": conversation_id,
                        "limit": limit
                    })
                    
                    messages = []
                    for row in result.fetchall():
                        messages.append({
                            "role": row[0],
                            "content": row[1],
                            "agent_id": row[2],
                            "timestamp": row[3].isoformat() if row[3] else None,
                            "metadata": json.loads(row[4]) if row[4] else {}
                        })
                    
                    # Actualizar cache
                    self.conversation_cache[conversation_id] = list(reversed(messages))
                    
                    return messages
            else:
                # Fallback al cache local
                return self.conversation_cache.get(conversation_id, [])
                
        except Exception as e:
            logger.error(f"Error obteniendo contexto de conversación: {e}")
            return []
    
    async def get_relevant_context(
        self,
        query: str,
        conversation_id: str = None,
        user_id: str = None,
        max_context_length: int = 2000
    ) -> str:
        """
        Obtiene contexto relevante para una consulta
        
        Args:
            query: Consulta actual
            conversation_id: ID de conversación
            user_id: ID del usuario
            max_context_length: Longitud máxima del contexto
            
        Returns:
            Texto de contexto relevante
        """
        try:
            # Buscar conocimiento relevante
            knowledge_results = await self.search_knowledge(
                query=query,
                limit=5,
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            # Obtener contexto de conversación reciente
            context_messages = []
            if conversation_id:
                recent_messages = await self.get_conversation_context(conversation_id, limit=10)
                context_messages = recent_messages
            
            # Construir contexto
            context_parts = []
            
            # Agregar resultados de búsqueda
            if knowledge_results:
                context_parts.append("=== CONOCIMIENTO RELEVANTE ===")
                for result in knowledge_results:
                    if result.get("title"):
                        context_parts.append(f"Documento: {result['title']}")
                    context_parts.append(result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"])
                    context_parts.append("")
            
            # Agregar mensajes de contexto
            if context_messages:
                context_parts.append("=== CONTEXTO DE CONVERSACIÓN ===")
                for msg in context_messages[-5:]:  # Últimos 5 mensajes
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")[:300]  # Limitar longitud
                    context_parts.append(f"{role}: {content}")
                context_parts.append("")
            
            # Unir y truncar si es necesario
            context = "\n".join(context_parts)
            if len(context) > max_context_length:
                context = context[:max_context_length] + "\n...(contexto truncado)"
            
            return context
            
        except Exception as e:
            logger.error(f"Error obteniendo contexto relevante: {e}")
            return ""
    
    async def summarize_memory(self, conversation_id: str) -> str:
        """
        Genera resumen de la memoria de una conversación
        
        Args:
            conversation_id: ID de conversación
            
        Returns:
            Resumen de la conversación
        """
        try:
            context_messages = await self.get_conversation_context(conversation_id, limit=50)
            
            if not context_messages:
                return "No hay mensajes en esta conversación."
            
            # Crear resumen básico
            user_messages = [msg for msg in context_messages if msg.get("role") == "user"]
            assistant_messages = [msg for msg in context_messages if msg.get("role") == "assistant"]
            
            summary_parts = [
                f"Conversación con {len(context_messages)} mensajes:",
                f"- {len(user_messages)} mensajes del usuario",
                f"- {len(assistant_messages)} respuestas del asistente",
                ""
            ]
            
            # Agregar temas principales (primeros mensajes)
            if user_messages:
                summary_parts.append("Temas principales:")
                for i, msg in enumerate(user_messages[:3]):
                    content = msg.get("content", "")[:100]
                    summary_parts.append(f"{i+1}. {content}...")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return "Error generando resumen de memoria."
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la memoria"""
        try:
            stats = {
                "agent_id": self.agent_id,
                "capabilities": self.get_capabilities(),
                "cache_stats": {
                    "conversations_cached": len(self.conversation_cache),
                    "memory_cache_size": len(self.memory_cache)
                }
            }
            
            if self.vector_store:
                vector_stats = await self.vector_store.get_stats()
                stats["vector_store"] = vector_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
    
    async def _generate_embedding(self, content: Any) -> List[float]:
        """Genera embedding usando el embedding service"""
        text = json.dumps(content) if isinstance(content, dict) else str(content)
        
        if self.embedding_service:
            try:
                embeddings = await self.embedding_service.generate_embeddings([text])
                if embeddings and len(embeddings) > 0:
                    return embeddings[0]
            except Exception as e:
                logger.warning(f"Error con embedding service: {e}")
        
        # Fallback a embedding determinístico
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(seed)
        embedding = np.random.normal(0, 1, 384).tolist()
        
        # Normalizar
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = (embedding / norm).tolist()
        
        return embedding
    
    async def store_insight(self, insight: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Almacena un insight"""
        try:
            memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generar embedding
            embedding = await self._generate_embedding(insight)
            
            # Almacenar en cache
            self.memory_cache[memory_id] = {
                "content": insight,
                "embedding": embedding,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Insight almacenado: {memory_id}")
            return {
                "success": True,
                "memory_id": memory_id,
                "operation": "store_insight"
            }
            
        except Exception as e:
            logger.error(f"Error almacenando insight: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_in_memory(self, query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Búsqueda simple en memoria"""
        try:
            query_embedding = await self._generate_embedding(query)
            
            results = []
            for memory_id, memory_data in self.memory_cache.items():
                # Calcular similitud coseno
                memory_embedding = memory_data["embedding"]
                dot_product = np.dot(query_embedding, memory_embedding)
                norm_query = np.linalg.norm(query_embedding)
                norm_memory = np.linalg.norm(memory_embedding)
                
                if norm_query > 0 and norm_memory > 0:
                    similarity = dot_product / (norm_query * norm_memory)
                else:
                    similarity = 0.0
                
                results.append({
                    "memory_id": memory_id,
                    "content": memory_data["content"],
                    "metadata": memory_data["metadata"],
                    "score": float(similarity),
                    "created_at": memory_data["created_at"]
                })
            
            # Ordenar por similitud
            results.sort(key=lambda x: x["score"], reverse=True)
            results = results[:limit]
            
            return {
                "success": True,
                "query": query,
                "total_results": len(results),
                "results": results,
                "search_type": "semantic_cache"
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """Procesa mensaje"""
        try:
            operation = message.payload.get("operation", "store")
            
            if operation == "store":
                result = await self.store_insight(
                    message.payload.get("insight", ""),
                    message.payload.get("metadata")
                )
            elif operation == "search":
                result = await self.search_in_memory(
                    message.payload.get("query", ""),
                    message.payload.get("limit", 5)
                )
            else:
                result = {"success": False, "error": f"Operación no soportada: {operation}"}
            
            return AgentResponse(
                message_id=f"resp_{message.message_id}",
                original_message_id=message.message_id,
                agent_id=self.agent_id,
                status=MessageStatus.DONE,
                result=result
            )
            
        except Exception as e:
            logger.exception("Error en Memory Manager")
            raise