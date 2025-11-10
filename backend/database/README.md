# PostgreSQL + pgvector para Sistema RAG

Sistema completo de base de datos PostgreSQL con extensión pgvector para funcionalidades RAG (Retrieval-Augmented Generation). Soporta embeddings vectoriales para búsqueda semántica y recuperación de conocimiento.

## 🏗️ Estructura del Sistema

```
/workspace/backend/database/
├── database.py              # Modelos SQLAlchemy
├── config.py               # Configuración y utilidades
├── init_database.sql       # Esquema SQL completo
├── requirements.txt        # Dependencias
├── test_database.py       # Tests de validación
├── init_db.py             # Script de inicialización automatizada
├── test_connection.py     # Script de pruebas de conectividad
├── __init__.py            # Paquete Python
├── README.md              # Documentación
└── migrations/
    ├── 001_init_database.py      # Inicialización de tablas
    └── 002_vector_functions.py   # Funciones RAG avanzadas
```

## 📋 Características

- ✅ **PostgreSQL** con extensión pgvector
- ✅ **Embeddings vectoriales** para búsqueda semántica
- ✅ **Modelos SQLAlchemy** optimizados
- ✅ **Búsqueda por similitud coseno** eficiente
- ✅ **Índices IVFFlat** para rendimiento
- ✅ **Operaciones CRUD** completas
- ✅ **Actualización masiva** de embeddings
- ✅ **Sistema de migraciones** modular
- ✅ **Tests exhaustivos** de conectividad
- ✅ **Configuración flexible** por entorno

## 🚀 Inicio Rápido

### 1. Instalación de Dependencias

```bash
pip install -r database/requirements.txt
```

### 2. Configuración de Base de Datos

```bash
# Crear archivo .env
cp .env.example .env
# Editar .env con sus credenciales
```

### 3. Inicialización

```bash
# Script automatizado de inicialización (recomendado)
python3 init_db.py

# Con variables de entorno personalizadas
POSTGRES_HOST=localhost POSTGRES_PORT=5432 python3 init_db.py

# Scripts alternativos de inicialización
python migrations/001_init_database.py --database-url $DATABASE_URL --create-sample

# Crear funciones RAG avanzadas
python migrations/002_vector_functions.py --database-url $DATABASE_URL --create-functions
```

### 4. Validación

```bash
# Validación completa de todos los servicios (recomendado)
python3 test_connection.py

# Validación individual de servicios
python3 test_connection.py postgres
python3 test_connection.py redis
python3 test_connection.py api

# Modo interactivo
python3 test_connection.py interactive

# Tests tradicionales
python test_database.py --database-url $DATABASE_URL

# Test específico de embeddings
python test_database.py --database-url $DATABASE_URL --test embedding
```

## 📊 Esquema de Base de Datos

### Tabla: conversations
- **id**: Identificador único
- **session_id**: ID de sesión único
- **user_id**: Identificador de usuario
- **title**: Título de conversación
- **created_at/updated_at**: Timestamps
- **metadata**: Datos adicionales en JSON

### Tabla: messages
- **id**: Identificador único
- **conversation_id**: Referencia a conversación
- **role**: Rol del mensaje (user/assistant/system)
- **content**: Contenido del mensaje
- **tokens**: Número de tokens
- **embedding**: Vector de 1536 dimensiones

### Tabla: agent_messages
- **id**: Identificador único
- **conversation_id**: Referencia a conversación
- **agent_name**: Nombre del agente
- **message_type**: Tipo (reasoning/action/result/planning)
- **content**: Contenido
- **step_number**: Número de paso
- **embedding**: Vector de 1536 dimensiones

### Tabla: knowledge_base
- **id**: Identificador único
- **title**: Título del documento
- **content**: Contenido
- **source_type**: Tipo de fuente
- **source_url/source_file**: Origen del contenido
- **tags**: Array de etiquetas
- **embedding**: Vector de 1536 dimensiones

## 🔧 Uso del Sistema

