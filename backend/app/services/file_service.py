"""
Servicio de gestión de archivos
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any, Tuple
import uuid
import os
import hashlib
import mimetypes
from datetime import datetime

from app.models.project import File, Project
from app.core.llm_router import LLMRouter

class FileService:
    """Servicio para gestión de archivos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_router: Optional[LLMRouter] = None
        
    def set_llm_router(self, llm_router: LLMRouter):
        """Set LLM router para análisis"""
        self.llm_router = llm_router
    
    def upload_file(
        self, 
        project_id: str,
        filename: str,
        content: bytes,
        user_id: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> File:
        """Subir archivo al proyecto"""
        
        # Validar proyecto
        project = self.db.query(Project).filter(
            and_(
                Project.id == project_id,
                Project.is_deleted == False
            )
        ).first()
        
        if not project:
            raise ValueError(f"Proyecto {project_id} no encontrado")
        
        # Calcular hash para deduplicación
        hash_sha256 = hashlib.sha256(content).hexdigest()
        size = len(content)
        
        # Determinar extension y mime type
        extension = os.path.splitext(filename)[1].lower()
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = "application/octet-stream"
        
        # Generar ruta de archivo
        file_id = str(uuid.uuid4())
        file_path = f"projects/{project_id}/files/{file_id}{extension}"
        
        # Verificar si existe un archivo con el mismo hash
        existing_file = self.db.query(File).filter(
            and_(
                File.hash_sha256 == hash_sha256,
                File.is_deleted == False
            )
        ).first()
        
        if existing_file:
            # Usar archivo existente (hard link o referencia)
            existing_file.metadata = {
                **existing_file.metadata,
                "referenced_projects": (
                    existing_file.metadata.get("referenced_projects", []) + [project_id]
                )
            }
            self.db.commit()
            return existing_file
        
        # Crear nuevo archivo
        file_obj = File(
            project_id=project_id,
            name=filename,
            path=file_path,
            size=size,
            mime_type=mime_type,
            extension=extension,
            hash_sha256=hash_sha256,
            metadata={"created_via": "upload", "original_size": size}
        )
        
        self.db.add(file_obj)
        self.db.commit()
        self.db.refresh(file_obj)
        
        # Aquí se escribiría el archivo físico al sistema de archivos
        # self._write_file_to_disk(file_path, content)
        
        return file_obj
    
    def get_file(self, file_id: str, user_id: Optional[str] = None) -> Optional[File]:
        """Obtener archivo por ID"""
        query = self.db.query(File).filter(
            and_(
                File.id == file_id,
                File.is_deleted == False
            )
        )
        
        if user_id:
            # Verificar que el usuario tenga acceso al proyecto
            query = query.join(Project).filter(
                and_(
                    Project.user_id == user_id,
                    Project.is_deleted == False
                )
            )
            
        return query.first()
    
    def get_project_files(
        self, 
        project_id: str, 
        user_id: Optional[str] = None,
        limit: int = 100, 
        offset: int = 0,
        file_type: Optional[str] = None
    ) -> List[File]:
        """Obtener archivos de un proyecto"""
        query = self.db.query(File).filter(
            and_(
                File.project_id == project_id,
                File.is_deleted == False
            )
        )
        
        if file_type:
            query = query.filter(File.extension.like(f"%.{file_type}"))
        
        if user_id:
            # Verificar acceso al proyecto
            query = query.join(Project).filter(Project.user_id == user_id)
        
        return query.order_by(desc(File.updated_at)).offset(offset).limit(limit).all()
    
    def update_file(
        self, 
        file_id: str,
        content: Optional[bytes] = None,
        name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Optional[File]:
        """Actualizar archivo"""
        file_obj = self.get_file(file_id, user_id)
        if not file_obj:
            return None
        
        if name is not None:
            file_obj.name = name
            # Actualizar extension si cambia el nombre
            new_extension = os.path.splitext(name)[1].lower()
            if new_extension != file_obj.extension:
                file_obj.extension = new_extension
                if not file_obj.mime_type:
                    mime_type, _ = mimetypes.guess_type(name)
                    file_obj.mime_type = mime_type or "application/octet-stream"
        
        if content is not None:
            # Recalcular hash y tamaño
            file_obj.hash_sha256 = hashlib.sha256(content).hexdigest()
            file_obj.size = len(content)
            file_obj.metadata = {
                **file_obj.metadata,
                "last_modified_via": "content_update"
            }
            # Aquí se escribiría el contenido al disco
            # self._write_file_to_disk(file_obj.path, content)
        
        file_obj.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(file_obj)
        
        return file_obj
    
    def delete_file(self, file_id: str, user_id: Optional[str] = None) -> bool:
        """Soft delete archivo"""
        file_obj = self.get_file(file_id, user_id)
        if not file_obj:
            return False
        
        file_obj.is_deleted = True
        file_obj.updated_at = datetime.utcnow()
        
        # Si el archivo es referenciado por múltiples proyectos, 
        # reducir referencias en lugar de eliminar
        referenced_projects = file_obj.metadata.get("referenced_projects", [])
        if len(referenced_projects) > 1:
            # Solo remover la referencia al proyecto actual
            if user_id:
                # Remover project_id de las referencias
                updated_refs = [p_id for p_id in referenced_projects if p_id != file_obj.project_id]
                file_obj.metadata["referenced_projects"] = updated_refs
        else:
            # Archivo es único, marcar como eliminado
            pass
        
        self.db.commit()
        return True
    
    def search_files(
        self, 
        query: str, 
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> List[File]:
        """Buscar archivos por nombre o contenido"""
        search_query = self.db.query(File).filter(
            and_(
                File.is_deleted == False,
                or_(
                    File.name.ilike(f"%{query}%"),
                    File.mime_type.ilike(f"%{query}%")
                )
            )
        )
        
        if project_id:
            search_query = search_query.filter(File.project_id == project_id)
        
        if file_type:
            search_query = search_query.filter(File.extension.like(f"%.{file_type}"))
        
        if user_id:
            search_query = search_query.join(Project).filter(
                and_(
                    Project.user_id == user_id,
                    Project.is_deleted == False
                )
            )
        
        return search_query.order_by(desc(File.updated_at)).limit(50).all()
    
    def get_file_preview(self, file_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Obtener preview del archivo (primeros KB para texto, metadata para binarios)"""
        file_obj = self.get_file(file_id, user_id)
        if not file_obj:
            return None
        
        # Aquí se leería el archivo del disco
        # Por ahora retornamos metadata
        return {
            "id": file_obj.id,
            "name": file_obj.name,
            "size": file_obj.size,
            "mime_type": file_obj.mime_type,
            "extension": file_obj.extension,
            "created_at": file_obj.created_at.isoformat(),
            "preview_available": file_obj.size < 10000,  # Preview solo para archivos < 10KB
            "is_text": file_obj.mime_type and file_obj.mime_type.startswith("text/"),
            "is_image": file_obj.mime_type and file_obj.mime_type.startswith("image/"),
            "metadata": file_obj.metadata
        }
    
    def get_duplicate_files(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Encontrar archivos duplicados"""
        # Query para encontrar archivos con el mismo hash
        query = self.db.query(File).filter(
            and_(
                File.is_deleted == False,
                File.hash_sha256.isnot(None)
            )
        )
        
        if user_id:
            query = query.join(Project).filter(Project.user_id == user_id)
        
        files = query.all()
        
        # Agrupar por hash
        duplicates = {}
        for file_obj in files:
            hash_key = file_obj.hash_sha256
            if hash_key not in duplicates:
                duplicates[hash_key] = []
            duplicates[hash_key].append(file_obj)
        
        # Retornar solo grupos con más de 1 archivo
        result = []
        for hash_key, file_list in duplicates.items():
            if len(file_list) > 1:
                result.append({
                    "hash": hash_key,
                    "count": len(file_list),
                    "files": [f.to_dict() for f in file_list],
                    "total_size": len(file_list) * file_list[0].size
                })
        
        return result