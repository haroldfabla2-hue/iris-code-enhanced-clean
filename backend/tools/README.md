# Sistema de Herramientas Básicas

Sistema modular de herramientas para el backend con funcionalidades de web scraping, ejecución segura de código Python, procesamiento de archivos y búsqueda web.

## 🛠️ Herramientas Disponibles

### 1. WebScraper
**Scraping web seguro usando BeautifulSoup**

- Extracción de contenido de páginas web
- Limpieza automática de HTML (remoción de scripts)
- Extracción de enlaces e imágenes
- Soporte para múltiples URLs
- Validación de dominios permitidos

```python
from tools import get_tool_manager

manager = get_tool_manager()

# Scraping básico
result = manager.execute_tool('web_scraper', 
    operation='scrape', 
    url='https://example.com'
)

# Extraer solo texto
result = manager.execute_tool('web_scraper',
    operation='extract_text',
    url='https://example.com'
)

# Scraping de múltiples URLs
result = manager.execute_tool('web_scraper',
    operation='scrape',
    urls=['https://site1.com', 'https://site2.com']
)
```

### 2. PythonExecutor
**Ejecución segura de código Python con sandboxing**

- Análisis AST de seguridad
- Restricción de módulos peligrosos
- Timeout automático
- Captura de output
- Testing de seguridad sin ejecución

```python
# Ejecutar código seguro
result = manager.execute_tool('python_executor',
    operation='execute',
    code='print("Hola mundo")\nresult = 2 + 2\nprint(f"Resultado: {result}")'
)

# Probar seguridad sin ejecutar
result = manager.execute_tool('python_executor',
    operation='test_safety',
    code='import os'  # Esto será bloqueado
)

# Ejecutar función
result = manager.execute_tool('python_executor',
    operation='execute_function',
    function_code='def suma(a, b): return a + b',
    function_name='suma',
    args={'a': 5, 'b': 3}
)
```

### 3. FileProcessor
**Procesamiento de archivos PDF, DOCX, TXT y más**

- Extracción de texto de PDFs
- Procesamiento de documentos DOCX
- Lectura de archivos de texto con detección de encoding
- Procesamiento de JSON y CSV
- Validación de tipos de archivo

```python
# Procesar archivo automáticamente
result = manager.execute_tool('file_processor',
    operation='auto',
    file_path='/path/to/document.pdf'
)

# Leer archivo de texto
result = manager.execute_tool('file_processor',
    operation='text',
    file_path='/path/to/file.txt'
)

# Extraer texto de PDF
result = manager.execute_tool('file_processor',
    operation='pdf',
    file_path='/path/to/document.pdf'
)

# Procesar archivo DOCX
result = manager.execute_tool('file_processor',
    operation='docx',
    file_path='/path/to/document.docx'
)
```

### 4. SearchEngine
**Búsqueda web usando DuckDuckGo y Wikipedia APIs**

- Búsqueda en DuckDuckGo
- Búsqueda en Wikipedia
- Búsqueda web consolidada
- Obtención de páginas específicas de Wikipedia

```python
# Búsqueda web consolidada
result = manager.execute_tool('search_engine',
    operation='web_search',
    query='inteligencia artificial',
    sources=['duckduckgo', 'wikipedia']
)

# Búsqueda específica en DuckDuckGo
result = manager.execute_tool('search_engine',
    operation='duckduckgo',
    query='python programming',
    safe_search=True
)

# Búsqueda en Wikipedia
result = manager.execute_tool('search_engine',
    operation='wikipedia',
    query='machine learning',
    limit=5
)

# Obtener página específica de Wikipedia
result = manager.execute_tool('search_engine',
    operation='wikipedia_page',
    title='Python (lenguaje de programación)'
)
```

## 🔐 Características de Seguridad

### Sandboxing
- **PythonExecutor**: Restricción de módulos peligrosos, análisis AST, límites de tiempo y memoria
- **WebScraper**: Validación de URLs, restricción de dominios, limpieza de HTML
- **FileProcessor**: Validación de tipos MIME, límites de tamaño, sanitización de rutas

### Sanitización
- Limpieza automática de entrada de usuario
- Remoción de código malicioso
- Validación de parámetros
- Escape de caracteres especiales

