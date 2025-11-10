"""
Configuración y utilidades para base de datos PostgreSQL con pgvector
Incluye funciones auxiliares para manejo de embeddings y configuración
"""

import os
import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Configuración de base de datos"""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600

class DatabaseManager:
    """Gestor centralizado de base de datos"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.session_factory = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging para operaciones de base de datos"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Establece conexión con la base de datos"""
        try:
            self.engine = create_engine(
                self.config.url,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle
            )
            
            self.session_factory = sessionmaker(bind=self.engine)
            
            # Test de conexión
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            
            self.logger.info("Conexión a base de datos establecida")
            return True
            
        except Exception as e:
            self.logger.error(f"Error conectando a base de datos: {e}")
            return False
    
    def get_session(self):
        """Obtiene una sesión de base de datos"""
        if not self.session_factory:
            raise RuntimeError("Base de datos no conectada. Llame a connect() primero.")
        
        return self.session_factory()
    
    def close(self):
        """Cierra conexiones"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Conexiones de base de datos cerradas")

class EmbeddingManager:
    """Gestor para operaciones con embeddings"""
    
    def __init__(self, database_manager: DatabaseManager):
        self.db = database_manager
    
    def similarity_search(
        self,
        query_embedding: List[float],
        table_name: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Busca contenido similar usando embeddings
        
        Args:
            query_embedding: Vector de consulta
            table_name: Tabla donde buscar ('messages', 'agent_messages', 'knowledge_base')
            limit: Número máximo de resultados
            threshold: Umbral mínimo de similitud
            
        Returns:
            Lista de resultados con contenido y similitud
        """
        try:
            session = self.db.get_session()
            
            # Llamar función de búsqueda vectorial
            embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
            query = """
            SELECT * FROM search_similar_content(:embedding, :table_name, :limit)
            WHERE similarity >= :threshold
            ORDER BY similarity DESC
            """
            
            result = session.execute(
                query,
                {
                    "embedding": embedding_str,
                    "table_name": table_name,
                    "limit": limit,
                    "threshold": threshold
                }
            )
            
            results = []
            for row in result:
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "title": row[2] if len(row) > 2 else None,
                    "similarity": float(row[3])
                })
            
            return results
            
        except Exception as e:
            self.db.logger.error(f"Error en búsqueda vectorial: {e}")
            return []
        finally:
            session.close()
    
    def batch_update_embeddings(
        self,
        table_name: str,
        records_with_content: List[tuple],  # (id, content)
        embedding_function
    ) -> bool:
        """
        Actualiza embeddings en lote usando una función de embedding
        
        Args:
            table_name: Nombre de la tabla
            records_with_content: Lista de tuplas (id, content)
            embedding_function: Función que toma texto y retorna embedding
            
        Returns:
            True si la operación fue exitosa
        """
        try:
            session = self.db.get_session()
            
            # Importar funciones necesarias
            from database import Message, AgentMessage, KnowledgeBase
            
            table_models = {
                'messages': Message,
                'agent_messages': AgentMessage,
                'knowledge_base': KnowledgeBase
            }
            
            if table_name not in table_models:
                raise ValueError(f"Tabla no válida: {table_name}")
            
            model_class = table_models[table_name]
            
            for record_id, content in records_with_content:
                try:
                    # Generar embedding
                    embedding = embedding_function(content)
                    
                    # Actualizar registro
                    record = session.query(model_class).filter_by(id=record_id).first()
                    if record:
                        record.set_embedding(embedding)
                    
                except Exception as e:
                    self.db.logger.warning(f"Error actualizando embedding para ID {record_id}: {e}")
                    continue
            
            session.commit()
            self.db.logger.info(f"Embeddings actualizados en {table_name}")
            return True
            
        except Exception as e:
            session.rollback()
            self.db.logger.error(f"Error en actualización masiva: {e}")
            return False
        finally:
            session.close()
    
    def get_embedding_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas sobre embeddings"""
        try:
            session = self.db.get_session()
            
            # Importar modelos
            from database import Message, AgentMessage, KnowledgeBase
            
            tables = {
                'messages': Message,
                'agent_messages': AgentMessage,
                'knowledge_base': KnowledgeBase
            }
            
            stats = {}
            
            for table_name, model_class in tables.items():
                total = session.query(model_class).count()
                with_embeddings = session.query(model_class).filter(
                    model_class.embedding.isnot(None)
                ).count()
                
                stats[table_name] = {
                    'total_records': total,
                    'with_embeddings': with_embeddings,
                    'coverage_percentage': (with_embeddings / total * 100) if total > 0 else 0
                }
            
            return stats
            
        except Exception as e:
            self.db.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
        finally:
            session.close()

class ConfigManager:
    """Gestor de configuración"""
    
    @staticmethod
    def load_config_from_env() -> DatabaseConfig:
        """Carga configuración desde variables de entorno"""
        
        # URL de base de datos
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:password@localhost:5432/rag_database"
        )
        
        # Configuración de pool
        pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        return DatabaseConfig(
            url=database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle
        )
    
    @staticmethod
    def create_env_template():
        """Crea archivo .env de ejemplo"""
        env_content = """# Configuración de Base de Datos PostgreSQL con pgvector
# Copie este archivo como .env y configure sus valores

# URL de conexión a PostgreSQL
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/rag_database

# Configuración de pool de conexiones
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Configuración de embeddings (opcional)
OPENAI_API_KEY=sk-tu-clave-api
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIMENSION=1536
"""
        
        with open(".env.example", "w") as f:
            f.write(env_content)
        
        print("✅ Archivo .env.example creado")

def setup_database_from_env():
    """Configura y conecta base de datos desde variables de entorno"""
    config = ConfigManager.load_config_from_env()
    db_manager = DatabaseManager(config)
    
    if db_manager.connect():
        return db_manager
    else:
        raise RuntimeError("No se pudo conectar a la base de datos")

# Funciones de conveniencia para uso directo
def get_database_manager():
    """Obtiene gestor de base de datos configurado"""
    config = ConfigManager.load_config_from_env()
    return DatabaseManager(config)

def get_embedding_manager():
    """Obtiene gestor de embeddings"""
    db_manager = get_database_manager()
    db_manager.connect()
    return EmbeddingManager(db_manager)

if __name__ == "__main__":
    # Ejemplo de uso
    print("🛠️ Configuración de Base de Datos")
    
    # Crear archivo de ejemplo
    ConfigManager.create_env_template()
    
    # Test de configuración
    try:
        config = ConfigManager.load_config_from_env()
        print(f"✅ Configuración cargada:")
        print(f"   URL: {config.url}")
        print(f"   Pool size: {config.pool_size}")
        
        # Test de conexión
        db_manager = DatabaseManager(config)
        if db_manager.connect():
            print("✅ Conexión exitosa")
            
            # Test de embeddings
            embed_manager = EmbeddingManager(db_manager)
            stats = embed_manager.get_embedding_statistics()
            print(f"📊 Estadísticas: {stats}")
            
            db_manager.close()
        else:
            print("❌ Error de conexión")
            
    except Exception as e:
        print(f"❌ Error: {e}")