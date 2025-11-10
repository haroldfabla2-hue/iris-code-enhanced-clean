"""
TaskManager para tracking de tareas en tiempo real
Integra con MultiAgentOrchestrator y Streaming SSE
"""
from typing import Dict, Any, Optional, List, AsyncGenerator
import asyncio
import logging
from datetime import datetime, timedelta
import uuid
import json
from enum import Enum
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Estados de tarea"""
    CREATED = "created"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class TaskPhase(Enum):
    """Fases de ejecución de tarea"""
    REASONING = "reasoning"
    PLANNING = "planning"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    COMPLETION = "completion"


@dataclass
class TaskInfo:
    """Información completa de una tarea"""
    task_id: str
    objective: str
    user_id: Optional[str]
    status: TaskStatus
    phase: TaskPhase
    progress: float
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TaskManager:
    """
    Gestor de tareas para tracking en tiempo real
    Maneja estado de tareas y streaming updates
    """
    
    def __init__(self):
        self.tasks: Dict[str, TaskInfo] = {}
        self.subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)
        self.task_locks: Dict[str, asyncio.Lock] = {}
        self.cleanup_interval = 3600  # 1 hora
        
        # Iniciar cleanup de tareas viejas
        self._start_cleanup_task()
    
    def create_task(
        self,
        objective: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Crea una nueva tarea"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        task_info = TaskInfo(
            task_id=task_id,
            objective=objective,
            user_id=user_id,
            status=TaskStatus.CREATED,
            phase=TaskPhase.REASONING,
            progress=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task_info
        self.task_locks[task_id] = asyncio.Lock()
        
        logger.info(f"Tarea creada: {task_id} - {objective}")
        return task_id
    
    async def update_task(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        phase: Optional[TaskPhase] = None,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Actualiza el estado de una tarea"""
        
        if task_id not in self.tasks:
            logger.warning(f"Tarea no encontrada: {task_id}")
            return False
        
        task_info = self.tasks[task_id]
        
        async with self.task_locks[task_id]:
            # Actualizar campos
            if status:
                task_info.status = status
            if phase:
                task_info.phase = phase
            if progress is not None:
                task_info.progress = progress
            if result is not None:
                task_info.result = result
            if error is not None:
                task_info.error = error
            if metadata:
                task_info.metadata.update(metadata)
            
            task_info.updated_at = datetime.now()
            
            # Crear update para streaming
            update = {
                "task_id": task_id,
                "status": task_info.status.value,
                "phase": task_info.phase.value if task_info.phase else None,
                "progress": task_info.progress,
                "message": message,
                "result": task_info.result,
                "metadata": {
                    **task_info.metadata,
                    "updated_at": task_info.updated_at.isoformat()
                },
                "timestamp": task_info.updated_at.isoformat()
            }
            
            # Notificar a suscriptores
            await self._notify_subscribers(task_id, update)
            
            logger.info(f"Tarea actualizada: {task_id} - {task_info.status.value} - {task_info.phase.value if task_info.phase else 'N/A'}")
            return True
    
    async def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Obtiene información de una tarea"""
        return self.tasks.get(task_id)
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado actual de una tarea"""
        task_info = self.tasks.get(task_id)
        if not task_info:
            return None
        
        return {
            "task_id": task_info.task_id,
            "status": task_info.status.value,
            "created_at": task_info.created_at.isoformat(),
            "updated_at": task_info.updated_at.isoformat(),
            "progress": task_info.progress,
            "phase": task_info.phase.value if task_info.phase else None,
            "user_id": task_info.user_id,
            "objective": task_info.objective,
            "result": task_info.result,
            "error": task_info.error,
            "metadata": task_info.metadata
        }
    
    async def list_tasks(
        self,
        user_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Lista tareas con filtros"""
        
        tasks = list(self.tasks.values())
        
        # Aplicar filtros
        if user_id:
            tasks = [t for t in tasks if t.user_id == user_id]
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        # Ordenar por fecha de creación (más recientes primero)
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        # Aplicar paginación
        paginated_tasks = tasks[offset:offset + limit]
        
        return [
            {
                "task_id": task.task_id,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "progress": task.progress,
                "phase": task.phase.value if task.phase else None,
                "user_id": task.user_id,
                "objective": task.objective[:100] + "..." if len(task.objective) > 100 else task.objective
            }
            for task in paginated_tasks
        ]
    
    async def delete_task(self, task_id: str) -> bool:
        """Elimina una tarea"""
        
        if task_id not in self.tasks:
            return False
        
        # Notificar cancelación a suscriptores
        await self.update_task(
            task_id=task_id,
            status=TaskStatus.CANCELLED,
            message="Tarea cancelada"
        )
        
        # Eliminar de estructuras de datos
        del self.tasks[task_id]
        del self.task_locks[task_id]
        
        # Limpiar suscriptores
        if task_id in self.subscribers:
            del self.subscribers[task_id]
        
        logger.info(f"Tarea eliminada: {task_id}")
        return True
    
    def subscribe(self, task_id: str, queue: asyncio.Queue):
        """Suscribe una cola para recibir updates de una tarea"""
        self.subscribers[task_id].append(queue)
    
    def unsubscribe(self, task_id: str, queue: asyncio.Queue):
        """Desuscribe una cola"""
        if task_id in self.subscribers:
            try:
                self.subscribers[task_id].remove(queue)
            except ValueError:
                pass
    
    async def _notify_subscribers(self, task_id: str, update: Dict[str, Any]):
        """Notifica a todos los suscriptores de una tarea"""
        
        if task_id not in self.subscribers:
            return
        
        # Hacer una copia del update para cada suscriptor
        for queue in self.subscribers[task_id][:]:  # Copia para evitar problemas durante iteración
            try:
                await queue.put(update.copy())
            except Exception as e:
                logger.warning(f"Error enviando update a suscriptor: {e}")
                # Remover suscriptor problemático
                try:
                    self.subscribers[task_id].remove(queue)
                except ValueError:
                    pass
    
    async def stream_task_updates(
        self,
        task_id: str,
        update_frequency: float = 1.0,
        max_duration: int = 300
    ) -> AsyncGenerator[str, None]:
        """Genera stream de updates para una tarea"""
        
        queue = asyncio.Queue()
        self.subscribe(task_id, queue)
        
        start_time = datetime.now()
        
        try:
            while True:
                # Verificar timeout
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= max_duration:
                    break
                
                # Esperar por update o timeout
                try:
                    update = await asyncio.wait_for(queue.get(), timeout=update_frequency)
                    yield f"data: {json.dumps(update)}\n\n"
                    
                    # Si la tarea está completada, terminar stream
                    if update.get("status") in ["completed", "error", "cancelled"]:
                        break
                        
                except asyncio.TimeoutError:
                    # Timeout sin updates - enviar heartbeat
                    heartbeat = {
                        "task_id": task_id,
                        "status": "heartbeat",
                        "timestamp": datetime.now().isoformat(),
                        "message": "Alive"
                    }
                    yield f"data: {json.dumps(heartbeat)}\n\n"
                    
        except asyncio.CancelledError:
            logger.info(f"Stream cancelado para tarea {task_id}")
            
        finally:
            self.unsubscribe(task_id, queue)
            
            # Enviar señal de fin
            yield "data: [DONE]\n\n"
    
    def _start_cleanup_task(self):
        """Inicia tarea de limpieza de tareas viejas"""
        
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self.cleanup_interval)
                    await self._cleanup_old_tasks()
                except Exception as e:
                    logger.error(f"Error en cleanup de tareas: {e}")
        
        # Iniciar en thread separado para no bloquear
        loop = asyncio.get_event_loop()
        loop.create_task(cleanup_loop())
    
    async def _cleanup_old_tasks(self):
        """Limpia tareas completadas hace más de 1 hora"""
        
        cutoff_time = datetime.now() - timedelta(hours=1)
        tasks_to_remove = []
        
        for task_id, task_info in self.tasks.items():
            if (task_info.status in [TaskStatus.COMPLETED, TaskStatus.ERROR, TaskStatus.CANCELLED] 
                and task_info.updated_at < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            await self.delete_task(task_id)
        
        if tasks_to_remove:
            logger.info(f"Limpieza completada: {len(tasks_to_remove)} tareas eliminadas")


# Instancia global del TaskManager
task_manager = TaskManager()