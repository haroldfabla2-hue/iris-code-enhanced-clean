"""
Sistema de herramientas básicas para el backend.
Incluye web scraping, ejecución de código Python, procesamiento de archivos y búsqueda web.
"""

try:
    # Intentar imports relativos (como paquete)
    from .base_tool import BaseTool, ToolResult, ToolStatus
    from .web_scraper import WebScraper
    from .python_executor import PythonExecutor
    from .file_processor import FileProcessor
    from .search_engine import SearchEngine
    from .tool_manager import ToolManager, get_tool_manager
except ImportError:
    # Imports absolutos (como módulo)
    from base_tool import BaseTool, ToolResult, ToolStatus
    from web_scraper import WebScraper
    from python_executor import PythonExecutor
    from file_processor import FileProcessor
    from search_engine import SearchEngine
    from tool_manager import ToolManager, get_tool_manager

__version__ = "1.0.0"
__all__ = [
    # Clases base
    'BaseTool',
    'ToolResult', 
    'ToolStatus',
    
    # Herramientas específicas
    'WebScraper',
    'PythonExecutor', 
    'FileProcessor',
    'SearchEngine',
    
    # Gestor
    'ToolManager',
    'get_tool_manager'
]

# Información de la versión
VERSION_INFO = {
    'version': __version__,
    'description': 'Sistema de herramientas básicas con seguridad y sandboxing',
    'tools': [
        'WebScraper - Scraping web seguro con BeautifulSoup',
        'PythonExecutor - Ejecución segura de código Python',
        'FileProcessor - Procesamiento de archivos PDF/DOCX/TXT',
        'SearchEngine - Búsqueda web con APIs públicas'
    ],
    'features': [
        'Sandboxing y sanitización de entrada',
        'Gestión de timeouts y errores',
        'Ejecución concurrente de herramientas',
        'Historial y estadísticas de uso',
        'Verificación de salud del sistema'
    ]
}

def get_version_info():
    """Obtiene información detallada de la versión"""
    return VERSION_INFO.copy()

def list_available_tools():
    """Lista las herramientas disponibles en el sistema"""
    return [
        {
            'name': 'web_scraper',
            'class': 'WebScraper',
            'description': 'Scraping web seguro usando BeautifulSoup',
            'capabilities': ['scrape_url', 'extract_links', 'extract_text', 'scrape_multiple_urls']
        },
        {
            'name': 'python_executor', 
            'class': 'PythonExecutor',
            'description': 'Ejecución segura de código Python con restricciones',
            'capabilities': ['execute_code', 'execute_function', 'test_code_safety']
        },
        {
            'name': 'file_processor',
            'class': 'FileProcessor', 
            'description': 'Procesamiento de archivos PDF, DOCX, TXT y más',
            'capabilities': ['read_text_file', 'extract_pdf_text', 'extract_docx_text', 'process_file']
        },
        {
            'name': 'search_engine',
            'class': 'SearchEngine',
            'description': 'Búsqueda web usando DuckDuckGo y Wikipedia APIs',
            'capabilities': ['duckduckgo_search', 'wikipedia_search', 'web_search', 'wikipedia_page']
        }
    ]

def initialize_tools():
    """Inicializa todas las herramientas del sistema"""
    from tool_manager import get_tool_manager
    
    manager = get_tool_manager()
    tools_info = manager.list_tools()
    
    return {
        'initialized': len(tools_info),
        'tools': tools_info,
        'status': 'ready'
    }

# Configuración por defecto del sistema
DEFAULT_CONFIG = {
    'max_execution_time': 300,  # 5 minutos
    'max_file_size': 10485760,  # 10MB
    'allowed_file_types': ['.txt', '.pdf', '.docx', '.csv', '.json', '.html', '.md'],
    'max_concurrent_tools': 5,
    'enable_logging': True,
    'log_level': 'INFO'
}

def get_default_config():
    """Obtiene la configuración por defecto del sistema"""
    return DEFAULT_CONFIG.copy()

# Ejemplo de uso básico
def example_usage():
    """Ejemplo básico de uso del sistema de herramientas"""
    examples = {
        'web_scraping': {
            'tool': 'web_scraper',
            'args': {
                'operation': 'scrape',
                'url': 'https://example.com'
            }
        },
        'python_execution': {
            'tool': 'python_executor', 
            'args': {
                'operation': 'execute',
                'code': 'print("Hola mundo")'
            }
        },
        'file_processing': {
            'tool': 'file_processor',
            'args': {
                'operation': 'text',
                'file_path': '/path/to/file.txt'
            }
        },
        'web_search': {
            'tool': 'search_engine',
            'args': {
                'operation': 'web_search',
                'query': 'python programming'
            }
        }
    }
    return examples