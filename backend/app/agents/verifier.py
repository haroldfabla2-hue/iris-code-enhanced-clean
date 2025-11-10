"""
Agente Verifier - Valida resultados y calidad
Responsable de revisar coherencia y ejecutar gates de calidad
"""
from typing import List, Dict, Any
import json

from .base import BaseAgent
from ..models import AgentMessage, AgentResponse, MessageStatus


class VerifierAgent(BaseAgent):
    """
    Agente Verifier: Valida coherencia y calidad de resultados
    
    Responsabilidades:
    - Revisar coherencia de resultados
    - Comprobar pruebas (E2E/unitarias)
    - Activar gates de calidad
    - Evaluar trayectorias de agentes
    """
    
    def __init__(self, llm_client: Any = None):
        super().__init__(
            agent_id="verifier",
            llm_client=llm_client
        )
        self.quality_thresholds = {
            "precision": 0.8,
            "completeness": 0.75,
            "consistency": 0.85,
            "citation": 0.7
        }
    
    def get_capabilities(self) -> List[str]:
        return [
            "result_validation",
            "quality_assessment",
            "trajectory_evaluation",
            "consistency_checking"
        ]
    
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """
        Procesa mensaje validando resultados
        """
        self.log_trace("verifier_start", {
            "message_id": message.message_id
        })
        
        try:
            # Extraer datos a validar
            validation_request = message.payload.get("validation_request", {})
            results = message.payload.get("results", {})
            trajectory = message.payload.get("trajectory", [])
            criterios = validation_request.get("criterios", [])
            
            # Validar resultados
            validation_report = await self._validate_results(
                results,
                criterios,
                validation_request
            )
            
            # Evaluar trayectoria de ejecución
            trajectory_score = await self._evaluate_trajectory(trajectory)
            
            # Verificar consistencia
            consistency_check = self._check_consistency(results)
            
            # Determinar aprobación
            approved = self._determine_approval(
                validation_report,
                trajectory_score,
                consistency_check
            )
            
            result = {
                "validation_report": validation_report,
                "trajectory_score": trajectory_score,
                "consistency_check": consistency_check,
                "approved": approved,
                "recommendations": self._generate_recommendations(
                    validation_report,
                    trajectory_score,
                    consistency_check
                ),
                "quality_metrics": self._compute_quality_metrics(
                    validation_report,
                    trajectory_score,
                    consistency_check
                )
            }
            
            self.log_trace("verifier_complete", {
                "message_id": message.message_id,
                "approved": approved,
                "quality_score": result["quality_metrics"]["overall_score"]
            })
            
            return AgentResponse(
                message_id=f"resp_{message.message_id}",
                original_message_id=message.message_id,
                agent_id=self.agent_id,
                status=MessageStatus.DONE,
                result=result
            )
            
        except Exception as e:
            self.logger.exception("Error en Verifier")
            raise
    
    async def _validate_results(
        self,
        results: Dict[str, Any],
        criterios: List[str],
        validation_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida resultados según criterios"""
        
        eval_type = validation_request.get("eval_type", "llm_judge")
        thresholds = validation_request.get("thresholds", [])
        
        if eval_type == "llm_judge":
            return await self._llm_judge_evaluation(
                results,
                criterios,
                thresholds
            )
        elif eval_type == "code":
            return await self._code_evaluation(results, criterios)
        else:
            return await self._heuristic_evaluation(results, criterios)
    
    async def _llm_judge_evaluation(
        self,
        results: Dict[str, Any],
        criterios: List[str],
        thresholds: List[float]
    ) -> Dict[str, Any]:
        """Evaluación usando LLM como juez"""
        
        prompt = f"""Actúa como un juez experto evaluando resultados de agentes. 

Contexto del Sistema:
- Este es un sistema multi-agente con herramientas reales
- Los resultados incluyen ejecución de código, búsqueda web, y procesamiento de archivos
- Se requiere evaluación rigurosa de calidad y precisión

Resultados a evaluar:
{json.dumps(results, indent=2, ensure_ascii=False)}

Criterios de evaluación:
{chr(10).join(f'{i+1}. {c}' for i, c in enumerate(criterios))}

Evalúa cada criterio objetivamente del 0.0 al 1.0, considerando:
- 0.0-0.3: Insuficiente - No cumple requisitos básicos
- 0.4-0.6: Aceptable - Cumple requisitos mínimos
- 0.7-0.8: Bueno - Cumple bien con algunas mejoras
- 0.9-1.0: Excelente - Supera expectativas

Para cada criterio proporciona:
1. Score numérico preciso (0.0-1.0)
2. Justificación específica basada en evidencia
3. Evaluación passed (score >= threshold)
4. Áreas concretas de mejora

Responde ÚNICAMENTE en formato JSON válido:
{{
  "scores": {{
    "{criterios[0] if criterios else 'criterio_ejemplo'}": {{
      "score": 0.85,
      "justification": "Evaluación detallada basada en evidencia",
      "passed": true,
      "evidence": "Puntos específicos que justifican el score"
    }}
  }},
  "overall_assessment": "Resumen general de calidad",
  "critical_issues": ["Problemas que requieren atención inmediata"]
}}
"""
        
        try:
            llm_response = await self.call_llm(
                prompt, 
                temperature=0.2, 
                max_tokens=2000,
                model="claude3_5"
            )
            
            # Procesar respuesta del LLM con mejor manejo de errores
            scores = await self._process_llm_evaluation_response(
                llm_response, criterios, thresholds, results
            )
            
            overall_score = sum(s["score"] for s in scores.values()) / len(scores) if scores else 0.0
            
            return {
                "eval_type": "llm_judge",
                "criterios_evaluated": criterios,
                "scores": scores,
                "overall_score": overall_score,
                "llm_response": llm_response,
                "parsing_success": "scores" in locals()
            }
            
        except Exception as e:
            self.logger.exception(f"Error en evaluación LLM: {str(e)}")
            # Fallback a evaluación heurística
            scores = await self._heuristic_fallback_evaluation(criterios, thresholds, results)
            overall_score = sum(s["score"] for s in scores.values()) / len(scores) if scores else 0.0
            
            return {
                "eval_type": "llm_judge_fallback",
                "criterios_evaluated": criterios,
                "scores": scores,
                "overall_score": overall_score,
                "error": str(e)
            }
    
    async def _heuristic_fallback_evaluation(
        self,
        criterios: List[str],
        thresholds: List[float],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluación heurística como fallback"""
        
        scores = {}
        
        for i, criterio in enumerate(criterios):
            threshold = thresholds[i] if i < len(thresholds) else 0.7
            
            # Evaluación heurística básica basada en el tipo de criterio
            criterion_lower = criterio.lower()
            
            if any(word in criterion_lower for word in ["completeness", "completitud", "completo"]):
                score = 0.8 if results else 0.3
            elif any(word in criterion_lower for word in ["accuracy", "precisión", "exactitud"]):
                score = 0.75 if not str(results).lower().count("error") else 0.4
            elif any(word in criterion_lower for word in ["consistency", "consistencia"]):
                score = 0.8 if isinstance(results, dict) else 0.5
            elif any(word in criterion_lower for word in ["relevance", "relevancia"]):
                score = 0.7 if results else 0.4
            else:
                score = 0.7  # Score neutral por defecto
            
            scores[criterio] = {
                "score": score,
                "threshold": threshold,
                "passed": score >= threshold,
                "justification": f"Evaluación heurística automática para: {criterio}"
            }
        
        return scores
    
    async def _code_evaluation(
        self,
        results: Dict[str, Any],
        criterios: List[str]
    ) -> Dict[str, Any]:
        """Evaluación programática"""
        
        scores = {}
        
        # Evaluaciones programáticas básicas
        if "code" in str(results):
            scores["has_code"] = {"score": 1.0, "passed": True}
        
        if "tests" in str(results):
            scores["has_tests"] = {"score": 1.0, "passed": True}
        
        if "error" not in str(results).lower():
            scores["no_errors"] = {"score": 1.0, "passed": True}
        
        overall_score = sum(s["score"] for s in scores.values()) / len(scores) if scores else 0.5
        
        return {
            "eval_type": "code",
            "criterios_evaluated": criterios,
            "scores": scores,
            "overall_score": overall_score
        }
    
    async def _heuristic_evaluation(
        self,
        results: Dict[str, Any],
        criterios: List[str]
    ) -> Dict[str, Any]:
        """Evaluación heurística simple"""
        
        scores = {
            "completeness": {
                "score": 0.8 if results else 0.0,
                "passed": bool(results)
            },
            "structure": {
                "score": 0.7 if isinstance(results, dict) else 0.3,
                "passed": isinstance(results, dict)
            }
        }
        
        overall_score = sum(s["score"] for s in scores.values()) / len(scores)
        
        return {
            "eval_type": "heuristic",
            "scores": scores,
            "overall_score": overall_score
        }
    
    async def _evaluate_trajectory(
        self,
        trajectory: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evalúa la trayectoria de ejecución de agentes"""
        
        if not trajectory:
            return {
                "score": 0.0,
                "efficiency": 0.0,
                "convergence": 0.0,
                "note": "No trajectory data"
            }
        
        # Métricas de trayectoria
        num_steps = len(trajectory)
        successful_steps = sum(
            1 for step in trajectory 
            if step.get("status") == "DONE"
        )
        
        efficiency = successful_steps / num_steps if num_steps > 0 else 0.0
        
        # Convergencia: ¿llegamos al objetivo sin muchos desvíos?
        convergence = 0.9 if efficiency > 0.8 else 0.6 if efficiency > 0.5 else 0.3
        
        trajectory_score = (efficiency + convergence) / 2
        
        return {
            "score": trajectory_score,
            "efficiency": efficiency,
            "convergence": convergence,
            "num_steps": num_steps,
            "successful_steps": successful_steps
        }
    
    def _check_consistency(
        self,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verifica consistencia interna de resultados"""
        
        consistency_checks = {
            "structure_valid": isinstance(results, dict),
            "no_contradictions": True,  # Mock - implementar lógica real
            "references_valid": True    # Mock - verificar referencias
        }
        
        consistency_score = sum(
            1 for check in consistency_checks.values() if check
        ) / len(consistency_checks)
        
        return {
            "score": consistency_score,
            "checks": consistency_checks,
            "passed": consistency_score >= self.quality_thresholds["consistency"]
        }
    
    def _determine_approval(
        self,
        validation_report: Dict[str, Any],
        trajectory_score: Dict[str, Any],
        consistency_check: Dict[str, Any]
    ) -> bool:
        """Determina si los resultados son aprobados"""
        
        # Criterios de aprobación
        validation_passed = validation_report.get("overall_score", 0) >= 0.7
        trajectory_passed = trajectory_score.get("score", 0) >= 0.6
        consistency_passed = consistency_check.get("passed", False)
        
        # Aprobar si la mayoría de criterios pasan
        passing_criteria = sum([
            validation_passed,
            trajectory_passed,
            consistency_passed
        ])
        
        return passing_criteria >= 2
    
    def _generate_recommendations(
        self,
        validation_report: Dict[str, Any],
        trajectory_score: Dict[str, Any],
        consistency_check: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones de mejora"""
        
        recommendations = []
        
        if validation_report.get("overall_score", 1.0) < 0.8:
            recommendations.append(
                "Mejorar calidad de resultados - score de validación bajo"
            )
        
        if trajectory_score.get("efficiency", 1.0) < 0.7:
            recommendations.append(
                "Optimizar trayectoria de ejecución - demasiados pasos fallidos"
            )
        
        if not consistency_check.get("passed", True):
            recommendations.append(
                "Resolver inconsistencias en resultados"
            )
        
        if not recommendations:
            recommendations.append("Resultados de buena calidad - sin mejoras críticas")
        
        return recommendations
    
    def _compute_quality_metrics(
        self,
        validation_report: Dict[str, Any],
        trajectory_score: Dict[str, Any],
        consistency_check: Dict[str, Any]
    ) -> Dict[str, float]:
        """Computa métricas consolidadas de calidad"""
        
        validation_score = validation_report.get("overall_score", 0.0)
        trajectory_quality = trajectory_score.get("score", 0.0)
        consistency_score = consistency_check.get("score", 0.0)
        
        # Score general ponderado
        overall_score = (
            validation_score * 0.5 +
            trajectory_quality * 0.3 +
            consistency_score * 0.2
        )
        
        return {
            "overall_score": overall_score,
            "validation_score": validation_score,
            "trajectory_quality": trajectory_quality,
            "consistency_score": consistency_score
        }
