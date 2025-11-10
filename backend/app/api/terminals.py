"""
Terminal API - Endpoints WebSocket para terminales en tiempo real
"""

import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from pydantic import BaseModel
import asyncio
import uuid
from datetime import datetime

from app.services.live_preview_service import live_preview_service, TerminalSession, ProcessStatus

logger = logging.getLogger(__name__)

router = APIRouter()

# Modelos Pydantic
class CreateTerminalRequest(BaseModel):
    name: str
    type: str = "custom"
    cwd: str = "/workspace"
    env: Optional[dict] = None

class CommandRequest(BaseModel):
    command: str
    terminal_id: str

class TerminalResponse(BaseModel):
    terminal_id: str
    session_id: str
    name: str
    type: str
    status: str
    cwd: str
    created_at: str

@router.websocket("/ws/{session_id}/{terminal_id}")
async def websocket_terminal_endpoint(
    websocket: WebSocket,
    session_id: str,
    terminal_id: str
):
    """Endpoint WebSocket para terminal en tiempo real"""
    
    # Verificar que la sesión existe
    session = await live_preview_service.get_session(session_id)
    if not session:
        await websocket.close(code=4000, reason="Session not found")
        return
    
    # Verificar que la terminal existe
    if terminal_id not in session.terminals:
        await websocket.close(code=4001, reason="Terminal not found")
        return
    
    # Aceptar conexión WebSocket
    await websocket.accept()
    
    # Conectar terminal al WebSocket
    terminal = session.terminals[terminal_id]
    terminal.websocket = websocket
    
    try:
        # Registrar conexión
        await live_preview_service.connect_websocket(session_id, terminal_id, websocket)
        
        # Enviar información inicial de la terminal
        terminal_info = {
            "type": "terminal_info",
            "terminal_id": terminal_id,
            "session_id": session_id,
            "name": terminal.terminal_id,
            "type": "main",
            "status": terminal.status.value,
            "cwd": terminal.cwd,
            "created_at": terminal.created_at.isoformat() if terminal.created_at else None
        }
        await websocket.send_json(terminal_info)
        
        # Manejar mensajes del cliente
        async for message in websocket.iter_text():
            try:
                data = json.loads(message)
                await handle_terminal_message(session_id, terminal_id, data, websocket)
            except json.JSONDecodeError:
                error_msg = {
                    "type": "error",
                    "message": "Invalid JSON message"
                }
                await websocket.send_json(error_msg)
            except Exception as e:
                logger.error(f"Error handling terminal message: {e}")
                error_msg = {
                    "type": "error", 
                    "message": f"Internal server error: {str(e)}"
                }
                await websocket.send_json(error_msg)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}, terminal {terminal_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}, terminal {terminal_id}: {e}")
    finally:
        # Desconectar terminal
        await live_preview_service.disconnect_websocket(session_id, websocket)
        terminal.websocket = None
        terminal.status = ProcessStatus.STOPPED

async def handle_terminal_message(session_id: str, terminal_id: str, data: dict, websocket: WebSocket):
    """Manejar mensajes recibidos de la terminal"""
    
    message_type = data.get("type")
    
    if message_type == "command":
        command = data.get("command", "").strip()
        if not command:
            return
        
        # Marcar terminal como activa
        terminal = live_preview_service.sessions[session_id].terminals[terminal_id]
        terminal.status = ProcessStatus.STARTING
        terminal.last_activity = datetime.now()
        
        # Ejecutar comando
        success = await live_preview_service.execute_command(session_id, terminal_id, command)
        
        if not success:
            error_msg = {
                "type": "error",
                "message": "Failed to execute command"
            }
            await websocket.send_json(error_msg)
            
    elif message_type == "break":
        # Interrumpir proceso en ejecución
        await send_to_terminal(session_id, terminal_id, "\n[Break signal sent]\n")
        
    elif message_type == "resize":
        # Redimensionar terminal
        cols = data.get("cols", 80)
        rows = data.get("rows", 24)
        
        resize_msg = {
            "type": "terminal_resized",
            "cols": cols,
            "rows": rows
        }
        await websocket.send_json(resize_msg)
        
    elif message_type == "ping":
        # Ping/pong para mantener conexión
        await websocket.send_json({"type": "pong"})
        
    elif message_type == "clear":
        # Limpiar terminal
        clear_output = "\033[2J\033[H"
        await send_to_terminal(session_id, terminal_id, clear_output)
        
    else:
        # Tipo de mensaje desconocido
        error_msg = {
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }
        await websocket.send_json(error_msg)

async def send_to_terminal(session_id: str, terminal_id: str, message: str):
    """Enviar mensaje a una terminal específica"""
    await live_preview_service._send_to_terminal(session_id, terminal_id, message)

