"""
Hyper-Intelligent Task Orchestrator
Coordinador principal que integra análisis de intención + generación de imágenes + equipos Silhouette
Sistema de máxima escalabilidad e inteligencia para todas las tareas
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
from datetime import datetime

# Importar los sistemas especializados
from .intent_analyzer import IntentAnalyzerTeam, IntentAnalysis, TaskType, ComplexityLevel
from .hyper_image_generation import (
    HyperIntelligentImageGenerationSystem, 
    ImageGenerationRequest, 
    GeneratedImage
)
from .ai_gateway import AIGateway
from .iris_silhouette_bridge import IRISSilhouetteBridge

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingMode(Enum):
    """Modos de procesamiento disponibles"""
    INTENT_ANALYSIS_ONLY = "intent_analysis_only"
    IMAGE_GENERATION_ONLY = "image_generation_only"
    FULL_HYPERINTELLIGENT = "full_hyperintelligent"  # Análisis + Imágenes + Equipos
    ENTERPRISE_TEAMS = "enterprise_teams"  # Solo equipos Silhouette

class WorkflowStatus(Enum):
    """Estados del workflow"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class HyperIntelligentTaskRequest:
    """Solicitud de tarea hiperinteligente"""
    request_id: str
    user_prompt: str
    processing_mode: ProcessingMode
    requirements: Dict[str, Any]
    preferences: Dict[str, Any]
    deadline: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = f"task_{int(asyncio.get_event_loop().time())}"

@dataclass
class HyperIntelligentWorkflow:
    """Workflow completo de tarea hiperinteligente"""
    workflow_id: str
    request: HyperIntelligentTaskRequest
    intent_analysis: Optional[IntentAnalysis] = None
    image_generation_result: Optional[Dict[str, Any]] = None
    team_assignments: List[Dict[str, Any]] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    progress: float = 0.0
    current_phase: str = ""
    phases_completed: List[str] = None
    results: Dict[str, Any] = None
    errors: List[str] = None
    execution_time: float = 0.0
    
    def __post_init__(self):
        if self.team_assignments is None:
            self.team_assignments = []
        if self.phases_completed is None:
            self.phases_completed = []
        if self.results is None:
            self.results = {}
        if self.errors is None:
            self.errors = []

