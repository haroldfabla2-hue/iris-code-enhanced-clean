"""
Modelos de mensajes para comunicación entre agentes
Basado en el contrato A2A definido en la arquitectura
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class MessageIntent(str, Enum):
    """Tipos de intención de mensaje"""
    INFORMATION_REQUEST = "information_request"
    DELEGATION = "delegation"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"
    ERROR = "error"
    RESULT = "result"


class MessageStatus(str, Enum):
    """Estados de procesamiento de mensaje"""
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"
    TIMEOUT = "timeout"


class ErrorInfo(BaseModel):
    """Información de error"""
    code: str
    message: str
    retry_after: Optional[int] = None
    retryable: bool = True


class Budget(BaseModel):
    """Presupuesto de recursos"""
    tokens: Optional[int] = None
    time_seconds: Optional[int] = None
    tools_max: Optional[int] = 3


class AgentMessage(BaseModel):
    """
    Mensaje estándar entre agentes
    Implementa el contrato A2A definido en la arquitectura
    """
    # Identificadores
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    trace_id: str = Field(default_factory=lambda: f"trc_{uuid.uuid4().hex[:12]}")
    conversation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Remitente/Destinatarios
    sender: str
    recipients: List[str]
    
    # Propósito
    intent: MessageIntent
    
    # Control de versión y causalidad
    context_version: str = "v1"
    causal_marks: Optional[Dict[str, int]] = None
    in_reply_to: Optional[str] = None
    
    # Contenido
    payload: Dict[str, Any]
    references: Optional[List[str]] = None
    
    # Presupuesto
    budget: Optional[Budget] = None
    
    # Estado
    status: MessageStatus = MessageStatus.PENDING
    errors: Optional[List[ErrorInfo]] = None
    
    # Metadatos
    metadata: Optional[Dict[str, Any]] = None


class TaskDelegation(BaseModel):
    """Payload específico para delegación de tareas"""
    task_id: str
    objetivo: str
    tool_map: List[str]
    limites: Budget
    criterio_exito: str
    context: Optional[Dict[str, Any]] = None


class ValidationRequest(BaseModel):
    """Payload específico para validación"""
    trajectory_id: str
    criterios: List[str]
    thresholds: List[float]
    eval_type: str  # "llm_judge" o "code"


class SynthesisRequest(BaseModel):
    """Payload específico para síntesis"""
    inputs: List[Dict[str, Any]]
    referencias: Optional[List[str]] = None
    formato_salida: str
    citacion: bool = True


class AgentResponse(BaseModel):
    """Respuesta de un agente"""
    message_id: str
    original_message_id: str
    agent_id: str
    status: MessageStatus
    result: Optional[Dict[str, Any]] = None
    errors: Optional[List[ErrorInfo]] = None
    execution_time_ms: Optional[float] = None
    tokens_used: Optional[int] = None
