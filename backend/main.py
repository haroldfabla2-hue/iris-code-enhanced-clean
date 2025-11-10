"""
API REST con FastAPI
Expone endpoints del sistema multi-agente
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import asyncio
import json
import logging

from app.core import settings
from app.core.llm_router import LLMRouter
from app.core.database import init_database, create_tables
from app.orchestrator import MultiAgentOrchestrator
from app.api import tools, memory, tasks, health
# Nuevos endpoints para IRIS Code
from app.api import projects, chat, assets
from app.api.memory import initialize_memory_manager

# IRIS-Silhouette Bridge integration
from app.api import bridge

# VEO3 Video Generation
from app.api import video

# Live Preview System
from app.api import preview, terminals
from app.services.live_preview_service import start_cleanup_task

# Hyper-Intelligent System
from app.services.hyperintelligent_orchestrator import (
    HyperIntelligentTaskOrchestrator, 
    HyperIntelligentTaskRequest, 
    ProcessingMode
)


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Inicializar FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Sistema Multi-Agente Superior a Silhouette Anonimo"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos de request/response
class TaskRequest(BaseModel):
    """Request para crear una tarea"""
    objetivo: str = Field(..., description="Objetivo a cumplir")
    contexto: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    user_id: Optional[str] = Field(None, description="ID del usuario")
    stream: bool = Field(False, description="Activar streaming de respuesta")


class TaskResponse(BaseModel):
    """Response de una tarea"""
    conversation_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Response de health check"""
    status: str
    version: str
    llm_stats: Optional[Dict[str, Any]] = None


class HyperIntelligentTaskRequest(BaseModel):
    """Request para tarea hiperinteligente"""
    user_prompt: str = Field(..., description="Prompt natural del usuario")
    processing_mode: str = Field("full_hyperintelligent", description="Modo de procesamiento: intent_analysis_only, image_generation_only, full_hyperintelligent, enterprise_teams")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Requerimientos específicos")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Preferencias del usuario")
    deadline: Optional[str] = Field(None, description="Deadline en formato ISO")


class HyperIntelligentWorkflowResponse(BaseModel):
    """Response de workflow hiperinteligente"""
    workflow_id: str
    status: str
    progress: float
    current_phase: str
    phases_completed: List[str]
    execution_time: float
    intent_analysis: Optional[Dict[str, Any]] = None
    image_generation_result: Optional[Dict[str, Any]] = None
    team_assignments: List[Dict[str, Any]] = None
    final_results: Optional[Dict[str, Any]] = None
    errors: List[str] = None
    recommendations: List[str] = None
    next_actions: List[str] = None


# Estado global
llm_router: Optional[LLMRouter] = None
orchestrator: Optional[MultiAgentOrchestrator] = None
hyper_orchestrator: Optional[HyperIntelligentTaskOrchestrator] = None


