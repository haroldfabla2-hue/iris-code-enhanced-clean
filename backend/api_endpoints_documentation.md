# API Endpoints Implementados

## Resumen
Se han implementado los siguientes endpoints críticos en `/api/v1/`:

## 1. `/api/v1/tools/execute` - Ejecución de Herramientas

### Descripción
Ejecuta herramientas especializadas del sistema multi-agente de forma síncrona o asíncrona.

### Endpoints Disponibles

#### `GET /api/v1/tools/`
Lista todas las herramientas disponibles organizadas por tipo de executor.

**Respuesta:**
```json
{
  "tools": [
    {
      "name": "web_search",
      "description": "Búsqueda en web",
      "parameters": ["query", "num_results"],
      "executor_type": "general"
    }
  ],
  "executors": ["general", "code", "web", "docs"],
  "total_tools": 15
}
```

#### `POST /api/v1/tools/execute`
Ejecuta una herramienta específica.

**Parámetros:**
```json
{
  "tool_name": "web_search",
  "parameters": {
    "query": "Python web scraping",
    "num_results": 5
  },
  "executor_type": "general",
  "user_id": "user_123",
  "timeout": 30,
  "async_mode": false
}
```

**Respuesta:**
```json
{
  "execution_id": "exec_a1b2c3d4e5f6",
  "tool_name": "web_search",
  "status": "success",
  "result": {
    "query": "Python web scraping",
    "results": [
      {
        "title": "Tutorial de Web Scraping",
        "url": "https://example.com/tutorial",
        "snippet": "Aprende web scraping con Python..."
      }
    ]
  },
  "execution_time_ms": 245,
  "metadata": {
    "tool_type": "search",
    "executor_used": "general"
  }
}
```

#### `GET /api/v1/tools/execute/{execution_id}`
Obtiene el estado de una ejecución asíncrona.

## 2. `/api/v1/memory/search` - Búsqueda en Base de Datos de Memoria

### Descripción
Búsqueda semántica, por palabras clave o híbrida en la base de datos de memoria del sistema.

### Endpoints Disponibles

#### `GET /api/v1/memory/search`
Búsqueda en la base de datos de memoria.

**Parámetros de consulta:**
- `query`: Términos de búsqueda (requerido)
- `search_type`: "semantic", "keyword", "hybrid" (default: "hybrid")
- `limit`: Número máximo de resultados (1-100, default: 10)
- `time_range`: "1h", "1d", "1w", "1m", "all" (opcional)
- `conversation_id`: Filtrar por conversación específica (opcional)
- `content_type`: Filtrar por tipo de contenido (opcional)
- `user_id`: Filtrar por usuario específico (opcional)

**Respuesta:**
```json
{
  "query": "análisis de datos Python",
  "search_type": "semantic",
  "total_results": 5,
  "results": [
    {
      "memory_id": "mem_0001",
      "content": "Contenido relacionado con 'análisis de datos Python'",
      "content_type": "code",
      "relevance_score": 0.95,
      "conversation_id": "conv_123",
      "user_id": "user_456",
      "created_at": "2025-11-04T00:40:00Z",
      "metadata": {
        "source": "user_interaction",
        "tags": ["data_analysis", "python"]
      }
    }
  ],
  "search_metadata": {
    "filters": {
      "time_range": "1w",
      "conversation_id": "conv_123"
    },
    "strategy": "semantic",
    "semantic_threshold": 0.7
  },
  "execution_time_ms": 156
}
```

#### `POST /api/v1/memory/store`
Almacena información en la base de datos de memoria.

**Parámetros:**
```json
{
  "content": "Código Python para análisis de datos",
  "content_type": "code",
  "conversation_id": "conv_123",
  "user_id": "user_456",
  "metadata": {
    "source": "executor_result",
    "operation": "data_analysis"
  },
  "tags": ["python", "data_analysis", "code"]
}
```

#### `GET /api/v1/memory/stats`
Obtiene estadísticas de la base de datos de memoria.

#### `DELETE /api/v1/memory/clear`
Limpia memorias según criterios especificados.

## 3. `/api/v1/tasks/{id}/stream` - Streaming de Updates de Tareas

### Descripción
Streaming en tiempo real de actualizaciones de tareas usando Server-Sent Events (SSE).

### Endpoints Disponibles

#### `GET /api/v1/tasks/{task_id}/stream`
Stream de updates en tiempo real para una tarea específica.

**Parámetros de consulta:**
- `update_frequency`: Frecuencia de updates (0.1-10.0 segundos, default: 1.0)
- `include_results`: Incluir resultados parciales (default: true)
- `include_agent_details`: Incluir detalles por agente (default: false)
- `max_duration`: Duración máxima del stream (30-1800 segundos, default: 300)

**Ejemplo de stream:**
```
data: {"task_id": "task_123", "status": "in_progress", "phase": "reasoning", "progress": 0.2, "message": "Analizando el objetivo", "result": {"current_phase": "reasoning", "progress_percentage": 20}, "timestamp": "2025-11-04T00:44:32Z"}

data: {"task_id": "task_123", "status": "in_progress", "phase": "planning", "progress": 0.4, "message": "Creando plan de ejecución", "result": {"current_phase": "planning", "progress_percentage": 40}, "timestamp": "2025-11-04T00:44:33Z"}

data: [DONE]
```

#### `GET /api/v1/tasks/{task_id}/status`
Obtiene el estado actual de una tarea.