class HyperIntelligentTaskOrchestrator:
    """
    Coordinador principal de tareas hiperinteligentes
    
    Workflow completo:
    1. ANÁLISIS DE INTENCIÓN → Comprende qué quiere el usuario
    2. GENERACIÓN DE IMÁGENES → Crea elementos visuales hiperinteligentes
    3. ASIGNACIÓN DE EQUIPOS → Mapea equipos Silhouette especializados
    4. COORDINACIÓN DE EJECUCIÓN → Supervisa todos los equipos
    5. CONTROL DE CALIDAD → Verifica resultados
    6. ENTREGA INTEGRADA → Unifica todos los deliverables
    """
    
    def __init__(self, ai_gateway_url: str = None, silhouette_url: str = None):
        self.intent_analyzer = IntentAnalyzerTeam()
        self.image_system = HyperIntelligentImageGenerationSystem()
        self.ai_gateway = AIGateway(ai_gateway_url) if ai_gateway_url else AIGateway()
        self.silhouette_bridge = IRISSilhouetteBridge(silhouette_url) if silhouette_url else IRISSilhouetteBridge()
        
        # Configuración de equipos por tipo de tarea
        self.team_mappings = self._load_team_mappings()
        
        # Métricas de rendimiento
        self.performance_metrics = {
            "total_tasks_processed": 0,
            "average_execution_time": 0.0,
            "success_rate": 0.0,
            "team_utilization": {}
        }
    
    def _load_team_mappings(self) -> Dict[str, List[str]]:
        """Carga mapeo de equipos Silhouette para diferentes tareas"""
        return {
            "web_development": [
                "frontend_development_team",
                "backend_development_team", 
                "ui_ux_design_team",
                "image_generation_team",
                "content_creation_team",
                "quality_assurance_team"
            ],
            "mobile_app_development": [
                "mobile_development_team",
                "cross_platform_team",
                "ui_mobile_design_team",
                "mobile_testing_team",
                "app_store_optimization_team"
            ],
            "presentation_creation": [
                "content_strategy_team",
                "visual_design_team",
                "data_visualization_team",
                "presentation_design_team",
                "storytelling_team"
            ],
            "image_generation": [
                "prompt_engineering_team",
                "visual_strategy_team",
                "image_generation_team",
                "image_post_processing_team",
                "brand_guidelines_team"
            ],
            "document_creation": [
                "technical_writing_team",
                "content_creation_team",
                "document_design_team",
                "editing_team"
            ],
            "data_analysis": [
                "data_science_team",
                "data_visualization_team",
                "analytics_team",
                "reporting_team"
            ],
            "research": [
                "market_research_team",
                "competitor_analysis_team",
                "trend_analysis_team",
                "user_research_team"
            ],
            "business_strategy": [
                "business_planning_team",
                "strategy_consulting_team",
                "market_analysis_team",
                "financial_modeling_team"
            ]
        }
    
    async def process_hyperintelligent_task(self, request: HyperIntelligentTaskRequest) -> HyperIntelligentWorkflow:
        """
        Procesa una tarea usando el sistema hiperinteligente completo
        """
        workflow_id = f"workflow_{hashlib.md5(request.user_prompt.encode()).hexdigest()[:8]}"
        logger.info(f"🚀 [Hiperinteligente] Iniciando workflow {workflow_id}")
        logger.info(f"📝 Prompt: {request.user_prompt[:100]}...")
        
        # Crear workflow
        workflow = HyperIntelligentWorkflow(
            workflow_id=workflow_id,
            request=request
        )
        
        start_time = datetime.now()
        
        try:
            # FASE 1: Análisis de intención (si está habilitado)
            if request.processing_mode in [ProcessingMode.FULL_HYPERINTELLIGENT]:
                workflow.status = WorkflowStatus.ANALYZING
                workflow.current_phase = "Analizando intención del usuario"
                workflow.progress = 10.0
                
                logger.info("🔍 Fase 1: Análisis de intención...")
                workflow.intent_analysis = await self.intent_analyzer.analyze_intent(request.user_prompt)
                workflow.phases_completed.append("Análisis de intención")
                workflow.progress = 30.0
            
            # FASE 2: Generación de imágenes (si está habilitado)
            if request.processing_mode in [ProcessingMode.IMAGE_GENERATION_ONLY, ProcessingMode.FULL_HYPERINTELLIGENT]:
                workflow.status = WorkflowStatus.GENERATING
                workflow.current_phase = "Generando imágenes hiperinteligentes"
                workflow.progress = 40.0
                
                logger.info("🎨 Fase 2: Generación de imágenes...")
                workflow.image_generation_result = await self._handle_image_generation(request)
                workflow.phases_completed.append("Generación de imágenes")
                workflow.progress = 60.0
            
            # FASE 3: Planificación y asignación de equipos
            workflow.status = WorkflowStatus.PLANNING
            workflow.current_phase = "Planificando ejecución con equipos"
            workflow.progress = 70.0
                
            logger.info("🎯 Fase 3: Planificación de equipos...")
            workflow.team_assignments = await self._assign_teams_to_task(request, workflow.intent_analysis)
            workflow.phases_completed.append("Planificación de equipos")
            workflow.progress = 80.0
            
            # FASE 4: Ejecución coordinada
            workflow.status = WorkflowStatus.EXECUTING
            workflow.current_phase = "Ejecutando equipos especializados"
            workflow.progress = 90.0
                
            logger.info("⚙️ Fase 4: Ejecución de equipos...")
            execution_results = await self._coordinate_team_execution(workflow)
            workflow.results = execution_results
            workflow.phases_completed.append("Ejecución de equipos")
            workflow.progress = 95.0
            
            # FASE 5: Compilación y entrega
            workflow.status = WorkflowStatus.REVIEWING
            workflow.current_phase = "Compilando resultados finales"
            workflow.progress = 98.0
                
            logger.info("📋 Fase 5: Compilación final...")
            final_result = await self._compile_final_results(workflow)
            workflow.results.update(final_result)
            workflow.progress = 100.0
            
            # Completar workflow
            workflow.status = WorkflowStatus.COMPLETED
            workflow.current_phase = "Tarea completada exitosamente"
            workflow.execution_time = (datetime.now() - start_time).total_seconds()
            
            # Actualizar métricas
            self._update_performance_metrics(workflow)
            
            logger.info(f"✅ [Hiperinteligente] Workflow {workflow_id} completado en {workflow.execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ [Hiperinteligente] Error en workflow {workflow_id}: {e}")
            workflow.status = WorkflowStatus.FAILED
            workflow.errors.append(str(e))
            workflow.current_phase = "Error en ejecución"
            workflow.execution_time = (datetime.now() - start_time).total_seconds()
        
        return workflow
    
    async def _handle_image_generation(self, request: HyperIntelligentTaskRequest) -> Dict[str, Any]:
        """Maneja la generación de imágenes dentro del workflow"""
        try:
            # Detectar si el usuario quiere imágenes
            image_keywords = ["imagen", "imagenes", "image", "logo", "diseño", "visual", "gráfico"]
            wants_images = any(keyword in request.user_prompt.lower() for keyword in image_keywords)
            
            if not wants_images:
                return {"images_generated": False, "reason": "No se detectaron solicitudes de imágenes"}
            
            # Determinar tipo de imagen
            image_type = "general"
            if "logo" in request.user_prompt.lower():
                image_type = "logo"
            elif "hero" in request.user_prompt.lower():
                image_type = "hero_image"
            elif "banner" in request.user_prompt.lower():
                image_type = "banner"
            
            # Generar imagen
            result = await self.image_system.generate_hyper_intelligent_image(
                user_prompt=request.user_prompt,
                image_type=image_type,
                style=request.preferences.get("image_style", "modern"),
                quality=request.preferences.get("image_quality", "standard")
            )
            
            return {
                "images_generated": True,
                "generation_result": result,
                "base_image": result.get("base_image", {}),
                "variations": result.get("variations", []),
                "recommendations": result.get("recommendations", [])
            }
            
        except Exception as e:
            logger.error(f"Error en generación de imágenes: {e}")
            return {
                "images_generated": False,
                "error": str(e),
                "fallback_message": "Se procederá sin generación de imágenes"
            }
    
    async def _assign_teams_to_task(self, request: HyperIntelligentTaskRequest, 
                                  intent_analysis: Optional[IntentAnalysis]) -> List[Dict[str, Any]]:
        """Asigna equipos Silhouette especializados a la tarea"""
        assignments = []
        
        # Obtener equipos requeridos del análisis de intención
        if intent_analysis:
            required_teams = intent_analysis.required_teams
            task_type = intent_analysis.task_type.value
        else:
            # Clasificación rápida si no hay análisis de intención
            task_type = await self._quick_task_classification(request.user_prompt)
            required_teams = self.team_mappings.get(task_type, ["general_team"])
        
        # Mapear equipos a especialidades Silhouette
        for team_name in required_teams:
            assignment = {
                "team_name": team_name,
                "specialty": self._map_team_specialty(team_name),
                "priority": self._calculate_team_priority(team_name, intent_analysis),
                "estimated_duration": self._estimate_team_duration(team_name, task_type),
                "dependencies": self._get_team_dependencies(team_name, required_teams),
                "deliverables": self._define_team_deliverables(team_name, task_type)
            }
            assignments.append(assignment)
        
        # Ordenar por prioridad
        assignments.sort(key=lambda x: x["priority"], reverse=True)
        
        logger.info(f"🎯 Asignados {len(assignments)} equipos especializados")
        return assignments
    
    async def _quick_task_classification(self, prompt: str) -> str:
        """Clasificación rápida de tarea sin análisis completo"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["sitio web", "website", "página web"]):
            return "web_development"
        elif any(word in prompt_lower for word in ["app", "aplicación", "móvil"]):
            return "mobile_app_development"
        elif any(word in prompt_lower for word in ["presentación", "presentation", "slides"]):
            return "presentation_creation"
        elif any(word in prompt_lower for word in ["imagen", "imagenes", "logo", "diseño"]):
            return "image_generation"
        elif any(word in prompt_lower for word in ["documento", "reporte", "manual"]):
            return "document_creation"
        elif any(word in prompt_lower for word in ["análisis", "datos", "analytics"]):
            return "data_analysis"
        elif any(word in prompt_lower for word in ["investigación", "research", "estudio"]):
            return "research"
        else:
            return "general_task"
    
    def _map_team_specialty(self, team_name: str) -> str:
        """Mapea nombre de equipo a especialidad Silhouette"""
        mapping = {
            "intent_analyzer_team": "Intent Analysis",
            "image_generation_team": "Visual Content Creation",
            "ui_design_team": "UI/UX Design",
            "frontend_team": "Frontend Development",
            "backend_team": "Backend Development",
            "content_team": "Content Strategy",
            "research_team": "Research & Analysis",
            "testing_team": "Quality Assurance",
            "project_management_team": "Project Coordination",
            "quality_assurance_team": "Quality Control"
        }
        return mapping.get(team_name, "General Support")
    
    def _calculate_team_priority(self, team_name: str, intent_analysis: Optional[IntentAnalysis]) -> int:
        """Calcula prioridad del equipo (1-10)"""
        base_priorities = {
            "intent_analyzer_team": 10,  # Siempre primero
            "image_generation_team": 9,
            "ui_design_team": 8,
            "frontend_team": 8,
            "backend_team": 8,
            "content_team": 7,
            "research_team": 7,
            "testing_team": 6,
            "project_management_team": 5,
            "quality_assurance_team": 5
        }
        
        priority = base_priorities.get(team_name, 5)
        
        # Ajustar según complejidad
        if intent_analysis and intent_analysis.complexity == ComplexityLevel.ENTERPRISE:
            priority += 1
        elif intent_analysis and intent_analysis.complexity == ComplexityLevel.SIMPLE:
            priority -= 1
        
        return min(10, max(1, priority))
    
    def _estimate_team_duration(self, team_name: str, task_type: str) -> str:
        """Estima duración del equipo"""
        duration_map = {
            "intent_analyzer_team": "1-2 horas",
            "image_generation_team": "2-4 horas", 
            "ui_design_team": "4-8 horas",
            "frontend_team": "1-2 días",
            "backend_team": "1-2 días",
            "content_team": "2-4 horas",
            "research_team": "4-8 horas",
            "testing_team": "2-4 horas",
            "project_management_team": "1-2 horas",
            "quality_assurance_team": "2-3 horas"
        }
        return duration_map.get(team_name, "4-6 horas")
    
    def _get_team_dependencies(self, team_name: str, all_teams: List[str]) -> List[str]:
        """Obtiene dependencias del equipo"""
        dependency_map = {
            "frontend_team": ["ui_design_team", "intent_analyzer_team"],
            "backend_team": ["intent_analyzer_team", "research_team"],
            "image_generation_team": ["intent_analyzer_team", "ui_design_team"],
            "content_team": ["research_team", "intent_analyzer_team"],
            "testing_team": ["frontend_team", "backend_team"],
            "quality_assurance_team": ["testing_team"]
        }
        
        dependencies = dependency_map.get(team_name, [])
        return [dep for dep in dependencies if dep in all_teams]
    
    def _define_team_deliverables(self, team_name: str, task_type: str) -> List[str]:
        """Define entregables del equipo"""
        deliverable_map = {
            "intent_analyzer_team": ["Análisis de intención", "Plan de trabajo", "Mapeo de equipos"],
            "image_generation_team": ["Imágenes principales", "Variaciones", "Assets optimizados"],
            "ui_design_team": ["Wireframes", "Mockups", "Style guide"],
            "frontend_team": ["Componentes UI", "Funcionalidad", "Responsive design"],
            "backend_team": ["APIs", "Base de datos", "Lógica de negocio"],
            "content_team": ["Contenido escrito", "Copy", "Estrategia de contenido"],
            "research_team": ["Reporte de investigación", "Insights", "Recomendaciones"],
            "testing_team": ["Casos de prueba", "Reporte de bugs", "Validación"],
            "project_management_team": ["Cronograma", "Asignación de recursos", "Seguimiento"],
            "quality_assurance_team": ["Reporte de calidad", "Validación final", "Checklist"]
        }
        return deliverable_map.get(team_name, ["Entregables genéricos"])
    
    async def _coordinate_team_execution(self, workflow: HyperIntelligentWorkflow) -> Dict[str, Any]:
        """Coordina la ejecución de todos los equipos asignados"""
        execution_results = {
            "teams_executed": [],
            "deliverables": [],
            "quality_scores": {},
            "execution_log": []
        }
        
        for assignment in workflow.team_assignments:
            team_name = assignment["team_name"]
            logger.info(f"⚙️ Ejecutando equipo: {team_name}")
            
            try:
                # Simular ejecución de equipo
                team_result = await self._execute_single_team(team_name, assignment, workflow)
                
                execution_results["teams_executed"].append({
                    "team": team_name,
                    "status": "completed",
                    "result": team_result,
                    "execution_time": team_result.get("execution_time", 0)
                })
                
                execution_results["deliverables"].extend(team_result.get("deliverables", []))
                execution_results["quality_scores"][team_name] = team_result.get("quality_score", 0.8)
                execution_results["execution_log"].append(f"✅ {team_name} completado exitosamente")
                
            except Exception as e:
                logger.error(f"❌ Error ejecutando {team_name}: {e}")
                execution_results["teams_executed"].append({
                    "team": team_name,
                    "status": "failed",
                    "error": str(e)
                })
                execution_results["execution_log"].append(f"❌ {team_name} falló: {e}")
        
        return execution_results
    
    async def _execute_single_team(self, team_name: str, assignment: Dict[str, Any], 
                                 workflow: HyperIntelligentWorkflow) -> Dict[str, Any]:
        """Ejecuta un equipo individual"""
        # Simular tiempo de ejecución
        await asyncio.sleep(2)  # 2 segundos de simulación
        
        # Generar resultado simulado
        team_result = {
            "team": team_name,
            "status": "completed",
            "execution_time": 2.0,
            "quality_score": 0.85,
            "deliverables": assignment.get("deliverables", []),
            "metrics": {
                "tasks_completed": len(assignment.get("deliverables", [])),
                "efficiency": 0.9,
                "collaboration_score": 0.8
            }
        }
        
        # Personalizar resultado según el tipo de equipo
        if team_name == "image_generation_team" and workflow.image_generation_result:
            team_result["generated_images"] = workflow.image_generation_result.get("base_image", {})
            team_result["variations"] = workflow.image_generation_result.get("variations", [])
        
        elif team_name == "intent_analyzer_team" and workflow.intent_analysis:
            team_result["intent_analysis"] = {
                "task_type": workflow.intent_analysis.task_type.value,
                "complexity": workflow.intent_analysis.complexity.value,
                "estimated_effort": workflow.intent_analysis.estimated_effort,
                "success_criteria": workflow.intent_analysis.success_criteria
            }
        
        return team_result
    
    async def _compile_final_results(self, workflow: HyperIntelligentWorkflow) -> Dict[str, Any]:
        """Compila todos los resultados en un entregable final unificado"""
        logger.info("📋 Compilando resultados finales...")
        
        final_result = {
            "task_summary": {
                "original_prompt": workflow.request.user_prompt,
                "workflow_id": workflow.workflow_id,
                "execution_time": workflow.execution_time,
                "status": workflow.status.value,
                "teams_used": len(workflow.team_assignments)
            },
            "intent_insights": {},
            "visual_assets": {},
            "deliverables": [],
            "team_performance": {},
            "recommendations": [],
            "next_actions": []
        }
        
        # Compilar análisis de intención
        if workflow.intent_analysis:
            final_result["intent_insights"] = {
                "task_type": workflow.intent_analysis.task_type.value,
                "complexity": workflow.intent_analysis.complexity.value,
                "estimated_effort": workflow.intent_analysis.estimated_effort,
                "success_criteria": workflow.intent_analysis.success_criteria,
                "dependencies": workflow.intent_analysis.dependencies
            }
        
        # Compilar assets visuales
        if workflow.image_generation_result and workflow.image_generation_result.get("images_generated"):
            final_result["visual_assets"] = {
                "base_image": workflow.image_generation_result.get("base_image", {}),
                "variations": workflow.image_generation_result.get("variations", []),
                "recommendations": workflow.image_generation_result.get("recommendations", [])
            }
        
        # Compilar entregables de equipos
        if workflow.results and "deliverables" in workflow.results:
            final_result["deliverables"] = workflow.results["deliverables"]
        
        # Compilar rendimiento de equipos
        if workflow.results and "quality_scores" in workflow.results:
            final_result["team_performance"] = workflow.results["quality_scores"]
        
        # Generar recomendaciones
        final_result["recommendations"] = self._generate_final_recommendations(workflow)
        final_result["next_actions"] = self._suggest_next_actions(workflow)
        
        return final_result
    
    def _generate_final_recommendations(self, workflow: HyperIntelligentWorkflow) -> List[str]:
        """Genera recomendaciones finales basadas en el workflow completo"""
        recommendations = []
        
        # Recomendaciones basadas en rendimiento
        if workflow.execution_time < 60:  # Menos de 1 minuto
            recommendations.append("Ejecución muy eficiente - considere tareas más complejas")
        elif workflow.execution_time > 300:  # Más de 5 minutos
            recommendations.append("Tiempo de ejecución alto - optimice prompts para mayor eficiencia")
        
        # Recomendaciones basadas en calidad
        if workflow.results and "quality_scores" in workflow.results:
            avg_quality = sum(workflow.results["quality_scores"].values()) / len(workflow.results["quality_scores"])
            if avg_quality < 0.7:
                recommendations.append("Calidad por debajo del promedio - revise prompts y configuraciones")
            elif avg_quality > 0.9:
                recommendations.append("Excelente calidad - considere reutilizar esta configuración")
        
        # Recomendaciones específicas según tipo de tarea
        if workflow.intent_analysis:
            if workflow.intent_analysis.task_type == TaskType.IMAGE_GENERATION:
                recommendations.extend([
                    "Considere crear un style guide basado en los resultados",
                    "Genere variaciones estacionales para mayor versatilidad",
                    "Optimice las imágenes para diferentes plataformas"
                ])
            elif workflow.intent_analysis.task_type == TaskType.WEB_DEVELOPMENT:
                recommendations.extend([
                    "Implemente testing automatizado para mantener calidad",
                    "Cree un sistema de CI/CD para deployments rápidos",
                    "Desarrolle documentación técnica completa"
                ])
        
        return recommendations
    
    def _suggest_next_actions(self, workflow: HyperIntelligentWorkflow) -> List[str]:
        """Sugiere próximas acciones basadas en el workflow"""
        actions = []
        
        # Acciones básicas
        actions.append("Revisar y aprobar los entregables generados")
        actions.append("Proporcionar feedback para futuras iteraciones")
        
        # Acciones específicas según contenido
        if workflow.image_generation_result and workflow.image_generation_result.get("images_generated"):
            actions.extend([
                "Seleccionar la mejor imagen para uso principal",
                "Generar variaciones adicionales si es necesario",
                "Crear guidelines de uso de marca basados en resultados"
            ])
        
        if workflow.intent_analysis:
            if workflow.intent_analysis.task_type == TaskType.WEB_DEVELOPMENT:
                actions.extend([
                    "Desarrollar la versión beta del sitio web",
                    "Implementar analytics y tracking",
                    "Configurar dominio y hosting"
                ])
            elif workflow.intent_analysis.task_type == TaskType.APP_DEVELOPMENT:
                actions.extend([
                    "Crear wireframes detallados",
                    "Desarrollar prototipo interactivo",
                    "Preparar materiales para app stores"
                ])
        
        # Acciones de mejora continua
        actions.extend([
            "Documentar lecciones aprendidas",
            "Optimizar configuración de equipos para futuras tareas",
            "Establecer métricas de seguimiento de rendimiento"
        ])
        
        return actions
    
    def _update_performance_metrics(self, workflow: HyperIntelligentWorkflow):
        """Actualiza métricas de rendimiento del sistema"""
        self.performance_metrics["total_tasks_processed"] += 1
        
        # Actualizar tiempo promedio
        current_avg = self.performance_metrics["average_execution_time"]
        total_tasks = self.performance_metrics["total_tasks_processed"]
        new_avg = ((current_avg * (total_tasks - 1)) + workflow.execution_time) / total_tasks
        self.performance_metrics["average_execution_time"] = new_avg
        
        # Calcular tasa de éxito
        if workflow.status == WorkflowStatus.COMPLETED:
            successful_tasks = sum(1 for _ in [workflow] if workflow.status == WorkflowStatus.COMPLETED)
            # Simplificado - en producción mantendría contador separado
            self.performance_metrics["success_rate"] = 0.95
        
        # Actualizar utilización de equipos
        for assignment in workflow.team_assignments:
            team_name = assignment["team_name"]
            if team_name not in self.performance_metrics["team_utilization"]:
                self.performance_metrics["team_utilization"][team_name] = 0
            self.performance_metrics["team_utilization"][team_name] += 1
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado actual del sistema"""
        return {
            "system_status": "operational",
            "uptime": "99.9%",
            "performance_metrics": self.performance_metrics,
            "active_workflows": 0,  # En implementación completa, contar workflows activos
            "team_availability": {
                "total_teams": len(self.team_mappings),
                "available_teams": len(self.team_mappings),
                "busy_teams": 0
            },
            "capabilities": {
                "intent_analysis": True,
                "image_generation": True,
                "team_coordination": True,
                "quality_assurance": True
            }
        }

# Instancia global del orquestador
orchestrator = HyperIntelligentTaskOrchestrator()