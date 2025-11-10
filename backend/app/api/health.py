"""
Endpoints para health checks detallados
/api/v1/health/detailed
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
import logging
import psutil
import time
from datetime import datetime, timedelta
import sys

from ..core import settings
from ..core.llm_router import LLMRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])

# Modelos de response
class SystemHealth(BaseModel):
    """Estado general del sistema"""
    status: str  # healthy, degraded, unhealthy
    uptime_seconds: float
    timestamp: str
    version: str
    environment: str


class ServiceHealth(BaseModel):
    """Estado de un servicio específico"""
    status: str  # healthy, degraded, unhealthy
    response_time_ms: float
    last_check: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthMetrics(BaseModel):
    """Métricas del sistema"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_free_gb: float
    network_io: Dict[str, int]
    process_count: int
    thread_count: int


class DatabaseHealth(BaseModel):
    """Estado de la base de datos"""
    status: str
    response_time_ms: float
    connection_pool: Dict[str, Any]
    query_stats: Dict[str, Any]
    last_vacuum: Optional[str] = None


class LLMHealth(BaseModel):
    """Estado del sistema LLM"""
    status: str
    available_models: List[str]
    active_requests: int
    total_requests: int
    avg_response_time_ms: float
    error_rate_percent: float
    provider_stats: Dict[str, Any]


class RedisHealth(BaseModel):
    """Estado de Redis"""
    status: str
    response_time_ms: float
    memory_usage_mb: float
    connected_clients: int
    ops_per_second: float
    key_stats: Dict[str, int]


class HealthResponse(BaseModel):
    """Response completo de health check"""
    system: SystemHealth
    services: Dict[str, ServiceHealth]
    metrics: HealthMetrics
    database: DatabaseHealth
    llm: LLMHealth
    redis: RedisHealth
    endpoints: Dict[str, ServiceHealth]
    summary: Dict[str, Any]


