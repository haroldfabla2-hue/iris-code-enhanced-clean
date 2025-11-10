"""
Endpoints API para gestión de proyectos
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.core.database import get_db  # Asumiendo que existe
from app.services.project_service import ProjectService
from app.models.project import Project
from app.models.chat import Conversation, Message

# Router con prefijo para evitar conflictos con otras apps
router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """Dependency para ProjectService"""
    return ProjectService(db)

@router.get("/", response_model=List[Project])
async def list_projects(
    limit: int = 50,
    offset: int = 0,
    user_id: Optional[str] = None,
    service: ProjectService = Depends(get_project_service)
):
    """Listar proyectos"""
    try:
        projects = service.get_projects(user_id=user_id, limit=limit, offset=offset)
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo proyectos: {str(e)}")

@router.post("/", response_model=Project)
async def create_project(
    name: str,
    description: Optional[str] = None,
    project_type: Optional[str] = None,
    user_id: Optional[str] = None,
    service: ProjectService = Depends(get_project_service)
):
    """Crear nuevo proyecto"""
    try:
        project = service.create_project(
            name=name,
            description=description,
            project_type=project_type,
            user_id=user_id
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando proyecto: {str(e)}")

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    user_id: Optional[str] = None,
    service: ProjectService = Depends(get_project_service)
):
    """Obtener proyecto por ID"""
    project = service.get_project(project_id, user_id=user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    project_type: Optional[str] = None,
    user_id: Optional[str] = None,
    service: ProjectService = Depends(get_project_service)
):
    """Actualizar proyecto"""
    project = service.update_project(
        project_id=project_id,
        name=name,
        description=description,
        project_type=project_type,
        user_id=user_id
    )
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    user_id: Optional[str] = None,
    service: ProjectService = Depends(get_project_service)
):
    """Eliminar proyecto (soft delete)"""
    success = service.delete_project(project_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"message": "Proyecto eliminado exitosamente"}

@router.get("/{project_id}/analytics")
async def get_project_analytics(
    project_id: str,
    user_id: Optional[str] = None,
    service: ProjectService = Depends(get_project_service)
):
    """Obtener analytics del proyecto"""
    analytics = service.get_project_analytics(project_id, user_id=user_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return analytics

@router.get("/{project_id}/conversations", response_model=List[Conversation])
async def get_project_conversations(
    project_id: str,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtener conversaciones del proyecto"""
    try:
        query = db.query(Conversation).filter(
            Conversation.project_id == project_id,
            Conversation.is_active == True
        )
        
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        
        conversations = query.order_by(Conversation.last_message_at.desc()).all()
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo conversaciones: {str(e)}")

@router.get("/{project_id}/summary")
async def generate_project_summary(
    project_id: str,
    user_id: Optional[str] = None,
    service: ProjectService = Depends(get_project_service)
):
    """Generar resumen del proyecto usando IA"""
    summary = service.generate_project_summary(project_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o resumen no disponible")
    return {"summary": summary}