"""
Preview API - Endpoints para gestión de previsualizaciones en vivo
"""

import json
import logging
import os
import tempfile
import shutil
import asyncio
from typing import Optional, Dict, List, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

from app.services.live_preview_service import live_preview_service, PreviewStatus

logger = logging.getLogger(__name__)

router = APIRouter()

# Modelos Pydantic
class CreatePreviewRequest(BaseModel):
    project_id: str
    framework: str
    files: Dict[str, str]
    port: Optional[int] = 3000
    auto_start: bool = True
    enable_hot_reload: bool = True

class UpdateFilesRequest(BaseModel):
    files: Dict[str, str]
    force_rebuild: bool = False

class DeployRequest(BaseModel):
    target: str = "production"  # production, staging, preview
    domain: Optional[str] = None
    environment: Optional[Dict[str, str]] = None

class PreviewResponse(BaseModel):
    session_id: str
    project_id: str
    status: str
    framework: str
    port: int
    url: str
    created_at: str
    terminals: List[str]

class PreviewStatsResponse(BaseModel):
    session_id: str
    project_id: str
    status: str
    framework: str
    uptime: int
    terminals: int
    active_terminals: int
    files_count: int
    memory_usage: int
    cpu_usage: int
    port: int
    url: str
    last_activity: Optional[str]

@router.post("/api/v1/preview/create")
async def create_preview_session(request: CreatePreviewRequest):
    """Crear nueva sesión de previsualización"""
    
    try:
        session_id = f"preview_{uuid.uuid4().hex[:12]}"
        
        # Crear sesión
        session = await live_preview_service.create_session(
            session_id=session_id,
            project_id=request.project_id,
            framework=request.framework,
            initial_files=request.files
        )
        
        # Configurar puerto
        session.port = request.port
        session.url = f"http://localhost:{request.port}"
        
        # Configurar auto-start
        if request.auto_start:
            # Aquí se iniciaría el servidor de desarrollo
            # Por ahora, simulamos el inicio
            logger.info(f"Auto-starting preview session {session_id}")
        
        # Respuesta
        response = PreviewResponse(
            session_id=session_id,
            project_id=request.project_id,
            status=session.status.value,
            framework=request.framework,
            port=session.port,
            url=session.url,
            created_at=session.created_at.isoformat() if session.created_at else None,
            terminals=list(session.terminals.keys())
        )
        
        logger.info(f"Created preview session {session_id} for project {request.project_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error creating preview session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/v1/preview/{session_id}")