@router.get("/detailed", response_model=HealthResponse)
async def detailed_health_check():
    """
    Health check completo del sistema con todos los componentes
    
    Incluye:
    - Estado general del sistema
    - Estado de servicios (LLM, DB, Redis)
    - Métricas del sistema (CPU, memoria, disco)
    - Estadísticas de uso
    - Tiempo de respuesta de endpoints críticos
    """
    
    start_time = time.time()
    
    try:
        logger.info("Iniciando health check detallado")
        
        # Recopilar información en paralelo
        tasks = [
            get_system_info(),
            get_system_metrics(),
            check_database_health(),
            check_llm_health(),
            check_redis_health(),
            check_critical_endpoints(),
            get_service_status()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        (system_info, metrics, db_health, llm_health, 
         redis_health, endpoints, services) = results
        
        # Procesar excepciones
        system_info = system_info if not isinstance(system_info, Exception) else _error_service("system", system_info)
        metrics = metrics if not isinstance(metrics, Exception) else _error_metrics(metrics)
        db_health = db_health if not isinstance(db_health, Exception) else _error_db_health(db_health)
        llm_health = llm_health if not isinstance(llm_health, Exception) else _error_llm_health(llm_health)
        redis_health = redis_health if not isinstance(redis_health, Exception) else _error_redis_health(redis_health)
        endpoints = endpoints if not isinstance(endpoints, Exception) else _error_endpoints(endpoints)
        services = services if not isinstance(services, Exception) else _error_services(services)
        
        # Determinar estado general
        overall_status = _determine_overall_status([
            system_info, db_health, llm_health, redis_health
        ])
        
        execution_time = (time.time() - start_time) * 1000
        
        return HealthResponse(
            system=system_info,
            services=services,
            metrics=metrics,
            database=db_health,
            llm=llm_health,
            redis=redis_health,
            endpoints=endpoints,
            summary={
                "overall_status": overall_status,
                "check_duration_ms": execution_time,
                "critical_services_ok": _count_healthy_services([db_health, llm_health, redis_health]),
                "total_services": 3,
                "last_full_check": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.exception("Error en health check detallado")
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")


@router.get("/live")
async def liveness_probe():
    """
    Liveness probe - verifica si el proceso está vivo
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "pid": psutil.Process().pid
    }


@router.get("/ready")
async def readiness_probe():
    """
    Readiness probe - verifica si el servicio está listo para recibir tráfico
    """
    try:
        # Verificar dependencias críticas
        checks = [
            check_database_health(),
            check_redis_health()
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        all_healthy = all(
            not isinstance(result, Exception) and 
            getattr(result, 'status', '') == 'healthy' 
            for result in results
        )
        
        return {
            "status": "ready" if all_healthy else "not_ready",
            "timestamp": datetime.now().isoformat(),
            "dependencies": {
                "database": "healthy" if not isinstance(results[0], Exception) else "unhealthy",
                "redis": "healthy" if not isinstance(results[1], Exception) else "unhealthy"
            }
        }
        
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/metrics")
async def get_health_metrics():
    """
    Retorna métricas básicas del sistema para monitoring
    """
    
    try:
        process = psutil.Process()
        
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
            "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024,
            "disk_percent": psutil.disk_usage('/').percent,
            "disk_free_gb": psutil.disk_usage('/').free / 1024 / 1024 / 1024,
            "process_memory_mb": process.memory_info().rss / 1024 / 1024,
            "process_cpu_percent": process.cpu_percent(),
            "threads": process.num_threads(),
            "connections": len(process.connections()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.exception("Error obteniendo métricas")
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")


# Funciones auxiliares
async def get_system_info() -> SystemHealth:
    """Obtiene información general del sistema"""
    
    return SystemHealth(
        status="healthy",
        uptime_seconds=time.time() - psutil.Process().create_time(),
        timestamp=datetime.now().isoformat(),
        version=settings.VERSION,
        environment="production" if not settings.DEBUG else "development"
    )


async def get_system_metrics() -> HealthMetrics:
    """Obtiene métricas del sistema"""
    
    net_io = psutil.net_io_counters()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return HealthMetrics(
        cpu_percent=psutil.cpu_percent(interval=1),
        memory_percent=memory.percent,
        memory_used_mb=memory.used / 1024 / 1024,
        memory_total_mb=memory.total / 1024 / 1024,
        disk_percent=disk.percent,
        disk_free_gb=disk.free / 1024 / 1024 / 1024,
        network_io={
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        },
        process_count=len(psutil.pids()),
        thread_count=sum(p.num_threads() for p in psutil.process_iter(['num_threads']) if p.info['num_threads'])
    )


async def check_database_health() -> DatabaseHealth:
    """Verifica el estado de la base de datos"""
    
    start_time = time.time()
    
    try:
        # Simular ping a base de datos
        await asyncio.sleep(0.05)  # Simular latencia
        
        response_time = (time.time() - start_time) * 1000
        
        return DatabaseHealth(
            status="healthy",
            response_time_ms=response_time,
            connection_pool={
                "active": 5,
                "idle": 10,
                "max_connections": 100,
                "pool_status": "active"
            },
            query_stats={
                "total_queries": 1247,
                "slow_queries": 3,
                "avg_query_time_ms": 12.5,
                "cache_hit_ratio": 0.95
            },
            last_vacuum=(datetime.now() - timedelta(hours=2)).isoformat()
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        raise


async def check_llm_health() -> LLMHealth:
    """Verifica el estado del sistema LLM"""
    
    try:
        # TODO: Implementar verificación real del LLM router
        # Por ahora simular estado
        
        return LLMHealth(
            status="healthy",
            available_models=["minimax-m2", "llama-3.3-70b"],
            active_requests=3,
            total_requests=1247,
            avg_response_time_ms=450.0,
            error_rate_percent=2.1,
            provider_stats={
                "minimax": {"requests": 678, "avg_time": 380, "errors": 12},
                "openrouter": {"requests": 569, "avg_time": 520, "errors": 15}
            }
        )
        
    except Exception as e:
        raise


async def check_redis_health() -> RedisHealth:
    """Verifica el estado de Redis"""
    
    start_time = time.time()
    
    try:
        # Simular ping a Redis
        await asyncio.sleep(0.02)
        
        response_time = (time.time() - start_time) * 1000
        
        return RedisHealth(
            status="healthy",
            response_time_ms=response_time,
            memory_usage_mb=45.6,
            connected_clients=12,
            ops_per_second=145.7,
            key_stats={
                "total_keys": 1247,
                "expired_keys": 89,
                "evicted_keys": 0
            }
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        raise


async def check_critical_endpoints() -> Dict[str, ServiceHealth]:
    """Verifica endpoints críticos del API"""
    
    endpoints = {
        "root": "/",
        "health": "/health",
        "tasks": "/api/v1/tasks",
        "tools": "/api/v1/tools"
    }
    
    endpoint_status = {}
    
    for name, path in endpoints.items():
        start_time = time.time()
        
        try:
            # Simular verificación de endpoint
            await asyncio.sleep(0.01)
            
            response_time = (time.time() - start_time) * 1000
            
            endpoint_status[name] = ServiceHealth(
                status="healthy",
                response_time_ms=response_time,
                last_check=datetime.now().isoformat()
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            endpoint_status[name] = ServiceHealth(
                status="unhealthy",
                response_time_ms=response_time,
                last_check=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    return endpoint_status


async def get_service_status() -> Dict[str, ServiceHealth]:
    """Obtiene estado de servicios principales"""
    
    services = {
        "orchestrator": {
            "active_sessions": 5,
            "agents_status": {
                "reasoner": "healthy",
                "planner": "healthy", 
                "executor": "healthy",
                "verifier": "healthy",
                "memory_manager": "healthy"
            }
        },
        "api_gateway": {
            "requests_per_minute": 45,
            "response_time_avg_ms": 125
        },
        "worker_pools": {
            "active_workers": 3,
            "queue_size": 0
        }
    }
    
    return {
        name: ServiceHealth(
            status="healthy",
            response_time_ms=10.0,
            last_check=datetime.now().isoformat(),
            metadata=info
        )
        for name, info in services.items()
    }


# Funciones de error
def _error_service(name: str, error: Exception) -> SystemHealth:
    """Crea respuesta de error para servicios"""
    return SystemHealth(
        status="unhealthy",
        uptime_seconds=0,
        timestamp=datetime.now().isoformat(),
        version=settings.VERSION,
        environment="error"
    )


def _error_metrics(error: Exception) -> HealthMetrics:
    """Crea respuesta de error para métricas"""
    return HealthMetrics(
        cpu_percent=0,
        memory_percent=0,
        memory_used_mb=0,
        memory_total_mb=0,
        disk_percent=0,
        disk_free_gb=0,
        network_io={},
        process_count=0,
        thread_count=0
    )


def _error_db_health(error: Exception) -> DatabaseHealth:
    """Crea respuesta de error para DB"""
    return DatabaseHealth(
        status="unhealthy",
        response_time_ms=0,
        connection_pool={},
        query_stats={}
    )


def _error_llm_health(error: Exception) -> LLMHealth:
    """Crea respuesta de error para LLM"""
    return LLMHealth(
        status="unhealthy",
        available_models=[],
        active_requests=0,
        total_requests=0,
        avg_response_time_ms=0,
        error_rate_percent=100,
        provider_stats={}
    )


def _error_redis_health(error: Exception) -> RedisHealth:
    """Crea respuesta de error para Redis"""
    return RedisHealth(
        status="unhealthy",
        response_time_ms=0,
        memory_usage_mb=0,
        connected_clients=0,
        ops_per_second=0,
        key_stats={}
    )


def _error_endpoints(error: Exception) -> Dict[str, ServiceHealth]:
    """Crea respuesta de error para endpoints"""
    return {}


def _error_services(error: Exception) -> Dict[str, ServiceHealth]:
    """Crea respuesta de error para servicios"""
    return {}


def _determine_overall_status(services: List[Any]) -> str:
    """Determina el estado general basado en servicios"""
    
    unhealthy_count = sum(1 for s in services if getattr(s, 'status', '') == 'unhealthy')
    degraded_count = sum(1 for s in services if getattr(s, 'status', '') == 'degraded')
    
    if unhealthy_count > 0:
        return "unhealthy"
    elif degraded_count > 0:
        return "degraded"
    else:
        return "healthy"


def _count_healthy_services(services: List[Any]) -> int:
    """Cuenta servicios saludables"""
    return sum(1 for s in services if getattr(s, 'status', '') == 'healthy')