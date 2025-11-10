"""
Live Preview Service - Maneja la previsualización en tiempo real con WebContainers
y múltiples terminales para IRIS Agent
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol
import subprocess
import os
import tempfile
import shutil
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreviewStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    STOPPING = "stopping"

class ProcessStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"

@dataclass
class TerminalSession:
    terminal_id: str
    project_id: str
    websocket: Optional[WebSocketServerProtocol] = None
    cwd: str = "/workspace"
    env: Dict[str, str] = None
    status: ProcessStatus = ProcessStatus.STOPPED
    output_buffer: List[str] = None
    last_activity: datetime = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.env is None:
            self.env = {
                "PATH": "/usr/local/bin:/usr/bin:/bin",
                "HOME": "/root",
                "USER": "root",
                "TERM": "xterm-256color",
                "LANG": "en_US.UTF-8",
                "LC_ALL": "en_US.UTF-8"
            }
        if self.output_buffer is None:
            self.output_buffer = []
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class PreviewSession:
    session_id: str
    project_id: str
    status: PreviewStatus
    framework: str
    port: int = 3000
    url: str = None
    terminals: Dict[str, TerminalSession] = None
    files: Dict[str, str] = None
    created_at: datetime = None
    last_activity: datetime = None
    container_stats: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.terminals is None:
            self.terminals = {}
        if self.files is None:
            self.files = {}
        if self.container_stats is None:
            self.container_stats = {
                "uptime": 0,
                "memory": 0,
                "cpu": 0,
                "file_count": 0
            }
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.url is None:
            self.url = f"http://localhost:{self.port}"

class LivePreviewService:
    """Servicio principal para manejar previsualizaciones en vivo"""
    
    def __init__(self):
        self.sessions: Dict[str, PreviewSession] = {}
        self.websocket_connections: Dict[str, List[WebSocketServerProtocol]] = {}
        self.active_processes: Dict[str, subprocess.Popen] = {}
        
    async def create_session(self, session_id: str, project_id: str, 
                           framework: str, initial_files: Dict[str, str] = None) -> PreviewSession:
        """Crear una nueva sesión de preview"""
        try:
            session = PreviewSession(
                session_id=session_id,
                project_id=project_id,
                status=PreviewStatus.STARTING,
                framework=framework,
                files=initial_files or {}
            )
            
            self.sessions[session_id] = session
            self.websocket_connections[session_id] = []
            
            # Inicializar terminales por defecto
            await self._initialize_default_terminals(session_id)
            
            session.status = PreviewStatus.RUNNING
            session.last_activity = datetime.now()
            
            logger.info(f"Created preview session {session_id} for project {project_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            raise
    
    async def _initialize_default_terminals(self, session_id: str):
        """Inicializar terminales por defecto para una sesión"""
        default_terminals = [
            {
                "id": "main",
                "name": "Main Terminal",
                "type": "main",
                "cwd": "/workspace"
            },
            {
                "id": "build",
                "name": "Build Terminal",
                "type": "build", 
                "cwd": "/workspace"
            },
            {
                "id": "test",
                "name": "Test Terminal",
                "type": "test",
                "cwd": "/workspace"
            },
            {
                "id": "debug",
                "name": "Debug Terminal", 
                "type": "debug",
                "cwd": "/workspace"
            },
            {
                "id": "logs",
                "name": "Logs Terminal",
                "type": "logs",
                "cwd": "/workspace"
            }
        ]
        
        for terminal_config in default_terminals:
            terminal = TerminalSession(
                terminal_id=terminal_config["id"],
                project_id=self.sessions[session_id].project_id,
                cwd=terminal_config["cwd"]
            )
            self.sessions[session_id].terminals[terminal_config["id"]] = terminal
    
    async def get_session(self, session_id: str) -> Optional[PreviewSession]:
        """Obtener una sesión por ID"""
        return self.sessions.get(session_id)
    
    async def update_session_files(self, session_id: str, files: Dict[str, str]):
        """Actualizar archivos de una sesión"""
        if session_id in self.sessions:
            self.sessions[session_id].files.update(files)
            self.sessions[session_id].last_activity = datetime.now()
            
            # Notificar a conexiones WebSocket
            await self._broadcast_to_session(session_id, {
                "type": "files_updated",
                "files": files,
                "timestamp": datetime.now().isoformat()
            })
    
    async def create_terminal(self, session_id: str, terminal_config: Dict[str, Any]) -> TerminalSession:
        """Crear una nueva terminal en una sesión"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        terminal_id = terminal_config.get("id", f"custom_{int(time.time())}")
        
        terminal = TerminalSession(
            terminal_id=terminal_id,
            project_id=self.sessions[session_id].project_id,
            cwd=terminal_config.get("cwd", "/workspace")
        )
        
        self.sessions[session_id].terminals[terminal_id] = terminal
        logger.info(f"Created terminal {terminal_id} for session {session_id}")
        
        return terminal
    
    async def execute_command(self, session_id: str, terminal_id: str, 
                            command: str) -> bool:
        """Ejecutar comando en una terminal"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            if terminal_id not in session.terminals:
                return False
            
            terminal = session.terminals[terminal_id]
            
            # Simular ejecución de comando
            await self._simulate_command_execution(session_id, terminal_id, command)
            
            # Actualizar actividad
            terminal.last_activity = datetime.now()
            session.last_activity = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return False
    
    async def _simulate_command_execution(self, session_id: str, terminal_id: str, command: str):
        """Simular ejecución de comando y enviar output"""
        terminal = self.sessions[session_id].terminals[terminal_id]
        
        # Comando de ayuda
        if command == "help":
            output = """
