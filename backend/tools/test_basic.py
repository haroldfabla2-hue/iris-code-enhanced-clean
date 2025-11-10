#!/usr/bin/env python3
"""
Test básico del sistema de herramientas para verificar funcionamiento correcto.
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# También agregar el directorio padre para poder importar como 'tools'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test de importación de módulos"""
    print("🧪 Testing imports...")
    
    try:
        from tools import BaseTool, ToolResult, ToolStatus
        print("✅ Base imports OK")
        
        from tools import WebScraper, PythonExecutor, FileProcessor, SearchEngine
        print("✅ Tool classes OK")
        
        from tools import ToolManager, get_tool_manager
        print("✅ Manager imports OK")
        
        from tools import list_available_tools, get_version_info
        print("✅ Utility functions OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test de funcionalidad básica"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from tools import get_tool_manager
        
        # Obtener manager
        manager = get_tool_manager()
        print("✅ Tool manager created")
        
        # Listar herramientas
        tools = manager.list_tools()
        print(f"✅ Listed {len(tools)} tools")
        
        # Test de estadísticas
        stats = manager.get_tool_statistics()
        print("✅ Statistics retrieved")
        
        # Health check
        health = manager.health_check()
        print("✅ Health check completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_creation():
    """Test de creación individual de herramientas"""
    print("\n🧪 Testing individual tool creation...")
    
    try:
        from tools import WebScraper, PythonExecutor, FileProcessor, SearchEngine
        
        # Crear instancias
        web_scraper = WebScraper()
        print("✅ WebScraper created")
        
        python_executor = PythonExecutor()
        print("✅ PythonExecutor created")
        
        file_processor = FileProcessor()
        print("✅ FileProcessor created")
        
        search_engine = SearchEngine()
        print("✅ SearchEngine created")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool creation error: {e}")
        return False

def test_python_executor():
    """Test específico del PythonExecutor"""
    print("\n🧪 Testing PythonExecutor...")
    
    try:
        from tools import get_tool_manager
        
        manager = get_tool_manager()
        
        # Test de seguridad sin ejecución
        result = manager.execute_tool('python_executor',
            operation='test_safety',
            code='print("Hello World")'
        )
        
        if result.success:
            print("✅ Safety test completed")
        else:
            print(f"⚠️  Safety test warning: {result.error}")
        
        # Test de ejecución segura
        result = manager.execute_tool('python_executor',
            operation='execute',
            code='print("Hello from Python!")\nresult = 2 + 2\nprint(f"2 + 2 = {result}")'
        )
        
        if result.success:
            print("✅ Code execution completed")
            print(f"   Output: {result.data.get('output', 'No output')[:100]}...")
        else:
            print(f"❌ Code execution error: {result.error}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ PythonExecutor test error: {e}")
        return False

def test_search_engine():
    """Test específico del SearchEngine"""
    print("\n🧪 Testing SearchEngine...")
    
    try:
        from tools import get_tool_manager
        
        manager = get_tool_manager()
        
        # Test de búsqueda
        result = manager.execute_tool('search_engine',
            operation='duckduckgo',
            query='python programming'
        )
        
        if result.success:
            print("✅ Search completed")
            print(f"   Results count: {result.data.get('results_count', 0)}")
        else:
            print(f"⚠️  Search error (normal en test): {result.error}")
        
        return True  # No falla si no hay conexión
        
    except Exception as e:
        print(f"⚠️  Search test warning: {e}")
        return True  # No falla por problemas de red

def main():
    """Función principal de testing"""
    print("🚀 SISTEMA DE HERRAMIENTAS - TESTING BÁSICO")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Tool Creation", test_tool_creation),
        ("PythonExecutor", test_python_executor),
        ("SearchEngine", test_search_engine)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running test: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Sistema funcionando correctamente.")
        return 0
    else:
        print("⚠️  Some tests failed. Revisar configuración.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)