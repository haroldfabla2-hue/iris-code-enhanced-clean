"""
TaskOrchestratorIntegrator
Integra TaskManager con MultiAgentOrchestrator para streaming real
"""
from typing import Dict, Any, Optional, Callable
import asyncio
import logging
from datetime import datetime

from .task_manager import task_manager, TaskStatus, TaskPhase

logger = logging.getLogger(__name__)


class TaskOrchestratorIntegrator:
    """
    Integrador que conecta TaskManager con MultiAgentOrchestrator
    Permite que las tareas reales se actualicen automáticamente
    """
    
    def __init__(self, task_manager, orchestrator):
        self.task_manager = task_manager
        self.orchestrator = orchestrator
        self.active_tasks: Dict[str, asyncio.Task] = {}
    
    async def execute_task_with_tracking(
        self,
        task_id: str,
        objective: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta una tarea con tracking completo
        
        Args:
            task_id: ID de la tarea
            objective: Objetivo a cumplir
            user_id: ID del usuario
            context: Contexto adicional
            
        Returns:
            Resultado de la tarea
        """
        
        try:
            logger.info(f"Iniciando ejecución de tarea {task_id}: {objective}")
            
            # Actualizar estado a in_progress
            await self.task_manager.update_task(
                task_id=task_id,
                status=TaskStatus.IN_PROGRESS,
                phase=TaskPhase.REASONING,
                progress=0.1,
                message="Iniciando razonamiento"
            )
            
            # Ejecutar tarea en el orquestador con callbacks de actualización
            result = await self.orchestrator.process_request(
                objetivo=objective,
                contexto=context or {}
            )
            
            # Marcar como completada
            await self.task_manager.update_task(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                phase=TaskPhase.COMPLETION,
                progress=1.0,
                message="Tarea completada exitosamente",
                result=result
            )
            
            logger.info(f"Tarea {task_id} completada exitosamente")
            return result
            
        except Exception as e:
            logger.error(f"Error ejecutando tarea {task_id}: {e}")
            
            # Marcar como error
            await self.task_manager.update_task(
                task_id=task_id,
                status=TaskStatus.ERROR,
                phase=TaskPhase.EXECUTION,
                message=f"Error en ejecución: {str(e)}",
                error=str(e)
            )
            
            raise
    
    def _update_task_progress(
        self,
        task_id: str,
        phase: str,
        progress: float,
        message: str
    ):
        """
        Callback para actualizar progreso de tarea
        
        Args:
            task_id: ID de la tarea
            phase: Fase actual
            progress: Progreso (0.0-1.0)
            message: Mensaje descriptivo
        """
        
        try:
            # Convertir string de fase a enum
            phase_enum = None
            if phase:
                try:
                    phase_enum = TaskPhase(phase.lower())
                except ValueError:
                    logger.warning(f"Fase desconocida: {phase}")
                    phase_enum = TaskPhase.EXECUTION
            
            # Actualizar en TaskManager
            asyncio.create_task(
                self.task_manager.update_task(
                    task_id=task_id,
                    phase=phase_enum,
                    progress=progress,
                    message=message
                )
            )
            
        except Exception as e:
            logger.error(f"Error actualizando progreso de tarea {task_id}: {e}")
    
    async def execute_task_async(
        self,
        task_id: str,
        objective: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Ejecuta una tarea de manera asíncrona
        
        Args:
            task_id: ID de la tarea
            objective: Objetivo a cumplir
            user_id: ID del usuario
            context: Contexto adicional
            
        Returns:
            Task ID (para tracking)
        """
        
        # Crear tarea asíncrona
        execution_task = asyncio.create_task(
            self.execute_task_with_tracking(
                task_id=task_id,
                objective=objective,
                user_id=user_id,
                context=context
            )
        )
        
        # Guardar referencia para cancellation
        self.active_tasks[task_id] = execution_task
        
        # Cleanup cuando termine
        execution_task.add_done_callback(
            lambda t: self.active_tasks.pop(task_id, None)
        )
        
        return task_id
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancela una tarea en ejecución
        
        Args:
            task_id: ID de la tarea a cancelar
            
        Returns:
            True si se canceló exitosamente
        """
        
        try:
            if task_id in self.active_tasks:
                # Cancelar tarea en orquestador
                task = self.active_tasks[task_id]
                task.cancel()
                
                # Esperar a que termine la cancelación
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                # Marcar como cancelada en TaskManager
                await self.task_manager.update_task(
                    task_id=task_id,
                    status=TaskStatus.CANCELLED,
                    message="Tarea cancelada por el usuario"
                )
                
                logger.info(f"Tarea {task_id} cancelada exitosamente")
                return True
            else:
                logger.warning(f"Tarea {task_id} no encontrada en tareas activas")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelando tarea {task_id}: {e}")
            return False
    
    async def get_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el progreso actual de una tarea
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            Información de progreso o None si no existe
        """
        
        try:
            return await self.task_manager.get_task_status(task_id)
        except Exception as e:
            logger.error(f"Error obteniendo progreso de tarea {task_id}: {e}")
            return None


# Instancia global del integrador
task_orchestrator_integrator = None


def initialize_task_orchestrator_integrator(task_manager_instance, orchestrator_instance):
    """
    Inicializa el integrador global
    
    Args:
        task_manager_instance: Instancia del TaskManager
        orchestrator_instance: Instancia del MultiAgentOrchestrator
    """
    global task_orchestrator_integrator
    task_orchestrator_integrator = TaskOrchestratorIntegrator(
        task_manager=task_manager_instance,
        orchestrator=orchestrator_instance
    )
    logger.info("TaskOrchestratorIntegrator inicializado")


def get_task_orchestrator_integrator() -> TaskOrchestratorIntegrator:
    """
    Obtiene la instancia global del integrador
    
    Returns:
        TaskOrchestratorIntegrator instance
        
    Raises:
        RuntimeError: Si no ha sido inicializado
    """
    global task_orchestrator_integrator
    if not task_orchestrator_integrator:
        raise RuntimeError("TaskOrchestratorIntegrator no ha sido inicializado")
    return task_orchestrator_integrator