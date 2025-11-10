-- Esquema de base de datos PostgreSQL con pgvector para RAG
-- Crear extensión pgvector para embeddings vectoriales
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de conversaciones
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    title VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Tabla de mensajes de usuario
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536)  -- Dimensión estándar para OpenAI embeddings
);

-- Tabla de mensajes de agentes
CREATE TABLE agent_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    message_type VARCHAR(50) NOT NULL CHECK (message_type IN ('reasoning', 'action', 'result', 'planning')),
    content TEXT NOT NULL,
    step_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536)
);

-- Tabla de base de conocimiento para RAG
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('document', 'web_page', 'manual_entry', 'generated')),
    source_url VARCHAR(1000),
    source_file VARCHAR(500),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536)  -- Vector para búsqueda semántica
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_embedding ON messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_agent_messages_conversation_id ON agent_messages(conversation_id);
CREATE INDEX idx_agent_messages_created_at ON agent_messages(created_at);
CREATE INDEX idx_agent_messages_embedding ON agent_messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_knowledge_base_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_knowledge_base_tags ON knowledge_base USING GIN (tags);
CREATE INDEX idx_knowledge_base_source_type ON knowledge_base(source_type);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar updated_at
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();