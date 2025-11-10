"""
Agente Memory Manager Simplificado para RAG
"""
from typing import List, Dict, Any, Optional
import json
import hashlib
from datetime import datetime
import logging
import numpy as np

from .base import BaseAgent
from ..models import AgentMessage, AgentResponse, MessageStatus

logger = logging.getLogger(__name__)


class MemoryManagerAgent(BaseAgent):
    """
    Agente Memory Manager: Gestión simplificada de memoria semántica
    """
    
    def __init__(self, llm_client: Any = None, vector_store: Any = None):
        super().__init__(
            agent_id="memory_manager",
            llm_client=llm_client
        )
        self.vector_store = vector_store
        self.memory_cache = {}  # Cache temporal
        self.embedding_cache = {}  # Cache de embeddings
        
    def get_capabilities(self) -> List[str]:
        return [
            "knowledge_storage",
            "context_retrieval", 
            "semantic_search",
            "memory_synthesis"
        ]
    
    async def _generate_embedding(self, content: Any) -> List[float]:
        """Genera embedding mock determinístico"""
        text = json.dumps(content) if isinstance(content, dict) else str(content)
        
        # Generar embedding determinístico basado en hash
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
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas"""
        return {
            "success": True,
            "stats": {
                "total_memories": len(self.memory_cache),
                "cache_type": "local",
                "search_enabled": True,
                "embeddings_enabled": True
            }
        }
    
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