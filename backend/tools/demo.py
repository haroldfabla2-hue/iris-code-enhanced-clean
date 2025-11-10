#!/usr/bin/env python3
"""
Demo y ejemplos de uso del sistema de herramientas básicas.
Muestra las capacidades de cada herramienta con ejemplos prácticos.
"""

import time
import sys
import os

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import get_tool_manager, list_available_tools

def print_separator(title="", char="=", width=80):
    """Imprime un separador decorativo"""
    if title:
        spaces = (width - len(title) - 2) // 2
        print(f"{char * spaces} {title} {char * spaces}")
    else:
        print(char * width)

def print_result(result, operation_name):
    """Imprime el resultado de una operación de forma formateada"""
    print(f"\n--- Resultado de {operation_name} ---")
    
    if result.success:
        print("✅ ÉXITO")
        if hasattr(result, 'data') and result.data:
            print(f"📊 Datos: {result.data}")
        if hasattr(result, 'execution_time'):
            print(f"⏱️  Tiempo: {result.execution_time:.2f}s")
    else:
        print("❌ ERROR")
        print(f"🚫 Error: {result.error}")
    
    print("-" * 50)

def demo_web_scraper():
    """Demuestra las funcionalidades del web scraper"""
    print_separator("DEMO: Web Scraper", "🕷️")
    
    manager = get_tool_manager()
    
    # Ejemplo 1: Scraping básico
    print("\n1. Scraping básico de una página web")
    result = manager.execute_tool('web_scraper',
        operation='scrape',
        url='https://httpbin.org/html'
    )
    print_result(result, "Web Scraping")
    
    # Ejemplo 2: Extracción de texto
    print("\n2. Extracción solo de texto")
    result = manager.execute_tool('web_scraper',
        operation='extract_text',
        url='https://httpbin.org/html'
    )
    print_result(result, "Extracción de Texto")
    
    # Ejemplo 3: URLs múltiples (simulado con la misma URL)
    print("\n3. Scraping de múltiples URLs")
    result = manager.execute_tool('web_scraper',
        operation='scrape',
        urls=['https://httpbin.org/html', 'https://httpbin.org/html']
    )
    print_result(result, "Scraping Múltiple")

def demo_python_executor():
    """Demuestra las funcionalidades del ejecutor Python"""
    print_separator("DEMO: Python Executor", "🐍")
    
    manager = get_tool_manager()
    
    # Ejemplo 1: Ejecución básica
    print("\n1. Ejecución de código Python básico")
    safe_code = '''
print("¡Hola desde Python!")
# Operaciones matemáticas
resultado = 2 + 2 * 3
print(f"2 + 2 * 3 = {resultado}")

# Lista y operaciones
numeros = [1, 2, 3, 4, 5]
cuadrados = [n**2 for n in numeros]
print(f"Cuadrados de {numeros}: {cuadrados}")

# Retornar resultado
resultado_final = sum(cuadrados)
'''
    
    result = manager.execute_tool('python_executor',
        operation='execute',
        code=safe_code
    )
    print_result(result, "Ejecución Python")
    
    # Ejemplo 2: Testing de seguridad
    print("\n2. Testing de seguridad de código")
    dangerous_code = '''
import os
import subprocess
exec("print('malicioso')")
'''
    
    result = manager.execute_tool('python_executor',
        operation='test_safety',
        code=dangerous_code
    )
    print_result(result, "Testing de Seguridad")
    
    # Ejemplo 3: Función personalizada
    print("\n3. Ejecución de función personalizada")
    function_code = '''
def calcular_fibonacci(n):
    """Calcula la serie de Fibonacci hasta n"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    
    return fib

def es_primo(num):
    """Verifica si un número es primo"""
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True
'''
    
    result = manager.execute_tool('python_executor',
        operation='execute_function',
        function_code=function_code,
        function_name='calcular_fibonacci',
        args={'n': 10}
    )
    print_result(result, "Ejecución de Función")

def demo_file_processor():
    """Demuestra las funcionalidades del procesador de archivos"""
    print_separator("DEMO: File Processor", "📁")
    
    manager = get_tool_manager()
    
    # Crear archivo de ejemplo para las demos
    example_files = []
    
    # Archivo de texto
    print("\n1. Procesamiento de archivos de texto")
    
    # Nota: En un entorno real, estos archivos existirían
    # Aquí simulamos el comportamiento
    
    result = manager.execute_tool('file_processor',
        operation='validate',
        file_path='/tmp/ejemplo.txt'
    )
    print_result(result, "Validación de Archivo")
    
    # JSON de ejemplo (simulado)
    print("\n2. Procesamiento de archivo JSON")
    result = manager.execute_tool('file_processor',
        operation='structured',
        file_path='/tmp/ejemplo.json'
    )
    print_result(result, "Procesamiento JSON")
    
    print("\n📝 Nota: En un entorno real, estos archivos existirían en el sistema")

def demo_search_engine():
    """Demuestra las funcionalidades del motor de búsqueda"""
    print_separator("DEMO: Search Engine", "🔍")
    
    manager = get_tool_manager()
    
    # Ejemplo 1: Búsqueda web consolidada
    print("\n1. Búsqueda web en múltiples fuentes")
    result = manager.execute_tool('search_engine',
        operation='web_search',
        query='Python programming language',
        sources=['duckduckgo', 'wikipedia']
    )
    print_result(result, "Búsqueda Web Consolidada")
    
    # Ejemplo 2: Búsqueda específica en DuckDuckGo
    print("\n2. Búsqueda en DuckDuckGo")
    result = manager.execute_tool('search_engine',
        operation='duckduckgo',
        query='inteligencia artificial',
        safe_search=True
    )
    print_result(result, "Búsqueda DuckDuckGo")
    
    # Ejemplo 3: Búsqueda en Wikipedia
    print("\n3. Búsqueda en Wikipedia")
    result = manager.execute_tool('search_engine',
        operation='wikipedia',
        query='Machine Learning',
        limit=3
    )
    print_result(result, "Búsqueda Wikipedia")
    
    # Ejemplo 4: Página específica de Wikipedia
    print("\n4. Página específica de Wikipedia")
    result = manager.execute_tool('search_engine',
        operation='wikipedia_page',
        title='Python (lenguaje de programación)'
    )
    print_result(result, "Página Wikipedia")

