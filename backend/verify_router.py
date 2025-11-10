#!/usr/bin/env python3
"""
Script de verificación rápida del LLM Router
Verifica configuración básica sin hacer requests reales
"""

import sys
import os
from datetime import datetime

# Añadir path para imports
sys.path.append('/workspace/backend')

try:
    from app.core.llm_router import LLMRouter, LLMProvider
    from app.core.config import settings
    print("✅ Imports exitosos")
except ImportError as e:
    print(f"❌ Error de import: {e}")
    sys.exit(1)

def check_configuration():
    """Verifica la configuración actual"""
    
    print("\n🔍 Verificación de Configuración LLM Router")
    print("=" * 50)
    
    # Verificar settings
    print("\n📋 Variables de Entorno:")
    print(f"   MINIMAX_API_KEY: {'✅' if settings.MINIMAX_API_KEY else '❌ (vacía)'}")
    print(f"   OPENROUTER_API_KEY: {'✅' if settings.OPENROUTER_API_KEY else '❌ (vacía)'}")
    print(f"   LLM_TIMEOUT_SECONDS: {settings.LLM_TIMEOUT_SECONDS}s")
    
    # Verificar inicialización del router
    print("\n🚀 Inicialización del Router:")
    try:
        router = LLMRouter()
        print("   ✅ Router inicializado correctamente")
        
        # Verificar disponibilidad de proveedores
        print("\n🔧 Disponibilidad de Proveedores:")
        
        providers_status = {
            "MiniMax M2": router.minimax_api_key and not router._is_circuit_breaker_open(LLMProvider.MINIMAX_M2),
            "OpenRouter Llama 70B": router.openrouter_api_key and not router._is_circuit_breaker_open(LLMProvider.OPENROUTER_LLAMA70B),
            "OpenRouter Llama 31": router.openrouter_api_key and not router._is_circuit_breaker_open(LLMProvider.OPENROUTER_LLAMA31_70B),
            "OpenRouter GPT-4": router.openrouter_api_key and not router._is_circuit_breaker_open(LLMProvider.OPENROUTER_GPT4),
            "OpenRouter Claude 3.5": router.openrouter_api_key and not router._is_circuit_breaker_open(LLMProvider.OPENROUTER_CLAUDE_3_5),
            "OpenRouter Gemini": router.openrouter_api_key and not router._is_circuit_breaker_open(LLMProvider.OPENROUTER_GEMINI),
        }
        
        for provider, available in providers_status.items():
            status = "✅" if available else "❌"
            circuit_status = ""
            if not available and "OpenRouter" in provider and router.openrouter_api_key:
                if router._is_circuit_breaker_open(LLMProvider(f"openrouter_{provider.split()[-1].lower()}")):
                    circuit_status = " (Circuit breaker abierto)"
            print(f"   {status} {provider}{circuit_status}")
        
        # Verificar modelos
        print("\n🤖 Modelos Disponibles:")
        for model_key, model_id in router.OPENROUTER_MODELS.items():
            print(f"   • {model_key}: {model_id}")
        
        # Verificar rate limits
        print("\n⏱️  Rate Limits (calls/minuto):")
        for provider, limiter in router.RATE_LIMITS.items():
            print(f"   • {provider.value}: {limiter.max_calls}/min")
        
        # Verificar estadísticas
        print("\n📊 Estadísticas Actuales:")
        stats = router.get_stats()
        print(f"   Total calls: {stats['total_calls']}")
        print(f"   Días restantes MiniMax gratis: {stats['minimax_free_days_remaining']}")
        
        # Test de selección de proveedor
        print("\n🎯 Test de Selección de Proveedor:")
        test_models = ["llama70b", "gpt4", "claude3_5"]
        
        for model in test_models:
            selected = router._select_provider(model)
            print(f"   {model} → {selected.value}")
        
        # Test de validación de respuesta
        print("\n🔍 Test de Validación de Respuestas:")
        test_responses = [
            "Esta es una respuesta válida del LLM",
            "Error: API key invalid", 
            "Mock response placeholder",
            "Fallback mode activated"
        ]
        
        for response in test_responses:
            is_valid = router._is_response_valid(response)
            status = "✅" if is_valid else "❌"
            print(f"   {status} {response[:30]}...")
        
        # Verificar fallback order
        print("\n🛡️  Orden de Fallback para MiniMax M2:")
        fallback_order = router._get_fallback_order(LLMProvider.MINIMAX_M2, "llama70b")
        for i, provider in enumerate(fallback_order, 1):
            print(f"   {i}. {provider.value}")
        
        router.close()
        
        print("\n✅ Verificación completada exitosamente")
        
        # Resumen final
        print("\n📝 Resumen:")
        if settings.OPENROUTER_API_KEY:
            print("   ✅ OpenRouter configurado - Router listo para usar")
        else:
            print("   ❌ OpenRouter no configurado - Solo fallback local disponible")
        
        if settings.MINIMAX_API_KEY:
            days_left = (datetime(2025, 11, 7) - datetime.utcnow()).days
            print(f"   ✅ MiniMax configurado - {days_left} días restantes (gratis)")
        else:
            print("   ⚠️  MiniMax no configurado")
        
    except Exception as e:
        print(f"   ❌ Error inicializando router: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"🕒 Verificación iniciada: {datetime.utcnow().isoformat()}")
    
    try:
        check_configuration()
    except KeyboardInterrupt:
        print("\n⚠️  Verificación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante verificación: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🏁 Verificación finalizada: {datetime.utcnow().isoformat()}")