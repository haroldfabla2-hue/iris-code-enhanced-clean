# 🚀 Comandos Útiles - LLM Router

## Verificación Rápida

```bash
# Verificar que el router se puede importar
cd /workspace/backend
python -c "from app.core.llm_router import LLMRouter; print('✅ Router OK')"

# Verificar configuración
python verify_router.py

# Test de conectividad básica
python test_connectivity.py
```

## Configuración

```bash
# Verificar API keys
python -c "from app.core.config import settings; print('OpenRouter:', bool(settings.OPENROUTER_API_KEY))"

# Ver variables de entorno
cat .env | grep -E "(MINIMAX|OPENROUTER)"

# Copiar ejemplo a .env
cp .env.example .env
```

## Desarrollo

```bash
# Ejecutar suite de pruebas completa
python test_llm_router.py

# Ver logs en tiempo real
tail -f /var/log/app.log | grep "llm_router"

# Test manual de un modelo específico
python -c "
import asyncio
from app.core.llm_router import LLMRouter

async def test():
    async with LLMRouter() as router:
        resp = await router.chat_completion('Hola', model='llama70b', max_tokens=50)
        print(resp[:100])

asyncio.run(test())
"
```

## Monitoreo

```bash
# Ver estadísticas del router
python -c "
import asyncio
from app.core.llm_router import LLMRouter

async def stats():
    async with LLMRouter() as router:
        s = router.get_stats()
        print(f'Total calls: {s[\"total_calls\"]}')
        print(f'Success rate: {s[\"overall_success_rate\"]:.2%}')

asyncio.run(stats())
"
```

## Debug

```bash
# Habilitar logging detallado
export LOG_LEVEL=DEBUG
python test_connectivity.py

# Verificar circuit breakers
python -c "
import asyncio
from app.core.llm_router import LLMRouter, LLMProvider

async def check():
    async with LLMRouter() as router:
        for provider in LLMProvider:
            is_open = router._is_circuit_breaker_open(provider)
            print(f'{provider.value}: {\"OPEN\" if is_open else \"CLOSED\"}')

asyncio.run(check())
"
```

## Utilidades

```bash
# Test de todos los modelos
python -c "
import asyncio
from app.core.llm_router import LLMRouter

async def test_all_models():
    async with LLMRouter() as router:
        models = ['llama70b', 'gpt4', 'claude3_5']
        for model in models:
            try:
                resp = await router.chat_completion('Hi', model=model, max_tokens=10)
                print(f'{model}: OK')
            except Exception as e:
                print(f'{model}: {e}')

asyncio.run(test_all_models())
"

# Benchmark simple
python -c "
import asyncio, time
from app.core.llm_router import LLMRouter

async def benchmark():
    async with LLMRouter() as router:
        start = time.time()
        await router.chat_completion('Count to 5', model='llama70b', max_tokens=50)
        end = time.time()
        print(f'Latencia: {end-start:.2f}s')

asyncio.run(benchmark())
"