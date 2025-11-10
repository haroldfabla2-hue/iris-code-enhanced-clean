"""
Test Server Completo con Assets y Memory API
Incluye todos los endpoints para testing completo
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime, timedelta
import random
import string

# Crear aplicación FastAPI
app = FastAPI(
    title="IRIS Complete Test Server",
    description="Servidor de prueba completo con Assets y Memory API",
    version="2.0.0-complete-test"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datos simulados para Memory API
memory_data = {
    "total_memories": 0,
    "memories": [],
    "stats": {
        "total_memories": 0,
        "memories_by_type": {},
        "memories_by_user": {},
        "recent_activity": {
            "searches_today": 0,
            "stores_today": 0,
            "last_search": None,
            "last_store": None
        },
        "storage_stats": {
            "total_size_mb": 0,
            "average_size_kb": 0,
            "oldest_memory": None,
            "newest_memory": None
        }
    }
}

# Pydantic models para Memory API
class MemorySearchRequest(BaseModel):
    query: str
    search_type: str = "semantic"
    limit: int = 10
    time_range: Optional[str] = None
    conversation_id: Optional[str] = None
    content_type: Optional[str] = None
    user_id: Optional[str] = None

class MemoryStoreRequest(BaseModel):
    content: str
    content_type: str = "text"
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class MemoryStoreResponse(BaseModel):
    memory_id: str
    status: str
    stored_at: str
    metadata: Dict[str, Any]

class MemoryClearRequest(BaseModel):
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    older_than: Optional[str] = None

# Modelos para Assets API
class AssetGenerationRequest(BaseModel):
    prompt: str
    category: Optional[str] = "branding"
    format_type: Optional[str] = "svg"
    style: str = "modern"
    requirements: Dict[str, Any] = {}
    stream: bool = False

class AssetResponse(BaseModel):
    generation_id: str
    status: str
    timestamp: str
    category: str
    format: str
    files: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None
    preview_url: Optional[str] = None

# ENDPOINTS DE HEALTH
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "server": "IRIS Complete Test Server",
        "version": "2.0.0-complete-test",
        "endpoints": {
            "assets_categories": "✅ ACTIVO",
            "assets_generate": "✅ ACTIVO",
            "assets_history": "✅ ACTIVO",
            "memory_search": "✅ ACTIVO",
            "memory_store": "✅ ACTIVO",
            "memory_stats": "✅ ACTIVO",
            "memory_clear": "✅ ACTIVO"
        },
        "timestamp": datetime.now().isoformat()
    }

# ENDPOINTS DE ASSETS API
@app.get("/api/v1/assets/categories")
async def get_asset_categories():
    return {
        "status": "success",
        "categories": [
            "branding", "mobile_ui", "marketing", 
            "saas_platform", "ecommerce", "executive", "ai_stress_test"
        ],
        "total": 7
    }

@app.post("/api/v1/assets/generate", response_model=AssetResponse)
async def generate_asset(request: AssetGenerationRequest):
    # Simular generación de asset
    await asyncio.sleep(1)  # Simular procesamiento
    
    generation_id = f"asset_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
    timestamp = datetime.now().isoformat()
    
    # Generar contenido SVG simulado
    svg_content = f'''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
    <circle cx="100" cy="100" r="80" fill="{random.choice(['#6366f1', '#8b5cf6', '#06b6d4', '#10b981'])}"/>
    <text x="100" y="110" font-family="Arial" font-size="16" text-anchor="middle" fill="white">IRIS</text>
    </svg>'''
    
    asset = AssetResponse(
        generation_id=generation_id,
        status="success",
        timestamp=timestamp,
        category=request.category or "branding",
        format=request.format_type or "svg",
        files=[{
            "filename": f"generated_asset_{generation_id.split('_')[-1]}.svg",
            "content": svg_content,
            "type": "svg",
            "size": len(svg_content)
        }],
        metadata={
            "prompt": request.prompt,
            "style": request.style,
            "generation_method": "simulated"
        }
    )
    
    return asset

@app.get("/api/v1/assets/history")
async def get_asset_history(limit: int = 50):
    return {
        "status": "success",
        "history": [],
        "total": 0
    }

# ENDPOINTS DE MEMORY API
@app.get("/api/v1/memory/search")
async def search_memory_get(
    query: str,
    search_type: str = "semantic",
    limit: int = 10,
    time_range: Optional[str] = None,
    conversation_id: Optional[str] = None,
    content_type: Optional[str] = None,
    user_id: Optional[str] = None
):
    # Simular búsqueda en memoria
    await asyncio.sleep(0.5)  # Simular búsqueda
    
    # Generar resultados simulados basados en la query
    results = []
    if query.lower() in ["proyecto", "project", "react"]:
        results = [
            {
                "content": "Proyecto React Dashboard - configuración de componentes y estado global",
                "content_type": "code",
                "relevance_score": 0.95,
                "stored_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "memory_id": "mem_proj_001",
                "metadata": {"project": "dashboard", "tech": "react"},
                "tags": ["react", "dashboard", "frontend"]
            }
        ]
    elif query.lower() in ["api", "endpoint", "backend"]:
        results = [
            {
                "content": "Configuración de API REST con FastAPI y endpoints de assets",
                "content_type": "config",
                "relevance_score": 0.88,
                "stored_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                "memory_id": "mem_api_001",
                "metadata": {"framework": "fastapi", "domain": "backend"},
                "tags": ["api", "fastapi", "backend"]
            }
        ]
    
    memory_data["stats"]["recent_activity"]["searches_today"] += 1
    memory_data["stats"]["recent_activity"]["last_search"] = datetime.now().isoformat()
    
    return {
        "query": query,
        "search_type": search_type,
        "total_results": len(results),
        "results": results,
        "search_metadata": {
            "execution_time_ms": 500,
            "search_engine": "simulated_rag",
            "filters_applied": {
                "time_range": time_range,
                "conversation_id": conversation_id,
                "content_type": content_type,
                "user_id": user_id
            }
        },
        "execution_time_ms": 500
    }

@app.post("/api/v1/memory/search")
async def search_memory_post(request: MemorySearchRequest):
    # Usar el mismo endpoint GET internamente
    return await search_memory_get(
        query=request.query,
        search_type=request.search_type,
        limit=request.limit,
        time_range=request.time_range,
        conversation_id=request.conversation_id,
        content_type=request.content_type,
        user_id=request.user_id
    )

@app.post("/api/v1/memory/store", response_model=MemoryStoreResponse)
async def store_memory(request: MemoryStoreRequest):
    memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
    stored_at = datetime.now().isoformat()
    
    # Almacenar en datos simulados
    memory_entry = {
        "memory_id": memory_id,
        "content": request.content,
        "content_type": request.content_type,
        "stored_at": stored_at,
        "conversation_id": request.conversation_id,
        "user_id": request.user_id,
        "metadata": request.metadata or {},
        "tags": request.tags or []
    }
    
    memory_data["memories"].append(memory_entry)
    memory_data["total_memories"] += 1
    
    # Actualizar estadísticas
    memory_data["stats"]["total_memories"] += 1
    memory_data["stats"]["memories_by_type"][request.content_type] = \
        memory_data["stats"]["memories_by_type"].get(request.content_type, 0) + 1
    
    if request.user_id:
        memory_data["stats"]["memories_by_user"][request.user_id] = \
            memory_data["stats"]["memories_by_user"].get(request.user_id, 0) + 1
    
    memory_data["stats"]["recent_activity"]["stores_today"] += 1
    memory_data["stats"]["recent_activity"]["last_store"] = stored_at
    
    return MemoryStoreResponse(
        memory_id=memory_id,
        status="stored",
        stored_at=stored_at,
        metadata={
            "content_type": request.content_type,
            "content_length": len(request.content),
            "conversation_id": request.conversation_id,
            "user_id": request.user_id,
            "tags": request.tags or [],
            "storage_method": "simulated_vector_db"
        }
    )

@app.get("/api/v1/memory/stats")
async def get_memory_stats():
    return {
        "total_memories": memory_data["stats"]["total_memories"],
        "memories_by_type": memory_data["stats"]["memories_by_type"],
        "memories_by_user": memory_data["stats"]["memories_by_user"],
        "recent_activity": memory_data["stats"]["recent_activity"],
        "storage_stats": memory_data["stats"]["storage_stats"]
    }

@app.delete("/api/v1/memory/clear")
async def clear_memory(
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    older_than: Optional[str] = None
):
    # Simular limpieza
    cleared_count = len(memory_data["memories"])
    
    memory_data["memories"] = []
    memory_data["total_memories"] = 0
    memory_data["stats"]["total_memories"] = 0
    memory_data["stats"]["memories_by_type"] = {}
    memory_data["stats"]["memories_by_user"] = {}
    
    return {
        "status": "cleared",
        "cleared_count": cleared_count,
        "cleared_at": datetime.now().isoformat(),
        "criteria": {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "older_than": older_than
        }
    }

# === CHAT API ENDPOINTS ===

# Chat API Models
class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: str  # 'user', 'assistant', 'system'
    content: str
    tokens: Optional[int] = None
    is_streaming: Optional[bool] = False
    stream_completed: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = {}
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Conversation(BaseModel):
    id: str
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    title: Optional[str] = None
    context_summary: Optional[str] = ''
    is_active: bool
    message_count: int
    created_at: str
    updated_at: str
    last_message_at: str
    metadata: Optional[Dict[str, Any]] = {}

class SendMessageRequest(BaseModel):
    content: str
    role: Optional[str] = 'user'
    stream: Optional[bool] = False
    user_id: Optional[str] = None

class SendMessageResponse(BaseModel):
    message: ChatMessage
    conversation_id: str
    streaming: Optional[bool] = False

# Chat data storage
chat_data = {
    "conversations": {},
    "messages": {},
    "total_conversations": 0,
    "total_messages": 0
}

def generate_id():
    return f"conv_{random.randint(100000, 999999)}"

def generate_message_id():
    return f"msg_{random.randint(100000, 999999)}"

@app.post("/api/v1/chat/", response_model=Conversation)
async def create_conversation(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    title: Optional[str] = None
):
    """Crear nueva conversación"""
    conversation_id = generate_id()
    now = datetime.now().isoformat()
    
    conversation = Conversation(
        id=conversation_id,
        user_id=user_id or None,
        project_id=project_id or None,
        title=title or f"Conversación {chat_data['total_conversations'] + 1}",
        context_summary='',
        is_active=True,
        message_count=0,
        created_at=now,
        updated_at=now,
        last_message_at=now
    )
    
    chat_data["conversations"][conversation_id] = conversation.dict()
    chat_data["messages"][conversation_id] = []
    chat_data["total_conversations"] += 1
    
    return conversation

@app.post("/api/v1/chat/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest
):
    """Enviar mensaje a una conversación"""
    if conversation_id not in chat_data["conversations"]:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    message_id = generate_message_id()
    now = datetime.now().isoformat()
    
    message = ChatMessage(
        id=message_id,
        role=request.role or 'user',
        content=request.content,
        created_at=now,
        updated_at=now
    )
    
    # Agregar mensaje
    chat_data["messages"][conversation_id].append(message.dict())
    chat_data["total_messages"] += 1
    
    # Simular respuesta del asistente
    assistant_message_id = generate_message_id()
    response_content = f"Respuesta simulada a: {request.content[:50]}..."
    
    assistant_message = ChatMessage(
        id=assistant_message_id,
        role='assistant',
        content=response_content,
        created_at=now,
        updated_at=now
    )
    
    chat_data["messages"][conversation_id].append(assistant_message.dict())
    chat_data["total_messages"] += 1
    
    # Actualizar conversación
    chat_data["conversations"][conversation_id]["message_count"] += 2
    chat_data["conversations"][conversation_id]["last_message_at"] = now
    
    response = SendMessageResponse(
        message=message,
        conversation_id=conversation_id,
        streaming=request.stream or False
    )
    
    return response

@app.get("/api/v1/chat/{conversation_id}/messages", response_model=List[ChatMessage])
async def get_messages(conversation_id: str):
    """Obtener mensajes de una conversación"""
    if conversation_id not in chat_data["conversations"]:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    return chat_data["messages"].get(conversation_id, [])

@app.get("/api/v1/chat/conversations", response_model=List[Conversation])
async def get_conversations(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    limit: int = 20
):
    """Obtener lista de conversaciones"""
    conversations = list(chat_data["conversations"].values())
    
    # Filtrar por user_id y project_id si se proporcionan
    if user_id:
        conversations = [c for c in conversations if c.get("user_id") == user_id]
    if project_id:
        conversations = [c for c in conversations if c.get("project_id") == project_id]
    
    # Ordenar por última actividad y limitar
    conversations.sort(key=lambda x: x.get("last_message_at", ""), reverse=True)
    return conversations[:limit]

@app.delete("/api/v1/chat/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Eliminar conversación"""
    if conversation_id not in chat_data["conversations"]:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Eliminar conversación y mensajes
    del chat_data["conversations"][conversation_id]
    if conversation_id in chat_data["messages"]:
        del chat_data["messages"][conversation_id]
    
    return {"status": "deleted", "conversation_id": conversation_id}

