#!/usr/bin/env python3
"""
Servidor de prueba con solo endpoints de assets - sin dependencias complejas
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="IRIS Asset Generation Test Server",
    version="1.0.0-assets-test"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock models (simplified versions)
class AssetGenerationRequest(BaseModel):
    prompt: str
    category: Optional[str] = None
    format_type: Optional[str] = None
    style: str = "modern"
    requirements: Dict[str, Any] = {}

class AssetResponse(BaseModel):
    generation_id: str
    status: str
    timestamp: str
    category: str
    format: str
    files: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error: Optional[str] = None
    preview_url: Optional[str] = None

# Mock service (simplified)
class MockAssetService:
    def get_asset_categories(self) -> List[str]:
        return [
            "branding", "mobile_ui", "marketing", 
            "saas_platform", "ecommerce", 
            "executive", "ai_stress_test"
        ]
    
    async def generate_asset(self, **kwargs) -> Dict[str, Any]:
        # Mock generation
        import time
        import uuid
        
        await asyncio.sleep(0.1)  # Simulate processing
        
        return {
            "generation_id": str(uuid.uuid4()),
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "category": kwargs.get("category", "branding"),
            "format": kwargs.get("format_type", "svg"),
            "files": [
                {
                    "filename": f"asset_{int(time.time())}.svg",
                    "content": '<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg"><circle cx="100" cy="100" r="50" fill="blue"/></svg>',
                    "type": "svg",
                    "size": 256
                }
            ],
            "metadata": {
                "prompt": kwargs.get("prompt", ""),
                "style": kwargs.get("style", "modern")
            },
            "error": None
        }

# Global service instance
asset_service = MockAssetService()

# Endpoints
@app.get("/api/v1/assets/categories")
async def get_asset_categories():
    """Obtiene las categorías de assets disponibles"""
    try:
        categories = asset_service.get_asset_categories()
        return {
            "status": "success",
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo categorías: {str(e)}")

@app.post("/api/v1/assets/generate", response_model=AssetResponse)
async def generate_asset(request: AssetGenerationRequest):
    """Genera un asset basado en prompt y especificaciones"""
    try:
        result = await asset_service.generate_asset(
            prompt=request.prompt,
            category=request.category,
            format_type=request.format_type,
            style=request.style,
            requirements=request.requirements
        )
        
        return AssetResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando asset: {str(e)}")

@app.get("/api/v1/assets/formats")
async def get_formats():
    """Obtiene formatos disponibles"""
    return {
        "status": "success",
        "formats": ["svg", "html", "png", "jpg", "python", "json", "xml"],
        "total": 7
    }

@app.get("/api/v1/assets/history")
async def get_history():
    """Mock history"""
    return {
        "status": "success",
        "history": [],
        "total": 0
    }

# Health checks
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "server": "IRIS Asset Test Server",
        "version": "1.0.0-assets-test",
        "endpoints": {
            "assets_generate": "✅ ACTIVO",
            "assets_categories": "✅ ACTIVO", 
            "assets_formats": "✅ ACTIVO"
        }
    }

@app.get("/")
async def root():
    return {
        "status": "IRIS Asset Generation Server",
        "version": "1.0.0-assets-test",
        "message": "Servidor de prueba para endpoints de assets"
    }

if __name__ == "__main__":
    import uvicorn
    import asyncio
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")