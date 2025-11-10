"""
Orquestador Multi-Agente con LangGraph
Coordina los 5 agentes especializados con paralelización
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from ..models import (
    AgentMessage,
    AgentResponse,
    MessageIntent,
    MessageStatus,
    Budget
)
from ..agents import (
    ReasonerAgent,
    PlannerAgent,
    ExecutorAgent,
    VerifierAgent,
    MemoryManagerAgent
)
from ..core import settings


logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Orquestador Multi-Agente Superior
    
    Responsabilidades:
    - Coordinar 5 agentes especializados
    - Paralelización de 3-5 agentes simultáneos
    - Pattern fan-out/fan-in
    - Router LLM inteligente
    - Checkpoints y recuperación
    - Observabilidad completa
    """
    
    def __init__(
        self,
        llm_router: Optional[Any] = None,
        redis_client: Optional[Any] = None,
        vector_store: Optional[Any] = None
    ):
        self.llm_router = llm_router
        self.redis_client = redis_client
        self.vector_store = vector_store
        
        # Inicializar agentes
        self.reasoner = ReasonerAgent(llm_client=llm_router)
        self.planner = PlannerAgent(llm_client=llm_router)
        self.verifier = VerifierAgent(llm_client=llm_router)
        self.memory_manager = MemoryManagerAgent(
            llm_client=llm_router,
            vector_store=vector_store
        )
        
        # Pool de executors especializados
        self.executors = {
            "general": ExecutorAgent("general", llm_client=llm_router),
            "code": ExecutorAgent("code", llm_client=llm_router),
            "web": ExecutorAgent("web", llm_client=llm_router),
            "docs": ExecutorAgent("docs", llm_client=llm_router)
        }
        
        # Estado de sesiones activas
        self.active_sessions = {}
        
        logger.info("MultiAgentOrchestrator inicializado")
    
    async def process_request(
        self,
        objetivo: str,
        contexto: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesa una solicitud completa con orquestación multi-agente
        
        Args:
            objetivo: Objetivo a cumplir
            contexto: Contexto adicional opcional
            user_id: ID del usuario
            
        Returns:
            Dict con resultado final y metadatos
        """
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"Iniciando proceso: {conversation_id} - {objetivo[:100]}")
        
        try:
            # Fase 1: Razonamiento (Reasoner)
            reasoning_result = await self._phase_reasoning(
                objetivo,
                contexto or {},
                conversation_id
            )
            
            # Fase 2: Planificación (Planner)
            planning_result = await self._phase_planning(
                reasoning_result,
                conversation_id
            )
            
            # Fase 3: Ejecución Paralela (Executors fan-out)
            execution_results = await self._phase_execution(
                planning_result,
                conversation_id
            )
            
            # Fase 4: Verificación (Verifier)
            verification_result = await self._phase_verification(
                execution_results,
                planning_result,
                conversation_id
            )
            
            # Fase 5: Síntesis y Memoria (Memory Manager)
            final_result = await self._phase_synthesis(
                reasoning_result,
                planning_result,
                execution_results,
                verification_result,
                conversation_id
            )
            
            logger.info(f"Proceso completado: {conversation_id}")
            
            return {
                "conversation_id": conversation_id,
                "status": "completed",
                "result": final_result,
                "phases": {
                    "reasoning": reasoning_result,
                    "planning": planning_result,
                    "execution": execution_results,
                    "verification": verification_result
                },
                "metadata": {
                    "agents_used": self._count_agents_used(planning_result),
                    "total_time_ms": self._calculate_total_time(),
                    "quality_score": verification_result.get(
                        "quality_metrics", {}
                    ).get("overall_score", 0.0)
                }
            }
            
        except Exception as e:
            logger.exception(f"Error en orquestación: {conversation_id}")
            
            return {
                "conversation_id": conversation_id,
                "status": "error",
                "error": str(e),
                "partial_results": self.active_sessions.get(conversation_id, {})
            }
    
    async def _phase_reasoning(
        self,
        objetivo: str,
        contexto: Dict[str, Any],
        conversation_id: str
    ) -> Dict[str, Any]:
        """Fase 1: Análisis de intención con Reasoner"""
        
        logger.info(f"[{conversation_id}] Fase 1: Reasoning")
        
        message = AgentMessage(
            conversation_id=conversation_id,
            sender="orchestrator",
            recipients=["reasoner"],
            intent=MessageIntent.INFORMATION_REQUEST,
            payload={
                "objetivo": objetivo,
                "contexto": contexto,
                "historial": contexto.get("historial", [])
            }
        )
        
        response = await self.reasoner.execute_with_timeout(message)
        
        if response.status != MessageStatus.DONE:
            raise RuntimeError(f"Reasoner falló: {response.errors}")
        
        return response.result
    
    async def _phase_planning(
        self,
        reasoning_result: Dict[str, Any],
        conversation_id: str
    ) -> Dict[str, Any]:
        """Fase 2: Planificación con Planner"""
        
        logger.info(f"[{conversation_id}] Fase 2: Planning")
        
        message = AgentMessage(
            conversation_id=conversation_id,
            sender="orchestrator",
            recipients=["planner"],
            intent=MessageIntent.DELEGATION,
            payload={
                "strategy": reasoning_result.get("strategy", {}),
                "enriched_context": reasoning_result.get("enriched_context", {})
            }
        )
        
        response = await self.planner.execute_with_timeout(message)
        
        if response.status != MessageStatus.DONE:
            raise RuntimeError(f"Planner falló: {response.errors}")
        
        return response.result
    
    async def _phase_execution(
        self,
        planning_result: Dict[str, Any],
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Fase 3: Ejecución paralela con Executors (fan-out pattern)
        
        Implementa paralelización de 3-5 agentes según el plan
        """
        
        logger.info(f"[{conversation_id}] Fase 3: Execution (parallel)")
        
        delegations = planning_result.get("delegations", [])
        parallelizable_tasks = planning_result.get("parallelizable_tasks", [])
        
        if not delegations:
            logger.warning("No hay delegaciones para ejecutar")
            return {"executions": [], "note": "No hay tareas para ejecutar"}
        
        # Agrupar tareas: paralelas vs secuenciales
        parallel_tasks = [
            d for d in delegations
            if d.get("parallelizable", False) or d["task_id"] in parallelizable_tasks
        ]
        sequential_tasks = [
            d for d in delegations
            if not (d.get("parallelizable", False) or d["task_id"] in parallelizable_tasks)
        ]
        
        all_results = []
        
        # Ejecutar tareas paralelas (máximo 5 concurrentes)
        if parallel_tasks:
            logger.info(f"Ejecutando {len(parallel_tasks)} tareas en paralelo")
            
            # Limitar concurrencia
            max_concurrent = min(
                len(parallel_tasks),
                settings.MAX_CONCURRENT_AGENTS
            )
            parallel_tasks = parallel_tasks[:max_concurrent]
            
            # Fan-out: ejecutar en paralelo
            parallel_results = await self._execute_parallel_tasks(
                parallel_tasks,
                conversation_id
            )
            all_results.extend(parallel_results)
        
        # Ejecutar tareas secuenciales
        if sequential_tasks:
            logger.info(f"Ejecutando {len(sequential_tasks)} tareas secuencialmente")
            
            for task in sequential_tasks:
                result = await self._execute_single_task(task, conversation_id)
                all_results.append(result)
        
        return {
            "executions": all_results,
            "num_parallel": len(parallel_tasks),
            "num_sequential": len(sequential_tasks),
            "total_executions": len(all_results)
        }
    
    async def _execute_parallel_tasks(
        self,
        tasks: List[Dict[str, Any]],
        conversation_id: str
    ) -> List[Dict[str, Any]]:
        """Ejecuta múltiples tareas en paralelo"""
        
        # Crear tareas asíncronas
        async_tasks = [
            self._execute_single_task(task, conversation_id)
            for task in tasks
        ]
        
        # Ejecutar concurrentemente y recoger resultados
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Procesar excepciones
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Tarea {tasks[i]['task_id']} falló: {result}")
                processed_results.append({
                    "task_id": tasks[i]["task_id"],
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_single_task(
        self,
        delegation: Dict[str, Any],
        conversation_id: str
    ) -> Dict[str, Any]:
        """Ejecuta una tarea individual con el executor apropiado"""
        
        task_id = delegation.get("task_id", "unknown")
        logger.info(f"[{conversation_id}] Ejecutando tarea: {task_id}")
        
        # Seleccionar executor según herramientas
        executor = self._select_executor(delegation.get("tool_map", []))
        
        message = AgentMessage(
            conversation_id=conversation_id,
            sender="orchestrator",
            recipients=[executor.agent_id],
            intent=MessageIntent.DELEGATION,
            payload={"delegation": delegation},
            budget=Budget(**delegation.get("limites", {}))
        )
        
        response = await executor.execute_with_timeout(message)
        
        return {
            "task_id": task_id,
            "executor": executor.agent_id,
            "status": response.status.value,
            "result": response.result,
            "execution_time_ms": response.execution_time_ms,
            "errors": response.errors
        }
    
    def _select_executor(self, tool_map: List[str]) -> ExecutorAgent:
        """Selecciona el executor más apropiado según herramientas"""
        
        if "python_executor" in tool_map:
            return self.executors["code"]
        elif "web_scraper" in tool_map:
            return self.executors["web"]
        elif "document_processor" in tool_map:
            return self.executors["docs"]
        else:
            return self.executors["general"]
    
    async def _phase_verification(
        self,
        execution_results: Dict[str, Any],
        planning_result: Dict[str, Any],
        conversation_id: str
    ) -> Dict[str, Any]:
        """Fase 4: Verificación con Verifier"""
        
        logger.info(f"[{conversation_id}] Fase 4: Verification")
        
        # Construir trayectoria
        trajectory = []
        for exec_result in execution_results.get("executions", []):
            trajectory.append({
                "task_id": exec_result.get("task_id"),
                "status": exec_result.get("status"),
                "executor": exec_result.get("executor")
            })
        
        message = AgentMessage(
            conversation_id=conversation_id,
            sender="orchestrator",
            recipients=["verifier"],
            intent=MessageIntent.VALIDATION,
            payload={
                "validation_request": {
                    "criterios": ["precision", "completeness", "consistency"],
                    "thresholds": [0.8, 0.75, 0.85],
                    "eval_type": "llm_judge"
                },
                "results": execution_results,
                "trajectory": trajectory
            }
        )
        
        response = await self.verifier.execute_with_timeout(message)
        
        if response.status != MessageStatus.DONE:
            logger.warning(f"Verifier con errores: {response.errors}")
        
        return response.result or {}
    
    async def _phase_synthesis(
        self,
        reasoning_result: Dict[str, Any],
        planning_result: Dict[str, Any],
        execution_results: Dict[str, Any],
        verification_result: Dict[str, Any],
        conversation_id: str
    ) -> Dict[str, Any]:
        """Fase 5: Síntesis final y almacenamiento en memoria"""
        
        logger.info(f"[{conversation_id}] Fase 5: Synthesis")
        
        # Recopilar todos los resultados
        all_results = [
            {"phase": "reasoning", "data": reasoning_result},
            {"phase": "planning", "data": planning_result},
            {"phase": "execution", "data": execution_results},
            {"phase": "verification", "data": verification_result}
        ]
        
        # Solicitar síntesis al Memory Manager
        message = AgentMessage(
            conversation_id=conversation_id,
            sender="orchestrator",
            recipients=["memory_manager"],
            intent=MessageIntent.SYNTHESIS,
            payload={
                "operation": "synthesis",
                "inputs": all_results,
                "synthesis_type": "summary"
            }
        )
        
        response = await self.memory_manager.execute_with_timeout(message)
        
        synthesis = response.result or {}
        
        # Almacenar en memoria para futuras consultas
        await self._store_session_memory(
            conversation_id,
            synthesis,
            verification_result
        )
        
        return {
            "synthesis": synthesis.get("content", ""),
            "approved": verification_result.get("approved", False),
            "quality_score": verification_result.get(
                "quality_metrics", {}
            ).get("overall_score", 0.0),
            "recommendations": verification_result.get("recommendations", []),
            "conversation_id": conversation_id
        }
    
    async def _store_session_memory(
        self,
        conversation_id: str,
        synthesis: Dict[str, Any],
        verification_result: Dict[str, Any]
    ):
        """Almacena la sesión en memoria para futuras referencias"""
        
        memory_content = {
            "conversation_id": conversation_id,
            "synthesis": synthesis.get("content", ""),
            "quality_score": verification_result.get(
                "quality_metrics", {}
            ).get("overall_score", 0.0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        message = AgentMessage(
            conversation_id=conversation_id,
            sender="orchestrator",
            recipients=["memory_manager"],
            intent=MessageIntent.INFORMATION_REQUEST,
            payload={
                "operation": "store",
                "content": memory_content,
                "metadata": {
                    "type": "session_summary",
                    "conversation_id": conversation_id
                },
                "memory_type": "session"
            }
        )
        
        await self.memory_manager.execute_with_timeout(message)
    
    def _count_agents_used(self, planning_result: Dict[str, Any]) -> int:
        """Cuenta cuántos agentes se usaron"""
        delegations = planning_result.get("delegations", [])
        return len(delegations) + 3  # +3 por Reasoner, Planner, Verifier
    
    def _calculate_total_time(self) -> float:
        """Calcula tiempo total aproximado"""
        # Mock - en producción usar timestamps reales
        return 0.0