async def get_preview_session(session_id: str):
    """Obtener información de una sesión de preview"""
    
    try:
        session = await live_preview_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Preview session not found")
        
        return {
            "session_id": session_id,
            "project_id": session.project_id,
            "status": session.status.value,
            "framework": session.framework,
            "port": session.port,
            "url": session.url,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "last_activity": session.last_activity.isoformat() if session.last_activity else None,
            "terminals": list(session.terminals.keys()),
            "files_count": len(session.files),
            "container_stats": session.container_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preview session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/v1/preview/{session_id}/status")
async def get_preview_status(session_id: str):
    """Obtener estado detallado de una sesión de preview"""
    
    try:
        session = await live_preview_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Preview session not found")
        
        stats = await live_preview_service.get_session_stats(session_id)
        
        return PreviewStatsResponse(
            session_id=session_id,
            project_id=session.project_id,
            status=session.status.value,
            framework=session.framework,
            uptime=stats["uptime"],
            terminals=stats["terminals"],
            active_terminals=stats["active_terminals"],
            files_count=stats["files_count"],
            memory_usage=stats["memory_usage"],
            cpu_usage=stats["cpu_usage"],
            port=stats["port"],
            url=stats["url"],
            last_activity=stats["last_activity"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preview status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/api/v1/preview/{session_id}/files")
async def update_preview_files(session_id: str, request: UpdateFilesRequest):
    """Actualizar archivos de una sesión de preview"""
    
    try:
        session = await live_preview_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Preview session not found")
        
        # Actualizar archivos
        await live_preview_service.update_session_files(session_id, request.files)
        
        # Notificar sobre rebuild si es necesario
        if request.force_rebuild:
            # Aquí se iniciaría un rebuild
            logger.info(f"Forcing rebuild for session {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "files_updated": len(request.files),
            "total_files": len(session.files),
            "force_rebuild": request.force_rebuild
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preview files: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/api/v1/preview/{session_id}")
async def close_preview_session(session_id: str):
    """Cerrar una sesión de preview"""
    
    try:
        session = await live_preview_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Preview session not found")
        
        await live_preview_service.close_session(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Preview session closed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing preview session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/v1/preview/{session_id}/deploy")
async def deploy_preview(
    session_id: str, 
    request: DeployRequest,
    background_tasks: BackgroundTasks
):
    """Desplegar una sesión de preview"""
    
    try:
        session = await live_preview_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Preview session not found")
        
        # Generar URL de deployment
        if request.target == "production":
            deploy_url = f"https://{session.project_id}.iris-app.dev"
        elif request.target == "staging":
            deploy_url = f"https://{session.project_id}-staging.iris-app.dev"
        else:  # preview
            deploy_url = f"https://{session.project_id}-preview.iris-app.dev"
        
        # Usar dominio personalizado si se proporciona
        if request.domain:
            deploy_url = f"https://{request.domain}"
        
        # Simular deployment
        logger.info(f"Deploying session {session_id} to {deploy_url}")
        
        # Tarea en background para deployment
        background_tasks.add_task(simulate_deployment, session_id, deploy_url)
        
        return {
            "success": True,
            "session_id": session_id,
            "deploy_url": deploy_url,
            "target": request.target,
            "status": "deploying"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying preview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def simulate_deployment(session_id: str, deploy_url: str):
    """Simular proceso de deployment en background"""
    try:
        # Simular tiempo de deployment
        await asyncio.sleep(3)
        
        # Aquí se realizaría el deployment real
        # Por ahora, solo registramos el éxito
        logger.info(f"Deployment completed for session {session_id} at {deploy_url}")
        
    except Exception as e:
        logger.error(f"Error in deployment simulation: {e}")

@router.get("/api/v1/preview/{session_id}/logs")
async def get_preview_logs(
    session_id: str,
    terminal_id: Optional[str] = Query(None, description="Specific terminal ID"),
    lines: int = Query(100, ge=1, le=1000, description="Number of log lines")
):
    """Obtener logs de una sesión de preview"""
    
    try:
        session = await live_preview_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Preview session not found")
        
        logs = []
        
        if terminal_id:
            # Logs de terminal específica
            if terminal_id in session.terminals:
                terminal = session.terminals[terminal_id]
                logs = terminal.output_buffer[-lines:]
            else:
                raise HTTPException(status_code=404, detail="Terminal not found")
        else:
            # Logs de todas las terminales
            for tid, terminal in session.terminals.items():
                terminal_logs = [f"[{tid}] {line}" for line in terminal.output_buffer[-lines:]]
                logs.extend(terminal_logs[-lines//len(session.terminals):])
        
        return {
            "session_id": session_id,
            "terminal_id": terminal_id,
            "logs": logs,
            "total_lines": len(logs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preview logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.websocket("/ws/preview/{session_id}")
async def websocket_preview_updates(
    websocket: WebSocket,
    session_id: str
):
    """WebSocket para actualizaciones en tiempo real del preview"""
    
    # Verificar que la sesión existe
    session = await live_preview_service.get_session(session_id)
    if not session:
        await websocket.close(code=4000, reason="Session not found")
        return
    
    await websocket.accept()
    
    try:
        # Enviar estado inicial
        initial_state = {
            "type": "session_connected",
            "session_id": session_id,
            "status": session.status.value,
            "framework": session.framework,
            "port": session.port,
            "url": session.url,
            "terminals": list(session.terminals.keys()),
            "files_count": len(session.files)
        }
        await websocket.send_json(initial_state)
        
        # Monitorear cambios en la sesión
        last_stats = await live_preview_service.get_session_stats(session_id)
        
        async for message in websocket.iter_text():
            try:
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    
                elif message_type == "get_stats":
                    stats = await live_preview_service.get_session_stats(session_id)
                    await websocket.send_json({
                        "type": "stats_update",
                        "stats": stats
                    })
                    
                elif message_type == "refresh_files":
                    # Refrescar archivos
                    files_update = {
                        "type": "files_update",
                        "files": session.files,
                        "count": len(session.files)
                    }
                    await websocket.send_json(files_update)
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Internal server error"
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for preview session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for preview session {session_id}: {e}")
    finally:
        # Cleanup si es necesario
        pass

@router.get("/api/v1/preview/list")
async def list_preview_sessions(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Listar todas las sesiones de preview"""
    
    try:
        sessions = await live_preview_service.list_sessions()
        
        # Filtrar por project_id si se proporciona
        if project_id:
            sessions = [s for s in sessions if s["project_id"] == project_id]
        
        # Filtrar por status si se proporciona
        if status:
            sessions = [s for s in sessions if s["status"] == status]
        
        return {
            "sessions": sessions,
            "total": len(sessions),
            "filters": {
                "project_id": project_id,
                "status": status
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing preview sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/v1/preview/stats")
async def get_preview_stats():
    """Obtener estadísticas generales del sistema de preview"""
    
    try:
        sessions = await live_preview_service.list_sessions()
        
        # Calcular estadísticas
        total_sessions = len(sessions)
        active_sessions = len([s for s in sessions if s["status"] == "running"])
        total_terminals = sum(s["terminals"] for s in sessions)
        active_terminals = sum(s["active_terminals"] for s in sessions)
        
        # Frameworks más populares
        frameworks = {}
        for session in sessions:
            framework = session["framework"]
            frameworks[framework] = frameworks.get(framework, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_terminals": total_terminals,
            "active_terminals": active_terminals,
            "frameworks": frameworks,
            "sessions": sessions[:10]  # Últimas 10 sesiones
        }
        
    except Exception as e:
        logger.error(f"Error getting preview stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/v1/preview/{session_id}/hot-reload")
async def trigger_hot_reload(session_id: str):
    """Forzar hot reload de una sesión de preview"""
    
    try:
        session = await live_preview_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Preview session not found")
        
        # Notificar a todas las terminales sobre hot reload
        for terminal_id in session.terminals:
            await live_preview_service._send_to_terminal(
                session_id, 
                terminal_id, 
                "\n[Hot reload triggered]\n"
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Hot reload triggered"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering hot reload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")