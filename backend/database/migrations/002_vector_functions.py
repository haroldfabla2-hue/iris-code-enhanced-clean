"""
Script de migración para operaciones RAG avanzadas
Incluye funciones para búsqueda vectorial y manejo de embeddings
"""

import os
import sys
import json
import numpy as np
from typing import List, Optional, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, Conversation, Message, AgentMessage, KnowledgeBase

def create_vector_search_functions(database_url: str):
    """
    Crea funciones SQL para búsqueda vectorial eficiente
    """
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Función para buscar contenido similar usando cosine similarity
            search_function = """
            CREATE OR REPLACE FUNCTION search_similar_content(
                query_embedding vector(1536),
                table_name text,
                limit_count integer DEFAULT 5
            )
            RETURNS TABLE (
                id integer,
                content text,
                title text,
                similarity float
            ) AS $$
            BEGIN
                IF table_name = 'messages' THEN
                    RETURN QUERY
                    SELECT 
                        m.id,
                        m.content,
                        '' as title,
                        1 - (m.embedding <=> query_embedding) as similarity
                    FROM messages m
                    WHERE m.embedding IS NOT NULL
                    ORDER BY m.embedding <=> query_embedding
                    LIMIT limit_count;
                ELSIF table_name = 'knowledge_base' THEN
                    RETURN QUERY
                    SELECT 
                        k.id,
                        k.content,
                        k.title,
                        1 - (k.embedding <=> query_embedding) as similarity
                    FROM knowledge_base k
                    WHERE k.embedding IS NOT NULL
                    ORDER BY k.embedding <=> query_embedding
                    LIMIT limit_count;
                ELSE
                    RAISE EXCEPTION 'Tabla no válida: %', table_name;
                END IF;
            END;
            $$ LANGUAGE plpgsql;
            """
            
            conn.execute(text(search_function))
            
            # Función para actualizar embeddings en lote
            batch_update_function = """
            CREATE OR REPLACE FUNCTION update_embeddings_batch(
                table_name text,
                id_list integer[],
                embedding_list vector(1536)[]
            )
            RETURNS void AS $$
            DECLARE
                i integer;
                table_id text;
            BEGIN
                FOR i IN 1..array_length(id_list, 1) LOOP
                    IF table_name = 'messages' THEN
                        UPDATE messages 
                        SET embedding = embedding_list[i]
                        WHERE id = id_list[i];
                    ELSIF table_name = 'agent_messages' THEN
                        UPDATE agent_messages 
                        SET embedding = embedding_list[i]
                        WHERE id = id_list[i];
                    ELSIF table_name = 'knowledge_base' THEN
                        UPDATE knowledge_base 
                        SET embedding = embedding_list[i]
                        WHERE id = id_list[i];
                    END IF;
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
            """
            
            conn.execute(text(batch_update_function))
            conn.commit()
            
            print("✅ Funciones de búsqueda vectorial creadas correctamente")
            
    except Exception as e:
        print(f"❌ Error al crear funciones vectoriales: {e}")
        return False
    
    return True

def search_similar_content(
    database_url: str,
    query_embedding: List[float],
    table_name: str,
    limit: int = 5
) -> List[dict]:
    """
    Busca contenido similar usando embeddings vectoriales
    """
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Convertir embedding a formato PostgreSQL
            embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
            result = conn.execute(
                text("SELECT * FROM search_similar_content(:embedding, :table_name, :limit)"),
                {
                    "embedding": embedding_str,
                    "table_name": table_name,
                    "limit": limit
                }
            )
            
            results = []
            for row in result:
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "title": row[2],
                    "similarity": float(row[3])
                })
            
            return results
            
    except Exception as e:
        print(f"❌ Error en búsqueda vectorial: {e}")
        return []

def update_embedding(
    session,
    record,
    embedding: List[float]
):
    """
    Actualiza el embedding de un registro
    """
    try:
        record.set_embedding(embedding)
        session.commit()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar embedding: {e}")
        session.rollback()
        return False

def batch_update_embeddings(
    database_url: str,
    table_name: str,
    records: List,
    embeddings: List[List[float]]
):
    """
    Actualiza múltiples embeddings de forma eficiente
    """
    if len(records) != len(embeddings):
        raise ValueError("El número de registros debe coincidir con el número de embeddings")
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Preparar datos para la función SQL
            id_list = [record.id for record in records]
            
            # Convertir embeddings a formato PostgreSQL
            embedding_list = []
            for embedding in embeddings:
                embedding_str = f"[{','.join(map(str, embedding))}]"
                embedding_list.append(embedding_str)
            
            # Llamar función de actualización en lote
            conn.execute(
                text("SELECT update_embeddings_batch(:table_name, :id_list, :embedding_list)"),
                {
                    "table_name": table_name,
                    "id_list": id_list,
                    "embedding_list": embedding_list
                }
            )
            
            conn.commit()
            print(f"✅ {len(records)} embeddings actualizados en {table_name}")
            return True
            
    except Exception as e:
        print(f"❌ Error en actualización por lotes: {e}")
        return False

def get_embedding_stats(database_url: str):
    """
    Obtiene estadísticas sobre los embeddings almacenados
    """
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Contar registros con embeddings
            stats_query = """
            SELECT 
                'messages' as table_name,
                COUNT(*) as total_records,
                COUNT(embedding) as records_with_embeddings,
                ROUND(AVG(array_length(string_to_array(trim(both '[]' from embedding), ','), 1)), 0) as avg_embedding_dimensions
            FROM messages
            UNION ALL
            SELECT 
                'agent_messages' as table_name,
                COUNT(*) as total_records,
                COUNT(embedding) as records_with_embeddings,
                ROUND(AVG(array_length(string_to_array(trim(both '[]' from embedding), ','), 1)), 0) as avg_embedding_dimensions
            FROM agent_messages
            UNION ALL
            SELECT 
                'knowledge_base' as table_name,
                COUNT(*) as total_records,
                COUNT(embedding) as records_with_embeddings,
                ROUND(AVG(array_length(string_to_array(trim(both '[]' from embedding), ','), 1)), 0) as avg_embedding_dimensions
            FROM knowledge_base;
            """
            
            result = conn.execute(text(stats_query))
            
            print("📊 Estadísticas de embeddings:")
            print("-" * 60)
            for row in result:
                print(f"Tabla: {row[0]}")
                print(f"  Total de registros: {row[1]}")
                print(f"  Con embeddings: {row[2]}")
                print(f"  Dimensiones promedio: {row[3]}")
                print()
                
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migración para funciones RAG avanzadas")
    parser.add_argument("--database-url", required=True, help="URL de conexión a PostgreSQL")
    parser.add_argument("--create-functions", action="store_true", help="Crear funciones SQL")
    parser.add_argument("--stats", action="store_true", help="Mostrar estadísticas de embeddings")
    
    args = parser.parse_args()
    
    if args.create_functions:
        create_vector_search_functions(args.database_url)
    
    if args.stats:
        get_embedding_stats(args.database_url)