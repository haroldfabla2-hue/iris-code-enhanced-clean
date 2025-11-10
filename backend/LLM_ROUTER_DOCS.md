# LLM Router - Documentación de Uso

## Resumen de Actualizaciones

El LLM Router ha sido completamente actualizado para implementar **funcionalidad real** en lugar del modo mock. Ahora incluye:

### ✅ Características Implementadas

1. **Conectividad Real con OpenRouter API**
   - Uso de la `OPENROUTER_API_KEY` configurada en settings
   - Soporte para múltiples modelos de OpenRouter
   - Headers HTTP correctos y payload estructurado

2. **Múltiples Modelos Soportados**
   - Llama 3.3 70B Instruct (`llama70b`)
   - Llama 3.1 70B Instruct (`llama31_70b`)
   - GPT-4 (`gpt4`)
   - GPT-4 Turbo (`gpt4_turbo`)
   - Claude 3 Sonnet (`claude3`)
   - Claude 3.5 Sonnet (`claude3_5`)
   - Gemini Pro (`gemini`)

3. **Sistema de Fallbacks Robusto**
   - Fallback automático entre proveedores
   - Circuit breaker para proveedores con errores frecuentes
   - Orden inteligente de fallbacks basado en el modelo

4. **Rate Limiting Avanzado**
   - Rate limiting por proveedor (calls por minuto)
   - Implementación con deques para tracking temporal
   - Auto-ajuste de calls según disponibilidad

5. **Error Handling Completo**
   - Manejo robusto de timeouts HTTP
   - Retry automático con fallbacks
   - Logging detallado de errores
   - Circuit breaker pattern

6. **Logging Detallado**
   - Request/Response logging estructurado
   - Métricas de performance (tiempo, tokens)
   - Logging separado para requests, errores y debug

7. **Timeout Handling**
   - Timeouts configurables por operación (connect, read, write, pool)
   - Verificación de rate limits con timeout
   - Manejo de respuestas lentas

## Configuración

### 1. Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus claves reales
MINIMAX_API_KEY=tu_minimax_api_key_aqui
OPENROUTER_API_KEY=sk-or-v1-tu_clave_openrouter_aqui
```

### 2. Obtener API Keys

#### OpenRouter
1. Registrar en https://openrouter.ai/
2. Ir a Keys section
3. Crear nueva API key
4. Configurar en `.env`

#### MiniMax M2 (Opcional)
1. Registrar en https://api.minimax.chat/
2. Obtener API key (gratis hasta 7 Nov 2025)
3. Configurar en `.env`

## Uso Básico

### Importación

```python
from app.core.llm_router import LLMRouter, LLMProvider

# Crear instancia del router
router = LLMRouter()

# O usar contexto manager (recomendado)
async with LLMRouter() as router:
    response = await router.chat_completion(
        prompt="Explica qué es la inteligencia artificial",
        model="llama70b",
        temperature=0.7,
        max_tokens=200
    )
    print(response)
```

### Modelos Disponibles

```python
# Llama 3.3 70B (Recomendado - buena relación calidad/velocidad)
await router.chat_completion(prompt, model="llama70b")

# Llama 3.1 70B (Versión anterior)
await router.chat_completion(prompt, model="llama31_70b")

# GPT-4 (Mayor calidad, más caro)
await router.chat_completion(prompt, model="gpt4")

# GPT-4 Turbo (Más rápido que GPT-4)
await router.chat_completion(prompt, model="gpt4_turbo")

# Claude 3.5 Sonnet (Excelente para razonamiento)
await router.chat_completion(prompt, model="claude3_5")

# Gemini Pro (Modelo de Google)
await router.chat_completion(prompt, model="gemini")
```

### Parámetros Avanzados

```python
response = await router.chat_completion(
    prompt="Tu prompt aquí",
    model="llama70b",           # Modelo específico
    temperature=0.7,           # Creatividad (0.0 - 2.0)
    max_tokens=2000,           # Máximo de tokens en respuesta
    provider=None,             # None = auto-seleccionar
    enable_fallback=True       # Habilitar fallbacks automáticos
)
```

## Características Avanzadas

### 1. Selección Manual de Proveedor

```python
# Forzar uso de un proveedor específico
response = await router.chat_completion(
    prompt="Tu prompt",
    provider=LLMProvider.OPENROUTER_LLAMA70B,
    model="llama70b"
)
```

### 2. Estadísticas y Monitoreo

```python
stats = router.get_stats()

print(f"Total calls: {stats['total_calls']}")
print(f"Success rate: {stats['overall_success_rate']:.2%}")

