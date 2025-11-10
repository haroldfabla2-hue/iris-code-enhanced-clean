"""
Endpoints para streaming de tareas
/api/v1/tasks/{id}/stream
"""
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import AsyncGenerator, Dict, Any, Optional, Literal
import asyncio
import json
import logging
from datetime import datetime, timedelta
import uuid

from ..orchestrator import MultiAgentOrchestrator
from ..services.task_manager import task_manager, TaskStatus, TaskPhase
from ..services.task_orchestrator_integrator import get_task_orchestrator_integrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])

# Modelos de request/response
class ExecuteTaskRequest(BaseModel):
    """Request para ejecutar una tarea"""
    objective: str = Field(..., description="Objetivo o tarea a cumplir")
    user_id: Optional[str] = Field(None, description="ID del usuario que solicita la tarea")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional para la ejecución")
class TaskUpdate(BaseModel):
    """Update de tarea para streaming"""
    task_id: str
    status: Literal["started", "in_progress", "completed", "error", "cancelled"]
    phase: Optional[str] = Field(None, description="Fase actual del proceso")
    progress: Optional[float] = Field(None, description="Progreso (0.0-1.0)", ge=0.0, le=1.0)
    message: Optional[str] = Field(None, description="Mensaje descriptivo")
    result: Optional[Dict[str, Any]] = Field(None, description="Resultado parcial")
    agent_updates: Optional[Dict[str, Any]] = Field(None, description="Updates por agente")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class TaskStreamConfig(BaseModel):
    """Configuración para streaming de tareas"""
    update_frequency: float = Field(1.0, description="Frecuencia de updates en segundos", ge=0.1, le=10.0)
    include_results: bool = Field(True, description="Incluir resultados parciales")
    include_agent_details: bool = Field(False, description="Incluir detalles por agente")
    max_duration: int = Field(300, description="Duración máxima en segundos", ge=30, le=1800)


