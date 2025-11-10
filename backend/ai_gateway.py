"""
AI Gateway Service - Router inteligente de IA
Centraliza el acceso a múltiples modelos de IA con fallback automático
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import logging
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="AI Gateway",
    description="Router inteligente de IA para Silhouette Enterprise",
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
class AIRequest(BaseModel):
    prompt: str
    task_type: Optional[str] = None
    model_preference: Optional[str] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

class AIResponse(BaseModel):
    response: str
    model_used: str
    processing_time: float
    task_type: str
    confidence: float
    fallback_used: bool = False

class ModelStatus(BaseModel):
    model_name: str
    status: str
    last_check: str
    response_time: float
    available: bool

# Estado de los modelos
model_status = {
    "minimax_m2": {"status": "unknown", "last_check": None, "response_time": 0, "available": False},
    "gemini_2_0": {"status": "unknown", "last_check": None, "response_time": 0, "available": False},
    "claude_3": {"status": "unknown", "last_check": None, "response_time": 0, "available": False},
    "gpt_4": {"status": "unknown", "last_check": None, "response_time": 0, "available": False},
    "llama_3_1": {"status": "unknown", "last_check": None, "response_time": 0, "available": False}
}

# Configuración de APIs
API_CONFIGS = {
    "minimax": {
        "base_url": "https://api.minimax.chat/v1",
        "api_key": os.getenv("MINIMAX_API_KEY"),
        "headers": {"Authorization": f"Bearer {os.getenv('MINIMAX_API_KEY')}"}
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "headers": {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"}
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "headers": {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    }
}

@app.get("/")
async def root():
    """Health check del AI Gateway"""
    return {
        "service": "AI Gateway",
        "version": "1.0.0",
        "status": "operational",
        "models": list(model_status.keys())
    }

@app.get("/health")
async def health_check():
    """Health check detallado"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models": model_status
    }

@app.get("/models/status", response_model=List[ModelStatus])
async def get_models_status():
    """Obtiene el estado de todos los modelos"""
    statuses = []
    for model_name, status in model_status.items():
        statuses.append(ModelStatus(
            model_name=model_name,
            status=status["status"],
            last_check=status["last_check"],
            response_time=status["response_time"],
            available=status["available"]
        ))
    return statuses

@app.post("/ai/route", response_model=AIResponse)
async def route_ai_request(request: AIRequest):
    """
    Ruta una solicitud de IA al modelo más apropiado con fallback automático
    """
    start_time = datetime.now()
    
    try:
        # Detectar tipo de tarea si no se proporciona
        task_type = request.task_type or await detect_task_type(request.prompt)
        
        # Seleccionar modelo óptimo
        optimal_model = select_optimal_model(task_type, request.model_preference)
        
        # Intentar generar respuesta
        response = await generate_with_fallback(request.prompt, optimal_model, task_type)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AIResponse(
            response=response["content"],
            model_used=response["model"],
            processing_time=processing_time,
            task_type=task_type,
            confidence=response["confidence"],
            fallback_used=response.get("fallback", False)
        )
        
    except Exception as e:
        logger.error(f"Error procesando solicitud AI: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando solicitud: {str(e)}"
        )

async def detect_task_type(prompt: str) -> str:
    """Detecta el tipo de tarea basándose en el prompt"""
    prompt_lower = prompt.lower()
    
    # Patrones de detección
    if any(word in prompt_lower for word in ["generar imagen", "crear imagen", "image", "visual"]):
        return "image_generation"
    elif any(word in prompt_lower for word in ["código", "programar", "develop", "code"]):
        return "code_generation"
    elif any(word in prompt_lower for word in ["analizar", "análisis", "analyze", "research"]):
        return "analysis"
    elif any(word in prompt_lower for word in ["escribir", "crear contenido", "write", "content"]):
        return "content_creation"
    elif any(word in prompt_lower for word in ["pregunta", "question", "explicar", "explain"]):
        return "question_answering"
    else:
        return "general"