def demo_concurrent_execution():
    """Demuestra la ejecución concurrente de herramientas"""
    print_separator("DEMO: Ejecución Concurrente", "⚡")
    
    manager = get_tool_manager()
    
    print("\nEjecutando múltiples herramientas en paralelo...")
    
    executions = [
        {
            'tool': 'python_executor',
            'args': {
                'operation': 'execute',
                'code': 'import time; time.sleep(1); print("Python completado")'
            },
            'id': 'python_task'
        },
        {
            'tool': 'search_engine', 
            'args': {
                'operation': 'duckduckgo',
                'query': 'demo search'
            },
            'id': 'search_task'
        },
        {
            'tool': 'web_scraper',
            'args': {
                'operation': 'extract_text',
                'url': 'https://httpbin.org/html'
            },
            'id': 'scraping_task'
        }
    ]
    
    start_time = time.time()
    results = manager.execute_multiple_tools(executions, parallel=True)
    total_time = time.time() - start_time
    
    print(f"\n⏱️  Tiempo total: {total_time:.2f}s")
    
    for task_id, result in results.items():
        print(f"\n--- Tarea: {task_id} ---")
        if result.success:
            print(f"✅ Éxito en {result.execution_time:.2f}s")
        else:
            print(f"❌ Error: {result.error}")

def demo_statistics():
    """Demuestra el sistema de estadísticas y monitoreo"""
    print_separator("DEMO: Estadísticas y Monitoreo", "📊")
    
    manager = get_tool_manager()
    
    # Obtener estadísticas
    print("\n1. Estadísticas de uso de herramientas")
    stats = manager.get_tool_statistics()
    
    print(f"📈 Total de herramientas: {stats['total_tools']}")
    print(f"📈 Total de ejecuciones: {stats['total_executions']}")
    print(f"📈 Ejecuciones recientes (última hora): {stats['recent_executions']}")
    
    for tool_name, tool_stats in stats['tools'].items():
        print(f"\n🔧 {tool_name}:")
        print(f"   - Total ejecuciones: {tool_stats['total_executions']}")
        print(f"   - Exitosas: {tool_stats['successful_executions']}")
        print(f"   - Fallidas: {tool_stats['failed_executions']}")
        if tool_stats['total_executions'] > 0:
            success_rate = tool_stats['successful_executions'] / tool_stats['total_executions'] * 100
            print(f"   - Tasa de éxito: {success_rate:.1f}%")
            print(f"   - Tiempo promedio: {tool_stats['average_execution_time']:.2f}s")
    
    # Health check
    print("\n2. Verificación de salud del sistema")
    health = manager.health_check()
    
    print(f"🏥 Estado general: {health['overall_status'].upper()}")
    print(f"🕐 Timestamp: {time.ctime(health['timestamp'])}")
    
    for tool_name, tool_health in health['tools'].items():
        status_icon = "✅" if tool_health['responsive'] else "❌"
        print(f"{status_icon} {tool_name}: {tool_health['status']}")
        if tool_health['issues']:
            for issue in tool_health['issues']:
                print(f"   ⚠️  {issue}")
    
    # Historial reciente
    print("\n3. Historial de ejecuciones recientes")
    history = manager.get_execution_history(limit=5)
    
    for entry in history:
        status_icon = "✅" if entry['success'] else "❌"
        timestamp = time.ctime(entry['timestamp'])
        print(f"{status_icon} {entry['tool_name']} - {timestamp} - {entry['execution_time']:.2f}s")

def main():
    """Función principal del demo"""
    print("🎯 SISTEMA DE HERRAMIENTAS BÁSICAS - DEMO COMPLETO")
    print("=" * 80)
    
    # Información del sistema
    print("\n📋 Información del Sistema:")
    tools = list_available_tools()
    print(f"🛠️  Herramientas disponibles: {len(tools)}")
    
    for tool in tools:
        print(f"   • {tool['name']}: {tool['description']}")
    
    print("\n" + "=" * 80)
    
    try:
        # Ejecutar demos
        demo_web_scraper()
        input("\n⏸️  Presiona Enter para continuar al siguiente demo...")
        
        demo_python_executor()
        input("\n⏸️  Presiona Enter para continuar al siguiente demo...")
        
        demo_file_processor()
        input("\n⏸️  Presiona Enter para continuar al siguiente demo...")
        
        demo_search_engine()
        input("\n⏸️  Presiona Enter para continuar al demo concurrente...")
        
        demo_concurrent_execution()
        input("\n⏸️  Presiona Enter para continuar a las estadísticas...")
        
        demo_statistics()
        
        print_separator("DEMO COMPLETADO", "🎉", width=60)
        print("\n✅ Todos los demos ejecutados exitosamente!")
        print("\n💡 Consejos para uso en producción:")
        print("   • Configurar timeouts apropiados")
        print("   • Implementar logging detallado")
        print("   • Monitorear estadísticas regularmente")
        print("   • Validar entrada de usuarios")
        print("   • Configurar dominios permitidos para web scraping")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error ejecutando demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()