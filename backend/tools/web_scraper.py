"""
Herramienta de web scraping usando BeautifulSoup.
Proporciona funcionalidades seguras para extraer contenido de páginas web.
"""

import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Comment
from typing import Dict, List, Any, Optional
import re
import json

from .base_tool import BaseTool, ToolResult

class WebScraper(BaseTool):
    """Herramienta para realizar web scraping de forma segura"""
    
    def __init__(self):
        super().__init__(
            name="web_scraper",
            description="Herramienta para realizar web scraping de páginas web de forma segura",
            timeout=60
        )
        
        # Headers para simular un navegador
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Elementos peligrosos a evitar
        self.dangerous_tags = ['script', 'style', 'embed', 'object', 'iframe', 'frame', 'frameset']
        
        # Patrones de URLs permitidas
        self.allowed_domains = None  # None significa todos los dominios
        self.max_content_length = 500000  # 500KB max
    
    def set_allowed_domains(self, domains: List[str]):
        """Establece dominios permitidos para el scraping"""
        self.allowed_domains = [d.lower() for d in domains]
    
    def _is_allowed_domain(self, url: str) -> bool:
        """Verifica si el dominio está permitido"""
        if self.allowed_domains is None:
            return True
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Verificar si el dominio está en la lista permitida
        for allowed_domain in self.allowed_domains:
            if domain == allowed_domain or domain.endswith('.' + allowed_domain):
                return True
        
        return False
    
    def _clean_html_content(self, soup: BeautifulSoup) -> str:
        """Limpia el contenido HTML y extrae texto"""
        # Remover comentarios HTML
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remover elementos peligrosos
        for tag in self.dangerous_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remover scripts inline y estilos
        for element in soup.find_all(['script', 'style']):
            element.decompose()
        
        # Remover elementos con eventos onclick, etc.
        for element in soup.find_all():
            # Remover atributos de eventos
            attrs_to_remove = [attr for attr in element.attrs if attr.startswith('on')]
            for attr in attrs_to_remove:
                del element.attrs[attr]
            
            # Remover atributos javascript:
            for attr, value in list(element.attrs.items()):
                if isinstance(value, str) and value.lower().startswith('javascript:'):
                    del element.attrs[attr]
        
        # Obtener solo texto visible (sin elementos script/style)
        text = soup.get_text()
        
        # Limpiar espacios en blanco múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrae datos estructurados comunes"""
        data = {}
        
        # Título de la página
        title_tag = soup.find('title')
        if title_tag:
            data['title'] = title_tag.get_text().strip()
        
        # Meta descripción
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            data['description'] = meta_desc['content'].strip()
        
        # Meta palabras clave
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            data['keywords'] = meta_keywords['content'].strip()
        
        # Headers H1-H6
        headers = {}
        for level in range(1, 7):
            h_tags = soup.find_all(f'h{level}')
            if h_tags:
                headers[f'h{level}'] = [h.get_text().strip() for h in h_tags]
        
        if headers:
            data['headers'] = headers
        
        # Enlaces
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            if text and href:
                # Convertir URLs relativas a absolutas
                if href.startswith('http'):
                    absolute_url = href
                else:
                    absolute_url = href  # El usuario debe proporcionar la URL base
                
                links.append({
                    'text': text,
                    'url': absolute_url
                })
        
        if links:
            data['links'] = links
        
        # Imágenes
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            title = img.get('title', '')
            
            images.append({
                'src': src,
                'alt': alt.strip() if alt else '',
                'title': title.strip() if title else ''
            })
        
        if images:
            data['images'] = images
        
        return data
    
    def scrape_url(self, url: str, extract_structured: bool = True, 
                   extract_text: bool = True, clean_html: bool = True) -> ToolResult:
        """
        Realiza scraping de una URL específica
        
        Args:
            url: URL a scrapear
            extract_structured: Si extraer datos estructurados
            extract_text: Si extraer texto plano
            clean_html: Si limpiar HTML (remover scripts, etc.)
            
        Returns:
            ToolResult con los datos extraídos
        """
        self.set_running()
        
        try:
            # Validar URL
            if not self.validate_url(url):
                return self.create_result(
                    success=False,
                    error=f"URL no válida: {url}"
                )
            
            # Verificar dominio permitido
            if not self._is_allowed_domain(url):
                return self.create_result(
                    success=False,
                    error=f"Dominio no permitido: {urlparse(url).netloc}"
                )
            
            # Realizar petición HTTP
            start_time = time.time()
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True
            )
            
            # Verificar status code
            if response.status_code != 200:
                return self.create_result(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.reason}"
                )
            
            # Verificar Content-Type
            content_type = response.headers.get('Content-Type', '').lower()
            if not content_type.startswith('text/html'):
                return self.create_result(
                    success=False,
                    error=f"Tipo de contenido no soportado: {content_type}"
                )
            
            # Leer contenido con límite
            content = response.text
            if len(content) > self.max_content_length:
                content = content[:self.max_content_length]
                self.logger.warning(f"Contenido truncado a {self.max_content_length} caracteres")
            
            # Parsear HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extraer datos
            result_data = {
                'url': url,
                'status_code': response.status_code,
                'content_length': len(content),
                'response_time': time.time() - start_time
            }
            
            if extract_text or clean_html:
                result_data['text'] = self._clean_html_content(soup)
            
            if extract_structured:
                result_data['structured'] = self._extract_structured_data(soup)
            
            self.set_completed()
            
            return self.create_result(
                success=True,
                data=result_data,
                url=url,
                content_length=len(content),
                response_time=time.time() - start_time
            )
            
        except requests.exceptions.Timeout:
            self.set_timeout()
            return self.create_result(
                success=False,
                error="Timeout en la petición HTTP"
            )
        
        except requests.exceptions.ConnectionError as e:
            self.set_failed(str(e))
            return self.create_result(
                success=False,
                error=f"Error de conexión: {str(e)}"
            )
        
        except Exception as e:
            return self.handle_exception(e)
    
    def scrape_multiple_urls(self, urls: List[str], **kwargs) -> Dict[str, ToolResult]:
        """
        Realiza scraping de múltiples URLs
        
        Args:
            urls: Lista de URLs a scrapear
            **kwargs: Argumentos adicionales para scrape_url
            
        Returns:
            Diccionario con resultados por URL
        """
        results = {}
        
        for i, url in enumerate(urls):
            self.logger.info(f"Procesando URL {i+1}/{len(urls)}: {url}")
            
            # Sanitizar URL
            sanitized_url = self.sanitize_input(url, max_length=200)
            
            # Ejecutar scraping
            result = self.scrape_url(sanitized_url, **kwargs)
            results[sanitized_url] = result
            
            # Pequeña pausa entre peticiones para no sobrecargar el servidor
            if i < len(urls) - 1:
                time.sleep(1)
        
        return results
    
    def extract_links(self, url: str) -> ToolResult:
        """Extrae todos los enlaces de una página web"""
        result = self.scrape_url(url, extract_structured=True, extract_text=False)
        
        if result.success:
            links = result.data.get('structured', {}).get('links', [])
            self.set_completed()
            return self.create_result(
                success=True,
                data=links,
                url=url,
                total_links=len(links)
            )
        
        return result
    
    def extract_text_only(self, url: str) -> ToolResult:
        """Extrae solo el texto limpio de una página web"""
        result = self.scrape_url(url, extract_structured=False, extract_text=True)
        
        if result.success:
            text = result.data.get('text', '')
            word_count = len(text.split()) if text else 0
            
            self.set_completed()
            return self.create_result(
                success=True,
                data={
                    'text': text,
                    'word_count': word_count,
                    'character_count': len(text)
                },
                url=url
            )
        
        return result
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Ejecuta la funcionalidad principal de web scraping
        
        Args:
            **kwargs: Argumentos que pueden incluir:
                - url: URL única a scrapear
                - urls: Lista de URLs a scrapear
                - operation: tipo de operación ('scrape', 'extract_links', 'extract_text')
                - extract_structured: si extraer datos estructurados
                - extract_text: si extraer texto
                
        Returns:
            ToolResult con el resultado de la operación
        """
        operation = kwargs.get('operation', 'scrape')
        
        if operation == 'extract_links':
            url = kwargs.get('url')
            if not url:
                return self.create_result(
                    success=False,
                    error="URL requerida para extraer enlaces"
                )
            return self.extract_links(url)
        
        elif operation == 'extract_text':
            url = kwargs.get('url')
            if not url:
                return self.create_result(
                    success=False,
                    error="URL requerida para extraer texto"
                )
            return self.extract_text_only(url)
        
        elif operation == 'scrape':
            urls = kwargs.get('urls', [])
            if not urls:
                return self.create_result(
                    success=False,
                    error="URLs requeridas para scraping"
                )
            
            if len(urls) == 1:
                return self.scrape_url(urls[0], **kwargs)
            else:
                return self.scrape_multiple_urls(urls, **kwargs)
        
        else:
            return self.create_result(
                success=False,
                error=f"Operación no reconocida: {operation}"
            )