### Conexión Básica

```python
from database.config import get_database_manager
from database.database import Conversation, Message

# Configurar y conectar
db_manager = get_database_manager()
db_manager.connect()

# Crear sesión
session = db_manager.get_session()

# Crear conversación
conversation = Conversation(
    session_id="session-123",
    user_id="user-456",
    title="Mi Conversación"
)
session.add(conversation)
session.commit()
```

### Manejo de Embeddings

```python
from database.config import get_embedding_manager

# Obtener gestor de embeddings
embed_manager = get_embedding_manager()

# Búsqueda por similitud
query_embedding = [0.1] * 1536  # Su embedding aquí
results = embed_manager.similarity_search(
    query_embedding=query_embedding,
    table_name="knowledge_base",
    limit=5,
    threshold=0.7
)

# Actualización masiva (simulada)
def mock_embedding_function(text):
    # Aquí integraría su modelo de embeddings real
    return [0.1] * 1536

records = [(1, "texto 1"), (2, "texto 2")]  # (id, contenido)
embed_manager.batch_update_embeddings(
    "knowledge_base", 
    records, 
    mock_embedding_function
)
```

### Búsqueda Semántica Directa

```python
# Búsqueda en mensajes
results = embed_manager.similarity_search(
    query_embedding=query_embedding,
    table_name="messages",
    limit=10,
    threshold=0.8
)

# Búsqueda en base de conocimiento
results = embed_manager.similarity_search(
    query_embedding=query_embedding,
    table_name="knowledge_base",
    limit=5,
    threshold=0.75
)
```

## 🛠️ Scripts de Automatización

### Script de Inicialización (init_db.py)

Script Python completo para inicialización automatizada de la base de datos con las siguientes características:

- ✅ **Configuración automática** de PostgreSQL con pgvector
- ✅ **Espera inteligente** hasta que la base de datos esté disponible
- ✅ **Creación de extensiones** (vector, uuid-ossp, pgcrypto)
- ✅ **Generación de tablas** con estructura optimizada
- ✅ **Creación de índices** para búsqueda vectorial eficiente
- ✅ **Configuración de triggers** para timestamps automáticos
- ✅ **Inserción de datos por defecto**
- ✅ **Logging detallado** del proceso completo
- ✅ **Estadísticas finales** de la base de datos

**Ejemplos de uso:**
```bash
# Inicialización completa
python3 init_db.py

# Solo probar conexión
from backend.database import DatabaseInitializer
initializer = DatabaseInitializer()
initializer.test_connection()

# Obtener estadísticas
stats = initializer.get_database_stats()
print(stats)
```

### Script de Validación (test_connection.py)

Script completo de validación de conectividad con soporte para:

- ✅ **PostgreSQL**: Conexión, pgvector, tablas, índices
- ✅ **Redis**: Ping, operaciones básicas, información del servidor
- ✅ **Backend API**: Endpoints de salud, tiempo de respuesta
- ✅ **Frontend**: Disponibilidad de la aplicación web
- ✅ **Prometheus**: Métricas de sistema
- ✅ **Grafana**: Estado del dashboard
- ✅ **Modo interactivo** con menú de selección
- ✅ **Reportes detallados** de estado

**Ejemplos de uso:**
```bash
# Validación completa
python3 test_connection.py

# Validación específica
python3 test_connection.py postgres
python3 test_connection.py redis
python3 test_connection.py api

# Modo interactivo
python3 test_connection.py interactive

# Uso programático
from backend.database import ConnectionTester
tester = ConnectionTester()
all_ok = tester.run_comprehensive_test()
print(f"Sistema operativo: {all_ok}")
```

## 🧪 Tests y Validación

### Tests Disponibles

```bash
# Test completo
python test_database.py --database-url $DATABASE_URL

# Tests específicos
python test_database.py --database-url $DATABASE_URL --test connection
python test_database.py --database-url $DATABASE_URL --test crud
python test_database.py --database-url $DATABASE_URL --test embedding
```