=== Available Commands ===
help         - Show this help
clear        - Clear terminal  
status       - Show terminal status
pwd          - Print working directory
ls           - List files
cat <file>   - Show file content
npm install  - Install dependencies
npm run dev  - Start development server
npm run build - Build project
"""
        elif command == "clear":
            output = "\033[2J\033[H"  # Clear screen
        elif command == "status":
            output = f"""
=== Terminal Status ===
ID: {terminal_id}
Type: main
Connected: Yes
CWD: {terminal.cwd}
Session: {session_id}
"""
        elif command == "pwd":
            output = f"{terminal.cwd}\n"
        elif command == "ls":
            files = list(self.sessions[session_id].files.keys())
            output = "\n".join(files) if files else "No files in project\n"
        elif command == "npm install":
            output = """
📦 Installing dependencies...
✅ Dependencies installed successfully
"""
        elif command == "npm run dev":
            output = f"""
🚀 Starting development server...
⚡ Local: http://localhost:{self.sessions[session_id].port}
🌍 Network: http://0.0.0.0:{self.sessions[session_id].port}
Server running...
"""
        elif command == "npm run build":
            output = """
📦 Building project...
✅ Build completed successfully
📁 Output: dist/
"""
        else:
            output = f"""
bash: {command.split()[0]}: command not found
Type 'help' for available commands.
"""
        
        # Enviar output a la terminal
        await self._send_to_terminal(session_id, terminal_id, output)
    
    async def _send_to_terminal(self, session_id: str, terminal_id: str, output: str):
        """Enviar output a una terminal específica"""
        if session_id in self.sessions and terminal_id in self.sessions[session_id].terminals:
            terminal = self.sessions[session_id].terminals[terminal_id]
            terminal.output_buffer.append(output)
            
            # Limitar buffer
            if len(terminal.output_buffer) > 1000:
                terminal.output_buffer = terminal.output_buffer[-1000:]
            
            # Enviar a WebSocket si está conectado
            message = {
                "type": "terminal_output",
                "terminal_id": terminal_id,
                "output": output,
                "timestamp": datetime.now().isoformat()
            }
            await self._broadcast_to_terminal(session_id, terminal_id, message)
    
    async def _broadcast_to_terminal(self, session_id: str, terminal_id: str, message: Dict[str, Any]):
        """Enviar mensaje a una terminal específica"""
        if session_id in self.websocket_connections:
            # Buscar conexiones específicas de esta terminal
            message_str = json.dumps(message)
            for websocket in self.websocket_connections[session_id]:
                # Aquí se podría filtrar por terminal_id si se guarda en el websocket
                try:
                    await websocket.send(message_str)
                except Exception as e:
                    logger.warning(f"Failed to send message to websocket: {e}")
    
    async def _broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        """Enviar mensaje a todas las conexiones de una sesión"""
        if session_id in self.websocket_connections:
            message_str = json.dumps(message)
            for websocket in self.websocket_connections[session_id]:
                try:
                    await websocket.send(message_str)
                except Exception as e:
                    logger.warning(f"Failed to send message to websocket: {e}")
    
    async def connect_websocket(self, session_id: str, terminal_id: str, 
                              websocket: WebSocketServerProtocol):
        """Conectar WebSocket a una terminal"""
        if session_id in self.websocket_connections:
            self.websocket_connections[session_id].append(websocket)
            
            # Enviar saludo
            welcome_message = {
                "type": "terminal_connected",
                "terminal_id": terminal_id,
                "session_id": session_id,
                "message": f"Welcome to IRIS Agent Terminal - {terminal_id}",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(welcome_message))
            
            # Enviar buffer de output si existe
            if (session_id in self.sessions and 
                terminal_id in self.sessions[session_id].terminals):
                terminal = self.sessions[session_id].terminals[terminal_id]
                if terminal.output_buffer:
                    for output in terminal.output_buffer[-50:]:  # Últimos 50 outputs
                        await self._send_to_terminal(session_id, terminal_id, output)
    
    async def disconnect_websocket(self, session_id: str, websocket: WebSocketServerProtocol):
        """Desconectar WebSocket"""
        if session_id in self.websocket_connections:
            try:
                self.websocket_connections[session_id].remove(websocket)
            except ValueError:
                pass
    
    async def close_session(self, session_id: str):
        """Cerrar una sesión de preview"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.status = PreviewStatus.STOPPING
            
            # Cerrar todas las conexiones WebSocket
            if session_id in self.websocket_connections:
                for websocket in self.websocket_connections[session_id]:
                    try:
                        await websocket.close()
                    except Exception as e:
                        logger.warning(f"Failed to close websocket: {e}")
                del self.websocket_connections[session_id]
            
            # Terminar procesos activos
            for process in self.active_processes.values():
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    logger.warning(f"Failed to terminate process: {e}")
            
            self.active_processes.clear()
            
            # Remover sesión
            del self.sessions[session_id]
            
            logger.info(f"Closed preview session {session_id}")
    
    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de una sesión"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        
        # Calcular uptime
        uptime = (datetime.now() - session.created_at).total_seconds()
        
        # Simular uso de memoria y CPU
        import random
        memory_usage = random.randint(50, 200)  # MB
        cpu_usage = random.randint(5, 25)  # %
        
        return {
            "session_id": session_id,
            "project_id": session.project_id,
            "status": session.status.value,
            "framework": session.framework,
            "uptime": int(uptime),
            "terminals": len(session.terminals),
            "active_terminals": len([t for t in session.terminals.values() if t.status == ProcessStatus.RUNNING]),
            "files_count": len(session.files),
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "port": session.port,
            "url": session.url,
            "last_activity": session.last_activity.isoformat() if session.last_activity else None
        }
    
    async def cleanup_expired_sessions(self):
        """Limpiar sesiones expiradas"""
        cutoff_time = datetime.now() - timedelta(hours=1)  # 1 hora de inactividad
        
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if session.last_activity < cutoff_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            logger.info(f"Cleaning up expired session {session_id}")
            await self.close_session(session_id)
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """Listar todas las sesiones activas"""
        sessions = []
        for session_id, session in self.sessions.items():
            stats = await self.get_session_stats(session_id)
            sessions.append(stats)
        return sessions

# Instancia global del servicio
live_preview_service = LivePreviewService()

# Tarea de limpieza periódica
async def cleanup_task():
    """Tarea periódica para limpiar sesiones expiradas"""
    while True:
        try:
            await asyncio.sleep(300)  # Cada 5 minutos
            await live_preview_service.cleanup_expired_sessions()
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")

# Iniciar tarea de limpieza
async def start_cleanup_task():
    """Iniciar la tarea de limpieza en background"""
    asyncio.create_task(cleanup_task())