@router.post("/api/v1/terminals/{project_id}/{session_id}")
async def create_terminal(
    project_id: str,
    session_id: str,
    request: CreateTerminalRequest
):
    """Crear una nueva terminal en una sesión"""
    
    try:
        # Crear configuración de terminal
        terminal_config = {
            "id": f"terminal_{uuid.uuid4().hex[:8]}",
            "name": request.name,
            "type": request.type,
            "cwd": request.cwd,
            "env": request.env or {}
        }
        
        # Crear terminal
        terminal = await live_preview_service.create_terminal(session_id, terminal_config)
        
        # Respuesta
        response = TerminalResponse(
            terminal_id=terminal.terminal_id,
            session_id=session_id,
            name=terminal.terminal_id,
            type=request.type,
            status=terminal.status.value,
            cwd=terminal.cwd,
            created_at=terminal.created_at.isoformat() if terminal.created_at else None
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating terminal: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/v1/terminals/{project_id}/{session_id}")
async def list_terminals(project_id: str, session_id: str):
    """Listar todas las terminales de una sesión"""
    
    try:
        session = await live_preview_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        terminals = []
        for terminal_id, terminal in session.terminals.items():
            terminals.append({
                "terminal_id": terminal_id,
                "name": terminal.terminal_id,
                "type": "main",  # Default type
                "status": terminal.status.value,
                "cwd": terminal.cwd,
                "created_at": terminal.created_at.isoformat() if terminal.created_at else None,
                "last_activity": terminal.last_activity.isoformat() if terminal.last_activity else None,
                "output_count": len(terminal.output_buffer)
            })
        
        return {
            "session_id": session_id,
            "terminals": terminals,
            "total": len(terminals)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing terminals: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/v1/terminals/{project_id}/{session_id}/{terminal_id}")
async def get_terminal_info(
    project_id: str,
    session_id: str,
    terminal_id: str
):
    """Obtener información detallada de una terminal"""
    
    try:
        session = await live_preview_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if terminal_id not in session.terminals:
            raise HTTPException(status_code=404, detail="Terminal not found")
        
        terminal = session.terminals[terminal_id]
        
        return {
            "terminal_id": terminal_id,
            "session_id": session_id,
            "project_id": project_id,
            "name": terminal.terminal_id,
            "type": "main",
            "status": terminal.status.value,
            "cwd": terminal.cwd,
            "env": terminal.env,
            "created_at": terminal.created_at.isoformat() if terminal.created_at else None,
            "last_activity": terminal.last_activity.isoformat() if terminal.last_activity else None,
            "output_count": len(terminal.output_buffer),
            "is_connected": terminal.websocket is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting terminal info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/v1/terminals/{project_id}/{session_id}/{terminal_id}/execute")
async def execute_command(
    project_id: str,
    session_id: str,
    terminal_id: str,
    request: CommandRequest
):
    """Ejecutar comando en una terminal (HTTP alternativa a WebSocket)"""
    
    try:
        success = await live_preview_service.execute_command(
            session_id, terminal_id, request.command
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to execute command")
        
        return {
            "success": True,
            "command": request.command,
            "terminal_id": terminal_id,
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/api/v1/terminals/{project_id}/{session_id}/{terminal_id}")
async def delete_terminal(
    project_id: str,
    session_id: str,
    terminal_id: str
):
    """Eliminar una terminal (no permite eliminar terminal principal)"""
    
    try:
        session = await live_preview_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if terminal_id not in session.terminals:
            raise HTTPException(status_code=404, detail="Terminal not found")
        
        # No permitir eliminar terminal principal
        if terminal_id == "main":
            raise HTTPException(status_code=400, detail="Cannot delete main terminal")
        
        # Cerrar WebSocket si está conectado
        terminal = session.terminals[terminal_id]
        if terminal.websocket:
            try:
                await terminal.websocket.close()
            except Exception as e:
                logger.warning(f"Failed to close websocket: {e}")
        
        # Eliminar terminal
        del session.terminals[terminal_id]
        
        return {
            "success": True,
            "terminal_id": terminal_id,
            "message": "Terminal deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting terminal: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/v1/terminals/stats")
async def get_terminals_stats():
    """Obtener estadísticas generales de terminales"""
    
    try:
        sessions = await live_preview_service.list_sessions()
        
        total_terminals = 0
        active_terminals = 0
        total_sessions = len(sessions)
        active_sessions = 0
        
        for session in sessions:
            if session["status"] == "running":
                active_sessions += 1
            total_terminals += session["terminals"]
            active_terminals += session["active_terminals"]
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_terminals": total_terminals,
            "active_terminals": active_terminals,
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"Error getting terminals stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")