@app.on_event("startup")
async def startup_event():
    """Inicialización al arrancar con VectorStore y servicios completos"""
    global llm_router, orchestrator, hyper_orchestrator
    
    logger.info("🚀 Iniciando IRIS Code - Sistema Multi-Agente Superior...")
    
    try:
        # 0. Inicializar base de datos para IRIS Code
        init_database()
        create_tables()
        logger.info("✅ Base de datos inicializada")
        
        # 1. Inicializar LLM Router
        llm_router = LLMRouter()
        logger.info("✅ LLM Router inicializado")
        
        # 2. Inicializar Embedding Service (HuggingFace)
        from app.services.embedding_service import EmbeddingService
        try:
            embedding_service = EmbeddingService(model_name="all-MiniLM-L6-v2")
            await embedding_service.initialize()
            logger.info("✅ Embedding Service (HuggingFace) inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Embedding Service no disponible: {e}")
            logger.info("🔄 Continuando sin Embedding Service (modo fallback)")
            embedding_service = None
        
        # 3. Inicializar VectorStore con PostgreSQL + pgvector
        from app.services.vector_store import VectorStore
        vector_store = None
        try:
            if embedding_service:
                vector_store = VectorStore(
                    db_url=settings.DATABASE_URL,
                    embedding_service=embedding_service
                )
                await vector_store.initialize()
                logger.info("✅ VectorStore (PostgreSQL + pgvector) inicializado")
            else:
                logger.info("🔄 Saltando VectorStore - Embedding Service no disponible")
        except Exception as e:
            logger.warning(f"⚠️ VectorStore no disponible: {e}")
            logger.info("🔄 Continuando sin VectorStore (modo fallback)")
            vector_store = None
        
        # 4. Inicializar Memory Manager actualizado con servicios disponibles
        from app.agents.memory_manager import MemoryManagerAgent
        memory_manager = MemoryManagerAgent(
            llm_client=llm_router,
            vector_store=vector_store,  # Puede ser None
            embedding_service=embedding_service  # Puede ser None
        )
        if vector_store:
            logger.info("✅ Memory Manager con VectorStore inicializado")
        else:
            logger.info("✅ Memory Manager (modo fallback sin VectorStore) inicializado")
        
        # 5. Inicializar Redis (básico por ahora)
        try:
            import redis.asyncio as redis
            redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await redis_client.ping()
            logger.info("✅ Redis conectado")
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}")
            redis_client = None
        
        # 6. Inicializar Orquestador con todos los servicios
        orchestrator = MultiAgentOrchestrator(
            llm_router=llm_router,
            redis_client=redis_client,
            vector_store=vector_store
        )
        logger.info("✅ MultiAgent Orchestrator inicializado")
        
        # 7. Inicializar TaskManager y TaskOrchestratorIntegrator
        from app.services.task_manager import task_manager
        from app.services.task_orchestrator_integrator import initialize_task_orchestrator_integrator
        initialize_task_orchestrator_integrator(task_manager, orchestrator)
        logger.info("✅ TaskManager y TaskOrchestratorIntegrator inicializados")
        
        # 8. Actualizar el memory manager global en la API
        from app.api.memory import initialize_memory_manager
        initialize_memory_manager(
            llm_client=llm_router,
            vector_store=vector_store,  # Puede ser None
            embedding_service=embedding_service  # Puede ser None
        )
        
        # 9. Inicializar Hyper-Intelligent Task Orchestrator
        hyper_orchestrator = HyperIntelligentTaskOrchestrator(
            ai_gateway_url="http://ai-gateway:8002",
            silhouette_url="http://silhouette-framework:8001"
        )
        logger.info("✅ Hyper-Intelligent Task Orchestrator inicializado")
        
        # 10. Inicializar Live Preview Service
        await start_cleanup_task()
        logger.info("✅ Live Preview Service (WebContainers + Multi-Terminal) inicializado")
        
        logger.info("🎉 Sistema completo inicializado exitosamente")
        logger.info("📊 Servicios activos:")
        logger.info("   - LLM Router con modelos minimax-m2 y llama-3.3-70b")
        logger.info("   - Embedding Service (HuggingFace all-MiniLM-L6-v2)")
        logger.info("   - VectorStore (PostgreSQL + pgvector)")
        logger.info("   - Memory Manager con búsqueda semántica")
        logger.info("   - Redis (cache y sesiones)")
        logger.info("   - Multi-Agent Orchestrator")
        
    except Exception as e:
        logger.error(f"❌ Error durante inicialización: {e}")
        import traceback
        traceback.print_exc()
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar"""
    global llm_router
    
    logger.info("Cerrando Sistema Multi-Agente Superior...")
    
    if llm_router:
        await llm_router.close()
    
    logger.info("Sistema cerrado correctamente")


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check principal"""
    return {
        "status": "running",
        "version": settings.VERSION,
        "llm_stats": llm_router.get_stats() if llm_router else None
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check detallado"""
    
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "llm_stats": None
    }
    
    if llm_router:
        health_status["llm_stats"] = llm_router.get_stats()
    
    if orchestrator is None:
        health_status["status"] = "degraded"
    
    return health_status


@app.post("/api/v1/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """
    Crea y ejecuta una tarea con el sistema multi-agente
    
    - **objetivo**: Descripción de lo que se quiere lograr
    - **contexto**: Información adicional opcional
    - **user_id**: Identificador del usuario (opcional)
    - **stream**: Si activar streaming (no implementado aún)
    """
    
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Orquestador no inicializado"
        )
    
    try:
        logger.info(f"Nueva tarea: {request.objetivo[:100]}")
        
        # Procesar request con orquestador
        result = await orchestrator.process_request(
            objetivo=request.objetivo,
            contexto=request.contexto,
            user_id=request.user_id
        )
        
        return TaskResponse(
            conversation_id=result["conversation_id"],
            status=result["status"],
            result=result.get("result"),
            error=result.get("error"),
            metadata=result.get("metadata")
        )
        
    except Exception as e:
        logger.exception("Error procesando tarea")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando tarea: {str(e)}"
        )


@app.get("/api/v1/tasks/{conversation_id}")
async def get_task_status(conversation_id: str):
    """
    Obtiene el estado de una tarea por su conversation_id
    """
    
    # TODO: Implementar recuperación de estado desde Redis
    
    return {
        "conversation_id": conversation_id,
        "status": "not_implemented",
        "message": "Consulta de estado no implementada aún"
    }


@app.get("/api/v1/stats")
async def get_system_stats():
    """
    Obtiene estadísticas del sistema
    """
    
    stats = {
        "system": {
            "version": settings.VERSION,
            "status": "running"
        }
    }
    
    if llm_router:
        stats["llm"] = llm_router.get_stats()
    
    if orchestrator:
        stats["orchestrator"] = {
            "active_sessions": len(orchestrator.active_sessions),
            "agents": {
                "reasoner": orchestrator.reasoner.agent_id,
                "planner": orchestrator.planner.agent_id,
                "verifier": orchestrator.verifier.agent_id,
                "memory_manager": orchestrator.memory_manager.agent_id,
                "executors": list(orchestrator.executors.keys())
            }
        }
    
    return stats


@app.post("/api/v1/llm/test")
async def test_llm(prompt: str = "Hola, ¿cómo estás?"):
    """
    Endpoint de prueba para el LLM Router
    """
    
    if llm_router is None:
        raise HTTPException(
            status_code=503,
            detail="LLM Router no inicializado"
        )
    
    try:
        response = await llm_router.chat_completion(prompt)
        
        return {
            "prompt": prompt,
            "response": response,
            "stats": llm_router.get_stats()
        }
        
    except Exception as e:
        logger.exception("Error en test LLM")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@app.post("/api/v1/rag/test")
async def test_rag_system(
    query: str = "test query",
    content: str = "This is a test content for RAG system"
):
    """
    Endpoint de prueba del sistema RAG completo
    Almacena contenido de prueba y luego lo busca
    """
    
    try:
        from app.api.memory import get_memory_manager
        
        logger.info("Probando sistema RAG...")
        
        # Obtener Memory Manager
        memory_mgr = get_memory_manager()
        
        # Paso 1: Almacenar contenido de prueba
        test_source = {
            "title": "Test Document",
            "source_type": "test",
            "tags": ["test", "rag"]
        }
        
        store_result = await memory_mgr.store_insight(
            insight=content,
            metadata=test_source
        )
        
        if not store_result.get("success"):
            raise Exception(f"Error almacenando: {store_result.get('error')}")
        
        # Paso 2: Buscar el contenido
        search_result = await memory_mgr.search_in_memory(
            query=query,
            limit=5
        )
        
        return {
            "status": "success",
            "test_query": query,
            "stored_content": content,
            "store_result": store_result,
            "search_result": search_result,
            "rag_system": "operational"
        }
        
    except Exception as e:
        logger.exception("Error en test RAG")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


# Incluir routers de endpoints
# Endpoints existentes del sistema
app.include_router(tools.router, prefix="/api/v1")
app.include_router(memory.router, prefix="/api/v1") 
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")

# Nuevos endpoints para IRIS Code
app.include_router(projects.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(assets.router)

# IRIS-Silhouette Bridge endpoints
app.include_router(bridge.router)

# VEO3 Video Generation endpoints
app.include_router(video.router)

# Live Preview System endpoints
app.include_router(preview.router)
app.include_router(terminals.router)

# Alias para compatibilidad con iris-agent frontend
@app.get("/metrics")
async def get_metrics():
    """Alias para /api/v1/stats - compatibilidad con iris-agent"""
    from app.api.health import get_system_stats
    return await get_system_stats()

@app.get("/api/v1/templates")
async def get_templates():
    """Listar templates disponibles"""
    # TODO: Implementar servicio de templates
    return {
        "templates": [
            {
                "id": "react-starter",
                "name": "React Starter",
                "description": "Plantilla básica de React con TypeScript",
                "category": "web-app",
                "tags": ["react", "typescript", "vite"]
            },
            {
                "id": "python-api", 
                "name": "Python API",
                "description": "API REST con FastAPI y PostgreSQL",
                "category": "backend",
                "tags": ["python", "fastapi", "postgresql"]
            }
        ],
        "total": 2
    }

@app.get("/projects/{project_id}/files")
async def get_project_files(project_id: str):
    """Alias para compatibilidad - delegar a endpoint de proyectos"""
    from app.api.projects import get_project_files
    return await get_project_files(project_id=project_id)


# =============================================================================
# HYPER-INTELLIGENT SYSTEM ENDPOINTS
# =============================================================================

@app.post("/api/v1/hyperintelligent/task", response_model=HyperIntelligentWorkflowResponse)
async def create_hyperintelligent_task(request: HyperIntelligentTaskRequest):
    """
    Crea y ejecuta una tarea usando el sistema hiperinteligente completo
    
    - **user_prompt**: Descripción natural de lo que quiere el usuario
    - **processing_mode**: 
      - "intent_analysis_only": Solo análisis de intención
      - "image_generation_only": Solo generación de imágenes
      - "full_hyperintelligent": Sistema completo (análisis + imágenes + equipos)
      - "enterprise_teams": Solo equipos Silhouette
    - **requirements**: Requerimientos específicos
    - **preferences**: Preferencias del usuario
    """
    
    if hyper_orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Hyper-Intelligent Orchestrator no inicializado"
        )
    
    try:
        logger.info(f"🚀 [Hiperinteligente] Nueva tarea: {request.user_prompt[:100]}...")
        
        # Crear solicitud interna
        from app.services.hyperintelligent_orchestrator import ProcessingMode as HIProcessingMode
        
        # Mapear modo de procesamiento
        mode_mapping = {
            "intent_analysis_only": HIProcessingMode.INTENT_ANALYSIS_ONLY,
            "image_generation_only": HIProcessingMode.IMAGE_GENERATION_ONLY,
            "full_hyperintelligent": HIProcessingMode.FULL_HYPERINTELLIGENT,
            "enterprise_teams": HIProcessingMode.ENTERPRISE_TEAMS
        }
        
        processing_mode = mode_mapping.get(request.processing_mode, HIProcessingMode.FULL_HYPERINTELLIGENT)
        
        # Crear deadline si se proporciona
        deadline = None
        if request.deadline:
            from datetime import datetime
            try:
                deadline = datetime.fromisoformat(request.deadline.replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Error parseando deadline: {e}")
        
        # Crear solicitud interna
        hyper_request = HyperIntelligentTaskRequest(
            request_id=f"api_{int(asyncio.get_event_loop().time())}",
            user_prompt=request.user_prompt,
            processing_mode=processing_mode,
            requirements=request.requirements,
            preferences=request.preferences,
            deadline=deadline
        )
        
        # Procesar con el orquestador hiperinteligente
        workflow = await hyper_orchestrator.process_hyperintelligent_task(hyper_request)
        
        # Convertir a response
        response = HyperIntelligentWorkflowResponse(
            workflow_id=workflow.workflow_id,
            status=workflow.status.value,
            progress=workflow.progress,
            current_phase=workflow.current_phase,
            phases_completed=workflow.phases_completed,
            execution_time=workflow.execution_time,
            intent_analysis=workflow.intent_analysis.to_dict() if workflow.intent_analysis else None,
            image_generation_result=workflow.image_generation_result,
            team_assignments=workflow.team_assignments,
            final_results=workflow.results,
            errors=workflow.errors,
            recommendations=workflow.results.get("recommendations", []) if workflow.results else [],
            next_actions=workflow.results.get("next_actions", []) if workflow.results else []
        )
        
        return response
        
    except Exception as e:
        logger.exception("Error procesando tarea hiperinteligente")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando tarea hiperinteligente: {str(e)}"
        )


@app.get("/api/v1/hyperintelligent/workflow/{workflow_id}")
async def get_hyperintelligent_workflow_status(workflow_id: str):
    """
    Obtiene el estado de un workflow hiperinteligente
    """
    
    if hyper_orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Hyper-Intelligent Orchestrator no inicializado"
        )
    
    # En implementación completa, recuperar desde base de datos
    # Por ahora, simular respuesta
    return {
        "workflow_id": workflow_id,
        "status": "not_implemented",
        "message": "Consulta de estado de workflow no implementada aún"
    }


@app.get("/api/v1/hyperintelligent/system/status")
async def get_hyperintelligent_system_status():
    """
    Obtiene el estado del sistema hiperinteligente
    """
    
    if hyper_orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Hyper-Intelligent Orchestrator no inicializado"
        )
    
    try:
        status = hyper_orchestrator.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@app.post("/api/v1/hyperintelligent/image/generate")
async def generate_hyperintelligent_image(
    prompt: str,
    image_type: str = "general",
    style: str = "modern",
    quality: str = "standard"
):
    """
    Genera imagen usando el sistema hiperinteligente de generación
    
    - **prompt**: Descripción de la imagen deseada
    - **image_type**: hero_image, logo, banner, icon, illustration
    - **style**: modern, minimalist, corporate, creative, technical
    - **quality**: draft, standard, premium
    """
    
    if hyper_orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Hyper-Intelligent Orchestrator no inicializado"
        )
    
    try:
        from app.services.hyper_image_generation import image_generation_system
        
        result = await image_generation_system.generate_hyper_intelligent_image(
            user_prompt=prompt,
            image_type=image_type,
            style=style,
            quality=quality
        )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        logger.exception("Error generando imagen hiperinteligente")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando imagen: {str(e)}"
        )


@app.post("/api/v1/hyperintelligent/intent/analyze")
async def analyze_intent(user_prompt: str):
    """
    Analiza la intención del usuario sin generar imágenes ni ejecutar equipos
    """
    
    if hyper_orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Hyper-Intelligent Orchestrator no inicializado"
        )
    
    try:
        from app.services.hyperintelligent_orchestrator import ProcessingMode
        
        # Crear solicitud solo para análisis
        request = HyperIntelligentTaskRequest(
            request_id=f"analysis_{int(asyncio.get_event_loop().time())}",
            user_prompt=user_prompt,
            processing_mode=ProcessingMode.INTENT_ANALYSIS_ONLY,
            requirements={},
            preferences={}
        )
        
        # Procesar solo el análisis
        workflow = await hyper_orchestrator.process_hyperintelligent_task(request)
        
        return {
            "status": "success",
            "workflow_id": workflow.workflow_id,
            "intent_analysis": workflow.intent_analysis.to_dict() if workflow.intent_analysis else None,
            "team_assignments": workflow.team_assignments,
            "estimated_effort": workflow.intent_analysis.estimated_effort if workflow.intent_analysis else None
        }
        
    except Exception as e:
        logger.exception("Error analizando intención")
        raise HTTPException(
            status_code=500,
            detail=f"Error analizando intención: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