# Por proveedor
for provider, data in stats['by_provider'].items():
    print(f"{provider}: {data['calls']} calls, {data['success_rate']:.2%} success")
```

### 3. Rate Limiting

El router maneja automáticamente rate limits:

- **MiniMax M2**: 60 calls/minuto
- **OpenRouter Llama**: 40 calls/minuto
- **OpenRouter GPT-4**: 20 calls/minuto
- **OpenRouter Claude**: 35 calls/minuto
- **OpenRouter Gemini**: 45 calls/minuto

### 4. Circuit Breaker

Protección automática contra proveedores problemáticos:

```python
# Verificar estado del circuit breaker
stats = router.get_stats()
circuit_status = stats['circuit_breaker_status']

for provider, is_open in circuit_status.items():
    if is_open:
        print(f"⚠️  Circuit breaker abierto para: {provider}")
```

### 5. Fallback Order

El router implementa un orden inteligente de fallbacks:

**Si MiniMax M2 falla:**
1. OpenRouter Llama 3.3 70B
2. OpenRouter Llama 3.1 70B  
3. OpenRouter GPT-4 Turbo
4. OpenRouter Claude 3.5

**Si OpenRouter falla:**
1. MiniMax M2 (si disponible)
2. Otros modelos de OpenRouter
3. Fallback local

## Ejemplos Prácticos

### Ejemplo 1: Chat Simple

```python
async def simple_chat():
    async with LLMRouter() as router:
        response = await router.chat_completion(
            prompt="¿Cuál es la capital de Francia?",
            model="llama70b"
        )
        print(response)
```

### Ejemplo 2: Con Múltiples Intentos

```python
async def robust_chat():
    async with LLMRouter() as router:
        for attempt in range(3):
            try:
                response = await router.chat_completion(
                    prompt="Explica machine learning",
                    model="claude3_5",
                    temperature=0.3,
                    max_tokens=500
                )
                return response
            except Exception as e:
                print(f"Intento {attempt + 1} falló: {e}")
                await asyncio.sleep(1)
```

### Ejemplo 3: Con Validación

```python
async def validated_chat():
    async with LLMRouter() as router:
        response = await router.chat_completion(
            prompt="Genera una lista de números del 1 al 10",
            model="llama70b"
        )
        
        # Validar respuesta
        if router._is_response_valid(response):
            print("✅ Respuesta válida recibida")
            return response
        else:
            print("❌ Respuesta inválida")
            return None
```

## Resolución de Problemas

### Error: "OPENROUTER_API_KEY no configurada"

```bash
# Verificar que la clave está en .env
cat .env | grep OPENROUTER_API_KEY

# Verificar que se carga correctamente
python -c "from app.core.config import settings; print('OPENROUTER_API_KEY:', bool(settings.OPENROUTER_API_KEY))"
```

### Error: "Rate limit excedido"

- El router maneja esto automáticamente con fallbacks
- Si persiste, verificar que no se estén haciendo demasiadas requests
- Considerar implementar caching de respuestas

### Error: "Todos los proveedores fallaron"

1. Verificar conectividad a internet
2. Verificar que las API keys sean válidas
3. Revisar logs para errores específicos
4. Considerar usar fallback local temporalmente

### Debug Mode

```python
import logging

# Habilitar logging detallado
logging.basicConfig(level=logging.DEBUG)

# El router creará logs detallados de cada request
```

## Mejores Prácticas

1. **Usar contexto manager** para manejo automático de recursos
2. **Implementar timeouts** apropiados para tu aplicación
3. **Monitorear estadísticas** regularmente
4. **Manejar fallbacks** de forma explícita en código crítico
5. **Caching** de respuestas para requests repetitivos
6. **Validar respuestas** en casos críticos

## Testing

Ejecutar pruebas del router:

```bash
cd /workspace/backend
python test_llm_router.py
```

Esto ejecuta pruebas de:
- Conectividad con diferentes modelos
- Sistema de fallbacks
- Rate limiting
- Estadísticas
- Contexto manager

## Migración desde Versión Anterior

Si migras desde el router anterior:

1. **Cambiar import**: Ya no necesitas `settings.MINIMAX_API_KEY` como parámetro
2. **Agregar modelo**: Especificar `model="llama70b"` en lugar de confiar en auto-selección
3. **Usar contexto manager**: `async with LLMRouter() as router:` es recomendado
4. **Verificar API keys**: Asegurar que `.env` tenga `OPENROUTER_API_KEY` configurada

La migración es compatible con código existente, pero se recomienda actualizar para aprovechar las nuevas características.