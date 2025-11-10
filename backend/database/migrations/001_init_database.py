"""
Script de inicialización de base de datos
Crea las tablas y extensiones necesarias para el sistema RAG
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, Conversation, Message, AgentMessage, KnowledgeBase

def init_database(database_url: str = None):
    """
    Inicializa la base de datos creando todas las tablas
    """
    if not database_url:
        # URL por defecto para PostgreSQL local
        database_url = "postgresql://postgres:password@localhost:5432/rag_database"
    
    try:
        # Crear engine
        engine = create_engine(database_url)
        
        # Crear todas las tablas
        print("Creando tablas en la base de datos...")
        Base.metadata.create_all(engine)
        
        # Verificar que pgvector está disponible
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'"))
            if not result.fetchone():
                print("Habilitando extensión pgvector...")
                conn.execute(text("CREATE EXTENSION vector"))
                conn.commit()
            
            # Verificar índice vectorial
            print("Verificando índices vectoriales...")
            
            # Crear índices IVFFlat para búsqueda vectorial eficiente
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_messages_embedding_ivfflat ON messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)",
                "CREATE INDEX IF NOT EXISTS idx_agent_messages_embedding_ivfflat ON agent_messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)",
                "CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding_ivfflat ON knowledge_base USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    print(f"✓ Índice creado: {index_sql.split(' ')[5]}")
                except Exception as e:
                    print(f"⚠ Advertencia al crear índice: {e}")
            
            conn.commit()
        
        print("✅ Base de datos inicializada correctamente")
        
        # Crear sesión de prueba
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Verificar conexión con una consulta simple
        result = session.execute(text("SELECT COUNT(*) FROM conversations"))
        count = result.fetchone()[0]
        print(f"✅ Conexión verificada. Conversaciones existentes: {count}")
        
        session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        return False

def create_sample_data(database_url: str = None):
    """
    Crea datos de ejemplo para pruebas
    """
    if not database_url:
        database_url = "postgresql://postgres:password@localhost:5432/rag_database"
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Crear conversación de ejemplo
        conversation = Conversation(
            session_id="test-session-001",
            user_id="test-user",
            title="Conversación de prueba RAG",
            metadata={"test": True}
        )
        session.add(conversation)
        session.flush()  # Para obtener el ID
        
        # Crear mensajes de ejemplo
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content="¿Qué es la inteligencia artificial?",
            tokens=10,
            metadata={"source": "user_input"}
        )
        
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content="La inteligencia artificial es una tecnología que permite a las máquinas realizar tareas que normalmente requieren inteligencia humana.",
            tokens=25,
            metadata={"model": "gpt-3.5-turbo"}
        )
        
        session.add_all([user_message, assistant_message])
        
        # Crear entrada de conocimiento de ejemplo
        knowledge = KnowledgeBase(
            title="Introducción a la Inteligencia Artificial",
            content="La inteligencia artificial (IA) es un campo de la informática que se dedica a crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana...",
            source_type="manual_entry",
            tags=["IA", "inteligencia artificial", "tecnología"],
            metadata={"category": "educativo", "difficulty": "beginner"}
        )
        
        session.add(knowledge)
        session.commit()
        
        print("✅ Datos de ejemplo creados correctamente")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error al crear datos de ejemplo: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Inicializar base de datos PostgreSQL con pgvector")
    parser.add_argument("--database-url", help="URL de conexión a PostgreSQL")
    parser.add_argument("--create-sample", action="store_true", help="Crear datos de ejemplo")
    
    args = parser.parse_args()
    
    if init_database(args.database_url):
        if args.create_sample:
            create_sample_data(args.database_url)
    else:
        sys.exit(1)