def select_optimal_model(task_type: str, preference: Optional[str] = None) -> str:
    """Selecciona el modelo óptimo para el tipo de tarea"""
    
    # Configuración de modelos por tipo de tarea
    model_preferences = {
        "image_generation": ["gemini_2_0", "claude_3", "gpt_4"],
        "code_generation": ["minimax_m2", "gpt_4", "claude_3"],
        "analysis": ["claude_3", "gpt_4", "gemini_2_0"],
        "content_creation": ["claude_3", "gpt_4", "gemini_2_0"],
        "question_answering": ["claude_3", "gpt_4", "gemini_2_0"],
        "general": ["claude_3", "gpt_4", "gemini_2_0"]
    }
    
    # Obtener lista de modelos preferidos
    preferred_models = model_preferences.get(task_type, model_preferences["general"])
    
    # Si hay preferencia específica, moverla al inicio
    if preference and preference in preferred_models:
        preferred_models.remove(preference)
        preferred_models.insert(0, preference)
    
    # Filtrar solo modelos disponibles
    available_models = [m for m in preferred_models if model_status[m]["available"]]
    
    # Retornar el primer modelo disponible, o el primero de la lista como fallback
    return available_models[0] if available_models else preferred_models[0]

async def generate_with_fallback(prompt: str, primary_model: str, task_type: str) -> Dict[str, Any]:
    """Genera respuesta con fallback automático a modelos alternativos"""
    
    # Orden de fallback para el modelo primario
    fallback_order = {
        "minimax_m2": ["claude_3", "gpt_4", "llama_3_1"],
        "gemini_2_0": ["claude_3", "gpt_4", "minimax_m2"],
        "claude_3": ["gpt_4", "gemini_2_0", "minimax_m2"],
        "gpt_4": ["claude_3", "gemini_2_0", "minimax_m2"],
        "llama_3_1": ["claude_3", "gpt_4", "gemini_2_0"]
    }
    
    # Obtener lista de fallback
    fallback_models = fallback_order.get(primary_model, ["claude_3", "gpt_4", "gemini_2_0"])
    
    # Intentar con cada modelo
    for model in [primary_model] + fallback_models:
        try:
            response = await call_model(model, prompt, task_type)
            if response:
                # Actualizar estado del modelo
                model_status[model]["status"] = "operational"
                model_status[model]["last_check"] = datetime.now().isoformat()
                model_status[model]["available"] = True
                return response
        except Exception as e:
            logger.warning(f"Modelo {model} falló: {e}")
            model_status[model]["status"] = "error"
            model_status[model]["last_check"] = datetime.now().isoformat()
            model_status[model]["available"] = False
            continue
    
    # Si todos fallan, retornar respuesta simulada
    logger.error("Todos los modelos fallaron, retornando respuesta simulada")
    return {
        "content": "Lo siento, no pude generar una respuesta en este momento. Por favor, intenta nuevamente.",
        "model": "fallback",
        "confidence": 0.1,
        "fallback": True
    }

async def call_model(model: str, prompt: str, task_type: str) -> Optional[Dict[str, Any]]:
    """Llama a un modelo específico (simulado)"""
    start_time = datetime.now()
    
    try:
        # Simular llamadas a diferentes APIs
        if model == "minimax_m2":
            return await call_minimax(prompt, task_type)
        elif model == "gemini_2_0":
            return await call_gemini(prompt, task_type)
        elif model == "claude_3":
            return await call_claude(prompt, task_type)
        elif model == "gpt_4":
            return await call_gpt4(prompt, task_type)
        elif model == "llama_3_1":
            return await call_llama(prompt, task_type)
        else:
            raise Exception(f"Modelo {model} no reconocido")
            
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        model_status[model]["response_time"] = processing_time
        raise e

