"""
Clase base para todas las herramientas del sistema.
Proporciona funcionalidades comunes como logging, sanitización y gestión de errores.
"""

import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolStatus(Enum):
    """Estados posibles para las herramientas"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class ToolResult:
    """Resultado de ejecución de herramienta"""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseTool(ABC):
    """Clase base para todas las herramientas del sistema"""
    
    def __init__(self, name: str, description: str, timeout: int = 30):
        self.name = name
        self.description = description
        self.timeout = timeout
        self.status = ToolStatus.IDLE
        self.start_time = None
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # Lista de patrones peligrosos para sanitización
        self.dangerous_patterns = [
            r'import\s+os',
            r'import\s+subprocess',
            r'import\s+sys',
            r'__import__',
            r'exec\(',
            r'eval\(',
            r'open\(',
            r'file\(',
            r'input\(',
            r'raw_input\(',
            r'compile\(',
            r'intern\(',
            r'breakpoint\(',
            r'help\(',
            r'vars\(',
            r'dir\(',
            r'locals\(',
            r'globals\(',
            r'__',
            r'globals',
            r'locals',
            r'frame',
            r'code'
        ]
    
    def sanitize_input(self, text: str, max_length: int = 1000) -> str:
        """
        Sanitiza la entrada de texto para prevenir inyección y contenido malicioso
        
        Args:
            text: Texto a sanitizar
            max_length: Longitud máxima permitida
            
        Returns:
            Texto sanitizado
        """
        if not isinstance(text, str):
            self.logger.warning(f"Entrada no es string: {type(text)}")
            return str(text)
        
        # Limitar longitud
        sanitized = text[:max_length]
        
        # Escapar caracteres especiales HTML
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Remover caracteres de control peligrosos
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)
        
        # Verificar patrones peligrosos
        for pattern in self.dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                self.logger.warning(f"Patrón peligroso detectado: {pattern}")
                sanitized = re.sub(pattern, '[BLOQUEADO]', sanitized)
        
        return sanitized.strip()
    
    def validate_url(self, url: str) -> bool:
        """
        Valida que una URL sea segura y accesible
        
        Args:
            url: URL a validar
            
        Returns:
            True si la URL es válida, False en caso contrario
        """
        if not isinstance(url, str):
            return False
        
        url = url.strip().lower()
        
        # Solo permitir HTTP y HTTPS
        if not (url.startswith('http://') or url.startswith('https://')):
            self.logger.warning(f"Protocolo no permitido: {url}")
            return False
        
        # Bloquear URLs con caracteres peligrosos
        dangerous_chars = ['<', '>', '"', "'", ';', '|', '&', '$', '`']
        if any(char in url for char in dangerous_chars):
            self.logger.warning(f"Caracteres peligrosos en URL: {url}")
            return False
        
        return True
    
    def set_running(self):
        """Marca la herramienta como en ejecución"""
        self.status = ToolStatus.RUNNING
        self.start_time = time.time()
        self.logger.info(f"Herramienta {self.name} iniciada")
    
    def set_completed(self):
        """Marca la herramienta como completada"""
        self.status = ToolStatus.COMPLETED
        self._log_execution_time()
    
    def set_failed(self, error: str):
        """Marca la herramienta como fallida"""
        self.status = ToolStatus.FAILED
        self._log_execution_time()
        self.logger.error(f"Herramienta {self.name} falló: {error}")
    
    def set_timeout(self):
        """Marca la herramienta como timeout"""
        self.status = ToolStatus.TIMEOUT
        self._log_execution_time()
        self.logger.warning(f"Herramienta {self.name} timeout")
    
    def _log_execution_time(self):
        """Registra el tiempo de ejecución"""
        if self.start_time:
            execution_time = time.time() - self.start_time
            self.logger.info(f"Tiempo de ejecución: {execution_time:.2f}s")
    
    def create_result(self, success: bool, data: Any = None, 
                     error: str = None, **metadata) -> ToolResult:
        """
        Crea un resultado estructurado
        
        Args:
            success: Si la operación fue exitosa
            data: Datos resultantes
            error: Mensaje de error si falló
            **metadata: Metadatos adicionales
            
        Returns:
            ToolResult con la información del resultado
        """
        execution_time = 0.0
        if self.start_time:
            execution_time = time.time() - self.start_time
        
        return ToolResult(
            success=success,
            data=data,
            error=error,
            execution_time=execution_time,
            metadata=metadata
        )
    
    def handle_exception(self, exception: Exception) -> ToolResult:
        """
        Maneja excepciones de forma consistente
        
        Args:
            exception: Excepción ocurrida
            
        Returns:
            ToolResult con información del error
        """
        self.set_failed(str(exception))
        
        # Log del traceback completo para debugging
        self.logger.exception("Excepción no manejada en herramienta")
        
        return self.create_result(
            success=False,
            error=str(exception),
            exception_type=type(exception).__name__
        )
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Ejecuta la funcionalidad específica de la herramienta
        
        Args:
            **kwargs: Argumentos específicos de la herramienta
            
        Returns:
            ToolResult con el resultado de la ejecución
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre la herramienta
        
        Returns:
            Diccionario con información de la herramienta
        """
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'timeout': self.timeout,
            'start_time': self.start_time
        }
    
    def __str__(self) -> str:
        return f"{self.name} ({self.status.value})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"