### Criterios de Validación

- ✅ **Conexión**: PostgreSQL accesible
- ✅ **pgvector**: Extensión vectorial disponible
- ✅ **Tablas**: Esquema completo creado
- ✅ **Índices**: Optimizaciones vectoriales activas
- ✅ **CRUD**: Operaciones básicas funcionales
- ⚠️ **Embeddings**: Funciones de vector disponibles
- ⚠️ **Rendimiento**: Consultas < 1 segundo

## 🔍 Funciones SQL Avanzadas

### search_similar_content()
```sql
SELECT * FROM search_similar_content(
    '[0.1,0.2,0.3,...]'::vector,  -- Query embedding
    'knowledge_base',             -- Tabla
    5                            -- Límite
);
```

### update_embeddings_batch()
```sql
SELECT update_embeddings_batch(
    'messages',                  -- Tabla
    ARRAY[1,2,3],               -- IDs
    ARRAY['[0.1,0.2,...]'::vector, '[0.4,0.5,...]'::vector]
);
```

## 📈 Optimizaciones de Rendimiento

### Índices Vectoriales
- **IVFFlat** con 100 listas para búsqueda eficiente
- **Índices GIN** para arrays de tags
- **Índices estándar** en campos de búsqueda frecuente

### Configuración de Pool
- **pool_size**: 10 conexiones simultáneas
- **max_overflow**: 20 conexiones adicionales
- **pool_timeout**: 30 segundos
- **pool_recycle**: 3600 segundos

## 🛠️ Configuración por Entorno

### Desarrollo Local
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag_dev
DB_POOL_SIZE=5
```

### Producción
```bash
DATABASE_URL=postgresql://user:pass@prod-server:5432/rag_prod
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión PostgreSQL | `postgresql://postgres:password@localhost:5432/rag_database` |
| `DB_POOL_SIZE` | Tamaño del pool de conexiones | `10` |
| `DB_MAX_OVERFLOW` | Conexiones adicionales | `20` |
| `DB_POOL_TIMEOUT` | Timeout de pool (segundos) | `30` |
| `DB_POOL_RECYCLE` | Reciclaje de conexiones (segundos) | `3600` |

## 🔗 Integración con RAG

### Flujo de Trabajo Típico

1. **Ingesta de Conocimiento**
   ```python
   # Agregar documentos a la base de conocimiento
   knowledge = KnowledgeBase(
       title="Documento importante",
       content="Contenido del documento...",
       source_type="document",
       tags=["importante", "referencia"]
   )
   session.add(knowledge)
   session.commit()
   ```

2. **Generación de Embeddings**
   ```python
   # Generar y almacenar embeddings
   embedding = generate_embedding(knowledge.content)
   knowledge.set_embedding(embedding)
   session.commit()
   ```

3. **Búsqueda Semántica**
   ```python
   # Buscar contenido relevante
   query_embedding = generate_embedding(user_query)
   relevant_docs = embed_manager.similarity_search(
       query_embedding,
       "knowledge_base",
       limit=5
   )
   ```

4. **Generación de Respuesta**
   ```python
   # Usar contexto recuperado para generar respuesta
   context = "\n".join([doc.content for doc in relevant_docs])
   response = llm.generate(user_query, context=context)
   ```

## 📋 Requisitos del Sistema

### PostgreSQL
- **Versión**: 12+ (recomendado 15+)
- **Extensión**: pgvector
- **Memoria**: Mínimo 2GB RAM
- **Espacio**: Variable según volumen de datos

### Python
- **Versión**: 3.8+
- **Extensiones**: sqlalchemy, psycopg2-binary, numpy

### Modelo de Embeddings
- **Dimensión**: 1536 (OpenAI standard)
- **Formatos soportados**: OpenAI, Hugging Face, locales

## 🚀 Script de Configuración Automatizada

### setup.sh

Script Bash completo para configuración automatizada de todo el entorno del sistema de agentes.