@router.post("/create")
async def create_task(
    objective: str,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Crea una nueva tarea para procesar
    
    - **objective**: Objetivo o tarea a cumplir
    - **user_id**: ID del usuario que solicita la tarea
    - **metadata**: Metadatos adicionales
    """
    
    try:
        logger.info(f"Creando nueva tarea: {objective}")
        
        # Crear tarea en TaskManager
        task_id = task_manager.create_task(
            objective=objective,
            user_id=user_id,
            metadata=metadata
        )
        
        # Inicializar tarea como started
        await task_manager.update_task(
            task_id=task_id,
            status=TaskStatus.STARTED,
            message="Tarea creada e iniciada"
        )
        
        return {
            "task_id": task_id,
            "status": "created",
            "objective": objective,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "stream_url": f"/api/v1/tasks/{task_id}/stream"
        }
        
    except Exception as e:
        logger.exception("Error creando tarea")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/execute")
async def execute_task(
    request: ExecuteTaskRequest,
    execute_async: bool = Query(True, description="Ejecutar de forma asíncrona")
):
    """
    Ejecuta una tarea usando el MultiAgentOrchestrator real
    
    - **request**: Datos de la tarea a ejecutar
    - **execute_async**: Si ejecutar de forma asíncrona (recomendado)
    """
    
    try:
        logger.info(f"Ejecutando tarea: {request.objective}")
        
        # Crear tarea en TaskManager
        task_id = task_manager.create_task(
            objective=request.objective,
            user_id=request.user_id,
            metadata=request.context
        )
        
        # Obtener integrador
        integrator = get_task_orchestrator_integrator()
        
        if execute_async:
            # Ejecutar asíncronamente
            await integrator.execute_task_async(
                task_id=task_id,
                objective=request.objective,
                user_id=request.user_id,
                context=request.context
            )
            
            return {
                "task_id": task_id,
                "status": "started",
                "objective": request.objective,
                "user_id": request.user_id,
                "execution_mode": "async",
                "stream_url": f"/api/v1/tasks/{task_id}/stream",
                "status_url": f"/api/v1/tasks/{task_id}/status",
                "message": "Tarea ejecutándose de forma asíncrona"
            }
        else:
            # Ejecutar de forma síncrona (bloqueante)
            result = await integrator.execute_task_with_tracking(
                task_id=task_id,
                objective=request.objective,
                user_id=request.user_id,
                context=request.context
            )
            
            return {
                "task_id": task_id,
                "status": "completed",
                "objective": request.objective,
                "user_id": request.user_id,
                "execution_mode": "sync",
                "result": result,
                "completed_at": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.exception("Error ejecutando tarea")
        
        # Marcar como error si la tarea se creó
        if 'task_id' in locals():
            await task_manager.update_task(
                task_id=task_id,
                status=TaskStatus.ERROR,
                message=f"Error en ejecución: {str(e)}",
                error=str(e)
            )
        
        raise HTTPException(status_code=500, detail=f"Error ejecutando tarea: {str(e)}")


@router.get("/{task_id}/stream")
async def stream_task_updates(
    task_id: str = Path(..., description="ID de la tarea"),
    update_frequency: float = Query(1.0, description="Frecuencia de updates en segundos"),
    include_results: bool = Query(True, description="Incluir resultados parciales"),
    include_agent_details: bool = Query(False, description="Incluir detalles por agente"),
    max_duration: int = Query(300, description="Duración máxima en segundos")
):
    """
    Stream de updates en tiempo real para una tarea específica
    
    - **task_id**: ID de la tarea a seguir
    - **update_frequency**: Frecuencia de updates (0.1-10.0 segundos)
    - **include_results**: Si incluir resultados parciales
    - **include_agent_details**: Si incluir detalles por agente
    - **max_duration**: Duración máxima del stream (30-1800 segundos)
    """
    
    logger.info(f"Iniciando stream para tarea: {task_id}")
    
    # Validar parámetros
    if not 0.1 <= update_frequency <= 10.0:
        raise HTTPException(status_code=400, detail="update_frequency debe estar entre 0.1 y 10.0")
    
    if not 30 <= max_duration <= 1800:
        raise HTTPException(status_code=400, detail="max_duration debe estar entre 30 y 1800 segundos")
    
    # Verificar que la tarea existe
    task_info = await task_manager.get_task(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail=f"Tarea no encontrada: {task_id}")
    
    # Generar stream usando TaskManager real
    return StreamingResponse(
        task_manager.stream_task_updates(
            task_id=task_id,
            update_frequency=update_frequency,
            max_duration=max_duration
        ),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/{task_id}/status")
async def get_task_status(task_id: str):
    """
    Obtiene el estado actual de una tarea
    
    - **task_id**: ID de la tarea
    """
    
    try:
        # Obtener estado real del TaskManager
        status_info = await task_manager.get_task_status(task_id)
        
        if not status_info:
            raise HTTPException(status_code=404, detail=f"Tarea no encontrada: {task_id}")
        
        # Calcular estimación de finalización si está en progreso
        if status_info["status"] == "in_progress" and status_info.get("progress", 0) > 0:
            # Estimación simple basada en progreso
            elapsed = (datetime.now() - datetime.fromisoformat(status_info["updated_at"])).total_seconds()
            if elapsed > 0:
                remaining_estimate = elapsed * (1 - status_info["progress"]) / status_info["progress"]
                estimated_completion = datetime.now() + timedelta(seconds=remaining_estimate)
                status_info["estimated_completion"] = estimated_completion.isoformat()
        
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error obteniendo estado de tarea {task_id}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/{task_id}/results")
async def get_task_results(
    task_id: str,
    include_intermediate: bool = Query(False, description="Incluir resultados intermedios")
):
    """
    Obtiene los resultados finales de una tarea
    
    - **task_id**: ID de la tarea
    - **include_intermediate**: Si incluir resultados intermedios
    """
    
    try:
        # TODO: Implementar recuperación de resultados reales
        
        mock_results = {
            "task_id": task_id,
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "final_result": {
                "summary": "Tarea completada exitosamente",
                "output": "Resultado final de la tarea",
                "artifacts": [
                    {"type": "file", "name": "resultado.txt", "path": "/tmp/resultado.txt"},
                    {"type": "data", "name": "dataset.csv", "records": 150}
                ]
            },
            "execution_stats": {
                "total_duration": 298.5,  # segundos
                "agents_used": ["reasoner", "planner", "executor", "verifier"],
                "tools_executed": 12,
                "total_cost": 0.045
            }
        }
        
        if include_intermediate:
            mock_results["intermediate_results"] = [
                {
                    "step": 1,
                    "phase": "reasoning",
                    "result": {"analysis": "Análisis completado"},
                    "timestamp": (datetime.now() - timedelta(minutes=4)).isoformat()
                },
                {
                    "step": 2, 
                    "phase": "planning",
                    "result": {"plan": "Plan de ejecución generado"},
                    "timestamp": (datetime.now() - timedelta(minutes=3)).isoformat()
                }
            ]
        
        return mock_results
        
    except Exception as e:
        logger.exception(f"Error obteniendo resultados de tarea {task_id}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancela una tarea en ejecución
    
    - **task_id**: ID de la tarea a cancelar
    """
    
    try:
        logger.info(f"Cancelando tarea: {task_id}")
        
        # Cancelar tarea en TaskManager
        success = await task_manager.delete_task(task_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Tarea no encontrada: {task_id}")
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "cancelled_at": datetime.now().isoformat(),
            "message": "Tarea cancelada por solicitud del usuario"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error cancelando tarea {task_id}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/list")
async def list_tasks(
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(20, description="Número máximo de resultados", ge=1, le=100),
    offset: int = Query(0, description="Offset para paginación", ge=0)
):
    """
    Lista tareas con filtros opcionales
    
    - **user_id**: Filtrar por usuario específico
    - **status**: Filtrar por estado (created, started, in_progress, completed, error, cancelled)
    - **limit**: Número máximo de resultados (1-100)
    - **offset**: Offset para paginación
    """
    
    try:
        # Convertir status string a enum
        status_enum = None
        if status:
            try:
                status_enum = TaskStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Estado inválido: {status}")
        
        # Obtener tareas del TaskManager real
        tasks = await task_manager.list_tasks(
            user_id=user_id,
            status=status_enum,
            limit=limit,
            offset=offset
        )
        
        return {
            "tasks": tasks,
            "total": len(tasks),
            "limit": limit,
            "offset": offset,
            "has_more": len(tasks) == limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error listando tareas")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Funciones auxiliares para streaming
async def _generate_task_updates(
    task_id: str,
    update_frequency: float,
    include_results: bool,
    include_agent_details: bool,
    max_duration: int
) -> AsyncGenerator[str, None]:
    """
    Genera actualizaciones de tarea en tiempo real
    """
    
    start_time = datetime.now()
    
    # Simulación de fases de tarea
    phases = [
        ("reasoning", "Analizando el objetivo", 0.2),
        ("planning", "Creando plan de ejecución", 0.4),
        ("execution", "Ejecutando tareas", 0.8),
        ("verification", "Verificando resultados", 0.9),
        ("completion", "Finalizando", 1.0)
    ]
    
    try:
        for phase_name, phase_message, progress in phases:
            # Calcular tiempo transcurrido
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if elapsed >= max_duration:
                break
            
            # Generar update
            update = TaskUpdate(
                task_id=task_id,
                status="in_progress",
                phase=phase_name,
                progress=progress,
                message=phase_message,
                result={
                    "current_phase": phase_name,
                    "progress_percentage": int(progress * 100)
                } if include_results else None,
                agent_updates={
                    "reasoner": {"status": "completed", "output": f"Razonamiento completado en {phase_name}"},
                    "planner": {"status": "completed", "output": "Plan creado"},
                    "executor": {"status": "in_progress", "output": "Ejecutando..."},
                    "verifier": {"status": "pending"}
                } if include_agent_details else None,
                metadata={
                    "elapsed_seconds": elapsed,
                    "estimated_remaining": (max_duration - elapsed),
                    "phase_start": datetime.now().isoformat()
                }
            )
            
            # Enviar update
            yield f"data: {update.json()}\n\n"
            
            # Esperar antes del siguiente update
            await asyncio.sleep(update_frequency)
        
        # Update final
        final_update = TaskUpdate(
            task_id=task_id,
            status="completed",
            phase="completed",
            progress=1.0,
            message="Tarea completada exitosamente",
            result={
                "completion_time": datetime.now().isoformat(),
                "total_duration": (datetime.now() - start_time).total_seconds()
            } if include_results else None,
            metadata={
                "completed_at": datetime.now().isoformat(),
                "total_duration": (datetime.now() - start_time).total_seconds()
            }
        )
        
        yield f"data: {final_update.json()}\n\n"
        
        # Señal de fin
        yield "data: [DONE]\n\n"
        
    except asyncio.CancelledError:
        # Cliente desconectado
        logger.info(f"Stream cancelado para tarea {task_id}")
        
        cancel_update = TaskUpdate(
            task_id=task_id,
            status="cancelled",
            message="Stream cancelado por el cliente",
            metadata={"cancelled_at": datetime.now().isoformat()}
        )
        
        yield f"data: {cancel_update.json()}\n\n"
        
    except Exception as e:
        # Error en el stream
        logger.exception(f"Error en stream de tarea {task_id}")
        
        error_update = TaskUpdate(
            task_id=task_id,
            status="error",
            message=f"Error en streaming: {str(e)}",
            metadata={"error_at": datetime.now().isoformat()}
        )
        
        yield f"data: {error_update.json()}\n\n"