### Monitoreo
- Logging detallado de todas las operaciones
- Tracking de tiempo de ejecución
- Estadísticas de uso y éxito/fallo
- Health checks del sistema

## 🚀 Uso Avanzado

### Ejecución Concurrente

```python
# Ejecutar múltiples herramientas en paralelo
executions = [
    {'tool': 'web_scraper', 'args': {'operation': 'scrape', 'url': 'https://site1.com'}},
    {'tool': 'search_engine', 'args': {'operation': 'web_search', 'query': 'python'}},
    {'tool': 'file_processor', 'args': {'operation': 'text', 'file_path': 'data.txt'}}
]

results = manager.execute_multiple_tools(executions, parallel=True)
```

### Estadísticas y Monitoreo

```python
# Obtener estadísticas
stats = manager.get_tool_statistics()
print(f"Total de ejecuciones: {stats['total_executions']}")

# Historial de ejecuciones
history = manager.get_execution_history(limit=10, successful_only=True)

# Health check del sistema
health = manager.health_check()
print(f"Estado general: {health['overall_status']}")
```

### Gestión de Herramientas

```python
# Listar herramientas disponibles
tools = manager.list_tools()

# Obtener información específica de una herramienta
web_scraper = manager.get_tool('web_scraper')
print(web_scraper.get_info())

# Reiniciar estadísticas
manager.reset_tool_stats('web_scraper')
```

## 📁 Estructura del Proyecto

```
/workspace/backend/tools/
├── __init__.py              # Inicialización del paquete
├── base_tool.py             # Clase base y funcionalidades comunes
├── web_scraper.py           # Herramienta de web scraping
├── python_executor.py       # Ejecutor seguro de Python
├── file_processor.py        # Procesador de archivos
├── search_engine.py         # Motor de búsqueda
├── tool_manager.py          # Gestor central de herramientas
├── requirements.txt         # Dependencias
└── README.md               # Esta documentación
```

## ⚙️ Configuración

### Configuración por Defecto

```python
from tools import get_default_config

config = get_default_config()
print(config)
```

### Configuración Personalizada

```python
from tools import ToolManager

# Crear manager con configuración personalizada
manager = ToolManager(max_workers=3)

# Configurar herramientas específicas
web_scraper = manager.get_tool('web_scraper')
web_scraper.set_allowed_domains(['example.com', 'trusted-site.org'])
```

## 🔧 Instalación

1. Instalar dependencias:
```bash
cd /workspace/backend/tools
pip install -r requirements.txt
```

2. Importar y usar:
```python
from tools import get_tool_manager

# Obtener instancia del manager
manager = get_tool_manager()

# Usar herramientas
result = manager.execute_tool('web_scraper', operation='scrape', url='https://example.com')
```

## 📊 Métricas y Logging

El sistema incluye logging completo y métricas:

- **Ejecución**: Tiempo, éxito/fallo, errores
- **Rendimiento**: Tiempo promedio por herramienta
- **Uso**: Frecuencia de uso de cada herramienta
- **Salud**: Estado general del sistema

```python
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.INFO)

# Obtener métricas detalladas
detailed_stats = manager.get_tool_statistics()
```

## 🚨 Limitaciones de Seguridad

- **PythonExecutor**: No permite imports de módulos del sistema
- **WebScraper**: Solo permite HTTP/HTTPS, dominios configurables
- **FileProcessor**: Tipos de archivo y tamaños limitados
- **Timeouts**: Todas las operaciones tienen límite de tiempo

## 🛡️ Mejores Prácticas

1. **Siempre validar entrada** del usuario antes de procesar
2. **Usar timeouts apropiados** para evitar bloqueos
3. **Monitorear estadísticas** de uso y rendimiento
4. **Implementar logging** para auditoría
5. **Configurar dominios permitidos** en web scraping
6. **Validar tipos de archivo** antes de procesamiento

## 📝 Ejemplos Completos

Ver el archivo de ejemplos en `__init__.py` para casos de uso completos.

## 🔄 Versión y Compatibilidad

- **Versión**: 1.0.0
- **Python**: 3.8+
- **Dependencias**: Ver requirements.txt

---

**Nota**: Este sistema está diseñado para ser seguro y estable. Todas las herramientas incluyen validaciones y restricciones para prevenir uso malicioso.