"""
Servicio de Chunking para Documentos
Implementa estrategias de división de texto para RAG
"""
from typing import List, Dict, Any, Optional, Tuple
import re
import logging
from dataclasses import dataclass
from enum import Enum
import tiktoken

logger = logging.getLogger(__name__)


class ChunkingStrategy(Enum):
    """Estrategias de chunking disponibles"""
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    SENTENCE_BASED = "sentence_based"
    PARAGRAPH_BASED = "paragraph_based"
    RECURSIVE = "recursive"


@dataclass
class Chunk:
    """Representa un chunk de documento"""
    id: str
    content: str
    start_position: int
    end_position: int
    token_count: int
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class DocumentChunker:
    """
    Servicio para dividir documentos en chunks optimizados para RAG
    
    Implementa múltiples estrategias de chunking para optimizar
    la recuperación de información relevante.
    """
    
    def __init__(self):
        """Inicializa el chunker"""
        self.tokenizer = None
        self._init_tokenizer()
    
    def _init_tokenizer(self):
        """Inicializa el tokenizer para conteo de tokens"""
        try:
            # Usar tokenizer de OpenAI para conteo preciso de tokens
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"No se pudo cargar tokenizer: {str(e)} - usando estimación por caracteres")
            self.tokenizer = None
    
    def chunk_document(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC,
        max_tokens: int = 500,
        overlap_tokens: int = 50,
        **kwargs
    ) -> List[Chunk]:
        """
        Divide un documento en chunks según la estrategia especificada
        
        Args:
            text: Texto del documento a dividir
            strategy: Estrategia de chunking a usar
            max_tokens: Número máximo de tokens por chunk
            overlap_tokens: Número de tokens de superposición entre chunks
            **kwargs: Argumentos adicionales específicos de cada estrategia
            
        Returns:
            Lista de chunks procesados
        """
        if not text or not text.strip():
            return []
        
        try:
            if strategy == ChunkingStrategy.FIXED_SIZE:
                return self._chunk_by_fixed_size(text, max_tokens, overlap_tokens)
            elif strategy == ChunkingStrategy.SEMANTIC:
                return self._chunk_semantically(text, max_tokens, overlap_tokens)
            elif strategy == ChunkingStrategy.SENTENCE_BASED:
                return self._chunk_by_sentences(text, max_tokens, overlap_tokens)
            elif strategy == ChunkingStrategy.PARAGRAPH_BASED:
                return self._chunk_by_paragraphs(text, max_tokens, overlap_tokens)
            elif strategy == ChunkingStrategy.RECURSIVE:
                return self._chunk_recursively(text, max_tokens, overlap_tokens)
            else:
                raise ValueError(f"Estrategia de chunking no soportada: {strategy}")
                
        except Exception as e:
            logger.error(f"Error en chunking: {str(e)}")
            # Fallback a chunking por tamaño fijo
            return self._chunk_by_fixed_size(text, max_tokens, overlap_tokens)
    
    def _chunk_by_fixed_size(
        self,
        text: str,
        max_tokens: int,
        overlap_tokens: int
    ) -> List[Chunk]:
        """Chunking por tamaño fijo de tokens"""
        chunks = []
        chunks_info = self._split_text_by_tokens(text, max_tokens, overlap_tokens)
        
        for i, chunk_info in enumerate(chunks_info):
            chunk = Chunk(
                id=f"chunk_{i:04d}",
                content=chunk_info["text"],
                start_position=chunk_info["start_pos"],
                end_position=chunk_info["end_pos"],
                token_count=chunk_info["token_count"],
                metadata={
                    "strategy": "fixed_size",
                    "chunk_index": i,
                    "total_chunks": len(chunks_info),
                    "overlap_tokens": overlap_tokens
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_semantically(
        self,
        text: str,
        max_tokens: int,
        overlap_tokens: int
    ) -> List[Chunk]:
        """Chunking semántico basado en puntuación y estructura"""
        # Dividir por párrafos primero
        paragraphs = self._split_into_paragraphs(text)
        chunks = []
        current_chunk = ""
        current_start = 0
        
        for para_idx, paragraph in enumerate(paragraphs):
            para_start = text.find(paragraph, current_start)
            para_end = para_start + len(paragraph)
            
            # Verificar si agregar este párrafo excede el límite
            test_chunk = current_chunk + ("\n\n" if current_chunk else "") + paragraph
            test_token_count = self._count_tokens(test_chunk)
            
            if test_token_count <= max_tokens:
                current_chunk = test_chunk
                current_start = para_end
            else:
                # Guardar chunk actual si tiene contenido
                if current_chunk.strip():
                    chunk = Chunk(
                        id=f"chunk_{len(chunks):04d}",
                        content=current_chunk.strip(),
                        start_position=current_start - len(current_chunk),
                        end_position=current_start,
                        token_count=self._count_tokens(current_chunk),
                        metadata={
                            "strategy": "semantic",
                            "chunk_index": len(chunks),
                            "paragraph_range": [para_idx - len(current_chunk.split('\n\n')), para_idx],
                            "overlap_tokens": overlap_tokens
                        }
                    )
                    chunks.append(chunk)
                
                # Iniciar nuevo chunk
                current_chunk = paragraph
                current_start = para_end
        
        # Agregar último chunk
        if current_chunk.strip():
            chunk = Chunk(
                id=f"chunk_{len(chunks):04d}",
                content=current_chunk.strip(),
                start_position=current_start - len(current_chunk),
                end_position=current_start,
                token_count=self._count_tokens(current_chunk),
                metadata={
                    "strategy": "semantic",
                    "chunk_index": len(chunks),
                    "paragraph_range": [len(paragraphs) - 1, len(paragraphs) - 1],
                    "overlap_tokens": overlap_tokens
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_sentences(
        self,
        text: str,
        max_tokens: int,
        overlap_tokens: int
    ) -> List[Chunk]:
        """Chunking basado en oraciones completas"""
        sentences = self._split_into_sentences(text)
        chunks = []
        current_chunk = ""
        current_start = 0
        
        for sent_idx, sentence in enumerate(sentences):
            sent_start = text.find(sentence, current_start)
            sent_end = sent_start + len(sentence)
            
            # Verificar si agregar esta oración excede el límite
            test_chunk = current_chunk + (" " if current_chunk else "") + sentence
            test_token_count = self._count_tokens(test_chunk)
            
            if test_token_count <= max_tokens:
                current_chunk = test_chunk
                current_start = sent_end
            else:
                # Guardar chunk actual si tiene contenido
                if current_chunk.strip():
                    chunk = Chunk(
                        id=f"chunk_{len(chunks):04d}",
                        content=current_chunk.strip(),
                        start_position=current_start - len(current_chunk),
                        end_position=current_start,
                        token_count=self._count_tokens(current_chunk),
                        metadata={
                            "strategy": "sentence_based",
                            "chunk_index": len(chunks),
                            "sentence_range": [sent_idx - current_chunk.count('.') - 1, sent_idx - 1],
                            "overlap_tokens": overlap_tokens
                        }
                    )
                    chunks.append(chunk)
                
                # Iniciar nuevo chunk
                current_chunk = sentence
                current_start = sent_end
        
        # Agregar último chunk
        if current_chunk.strip():
            chunk = Chunk(
                id=f"chunk_{len(chunks):04d}",
                content=current_chunk.strip(),
                start_position=current_start - len(current_chunk),
                end_position=current_start,
                token_count=self._count_tokens(current_chunk),
                metadata={
                    "strategy": "sentence_based",
                    "chunk_index": len(chunks),
                    "sentence_range": [len(sentences) - 1, len(sentences) - 1],
                    "overlap_tokens": overlap_tokens
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_paragraphs(
        self,
        text: str,
        max_tokens: int,
        overlap_tokens: int
    ) -> List[Chunk]:
        """Chunking basado en párrafos"""
        paragraphs = self._split_into_paragraphs(text)
        chunks = []
        current_chunk = ""
        current_start = 0
        
        for para_idx, paragraph in enumerate(paragraphs):
            para_start = text.find(paragraph, current_start)
            para_end = para_start + len(paragraph)
            
            test_chunk = current_chunk + ("\n\n" if current_chunk else "") + paragraph
            test_token_count = self._count_tokens(test_chunk)
            
            if test_token_count <= max_tokens:
                current_chunk = test_chunk
                current_start = para_end
            else:
                if current_chunk.strip():
                    chunk = Chunk(
                        id=f"chunk_{len(chunks):04d}",
                        content=current_chunk.strip(),
                        start_position=current_start - len(current_chunk),
                        end_position=current_start,
                        token_count=self._count_tokens(current_chunk),
                        metadata={
                            "strategy": "paragraph_based",
                            "chunk_index": len(chunks),
                            "paragraph_index": para_idx - 1,
                            "overlap_tokens": overlap_tokens
                        }
                    )
                    chunks.append(chunk)
                
                current_chunk = paragraph
                current_start = para_end
        
        if current_chunk.strip():
            chunk = Chunk(
                id=f"chunk_{len(chunks):04d}",
                content=current_chunk.strip(),
                start_position=current_start - len(current_chunk),
                end_position=current_start,
                token_count=self._count_tokens(current_chunk),
                metadata={
                    "strategy": "paragraph_based",
                    "chunk_index": len(chunks),
                    "paragraph_index": len(paragraphs) - 1,
                    "overlap_tokens": overlap_tokens
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_recursively(
        self,
        text: str,
        max_tokens: int,
        overlap_tokens: int
    ) -> List[Chunk]:
        """Chunking recursivo que intenta preservar estructura semántica"""
        # Primero intentar dividir por párrafos
        chunks_info = self._split_text_by_tokens(text, max_tokens, overlap_tokens)
        
        # Refinar chunks para preservar oraciones completas
        refined_chunks = []
        for chunk_info in chunks_info:
            chunk_text = chunk_info["text"]
            
            # Si el chunk es muy grande, intentar dividirlo por oraciones
            if self._count_tokens(chunk_text) > max_tokens * 0.8:
                sentences = self._split_into_sentences(chunk_text)
                refined_chunk = ""
                for sentence in sentences:
                    test_chunk = refined_chunk + (" " if refined_chunk else "") + sentence
                    if self._count_tokens(test_chunk) <= max_tokens:
                        refined_chunk = test_chunk
                    else:
                        if refined_chunk.strip():
                            refined_chunks.append(refined_chunk.strip())
                        refined_chunk = sentence
                
                if refined_chunk.strip():
                    refined_chunks.append(refined_chunk.strip())
            else:
                refined_chunks.append(chunk_text.strip())
        
        # Crear objetos Chunk
        chunks = []
        for i, content in enumerate(refined_chunks):
            chunk = Chunk(
                id=f"chunk_{i:04d}",
                content=content,
                start_position=0,  # No aplicable para chunks refinados
                end_position=0,   # No aplicable para chunks refinados
                token_count=self._count_tokens(content),
                metadata={
                    "strategy": "recursive",
                    "chunk_index": i,
                    "total_chunks": len(refined_chunks),
                    "overlap_tokens": overlap_tokens,
                    "refined": True
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_text_by_tokens(
        self,
        text: str,
        max_tokens: int,
        overlap_tokens: int
    ) -> List[Dict[str, Any]]:
        """Divide texto por tokens manteniendo superposición"""
        chunks_info = []
        words = text.split()
        current_chunk = []
        current_token_count = 0
        start_pos = 0
        
        for i, word in enumerate(words):
            word_tokens = self._count_tokens(word + " ")
            new_token_count = current_token_count + word_tokens
            
            if new_token_count <= max_tokens:
                current_chunk.append(word)
                current_token_count = new_token_count
            else:
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunk_info = {
                        "text": chunk_text,
                        "start_pos": start_pos,
                        "end_pos": start_pos + len(chunk_text),
                        "token_count": current_token_count
                    }
                    chunks_info.append(chunk_info)
                    
                    # Calcular nueva posición de inicio con overlap
                    overlap_words = self._get_overlap_words(current_chunk, overlap_tokens)
                    overlap_text = " ".join(overlap_words)
                    start_pos = start_pos + len(chunk_text) - len(overlap_text)
                    
                    # Iniciar nuevo chunk con overlap
                    current_chunk = overlap_words + [word]
                    current_token_count = self._count_tokens(" ".join(current_chunk))
        
        # Agregar último chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_info = {
                "text": chunk_text,
                "start_pos": start_pos,
                "end_pos": start_pos + len(chunk_text),
                "token_count": current_token_count
            }
            chunks_info.append(chunk_info)
        
        return chunks_info
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Divide texto en párrafos"""
        # Buscar doble salto de línea o patrones de párrafo
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divide texto en oraciones preservando puntuación"""
        # Pattern que preserva puntuación y maneja abreviaciones
        sentence_pattern = r'(?<=\.)\s+(?=[A-Z])|(?<=\!)\s+(?=[A-Z])|(?<=\?)\s+(?=[A-Z])|(?<=:)\s+(?=[A-Z])'
        
        # Dividir por puntuación seguida de espacio y mayúscula
        sentences = re.split(sentence_pattern, text)
        
        # Limpiar y filtrar oraciones vacías
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _get_overlap_words(self, words: List[str], overlap_tokens: int) -> List[str]:
        """Obtiene palabras para el overlap desde el final del chunk anterior"""
        if overlap_tokens <= 0 or not words:
            return []
        
        overlap_words = []
        current_tokens = 0
        
        # Tomar palabras del final hacia el principio
        for word in reversed(words):
            word_tokens = self._count_tokens(word + " ")
            if current_tokens + word_tokens <= overlap_tokens:
                overlap_words.insert(0, word)
                current_tokens += word_tokens
            else:
                break
        
        return overlap_words
    
    def _count_tokens(self, text: str) -> int:
        """Cuenta tokens en el texto"""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception:
                pass
        
        # Fallback: estimación por caracteres (aproximadamente 4 caracteres por token)
        return len(text) // 4
    
    def get_chunking_stats(
        self,
        chunks: List[Chunk],
        original_text: str
    ) -> Dict[str, Any]:
        """Obtiene estadísticas del chunking realizado"""
        if not chunks:
            return {"error": "No hay chunks para analizar"}
        
        token_counts = [chunk.token_count for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "original_text_length": len(original_text),
            "total_tokens_original": self._count_tokens(original_text),
            "total_tokens_chunked": sum(token_counts),
            "avg_tokens_per_chunk": sum(token_counts) / len(token_counts),
            "min_tokens_per_chunk": min(token_counts),
            "max_tokens_per_chunk": max(token_counts),
            "compression_ratio": len(original_text) / sum(len(chunk.content) for chunk in chunks),
            "strategies_used": list(set(chunk.metadata.get("strategy", "unknown") for chunk in chunks))
        }


# Instancia global del chunker
document_chunker = DocumentChunker()