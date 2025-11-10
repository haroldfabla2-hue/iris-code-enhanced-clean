"""
Configuración central del sistema
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # General
    APP_NAME: str = "Sistema Multi-Agente Superior"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # API Keys
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # MiniMax M2 API
    MINIMAX_API_BASE: str = "https://api.minimax.chat/v1"
    MINIMAX_MODEL: str = "minimax-m2"
    
    # OpenRouter API
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct"
    
    # PostgreSQL (Docker Compose)
    POSTGRES_HOST: str = "postgres"  # Cambiado de localhost para Docker
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "agente_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_secure_password"  # Actualizado para coincidir con .env
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis (Docker Compose)
    REDIS_HOST: str = "redis"  # Cambiado de localhost para Docker
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Límites y Timeouts
    MAX_CONCURRENT_AGENTS: int = 5
    MAX_TOOLS_PER_AGENT: int = 3
    AGENT_TIMEOUT_SECONDS: int = 120
    LLM_TIMEOUT_SECONDS: int = 30
    
    # Observabilidad
    ENABLE_TRACING: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
