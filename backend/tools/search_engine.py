"""
Motor de búsqueda que utiliza APIs públicas como DuckDuckGo y Wikipedia.
Proporciona búsquedas web seguras y acceso a información de Wikipedia.
"""

import requests
import time
import json
from urllib.parse import quote, urljoin
from typing import Dict, List, Any, Optional
import re

from .base_tool import BaseTool, ToolResult

class SearchEngine(BaseTool):
    """Motor de búsqueda con soporte para DuckDuckGo y Wikipedia"""
    
    def __init__(self):
        super().__init__(
            name="search_engine",
            description="Motor de búsqueda que utiliza APIs públicas como DuckDuckGo y Wikipedia",
            timeout=60
        )
        
        # Headers para las peticiones HTTP
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/html, text/plain',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # URLs de APIs
        self.duckduckgo_api = "https://api.duckduckgo.com/"
        self.wikipedia_api = "https://es.wikipedia.org/api/rest_v1/"
        
        # Límites de resultados
        self.max_search_results = 10
        self.max_pages = 5  # Para búsqueda paginada
    
    def _make_request(self, url: str, params: Optional[Dict] = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Realiza una petición HTTP de forma segura
        
        Args:
            url: URL a solicitar
            params: Parámetros de la petición
            timeout: Timeout en segundos
            
        Returns:
            Datos de la respuesta
        """
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            # Intentar parsear como JSON, fallback a texto
            try:
                return response.json()
            except json.JSONDecodeError:
                return {'text': response.text, 'status_code': response.status_code}
                
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Timeout en petición a {url}")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Error de conexión: {str(e)}")
        except requests.exceptions.HTTPError as e:
            raise HTTPError(f"Error HTTP {e.response.status_code}: {e.response.reason}")
        except Exception as e:
            raise Exception(f"Error en petición: {str(e)}")
    
    def duckduckgo_search(self, query: str, safe_search: bool = True, 
                         region: str = "es-es") -> ToolResult:
        """
        Realiza búsqueda en DuckDuckGo
        
        Args:
            query: Consulta de búsqueda
            safe_search: Si activar búsqueda segura
            region: Región de búsqueda
            
        Returns:
            ToolResult con resultados de DuckDuckGo
        """
        self.set_running()
        
        try:
            # Sanitizar y validar consulta
            sanitized_query = self.sanitize_input(query, max_length=200)
            
            if not sanitized_query.strip():
                return self.create_result(
                    success=False,
                    error="Consulta de búsqueda vacía"
                )
            
            # Parámetros para DuckDuckGo Instant Answer API
            params = {
                'q': sanitized_query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            if safe_search:
                params['safe_search'] = 'moderate'
            
            params['region'] = region
            
            # Realizar petición
            start_time = time.time()
            data = self._make_request(self.duckduckgo_api, params, timeout=30)
            response_time = time.time() - start_time
            
            # Procesar resultados
            results = self._process_duckduckgo_results(data, sanitized_query)
            
            self.set_completed()
            
            return self.create_result(
                success=True,
                data=results,
                query=sanitized_query,
                source="duckduckgo",
                response_time=response_time,
                results_count=len(results.get('results', []))
            )
            
        except TimeoutError as e:
            self.set_timeout()
            return self.create_result(
                success=False,
                error=f"Timeout en búsqueda DuckDuckGo: {str(e)}"
            )
        except Exception as e:
            return self.handle_exception(e)
    
    def _process_duckduckgo_results(self, data: Dict, query: str) -> Dict[str, Any]:
        """Procesa los resultados de DuckDuckGo"""
        results = {
            'query': query,
            'results': [],
            'abstract': None,
            'related_topics': [],
            'definition': None,
            'instant_answer': None
        }
        
        # Instant Answer
        if data.get('Abstract'):
            results['instant_answer'] = {
                'text': data.get('Abstract', ''),
                'source': data.get('AbstractSource', ''),
                'url': data.get('AbstractURL', '')
            }
            results['abstract'] = data.get('Abstract', '')
        
        # Definition
        if data.get('Definition'):
            results['definition'] = {
                'text': data.get('Definition', ''),
                'source': data.get('DefinitionSource', ''),
                'url': data.get('DefinitionURL', '')
            }
        
        # Resultados de búsqueda principales
        if data.get('Results'):
            for item in data['Results'][:self.max_search_results]:
                results['results'].append({
                    'title': item.get('Text', ''),
                    'url': item.get('FirstURL', ''),
                    'snippet': item.get('Text', '')
                })
        
        # Tópicos relacionados
        if data.get('RelatedTopics'):
            for topic in data['RelatedTopics'][:10]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results['related_topics'].append({
                        'text': topic.get('Text', ''),
                        'url': topic.get('FirstURL', '')
                    })
        
        return results
    
    def wikipedia_search(self, query: str, limit: int = 5) -> ToolResult:
        """
        Busca en Wikipedia en español
        
        Args:
            query: Consulta de búsqueda
            limit: Límite de resultados
            
        Returns:
            ToolResult con resultados de Wikipedia
        """
        self.set_running()
        
        try:
            # Sanitizar y validar consulta
            sanitized_query = self.sanitize_input(query, max_length=200)
            
            if not sanitized_query.strip():
                return self.create_result(
                    success=False,
                    error="Consulta de búsqueda vacía"
                )
            
            # 1. Buscar páginas relacionadas
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': sanitized_query,
                'srlimit': min(limit, 10),
                'srprop': 'snippet|titlesnippet',
                'origin': '*'
            }
            
            start_time = time.time()
            search_data = self._make_request(
                "https://es.wikipedia.org/w/api.php",
                search_params,
                timeout=30
            )
            response_time = time.time() - start_time
            
            # 2. Obtener resumen de las páginas encontradas
            results = self._process_wikipedia_results(search_data, sanitized_query)
            
            self.set_completed()
            
            return self.create_result(
                success=True,
                data=results,
                query=sanitized_query,
                source="wikipedia",
                response_time=response_time,
                results_count=len(results.get('pages', []))
            )
            
        except TimeoutError as e:
            self.set_timeout()
            return self.create_result(
                success=False,
                error=f"Timeout en búsqueda Wikipedia: {str(e)}"
            )
        except Exception as e:
            return self.handle_exception(e)
    
    def _process_wikipedia_results(self, data: Dict, query: str) -> Dict[str, Any]:
        """Procesa los resultados de Wikipedia"""
        results = {
            'query': query,
            'pages': [],
            'total_hits': 0
        }
        
        if 'query' in data and 'search' in data['query']:
            search_results = data['query']['search']
            results['total_hits'] = data['query'].get('searchinfo', {}).get('totalhits', 0)
            
            for item in search_results:
                page_id = item['pageid']
                title = item['title']
                
                # Obtener resumen de la página
                summary = self._get_wikipedia_summary(page_id)
                
                page_info = {
                    'pageid': page_id,
                    'title': title,
                    'snippet': item.get('snippet', ''),
                    'size': item.get('size', 0),
                    'word_count': item.get('wordcount', 0),
                    'timestamp': item.get('timestamp', '')
                }
                
                if summary:
                    page_info['summary'] = summary
                    page_info['extract'] = summary.get('extract', '')
                    page_info['thumbnail'] = summary.get('thumbnail', {})
                    page_info['originalimage'] = summary.get('originalimage', {})
                
                results['pages'].append(page_info)
        
        return results
    
    def _get_wikipedia_summary(self, page_id: int) -> Optional[Dict]:
        """Obtiene el resumen de una página de Wikipedia"""
        try:
            summary_url = f"{self.wikipedia_api}page/summary/{page_id}"
            return self._make_request(summary_url, timeout=15)
        except Exception as e:
            self.logger.warning(f"Error obteniendo resumen para página {page_id}: {e}")
            return None
    
    def wikipedia_page(self, title: str) -> ToolResult:
        """
        Obtiene información completa de una página específica de Wikipedia
        
        Args:
            title: Título de la página
            
        Returns:
            ToolResult con información de la página
        """
        self.set_running()
        
        try:
            # Sanitizar título
            sanitized_title = self.sanitize_input(title, max_length=200).strip()
            
            if not sanitized_title:
                return self.create_result(
                    success=False,
                    error="Título de página vacío"
                )
            
            # URL encode del título
            encoded_title = quote(sanitized_title.replace(' ', '_'))
            
            start_time = time.time()
            
            # Obtener resumen
            summary_url = f"{self.wikipedia_api}page/summary/{encoded_title}"
            summary_data = self._make_request(summary_url, timeout=30)
            
            # Obtener contenido HTML (opcional)
            content_url = f"{self.wikipedia_api}page/html/{encoded_title}"
            try:
                content_data = self._make_request(content_url, timeout=30)
            except Exception:
                content_data = None
            
            response_time = time.time() - start_time
            
            # Procesar datos
            page_info = self._process_wikipedia_page_data(summary_data, content_data)
            
            self.set_completed()
            
            return self.create_result(
                success=True,
                data=page_info,
                page_title=sanitized_title,
                source="wikipedia",
                response_time=response_time
            )
            
        except TimeoutError as e:
            self.set_timeout()
            return self.create_result(
                success=False,
                error=f"Timeout obteniendo página Wikipedia: {str(e)}"
            )
        except Exception as e:
            return self.handle_exception(e)
    
    def _process_wikipedia_page_data(self, summary: Dict, content: Optional[Dict]) -> Dict[str, Any]:
        """Procesa datos de una página de Wikipedia"""
        page_info = {
            'title': summary.get('title', ''),
            'pageid': summary.get('pageid', 0),
            'extract': summary.get('extract', ''),
            'description': summary.get('description', ''),
            'type': summary.get('type', ''),
            'lang': summary.get('lang', 'es'),
            'content_urls': summary.get('content_urls', {}),
            'thumbnail': summary.get('thumbnail', {}),
            'originalimage': summary.get('originalimage', {}),
            'coordinates': summary.get('coordinates', {}),
            'titles': summary.get('titles', {}),
            'related': summary.get('related', [])
        }
        
        # Información adicional si está disponible
        if 'content_model' in summary:
            page_info['content_model'] = summary['content_model']
        
        if 'canonical_title' in summary:
            page_info['canonical_title'] = summary['canonical_title']
        
        # Contenido HTML si está disponible
        if content and 'text' in content:
            page_info['html_content'] = content['text']
            page_info['sections'] = content.get('sections', [])
        
        return page_info
    
    def web_search(self, query: str, sources: List[str] = ['duckduckgo', 'wikipedia']) -> ToolResult:
        """
        Realiza búsqueda web usando múltiples fuentes
        
        Args:
            query: Consulta de búsqueda
            sources: Lista de fuentes a usar
            
        Returns:
            ToolResult con resultados consolidados
        """
        self.set_running()
        
        try:
            sanitized_query = self.sanitize_input(query, max_length=200)
            
            if not sanitized_query.strip():
                return self.create_result(
                    success=False,
                    error="Consulta de búsqueda vacía"
                )
            
            all_results = {
                'query': sanitized_query,
                'sources': {},
                'summary': {},
                'timestamp': time.time()
            }
            
            # Ejecutar búsquedas en paralelo (simulado secuencialmente)
            for source in sources:
                try:
                    if source == 'duckduckgo':
                        result = self.duckduckgo_search(sanitized_query)
                        if result.success:
                            all_results['sources']['duckduckgo'] = result.data
                    
                    elif source == 'wikipedia':
                        result = self.wikipedia_search(sanitized_query)
                        if result.success:
                            all_results['sources']['wikipedia'] = result.data
                    
                    # Pequeña pausa entre peticiones
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.warning(f"Error en búsqueda {source}: {e}")
                    all_results['sources'][source] = {'error': str(e)}
            
            # Crear resumen consolidado
            all_results['summary'] = self._create_consolidated_summary(all_results['sources'])
            
            self.set_completed()
            
            return self.create_result(
                success=True,
                data=all_results,
                query=sanitized_query,
                sources_used=list(all_results['sources'].keys()),
                results_count=sum(len(source_data.get('results', [])) for source_data in all_results['sources'].values() if isinstance(source_data, dict))
            )
            
        except Exception as e:
            return self.handle_exception(e)
    
    def _create_consolidated_summary(self, sources_data: Dict) -> Dict[str, Any]:
        """Crea un resumen consolidado de todas las fuentes"""
        summary = {
            'total_sources': len(sources_data),
            'successful_sources': 0,
            'total_results': 0,
            'common_themes': [],
            'best_match': None
        }
        
        all_titles = []
        all_snippets = []
        
        for source, data in sources_data.items():
            if isinstance(data, dict) and 'error' not in data:
                summary['successful_sources'] += 1
                
                # Contar resultados
                if 'results' in data:
                    summary['total_results'] += len(data['results'])
                    for result in data['results']:
                        if result.get('title'):
                            all_titles.append(result['title'])
                        if result.get('snippet'):
                            all_snippets.append(result['snippet'])
                
                elif 'pages' in data:
                    summary['total_results'] += len(data['pages'])
                    for page in data['pages']:
                        if page.get('title'):
                            all_titles.append(page['title'])
                        if page.get('snippet'):
                            all_snippets.append(page['snippet'])
        
        # Intentar identificar temas comunes (análisis muy básico)
        if all_titles:
            # Palabras más comunes en títulos
            word_count = {}
            for title in all_titles:
                words = re.findall(r'\b\w+\b', title.lower())
                for word in words:
                    if len(word) > 3:  # Solo palabras de más de 3 caracteres
                        word_count[word] = word_count.get(word, 0) + 1
            
            # Top 3 palabras más comunes
            common_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:3]
            summary['common_themes'] = [word for word, count in common_words]
        
        return summary
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Ejecuta la funcionalidad principal del motor de búsqueda
        
        Args:
            **kwargs: Argumentos que pueden incluir:
                - query: Consulta de búsqueda
                - operation: tipo de operación ('search', 'duckduckgo', 'wikipedia', 'web_search')
                - sources: lista de fuentes para búsqueda web
                - title: título de página para Wikipedia
                - limit: límite de resultados
                - safe_search: si activar búsqueda segura
                
        Returns:
            ToolResult con el resultado de la operación
        """
        operation = kwargs.get('operation', 'search')
        query = kwargs.get('query')
        title = kwargs.get('title')
        
        if operation == 'duckduckgo':
            if not query:
                return self.create_result(
                    success=False,
                    error="Consulta requerida para búsqueda DuckDuckGo"
                )
            return self.duckduckgo_search(
                query,
                safe_search=kwargs.get('safe_search', True),
                region=kwargs.get('region', 'es-es')
            )
        
        elif operation == 'wikipedia':
            if not query:
                return self.create_result(
                    success=False,
                    error="Consulta requerida para búsqueda Wikipedia"
                )
            return self.wikipedia_search(
                query,
                limit=kwargs.get('limit', 5)
            )
        
        elif operation == 'wikipedia_page':
            if not title:
                return self.create_result(
                    success=False,
                    error="Título requerido para obtener página Wikipedia"
                )
            return self.wikipedia_page(title)
        
        elif operation == 'web_search':
            if not query:
                return self.create_result(
                    success=False,
                    error="Consulta requerida para búsqueda web"
                )
            return self.web_search(
                query,
                sources=kwargs.get('sources', ['duckduckgo', 'wikipedia'])
            )
        
        else:  # 'search' por defecto
            if not query:
                return self.create_result(
                    success=False,
                    error="Consulta requerida para búsqueda"
                )
            
            # Determinar tipo de búsqueda automáticamente
            # Si la consulta parece ser sobre un tema específico, usar búsqueda web
            return self.web_search(
                query,
                sources=kwargs.get('sources', ['duckduckgo', 'wikipedia'])
            )