# === PROJECTS API ENDPOINTS ===

# Projects API Models
class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = ''
    user_id: Optional[str] = None
    project_type: Optional[str] = ''
    created_at: str
    updated_at: str
    last_activity: str
    metadata: Optional[Dict[str, Any]] = {}
    is_deleted: Optional[bool] = False

class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = ''
    user_id: Optional[str] = None
    project_type: Optional[str] = 'web-app'
    metadata: Optional[Dict[str, Any]] = {}

class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ProjectAnalytics(BaseModel):
    total_files: int
    total_conversations: int
    total_messages: int
    project_size_mb: float
    last_activity_date: Optional[str] = None
    activity_summary: Dict[str, Any]

class ProjectConversation(BaseModel):
    id: str
    title: Optional[str] = ''
    message_count: int
    created_at: str
    last_message_at: str
    is_active: bool

class ProjectSummary(BaseModel):
    id: str
    name: str
    description: Optional[str] = ''
    status: str
    stats: Dict[str, Any]
    created_at: str
    updated_at: str

# Projects data storage
projects_data = {
    "projects": {},
    "total_projects": 0
}

def generate_project_id():
    return f"proj_{random.randint(100000, 999999)}"

@app.get("/api/v1/projects/", response_model=List[Project])
async def get_projects(
    user_id: Optional[str] = None,
    limit: int = 20
):
    """Obtener lista de proyectos"""
    projects = list(projects_data["projects"].values())
    
    # Filtrar por user_id si se proporciona
    if user_id:
        projects = [p for p in projects if p.get("user_id") == user_id]
    
    # Ordenar por última actividad y limitar
    projects.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
    return projects[:limit]

