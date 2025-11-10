"""
Test de conectividad y funcionalidad para base de datos PostgreSQL con pgvector
Valida la configuración y operaciones básicas del sistema RAG
"""

import os
import sys
import json
import time
from typing import List
import numpy as np

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base, Conversation, Message, AgentMessage, KnowledgeBase

class DatabaseTester:
    """Tester para validar la funcionalidad de la base de datos"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or self._get_default_db_url()
        self.engine = None
        self.session = None
        
    def _get_default_db_url(self) -> str:
        """Obtiene la URL de base de datos desde variables de entorno o usa默认值"""
        return os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:password@localhost:5432/rag_database"
        )
    
    def connect(self) -> bool:
        """Establece conexión con la base de datos"""
        try:
            self.engine = create_engine(self.database_url)
            self.session = sessionmaker(bind=self.engine)()
            
            # Test de conexión básica
            result = self.session.execute(text("SELECT 1"))
            result.fetchone()
            
            print("✅ Conexión establecida correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_pgvector_extension(self) -> bool:
        """Verifica que pgvector esté disponible"""
        try:
            result = self.session.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            
            if result.fetchone():
                print("✅ Extensión pgvector disponible")
                return True
            else:
                print("⚠️ pgvector no está instalado. Ejecute: CREATE EXTENSION vector;")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando pgvector: {e}")
            return False
    
    def test_table_creation(self) -> bool:
        """Verifica que todas las tablas existan"""
        try:
            tables_to_check = [
                'conversations', 'messages', 'agent_messages', 'knowledge_base'
            ]
            
            for table in tables_to_check:
                result = self.session.execute(
                    text(f"SELECT COUNT(*) FROM {table} WHERE 1=0")
                )
                print(f"✅ Tabla '{table}' existe")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verificando tablas: {e}")
            return False
    
    def test_vector_columns(self) -> bool:
        """Verifica que las columnas vector existen"""
        try:
            vector_columns_query = """
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE data_type = 'text' 
            AND column_name = 'embedding'
            AND table_schema = 'public'
            """
            
            result = self.session.execute(text(vector_columns_query))
            embeddings_found = 0
            
            for row in result:
                print(f"✅ Columna embedding encontrada en tabla '{row[0]}'")
                embeddings_found += 1
            
            if embeddings_found >= 3:  # messages, agent_messages, knowledge_base
                print("✅ Todas las columnas vector configuradas correctamente")
                return True
            else:
                print(f"⚠️ Solo {embeddings_found} tablas tienen columnas embedding")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando columnas vector: {e}")
            return False
    
    def test_crud_operations(self) -> bool:
        """Test de operaciones CRUD básicas"""
        try:
            # Crear conversación
            conversation = Conversation(
                session_id=f"test-{int(time.time())}",
                user_id="test-user",
                title="Test de funcionalidades"
            )
            self.session.add(conversation)
            self.session.flush()
            
            # Crear mensaje
            message = Message(
                conversation_id=conversation.id,
                role="user",
                content="Mensaje de prueba",
                tokens=5
            )
            self.session.add(message)
            
            # Crear mensaje de agente
            agent_message = AgentMessage(
                conversation_id=conversation.id,
                agent_name="test-agent",
                message_type="reasoning",
                content="Razonamiento de prueba",
                step_number=1
            )
            self.session.add(agent_message)
            
            # Crear entrada de conocimiento
            knowledge = KnowledgeBase(
                title="Documento de prueba",
                content="Contenido de prueba para testing",
                source_type="manual_entry",
                tags=["test", "prueba"]
            )
            self.session.add(knowledge)
            
            self.session.commit()
            
            # Verificar lectura
            retrieved_conversation = self.session.query(Conversation).filter_by(
                id=conversation.id
            ).first()
            
            if retrieved_conversation:
                print("✅ Operaciones CRUD funcionan correctamente")
                
                # Limpiar datos de prueba
                self.session.delete(retrieved_conversation)
                self.session.commit()
                return True
            else:
                print("❌ Error en operaciones de lectura")
                return False
                
        except Exception as e:
            print(f"❌ Error en operaciones CRUD: {e}")
            self.session.rollback()
            return False
    
    def test_embedding_operations(self) -> bool:
        """Test de operaciones con embeddings"""
        try:
            # Crear datos con embeddings simulados
            conversation = Conversation(
                session_id=f"embed-test-{int(time.time())}",
                user_id="test-user"
            )
            self.session.add(conversation)
            self.session.flush()
            
            # Simular embeddings (normalmente vendrían de un modelo)
            test_embedding = [0.1] * 1536  # 1536 dimensiones estándar
            
            # Mensaje con embedding
            message = Message(
                conversation_id=conversation.id,
                role="user",
                content="Mensaje para test de embedding",
                tokens=10
            )
            message.set_embedding(test_embedding)
            self.session.add(message)
            
            # Conocimiento con embedding
            knowledge = KnowledgeBase(
                title="Documento con embedding",
                content="Contenido de documento para test vectorial",
                source_type="manual_entry",
                tags=["embedding", "test"]
            )
            knowledge.set_embedding(test_embedding)
            self.session.add(knowledge)
            
            self.session.commit()
            
            # Verificar embeddings
            retrieved_message = self.session.query(Message).filter_by(
                id=message.id
            ).first()
            
            retrieved_knowledge = self.session.query(KnowledgeBase).filter_by(
                id=knowledge.id
            ).first()
            
            if (retrieved_message.get_embedding() == test_embedding and 
                retrieved_knowledge.get_embedding() == test_embedding):
                print("✅ Operaciones con embeddings funcionan correctamente")
                
                # Limpiar
                self.session.delete(conversation)
                self.session.commit()
                return True
            else:
                print("❌ Error en almacenamiento/recuperación de embeddings")
                return False
                
        except Exception as e:
            print(f"❌ Error en operaciones con embeddings: {e}")
            self.session.rollback()
            return False
    
    def test_search_function(self) -> bool:
        """Test de función de búsqueda vectorial"""
        try:
            # Verificar que la función de búsqueda existe
            result = self.session.execute(text(
                "SELECT routine_name FROM information_schema.routines "
                "WHERE routine_name = 'search_similar_content'"
            ))
            
            if result.fetchone():
                print("✅ Función de búsqueda vectorial disponible")
                return True
            else:
                print("⚠️ Función de búsqueda no encontrada (ejecute migrations/002_vector_functions.py)")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando función de búsqueda: {e}")
            return False
    
    def test_performance(self) -> bool:
        """Test básico de rendimiento"""
        try:
            start_time = time.time()
            
            # Test de consulta simple
            result = self.session.execute(text("SELECT COUNT(*) FROM conversations"))
            result.fetchone()
            
            query_time = time.time() - start_time
            
            if query_time < 1.0:  # Menos de 1 segundo
                print(f"✅ Rendimiento aceptable ({query_time:.3f}s)")
                return True
            else:
                print(f"⚠️ Consulta lenta ({query_time:.3f}s)")
                return False
                
        except Exception as e:
            print(f"❌ Error en test de rendimiento: {e}")
            return False
    
    def cleanup(self):
        """Limpia recursos"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
    
    def run_all_tests(self) -> dict:
        """Ejecuta todos los tests y retorna resultados"""
        print("🧪 Iniciando tests de base de datos PostgreSQL + pgvector")
        print("=" * 60)
        
        results = {}
        
        tests = [
            ("Conexión", self.connect),
            ("Extensión pgvector", self.test_pgvector_extension),
            ("Creación de tablas", self.test_table_creation),
            ("Columnas vector", self.test_vector_columns),
            ("Operaciones CRUD", self.test_crud_operations),
            ("Operaciones embeddings", self.test_embedding_operations),
            ("Función de búsqueda", self.test_search_function),
            ("Rendimiento", self.test_performance),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Test: {test_name}")
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ Error en test '{test_name}': {e}")
                results[test_name] = False
        
        self.cleanup()
        
        # Resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE TESTS")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nResultado: {passed}/{total} tests pasaron")
        
        if passed == total:
            print("🎉 ¡Todos los tests pasaron! Base de datos lista para RAG")
        else:
            print("⚠️ Algunos tests fallaron. Revise la configuración")
        
        return results

def main():
    """Función principal para ejecutar tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test de base de datos PostgreSQL con pgvector")
    parser.add_argument("--database-url", help="URL de conexión a PostgreSQL")
    parser.add_argument("--test", choices=["all", "connection", "crud", "embedding"], 
                       default="all", help="Tipo de test a ejecutar")
    
    args = parser.parse_args()
    
    tester = DatabaseTester(args.database_url)
    
    try:
        if args.test == "all":
            tester.run_all_tests()
        elif args.test == "connection":
            if tester.connect():
                print("✅ Test de conexión exitoso")
            else:
                sys.exit(1)
        elif args.test == "crud":
            if tester.connect() and tester.test_crud_operations():
                print("✅ Test CRUD exitoso")
            else:
                sys.exit(1)
        elif args.test == "embedding":
            if tester.connect() and tester.test_embedding_operations():
                print("✅ Test de embeddings exitoso")
            else:
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()