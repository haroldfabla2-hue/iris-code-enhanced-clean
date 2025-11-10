"""
Servicio de Embeddings usando HuggingFace Transformers
Genera embeddings vectoriales de manera gratuita y eficiente
"""
from typing import List, Dict, Any, Optional
import asyncio
import logging
import numpy as np
import time
import os

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Servicio de embeddings usando modelos de HuggingFace
    
    Utiliza sentence-transformers para generar embeddings de alta calidad
    de manera completamente gratuita.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Inicializa el servicio de embeddings
        
        Args:
            model_name: Nombre del modelo de sentence-transformers a usar
                       Default: "all-MiniLM-L6-v2" (384 dimensiones, muy rápido)
                       Alternativas: "all-mpnet-base-v2" (768 dimensiones, mejor calidad)
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        # Importación lazy de torch para determinar el dispositivo
        try:
            import torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            self.device = "cpu"
        self.embedding_cache = {}  # Cache para embeddings frecuentes
        self.cache_size_limit = 1000
        self.model_loading_time = None
        
    async def initialize(self) -> Dict[str, Any]:
        """
        Inicializa el modelo de embeddings
        
        Returns:
            Dict con información del modelo cargado
        """
        try:
            logger.info(f"Inicializando modelo de embeddings: {self.model_name}")
            start_time = time.time()
            
            # Cargar modelo en un thread pool para evitar bloqueo
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._load_model_sync)
            
            self.model_loading_time = time.time() - start_time
            
            return {
                "success": True,
                "model_name": self.model_name,
                "device": self.device,
                "loading_time_seconds": round(self.model_loading_time, 2),
                "embedding_dimensions": self.model.get_sentence_embedding_dimension(),
                "max_sequence_length": self.model.max_seq_length,
                "model_type": "sentence-transformers"
            }
            
        except Exception as e:
            logger.error(f"Error inicializando modelo de embeddings: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model_name": self.model_name
            }
    
    def _load_model_sync(self):
        """Carga el modelo de manera síncrona (para usar en thread pool)"""
        try:
            # Importaciones lazy
            import torch
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Cargando modelo sentence-transformers: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Configurar dispositivo
            if self.device == "cuda":
                self.model = self.model.cuda()
            
            logger.info(f"Modelo cargado exitosamente en {self.device}")
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {str(e)}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Genera embedding vectorial de un texto
        
        Args:
            text: Texto a vectorizar
            
        Returns:
            Lista de floats representando el embedding
        """
        if not text or not text.strip():
            # Retornar embedding cero para texto vacío
            dim = 384 if self.model_name == "all-MiniLM-L6-v2" else 768
            return [0.0] * dim
        
        # Limpiar y normalizar texto
        cleaned_text = self._clean_text(text)
        
        # Verificar cache
        cache_key = hash(cleaned_text)
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            # Generar embedding en thread pool
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self._generate_embedding_sync, 
                cleaned_text
            )
            
            # Actualizar cache si no está lleno
            if len(self.embedding_cache) < self.cache_size_limit:
                self.embedding_cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generando embedding: {str(e)}")
            # Retornar embedding cero en caso de error
            dim = 384 if self.model_name == "all-MiniLM-L6-v2" else 768
            return [0.0] * dim
    
    def _generate_embedding_sync(self, text: str) -> List[float]:
        """Genera embedding de manera síncrona"""
        try:
            # Generar embedding
            embedding_vector = self.model.encode([text])[0]
            
            # Convertir a lista y normalizar
            embedding_list = embedding_vector.tolist()
            
            # Normalizar para que tenga norma 1 (útil para cosine similarity)
            embedding_array = np.array(embedding_list)
            norm = np.linalg.norm(embedding_array)
            if norm > 0:
                embedding_list = (embedding_array / norm).tolist()
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Error en generación síncrona de embedding: {str(e)}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para múltiples textos de manera eficiente
        
        Args:
            texts: Lista de textos a vectorizar
            
        Returns:
            Lista de embeddings (cada uno es una lista de floats)
        """
        if not texts:
            return []
        
        try:
            # Limpiar textos
            cleaned_texts = [self._clean_text(text) for text in texts]
            
            # Verificar cache para textos existentes
            embeddings = []
            texts_to_process = []
            indices_to_process = []
            
            for i, text in enumerate(cleaned_texts):
                if not text:  # Texto vacío
                    dim = 384 if self.model_name == "all-MiniLM-L6-v2" else 768
                    embeddings.append([0.0] * dim)
                else:
                    cache_key = hash(text)
                    if cache_key in self.embedding_cache:
                        embeddings.append(self.embedding_cache[cache_key])
                    else:
                        texts_to_process.append(text)
                        indices_to_process.append(i)
                        embeddings.append(None)  # Placeholder
            
            # Procesar textos no cacheados
            if texts_to_process:
                loop = asyncio.get_event_loop()
                new_embeddings = await loop.run_in_executor(
                    None,
                    self._generate_embeddings_batch_sync,
                    texts_to_process
                )
                
                # Insertar embeddings procesados en las posiciones correctas
                for i, embedding in zip(indices_to_process, new_embeddings):
                    embeddings[i] = embedding
                    
                    # Actualizar cache
                    if len(self.embedding_cache) < self.cache_size_limit:
                        self.embedding_cache[hash(cleaned_texts[i])] = embedding
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error en generación batch de embeddings: {str(e)}")
            # Retornar embeddings cero en caso de error
            dim = 384 if self.model_name == "all-MiniLM-L6-v2" else 768
            return [[0.0] * dim for _ in texts]
    
    def _generate_embeddings_batch_sync(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings de manera síncrona para múltiples textos"""
        try:
            # Generar embeddings batch
            embedding_vectors = self.model.encode(texts)
            
            embeddings = []
            for embedding_vector in embedding_vectors:
                embedding_list = embedding_vector.tolist()
                
                # Normalizar
                embedding_array = np.array(embedding_list)
                norm = np.linalg.norm(embedding_array)
                if norm > 0:
                    embedding_list = (embedding_array / norm).tolist()
                
                embeddings.append(embedding_list)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error en generación batch síncrona: {str(e)}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Alias para generate_embeddings_batch (compatibilidad)
        
        Args:
            texts: Lista de textos a vectorizar
            
        Returns:
            Lista de embeddings (cada uno es una lista de floats)
        """
        return await self.generate_embeddings_batch(texts)
    
    async def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcula similitud coseno entre dos embeddings
        
        Args:
            embedding1: Primer embedding
            embedding2: Segundo embedding
            
        Returns:
            Similitud coseno (0.0 a 1.0)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calcular producto punto y normas
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Asegurar que esté en rango [-1, 1]
            return max(-1.0, min(1.0, float(similarity)))
            
        except Exception as e:
            logger.error(f"Error calculando similitud coseno: {str(e)}")
            return 0.0
    
    def _clean_text(self, text: str) -> str:
        """
        Limpia y normaliza texto para embedding
        
        Args:
            text: Texto a limpiar
            
        Returns:
            Texto limpiado
        """
        if not text:
            return ""
        
        # Remover caracteres especiales excesivos y normalizar espacios
        import re
        text = re.sub(r'\s+', ' ', text)  # Múltiples espacios a uno solo
        text = text.strip()
        
        # Limitar longitud para evitar problemas con el modelo
        max_length = 8000  # Caracteres
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del cache de embeddings
        
        Returns:
            Dict con estadísticas del cache
        """
        return {
            "cache_size": len(self.embedding_cache),
            "cache_limit": self.cache_size_limit,
            "cache_utilization": len(self.embedding_cache) / self.cache_size_limit,
            "model_name": self.model_name,
            "device": self.device
        }
    
    def clear_cache(self):
        """Limpia el cache de embeddings"""
        self.embedding_cache.clear()
        logger.info("Cache de embeddings limpiado")
    
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información detallada del modelo
        
        Returns:
            Dict con información del modelo
        """
        if not self.model:
            return {
                "loaded": False,
                "model_name": self.model_name,
                "error": "Modelo no inicializado"
            }
        
        # Importación lazy para torch
        import torch
        
        return {
            "loaded": True,
            "model_name": self.model_name,
            "device": self.device,
            "embedding_dimensions": self.model.get_sentence_embedding_dimension(),
            "max_sequence_length": getattr(self.model, 'max_seq_length', 'unknown'),
            "model_type": "sentence-transformers",
            "loading_time_seconds": self.model_loading_time,
            "cache_stats": self.get_cache_stats(),
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }


# Instancia global del servicio de embeddings
embedding_service = EmbeddingService()


async def initialize_embedding_service(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingService:
    """
    Inicializa el servicio global de embeddings
    
    Args:
        model_name: Nombre del modelo a usar
        
    Returns:
        Instancia del EmbeddingService inicializada
    """
    global embedding_service
    
    # Actualizar modelo si es diferente
    if embedding_service.model_name != model_name:
        embedding_service = EmbeddingService(model_name)
    
    # Inicializar si no está cargado
    if not embedding_service.model:
        result = await embedding_service.initialize()
        if not result.get("success"):
            raise Exception(f"Error inicializando embedding service: {result.get('error')}")
    
    return embedding_service