"""
API endpoints for IRIS-Silhouette Bridge
Provides frontend access to enhanced processing modes
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import logging

from ..services.iris_silhouette_bridge import bridge
from ..services.ai_gateway import ai_gateway
from ..models import AgentMessage, TaskResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bridge", tags=["bridge"])

@router.get("/status")
async def get_bridge_status():
    """Get comprehensive bridge system status"""
    try:
        status = bridge.get_unified_system_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Error getting bridge status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/iris-agents")
async def get_iris_agents_status():
    """Get IRIS agents status and enhancements"""
    try:
        status = bridge.get_iris_agents_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Error getting IRIS agents status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/silhouette-teams")
async def get_silhouette_teams_status():
    """Get Silhouette enterprise teams status"""
    try:
        status = bridge.get_silhouette_teams_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Error getting Silhouette teams status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processing-modes")
async def get_processing_modes():
    """Get available processing modes"""
    return {
        "modes": [
            {
                "id": "traditional",
                "name": "Traditional IRIS",
                "description": "Original IRIS Code agents - 100% backwards compatible",
                "features": ["Original 5 agents", "Monaco Editor", "Existing workflows"]
            },
            {
                "id": "enhanced",
                "name": "Enhanced IRIS",
                "description": "IRIS agents enhanced with AI assistance",
                "features": ["AI-powered reasoning", "Multimodal analysis", "Smart coding"]
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "description": "Silhouette v3.0 enterprise teams",
                "features": ["45+ specialized teams", "Business intelligence", "Enterprise analytics"]
            },
            {
                "id": "hybrid",
                "name": "Hybrid",
                "description": "Intelligent combination of IRIS + AI + Enterprise",
                "features": ["Smart routing", "Adaptive processing", "Best of all worlds"]
            }
        ],
        "current_mode": bridge.get_processing_mode()
    }

@router.post("/mode")
async def set_processing_mode(mode: str):
    """Set processing mode"""
    try:
        if bridge.set_processing_mode(mode):
            return {
                "success": True,
                "message": f"Processing mode set to: {mode}",
                "current_mode": bridge.get_processing_mode()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")
    except Exception as e:
        logger.error(f"Error setting processing mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-task")
async def process_task_enhanced(
    task_type: str,
    prompt: str,
    context: Optional[Dict[str, Any]] = None,
    user_mode: Optional[str] = None
):
    """Process task through bridge with enhanced capabilities"""
    try:
        result = await bridge.process_task(task_type, prompt, context, user_mode)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error processing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-models")
async def get_ai_models():
    """Get available AI models and routing configuration"""
    try:
        models = ai_gateway.get_available_models()
        return JSONResponse(content=models)
    except Exception as e:
        logger.error(f"Error getting AI models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-process")
async def process_ai_request(
    task_type: str,
    prompt: str,
    context: Optional[Dict[str, Any]] = None
):
    """Direct AI processing through gateway"""
    try:
        result = await ai_gateway.process_request(task_type, prompt, context)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in AI processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routing/{task_type}")
async def get_task_routing(task_type: str):
    """Get routing decision for a specific task type"""
    try:
        from ..services.iris_silhouette_bridge import TaskRouter
        router_instance = TaskRouter()
        routing = router_instance.route_task(task_type)
        return JSONResponse(content=routing)
    except Exception as e:
        logger.error(f"Error getting task routing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integration-info")
async def get_integration_info():
    """Get detailed information about IRIS-Silhouette integration"""
    return {
        "integration_summary": {
            "preserved": "100% original IRIS Code functionality",
            "enhanced": "AI Gateway with Gemini 2.0 + MiniMax",
            "added": "45+ Silhouette v3.0 enterprise teams",
            "modes": "Traditional, Enhanced, Enterprise, Hybrid",
            "cost": "Free (only API keys needed)"
        },
        "backwards_compatibility": {
            "status": "100%",
            "agents": "All 5 original agents preserved",
            "workflows": "Existing workflows maintained",
            "ui": "Original interface available",
            "api": "Existing endpoints work unchanged"
        },
        "new_capabilities": {
            "ai_gateway": {
                "multimodal": "Gemini 2.0 Experimental (OpenRouter)",
                "coding": "MiniMax 6.5S (specialist)",
                "routing": "Intelligent task-based routing"
            },
            "enterprise_teams": {
                "count": 45,
                "categories": 15,
                "examples": [
                    "Business Intelligence Team",
                    "Security & Compliance Team", 
                    "Technology Architecture Team",
                    "Operations & Performance Team"
                ]
            },
            "processing_modes": {
                "traditional": "Original IRIS Code experience",
                "enhanced": "IRIS + AI assistance",
                "enterprise": "Full Silhouette capabilities",
                "hybrid": "Intelligent auto-routing"
            }
        },
        "deployment": {
            "ready": True,
            "target": "Atlantic.Net server",
            "configuration": "Caddy reverse proxy setup",
            "services": "Docker compose orchestration"
        }
    }

@router.post("/unified-chat")
async def unified_chat_processing(
    message: str,
    mode: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
):
    """
    Unified chat processing that works with all modes
    Integrates with existing chat API
    """
    try:
        # Determine task type from message
        task_type = _determine_task_type(message)
        
        # Process through bridge
        result = await bridge.process_task(
            task_type=task_type,
            prompt=message,
            context=context or {},
            user_mode=mode
        )
        
        # Format as chat response
        return {
            "response": result.get("response", "Processing complete"),
            "mode": result.get("mode", "traditional"),
            "task_type": task_type,
            "processing_info": result.get("processing_info", {}),
            "success": result.get("success", True),
            "timestamp": result.get("processing_info", {}).get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error in unified chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _determine_task_type(message: str) -> str:
    """
    Determine task type from user message
    Simple heuristic for demonstration
    """
    message_lower = message.lower()
    
    # Code-related tasks
    if any(word in message_lower for word in ["code", "function", "class", "api", "debug", "error"]):
        return "code_generation"
    
    # Analysis tasks
    if any(word in message_lower for word in ["analyze", "analysis", "review", "examine"]):
        return "multimodal_analysis"
    
    # Planning tasks
    if any(word in message_lower for word in ["plan", "strategy", "design", "architecture"]):
        return "system_architecture"
    
    # Creative tasks
    if any(word in message_lower for word in ["create", "write", "generate", "build"]):
        return "creative_writing"
    
    # Default to simple chat
    return "simple_chat"