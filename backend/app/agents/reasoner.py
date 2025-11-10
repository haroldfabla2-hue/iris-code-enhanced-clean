"""
Agente Reasoner - Analiza intención y prepara contexto
Responsable de interpretar, resumir contexto y preparar prompts
"""
from typing import List, Dict, Any
import json
from datetime import datetime

from .base import BaseAgent
from ..models import AgentMessage, AgentResponse, MessageStatus, MessageIntent


class ReasonerAgent(BaseAgent):
    """
    Agente Reasoner: Analiza la intención del usuario y descompone el problema
    
    Responsabilidades:
    - Interpretar intención del usuario
    - Resumir contexto relevante
    - Preparar prompts enriquecidos
    - Definir estrategia de exploración
    """
    
    def __init__(self, llm_client: Any = None):
        super().__init__(
            agent_id="reasoner",
            llm_client=llm_client
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "intent_analysis",
            "context_summarization",
            "strategy_definition",
            "prompt_preparation"
        ]
    
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """
        Procesa mensaje analizando intención y preparando estrategia
        """
        self.log_trace("reasoner_start", {
            "message_id": message.message_id,
            "intent": message.intent
        })
        
        try:
            # Extraer objetivo del payload
            objetivo = message.payload.get("objetivo", "")
            contexto = message.payload.get("contexto", {})
            historial = message.payload.get("historial", [])
            
            # Analizar intención
            intent_analysis = await self._analyze_intent(objetivo, contexto)
            
            # Definir estrategia
            strategy = await self._define_strategy(intent_analysis, contexto)
            
            # Preparar contexto enriquecido
            enriched_context = await self._enrich_context(
                objetivo,
                contexto,
                historial,
                strategy
            )
            
            result = {
                "intent_analysis": intent_analysis,
                "strategy": strategy,
                "enriched_context": enriched_context,
                "recommendations": {
                    "agents_needed": strategy.get("agents_needed", 1),
                    "parallel_execution": strategy.get("parallel", False),
                    "tools_suggested": strategy.get("tools", [])
                }
            }
            
            self.log_trace("reasoner_complete", {
                "message_id": message.message_id,
                "agents_needed": result["recommendations"]["agents_needed"]
            })
            
            return AgentResponse(
                message_id=f"resp_{message.message_id}",
                original_message_id=message.message_id,
                agent_id=self.agent_id,
                status=MessageStatus.DONE,
                result=result
            )
            
        except Exception as e:
            self.logger.exception("Error en Reasoner")
            raise
    
    async def _analyze_intent(
        self,
        objetivo: str,
        contexto: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analiza la intención del usuario"""
        
        # Categorizar tipo de tarea
        task_type = self._categorize_task(objetivo)
        
        # Estimar complejidad
        complexity = self._estimate_complexity(objetivo, contexto)
        
        prompt = f"""Analiza la siguiente solicitud del usuario y extrae la intención principal:

Objetivo: {objetivo}
Contexto: {json.dumps(contexto, indent=2)}

Proporciona:
1. Intención principal
2. Subtareas identificadas
3. Requisitos de información
4. Criterios de éxito
"""
        
        # Llamar al LLM
        llm_response = await self.call_llm(prompt, temperature=0.3)
        
        return {
            "type": task_type,
            "complexity": complexity,
            "main_intent": objetivo,
            "llm_analysis": llm_response,
            "requires_tools": self._requires_tools(objetivo),
            "requires_memory": self._requires_memory(contexto)
        }
    
    async def _define_strategy(
        self,
        intent_analysis: Dict[str, Any],
        contexto: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Define estrategia de ejecución basada en complejidad"""
        
        complexity = intent_analysis.get("complexity", "medium")
        task_type = intent_analysis.get("type", "general")
        
        # Herramientas recomendadas basadas en el tipo de tarea
        if task_type == "coding":
            tools = ["python_executor", "file_processor"]
        elif task_type == "research":
            tools = ["search_engine", "web_scraper"]
        elif task_type == "analysis":
            tools = ["python_executor", "search_engine", "file_processor"]
        elif task_type == "web_interaction":
            tools = ["web_scraper", "search_engine"]
        else:
            tools = ["python_executor", "search_engine"]
        
        # Estrategia según complejidad (basado en arquitectura)
        if complexity == "low":
            agents_needed = 1
            parallel = False
            tools = tools[:2]  # Limitar herramientas
        elif complexity == "medium":
            agents_needed = 2
            parallel = True
            tools = tools[:3]  # Herramientas principales
        else:  # high
            agents_needed = min(5, len(tools) + 2)
            parallel = True
            tools = tools  # Todas las herramientas
        
        return {
            "approach": "breadth_first" if parallel else "sequential",
            "agents_needed": agents_needed,
            "parallel": parallel,
            "tools": tools,
            "task_type": task_type,
            "reasoning_model": "claude3_5",
            "planning_model": "llama70b",
            "budget": {
                "tokens_per_agent": 4000,
                "time_seconds": 120,
                "max_iterations": 3
            },
            "criteria": {
                "success_threshold": 0.85,
                "quality_gate": True
            }
        }
    
    async def _enrich_context(
        self,
        objetivo: str,
        contexto: Dict[str, Any],
        historial: List[Dict],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enriquece el contexto con información relevante"""
        
        return {
            "objetivo": objetivo,
            "contexto_original": contexto,
            "historial_resumido": self._summarize_history(historial),
            "strategy": strategy,
            "timestamp": datetime.utcnow().isoformat(),
            "memory_hints": self._extract_memory_hints(contexto),
            "constraints": self._extract_constraints(contexto)
        }
    
    def _categorize_task(self, objetivo: str) -> str:
        """Categoriza el tipo de tarea"""
        objetivo_lower = objetivo.lower()
        
        if any(kw in objetivo_lower for kw in ["código", "programar", "implementar", "desarrollar"]):
            return "coding"
        elif any(kw in objetivo_lower for kw in ["buscar", "investigar", "encontrar", "información"]):
            return "research"
        elif any(kw in objetivo_lower for kw in ["analizar", "comparar", "evaluar"]):
            return "analysis"
        elif any(kw in objetivo_lower for kw in ["web", "navegar", "scrape"]):
            return "web_interaction"
        else:
            return "general"
    
    def _estimate_complexity(self, objetivo: str, contexto: Dict) -> str:
        """Estima complejidad de la tarea"""
        # Heurística simple basada en longitud y contexto
        words = len(objetivo.split())
        has_context = bool(contexto)
        
        if words < 10 and not has_context:
            return "low"
        elif words < 30 or (words < 50 and not has_context):
            return "medium"
        else:
            return "high"
    
    def _requires_tools(self, objetivo: str) -> bool:
        """Determina si requiere herramientas externas"""
        tool_keywords = ["código", "web", "buscar", "archivo", "git", "documento"]
        return any(kw in objetivo.lower() for kw in tool_keywords)
    
    def _requires_memory(self, contexto: Dict) -> bool:
        """Determina si requiere acceso a memoria"""
        return bool(contexto.get("session_id") or contexto.get("user_id"))
    
    def _summarize_history(self, historial: List[Dict]) -> str:
        """Resume historial de conversación"""
        if not historial:
            return "Sin historial previo"
        
        recent = historial[-3:] if len(historial) > 3 else historial
        summary = "\n".join([
            f"- {item.get('role', 'user')}: {item.get('content', '')[:100]}..."
            for item in recent
        ])
        return summary
    
    def _extract_memory_hints(self, contexto: Dict) -> List[str]:
        """Extrae pistas para búsqueda en memoria"""
        hints = []
        if contexto.get("user_id"):
            hints.append(f"user:{contexto['user_id']}")
        if contexto.get("session_id"):
            hints.append(f"session:{contexto['session_id']}")
        if contexto.get("domain"):
            hints.append(f"domain:{contexto['domain']}")
        return hints
    
    async def enhance_with_external_info(self, objetivo: str) -> Dict[str, Any]:
        """Enriquece el análisis con información externa usando búsqueda"""
        try:
            # Búsqueda web para contexto adicional
            search_result = await self.call_tool(
                "search_engine",
                query=f"{objetivo} información técnica",
                operation="web_search",
                sources=["duckduckgo", "wikipedia"]
            )
            
            if search_result.get("success"):
                return {
                    "external_context": search_result.get("data", {}),
                    "enhanced": True
                }
        except Exception as e:
            self.logger.warning(f"Error obteniendo contexto externo: {e}")
        
        return {"enhanced": False}
    
    def _extract_constraints(self, contexto: Dict) -> Dict[str, Any]:
        """Extrae restricciones del contexto"""
        return {
            "max_time": contexto.get("max_time"),
            "max_cost": contexto.get("max_cost"),
            "required_quality": contexto.get("quality", 0.8),
            "language": contexto.get("language", "es")
        }
