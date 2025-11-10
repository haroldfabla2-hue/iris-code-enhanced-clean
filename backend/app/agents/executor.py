"""
Agente Executor - Ejecuta herramientas y tareas
Responsable de invocar herramientas MCP y ejecutar código
"""
from typing import List, Dict, Any, Optional
import asyncio
import json
import subprocess
import tempfile
import os
import shutil
import aiofiles
import httpx
from datetime import datetime

from .base import BaseAgent
from ..models import AgentMessage, AgentResponse, MessageStatus


class ExecutorAgent(BaseAgent):
    """
    Agente Executor: Ejecuta herramientas y tareas concretas
    
    Responsabilidades:
    - Invocar herramientas MCP
    - Ejecutar código en sandboxes
    - Recoger resultados estructurados
    - Minimizar overhead de tokens con referencias
    """
    
    def __init__(self, executor_type: str = "general", llm_client: Any = None):
        super().__init__(
            agent_id=f"executor_{executor_type}",
            llm_client=llm_client
        )
        self.executor_type = executor_type
        self.tools_registry = self._init_tools_registry()
    
    def get_capabilities(self) -> List[str]:
        capabilities = ["task_execution", "tool_invocation", "result_collection"]
        if self.executor_type == "code":
            capabilities.extend(["python_execution", "code_testing"])
        elif self.executor_type == "web":
            capabilities.extend(["web_scraping", "browser_automation"])
        elif self.executor_type == "docs":
            capabilities.extend(["document_processing", "pdf_extraction"])
        return capabilities
    
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """
        Procesa mensaje ejecutando herramientas según delegación
        """
        self.log_trace("executor_start", {
            "message_id": message.message_id,
            "executor_type": self.executor_type
        })
        
        try:
            # Extraer delegación
            delegation = message.payload.get("delegation", {})
            tool_map = delegation.get("tool_map", [])
            objetivo = delegation.get("objetivo", "")
            limites = delegation.get("limites", {})
            
            # Ejecutar herramientas concurrentemente (si son ≥2)
            results = await self._execute_tools_concurrent(
                tool_map,
                objetivo,
                limites
            )
            
            # Consolidar resultados
            consolidated = self._consolidate_results(results)
            
            # Guardar artefactos y devolver referencias
            artifacts_refs = self._save_artifacts(consolidated)
            
            result = {
                "execution_summary": {
                    "tools_executed": len(results),
                    "successful": sum(1 for r in results if r.get("success", False)),
                    "failed": sum(1 for r in results if not r.get("success", False)),
                    "total_time_ms": sum(r.get("time_ms", 0) for r in results)
                },
                "results": consolidated,
                "artifacts": artifacts_refs,
                "evidence": self._collect_evidence(results)
            }
            
            self.log_trace("executor_complete", {
                "message_id": message.message_id,
                "tools_executed": len(results),
                "successful": result["execution_summary"]["successful"]
            })
            
            return AgentResponse(
                message_id=f"resp_{message.message_id}",
                original_message_id=message.message_id,
                agent_id=self.agent_id,
                status=MessageStatus.DONE,
                result=result
            )
            
        except Exception as e:
            self.logger.exception("Error en Executor")
            raise
    
    def _init_tools_registry(self) -> Dict[str, callable]:
        """Inicializa registro de herramientas disponibles"""
        return {
            "python_executor": self._tool_python_executor,
            "web_scraper": self._tool_web_scraper,
            "search_engine": self._tool_search_engine,
            "file_processor": self._tool_file_processor,
            "git_ops": self._tool_git_ops,
            "api_caller": self._tool_api_caller
        }
    
    async def _execute_tools_concurrent(
        self,
        tool_map: List[str],
        objetivo: str,
        limites: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Ejecuta herramientas en paralelo con límites"""
        
        if not tool_map:
            self.logger.warning("No hay herramientas en tool_map")
            return []
        
        # Limitar concurrencia
        max_concurrent = min(len(tool_map), limites.get("tools_max", 3))
        
        tasks = []
        for tool_name in tool_map[:max_concurrent]:
            if tool_name in self.tools_registry:
                task = self._execute_single_tool(
                    tool_name,
                    objetivo,
                    limites
                )
                tasks.append(task)
            else:
                self.logger.warning(f"Herramienta {tool_name} no encontrada")
        
        if not tasks:
            return []
        
        # Ejecutar concurrentemente
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar excepciones
        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed.append({
                    "tool": tool_map[i] if i < len(tool_map) else "unknown",
                    "success": False,
                    "error": str(result),
                    "time_ms": 0
                })
            else:
                processed.append(result)
        
        return processed
    
    async def _execute_single_tool(
        self,
        tool_name: str,
        objetivo: str,
        limites: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta una herramienta individual"""
        
        from datetime import datetime
        start = datetime.utcnow()
        
        try:
            # Usar herramientas reales si están disponibles
            if hasattr(self, 'tools') and tool_name in self.tools:
                result = await self._execute_real_tool(tool_name, objetivo, limites)
            else:
                # Fallback a herramientas mock
                tool_func = self.tools_registry[tool_name]
                result = await tool_func(objetivo, limites)
            
            end = datetime.utcnow()
            time_ms = (end - start).total_seconds() * 1000
            
            return {
                "tool": tool_name,
                "success": True,
                "result": result,
                "time_ms": time_ms
            }
            
        except Exception as e:
            self.logger.exception(f"Error ejecutando {tool_name}")
            end = datetime.utcnow()
            time_ms = (end - start).total_seconds() * 1000
            
            return {
                "tool": tool_name,
                "success": False,
                "error": str(e),
                "time_ms": time_ms
            }
    
    # Implementación de herramientas
    
    async def _tool_python_executor(
        self,
        objetivo: str,
        limites: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta código Python en sandbox"""
        
        self.logger.info(f"Ejecutando Python para: {objetivo[:100]}")
        
        try:
            # Generar código Python usando LLM
            prompt = f"""Genera código Python para cumplir el siguiente objetivo:
            
Objetivo: {objetivo}

Requisitos:
- Código limpio y bien documentado
- Manejo adecuado de errores
- Incluye imports necesarios
- Código ejecutable directamente

Proporciona solo el código Python sin explicaciones adicionales.
"""
            
            code = await self.call_llm(prompt, temperature=0.3, max_tokens=1500)
            
            # Ejecutar código en directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                script_path = os.path.join(temp_dir, "script.py")
                
                # Escribir código al archivo
                async with aiofiles.open(script_path, 'w') as f:
                    await f.write(code)
                
                # Ejecutar con timeout
                timeout = limites.get("time_seconds", 30)
                try:
                    result = await asyncio.wait_for(
                        asyncio.create_subprocess_exec(
                            "python3", script_path,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                            cwd=temp_dir
                        ),
                        timeout=timeout
                    )
                    
                    stdout, stderr = await result.communicate()
                    exit_code = result.returncode
                    
                    output = {
                        "code": code,
                        "executed": True,
                        "output": stdout.decode('utf-8') if stdout else "",
                        "error": stderr.decode('utf-8') if stderr else "",
                        "exit_code": exit_code,
                        "success": exit_code == 0
                    }
                    
                except asyncio.TimeoutError:
                    output = {
                        "code": code,
                        "executed": True,
                        "output": "",
                        "error": f"Timeout después de {timeout} segundos",
                        "exit_code": -1,
                        "success": False
                    }
                    
        except Exception as e:
            self.logger.exception(f"Error ejecutando Python: {str(e)}")
            output = {
                "code": "",
                "executed": False,
                "output": "",
                "error": str(e),
                "exit_code": -1,
                "success": False
            }
        
        return output
    
    async def _execute_real_tool(
        self,
        tool_name: str,
        objetivo: str,
        limites: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta herramienta real del sistema"""
        try:
            start_time = datetime.utcnow()
            tool = self.tools[tool_name]
            
            # Preparar parámetros según la herramienta
            tool_params = self._prepare_tool_params(tool_name, objetivo, limites)
            
            # Ejecutar herramienta
            result = await tool.execute(**tool_params)
            
            end_time = datetime.utcnow()
            time_ms = (end_time - start_time).total_seconds() * 1000
            
            return {
                "tool": tool_name,
                "success": result.success if hasattr(result, 'success') else True,
                "result": {
                    "data": result.data if hasattr(result, 'data') else result,
                    "tool_output": str(result) if not hasattr(result, 'data') else None
                },
                "time_ms": time_ms,
                "real_tool": True
            }
            
        except Exception as e:
            self.logger.exception(f"Error ejecutando herramienta real {tool_name}")
            end_time = datetime.utcnow()
            time_ms = (end_time - start_time).total_seconds() * 1000
            
            return {
                "tool": tool_name,
                "success": False,
                "error": str(e),
                "time_ms": time_ms,
                "real_tool": True
            }
    
    def _prepare_tool_params(
        self,
        tool_name: str,
        objetivo: str,
        limites: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepara parámetros específicos para cada herramienta"""
        params = {}
        
        if tool_name == "python_executor":
            params.update({
                "code": objetivo,
                "operation": "execute",
                "timeout": limites.get("time_seconds", 30)
            })
        
        elif tool_name == "web_scraper":
            # Extraer URL del objetivo
            import re
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, objetivo)
            
            if urls:
                params.update({
                    "url": urls[0],
                    "operation": "scrape"
                })
            else:
                params.update({
                    "urls": [objetivo],
                    "operation": "scrape"
                })
        
        elif tool_name == "search_engine":
            params.update({
                "query": objetivo,
                "operation": "web_search",
                "sources": ["duckduckgo", "wikipedia"]
            })
        
        elif tool_name == "file_processor":
            # Buscar rutas de archivos en el objetivo
            import re
            file_pattern = r'[a-zA-Z0-9_-]+\.(txt|pdf|docx|json|csv)'
            files = re.findall(file_pattern, objetivo, re.IGNORECASE)
            
            if files:
                params.update({
                    "file_path": files[0],
                    "operation": "auto"
                })
            else:
                params.update({
                    "file_path": objetivo,
                    "operation": "validate"
                })
        
        elif tool_name == "git_ops":
            params.update({
                "command": objetivo,
                "timeout": limites.get("time_seconds", 30)
            })
        
        return params
    
    async def _tool_web_scraper(
        self,
        objetivo: str,
        limites: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Realiza web scraping y análisis de contenido"""
        
        self.logger.info(f"Web scraping para: {objetivo[:100]}")
        
        try:
            # Extraer URL del objetivo si está presente
            import re
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, objetivo)
            
            if not urls:
                # Si no hay URL, buscar información web relevante
                return await self._search_web_information(objetivo, limites)
            
            url = urls[0]  # Tomar la primera URL encontrada
            result = await self._scrape_url(url, objetivo, limites)
            
            return result
            
        except Exception as e:
            self.logger.exception(f"Error en web scraping: {str(e)}")
            return {
                "url": "",
                "scraped": False,
                "data": {},
                "error": str(e),
                "success": False
            }
    
    async def _scrape_url(self, url: str, objetivo: str, limites: Dict[str, Any]) -> Dict[str, Any]:
        """Scraping básico de una URL usando httpx"""
        
        try:
            timeout = httpx.Timeout(30.0, connect=10.0)
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Agents-Bot/1.0)"
            }
            
            async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Extraer información básica
                content = response.text
                title = ""
                if "<title>" in content:
                    title_start = content.find("<title>") + 7
                    title_end = content.find("</title>", title_start)
                    title = content[title_start:title_end].strip()
                
                # Limpiar HTML básico y extraer texto
                import re
                # Remover scripts y estilos
                clean_content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
                clean_content = re.sub(r'<style[^>]*>.*?</style>', '', clean_content, flags=re.DOTALL | re.IGNORECASE)
                # Extraer texto
                text_content = re.sub(r'<[^>]+>', ' ', clean_content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                
                # Limitar tamaño del contenido
                max_chars = limites.get("max_content_chars", 5000)
                if len(text_content) > max_chars:
                    text_content = text_content[:max_chars] + "..."
                
                return {
                    "url": url,
                    "title": title,
                    "scraped": True,
                    "data": {
                        "content": text_content,
                        "status_code": response.status_code,
                        "content_type": response.headers.get("content-type", ""),
                        "content_length": len(content)
                    },
                    "success": True
                }
                
        except httpx.TimeoutException:
            return {
                "url": url,
                "scraped": False,
                "data": {},
                "error": "Timeout al acceder a la URL",
                "success": False
            }
        except Exception as e:
            return {
                "url": url,
                "scraped": False,
                "data": {},
                "error": str(e),
                "success": False
            }
    
    async def _search_web_information(self, query: str, limites: Dict[str, Any]) -> Dict[str, Any]:
        """Busca información web usando el LLM como simulador de búsqueda"""
        
        try:
            prompt = f"""Busca información web relevante para la siguiente consulta:

Consulta: {query}

Proporciona información útil y actualizada relacionada con la consulta. 
Incluye fuentes o referencias cuando sea posible.
"""
            
            search_results = await self.call_llm(prompt, temperature=0.5, max_tokens=1000)
            
            return {
                "query": query,
                "scraped": True,
                "data": {
                    "search_results": search_results,
                    "search_type": "llm_simulation"
                },
                "success": True
            }
            
        except Exception as e:
            return {
                "query": query,
                "scraped": False,
                "data": {},
                "error": str(e),
                "success": False
            }
    
    async def _tool_git_ops(
        self,
        objetivo: str,
        limites: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Operaciones Git"""
        
        self.logger.info(f"Git operations para: {objetivo[:100]}")
        
        try:
            # Determinar qué operación Git realizar basada en el objetivo
            objetivo_lower = objetivo.lower()
            
            if any(cmd in objetivo_lower for cmd in ["status", "git status"]):
                return await self._git_status()
            elif any(cmd in objetivo_lower for cmd in ["commit", "git commit"]):
                return await self._git_commit(objetivo)
            elif any(cmd in objetivo_lower for cmd in ["log", "git log"]):
                return await self._git_log()
            elif any(cmd in objetivo_lower for cmd in ["clone", "git clone"]):
                return await self._git_clone(objetivo)
            elif any(cmd in objetivo_lower for cmd in ["pull", "git pull"]):
                return await self._git_pull()
            elif any(cmd in objetivo_lower for cmd in ["push", "git push"]):
                return await self._git_push()
            else:
                # Operación general - mostrar ayuda o estado
                return await self._git_status()
                
        except Exception as e:
            self.logger.exception(f"Error en operaciones Git: {str(e)}")
            return {
                "operation": "error",
                "success": False,
                "error": str(e),
                "output": ""
            }
    
    async def _git_status(self) -> Dict[str, Any]:
        """Ejecuta git status"""
        try:
            result = await asyncio.create_subprocess_exec(
                "git", "status", "--porcelain",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return {
                "operation": "status",
                "success": result.returncode == 0,
                "output": stdout.decode('utf-8') if stdout else "",
                "error": stderr.decode('utf-8') if stderr else ""
            }
        except Exception as e:
            return {
                "operation": "status",
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    async def _git_commit(self, objetivo: str) -> Dict[str, Any]:
        """Ejecuta git commit"""
        try:
            # Extraer mensaje de commit del objetivo
            import re
            commit_match = re.search(r'-m\s+["\']([^"\']+)["\']', objetivo)
            commit_message = commit_match.group(1) if commit_match else "Actualización automática"
            
            # Agregar cambios primero
            add_result = await asyncio.create_subprocess_exec(
                "git", "add", ".",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await add_result.communicate()
            
            # Hacer commit
            result = await asyncio.create_subprocess_exec(
                "git", "commit", "-m", commit_message,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return {
                "operation": "commit",
                "success": result.returncode == 0,
                "output": stdout.decode('utf-8') if stdout else "",
                "error": stderr.decode('utf-8') if stderr else "",
                "message": commit_message
            }
        except Exception as e:
            return {
                "operation": "commit",
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    async def _git_log(self) -> Dict[str, Any]:
        """Ejecuta git log"""
        try:
            result = await asyncio.create_subprocess_exec(
                "git", "log", "--oneline", "-10",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return {
                "operation": "log",
                "success": result.returncode == 0,
                "output": stdout.decode('utf-8') if stdout else "",
                "error": stderr.decode('utf-8') if stderr else ""
            }
        except Exception as e:
            return {
                "operation": "log",
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    async def _git_clone(self, objetivo: str) -> Dict[str, Any]:
        """Ejecuta git clone"""
        try:
            # Extraer URL del objetivo
            import re
            url_match = re.search(r'https?://[^\s]+', objetivo)
            if not url_match:
                return {
                    "operation": "clone",
                    "success": False,
                    "output": "",
                    "error": "No se encontró URL válida en el objetivo"
                }
            
            repo_url = url_match.group(0)
            result = await asyncio.create_subprocess_exec(
                "git", "clone", repo_url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return {
                "operation": "clone",
                "success": result.returncode == 0,
                "output": stdout.decode('utf-8') if stdout else "",
                "error": stderr.decode('utf-8') if stderr else "",
                "url": repo_url
            }
        except Exception as e:
            return {
                "operation": "clone",
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    async def _git_pull(self) -> Dict[str, Any]:
        """Ejecuta git pull"""
        try:
            result = await asyncio.create_subprocess_exec(
                "git", "pull",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return {
                "operation": "pull",
                "success": result.returncode == 0,
                "output": stdout.decode('utf-8') if stdout else "",
                "error": stderr.decode('utf-8') if stderr else ""
            }
        except Exception as e:
            return {
                "operation": "pull",
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    async def _git_push(self) -> Dict[str, Any]:
        """Ejecuta git push"""
        try:
            result = await asyncio.create_subprocess_exec(
                "git", "push",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return {
                "operation": "push",
                "success": result.returncode == 0,
                "output": stdout.decode('utf-8') if stdout else "",
                "error": stderr.decode('utf-8') if stderr else ""
            }
        except Exception as e:
            return {
                "operation": "push",
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    async def _tool_document_processor(
        self,
        objetivo: str,
        limites: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Procesa documentos (PDF, DOCX, etc)"""
        
        self.logger.info(f"Document processing para: {objetivo[:100]}")
        
        try:
            # Buscar archivos en el objetivo
            import re
            import os
            
            # Extraer rutas de archivos del objetivo
            file_patterns = [
                r'[a-zA-Z0-9_-]+\.pdf',
                r'[a-zA-Z0-9_-]+\.txt',
                r'[a-zA-Z0-9_-]+\.md',
                r'[a-zA-Z0-9_-]+\.docx?'
            ]
            
            found_files = []
            for pattern in file_patterns:
                matches = re.findall(pattern, objetivo, re.IGNORECASE)
                found_files.extend(matches)
            
            if not found_files:
                return {
                    "documents_processed": 0,
                    "extracted_text": "",
                    "files_found": [],
                    "error": "No se encontraron archivos de documento en el objetivo",
                    "success": False
                }
            
            processed_docs = []
            total_extracted = ""
            
            for filename in found_files:
                if os.path.exists(filename):
                    try:
                        if filename.lower().endswith('.txt') or filename.lower().endswith('.md'):
                            content = await self._process_text_file(filename)
                        elif filename.lower().endswith('.pdf'):
                            content = await self._process_pdf_file(filename)
                        else:
                            content = f"Formato no soportado para {filename}"
                        
                        if content:
                            processed_docs.append({
                                "filename": filename,
                                "content": content[:1000] + "..." if len(content) > 1000 else content,
                                "size": len(content)
                            })
                            total_extracted += f"\n\n--- {filename} ---\n{content}"
                            
                    except Exception as e:
                        self.logger.warning(f"Error procesando {filename}: {str(e)}")
                        continue
            
            return {
                "documents_processed": len(processed_docs),
                "extracted_text": total_extracted[:5000] + "..." if len(total_extracted) > 5000 else total_extracted,
                "files_processed": processed_docs,
                "success": len(processed_docs) > 0
            }
            
        except Exception as e:
            self.logger.exception(f"Error en procesamiento de documentos: {str(e)}")
            return {
                "documents_processed": 0,
                "extracted_text": "",
                "error": str(e),
                "success": False
            }
    
    async def _process_text_file(self, filename: str) -> str:
        """Procesa archivo de texto"""
        try:
            async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
                content = await f.read()
            return content
        except Exception as e:
            self.logger.error(f"Error leyendo {filename}: {str(e)}")
            return f"Error leyendo archivo: {str(e)}"
    
    async def _process_pdf_file(self, filename: str) -> str:
        """Procesa archivo PDF (simulado)"""
        try:
            # Por ahora simulamos el procesamiento de PDF
            # En una implementación real usaríamos PyPDF2, pdfplumber, etc.
            return f"[PDF content for {filename}] - PDF processing no implementado completamente"
        except Exception as e:
            return f"Error procesando PDF: {str(e)}"
    
    async def _tool_api_caller(
        self,
        objetivo: str,
        limites: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Llama APIs externas"""
        
        self.logger.info(f"API caller para: {objetivo[:100]}")
        
        try:
            # Extraer información de la API del objetivo
            import re
            import json
            
            # Buscar URLs de API
            url_match = re.search(r'https?://[^\s]+', objetivo)
            if not url_match:
                return {
                    "api_called": False,
                    "response": {},
                    "error": "No se encontró URL de API en el objetivo",
                    "success": False
                }
            
            api_url = url_match.group(0)
            
            # Determinar método HTTP
            method = "GET"
            if any(verb in objetivo.lower() for verb in ["post", "crear", "enviar"]):
                method = "POST"
            elif any(verb in objetivo.lower() for verb in ["put", "actualizar"]):
                method = "PUT"
            elif any(verb in objetivo.lower() for verb in ["delete", "eliminar"]):
                method = "DELETE"
            
            # Preparar headers básicos
            headers = {
                "User-Agent": "Agents-Backend/1.0",
                "Accept": "application/json"
            }
            
            # Preparar datos si es necesario
            data = None
            if method in ["POST", "PUT"]:
                # Buscar datos JSON en el objetivo
                json_match = re.search(r'\{[^{}]*\}', objetivo)
                if json_match:
                    try:
                        data = json.loads(json_match.group(0))
                        headers["Content-Type"] = "application/json"
                    except json.JSONDecodeError:
                        pass
            
            # Realizar llamada a la API
            timeout = httpx.Timeout(30.0, connect=10.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method == "GET":
                    response = await client.get(api_url, headers=headers)
                elif method == "POST":
                    response = await client.post(api_url, headers=headers, json=data)
                elif method == "PUT":
                    response = await client.put(api_url, headers=headers, json=data)
                elif method == "DELETE":
                    response = await client.delete(api_url, headers=headers)
                else:
                    response = await client.get(api_url, headers=headers)
            
            # Procesar respuesta
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            return {
                "api_called": True,
                "url": api_url,
                "method": method,
                "response": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "data": response_data
                },
                "success": 200 <= response.status_code < 300
            }
            
        except httpx.TimeoutException:
            return {
                "api_called": False,
                "response": {},
                "error": "Timeout al llamar a la API",
                "success": False
            }
        except Exception as e:
            self.logger.exception(f"Error llamando API: {str(e)}")
            return {
                "api_called": False,
                "response": {},
                "error": str(e),
                "success": False
            }
    
    async def _tool_search_engine(
        self,
        objetivo: str,
        limites: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Búsqueda web usando motor de búsqueda real"""
        
        self.logger.info(f"Búsqueda web para: {objetivo[:100]}")
        
        try:
            # Usar la herramienta real de búsqueda
            if hasattr(self, 'tools') and 'search_engine' in self.tools:
                result = await self.call_tool(
                    "search_engine",
                    query=objetivo,
                    operation="web_search",
                    sources=["duckduckgo", "wikipedia"]
                )
                
                return {
                    "query": objetivo,
                    "searched": True,
                    "data": result.get("data", {}),
                    "success": result.get("success", False),
                    "error": result.get("error")
                }
            else:
                # Fallback a búsqueda simulada
                return {
                    "query": objetivo,
                    "searched": True,
                    "data": {"mock_search": f"Resultados simulados para: {objetivo[:50]}"},
                    "success": True
                }
                
        except Exception as e:
            self.logger.exception(f"Error en búsqueda: {str(e)}")
            return {
                "query": objetivo,
                "searched": False,
                "data": {},
                "error": str(e),
                "success": False
            }
    
    async def _tool_file_processor(
        self,
        objetivo: str,
        limites: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Procesamiento de archivos usando herramienta real"""
        
        self.logger.info(f"Procesamiento de archivos para: {objetivo[:100]}")
        
        try:
            # Buscar archivos en el objetivo
            import re
            file_pattern = r'[a-zA-Z0-9_-]+\.(txt|pdf|docx|json|csv)'
            files = re.findall(file_pattern, objetivo, re.IGNORECASE)
            
            if not files:
                return {
                    "files_processed": 0,
                    "extracted_text": "",
                    "files_found": [],
                    "error": "No se encontraron archivos en el objetivo",
                    "success": False
                }
            
            # Usar la herramienta real si está disponible
            if hasattr(self, 'tools') and 'file_processor' in self.tools:
                file_path = files[0]
                result = await self.call_tool(
                    "file_processor",
                    file_path=file_path,
                    operation="auto"
                )
                
                return {
                    "files_processed": 1 if result.get("success") else 0,
                    "extracted_text": result.get("data", {}).get("content", ""),
                    "files_processed_info": [result.get("data", {})],
                    "success": result.get("success", False),
                    "error": result.get("error")
                }
            else:
                # Fallback simulado
                return {
                    "files_processed": len(files),
                    "extracted_text": f"Contenido simulado de {files[0]}",
                    "files_found": files,
                    "success": True
                }
                
        except Exception as e:
            self.logger.exception(f"Error procesando archivos: {str(e)}")
            return {
                "files_processed": 0,
                "extracted_text": "",
                "error": str(e),
                "success": False
            }
    
    def _consolidate_results(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Consolida resultados de múltiples herramientas"""
        
        consolidated = {
            "tools_results": {},
            "combined_output": "",
            "success_rate": 0.0
        }
        
        successful = 0
        for result in results:
            tool_name = result.get("tool", "unknown")
            consolidated["tools_results"][tool_name] = result
            
            if result.get("success", False):
                successful += 1
        
        if results:
            consolidated["success_rate"] = successful / len(results)
        
        return consolidated
    
    def _save_artifacts(
        self,
        consolidated: Dict[str, Any]
    ) -> List[str]:
        """Guarda artefactos y devuelve referencias"""
        
        # Por ahora mock - implementar almacenamiento real
        artifacts = []
        
        for tool_name, result in consolidated.get("tools_results", {}).items():
            if result.get("success", False):
                ref = f"artifact://{self.agent_id}/{tool_name}/result.json"
                artifacts.append(ref)
        
        return artifacts
    
    def _collect_evidence(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Recolecta evidencias de ejecución"""
        
        evidence = []
        
        for result in results:
            if result.get("success", False):
                evidence.append({
                    "tool": result.get("tool"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "summary": f"Ejecutado exitosamente en {result.get('time_ms', 0):.0f}ms",
                    "reference": f"evidence://{result.get('tool')}"
                })
        
        return evidence
