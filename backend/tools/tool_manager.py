"""
Gestor principal de herramientas del sistema.
Coordina y gestiona todas las herramientas disponibles de forma centralizada.
"""

import time
import logging
from typing import Dict, List, Any, Optional, Type, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps

from .base_tool import BaseTool, ToolResult, ToolStatus
from .web_scraper import WebScraper
from .python_executor import PythonExecutor
from .file_processor import FileProcessor
from .search_engine import SearchEngine

# Configurar logging
logger = logging.getLogger(__name__)

class ToolManagerError(Exception):
    """Error específico del gestor de herramientas"""
    pass

class ToolNotFoundError(ToolManagerError):
    """Error cuando una herramienta no se encuentra"""
    pass

class ToolExecutionError(ToolManagerError):
    """Error en la ejecución de herramientas"""
    pass

class ToolManager:
    """Gestor central de todas las herramientas del sistema"""
    
    def __init__(self, max_workers: int = 5):
        """
        Inicializa el gestor de herramientas
        
        Args:
            max_workers: Número máximo de workers para ejecución concurrente
        """
        self.max_workers = max_workers
        self.tools: Dict[str, BaseTool] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.tool_stats: Dict[str, Dict[str, Any]] = {}
        
        # Inicializar herramientas disponibles
        self._register_default_tools()
        
        logger.info(f"ToolManager inicializado con {len(self.tools)} herramientas")
    
    def _register_default_tools(self):
        """Registra las herramientas predeterminadas del sistema"""
        try:
            # Web Scraper
            self.register_tool(WebScraper(), "web_scraper")
            
            # Python Executor
            self.register_tool(PythonExecutor(), "python_executor")
            
            # File Processor
            self.register_tool(FileProcessor(), "file_processor")
            
            # Search Engine
            self.register_tool(SearchEngine(), "search_engine")
            
            logger.info("Herramientas predeterminadas registradas correctamente")
            
        except Exception as e:
            logger.error(f"Error registrando herramientas predeterminadas: {e}")
            raise
    
    def register_tool(self, tool: BaseTool, name: Optional[str] = None) -> None:
        """
        Registra una nueva herramienta
        
        Args:
            tool: Instancia de la herramienta
            name: Nombre opcional para la herramienta (por defecto usa tool.name)
            
        Raises:
            ToolManagerError: Si la herramienta ya existe o es inválida
        """
        if not isinstance(tool, BaseTool):
            raise ToolManagerError("La herramienta debe ser una instancia de BaseTool")
        
        tool_name = name or tool.name
        
        if tool_name in self.tools:
            raise ToolManagerError(f"La herramienta '{tool_name}' ya está registrada")
        
        # Validar que la herramienta tenga los métodos necesarios
        required_methods = ['execute', 'get_info', 'sanitize_input']
        for method in required_methods:
            if not hasattr(tool, method):
                raise ToolManagerError(f"La herramienta no tiene el método requerido: {method}")
        
        self.tools[tool_name] = tool
        self.tool_stats[tool_name] = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0,
            'last_execution': None
        }
        
        logger.info(f"Herramienta '{tool_name}' registrada correctamente")
    
    def unregister_tool(self, name: str) -> bool:
        """
        Desregistra una herramienta
        
        Args:
            name: Nombre de la herramienta
            
        Returns:
            True si se desregistró correctamente, False si no existía
        """
        if name in self.tools:
            del self.tools[name]
            if name in self.tool_stats:
                del self.tool_stats[name]
            logger.info(f"Herramienta '{name}' desregistrada")
            return True
        return False
    
    def get_tool(self, name: str) -> BaseTool:
        """
        Obtiene una herramienta por nombre
        
        Args:
            name: Nombre de la herramienta
            
        Returns:
            Instancia de la herramienta
            
        Raises:
            ToolNotFoundError: Si la herramienta no existe
        """
        if name not in self.tools:
            raise ToolNotFoundError(f"Herramienta '{name}' no encontrada")
        
        return self.tools[name]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lista todas las herramientas disponibles
        
        Returns:
            Lista con información de las herramientas
        """
        tools_info = []
        
        for name, tool in self.tools.items():
            tool_info = tool.get_info()
            tool_info['statistics'] = self.tool_stats.get(name, {})
            tools_info.append(tool_info)
        
        return tools_info
    
    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """
        Ejecuta una herramienta específica
        
        Args:
            name: Nombre de la herramienta
            **kwargs: Argumentos para la herramienta
            
        Returns:
            ToolResult con el resultado de la ejecución
            
        Raises:
            ToolNotFoundError: Si la herramienta no existe
            ToolExecutionError: Si hay error en la ejecución
        """
        if name not in self.tools:
            raise ToolNotFoundError(f"Herramienta '{name}' no encontrada")
        
        tool = self.tools[name]
        start_time = time.time()
        
        try:
            logger.info(f"Ejecutando herramienta '{name}' con argumentos: {list(kwargs.keys())}")
            
            # Ejecutar herramienta
            result = tool.execute(**kwargs)
            
            # Actualizar estadísticas
            self._update_tool_stats(name, result, time.time() - start_time)
            
            # Registrar en historial
            self._add_to_history(name, kwargs, result, start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error ejecutando herramienta '{name}': {e}")
            error_result = ToolResult(
                success=False,
                error=f"Error en ejecución: {str(e)}",
                execution_time=time.time() - start_time
            )
            
            self._update_tool_stats(name, error_result, time.time() - start_time)
            self._add_to_history(name, kwargs, error_result, start_time)
            
            raise ToolExecutionError(f"Error ejecutando herramienta '{name}': {str(e)}") from e
    
    def execute_multiple_tools(self, executions: List[Dict[str, Any]], 
                              parallel: bool = True) -> Dict[str, ToolResult]:
        """
        Ejecuta múltiples herramientas
        
        Args:
            executions: Lista de ejecuciones con formato {'tool': 'nombre', 'args': {...}}
            parallel: Si ejecutar en paralelo
            
        Returns:
            Diccionario con resultados por herramienta
        """
        results = {}
        
        if not executions:
            return results
        
        if parallel and len(executions) > 1:
            results = self._execute_parallel(executions)
        else:
            results = self._execute_sequential(executions)
        
        return results
    
    def _execute_sequential(self, executions: List[Dict[str, Any]]) -> Dict[str, ToolResult]:
        """Ejecuta herramientas secuencialmente"""
        results = {}
        
        for i, execution in enumerate(executions):
            tool_name = execution.get('tool')
            args = execution.get('args', {})
            identifier = execution.get('id', f"execution_{i}")
            
            try:
                result = self.execute_tool(tool_name, **args)
                results[identifier] = result
            except Exception as e:
                results[identifier] = ToolResult(
                    success=False,
                    error=f"Error en ejecución: {str(e)}"
                )
        
        return results
    
    def _execute_parallel(self, executions: List[Dict[str, Any]]) -> Dict[str, ToolResult]:
        """Ejecuta herramientas en paralelo"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Enviar todas las tareas
            future_to_execution = {}
            
            for i, execution in enumerate(executions):
                tool_name = execution.get('tool')
                args = execution.get('args', {})
                identifier = execution.get('id', f"execution_{i}")
                
                future = executor.submit(self.execute_tool, tool_name, **args)
                future_to_execution[future] = identifier
            
            # Recoger resultados
            for future in as_completed(future_to_execution):
                identifier = future_to_execution[future]
                
                try:
                    result = future.result()
                    results[identifier] = result
                except Exception as e:
                    results[identifier] = ToolResult(
                        success=False,
                        error=f"Error en ejecución paralela: {str(e)}"
                    )
        
        return results
    
    def _update_tool_stats(self, tool_name: str, result: ToolResult, execution_time: float):
        """Actualiza estadísticas de una herramienta"""
        if tool_name not in self.tool_stats:
            self.tool_stats[tool_name] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'total_execution_time': 0.0,
                'average_execution_time': 0.0,
                'last_execution': None
            }
        
        stats = self.tool_stats[tool_name]
        stats['total_executions'] += 1
        stats['total_execution_time'] += execution_time
        stats['last_execution'] = time.time()
        
        if result.success:
            stats['successful_executions'] += 1
        else:
            stats['failed_executions'] += 1
        
        # Calcular promedio
        if stats['total_executions'] > 0:
            stats['average_execution_time'] = stats['total_execution_time'] / stats['total_executions']
    
    def _add_to_history(self, tool_name: str, args: Dict, result: ToolResult, start_time: float):
        """Añade ejecución al historial"""
        history_entry = {
            'timestamp': start_time,
            'tool_name': tool_name,
            'args': args,
            'success': result.success,
            'execution_time': result.execution_time,
            'error': result.error
        }
        
        # Mantener solo las últimas 1000 entradas
        self.execution_history.append(history_entry)
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de todas las herramientas
        
        Returns:
            Diccionario con estadísticas de herramientas
        """
        return {
            'tools': self.tool_stats,
            'total_tools': len(self.tools),
            'total_executions': len(self.execution_history),
            'recent_executions': len([h for h in self.execution_history if time.time() - h['timestamp'] < 3600])  # Última hora
        }
    
    def get_execution_history(self, limit: int = 100, 
                             tool_name: Optional[str] = None,
                             successful_only: bool = False) -> List[Dict[str, Any]]:
        """
        Obtiene historial de ejecuciones
        
        Args:
            limit: Límite de entradas a devolver
            tool_name: Filtrar por nombre de herramienta
            successful_only: Solo mostrar ejecuciones exitosas
            
        Returns:
            Lista de entradas del historial
        """
        filtered_history = self.execution_history
        
        if tool_name:
            filtered_history = [h for h in filtered_history if h['tool_name'] == tool_name]
        
        if successful_only:
            filtered_history = [h for h in filtered_history if h['success']]
        
        # Devolver las más recientes
        return filtered_history[-limit:]
    
    def health_check(self) -> Dict[str, Any]:
        """
        Realiza verificación de salud de todas las herramientas
        
        Returns:
            Estado de salud de las herramientas
        """
        health_status = {
            'timestamp': time.time(),
            'overall_status': 'healthy',
            'tools': {},
            'issues': []
        }
        
        for name, tool in self.tools.items():
            tool_health = {
                'name': name,
                'status': tool.status.value,
                'responsive': True,
                'issues': []
            }
            
            # Verificar si la herramienta responde
            try:
                info = tool.get_info()
                if info['status'] == ToolStatus.FAILED.value:
                    tool_health['issues'].append('Última ejecución falló')
                    tool_health['responsive'] = False
                
            except Exception as e:
                tool_health['responsive'] = False
                tool_health['issues'].append(f'Error obteniendo info: {str(e)}')
            
            # Verificar estadísticas
            if name in self.tool_stats:
                stats = self.tool_stats[name]
                if stats['total_executions'] > 0:
                    success_rate = stats['successful_executions'] / stats['total_executions']
                    if success_rate < 0.5:  # Menos del 50% de éxito
                        tool_health['issues'].append(f'Tasa de éxito baja: {success_rate:.2%}')
                        tool_health['responsive'] = False
            
            health_status['tools'][name] = tool_health
            
            if not tool_health['responsive']:
                health_status['overall_status'] = 'unhealthy'
                health_status['issues'].extend([f"{name}: {issue}" for issue in tool_health['issues']])
        
        return health_status
    
    def reset_tool_stats(self, tool_name: Optional[str] = None):
        """
        Reinicia estadísticas de herramientas
        
        Args:
            tool_name: Herramienta específica o None para todas
        """
        if tool_name:
            if tool_name in self.tool_stats:
                self.tool_stats[tool_name] = {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'failed_executions': 0,
                    'total_execution_time': 0.0,
                    'average_execution_time': 0.0,
                    'last_execution': None
                }
                logger.info(f"Estadísticas de '{tool_name}' reiniciadas")
        else:
            for name in self.tool_stats:
                self.tool_stats[name] = {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'failed_executions': 0,
                    'total_execution_time': 0.0,
                    'average_execution_time': 0.0,
                    'last_execution': None
                }
            logger.info("Todas las estadísticas de herramientas reiniciadas")
    
    def cleanup(self):
        """Limpia recursos del gestor"""
        logger.info("Limpiando ToolManager...")
        
        # Reiniciar estadísticas
        self.reset_tool_stats()
        
        # Limpiar historial
        self.execution_history.clear()
        
        logger.info("ToolManager limpiado correctamente")

# Instancia global del gestor de herramientas
_global_tool_manager = None

def get_tool_manager() -> ToolManager:
    """
    Obtiene la instancia global del gestor de herramientas
    
    Returns:
        Instancia global de ToolManager
    """
    global _global_tool_manager
    if _global_tool_manager is None:
        _global_tool_manager = ToolManager()
    return _global_tool_manager

def reset_tool_manager():
    """Reinicia la instancia global del gestor de herramientas"""
    global _global_tool_manager
    if _global_tool_manager is not None:
        _global_tool_manager.cleanup()
    _global_tool_manager = None