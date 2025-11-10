"""
Intent Analyzer Service - Analizador de intención hiperinteligente
Procesa y analiza intenciones del usuario de forma independiente
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import logging
import os
from datetime import datetime
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Intent Analyzer",
    description="Servicio especializado en análisis de intención de usuario",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de request/response
class IntentAnalysisRequest(BaseModel):
    user_prompt: str
    context: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

class IntentAnalysisResponse(BaseModel):
    analysis_id: str
    original_prompt: str
    primary_intent: str
    task_type: str
    complexity: str
    required_teams: List[str]
    sub_tasks: List[Dict[str, Any]]
    context: Dict[str, Any]
    estimated_effort: str
    success_criteria: List[str]
    dependencies: List[str]
    confidence_score: float
    processing_time: float

class IntentValidationRequest(BaseModel):
    user_prompt: str
    suggested_intent: str
    context: Optional[Dict[str, Any]] = None

# Simulación de análisis de intención
async def analyze_user_intent(prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """Analiza la intención del usuario de forma inteligente"""
    start_time = datetime.now()
    
    # Detectar tipo de tarea
    task_type = detect_task_type(prompt)
    
    # Evaluar complejidad
    complexity = assess_complexity(prompt)
    
    # Extraer intención principal
    primary_intent = extract_primary_intent(prompt)
    
    # Descomponer en subtareas
    sub_tasks = decompose_into_subtasks(prompt, task_type)
    
    # Mapear equipos requeridos
    required_teams = map_required_teams(task_type, complexity)
    
    # Extraer contexto adicional
    extracted_context = extract_context(prompt, context)
    
    # Estimar esfuerzo
    estimated_effort = estimate_effort(complexity, len(sub_tasks))
    
    # Definir criterios de éxito
    success_criteria = define_success_criteria(task_type, prompt)
    
    # Identificar dependencias
    dependencies = identify_dependencies(sub_tasks)
    
    processing_time = (datetime.now() - start_time).total_seconds()
    
    return {
        "analysis_id": f"analysis_{int(datetime.now().timestamp())}",
        "original_prompt": prompt,
        "primary_intent": primary_intent,
        "task_type": task_type,
        "complexity": complexity,
        "required_teams": required_teams,
        "sub_tasks": sub_tasks,
        "context": extracted_context,
        "estimated_effort": estimated_effort,
        "success_criteria": success_criteria,
        "dependencies": dependencies,
        "confidence_score": calculate_confidence(prompt, task_type),
        "processing_time": processing_time
    }

def detect_task_type(prompt: str) -> str:
    """Detecta el tipo de tarea basándose en el prompt"""
    prompt_lower = prompt.lower()
    
    # Patrones de detección
    if any(word in prompt_lower for word in ["sitio web", "website", "página web", "web"]):
        return "web_development"
    elif any(word in prompt_lower for word in ["app", "aplicación", "móvil", "mobile"]):
        return "mobile_app_development"
    elif any(word in prompt_lower for word in ["presentación", "presentation", "slides"]):
        return "presentation_creation"
    elif any(word in prompt_lower for word in ["imagen", "imagenes", "logo", "diseño visual", "visual"]):
        return "image_generation"
    elif any(word in prompt_lower for word in ["documento", "reporte", "manual", "escribir"]):
        return "document_creation"
    elif any(word in prompt_lower for word in ["análisis", "datos", "analytics", "investigación"]):
        return "data_analysis"
    elif any(word in prompt_lower for word in ["investigación", "research", "estudio", "mercado"]):
        return "research"
    elif any(word in prompt_lower for word in ["estrategia", "plan negocio", "business plan"]):
        return "business_strategy"
    else:
        return "general_task"

def assess_complexity(prompt: str) -> str:
    """Evalúa la complejidad de la tarea"""
    prompt_lower = prompt.lower()
    
    # Indicadores de complejidad
    simple_indicators = ["simple", "básico", "quick", "rápido", "fácil"]
    moderate_indicators = ["desarrollar", "crear", "construir", "múltiple"]
    complex_indicators = ["sistema", "plataforma", "complejo", "avanzado", "enterprise"]
    
    simple_count = sum(1 for word in simple_indicators if word in prompt_lower)
    moderate_count = sum(1 for word in moderate_indicators if word in prompt_lower)
    complex_count = sum(1 for word in complex_indicators if word in prompt_lower)
    
    # Evaluar longitud
    length_factor = len(prompt) / 100  # Normalizar por 100 caracteres
    
    # Evaluar número de requisitos
    requirements = [word for word in prompt_lower.split() if word in ["necesito", "requiero", "quiero"]]
    requirements_count = len(requirements)
    
    complexity_score = (moderate_count * 1) + (complex_count * 2) + (length_factor * 0.5) + (requirements_count * 0.3)
    
    if complexity_score < 2:
        return "simple"
    elif complexity_score < 4:
        return "moderate"
    elif complexity_score < 6:
        return "complex"
    else:
        return "enterprise"

def extract_primary_intent(prompt: str) -> str:
    """Extrae la intención principal del prompt"""
    # Simplificado: tomar los primeros 100 caracteres o hasta el primer punto
    if "." in prompt:
        return prompt[:100] + "..."
    return prompt[:100] + "..." if len(prompt) > 100 else prompt

def decompose_into_subtasks(prompt: str, task_type: str) -> List[Dict[str, Any]]:
    """Descompone la tarea en subtareas específicas"""
    
    subtasks_map = {
        "web_development": [
            {"name": "Análisis de requerimientos", "duration": "2-4 horas", "team": "research_team"},
            {"name": "Diseño de wireframes", "duration": "4-6 horas", "team": "ui_design_team"},
            {"name": "Desarrollo frontend", "duration": "1-2 días", "team": "frontend_team"},
            {"name": "Desarrollo backend", "duration": "1-2 días", "team": "backend_team"},
            {"name": "Testing y QA", "duration": "4-6 horas", "team": "testing_team"},
            {"name": "Deploy y configuración", "duration": "2-4 horas", "team": "devops_team"}
        ],
        "mobile_app_development": [
            {"name": "Investigación de mercado", "duration": "4-6 horas", "team": "market_research_team"},
            {"name": "Diseño de UI/UX móvil", "duration": "1-2 días", "team": "mobile_design_team"},
            {"name": "Desarrollo de app", "duration": "2-3 días", "team": "mobile_dev_team"},
            {"name": "Backend y APIs", "duration": "1-2 días", "team": "backend_team"},
            {"name": "Testing y debugging", "duration": "4-6 horas", "team": "testing_team"},
            {"name": "Publicación en stores", "duration": "2-3 horas", "team": "app_store_team"}
        ],
        "image_generation": [
            {"name": "Análisis de intención visual", "duration": "30 min", "team": "visual_strategy_team"},
            {"name": "Creación de prompts", "duration": "1-2 horas", "team": "prompt_engineering_team"},
            {"name": "Generación de imágenes", "duration": "1-2 horas", "team": "image_generation_team"},
            {"name": "Post-procesamiento", "duration": "30-60 min", "team": "image_post_processing_team"}
        ],
        "presentation_creation": [
            {"name": "Estructura y contenido", "duration": "2-3 horas", "team": "content_team"},
            {"name": "Diseño de slides", "duration": "2-3 horas", "team": "design_team"},
            {"name": "Generación de visuales", "duration": "1-2 horas", "team": "image_generation_team"},
            {"name": "Revisión y refinamiento", "duration": "1-2 horas", "team": "content_team"}
        ]
    }
    
    return subtasks_map.get(task_type, [
        {"name": "Investigación y análisis", "duration": "2-4 horas", "team": "research_team"},
        {"name": "Desarrollo/implementación", "duration": "4-6 horas", "team": "specialized_team"},
        {"name": "Revisión y entrega", "duration": "1-2 horas", "team": "quality_team"}
    ])

def map_required_teams(task_type: str, complexity: str) -> List[str]:
    """Mapea los equipos requeridos según tipo y complejidad"""
    
    base_teams = {
        "web_development": ["ui_design_team", "frontend_team", "backend_team", "testing_team"],
        "mobile_app_development": ["mobile_design_team", "mobile_dev_team", "backend_team", "testing_team"],
        "image_generation": ["visual_strategy_team", "prompt_engineering_team", "image_generation_team"],
        "presentation_creation": ["content_team", "design_team", "image_generation_team"],
        "document_creation": ["content_team", "editing_team"],
        "data_analysis": ["data_science_team", "visualization_team"],
        "research": ["market_research_team", "analysis_team"],
        "business_strategy": ["business_planning_team", "market_analysis_team"]
    }
    
    teams = base_teams.get(task_type, ["research_team", "analysis_team"])
    
    # Agregar equipos base para complejidad
    if complexity in ["complex", "enterprise"]:
        teams.extend(["project_management_team", "quality_assurance_team"])
    
    return list(set(teams))  # Eliminar duplicados

def extract_context(prompt: str, provided_context: Optional[Dict] = None) -> Dict[str, Any]:
    """Extrae contexto adicional del prompt"""
    
    context = provided_context or {}
    
    # Detectar idioma
    context["language"] = "es" if any(word in prompt.lower() for word in ["crear", "desarrollar", "hacer"]) else "en"
    
    # Detectar urgencia
    context["urgency"] = "alta" if any(word in prompt.lower() for word in ["urgente", "rápido", "quick"]) else "normal"
    
    # Detectar industria
    if any(word in prompt.lower() for word in ["tech", "tecnología", "software"]):
        context["industry"] = "technology"
    elif any(word in prompt.lower() for word in ["salud", "health", "médico"]):
        context["industry"] = "healthcare"
    elif any(word in prompt.lower() for word in ["educación", "education"]):
        context["industry"] = "education"
    else:
        context["industry"] = "general"
    
    # Detectar audiencia
    if any(word in prompt.lower() for word in ["empresa", "business", "corporativo"]):
        context["audience"] = "business"
    elif any(word in prompt.lower() for word in ["joven", "young", "millennial"]):
        context["audience"] = "young_adults"
    else:
        context["audience"] = "general"
    
    return context

def estimate_effort(complexity: str, num_subtasks: int) -> str:
    """Estima el esfuerzo basado en complejidad y número de subtareas"""
    
    base_hours = {
        "simple": 4,
        "moderate": 8,
        "complex": 16,
        "enterprise": 32
    }
    
    estimated_hours = base_hours.get(complexity, 8) * (1 + num_subtasks * 0.1)
    
    if estimated_hours <= 8:
        return f"{estimated_hours:.0f} horas (1 día)"
    elif estimated_hours <= 24:
        return f"{estimated_hours:.0f} horas ({estimated_hours/8:.1f} días)"
    elif estimated_hours <= 80:
        return f"{estimated_hours:.0f} horas ({estimated_hours/8:.1f} días)"
    else:
        return f"{estimated_hours:.0f} horas ({estimated_hours/40:.1f} semanas)"

def define_success_criteria(task_type: str, prompt: str) -> List[str]:
    """Define criterios de éxito para la tarea"""
    
    criteria_map = {
        "web_development": [
            "Sitio web funcional y responsive",
            "Navegación intuitiva",
            "Optimización de velocidad",
            "Compatibilidad cross-browser"
        ],
        "mobile_app_development": [
            "App funcional en iOS y Android",
            "Interfaz intuitiva y atractiva",
            "Rendimiento óptimo",
            "Publicación en stores"
        ],
        "image_generation": [
            "Imágenes que reflejan la intención",
            "Calidad profesional",
            "Coherencia visual",
            "Resolución apropiada"
        ],
        "presentation_creation": [
            "Presentación visualmente atractiva",
            "Mensaje claro y estructurado",
            "Flujo narrativo coherente",
            "Elementos visuales impactantes"
        ]
    }
    
    return criteria_map.get(task_type, [
        "Objetivo principal cumplido",
        "Calidad profesional",
        "Cumplimiento de requerimientos",
        "Entrega en tiempo acordado"
    ])

def identify_dependencies(sub_tasks: List[Dict[str, Any]]) -> List[str]:
    """Identifica dependencias entre subtareas"""
    
    dependencies = []
    
    # Dependencias comunes
    task_names = [task["name"] for task in sub_tasks]
    
    if "Análisis de requerimientos" in task_names:
        dependencies.append("Diseño y wireframes")
    if "Diseño de wireframes" in task_names:
        dependencies.append("Desarrollo frontend")
    if "Generación de imágenes" in task_names:
        dependencies.append("Desarrollo frontend o diseño")
    if "Desarrollo backend" in task_names:
        dependencies.append("Integración y testing")
    if "Testing" in task_names:
        dependencies.append("Desarrollo completado")
    
    return list(set(dependencies))

def calculate_confidence(prompt: str, task_type: str) -> float:
    """Calcula la confianza del análisis"""
    
    base_confidence = 0.7
    
    # Ajustar confianza basándose en claridad del prompt
    clarity_indicators = len([word for word in prompt.split() if len(word) > 3])
    clarity_factor = min(0.2, clarity_indicators * 0.01)
    
    # Ajustar confianza basándose en especificidad
    if "específico" in prompt.lower() or "specific" in prompt.lower():
        specificity_factor = 0.1
    else:
        specificity_factor = 0
    
    confidence = base_confidence + clarity_factor + specificity_factor
    return min(0.95, max(0.5, confidence))

@app.get("/")
async def root():
    """Health check del Intent Analyzer"""
    return {
        "service": "Intent Analyzer",
        "version": "1.0.0",
        "status": "operational",
        "capabilities": [
            "Análisis de intención",
            "Clasificación de tareas",
            "Estimación de complejidad",
            "Mapeo de equipos",
            "Descomposición de tareas"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check detallado"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Intent Analyzer",
        "version": "1.0.0"
    }

@app.post("/intent/analyze", response_model=IntentAnalysisResponse)
async def analyze_intent_endpoint(request: IntentAnalysisRequest):
    """
    Analiza la intención del usuario y retorna análisis completo
    """
    try:
        logger.info(f"🔍 Analizando intención: {request.user_prompt[:100]}...")
        
        analysis = await analyze_user_intent(
            prompt=request.user_prompt,
            context=request.context
        )
        
        return IntentAnalysisResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Error analizando intención: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando análisis: {str(e)}"
        )

@app.post("/intent/validate")
async def validate_intent_endpoint(request: IntentValidationRequest):
    """
    Valida una intención sugerida
    """
    try:
        # Simular validación
        validation_result = {
            "original_prompt": request.user_prompt,
            "suggested_intent": request.suggested_intent,
            "validation_score": 0.85,
            "is_valid": True,
            "suggestions": [
                "La intención es clara y bien definida",
                "Se recomienda especificar más detalles sobre el resultado esperado"
            ]
        }
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validando intención: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error validando intención: {str(e)}"
        )

@app.get("/intent/task-types")
async def get_supported_task_types():
    """Retorna los tipos de tareas soportados"""
    return {
        "task_types": [
            "web_development",
            "mobile_app_development", 
            "presentation_creation",
            "image_generation",
            "document_creation",
            "data_analysis",
            "research",
            "business_strategy"
        ],
        "descriptions": {
            "web_development": "Desarrollo de sitios web y aplicaciones web",
            "mobile_app_development": "Desarrollo de aplicaciones móviles",
            "presentation_creation": "Creación de presentaciones y demos",
            "image_generation": "Generación de imágenes y elementos visuales",
            "document_creation": "Creación de documentos y reportes",
            "data_analysis": "Análisis de datos y generación de insights",
            "research": "Investigación de mercado y análisis competitivo",
            "business_strategy": "Estrategia empresarial y planificación"
        }
    }

@app.get("/intent/teams")
async def get_available_teams():
    """Retorna los equipos disponibles"""
    return {
        "teams": [
            "research_team",
            "ui_design_team", 
            "frontend_team",
            "backend_team",
            "mobile_dev_team",
            "testing_team",
            "content_team",
            "image_generation_team",
            "project_management_team",
            "quality_assurance_team"
        ],
        "specialties": {
            "research_team": "Investigación y análisis",
            "ui_design_team": "Diseño de interfaces",
            "frontend_team": "Desarrollo frontend",
            "backend_team": "Desarrollo backend",
            "mobile_dev_team": "Desarrollo móvil",
            "testing_team": "Testing y QA",
            "content_team": "Creación de contenido",
            "image_generation_team": "Generación de imágenes",
            "project_management_team": "Gestión de proyectos",
            "quality_assurance_team": "Control de calidad"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Inicialización del Intent Analyzer"""
    logger.info("🚀 Intent Analyzer iniciando...")
    logger.info("✅ Intent Analyzer inicializado - Listo para analizar intenciones")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "intent_analyzer:app",
        host="0.0.0.0", 
        port=8003,
        reload=False
    )