"""
Servicio de gestión de proyectos
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
import uuid
import os
import shutil
import json
from datetime import datetime

from app.models.project import Project, File
from app.orchestrator import MultiAgentOrchestrator
from app.core.llm_router import LLMRouter

class ProjectService:
    """Servicio para gestión de proyectos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator: Optional[MultiAgentOrchestrator] = None
        self.llm_router: Optional[LLMRouter] = None
        
    def set_orchestrator(self, orchestrator: MultiAgentOrchestrator):
        """Set orchestrator para análisis con IA"""
        self.orchestrator = orchestrator
        
    def set_llm_router(self, llm_router: LLMRouter):
        """Set LLM router para análisis"""
        self.llm_router = llm_router
    
    def create_project(
        self, 
        name: str, 
        description: Optional[str] = None,
        user_id: Optional[str] = None,
        project_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Project:
        """Crear nuevo proyecto"""
        
        # Validar nombre único por usuario
        existing = self.db.query(Project).filter(
            and_(
                Project.name == name,
                Project.user_id == user_id,
                Project.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"Proyecto '{name}' ya existe para el usuario {user_id}")
        
        # Crear proyecto
        project = Project(
            name=name,
            description=description,
            user_id=user_id,
            project_type=project_type,
            metadata=metadata or {}
        )
        
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        # Crear directorio de archivos
        self._create_project_directory(project.id)
        
        return project
    
    def get_project(self, project_id: str, user_id: Optional[str] = None) -> Optional[Project]:
        """Obtener proyecto por ID"""
        query = self.db.query(Project).filter(
            and_(
                Project.id == project_id,
                Project.is_deleted == False
            )
        )
        
        if user_id:
            query = query.filter(Project.user_id == user_id)
            
        return query.first()
    
    def get_projects(
        self, 
        user_id: Optional[str] = None, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Project]:
        """Obtener lista de proyectos"""
        query = self.db.query(Project).filter(
            Project.is_deleted == False
        )
        
        if user_id:
            query = query.filter(Project.user_id == user_id)
        
        return query.order_by(desc(Project.last_activity)).offset(offset).limit(limit).all()
    
    def update_project(
        self, 
        project_id: str, 
        name: Optional[str] = None,
        description: Optional[str] = None,
        project_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Optional[Project]:
        """Actualizar proyecto"""
        project = self.get_project(project_id, user_id)
        if not project:
            return None
        
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if project_type is not None:
            project.project_type = project_type
        if metadata is not None:
            project.metadata = metadata
            
        project.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def delete_project(self, project_id: str, user_id: Optional[str] = None) -> bool:
        """Soft delete proyecto"""
        project = self.get_project(project_id, user_id)
        if not project:
            return False
        
        project.is_deleted = True
        project.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Opcional: eliminar archivos físicos después de un período de gracia
        # self._schedule_directory_cleanup(project.id)
        
        return True
    
    def get_project_analytics(self, project_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtener analytics del proyecto"""
        project = self.get_project(project_id, user_id)
        if not project:
            return {}
        
        # Contar archivos
        files_count = self.db.query(File).filter(
            and_(
                File.project_id == project_id,
                File.is_deleted == False
            )
        ).count()
        
        # Calcular tamaño total
        size_result = self.db.query(File.size).filter(
            and_(
                File.project_id == project_id,
                File.is_deleted == False
            )
        ).all()
        
        total_size = sum(result[0] for result in size_result) if size_result else 0
        
        # Tipos de archivos
        file_types_result = self.db.query(
            File.extension,
            File.size
        ).filter(
            and_(
                File.project_id == project_id,
                File.is_deleted == False
            )
        ).all()
        
        file_types = {}
        for ext, size in file_types_result:
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "project_id": project_id,
            "name": project.name,
            "files_count": files_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "created_at": project.created_at.isoformat(),
            "last_activity": project.last_activity.isoformat()
        }
    
    def _create_project_directory(self, project_id: str):
        """Crear directorio físico para el proyecto"""
        # Este es un path relativo, la implementación real dependerá del mounting
        project_path = f"projects/{project_id}"
        
        # En la implementación real, se debería crear el directorio en el volumen mountado
        # Por ahora, solo registramos la acción
        pass
    
    def generate_project_summary(self, project_id: str) -> Optional[str]:
        """Generar resumen del proyecto usando IA"""
        project = self.get_project(project_id)
        if not project or not self.orchestrator:
            return None
        
        # Obtener información del proyecto
        files = self.db.query(File).filter(
            and_(
                File.project_id == project_id,
                File.is_deleted == False
            )
        ).all()
        
        # Crear contexto
        context = {
            "project": {
                "name": project.name,
                "description": project.description,
                "type": project.project_type,
                "created_at": project.created_at.isoformat(),
            },
            "files": [
                {
                    "name": f.name,
                    "type": f.extension,
                    "size": f.size,
                    "mime_type": f.mime_type
                } for f in files
            ]
        }
        
        # Generar resumen con orquestador
        summary_prompt = f"""
        Analiza este proyecto y genera un resumen descriptivo:
        
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        Proporciona:
        1. Resumen general del proyecto
        2. Propósito y funcionalidades
        3. Tecnologías aparentes
        4. Recomendaciones de desarrollo
        """
        
        # Esta implementación dependerá del orchestrator disponible
        return f"Proyecto {project.name} con {len(files)} archivos."