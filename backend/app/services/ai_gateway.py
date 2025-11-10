"""
AI Gateway Service
Integrates with existing LLM Router to provide AI model routing
Routes requests to optimal models based on task type
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

from ..core.llm_router import LLMRouter, LLMProvider
from ..core.config import settings

logger = logging.getLogger(__name__)

# AI Providers Configuration
AI_PROVIDERS = {
    "openrouter": {
        "name": "OpenRouter",
        "api_base": "https://openrouter.ai/api/v1",
        "api_key": os.getenv("OPENROUTER_API_KEY", ""),
        "models": {
            "multimodal_primary": {
                "id": "google/gemini-2.0-exp:free",
                "name": "Gemini 2.0 Experimental",
                "type": "multimodal",
                "capabilities": ["text", "image", "code", "reasoning", "creative"],
                "priority": 1,
                "rate_limit": "10000/day",
                "cost": "free"
            },
            "multimodal_fallback": {
                "id": "meta-llama/llama-3.1-70b-instruct:free", 
                "name": "Llama 3.1 70B",
                "type": "text",
                "capabilities": ["text", "code", "reasoning"],
                "priority": 2,
                "rate_limit": "5000/day",
                "cost": "free"
            },
            "analysis_specialist": {
                "id": "google/gemma-2-9b:free",
                "name": "Gemma 2 9B",
                "type": "text",
                "capabilities": ["analysis", "research", "summarization"],
                "priority": 3,
                "rate_limit": "3000/day",
                "cost": "free"
            }
        }
    },
    "minimax": {
        "name": "MiniMax",
        "api_base": "https://api.minimax.chat/v1",
        "api_key": os.getenv("MINIMAX_API_KEY", ""),
        "models": {
            "coding_primary": {
                "id": "abab6.5s-chat",
                "name": "MiniMax 6.5S Chat",
                "type": "coding",
                "capabilities": ["code_generation", "debugging", "architecture", "optimization"],
                "priority": 1,
                "focus": "programming",
                "cost": "free"
            },
            "coding_specialist": {
                "id": "abab6.5s-code",
                "name": "MiniMax 6.5S Code", 
                "type": "coding",
                "capabilities": ["code_completion", "refactoring", "testing", "documentation"],
                "priority": 2,
                "focus": "advanced_programming",
                "cost": "free"
            }
        }
    }
}

# Task Type Routing Rules
TASK_ROUTING = {
    "multimodal_analysis": {
        "primary": "openrouter.multimodal_primary",
        "fallback": ["openrouter.multimodal_fallback"],
        "description": "Image + text analysis, document understanding"
    },
    "creative_writing": {
        "primary": "openrouter.multimodal_primary", 
        "fallback": ["openrouter.multimodal_fallback"],
        "description": "Content creation, storytelling, creative tasks"
    },
    "logical_reasoning": {
        "primary": "openrouter.multimodal_primary",
        "fallback": ["openrouter.analysis_specialist"],
        "description": "Complex reasoning, problem solving, analysis"
    },
    "code_generation": {
        "primary": "minimax.coding_primary",
        "fallback": ["minimax.coding_specialist", "openrouter.multimodal_primary"],
        "description": "Code writing, API development, architecture"
    },
    "code_review": {
        "primary": "minimax.coding_specialist",
        "fallback": ["minimax.coding_primary"],
        "description": "Code review, optimization, best practices"
    },
    "debugging": {
        "primary": "minimax.coding_specialist", 
        "fallback": ["minimax.coding_primary"],
        "description": "Bug fixing, error analysis, debugging"
    },
    "system_architecture": {
        "primary": "minimax.coding_primary",
        "fallback": ["openrouter.multimodal_primary"],
        "description": "System design, architecture decisions, scaling"
    },
    "data_analysis": {
        "primary": "openrouter.multimodal_primary",
        "fallback": ["openrouter.analysis_specialist"],
        "description": "Data processing, analysis, visualization"
    },
    "documentation": {
        "primary": "openrouter.multimodal_primary",
        "fallback": ["minimax.coding_specialist"],
        "description": "Technical documentation, API docs, guides"
    }
}

class AIGateway:
    """
    AI Gateway service that routes requests to optimal AI models
    Works alongside existing LLM Router
    """
    
    def __init__(self):
        self.llm_router = None
        self.config = AI_PROVIDERS
        self.task_routing = TASK_ROUTING
        self._init_router()
    
    def _init_router(self):
        """Initialize the existing LLM Router"""
        try:
            self.llm_router = LLMRouter()
            logger.info("AI Gateway initialized with LLM Router")
        except Exception as e:
            logger.error(f"Failed to initialize LLM Router: {e}")
            self.llm_router = None
    
    def route_task(self, task_type: str) -> Dict[str, Any]:
        """
        Route a task to the optimal AI model
        """
        if task_type not in self.task_routing:
            # Default routing for unknown task types
            return {
                "provider": "minimax",
                "model": "coding_primary",
                "fallback": True,
                "reason": f"Unknown task type '{task_type}', using default"
            }
        
        routing_config = self.task_routing[task_type]
        primary_key = routing_config["primary"]
        
        if "." in primary_key:
            provider, model = primary_key.split(".", 1)
        else:
            provider, model = "minimax", primary_key
        
        return {
            "provider": provider,
            "model": model,
            "fallback": routing_config.get("fallback", []),
            "description": routing_config.get("description", ""),
            "task_type": task_type
        }
    
    async def process_request(
        self, 
        task_type: str, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a request through the AI Gateway
        """
        try:
            # Route to optimal model
            routing = self.route_task(task_type)
            
            # Use existing LLM Router for actual processing
            if self.llm_router:
                # Map task type to LLM Provider
                if routing["provider"] == "minimax":
                    provider = LLMProvider.MINIMAX_M2
                elif routing["provider"] == "openrouter":
                    # Map to appropriate OpenRouter model
                    if "gemini" in routing["model"]:
                        provider = LLMProvider.OPENROUTER_GEMINI
                    elif "llama" in routing["model"]:
                        provider = LLMProvider.OPENROUTER_LLAMA31_70B
                    else:
                        provider = LLMProvider.OPENROUTER_GPT4_TURBO
                else:
                    provider = LLMProvider.MINIMAX_M2
                
                # Process with LLM Router
                response = await self.llm_router.generate_completion(
                    prompt=prompt,
                    provider=provider,
                    context=context or {}
                )
                
                return {
                    "success": True,
                    "response": response.get("content", ""),
                    "provider": routing["provider"],
                    "model": routing["model"],
                    "task_type": task_type,
                    "routing_info": routing,
                    "usage": response.get("usage", {}),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Fallback to direct API call
                return await self._direct_api_call(routing, prompt, context)
                
        except Exception as e:
            logger.error(f"Error in AI Gateway: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_type": task_type,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _direct_api_call(
        self, 
        routing: Dict[str, Any], 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Direct API call as fallback
        """
        provider = routing["provider"]
        
        if provider == "openrouter":
            return await self._call_openrouter(routing["model"], prompt, context)
        elif provider == "minimax":
            return await self._call_minimax(routing["model"], prompt, context)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def _call_openrouter(
        self, 
        model: str, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Direct OpenRouter API call
        """
        api_key = self.config["openrouter"]["api_key"]
        if not api_key or api_key.startswith("${"):
            raise ValueError("OpenRouter API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are IRIS Code's AI assistant, helping with development and problem-solving."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"],
                    "provider": "openrouter",
                    "model": model
                }
            else:
                raise Exception(f"OpenRouter API error: {response.status_code}")
    
    async def _call_minimax(
        self, 
        model: str, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Direct MiniMax API call
        """
        api_key = self.config["minimax"]["api_key"]
        if not api_key or api_key.startswith("${"):
            raise ValueError("MiniMax API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.minimax.chat/v1/text/chatcompletion_pro",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are IRIS Code's coding specialist, helping with programming and development tasks."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data["reply"],
                    "provider": "minimax",
                    "model": model
                }
            else:
                raise Exception(f"MiniMax API error: {response.status_code}")
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        Get list of available models
        """
        return {
            "providers": self.config,
            "routing": self.task_routing,
            "status": "active" if self.llm_router else "direct_only"
        }
    
    def is_configured(self) -> bool:
        """
        Check if AI Gateway is properly configured
        """
        openrouter_key = self.config["openrouter"]["api_key"]
        minimax_key = self.config["minimax"]["api_key"]
        
        configured = []
        if openrouter_key and not openrouter_key.startswith("${"):
            configured.append("openrouter")
        if minimax_key and not minimax_key.startswith("${"):
            configured.append("minimax")
        
        return len(configured) > 0

# Global instance
ai_gateway = AIGateway()