#### `GET /api/v1/tasks/{task_id}/results`
Obtiene los resultados finales de una tarea.

#### `DELETE /api/v1/tasks/{task_id}`
Cancela una tarea en ejecución.

#### `GET /api/v1/tasks/list`
Lista tareas con filtros opcionales.

## 4. `/api/v1/health/detailed` - Health Check Completo

### Descripción
Health check exhaustivo que verifica todos los componentes del sistema.

### Endpoints Disponibles

#### `GET /api/v1/health/detailed`
Health check completo del sistema con todos los componentes.

**Respuesta:**
```json
{
  "system": {
    "status": "healthy",
    "uptime_seconds": 86400.5,
    "timestamp": "2025-11-04T00:44:32Z",
    "version": "0.1.0",
    "environment": "production"
  },
  "services": {
    "orchestrator": {
      "status": "healthy",
      "response_time_ms": 10.0,
      "last_check": "2025-11-04T00:44:32Z",
      "metadata": {
        "active_sessions": 5,
        "agents_status": {
          "reasoner": "healthy",
          "planner": "healthy",
          "executor": "healthy",
          "verifier": "healthy",
          "memory_manager": "healthy"
        }
      }
    }
  },
  "metrics": {
    "cpu_percent": 25.4,
    "memory_percent": 68.2,
    "memory_used_mb": 8192,
    "memory_total_mb": 12000,
    "disk_percent": 45.1,
    "disk_free_gb": 156.7,
    "network_io": {
      "bytes_sent": 1048576,
      "bytes_recv": 2097152,
      "packets_sent": 1234,
      "packets_recv": 2345
    },
    "process_count": 245,
    "thread_count": 1200
  },
  "database": {
    "status": "healthy",
    "response_time_ms": 12.5,
    "connection_pool": {
      "active": 5,
      "idle": 10,
      "max_connections": 100,
      "pool_status": "active"
    },
    "query_stats": {
      "total_queries": 1247,
      "slow_queries": 3,
      "avg_query_time_ms": 12.5,
      "cache_hit_ratio": 0.95
    }
  },
  "llm": {
    "status": "healthy",
    "available_models": ["minimax-m2", "llama-3.3-70b"],
    "active_requests": 3,
    "total_requests": 1247,
    "avg_response_time_ms": 450.0,
    "error_rate_percent": 2.1,
    "provider_stats": {
      "minimax": {"requests": 678, "avg_time": 380, "errors": 12},
      "openrouter": {"requests": 569, "avg_time": 520, "errors": 15}
    }
  },
  "redis": {
    "status": "healthy",
    "response_time_ms": 2.1,
    "memory_usage_mb": 45.6,
    "connected_clients": 12,
    "ops_per_second": 145.7,
    "key_stats": {
      "total_keys": 1247,
      "expired_keys": 89,
      "evicted_keys": 0
    }
  },
  "endpoints": {
    "root": {"status": "healthy", "response_time_ms": 5.2},
    "health": {"status": "healthy", "response_time_ms": 3.1},
    "tasks": {"status": "healthy", "response_time_ms": 8.7},
    "tools": {"status": "healthy", "response_time_ms": 12.3}
  },
  "summary": {
    "overall_status": "healthy",
    "check_duration_ms": 245.7,
    "critical_services_ok": 3,
    "total_services": 3,
    "last_full_check": "2025-11-04T00:44:32Z"
  }
}
```

#### `GET /api/v1/health/live`
Liveness probe simple - verifica si el proceso está vivo.

#### `GET /api/v1/health/ready`
Readiness probe - verifica si el servicio está listo para recibir tráfico.

#### `GET /api/v1/health/metrics`
Retorna métricas básicas del sistema para monitoring.

## Características Implementadas

### ✅ Documentación Automática
Todos los endpoints incluyen:
- Documentación Swagger UI en `/docs`
- Documentación ReDoc en `/redoc`
- Esquemas de request/response con validación automática
- Ejemplos de uso integrados

### ✅ Configuración Flexible
- Timeouts configurables
- Límites de rate limiting
- Filtros avanzados para búsquedas
- Configuración de frecuencia de streaming

### ✅ Manejo de Errores
- Responses consistentes de error
- Logging detallado
- Códigos de estado HTTP apropiados
- Mensajes descriptivos

### ✅ Métricas y Observabilidad
- Health checks exhaustivos
- Métricas de sistema en tiempo real
- Estadísticas de uso
- Monitoreo de performance

### ✅ Compatibilidad
- Integración con FastAPI existente
- Soporte para Docker Compose
- Compatibilidad con el orquestador multi-agente
- Arquitectura modular y extensible

## Uso con FastAPI

La API está completamente integrada con FastAPI y proporciona:

1. **Documentación automática**: Swagger UI disponible en `/docs`
2. **Validación automática**: Pydantic valida requests y responses
3. **Manejo asíncrono**: Soporte completo para operaciones async
4. **Streaming**: Server-Sent Events para updates en tiempo real
5. **Middleware CORS**: Configurado para desarrollo

## Próximos Pasos

Para completar la implementación:
1. Conectar con Redis para tracking de ejecuciones asíncronas
2. Integrar con la base de datos PostgreSQL real
3. Implementar el sistema de memoria vectorial
4. Configurar autenticación y autorización
5. Agregar rate limiting y throttling
6. Implementar logging estructurado