async def call_minimax(prompt: str, task_type: str) -> Dict[str, Any]:
    """Llamada simulada a MiniMax M2"""
    await asyncio.sleep(1)  # Simular tiempo de respuesta
    
    if "código" in prompt.lower() or "code" in prompt.lower():
        return {
            "content": f"```python\n# Código generado por MiniMax M2 para: {task_type}\ndef solution():\n    print('Hello from MiniMax!')\n    return 'Solution implemented'\n```",
            "model": "minimax_m2",
            "confidence": 0.9
        }
    else:
        return {
            "content": f"Respuesta generada por MiniMax M2 para tarea: {task_type}. Contenido: {prompt[:100]}...",
            "model": "minimax_m2",
            "confidence": 0.8
        }

async def call_gemini(prompt: str, task_type: str) -> Dict[str, Any]:
    """Llamada simulada a Gemini 2.0"""
    await asyncio.sleep(0.8)  # Simular tiempo de respuesta
    
    if "imagen" in prompt.lower() or "visual" in prompt.lower():
        return {
            "content": f"Generación de imagen solicitada. Estilo recomendado para {task_type}: Moderno y profesional. Dimensiones sugeridas: 1024x1024. Paleta de colores: Azul corporativo y blanco.",
            "model": "gemini_2_0",
            "confidence": 0.85
        }
    else:
        return {
            "content": f"Análisis de Gemini 2.0: {prompt[:200]}... Tipo de tarea identificada: {task_type}",
            "model": "gemini_2_0",
            "confidence": 0.8
        }

async def call_claude(prompt: str, task_type: str) -> Dict[str, Any]:
    """Llamada simulada a Claude 3"""
    await asyncio.sleep(1.2)  # Simular tiempo de respuesta
    
    return {
        "content": f"Análisis detallado por Claude 3 para {task_type}: {prompt} - He identificado los elementos clave y proporciono una solución estructurada y bien fundamentada.",
        "model": "claude_3",
        "confidence": 0.9
    }

async def call_gpt4(prompt: str, task_type: str) -> Dict[str, Any]:
    """Llamada simulada a GPT-4"""
    await asyncio.sleep(1.5)  # Simular tiempo de respuesta
    
    return {
        "content": f"Solución GPT-4 para {task_type}: {prompt} - Respuesta completa con análisis profundo y recomendaciones específicas.",
        "model": "gpt_4",
        "confidence": 0.85
    }

async def call_llama(prompt: str, task_type: str) -> Dict[str, Any]:
    """Llamada simulada a Llama 3.1"""
    await asyncio.sleep(0.7)  # Simular tiempo de respuesta
    
    return {
        "content": f"Análisis de Llama 3.1: {task_type} task detected. Prompt: {prompt}. Providing comprehensive solution with technical details.",
        "model": "llama_3_1",
        "confidence": 0.75
    }

@app.post("/ai/test/{model_name}")
async def test_model(model_name: str, prompt: str = "Hello, test message"):
    """Endpoint para probar un modelo específico"""
    
    try:
        response = await call_model(model_name, prompt, "test")
        return {
            "model": model_name,
            "prompt": prompt,
            "response": response,
            "status": "success"
        }
    except Exception as e:
        return {
            "model": model_name,
            "prompt": prompt,
            "error": str(e),
            "status": "failed"
        }

# Simular verificación de estado de modelos al inicio
@app.on_event("startup")
async def startup_event():
    """Inicialización del AI Gateway"""
    logger.info("🚀 AI Gateway iniciando...")
    
    # Simular verificación inicial de modelos
    for model_name in model_status.keys():
        try:
            # En implementación real, harías una llamada real
            model_status[model_name]["status"] = "operational"
            model_status[model_name]["last_check"] = datetime.now().isoformat()
            model_status[model_name]["available"] = True
            model_status[model_name]["response_time"] = 1.0
        except Exception as e:
            model_status[model_name]["status"] = "error"
            model_status[model_name]["available"] = False
            logger.warning(f"Modelo {model_name} no disponible: {e}")
    
    logger.info("✅ AI Gateway inicializado con modelos: %s", list(model_status.keys()))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "ai_gateway:app",
        host="0.0.0.0",
        port=8002,
        reload=False
    )