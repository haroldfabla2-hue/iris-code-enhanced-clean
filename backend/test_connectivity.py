#!/usr/bin/env python3
"""
Test rápido de conectividad real con OpenRouter
"""

import asyncio
import sys
sys.path.append('/workspace/backend')

from app.core.llm_router import LLMRouter

async def test_real_connectivity():
    """Test básico de conectividad real"""
    
    print("🧪 Test de Conectividad Real con OpenRouter")
    print("=" * 50)
    
    async with LLMRouter() as router:
        try:
            print("🔄 Realizando test request...")
            
            response = await router.chat_completion(
                prompt="Hola, responde brevemente con 'Test exitoso' si puedes leer esto.",
                model="llama70b",
                temperature=0.1,
                max_tokens=50
            )
            
            print(f"✅ Respuesta recibida:")
            print(f"   {response}")
            
            # Verificar estadísticas
            stats = router.get_stats()
            print(f"\n📊 Estadísticas del test:")
            print(f"   Total calls: {stats['total_calls']}")
            print(f"   Llamadas a OpenRouter Llama 70B: {stats['by_provider'].get('openrouter_llama70b', {}).get('calls', 0)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en test de conectividad: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_real_connectivity())
    if success:
        print("\n✅ Conectividad real funcionando correctamente!")
    else:
        print("\n❌ Problemas con la conectividad real")