**Características:**
- ✅ **Verificación de dependencias** (Docker, Docker Compose, Python, Node.js)
- ✅ **Creación de archivos de configuración** (.env, docker-compose)
- ✅ **Configuración de servicios** (PostgreSQL, Redis, Prometheus, Grafana)
- ✅ **Instalación de dependencias** Python y Node.js
- ✅ **Inicio automático** de todos los contenedores
- ✅ **Inicialización de base de datos** con pgvector
- ✅ **Validación completa** de servicios
- ✅ **Información de acceso** al finalizar

**Opciones de uso:**
```bash
# Configuración completa (recomendado)
./setup.sh setup

# Solo verificar dependencias
./setup.sh deps

# Solo iniciar servicios
./setup.sh services

# Solo inicializar base de datos
./setup.sh init-db

# Solo probar conexiones
./setup.sh test

# Mostrar información de acceso
./setup.sh info

# Mostrar ayuda
./setup.sh help
```

**Flujo de configuración:**
1. Verificar Docker y Docker Compose
2. Crear archivo .env con configuración por defecto
3. Crear directorios necesarios
4. Configurar PostgreSQL con pgvector
5. Configurar Redis
6. Configurar Prometheus
7. Configurar Grafana
8. Instalar dependencias de Python
9. Construir y levantar contenedores
10. Inicializar base de datos
11. Probar conexiones
12. Mostrar información de acceso

**Salida esperada:**
```
===============================================================
CONFIGURACIÓN COMPLETA DEL SISTEMA
===============================================================
✅ Docker está instalado y ejecutándose
✅ Docker Compose está disponible
✅ Python3 está disponible
✅ Node.js está disponible

📋 Servicios disponibles:
├── Frontend (React):     http://localhost:3000
├── Backend API (FastAPI): http://localhost:8000
├── PostgreSQL:           localhost:5432
├── Redis:                localhost:6379
├── Prometheus:           http://localhost:9090
└── Grafana:              http://localhost:3001

🎯 ¡Inicialización completada exitosamente!
```

## 🐛 Troubleshooting

### Error: "relation does not exist"
```bash
# Ejecutar inicialización
python migrations/001_init_database.py --database-url $DATABASE_URL
```

### Error: "undefined table"
```bash
# Verificar esquema y extensión
python test_database.py --database-url $DATABASE_URL --test connection
```

### Error: "pgvector extension not found"
```sql
-- Ejecutar manualmente en PostgreSQL
CREATE EXTENSION vector;
```

### Problemas con Scripts de Automatización

#### Error: "No module named 'psycopg2'"
```bash
# Instalar dependencias
pip3 install psycopg2-binary redis requests
# o desde requirements.txt
pip3 install -r /workspace/backend/requirements.txt
```

#### Error: "Connection refused" en init_db.py
```bash
# Verificar que PostgreSQL esté ejecutándose
docker ps | grep postgres

# Verificar logs
docker-compose logs postgres

# Usar script de configuración automatizada
./setup.sh services
```

#### Error: "pgvector extension not found"
```bash
# Verificar con test_connection.py
python3 test_connection.py postgres

# Si falla, verificar imagen de PostgreSQL
docker-compose down
docker system prune -f
./setup.sh setup
```

#### Error: "Redis connection failed"
```bash
# Probar conectividad
python3 test_connection.py redis

# Reiniciar Redis
docker-compose restart redis
```

### Rendimiento Lento
```bash
# Recrear índices IVFFlat
DROP INDEX IF EXISTS idx_knowledge_base_embedding_ivfflat;
CREATE INDEX idx_knowledge_base_embedding_ivfflat 
ON knowledge_base USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

## 📞 Soporte

Para problemas o consultas:
1. Ejecutar `test_database.py` para diagnóstico
2. Verificar logs de PostgreSQL
3. Validar configuración de entorno
4. Consultar documentación de pgvector

---

**Estado**: ✅ Implementación completa lista para producción  
**Versión**: 1.0.0  
**Última actualización**: 2025-11-04