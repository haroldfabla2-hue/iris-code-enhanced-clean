#!/usr/bin/env python3
"""
Script de prueba para verificar funcionalidad real de agentes
"""
import asyncio
import os
from datetime import datetime

# Configurar variables de entorno de prueba si no existen
if not os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = "test_key_fallback"

async def test_base_agent():
    """Prueba el agente base con LLM real"""
    print("🧪 Probando BaseAgent...")
    
    try:
        from app.agents.base import BaseAgent
        
        class TestAgent(BaseAgent):
            async def process_message(self, message):
                pass
            def get_capabilities(self):
                return ["test"]
        
        agent = TestAgent("test_agent")
        
        # Probar llamada LLM
        response = await agent.call_llm(
            "Di 'Hola mundo' en español",
            temperature=0.5
        )
        
        print(f"✅ LLM Response: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error en BaseAgent: {str(e)}")
        return False

async def test_executor_tools():
    """Prueba las herramientas del executor"""
    print("\n🧪 Probando ExecutorAgent...")
    
    try:
        from app.agents.executor import ExecutorAgent
        
        executor = ExecutorAgent("test")
        
        # Probar Python executor (simulado)
        result = await executor._tool_python_executor(
            "print('Hola desde Python')",
            {"time_seconds": 10}
        )
        
        print(f"✅ Python Executor: {result.get('success', False)}")
        
        # Probar web scraper con URL de ejemplo
        result = await executor._tool_web_scraper(
            "https://httpbin.org/get",
            {}
        )
        
        print(f"✅ Web Scraper: {result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en ExecutorAgent: {str(e)}")
        return False

async def test_memory_manager():
    """Prueba el memory manager"""
    print("\n🧪 Probando MemoryManagerAgent...")
    
    try:
        from app.agents.memory_manager import MemoryManagerAgent
        
        memory_agent = MemoryManagerAgent()
        
        # Probar almacenar memoria
        store_result = await memory_agent._store_memory({
            "content": {"test": "contenido de prueba"},
            "metadata": {"source": "test"},
            "memory_type": "test"
        })
        
        print(f"✅ Memory Store: {store_result.get('success', False)}")
        
        # Probar recuperar memoria
        retrieve_result = await memory_agent._retrieve_memory({
            "query": "contenido de prueba",
            "top_k": 3
        })
        
        print(f"✅ Memory Retrieve: {retrieve_result.get('num_results', 0)} resultados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en MemoryManagerAgent: {str(e)}")
        return False

async def test_verifier():
    """Prueba el verifier agent"""
    print("\n🧪 Probando VerifierAgent...")
    
    try:
        from app.agents.verifier import VerifierAgent
        
        verifier = VerifierAgent()
        
        # Probar evaluación LLM
        result = await verifier._llm_judge_evaluation(
            {"example": "resultado a evaluar"},
            ["completeness", "accuracy"],
            [0.7, 0.8]
        )
        
        print(f"✅ LLM Judge: {result.get('overall_score', 0):.2f} score")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en VerifierAgent: {str(e)}")
        return False

async def main():
    """Ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas de funcionalidad real de agentes")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    
    results = []
    
    # Ejecutar todas las pruebas
    results.append(await test_base_agent())
    results.append(await test_executor_tools())
    results.append(await test_memory_manager())
    results.append(await test_verifier())
    
    # Resumen de resultados
    print(f"\n📊 Resumen de Pruebas:")
    print(f"✅ Exitosas: {sum(results)}")
    print(f"❌ Fallidas: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 ¡Todas las pruebas pasaron! Agentes con funcionalidad real listos.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisar configuración.")
    
    return all(results)

if __name__ == "__main__":
    asyncio.run(main())
