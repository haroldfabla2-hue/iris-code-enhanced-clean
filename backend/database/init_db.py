#!/usr/bin/env python3
"""
Script de inicialización de base de datos PostgreSQL con pgvector
Configura la base de datos, índices y estructuras necesarias para el sistema de agentes.
"""

import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from typing import Optional, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Inicializador de base de datos PostgreSQL con pgvector"""
    
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 database: str = None,
                 user: str = None,
                 password: str = None):
        """
        Inicializar el configurador de base de datos
        
        Args:
            host: Host de PostgreSQL (por defecto desde env)
            port: Puerto de PostgreSQL (por defecto desde env)
            database: Nombre de la base de datos (por defecto desde env)
            user: Usuario de PostgreSQL (por defecto desde env)
            password: Contraseña de PostgreSQL (por defecto desde env)
        """
        self.config = {
            'host': host or os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(port or os.getenv('POSTGRES_PORT', '5432')),
            'database': database or os.getenv('POSTGRES_DB', 'agente_db'),
            'user': user or os.getenv('POSTGRES_USER', 'postgres'),
            'password': password or os.getenv('POSTGRES_PASSWORD', 'postgres_secure_password')
        }
        
    def _get_connection(self, use_db: bool = True) -> psycopg2.extensions.connection:
        """Establecer conexión a PostgreSQL"""
        try:
            if use_db:
                conn_str = f"host='{self.config['host']}' port='{self.config['port']}' database='{self.config['database']}' user='{self.config['user']}' password='{self.config['password']}'"
            else:
                conn_str = f"host='{self.config['host']}' port='{self.config['port']}' user='{self.config['user']}' password='{self.config['password']}'"
            
            conn = psycopg2.connect(conn_str)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return conn
        except Exception as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            raise
    
    def wait_for_db(self, max_retries: int = 30, delay: float = 2.0) -> bool:
        """
        Esperar hasta que la base de datos esté disponible
        
        Args:
            max_retries: Número máximo de intentos
            delay: Tiempo de espera entre intentos
            
        Returns:
            True si la conexión es exitosa
        """
        logger.info(f"Esperando conexión a PostgreSQL en {self.config['host']}:{self.config['port']}...")
        
        for attempt in range(max_retries):
            try:
                conn = self._get_connection(use_db=False)
                conn.close()
                logger.info("✅ Conexión a PostgreSQL establecida")
                return True
            except Exception as e:
                logger.warning(f"Intento {attempt + 1}/{max_retries} falló: {e}")
                time.sleep(delay)
        
        logger.error("❌ No se pudo establecer conexión a PostgreSQL")
        return False
    
    def test_connection(self) -> bool:
        """Probar la conexión a la base de datos"""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                logger.info(f"✅ Conectado a PostgreSQL: {version[0]}")
                
                # Verificar extensión pgvector
                cur.execute("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector';")
                has_pgvector = cur.fetchone()[0] > 0
                
                if has_pgvector:
                    logger.info("✅ Extensión pgvector disponible")
                else:
                    logger.warning("⚠️  Extensión pgvector no encontrada")
                
                # Verificar tablas existentes
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name;
                """)
                tables = cur.fetchall()
                logger.info(f"📋 Tablas existentes: {len(tables)}")
                for table in tables:
                    logger.info(f"  - {table[0]}")
            
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error probando conexión: {e}")
            return False
    
    def create_extensions(self) -> bool:
        """Crear extensiones necesarias"""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Habilitar pgvector
                logger.info("🔧 Habilitando extensión pgvector...")
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                
                # Habilitar uuid-ossp para UUIDs
                logger.info("🔧 Habilitando extensión uuid-ossp...")
                cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
                
                # Habilitar pgcrypto para hash y cifrado
                logger.info("🔧 Habilitando extensión pgcrypto...")
                cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
                
                logger.info("✅ Extensiones creadas correctamente")
            
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error creando extensiones: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Crear las tablas principales del sistema"""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Tabla de documentos fuente
                logger.info("📝 Creando tabla source_documents...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS source_documents (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        content TEXT NOT NULL,
                        metadata JSONB,
                        hash TEXT UNIQUE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Tabla de chunks con embeddings
                logger.info("🔢 Creando tabla document_chunks...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        doc_id UUID REFERENCES source_documents(id) ON DELETE CASCADE,
                        content TEXT NOT NULL,
                        embedding vector(768),
                        metadata JSONB,
                        chunk_index INTEGER,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Tabla de colecciones
                logger.info("📁 Creando tabla collections...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS collections (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Tabla de relación chunks-collections
                logger.info("🔗 Creando tabla chunk_collections...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chunk_collections (
                        chunk_id UUID REFERENCES document_chunks(id) ON DELETE CASCADE,
                        collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
                        PRIMARY KEY (chunk_id, collection_id)
                    );
                """)
                
                # Tabla de sesiones de agentes
                logger.info("🎭 Creando tabla agent_sessions...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS agent_sessions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        conversation_id TEXT UNIQUE NOT NULL,
                        user_id TEXT,
                        status TEXT DEFAULT 'active',
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Tabla de snapshots de estado
                logger.info("💾 Creando tabla state_snapshots...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS state_snapshots (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        conversation_id TEXT NOT NULL,
                        phase TEXT NOT NULL,
                        state JSONB NOT NULL,
                        checksum TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                logger.info("✅ Tablas creadas correctamente")
            
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            return False
    
    def create_indexes(self) -> bool:
        """Crear índices para optimización de consultas"""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                logger.info("🔍 Creando índices para búsqueda vectorial...")
                
                # Índice HNSW para búsqueda vectorial
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
                    ON document_chunks USING hnsw (embedding vector_cosine_ops);
                """)
                
                logger.info("🔍 Creando índices para búsquedas frecuentes...")
                
                # Índices para sesiones de agentes
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_agent_sessions_conversation_id 
                    ON agent_sessions(conversation_id);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_agent_sessions_user_id 
                    ON agent_sessions(user_id);
                """)
                
                # Índices para snapshots
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_state_snapshots_conversation_id 
                    ON state_snapshots(conversation_id);
                """)
                
                # Índices para chunks
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_document_chunks_doc_id 
                    ON document_chunks(doc_id);
                """)
                
                # Índices para colecciones
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_collections_name 
                    ON collections(name);
                """)
                
                logger.info("✅ Índices creados correctamente")
            
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error creando índices: {e}")
            return False
    
    def create_functions_and_triggers(self) -> bool:
        """Crear funciones y triggers necesarios"""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                logger.info("⚙️ Creando función para actualizar timestamps...")
                
                # Función para actualizar timestamp
                cur.execute("""
                    CREATE OR REPLACE FUNCTION update_updated_at_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = NOW();
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';
                """)
                
                logger.info("⚙️ Creando triggers...")
                
                # Triggers para auto-actualizar timestamps
                cur.execute("""
                    CREATE TRIGGER update_source_documents_updated_at 
                    BEFORE UPDATE ON source_documents
                    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
                """)
                
                cur.execute("""
                    CREATE TRIGGER update_agent_sessions_updated_at 
                    BEFORE UPDATE ON agent_sessions
                    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
                """)
                
                logger.info("✅ Funciones y triggers creados correctamente")
            
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error creando funciones y triggers: {e}")
            return False
    
    def insert_default_data(self) -> bool:
        """Insertar datos por defecto"""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                logger.info("📝 Insertando datos por defecto...")
                
                # Insertar colección por defecto
                cur.execute("""
                    INSERT INTO collections (name, description, metadata) 
                    VALUES (
                        'default',
                        'Colección por defecto para conocimiento general',
                        '{"type": "default", "auto_created": true}'
                    ) ON CONFLICT (name) DO NOTHING;
                """)
                
                logger.info("✅ Datos por defecto insertados correctamente")
            
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error insertando datos por defecto: {e}")
            return False
    
    def initialize_database(self) -> bool:
        """Ejecutar la inicialización completa de la base de datos"""
        logger.info("🚀 Iniciando configuración de base de datos...")
        
        # Esperar a que PostgreSQL esté disponible
        if not self.wait_for_db():
            return False
        
        # Crear extensiones
        if not self.create_extensions():
            return False
        
        # Crear tablas
        if not self.create_tables():
            return False
        
        # Crear índices
        if not self.create_indexes():
            return False
        
        # Crear funciones y triggers
        if not self.create_functions_and_triggers():
            return False
        
        # Insertar datos por defecto
        if not self.insert_default_data():
            return False
        
        # Probar conexión final
        if not self.test_connection():
            return False
        
        logger.info("🎉 ¡Base de datos inicializada correctamente!")
        return True
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos"""
        try:
            conn = self._get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                stats = {}
                
                # Contar tablas
                cur.execute("""
                    SELECT COUNT(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
                stats['total_tables'] = cur.fetchone()['table_count']
                
                # Contar registros por tabla
                tables = ['source_documents', 'document_chunks', 'collections', 
                         'chunk_collections', 'agent_sessions', 'state_snapshots']
                
                for table in tables:
                    try:
                        cur.execute(f"SELECT COUNT(*) as count FROM {table};")
                        result = cur.fetchone()
                        stats[f'{table}_count'] = result['count'] if result else 0
                    except:
                        stats[f'{table}_count'] = 0
                
                return stats
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

def main():
    """Función principal"""
    try:
        # Crear inicializador
        initializer = DatabaseInitializer()
        
        # Ejecutar inicialización
        success = initializer.initialize_database()
        
        if success:
            # Mostrar estadísticas
            stats = initializer.get_database_stats()
            logger.info("📊 Estadísticas de la base de datos:")
            for key, value in stats.items():
                logger.info(f"  {key}: {value}")
            
            logger.info("🎯 ¡Inicialización completada exitosamente!")
            return 0
        else:
            logger.error("💥 Error durante la inicialización")
            return 1
            
    except KeyboardInterrupt:
        logger.info("⏹️ Inicialización cancelada por el usuario")
        return 1
    except Exception as e:
        logger.error(f"💥 Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit(main())