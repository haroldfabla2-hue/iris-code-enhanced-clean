"""
Intent Analyzer Team - Núcleo Hiperinteligente de Análisis de Intenciones
Sistema que analiza, comprende y descompone intenciones del usuario en tareas específicas
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Tipos de tareas que puede identificar el analizador"""
    WEB_DEVELOPMENT = "web_development"
    APP_DEVELOPMENT = "app_development" 
    PRESENTATION_CREATION = "presentation_creation"
    IMAGE_GENERATION = "image_generation"
    DOCUMENT_CREATION = "document_creation"
    DATA_ANALYSIS = "data_analysis"
    RESEARCH = "research"
    DESIGN = "design"
    PROGRAMMING = "programming"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    BUSINESS_STRATEGY = "business_strategy"
    MULTIMEDIA = "multimedia"

class ComplexityLevel(Enum):
    """Niveles de complejidad de la tarea"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"

class IntentStage(Enum):
    """Etapas del proceso de análisis de intención"""
    PARSING = "parsing"
    UNDERSTANDING = "understanding"
    DECOMPOSITION = "decomposition"
    PLANNING = "planning"
    TEAM_ROUTING = "team_routing"

@dataclass
class IntentAnalysis:
    """Análisis completo de la intención del usuario"""
    original_prompt: str
    primary_intent: str
    task_type: TaskType
    complexity: ComplexityLevel
    required_teams: List[str]
    sub_tasks: List[Dict[str, Any]]
    context: Dict[str, Any]
    estimated_effort: str
    success_criteria: List[str]
    dependencies: List[str]

@dataclass
class TeamRequirement:
    """Requerimientos específicos de un equipo"""
    team_name: str
    specialty: str
    priority: int  # 1-10, siendo 10 la máxima prioridad
    capabilities_needed: List[str]
    estimated_time: str
    dependencies: List[str]

class IntentAnalyzerTeam:
    """
    Equipo hiperinteligente de análisis de intenciones
    
    Proceso:
    1. ANÁLISIS LINGUÍSTICO → Comprende el lenguaje natural
    2. CLASIFICACIÓN DE TAREA → Identifica tipo de tarea
    3. DESCOMPOSICIÓN → Divide en subtareas específicas
    4. MAPEO DE EQUIPOS → Asigna equipos Silhouette especializados
    5. PLANIFICACIÓN → Crea plan de ejecución completo
    6. VALIDACIÓN → Verifica viabilidad y dependencias
    """
    
    def __init__(self, ai_gateway_url: str = None):
        self.ai_gateway_url = ai_gateway_url or "http://ai-gateway:8002"
        self.task_patterns = self._load_task_patterns()
        self.team_mappings = self._load_team_mappings()
        self.complexity_indicators = self._load_complexity_indicators()
        
    def _load_task_patterns(self) -> Dict[TaskType, List[str]]:
        """Carga patrones de reconocimiento de tareas"""
        return {
            TaskType.WEB_DEVELOPMENT: [
                r"site web|web page|website|landing page|ecommerce|blog",
                r"desarrollar.*web|crear.*sitio|construir.*página",
                r"frontend|backend|fullstack|react|vue|angular"
            ],
            TaskType.APP_DEVELOPMENT: [
                r"app.*móvil|aplicación.*móvil|android|ios",
                r"desarrollar.*app|crear.*aplicación|build.*app",
                r"mobile app|native app|cross-platform"
            ],
            TaskType.PRESENTATION_CREATION: [
                r"presentación|slides|powerpoint|keynote",
                r"crear.*presentación|hacer.*slides|desarrollar.*demo",
                r"pitch deck|business plan|proposal"
            ],
            TaskType.IMAGE_GENERATION: [
                r"imagen|imagenes|generar.*imagen|crear.*imagen",
                r"logo|diseño.*gráfico|banner|poster",
                r"imagen.*para.*sitio|imagen.*para.*app",
                r"visual|artwork|graphics|photos"
            ],
            TaskType.DOCUMENT_CREATION: [
                r"documento|reporte|manual|guía",
                r"crear.*documento|escribir.*reporte",
                r"pdf|doc|write|documentation"
            ],
            TaskType.DATA_ANALYSIS: [
                r"análisis.*datos|data.*analysis|analytics",
                r"gráfico|chart|visualization|reporte.*datos",
                r"estadística|métrica|kpi|dashboard"
            ],
            TaskType.RESEARCH: [
                r"investigación|research|study|análisis.*mercado",
                r"estudiar|investigar|analizar.*competencia",
                r"mercado|competencia|trend|oportunidad"
            ],
            TaskType.DESIGN: [
                r"diseño|design|ui|ux|interfaz",
                r"prototipo|wireframe|mockup|design.*system",
                r"crear.*diseño|diseñar|diseñar.*interfaz"
            ],
            TaskType.PROGRAMMING: [
                r"código|code|programming|desarrollo",
                r"script|automation|backend|api",
                r"desarrollar.*sistema|escribir.*código"
            ],
            TaskType.BUSINESS_STRATEGY: [
                r"estrategia|strategy|plan.*negocio|business plan",
                r"modelo.*negocio|monetización|revenue",
                r"startup|empresa|company|organization"
            ]
        }
    
    def _load_team_mappings(self) -> Dict[TaskType, List[TeamRequirement]]:
        """Carga mapeo de equipos Silhouette para cada tipo de tarea"""
        return {
            TaskType.WEB_DEVELOPMENT: [
                TeamRequirement("frontend_team", "Web Development", 10, 
                              ["React", "Vue", "TypeScript", "CSS"], "2-3 días", []),
                TeamRequirement("backend_team", "Backend Development", 9,
                              ["Node.js", "Python", "APIs", "Database"], "2-3 días", []),
                TeamRequirement("ui_design_team", "UI/UX Design", 8,
                              ["Figma", "Prototyping", "Design Systems"], "1-2 días", []),
                TeamRequirement("content_team", "Content Creation", 7,
                              ["Copywriting", "SEO", "Content Strategy"], "1-2 días", []),
                TeamRequirement("image_generation_team", "Image Generation", 8,
                              ["Logo Design", "Icons", "Hero Images"], "1 día", [])
            ],
            TaskType.APP_DEVELOPMENT: [
                TeamRequirement("mobile_dev_team", "Mobile Development", 10,
                              ["React Native", "Flutter", "iOS", "Android"], "3-4 días", []),
                TeamRequirement("ui_design_team", "UI/UX Design", 9,
                              ["Mobile UI", "Responsive Design", "Prototyping"], "2-3 días", []),
                TeamRequirement("backend_team", "Backend Development", 9,
                              ["APIs", "Database", "Cloud Services"], "2-3 días", []),
                TeamRequirement("image_generation_team", "Image Generation", 7,
                              ["App Icons", "Splash Screens", "Assets"], "1 día", []),
                TeamRequirement("testing_team", "Quality Assurance", 8,
                              ["Unit Testing", "Integration Testing"], "1-2 días", [])
            ],
            TaskType.PRESENTATION_CREATION: [
                TeamRequirement("content_team", "Content Strategy", 10,
                              ["Copywriting", "Structure", "Narrative"], "1-2 días", []),
                TeamRequirement("design_team", "Visual Design", 9,
                              ["Slides Design", "Charts", "Infographics"], "1-2 días", []),
                TeamRequirement("image_generation_team", "Image Generation", 8,
                              ["Hero Images", "Illustrations", "Icons"], "1 día", []),
                TeamRequirement("data_viz_team", "Data Visualization", 7,
                              ["Charts", "Graphs", "Metrics"], "1 día", [])
            ],
            TaskType.IMAGE_GENERATION: [
                TeamRequirement("prompt_engineering_team", "Prompt Engineering", 10,
                              ["AI Prompts", "Style Guidelines", "Quality Control"], "2-3 horas", []),
                TeamRequirement("visual_strategy_team", "Visual Strategy", 9,
                              ["Brand Guidelines", "Color Schemes", "Layout"], "2-3 horas", []),
                TeamRequirement("image_generation_team", "Image Generation", 10,
                              ["DALL-E", "Midjourney", "Stable Diffusion"], "1-2 horas", []),
                TeamRequirement("image_post_processing_team", "Image Post-Processing", 8,
                              ["Photo Editing", "Retouching", "Optimization"], "1 hora", [])
            ],
            TaskType.BUSINESS_STRATEGY: [
                TeamRequirement("market_research_team", "Market Research", 10,
                              ["Market Analysis", "Competitor Analysis"], "2-3 días", []),
                TeamRequirement("business_planning_team", "Business Planning", 9,
                              ["Business Models", "Financial Projections"], "2-3 días", []),
                TeamRequirement("data_analysis_team", "Data Analysis", 8,
                              ["Analytics", "Metrics", "Dashboards"], "1-2 días", []),
                TeamRequirement("presentation_team", "Presentation Design", 7,
                              ["Pitch Decks", "Executive Summaries"], "1-2 días", [])
            ]
        }
    
    def _load_complexity_indicators(self) -> Dict[ComplexityLevel, List[str]]:
        """Carga indicadores de complejidad de tareas"""
        return {
            ComplexityLevel.SIMPLE: [
                "crear una", "hacer un", "simple", "básico", "quick",
                "rápido", "fácil", "una sola", "un solo"
            ],
            ComplexityLevel.MODERATE: [
                "desarrollar", "crear", "construir", "diseñar", "generar",
                "implementar", "desarrollar", "múltiple", "varios"
            ],
            ComplexityLevel.COMPLEX: [
                "sistema completo", "plataforma", "ecosistema", "suite",
                "multiples", "complejo", "avanzado", "integración"
            ],
            ComplexityLevel.ENTERPRISE: [
                "enterprise", "corporativo", "a gran escala", "millones",
                "multinacional", "complejidad alta", "arquitectura", "micro-servicios"
            ]
        }
    
    async def analyze_intent(self, user_prompt: str) -> IntentAnalysis:
        """
        Analiza la intención del usuario y devuelve un análisis completo
        
        Args:
            user_prompt: Prompt natural del usuario
            
        Returns:
            IntentAnalysis: Análisis completo de la intención
        """
        logger.info(f"🔍 Iniciando análisis de intención: {user_prompt[:100]}...")
        
        # Etapa 1: Análisis linguístico y clasificación
        task_type = await self._classify_task_type(user_prompt)
        complexity = await self._assess_complexity(user_prompt)
        
        # Etapa 2: Comprensión contextual
        primary_intent = await self._extract_primary_intent(user_prompt)
        context = await self._extract_context(user_prompt)
        
        # Etapa 3: Descomposición en subtareas
        sub_tasks = await self._decompose_into_subtasks(user_prompt, task_type)
        
        # Etapa 4: Mapeo de equipos requeridos
        required_teams = self._map_teams_to_task(task_type, complexity)
        
        # Etapa 5: Planificación y estimación
        estimated_effort = self._estimate_effort(complexity, len(sub_tasks))
        success_criteria = self._define_success_criteria(task_type, user_prompt)
        dependencies = self._identify_dependencies(sub_tasks)
        
        analysis = IntentAnalysis(
            original_prompt=user_prompt,
            primary_intent=primary_intent,
            task_type=task_type,
            complexity=complexity,
            required_teams=required_teams,
            sub_tasks=sub_tasks,
            context=context,
            estimated_effort=estimated_effort,
            success_criteria=success_criteria,
            dependencies=dependencies
        )
        
        logger.info(f"✅ Análisis completado - Tarea: {task_type.value}, Complejidad: {complexity.value}")
        return analysis
    
    async def _classify_task_type(self, prompt: str) -> TaskType:
        """Clasifica el tipo de tarea basándose en patrones linguísticos"""
        prompt_lower = prompt.lower()
        
        for task_type, patterns in self.task_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    logger.info(f"📋 Tarea clasificada como: {task_type.value}")
                    return task_type
        
        # Si no se encuentra patrón específico, usar análisis de IA
        return await self._classify_with_ai(prompt)
    
    async def _classify_with_ai(self, prompt: str) -> TaskType:
        """Clasifica tarea usando IA cuando no hay patrones exactos"""
        try:
            # Aquí se integraría con el AI Gateway para clasificación
            # Por ahora, clasificación heurística
            if any(word in prompt.lower() for word in ["crear", "desarrollar", "hacer"]):
                if "web" in prompt.lower() or "sitio" in prompt.lower():
                    return TaskType.WEB_DEVELOPMENT
                elif "app" in prompt.lower() or "aplicación" in prompt.lower():
                    return TaskType.APP_DEVELOPMENT
                elif "presentación" in prompt.lower():
                    return TaskType.PRESENTATION_CREATION
                else:
                    return TaskType.DOCUMENT_CREATION
            else:
                return TaskType.RESEARCH
        except Exception as e:
            logger.error(f"Error en clasificación IA: {e}")
            return TaskType.RESEARCH
    
    async def _assess_complexity(self, prompt: str) -> ComplexityLevel:
        """Evalúa la complejidad de la tarea"""
        prompt_lower = prompt.lower()
        
        # Contar indicadores de cada nivel
        complexity_scores = {}
        for level, indicators in self.complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in prompt_lower)
            complexity_scores[level] = score
        
        # Determinar nivel de complejidad
        max_score = max(complexity_scores.values())
        if max_score == 0:
            return ComplexityLevel.MODERATE
        
        for level, score in complexity_scores.items():
            if score == max_score:
                return level
        
        return ComplexityLevel.MODERATE
    
    async def _extract_primary_intent(self, prompt: str) -> str:
        """Extrae la intención principal del prompt"""
        # Lógica simplificada - en implementación completa usaría NLP
        if len(prompt) > 100:
            return prompt[:100] + "..."
        return prompt
    
    async def _extract_context(self, prompt: str) -> Dict[str, Any]:
        """Extrae contexto adicional del prompt"""
        context = {
            "language": "es" if any(word in prompt.lower() for word in ["crear", "desarrollar", "hacer"]) else "en",
            "urgency": "alta" if "urgente" in prompt.lower() or "rápido" in prompt.lower() else "normal",
            "audience": "general",
            "industry": "general",
            "requirements": []
        }
        
        # Detectar palabras clave específicas
        if "empresa" in prompt.lower() or "business" in prompt.lower():
            context["audience"] = "business"
        if "tech" in prompt.lower() or "tecnología" in prompt.lower():
            context["industry"] = "technology"
        if "médico" in prompt.lower() or "health" in prompt.lower():
            context["industry"] = "healthcare"
        
        return context
    
    async def _decompose_into_subtasks(self, prompt: str, task_type: TaskType) -> List[Dict[str, Any]]:
        """Descompone la tarea en subtareas específicas"""
        subtasks = []
        
        # Descomposición base según tipo de tarea
        if task_type == TaskType.WEB_DEVELOPMENT:
            subtasks = [
                {"name": "Análisis de requerimientos", "duration": "2-4 horas", "team": "research_team"},
                {"name": "Diseño de wireframes", "duration": "4-6 horas", "team": "ui_design_team"},
                {"name": "Desarrollo frontend", "duration": "1-2 días", "team": "frontend_team"},
                {"name": "Desarrollo backend", "duration": "1-2 días", "team": "backend_team"},
                {"name": "Integración y testing", "duration": "4-6 horas", "team": "testing_team"},
                {"name": "Generación de assets", "duration": "2-4 horas", "team": "image_generation_team"}
            ]
        elif task_type == TaskType.APP_DEVELOPMENT:
            subtasks = [
                {"name": "Investigación de mercado", "duration": "4-6 horas", "team": "market_research_team"},
                {"name": "Diseño de UI/UX móvil", "duration": "1-2 días", "team": "ui_design_team"},
                {"name": "Desarrollo de app", "duration": "2-3 días", "team": "mobile_dev_team"},
                {"name": "Backend y APIs", "duration": "1-2 días", "team": "backend_team"},
                {"name": "Testing y QA", "duration": "4-6 horas", "team": "testing_team"},
                {"name": "Generación de assets", "duration": "2-4 horas", "team": "image_generation_team"}
            ]
        elif task_type == TaskType.PRESENTATION_CREATION:
            subtasks = [
                {"name": "Estructura y contenido", "duration": "2-3 horas", "team": "content_team"},
                {"name": "Diseño de slides", "duration": "2-3 horas", "team": "design_team"},
                {"name": "Generación de visuales", "duration": "1-2 horas", "team": "image_generation_team"},
                {"name": "Revisión y refinamiento", "duration": "1-2 horas", "team": "content_team"}
            ]
        elif task_type == TaskType.IMAGE_GENERATION:
            subtasks = [
                {"name": "Análisis de intención visual", "duration": "30 min", "team": "intent_analyzer_team"},
                {"name": "Creación de prompts", "duration": "1-2 horas", "team": "prompt_engineering_team"},
                {"name": "Generación de imágenes", "duration": "1-2 horas", "team": "image_generation_team"},
                {"name": "Post-procesamiento", "duration": "30-60 min", "team": "image_post_processing_team"}
            ]
        else:
            # Subtareas genéricas
            subtasks = [
                {"name": "Investigación y análisis", "duration": "2-4 horas", "team": "research_team"},
                {"name": "Desarrollo/implementación", "duration": "4-6 horas", "team": "specialized_team"},
                {"name": "Revisión y entrega", "duration": "1-2 horas", "team": "quality_team"}
            ]
        
        return subtasks
    
    def _map_teams_to_task(self, task_type: TaskType, complexity: ComplexityLevel) -> List[str]:
        """Mapea los equipos requeridos para la tarea"""
        base_teams = self.team_mappings.get(task_type, [])
        
        # Agregar equipos base para todas las tareas
        all_tasks_teams = [
            "intent_analyzer_team",  # Siempre presente
            "project_management_team",  # Coordinación
            "quality_assurance_team"  # Control de calidad
        ]
        
        # Ajustar prioridad según complejidad
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            all_tasks_teams.extend([
                "architecture_team",  # Diseño de arquitectura
                "security_team",      # Seguridad
                "performance_team"    # Optimización
            ])
        
        # Combinar equipos específicos + base
        specific_teams = [team.team_name for team in base_teams]
        required_teams = specific_teams + all_tasks_teams
        
        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_teams = []
        for team in required_teams:
            if team not in seen:
                seen.add(team)
                unique_teams.append(team)
        
        return unique_teams
    
    def _estimate_effort(self, complexity: ComplexityLevel, num_subtasks: int) -> str:
        """Estima el esfuerzo total basado en complejidad y número de subtareas"""
        base_hours = {
            ComplexityLevel.SIMPLE: 4,
            ComplexityLevel.MODERATE: 8,
            ComplexityLevel.COMPLEX: 16,
            ComplexityLevel.ENTERPRISE: 32
        }
        
        estimated_hours = base_hours[complexity] * (1 + num_subtasks * 0.1)
        
        if estimated_hours <= 8:
            return f"{estimated_hours:.0f} horas (1 día)"
        elif estimated_hours <= 24:
            return f"{estimated_hours:.0f} horas ({estimated_hours/8:.1f} días)"
        elif estimated_hours <= 80:
            return f"{estimated_hours:.0f} horas ({estimated_hours/8:.1f} días)"
        else:
            return f"{estimated_hours:.0f} horas ({estimated_hours/40:.1f} semanas)"
    
    def _define_success_criteria(self, task_type: TaskType, prompt: str) -> List[str]:
        """Define criterios de éxito para la tarea"""
        criteria = []
        
        if task_type == TaskType.WEB_DEVELOPMENT:
            criteria = [
                "Sitio web funcional y responsive",
                "Código limpio y bien documentado",
                "Navegación intuitiva",
                "Optimización de velocidad",
                "Compatibilidad cross-browser"
            ]
        elif task_type == TaskType.APP_DEVELOPMENT:
            criteria = [
                "App funcional en iOS y Android",
                "Interfaz intuitiva y atractiva",
                "Rendimiento óptimo",
                "Funcionalidad offline",
                "Publicación en stores"
            ]
        elif task_type == TaskType.PRESENTATION_CREATION:
            criteria = [
                "Presentación visualmente atractiva",
                "Mensaje claro y estructurado",
                "Flujo narrativo coherente",
                "Elementos visuales impactantes",
                "Tiempo de presentación apropiado"
            ]
        elif task_type == TaskType.IMAGE_GENERATION:
            criteria = [
                "Imágenes que reflejan la intención",
                "Calidad profesional",
                "Coherencia visual",
                "Resolución apropiada",
                "Formato optimizado para uso"
            ]
        else:
            criteria = [
                "Objetivo principal cumplido",
                "Calidad profesional",
                "Cumplimiento de requerimientos",
                "Entrega en tiempo acordado",
                "Documentación completa"
            ]
        
        return criteria
    
    def _identify_dependencies(self, subtasks: List[Dict[str, Any]]) -> List[str]:
        """Identifica dependencias entre subtareas"""
        dependencies = []
        
        for i, subtask in enumerate(subtasks):
            # Dependencias secuenciales típicas
            if subtask["name"] == "Análisis de requerimientos":
                dependencies.extend(["Diseño wireframes", "Desarrollo"])
            elif subtask["name"] == "Diseño de wireframes":
                dependencies.append("Desarrollo frontend")
            elif subtask["name"] == "Desarrollo frontend":
                dependencies.append("Integración y testing")
            elif subtask["name"] == "Desarrollo backend":
                dependencies.append("Integración y testing")
            elif subtask["name"] == "Generación de assets":
                dependencies.append("Desarrollo frontend")
        
        return list(set(dependencies))  # Eliminar duplicados
    
    async def generate_team_workflow(self, analysis: IntentAnalysis) -> Dict[str, Any]:
        """Genera el workflow completo de equipos para ejecutar la tarea"""
        workflow = {
            "workflow_id": hashlib.md5(analysis.original_prompt.encode()).hexdigest()[:8],
            "task_type": analysis.task_type.value,
            "complexity": analysis.complexity.value,
            "estimated_total_time": analysis.estimated_effort,
            "phases": []
        }
        
        # Fase 1: Análisis y planificación
        workflow["phases"].append({
            "phase": 1,
            "name": "Análisis y Planificación",
            "teams": ["intent_analyzer_team", "project_management_team"],
            "duration": "1-2 horas",
            "deliverables": ["Análisis de requerimientos", "Plan de proyecto"]
        })
        
        # Fase 2: Investigación y diseño
        if "research" in [team for team in analysis.required_teams]:
            workflow["phases"].append({
                "phase": 2,
                "name": "Investigación y Diseño",
                "teams": [team for team in analysis.required_teams if "research" in team or "design" in team],
                "duration": "4-8 horas",
                "deliverables": ["Research findings", "Design mockups", "Visual strategy"]
            })
        
        # Fase 3: Desarrollo/Implementación
        development_teams = [team for team in analysis.required_teams 
                           if any(keyword in team for keyword in ["development", "generation", "creation"])]
        if development_teams:
            workflow["phases"].append({
                "phase": 3,
                "name": "Desarrollo e Implementación",
                "teams": development_teams,
                "duration": "8-16 horas",
                "deliverables": ["Producto funcional", "Assets generados", "Código desarrollado"]
            })
        
        # Fase 4: Control de calidad
        workflow["phases"].append({
            "phase": 4,
            "name": "Control de Calidad",
            "teams": ["quality_assurance_team", "testing_team"],
            "duration": "2-4 horas",
            "deliverables": ["Testing completo", "Revisión de calidad", "Correcciones finales"]
        })
        
        return workflow
    
    def to_dict(self, analysis: IntentAnalysis) -> Dict[str, Any]:
        """Convierte el análisis a diccionario para serialización"""
        return {
            "original_prompt": analysis.original_prompt,
            "primary_intent": analysis.primary_intent,
            "task_type": analysis.task_type.value,
            "complexity": analysis.complexity.value,
            "required_teams": analysis.required_teams,
            "sub_tasks": analysis.sub_tasks,
            "context": analysis.context,
            "estimated_effort": analysis.estimated_effort,
            "success_criteria": analysis.success_criteria,
            "dependencies": analysis.dependencies
        }

# Instancia global del analizador
intent_analyzer = IntentAnalyzerTeam()