@app.post("/api/v1/projects/", response_model=Project)
async def create_project(request: CreateProjectRequest):
    """Crear nuevo proyecto"""
    project_id = generate_project_id()
    now = datetime.now().isoformat()
    
    project = Project(
        id=project_id,
        name=request.name,
        description=request.description or '',
        user_id=request.user_id,
        project_type=request.project_type or 'web-app',
        created_at=now,
        updated_at=now,
        last_activity=now
    )
    
    projects_data["projects"][project_id] = project.dict()
    projects_data["total_projects"] += 1
    
    return project

@app.get("/api/v1/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Obtener proyecto específico"""
    if project_id not in projects_data["projects"]:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    return projects_data["projects"][project_id]

@app.put("/api/v1/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, request: UpdateProjectRequest):
    """Actualizar proyecto"""
    if project_id not in projects_data["projects"]:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    project = projects_data["projects"][project_id]
    now = datetime.now().isoformat()
    
    # Actualizar campos proporcionados
    if request.name is not None:
        project["name"] = request.name
    if request.description is not None:
        project["description"] = request.description
    if request.project_type is not None:
        project["project_type"] = request.project_type
    if request.metadata is not None:
        project["metadata"] = request.metadata
    
    project["updated_at"] = now
    project["last_activity"] = now
    
    return Project(**project)

@app.delete("/api/v1/projects/{project_id}")
async def delete_project(project_id: str):
    """Eliminar proyecto"""
    if project_id not in projects_data["projects"]:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Marcar como eliminado (soft delete)
    projects_data["projects"][project_id]["is_deleted"] = True
    projects_data["projects"][project_id]["last_activity"] = datetime.now().isoformat()
    
    return {"status": "deleted", "project_id": project_id}

@app.get("/api/v1/projects/{project_id}/analytics", response_model=ProjectAnalytics)
async def get_project_analytics(project_id: str):
    """Obtener analytics del proyecto"""
    if project_id not in projects_data["projects"]:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Simular analytics
    return ProjectAnalytics(
        total_files=random.randint(5, 50),
        total_conversations=random.randint(1, 20),
        total_messages=random.randint(10, 200),
        project_size_mb=round(random.uniform(1.0, 50.0), 2),
        last_activity_date=datetime.now().isoformat(),
        activity_summary={
            "files_created_this_week": random.randint(0, 10),
            "conversations_this_week": random.randint(0, 5),
            "most_active_day": random.choice(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"])
        }
    )

@app.get("/api/v1/projects/{project_id}/conversations", response_model=List[ProjectConversation])
async def get_project_conversations(project_id: str, limit: int = 20):
    """Obtener conversaciones del proyecto"""
    if project_id not in projects_data["projects"]:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Simular conversaciones del proyecto
    conversations = []
    for i in range(random.randint(1, min(10, limit))):
        conv_id = f"conv_{random.randint(100000, 999999)}"
        conversations.append(ProjectConversation(
            id=conv_id,
            title=f"Conversación {i + 1} del proyecto",
            message_count=random.randint(2, 20),
            created_at=datetime.now().isoformat(),
            last_message_at=datetime.now().isoformat(),
            is_active=random.choice([True, False])
        ))
    
    return conversations[:limit]

@app.get("/api/v1/projects/{project_id}/summary", response_model=ProjectSummary)
async def get_project_summary(project_id: str):
    """Obtener resumen del proyecto"""
    if project_id not in projects_data["projects"]:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    project = projects_data["projects"][project_id]
    
    return ProjectSummary(
        id=project_id,
        name=project["name"],
        description=project.get("description", ""),
        status="active" if not project.get("is_deleted", False) else "archived",
        stats={
            "files_count": random.randint(5, 50),
            "conversations_count": random.randint(1, 20),
            "total_messages": random.randint(10, 200),
            "last_activity": project.get("last_activity", datetime.now().isoformat())
        },
        created_at=project["created_at"],
        updated_at=project["updated_at"]
    )

# === TASKS API ENDPOINTS ===

# Tasks API Models
class TaskRequest(BaseModel):
    task_id: Optional[str] = None
    task_type: str  # 'generation', 'analysis', 'processing', 'automation'
    title: Optional[str] = ''
    description: Optional[str] = ''
    priority: Optional[str] = 'medium'  # 'low', 'medium', 'high', 'urgent'
    parameters: Optional[Dict[str, Any]] = {}
    dependencies: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
    budget: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    task_id: str
    status: str  # 'pending', 'processing', 'completed', 'failed', 'timeout'
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int
    metadata: Optional[Dict[str, Any]] = {}
    created_at: str
    updated_at: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: int  # 0-100
    current_step: Optional[str] = None
    estimated_completion: Optional[str] = None
    execution_time_ms: int
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class TaskResult(BaseModel):
    task_id: str
    result: Dict[str, Any]
    execution_time_ms: int
    metadata: Optional[Dict[str, Any]] = {}
    created_at: str
    completed_at: str

class TaskList(BaseModel):
    tasks: List[TaskResponse]
    total: int
    pending: int
    processing: int
    completed: int
    failed: int

# Tasks data storage
tasks_data = {
    "tasks": {},
    "total_tasks": 0
}

def generate_task_id():
    return f"task_{random.randint(100000, 999999)}"

@app.post("/api/v1/tasks/create", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """Crear nueva tarea"""
    task_id = generate_task_id()
    now = datetime.now().isoformat()
    
    task = TaskResponse(
        task_id=task_id,
        status="pending",
        execution_time_ms=0,
        created_at=now,
        updated_at=now
    )
    
    tasks_data["tasks"][task_id] = {
        "request": request.dict(),
        "response": task.dict(),
        "created_at": now
    }
    tasks_data["total_tasks"] += 1
    
    return task

@app.post("/api/v1/tasks/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """Ejecutar tarea"""
    task_id = request.task_id or generate_task_id()
    start_time = datetime.now()
    now = start_time.isoformat()
    
    try:
        # Simular ejecución según el tipo de tarea
        if request.task_type == "generation":
            result = {
                "task_type": request.task_type,
                "title": request.title,
                "description": request.description,
                "parameters": request.parameters,
                "output": "Asset generado exitosamente",
                "files_created": ["generated_asset.svg", "preview.png"],
                "status": "success"
            }
        elif request.task_type == "analysis":
            result = {
                "task_type": request.task_type,
                "title": request.title,
                "description": request.description,
                "parameters": request.parameters,
                "analysis_results": {
                    "summary": "Análisis completado",
                    "insights": ["Insight 1", "Insight 2", "Insight 3"],
                    "confidence": 0.85
                },
                "status": "success"
            }
        elif request.task_type == "processing":
            result = {
                "task_type": request.task_type,
                "title": request.title,
                "description": request.description,
                "parameters": request.parameters,
                "processed_data": "Datos procesados correctamente",
                "output_format": "json",
                "records_processed": random.randint(100, 1000),
                "status": "success"
            }
        elif request.task_type == "automation":
            result = {
                "task_type": request.task_type,
                "title": request.title,
                "description": request.description,
                "parameters": request.parameters,
                "workflow_executed": request.parameters.get("workflow", "default"),
                "steps_completed": random.randint(3, 10),
                "automation_result": "Workflow ejecutado exitosamente",
                "status": "success"
            }
        else:
            result = {
                "task_type": request.task_type,
                "title": request.title,
                "description": request.description,
                "parameters": request.parameters,
                "output": "Tarea ejecutada",
                "status": "success"
            }
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        response = TaskResponse(
            task_id=task_id,
            status="completed",
            result=result,
            execution_time_ms=execution_time,
            created_at=now,
            updated_at=now
        )
        
        # Guardar en historial
        tasks_data["tasks"][task_id] = {
            "request": request.dict(),
            "response": response.dict(),
            "created_at": now
        }
        tasks_data["total_tasks"] += 1
        
        return response
        
    except Exception as e:
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        return TaskResponse(
            task_id=task_id,
            status="failed",
            error=str(e),
            execution_time_ms=execution_time,
            created_at=now,
            updated_at=now
        )

@app.get("/api/v1/tasks/{task_id}/status", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Obtener estado de tarea"""
    if task_id not in tasks_data["tasks"]:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task_data = tasks_data["tasks"][task_id]
    response = task_data["response"]
    
    return TaskStatus(
        task_id=task_id,
        status=response["status"],
        progress=100 if response["status"] == "completed" else 0,
        current_step="Completado" if response["status"] == "completed" else "Procesando",
        execution_time_ms=response["execution_time_ms"],
        error=response.get("error"),
        metadata=response.get("metadata", {})
    )

@app.get("/api/v1/tasks/{task_id}/results", response_model=TaskResult)
async def get_task_result(task_id: str):
    """Obtener resultado de tarea"""
    if task_id not in tasks_data["tasks"]:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task_data = tasks_data["tasks"][task_id]
    response = task_data["response"]
    created_at = task_data["created_at"]
    
    if response["status"] != "completed":
        raise HTTPException(status_code=400, detail="Tarea no completada")
    
    return TaskResult(
        task_id=task_id,
        result=response.get("result", {}),
        execution_time_ms=response["execution_time_ms"],
        metadata=response.get("metadata", {}),
        created_at=created_at,
        completed_at=response["updated_at"]
    )

@app.delete("/api/v1/tasks/{task_id}")
async def delete_task(task_id: str):
    """Eliminar tarea"""
    if task_id not in tasks_data["tasks"]:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    del tasks_data["tasks"][task_id]
    return {"status": "deleted", "task_id": task_id}

@app.get("/api/v1/tasks/list", response_model=TaskList)
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 20
):
    """Listar tareas"""
    tasks = list(tasks_data["tasks"].values())
    responses = [task["response"] for task in tasks]
    
    # Filtrar por status si se proporciona
    if status:
        responses = [t for t in responses if t["status"] == status]
    
    # Contar por status
    total = len(responses)
    pending = len([t for t in responses if t["status"] == "pending"])
    processing = len([t for t in responses if t["status"] == "processing"])
    completed = len([t for t in responses if t["status"] == "completed"])
    failed = len([t for t in responses if t["status"] == "failed"])
    
    # Limitar resultados
    responses = responses[:limit]
    
    return TaskList(
        tasks=[TaskResponse(**task) for task in responses],
        total=total,
        pending=pending,
        processing=processing,
        completed=completed,
        failed=failed
    )

@app.get("/api/v1/tasks/{task_id}/stream")
async def stream_task_progress(task_id: str):
    """Streaming de progreso de tarea"""
    if task_id not in tasks_data["tasks"]:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    async def generate():
        # Simular streaming de progreso
        for progress in [0, 25, 50, 75, 100]:
            yield f"data: {{\"type\": \"progress\", \"progress\": {progress}}}\n\n"
            await asyncio.sleep(0.5)
        
        # Estado final
        task_data = tasks_data["tasks"][task_id]
        response = task_data["response"]
        yield f"data: {{\"type\": \"completed\", \"result\": {json.dumps(response.get('result', {}))}}}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

# === BRIDGE API ENDPOINTS ===

# Bridge API Models
class SystemStatus(BaseModel):
    status: str  # 'healthy', 'degraded', 'unhealthy'
    services: Dict[str, bool]
    uptime: float
    last_check: str

class AgentInfo(BaseModel):
    id: str
    name: str
    type: str
    status: str  # 'active', 'inactive', 'busy'
    capabilities: List[str]
    load: float
    last_activity: str

class TeamInfo(BaseModel):
    id: str
    name: str
    members: List[AgentInfo]
    status: str  # 'active', 'inactive'
    specialization: str
    current_task: Optional[str] = None

class ProcessingMode(BaseModel):
    id: str
    name: str
    description: str
    performance: str  # 'low', 'medium', 'high'
    resource_usage: float
    supported_agents: List[str]

class UnifiedChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}
    agent_type: Optional[str] = None
    team_id: Optional[str] = None
    mode: Optional[str] = None

class UnifiedChatResponse(BaseModel):
    response: str
    agent_used: Optional[str] = None
    team_used: Optional[str] = None
    processing_time_ms: int
    confidence: float
    suggestions: Optional[List[str]] = []

class AIModel(BaseModel):
    id: str
    name: str
    provider: str
    type: str  # 'llm', 'embedding', 'generation'
    status: str  # 'active', 'inactive', 'training'
    performance_metrics: Dict[str, float]

class TaskRoutingResponse(BaseModel):
    recommended_agents: List[str]
    recommended_team: Optional[str] = None
    estimated_completion: str
    routing_score: float
    alternative_options: List[str]

class IntegrationInfo(BaseModel):
    system_name: str
    version: str
    capabilities: List[str]
    endpoints: List[str]
    health_status: str  # 'healthy', 'degraded', 'unhealthy'
    last_sync: str

# Bridge data storage
bridge_data = {
    "system_status": "healthy",
    "selected_mode": "balanced",
    "total_requests": 0
}

@app.get("/api/v1/bridge/status", response_model=SystemStatus)
async def get_bridge_status():
    """Obtener estado del sistema bridge"""
    return SystemStatus(
        status=random.choice(["healthy", "healthy", "healthy", "degraded"]),  # Mostly healthy
        services={
            "iris_agents": random.choice([True, True, True, False]),
            "silhouette_teams": random.choice([True, True, False]),
            "processing_modes": True
        },
        uptime=random.uniform(1000, 10000),
        last_check=datetime.now().isoformat()
    )

@app.get("/api/v1/bridge/iris-agents", response_model=List[AgentInfo])
async def get_iris_agents():
    """Obtener agentes IRIS disponibles"""
    agents = []
    agent_types = ["planner", "reasoner", "executor", "verifier", "generator", "analyzer"]
    
    for i in range(random.randint(3, 8)):
        agent_id = f"agent_{i+1:03d}"
        agents.append(AgentInfo(
            id=agent_id,
            name=f"IRIS Agent {i+1}",
            type=random.choice(agent_types),
            status=random.choice(["active", "active", "active", "busy"]),
            capabilities=[random.choice(agent_types), "general"],
            load=round(random.uniform(0.1, 0.9), 2),
            last_activity=datetime.now().isoformat()
        ))
    
    return agents

@app.get("/api/v1/bridge/silhouette-teams", response_model=List[TeamInfo])
async def get_silhouette_teams():
    """Obtener equipos Silhouette disponibles"""
    teams = []
    specializations = ["web_development", "data_analysis", "automation", "research", "creative"]
    
    for i in range(random.randint(2, 5)):
        team_id = f"team_{i+1:03d}"
        # Crear miembros del equipo
        members = []
        for j in range(random.randint(2, 4)):
            members.append(AgentInfo(
                id=f"{team_id}_member_{j+1}",
                name=f"Team {i+1} Member {j+1}",
                type=random.choice(["specialist", "generalist", "coordinator"]),
                status="active",
                capabilities=[random.choice(specializations)],
                load=round(random.uniform(0.2, 0.8), 2),
                last_activity=datetime.now().isoformat()
            ))
        
        teams.append(TeamInfo(
            id=team_id,
            name=f"Silhouette Team {i+1}",
            members=members,
            status="active",
            specialization=random.choice(specializations),
            current_task=random.choice([None, "web_scraping", "data_processing", "content_generation"])
        ))
    
    return teams

@app.get("/api/v1/bridge/processing-modes", response_model=List[ProcessingMode])
async def get_processing_modes():
    """Obtener modos de procesamiento disponibles"""
    return [
        ProcessingMode(
            id="fast",
            name="Modo Rápido",
            description="Procesamiento optimizado para velocidad",
            performance="high",
            resource_usage=0.3,
            supported_agents=["executor", "generator"]
        ),
        ProcessingMode(
            id="balanced",
            name="Modo Balanceado",
            description="Balance entre velocidad y calidad",
            performance="medium",
            resource_usage=0.5,
            supported_agents=["planner", "reasoner", "executor"]
        ),
        ProcessingMode(
            id="quality",
            name="Modo Calidad",
            description="Procesamiento optimizado para calidad",
            performance="low",
            resource_usage=0.7,
            supported_agents=["verifier", "analyzer", "planner"]
        ),
        ProcessingMode(
            id="intensive",
            name="Modo Intensivo",
            description="Máximo rendimiento con todos los recursos",
            performance="high",
            resource_usage=0.9,
            supported_agents=["planner", "reasoner", "executor", "verifier", "generator", "analyzer"]
        )
    ]

@app.post("/api/v1/bridge/mode")
async def select_processing_mode(mode_data: Dict[str, Any]):
    """Seleccionar modo de procesamiento"""
    mode_id = mode_data.get("mode_id", "balanced")
    bridge_data["selected_mode"] = mode_id
    bridge_data["total_requests"] += 1
    
    return {
        "status": "mode_selected",
        "mode_id": mode_id,
        "message": f"Modo {mode_id} activado exitosamente"
    }

@app.post("/api/v1/bridge/process-task")
async def process_task_bridge(task_data: Dict[str, Any]):
    """Procesar tarea a través del bridge"""
    task = task_data.get("task", "general_task")
    parameters = task_data.get("parameters", {})
    bridge_data["total_requests"] += 1
    
    # Simular procesamiento
    processing_time = random.randint(100, 2000)
    await asyncio.sleep(0.1)  # Simular latencia
    
    result = {
        "task": task,
        "parameters": parameters,
        "mode_used": bridge_data["selected_mode"],
        "processing_time_ms": processing_time,
        "agents_involved": random.sample(["planner", "reasoner", "executor"], random.randint(1, 3)),
        "result": f"Tarea '{task}' procesada exitosamente",
        "status": "completed",
        "confidence": round(random.uniform(0.7, 0.99), 2)
    }
    
    return result

@app.get("/api/v1/bridge/ai-models", response_model=List[AIModel])
async def get_ai_models():
    """Obtener modelos de IA disponibles"""
    models = [
        AIModel(
            id="gpt-4",
            name="GPT-4",
            provider="OpenAI",
            type="llm",
            status="active",
            performance_metrics={"speed": 0.8, "accuracy": 0.95, "cost": 0.9}
        ),
        AIModel(
            id="claude-3",
            name="Claude 3",
            provider="Anthropic",
            type="llm",
            status="active",
            performance_metrics={"speed": 0.9, "accuracy": 0.93, "cost": 0.8}
        ),
        AIModel(
            id="text-embedding-ada-002",
            name="Ada Embedding",
            provider="OpenAI",
            type="embedding",
            status="active",
            performance_metrics={"speed": 0.95, "accuracy": 0.88, "cost": 0.3}
        ),
        AIModel(
            id="dall-e-3",
            name="DALL-E 3",
            provider="OpenAI",
            type="generation",
            status="active",
            performance_metrics={"speed": 0.6, "accuracy": 0.92, "cost": 0.85}
        ),
        AIModel(
            id="minimax-free",
            name="MiniMax Free",
            provider="MiniMax",
            type="llm",
            status="active",
            performance_metrics={"speed": 0.95, "accuracy": 0.85, "cost": 0.1}
        )
    ]
    
    return models

@app.post("/api/v1/bridge/ai-process")
async def process_with_ai(ai_data: Dict[str, Any]):
    """Procesar con modelo de IA"""
    prompt = ai_data.get("prompt", "")
    model_id = ai_data.get("model_id", "minimax-free")
    parameters = ai_data.get("parameters", {})
    bridge_data["total_requests"] += 1
    
    # Simular procesamiento de IA
    processing_time = random.randint(200, 3000)
    await asyncio.sleep(0.2)
    
    # Generar respuesta simulada basada en el modelo
    responses = {
        "gpt-4": f"Análisis avanzado de: {prompt[:50]}... con alta precisión y contexto completo.",
        "claude-3": f"Análisis detallado de: {prompt[:50]}... con enfoque ético y estructurado.",
        "minimax-free": f"Análisis eficiente de: {prompt[:50]}... optimizado para velocidad.",
        "default": f"Procesamiento de IA completado para: {prompt[:50]}..."
    }
    
    return {
        "prompt": prompt,
        "model_used": model_id,
        "processing_time_ms": processing_time,
        "response": responses.get(model_id, responses["default"]),
        "tokens_used": random.randint(100, 1000),
        "confidence": round(random.uniform(0.75, 0.98), 2),
        "parameters": parameters
    }

@app.get("/api/v1/bridge/routing/{task_type}", response_model=TaskRoutingResponse)
async def get_task_routing(task_type: str):
    """Obtener enrutamiento recomendado para tipo de tarea"""
    agents = ["planner", "reasoner", "executor", "verifier", "generator", "analyzer"]
    teams = ["team_001", "team_002", "team_003"]
    
    # Seleccionar agentes relevantes según el tipo de tarea
    task_agent_map = {
        "web_development": ["planner", "generator", "executor"],
        "data_analysis": ["analyzer", "reasoner", "verifier"],
        "automation": ["executor", "planner", "verifier"],
        "research": ["reasoner", "analyzer", "planner"],
        "creative": ["generator", "planner", "verifier"]
    }
    
    recommended_agents = task_agent_map.get(task_type, random.sample(agents, 3))
    estimated_time = random.randint(5, 30)
    
    return TaskRoutingResponse(
        recommended_agents=recommended_agents,
        recommended_team=random.choice(teams) if random.choice([True, False]) else None,
        estimated_completion=f"{estimated_time} minutos",
        routing_score=round(random.uniform(0.7, 0.95), 2),
        alternative_options=agents[:3]
    )

@app.get("/api/v1/bridge/integration-info", response_model=List[IntegrationInfo])
async def get_integration_info():
    """Obtener información de integraciones"""
    return [
        IntegrationInfo(
            system_name="IRIS Core",
            version="2.1.0",
            capabilities=["multi_agent", "task_orchestration", "memory_management"],
            endpoints=["/api/v1/chat", "/api/v1/memory", "/api/v1/tasks"],
            health_status="healthy",
            last_sync=datetime.now().isoformat()
        ),
        IntegrationInfo(
            system_name="SilhouetteMCP",
            version="1.5.2",
            capabilities=["team_coordination", "workflow_automation", "agent_management"],
            endpoints=["/bridge/teams", "/bridge/workflows", "/bridge/routing"],
            health_status="healthy",
            last_sync=datetime.now().isoformat()
        ),
        IntegrationInfo(
            system_name="AI Gateway",
            version="3.0.1",
            capabilities=["llm_routing", "model_selection", "cost_optimization"],
            endpoints=["/gateway/chat", "/gateway/models", "/gateway/usage"],
            health_status="healthy",
            last_sync=datetime.now().isoformat()
        )
    ]

@app.post("/api/v1/bridge/unified-chat", response_model=UnifiedChatResponse)
async def unified_chat(request: UnifiedChatRequest):
    """Chat unificado a través del bridge"""
    message = request.message
    context = request.context or {}
    bridge_data["total_requests"] += 1
    
    # Simular procesamiento inteligente
    processing_time = random.randint(150, 1000)
    await asyncio.sleep(0.1)
    
    # Determinar agente y equipo basado en el contexto
    agent_used = random.choice(["planner", "reasoner", "generator", "analyzer"])
    team_used = random.choice([None, "team_001", "team_002"])
    
    # Generar respuesta contextual
    responses = [
        f"He analizado tu mensaje: '{message[:30]}...' y tengo una respuesta completa.",
        f"Basado en el contexto proporcionado, aquí está mi análisis: {message[:40]}...",
        f"Procesando tu consulta: '{message[:25]}...' - resultados listos.",
        f"Respuesta unificada para: '{message[:35]}...' con confianza alta."
    ]
    
    return UnifiedChatResponse(
        response=random.choice(responses),
        agent_used=agent_used,
        team_used=team_used,
        processing_time_ms=processing_time,
        confidence=round(random.uniform(0.8, 0.98), 2),
        suggestions=[
            "¿Podrías proporcionar más contexto?",
            "¿Te gustaría que profundice en algún aspecto específico?",
            "¿Necesitas que consulte fuentes adicionales?"
        ]
    )

# === TOOLS API ENDPOINTS ===

# Tools API Models
class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}
    executor_type: str = "general"
    user_id: Optional[str] = None
    timeout: Optional[int] = 30
    async_mode: bool = False

class ToolResponse(BaseModel):
    execution_id: str
    tool_name: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int
    metadata: Optional[Dict[str, Any]] = None

class ToolsListResponse(BaseModel):
    tools: List[Dict[str, Any]]
    executors: List[str]
    total_tools: int

# Tools data storage
tools_data = {
    "available_tools": {
        "general": [
            {"name": "web_search", "description": "Búsqueda en web", "parameters": ["query", "num_results"]},
            {"name": "text_analysis", "description": "Análisis de texto", "parameters": ["text", "analysis_type"]},
            {"name": "data_processing", "description": "Procesamiento de datos", "parameters": ["data", "operation"]}
        ],
        "code": [
            {"name": "python_execute", "description": "Ejecutar código Python", "parameters": ["code", "timeout"]},
            {"name": "code_test", "description": "Probar código", "parameters": ["code", "test_cases"]},
            {"name": "package_install", "description": "Instalar paquete", "parameters": ["package_name", "version"]}
        ],
        "web": [
            {"name": "web_scrape", "description": "Web scraping", "parameters": ["url", "selector"]},
            {"name": "browser_automation", "description": "Automatización de navegador", "parameters": ["action", "target"]},
            {"name": "api_call", "description": "Llamada API", "parameters": ["url", "method", "headers"]}
        ],
        "docs": [
            {"name": "pdf_extract", "description": "Extraer texto de PDF", "parameters": ["file_path", "pages"]},
            {"name": "document_parse", "description": "Procesar documento", "parameters": ["file_path", "format"]},
            {"name": "text_summarize", "description": "Resumir texto", "parameters": ["text", "max_length"]}
        ]
    },
    "executions": {},
    "total_executions": 0
}

@app.get("/api/v1/tools/", response_model=ToolsListResponse)
async def list_available_tools():
    """Lista todas las herramientas disponibles organizadas por tipo de executor"""
    all_tools = []
    for executor_type, tools in tools_data["available_tools"].items():
        for tool in tools:
            all_tools.append({
                **tool,
                "executor_type": executor_type
            })
    
    return ToolsListResponse(
        tools=all_tools,
        executors=list(tools_data["available_tools"].keys()),
        total_tools=len(all_tools)
    )

@app.post("/api/v1/tools/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Ejecuta una herramienta específica"""
    execution_id = f"exec_{random.randint(100000, 999999)}"
    start_time = datetime.now()
    
    try:
        # Simular ejecución según el tipo de herramienta
        if request.tool_name == "web_search":
            result = {
                "query": request.parameters.get("query", ""),
                "results": [
                    {"title": f"Resultado 1 para '{request.parameters.get('query', '')}'", "url": "https://example1.com", "snippet": "Snippet de resultado..."},
                    {"title": f"Resultado 2 para '{request.parameters.get('query', '')}'", "url": "https://example2.com", "snippet": "Snippet de resultado..."},
                    {"title": f"Resultado 3 para '{request.parameters.get('query', '')}'", "url": "https://example3.com", "snippet": "Snippet de resultado..."}
                ],
                "total_results": 3
            }
        elif request.tool_name == "python_execute":
            result = {
                "code": request.parameters.get("code", "print('Hello World')"),
                "output": "Hello World",
                "execution_time": "0.05s",
                "status": "success"
            }
        elif request.tool_name == "web_scrape":
            result = {
                "url": request.parameters.get("url", ""),
                "content": "Contenido extraído de la página web...",
                "elements_found": 15,
                "status": "success"
            }
        elif request.tool_name == "pdf_extract":
            result = {
                "file_path": request.parameters.get("file_path", ""),
                "text_extracted": "Texto extraído del documento PDF...",
                "pages_processed": request.parameters.get("pages", 1),
                "status": "success"
            }
        elif request.tool_name == "text_analysis":
            result = {
                "text": request.parameters.get("text", ""),
                "analysis_type": request.parameters.get("analysis_type", "general"),
                "sentiment": "positive",
                "keywords": ["keyword1", "keyword2", "keyword3"],
                "summary": "Análisis completado del texto proporcionado",
                "status": "success"
            }
        else:
            # Herramienta genérica
            result = {
                "tool": request.tool_name,
                "input_params": request.parameters,
                "output": "Resultado simulado de herramienta",
                "status": "success"
            }
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        response = ToolResponse(
            execution_id=execution_id,
            tool_name=request.tool_name,
            status="success",
            result=result,
            execution_time_ms=execution_time
        )
        
        # Guardar en historial
        tools_data["executions"][execution_id] = {
            "request": request.dict(),
            "response": response.dict(),
            "timestamp": start_time.isoformat()
        }
        tools_data["total_executions"] += 1
        
        return response
        
    except Exception as e:
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        return ToolResponse(
            execution_id=execution_id,
            tool_name=request.tool_name,
            status="error",
            error=str(e),
            execution_time_ms=execution_time
        )

@app.get("/api/v1/tools/execute/{execution_id}")
async def get_execution_status(execution_id: str):
    """Obtiene el estado de una ejecución"""
    if execution_id in tools_data["executions"]:
        execution_data = tools_data["executions"][execution_id]
        return {
            "execution_id": execution_id,
            "status": "completed",
            "message": "Ejecución completada",
            "result": execution_data["response"].get("result"),
            "error": execution_data["response"].get("error"),
            "execution_time_ms": execution_data["response"].get("execution_time_ms"),
            "started_at": execution_data["timestamp"],
            "completed_at": execution_data["timestamp"]
        }
    else:
        return {
            "execution_id": execution_id,
            "status": "not_found",
            "message": "ID de ejecución no encontrado"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando IRIS Complete Test Server...")
    print("📡 Endpoints disponibles:")
    print("   - Health: GET /health")
    print("   - Assets: GET /api/v1/assets/categories")
    print("   - Assets: POST /api/v1/assets/generate")
    print("   - Chat: POST /api/v1/chat/")
    print("   - Chat: POST /api/v1/chat/{id}/messages")
    print("   - Chat: GET /api/v1/chat/{id}/messages")
    print("   - Chat: GET /api/v1/chat/conversations")
    print("   - Chat: DELETE /api/v1/chat/{id}")
    print("   - Memory: GET/POST /api/v1/memory/search")
    print("   - Memory: POST /api/v1/memory/store")
    print("   - Memory: GET /api/v1/memory/stats")
    print("   - Memory: DELETE /api/v1/memory/clear")
    print("   - Projects: GET /api/v1/projects/")
    print("   - Projects: POST /api/v1/projects/")
    print("   - Projects: GET /api/v1/projects/{id}")
    print("   - Projects: PUT /api/v1/projects/{id}")
    print("   - Projects: DELETE /api/v1/projects/{id}")
    print("   - Projects: GET /api/v1/projects/{id}/analytics")
    print("   - Projects: GET /api/v1/projects/{id}/conversations")
    print("   - Projects: GET /api/v1/projects/{id}/summary")
    print("   - Tasks: POST /api/v1/tasks/create")
    print("   - Tasks: POST /api/v1/tasks/execute")
    print("   - Tasks: GET /api/v1/tasks/{id}/status")
    print("   - Tasks: GET /api/v1/tasks/{id}/results")
    print("   - Tasks: DELETE /api/v1/tasks/{id}")
    print("   - Tasks: GET /api/v1/tasks/list")
    print("   - Tasks: GET /api/v1/tasks/{id}/stream")
    print("   - Bridge: GET /api/v1/bridge/status")
    print("   - Bridge: GET /api/v1/bridge/iris-agents")
    print("   - Bridge: GET /api/v1/bridge/silhouette-teams")
    print("   - Bridge: GET /api/v1/bridge/processing-modes")
    print("   - Bridge: POST /api/v1/bridge/mode")
    print("   - Bridge: POST /api/v1/bridge/process-task")
    print("   - Bridge: GET /api/v1/bridge/ai-models")
    print("   - Bridge: POST /api/v1/bridge/ai-process")
    print("   - Bridge: GET /api/v1/bridge/routing/{task_type}")
    print("   - Bridge: GET /api/v1/bridge/integration-info")
    print("   - Bridge: POST /api/v1/bridge/unified-chat")
    print("   - Tools: GET /api/v1/tools/")
    print("   - Tools: POST /api/v1/tools/execute")
    print("   - Tools: GET /api/v1/tools/execute/{id}")
    print("🌐 Servidor en: http://localhost:8001")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")