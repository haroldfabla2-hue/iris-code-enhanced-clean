"""
API Endpoints para Generación de Assets en Tiempo Real
Sistema de chat para IRIS que permite generar cualquier asset
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime

from app.services.asset_generation_service import AssetGenerationService
from app.core.llm_router import LLMRouter

# Router con prefijo único
router = APIRouter(prefix="/api/v1/assets", tags=["assets"])

# Pydantic models
class AssetGenerationRequest(BaseModel):
    """Request para generar un asset"""
    prompt: str = Field(..., description="Descripción detallada del asset a generar")
    category: Optional[str] = Field(None, description="Categoría del asset (branding, marketing, etc.)")
    format_type: Optional[str] = Field(None, description="Formato específico (svg, html, png, etc.)")
    style: str = Field("modern", description="Estilo visual (modern, minimalist, corporate, etc.)")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Requerimientos específicos")
    stream: bool = Field(False, description="Activar streaming de respuesta")

class AssetResponse(BaseModel):
    """Response de generación de asset"""
    generation_id: str
    status: str
    timestamp: str
    category: str
    format: str
    files: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None
    preview_url: Optional[str] = None

class ChatMessage(BaseModel):
    """Mensaje de chat para IRIS"""
    message: str = Field(..., description="Mensaje del usuario")
    conversation_id: Optional[str] = Field(None, description="ID de conversación")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexto adicional")

class ChatResponse(BaseModel):
    """Response de chat con IRIS"""
    conversation_id: str
    message_id: str
    response: str
    asset_generated: Optional[AssetResponse] = None
    suggestions: List[str] = []
    timestamp: str

# Instancia global del servicio
asset_service = None

def get_asset_service(llm_router: LLMRouter = None) -> AssetGenerationService:
    """Dependency para AssetGenerationService"""
    global asset_service
    if asset_service is None:
        asset_service = AssetGenerationService(llm_router)
    return asset_service

@router.get("/categories", response_model=Dict[str, Any])
async def get_asset_categories(service: AssetGenerationService = Depends(get_asset_service)):
    """
    Obtiene las categorías de assets disponibles
    """
    try:
        categories = service.get_asset_categories()
        return {
            "status": "success",
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo categorías: {str(e)}")

@router.post("/generate", response_model=AssetResponse)
async def generate_asset(
    request: AssetGenerationRequest,
    background_tasks: BackgroundTasks,
    service: AssetGenerationService = Depends(get_asset_service)
):
    """
    Genera un asset basado en prompt y especificaciones
    
    - **prompt**: Descripción detallada del asset
    - **category**: Categoría (branding, mobile_ui, marketing, saas_platform, ecommerce, executive, ai_stress_test)
    - **format_type**: Formato específico (svg, html, png, jpg, etc.)
    - **style**: Estilo visual (modern, minimalist, corporate, creative, technical)
    - **requirements**: Requerimientos específicos adicionales
    """
    try:
        # Generar el asset
        result = await service.generate_asset(
            prompt=request.prompt,
            category=request.category,
            format_type=request.format_type,
            style=request.style,
            requirements=request.requirements
        )
        
        # Convertir a response model
        response = AssetResponse(
            generation_id=result.get("generation_id", ""),
            status=result.get("status", "unknown"),
            timestamp=result.get("timestamp", datetime.now().isoformat()),
            category=result.get("category", ""),
            format=result.get("format", ""),
            files=result.get("files", []),
            metadata=result.get("metadata", {}),
            error=result.get("error"),
            preview_url=result.get("files", [{}])[0].get("url") if result.get("files") else None
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando asset: {str(e)}")

@router.post("/generate/stream")
async def generate_asset_stream(
    request: AssetGenerationRequest,
    service: AssetGenerationService = Depends(get_asset_service)
):
    """
    Genera un asset con streaming de progreso
    """
    async def generate_stream():
        try:
            # Enviar progreso inicial
            yield f"data: {json.dumps({'status': 'starting', 'message': 'Iniciando generación...'})}\n\n"
            
            # Generar el asset
            result = await service.generate_asset(
                prompt=request.prompt,
                category=request.category,
                format_type=request.format_type,
                style=request.style,
                requirements=request.requirements
            )
            
            # Enviar progreso
            yield f"data: {json.dumps({'status': 'processing', 'message': 'Generando contenido...'})}\n\n"
            
            # Enviar resultado final
            response = AssetResponse(
                generation_id=result.get("generation_id", ""),
                status=result.get("status", "unknown"),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                category=result.get("category", ""),
                format=result.get("format", ""),
                files=result.get("files", []),
                metadata=result.get("metadata", {}),
                error=result.get("error"),
                preview_url=result.get("files", [{}])[0].get("url") if result.get("files") else None
            )
            
            yield f"data: {json.dumps({'status': 'completed', 'result': response.dict()})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.post("/chat", response_model=ChatResponse)
async def chat_with_iris(
    message: ChatMessage,
    service: AssetGenerationService = Depends(get_asset_service)
):
    """
    Chat con IRIS que puede generar assets automáticamente
    
    - **message**: Mensaje del usuario
    - **conversation_id**: ID de conversación (opcional)
    - **context**: Contexto adicional
    """
    try:
        conversation_id = message.conversation_id or f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        message_id = f"msg_{int(asyncio.get_event_loop().time())}"
        
        # Analizar el mensaje para detectar si requiere generación de asset
        requires_asset = await _analyze_if_requires_asset(message.message, service.llm_router)
        
        asset_result = None
        response_text = ""
        suggestions = []
        
        if requires_asset:
            # Generar asset automáticamente
            asset_result = await service.generate_asset(
                prompt=message.message,
                style="modern"
            )
            
            if asset_result.get("status") == "completed":
                response_text = f"¡Perfecto! He generado un asset {asset_result.get('category')} para ti. {asset_result.get('files', [{}])[0].get('filename', 'Asset')} está listo."
                suggestions = _generate_suggestions(asset_result)
            else:
                response_text = "He intentado generar el asset, pero hubo un error. ¿Podrías ser más específico con tu solicitud?"
        else:
            # Respuesta conversacional normal
            response_text = await _generate_conversational_response(message.message, service.llm_router)
            suggestions = [
                "Genera un logo para mi empresa",
                "Crea una landing page de marketing",
                "Diseña un dashboard analytics",
                "Haz una página de producto e-commerce"
            ]
        
        return ChatResponse(
            conversation_id=conversation_id,
            message_id=message_id,
            response=response_text,
            asset_generated=AssetResponse(
                generation_id=asset_result.get("generation_id", "") if asset_result else "",
                status=asset_result.get("status", "") if asset_result else "",
                timestamp=asset_result.get("timestamp", "") if asset_result else "",
                category=asset_result.get("category", "") if asset_result else "",
                format=asset_result.get("format", "") if asset_result else "",
                files=asset_result.get("files", []) if asset_result else [],
                metadata=asset_result.get("metadata", {}) if asset_result else {},
                error=asset_result.get("error") if asset_result else None,
                preview_url=asset_result.get("files", [{}])[0].get("url") if asset_result and asset_result.get("files") else None
            ) if asset_result else None,
            suggestions=suggestions,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en chat: {str(e)}")

@router.get("/generate/{generation_id}", response_model=AssetResponse)
async def get_generation_status(
    generation_id: str,
    service: AssetGenerationService = Depends(get_asset_service)
):
    """
    Obtiene el estado de una generación específica
    """
    # TODO: Implementar búsqueda en historial
    raise HTTPException(status_code=404, detail="Generación no encontrada o no implementada aún")

@router.get("/history", response_model=List[AssetResponse])
async def get_generation_history(
    limit: int = 50,
    service: AssetGenerationService = Depends(get_asset_service)
):
    """
    Obtiene el historial de generaciones
    """
    try:
        history = service.get_generation_history(limit)
        return [
            AssetResponse(
                generation_id=item.get("generation_id", ""),
                status=item.get("status", ""),
                timestamp=item.get("timestamp", ""),
                category=item.get("category", ""),
                format=item.get("format", ""),
                files=item.get("files", []),
                metadata=item.get("metadata", {}),
                error=item.get("error"),
                preview_url=item.get("files", [{}])[0].get("url") if item.get("files") else None
            )
            for item in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")

@router.post("/regenerate/{generation_id}", response_model=AssetResponse)
async def regenerate_asset(
    generation_id: str,
    new_prompt: Optional[str] = None,
    service: AssetGenerationService = Depends(get_asset_service)
):
    """
    Regenera un asset existente con nuevas especificaciones
    """
    try:
        result = await service.regenerate_asset(generation_id, new_prompt)
        
        if result.get("status") == "not_implemented":
            raise HTTPException(status_code=501, detail="Regeneración no implementada aún")
        
        response = AssetResponse(
            generation_id=result.get("generation_id", ""),
            status=result.get("status", ""),
            timestamp=result.get("timestamp", ""),
            category=result.get("category", ""),
            format=result.get("format", ""),
            files=result.get("files", []),
            metadata=result.get("metadata", {}),
            error=result.get("error"),
            preview_url=result.get("files", [{}])[0].get("url") if result.get("files") else None
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerando asset: {str(e)}")

# Funciones auxiliares
async def _analyze_if_requires_asset(message: str, llm_router: LLMRouter = None) -> bool:
    """Analiza si un mensaje requiere generación de asset"""
    message_lower = message.lower()
    
    # Palabras clave que indican generación de asset
    asset_keywords = [
        "genera", "crea", "diseña", "haz", "build", "make", "create", "design",
        "logo", "branding", "página", "website", "dashboard", "app", "icono",
        "landing", "ecommerce", "marketing", "presentación"
    ]
    
    # Si contiene palabras clave de assets, probablemente requiere generación
    if any(keyword in message_lower for keyword in asset_keywords):
        return True
    
    # Si es muy corto, probablemente no requiere asset
    if len(message.split()) < 3:
        return False
    
    # Análisis más avanzado con LLM si está disponible
    if llm_router:
        try:
            analysis_prompt = f"""
            Analiza si este mensaje requiere generar un asset visual o web:
            
            MENSAJE: {message}
            
            Responde solo "YES" o "NO".
            """
            response = await llm_router.chat_completion(analysis_prompt)
            return "YES" in response.upper()
        except Exception as e:
            print(f"Error en análisis LLM: {e}")
    
    return False

async def _generate_conversational_response(message: str, llm_router: LLMRouter = None) -> str:
    """Genera una respuesta conversacional para IRIS"""
    if llm_router:
        try:
            response_prompt = f"""
            Eres IRIS, un asistente de IA especializado en generación de assets. 
            Responde de manera amigable y útil a este mensaje:
            
            MENSAJE: {message}
            
            Si el mensaje no es sobre generar assets, responde de forma conversacional y ofrece ayuda.
            """
            return await llm_router.chat_completion(response_prompt)
        except Exception as e:
            print(f"Error generando respuesta: {e}")
    
    # Respuesta de fallback
    responses = [
        "¡Hola! ¿En qué puedo ayudarte hoy? Puedo generar logos, páginas web, dashboards y más.",
        "Estoy aquí para ayudarte a crear assets increíbles. ¿Qué te gustaría generar?",
        "¡Perfecto! Estoy listo para generar cualquier asset que necesites.",
        "Como IRIS, puedo crear desde logos hasta aplicaciones completas. ¿Qué tienes en mente?"
    ]
    
    import random
    return random.choice(responses)

def _generate_suggestions(asset_result: Dict[str, Any]) -> List[str]:
    """Genera sugerencias basadas en el resultado"""
    category = asset_result.get("category", "")
    
    suggestions_map = {
        "branding": [
            "Genera un favicon para la web",
            "Crea un paquete de marca completo",
            "Diseña tarjetas de presentación"
        ],
        "marketing": [
            "Crea un banner para redes sociales",
            "Genera una newsletter",
            "Diseña un flyer promocional"
        ],
        "saas_platform": [
            "Crea un dashboard de usuarios",
            "Genera una página de configuración",
            "Diseña gráficos de analytics"
        ],
        "ecommerce": [
            "Crea una página de checkout",
            "Genera un carrito de compras",
            "Diseña filtros de productos"
        ],
        "executive": [
            "Crea una presentación de pitch",
            "Genera un reporte ejecutivo",
            "Diseña slides de investor"
        ]
    }
    
    return suggestions_map.get(category, [
        "¿Te gustaría generar otro asset?",
        "¿Necesitas una variación de este asset?",
        "¿Quieres que añada funcionalidades?"
    ])
