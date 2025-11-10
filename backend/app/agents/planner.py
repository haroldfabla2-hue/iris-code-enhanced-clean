"""
Agente Planner - Crea plan de pasos ejecutables
Responsable de descomponer tareas y definir herramientas
"""
from typing import List, Dict, Any
import uuid

from .base import BaseAgent
from ..models import AgentMessage, AgentResponse, MessageStatus, TaskDelegation, Budget


class PlannerAgent(BaseAgent):
    """
    Agente Planner: Descompone tareas en subtareas ejecutables
    
    Responsabilidades:
    - Crear plan de pasos (fan-out/fan-in)
    - Definir tool calls necesarias
    - Establecer criterios de terminación
    - Gestionar dependencias entre subtareas
    """
    
    def __init__(self, llm_client: Any = None):
        super().__init__(
            agent_id="planner",
            llm_client=llm_client
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "task_decomposition",
            "tool_selection",
            "dependency_management",
            "plan_optimization"
        ]
    
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """
        Procesa mensaje creando un plan de ejecución
        """
        self.log_trace("planner_start", {
            "message_id": message.message_id
        })
        
        try:
            # Extraer estrategia del Reasoner
            strategy = message.payload.get("strategy", {})
            enriched_context = message.payload.get("enriched_context", {})
            objetivo = enriched_context.get("objetivo", "")
            
            # Crear plan de subtareas
            plan = await self._create_plan(objetivo, strategy, enriched_context)
            
            # Optimizar orden de ejecución
            optimized_plan = self._optimize_execution_order(plan)
            
            # Definir tool map para cada subtarea
            tool_assignments = self._assign_tools(optimized_plan, strategy)
            
            # Crear delegaciones para executors
            delegations = self._create_delegations(
                optimized_plan,
                tool_assignments,
                strategy
            )
            
            result = {
                "plan": optimized_plan,
                "tool_assignments": tool_assignments,
                "delegations": delegations,
                "execution_graph": self._build_execution_graph(optimized_plan),
                "estimated_time": self._estimate_execution_time(optimized_plan),
                "parallelizable_tasks": self._identify_parallel_tasks(optimized_plan)
            }
            
            self.log_trace("planner_complete", {
                "message_id": message.message_id,
                "num_subtasks": len(optimized_plan["subtasks"]),
                "parallelizable": len(result["parallelizable_tasks"])
            })
            
            return AgentResponse(
                message_id=f"resp_{message.message_id}",
                original_message_id=message.message_id,
                agent_id=self.agent_id,
                status=MessageStatus.DONE,
                result=result
            )
            
        except Exception as e:
            self.logger.exception("Error en Planner")
            raise
    
    async def _create_plan(
        self,
        objetivo: str,
        strategy: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crea plan inicial de subtareas"""
        
        prompt = f"""Descompón la siguiente tarea en subtareas ejecutables:

Objetivo: {objetivo}
Estrategia: {strategy.get('approach', 'sequential')}
Agentes disponibles: {strategy.get('agents_needed', 1)}
Herramientas: {', '.join(strategy.get('tools', []))}

Proporciona un plan estructurado con:
1. Subtareas claras y accionables
2. Dependencias entre tareas
3. Criterios de éxito por subtarea
4. Herramientas necesarias
"""
        
        # Usar modelo específico para planificación con herramientas
        try:
            llm_response = await self.call_llm(
                prompt, 
                temperature=0.4, 
                max_tokens=2000,
                model=strategy.get("planning_model", "llama70b")
            )
        except Exception as e:
            self.logger.warning(f"Error LLM en planificación: {e}")
            llm_response = f"Plan generado automáticamente para: {objetivo[:100]}"
        
        # Generar subtareas basadas en estrategia
        subtasks = await self._generate_subtasks_with_tools(objetivo, strategy, llm_response)
        
        return {
            "plan_id": f"plan_{uuid.uuid4().hex[:12]}",
            "objetivo": objetivo,
            "approach": strategy.get("approach", "sequential"),
            "subtasks": subtasks,
            "llm_suggestions": llm_response
        }
    
    async def _generate_subtasks_with_tools(
        self,
        objetivo: str,
        strategy: Dict[str, Any],
        llm_suggestions: str
    ) -> List[Dict[str, Any]]:
        """Genera lista de subtareas con asignación inteligente de herramientas"""
        
        agents_needed = strategy.get("agents_needed", 1)
        approach = strategy.get("approach", "sequential")
        available_tools = strategy.get("tools", [])
        task_type = strategy.get("task_type", "general")
        
        subtasks = []
        
        # Tarea de preparación mejorada
        prep_tools = await self._select_preparation_tools(task_type, available_tools)
        subtasks.append({
            "task_id": f"task_{uuid.uuid4().hex[:8]}",
            "name": "Preparación de contexto",
            "description": "Validar requisitos y preparar entorno",
            "type": "preparation",
            "dependencies": [],
            "tools": prep_tools,
            "priority": 1,
            "estimated_time": 10
        })
        
        # Generar tareas específicas según el tipo
        execution_tasks = await self._generate_execution_tasks(
            objetivo, task_type, available_tools, agents_needed, approach
        )
        subtasks.extend(execution_tasks)
        
        # Síntesis final con herramientas de análisis
        synthesis_tools = self._select_synthesis_tools(task_type, available_tools)
        last_exploration_tasks = [
            t["task_id"] for t in subtasks if t["type"] in ["exploration", "execution"]
        ]
        subtasks.append({
            "task_id": f"task_{uuid.uuid4().hex[:8]}",
            "name": "Síntesis de resultados",
            "description": "Consolidar resultados y generar respuesta final",
            "type": "synthesis",
            "dependencies": last_exploration_tasks,
            "tools": synthesis_tools,
            "priority": 99,
            "estimated_time": 20
        })
        
        return subtasks
    
    async def _select_preparation_tools(self, task_type: str, available_tools: List[str]) -> List[str]:
        """Selecciona herramientas apropiadas para preparación"""
        prep_tools = []
        
        if "search_engine" in available_tools:
            prep_tools.append("search_engine")
        
        if task_type in ["coding", "analysis"] and "python_executor" in available_tools:
            prep_tools.append("python_executor")
        
        return prep_tools
    
    async def _generate_execution_tasks(
        self,
        objetivo: str,
        task_type: str,
        available_tools: List[str],
        agents_needed: int,
        approach: str
    ) -> List[Dict[str, Any]]:
        """Genera tareas de ejecución específicas por tipo"""
        tasks = []
        
        if approach == "breadth_first":
            # Tareas paralelas de exploración
            for i in range(min(agents_needed, len(available_tools))):
                tool = available_tools[i % len(available_tools)]
                task_desc = self._get_task_description(task_type, i+1, tool)
                
                tasks.append({
                    "task_id": f"task_{uuid.uuid4().hex[:8]}",
                    "name": f"Exploración {i+1}: {tool}",
                    "description": task_desc,
                    "type": "exploration",
                    "dependencies": [],
                    "tools": [tool],
                    "priority": 2,
                    "estimated_time": 60,
                    "parallelizable": True
                })
        else:
            # Tareas secuenciales
            prev_task_id = None
            for i in range(agents_needed):
                tool_idx = i % len(available_tools)
                tool = available_tools[tool_idx]
                task_id = f"task_{uuid.uuid4().hex[:8]}"
                
                task_desc = self._get_task_description(task_type, i+1, tool)
                dependencies = [prev_task_id] if prev_task_id else []
                
                tasks.append({
                    "task_id": task_id,
                    "name": f"Paso {i+1}: {tool}",
                    "description": task_desc,
                    "type": "execution",
                    "dependencies": dependencies,
                    "tools": [tool],
                    "priority": 2 + i,
                    "estimated_time": 45
                })
                prev_task_id = task_id
        
        return tasks
    
    def _get_task_description(self, task_type: str, step: int, tool: str) -> str:
        """Genera descripción de tarea basada en tipo y herramienta"""
        descriptions = {
            "coding": {
                "python_executor": f"Desarrollar código Python para el paso {step}",
                "file_processor": f"Procesar archivos de código en el paso {step}"
            },
            "research": {
                "search_engine": f"Buscar información relevante paso {step}",
                "web_scraper": f"Extraer datos web paso {step}"
            },
            "analysis": {
                "python_executor": f"Análisis de datos paso {step}",
                "search_engine": f"Investigación para análisis paso {step}"
            },
            "web_interaction": {
                "web_scraper": f"Interacción web paso {step}",
                "search_engine": f"Búsqueda web paso {step}"
            }
        }
        
        return descriptions.get(task_type, {}).get(tool, f"Ejecutar {tool} en paso {step}")
    
    def _select_synthesis_tools(self, task_type: str, available_tools: List[str]) -> List[str]:
        """Selecciona herramientas para síntesis final"""
        synthesis_tools = []
        
        if "python_executor" in available_tools:
            synthesis_tools.append("python_executor")
        
        if task_type == "research" and "search_engine" in available_tools:
            synthesis_tools.append("search_engine")
        
        return synthesis_tools

    def _generate_subtasks(
        self,
        objetivo: str,
        strategy: Dict[str, Any],
        llm_suggestions: str
    ) -> List[Dict[str, Any]]:
        """Genera lista de subtareas"""
        
        agents_needed = strategy.get("agents_needed", 1)
        approach = strategy.get("approach", "sequential")
        
        subtasks = []
        
        # Siempre: preparación inicial
        subtasks.append({
            "task_id": f"task_{uuid.uuid4().hex[:8]}",
            "name": "Preparación de contexto",
            "description": "Validar requisitos y preparar entorno",
            "type": "preparation",
            "dependencies": [],
            "tools": [],
            "priority": 1,
            "estimated_time": 10
        })
        
        # Según complejidad
        if approach == "breadth_first":
            # Tareas paralelas de exploración
            for i in range(min(agents_needed, 5)):
                subtasks.append({
                    "task_id": f"task_{uuid.uuid4().hex[:8]}",
                    "name": f"Exploración {i+1}",
                    "description": f"Investigar aspecto {i+1} del objetivo",
                    "type": "exploration",
                    "dependencies": ["task_" + subtasks[0]["task_id"].split('_')[1]],
                    "tools": strategy.get("tools", []),
                    "priority": 2,
                    "estimated_time": 60,
                    "parallelizable": True
                })
        else:
            # Tareas secuenciales
            prev_task_id = subtasks[0]["task_id"]
            for i in range(agents_needed):
                task_id = f"task_{uuid.uuid4().hex[:8]}"
                subtasks.append({
                    "task_id": task_id,
                    "name": f"Paso {i+1}",
                    "description": f"Ejecutar paso {i+1} del plan",
                    "type": "execution",
                    "dependencies": [prev_task_id],
                    "tools": strategy.get("tools", []),
                    "priority": 2 + i,
                    "estimated_time": 45
                })
                prev_task_id = task_id
        
        # Siempre: síntesis final
        last_exploration_tasks = [
            t["task_id"] for t in subtasks if t["type"] in ["exploration", "execution"]
        ]
        subtasks.append({
            "task_id": f"task_{uuid.uuid4().hex[:8]}",
            "name": "Síntesis de resultados",
            "description": "Consolidar resultados y generar respuesta final",
            "type": "synthesis",
            "dependencies": last_exploration_tasks,
            "tools": [],
            "priority": 99,
            "estimated_time": 20
        })
        
        return subtasks
    
    def _optimize_execution_order(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza orden de ejecución considerando dependencias"""
        
        subtasks = plan["subtasks"]
        
        # Ordenar por prioridad y dependencias
        sorted_tasks = sorted(subtasks, key=lambda x: x["priority"])
        
        plan["subtasks"] = sorted_tasks
        plan["execution_order"] = [t["task_id"] for t in sorted_tasks]
        
        return plan
    
    def _assign_tools(
        self,
        plan: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Asigna herramientas específicas a cada subtarea"""
        
        tool_assignments = {}
        available_tools = strategy.get("tools", [])
        
        for subtask in plan["subtasks"]:
            task_id = subtask["task_id"]
            task_type = subtask["type"]
            
            # Asignar herramientas específicas según tipo de tarea
            if task_type == "preparation":
                tool_assignments[task_id] = subtask.get("tools", [])
            elif task_type == "exploration":
                # Herramientas específicas para exploración
                tools = subtask.get("tools", available_tools[:1])
                tool_assignments[task_id] = tools
            elif task_type == "execution":
                # Herramientas de ejecución directa
                tools = subtask.get("tools", available_tools[:2])
                tool_assignments[task_id] = tools
            elif task_type == "synthesis":
                # Herramientas para síntesis y análisis final
                tools = subtask.get("tools", ["python_executor"])
                tool_assignments[task_id] = tools
            else:
                tool_assignments[task_id] = []
        
        return tool_assignments
    
    def _create_delegations(
        self,
        plan: Dict[str, Any],
        tool_assignments: Dict[str, List[str]],
        strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Crea delegaciones para executors"""
        
        delegations = []
        budget_config = strategy.get("budget", {})
        
        for subtask in plan["subtasks"]:
            if subtask["type"] in ["exploration", "execution"]:
                delegation = {
                    "task_id": subtask["task_id"],
                    "objetivo": subtask["description"],
                    "tool_map": tool_assignments.get(subtask["task_id"], []),
                    "limites": {
                        "tokens": budget_config.get("tokens_per_agent", 4000),
                        "time_seconds": budget_config.get("time_seconds", 120),
                        "tools_max": 3
                    },
                    "criterio_exito": f"Completar: {subtask['name']}",
                    "dependencies": subtask["dependencies"],
                    "parallelizable": subtask.get("parallelizable", False)
                }
                delegations.append(delegation)
        
        return delegations
    
    def _build_execution_graph(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Construye grafo de ejecución"""
        
        nodes = {}
        edges = []
        
        for subtask in plan["subtasks"]:
            task_id = subtask["task_id"]
            nodes[task_id] = {
                "name": subtask["name"],
                "type": subtask["type"],
                "priority": subtask["priority"]
            }
            
            for dep in subtask["dependencies"]:
                edges.append({"from": dep, "to": task_id})
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def _estimate_execution_time(self, plan: Dict[str, Any]) -> int:
        """Estima tiempo total de ejecución en segundos"""
        
        # Si hay tareas paralelas, calcular el camino crítico
        max_parallel_time = 0
        sequential_time = 0
        
        for subtask in plan["subtasks"]:
            if subtask.get("parallelizable", False):
                max_parallel_time = max(
                    max_parallel_time,
                    subtask.get("estimated_time", 60)
                )
            else:
                sequential_time += subtask.get("estimated_time", 60)
        
        return sequential_time + max_parallel_time
    
    def _identify_parallel_tasks(self, plan: Dict[str, Any]) -> List[str]:
        """Identifica qué tareas pueden ejecutarse en paralelo"""
        
        parallel_tasks = [
            subtask["task_id"]
            for subtask in plan["subtasks"]
            if subtask.get("parallelizable", False)
        ]
        
        return parallel_tasks
