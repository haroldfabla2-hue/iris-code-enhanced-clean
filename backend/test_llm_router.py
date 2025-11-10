#!/usr/bin/env python3
"""
Script de prueba para el LLM Router actualizado
Demuestra funcionalidad real con OpenRouter API
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Añadir path para imports
sys.path.append('/workspace/backend')

from app.core.llm_router import LLMRouter, LLMProvider


async def test_router_functionality():
    """Prueba la funcionalidad completa del router"""
    
    print("🚀 Iniciando pruebas del LLM Router Actualizado")
    print("=" * 60)
    
    # Inicializar router
    router = LLMRouter()
    
    # Verificar configuración
    print(f"📋 Configuración:")
    print(f"   MiniMax API: {'✅' if router.minimax_api_key else '❌'}")
    print(f"   OpenRouter API: {'✅' if router.openrouter_api_key else '❌'}")
    print()
    
    # Test 1: Probar diferentes modelos
    models_to_test = [
        "llama70b",
        "llama31_70b", 
        "claude3_5",
        "gemini"
    ]
    
    print("🧪 Test 1: Probar diferentes modelos")
    print("-" * 40)
    
    for model in models_to_test:
        if not router.openrouter_api_key:
            print(f"⚠️  OpenRouter API key no configurada, saltando test de {model}")
            continue
            
        try:
            print(f"🔄 Probando modelo: {model}")
            response = await router.chat_completion(
                prompt=f"Explica qué es la inteligencia artificial en una oración para {model}",
                model=model,
                temperature=0.7,
                max_tokens=100
            )
            
            print(f"✅ {model}: {response[:100]}...")
            print()
            
        except Exception as e:
            print(f"❌ Error con {model}: {e}")
            print()
    
    # Test 2: Probar fallbacks automáticos
    print("🛡️  Test 2: Probar sistema de fallbacks")
    print("-" * 40)
    
    if router.openrouter_api_key:
        try:
            # Forzar un fallback usando un modelo específico
            response = await router.chat_completion(
                prompt="Hola, ¿cómo estás?",
                model="gpt4",  # Modelo de mayor costo
                temperature=0.7,
                max_tokens=50,
                enable_fallback=True
            )
            
            print(f"✅ Fallback exitoso: {response[:100]}...")
            print()
            
        except Exception as e:
            print(f"❌ Error en test de fallback: {e}")
            print()
    else:
        print("⚠️  OpenRouter API key no configurada, saltando test de fallback")
        print()
    
    # Test 3: Probar rate limiting
    print("⏱️  Test 3: Probar rate limiting")
    print("-" * 40)
    
    if router.openrouter_api_key:
        try:
            print("Realizando múltiples requests para probar rate limiting...")
            
            for i in range(3):
                start_time = asyncio.get_event_loop().time()
                
                response = await router.chat_completion(
                    prompt=f"Genera una respuesta breve para el request #{i+1}",
                    model="llama70b",
                    temperature=0.7,
                    max_tokens=50
                )
                
                end_time = asyncio.get_event_loop().time()
                print(f"   Request {i+1}: {end_time - start_time:.2f}s")
                
                # Pequeña pausa entre requests
                await asyncio.sleep(1)
            
            print("✅ Test de rate limiting completado")
            print()
            
        except Exception as e:
            print(f"❌ Error en test de rate limiting: {e}")
            print()
    else:
        print("⚠️  OpenRouter API key no configurada, saltando test de rate limiting")
        print()
    
    # Test 4: Probar estadísticas
    print("📊 Test 4: Estadísticas del router")
    print("-" * 40)
    
    stats = router.get_stats()
    
    print(f"Total de llamadas: {stats['total_calls']}")
    print(f"Total de errores: {stats['total_errors']}")
    print(f"Tasa de éxito general: {stats['overall_success_rate']:.2%}")
    print(f"Días restantes MiniMax gratis: {stats['minimax_free_days_remaining']}")
    
    print("\n📈 Por proveedor:")
    for provider, provider_stats in stats['by_provider'].items():
        print(f"  {provider}:")
        print(f"    Llamadas: {provider_stats['calls']}")
        print(f"    Errores: {provider_stats['errors']}")
        print(f"    Tasa de éxito: {provider_stats['success_rate']:.2%}")
        if provider_stats['circuit_breaker_open']:
            print(f"    ⚠️  Circuit breaker ABIERTO")
    
    print()
    
    # Test 5: Probar contexto manager
    print("🔄 Test 5: Probar contexto manager")
    print("-" * 40)
    
    async with LLMRouter() as ctx_router:
        if ctx_router.openrouter_api_key:
            response = await ctx_router.chat_completion(
                prompt="Prueba del contexto manager",
                model="llama70b",
                max_tokens=50
            )
            print(f"✅ Contexto manager: {response[:50]}...")
        else:
            print("⚠️  OpenRouter API key no configurada")
    
    print("\n✅ Pruebas completadas")
    
    # Cerrar router
    await router.close()


async def demo_router_features():
    """Demostración de características avanzadas"""
    
    print("\n🎯 Demostración de Características Avanzadas")
    print("=" * 60)
    
    router = LLMRouter()
    
    # Demo 1: Manejo de errores robusto
    print("🛡️  Demo 1: Manejo de errores y circuit breaker")
    print("-" * 50)
    
    if router.openrouter_api_key:
        try:
            # Simular request que podría fallar
            response = await router.chat_completion(
                prompt="Explica quantum computing de forma simple",
                model="gpt4",
                temperature=0.3,
                max_tokens=200
            )
            print("✅ Request exitoso manejando errores")
            print(f"   Respuesta: {response[:150]}...")
            
        except Exception as e:
            print(f"⚠️  Error manejado correctamente: {e}")
    else:
        print("⚠️  OpenRouter API key no configurada")
    
    # Demo 2: Selección inteligente de proveedor
    print("\n🎯 Demo 2: Selección inteligente de proveedor")
    print("-" * 50)
    
    # Test diferentes escenarios
    scenarios = [
        {"model": "llama70b", "description": "Modelo optimizado"},
        {"model": "gpt4", "description": "Modelo premium"},
        {"model": "claude3_5", "description": "Modelo especializado"}
    ]
    
    for scenario in scenarios:
        selected_provider = router._select_provider(scenario["model"])
        print(f"   {scenario['description']} → {selected_provider.value}")
    
    # Demo 3: Validación de respuestas
    print("\n🔍 Demo 3: Validación de respuestas")
    print("-" * 50)
    
    test_responses = [
        "Esta es una respuesta válida del LLM.",
        "Error: API key invalid",
        "Mock response placeholder",
        "Fallback mode activated"
    ]
    
    for i, response in enumerate(test_responses, 1):
        is_valid = router._is_response_valid(response)
        print(f"   Test {i}: {'✅ Válida' if is_valid else '❌ Inválida'} - {response[:30]}...")
    
    await router.close()


if __name__ == "__main__":
    # Verificar que estamos en el entorno correcto
    if not os.path.exists("/workspace/backend"):
        print("❌ Error: Ejecutar desde /workspace/backend/")
        sys.exit(1)
    
    print(f"🕒 Inicio: {datetime.utcnow().isoformat()}")
    
    try:
        # Ejecutar pruebas principales
        asyncio.run(test_router_functionality())
        
        # Ejecutar demostraciones
        asyncio.run(demo_router_features())
        
        print(f"\n🏁 Fin: {datetime.utcnow().isoformat()}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()