"""
Servicio de Generación de Assets en Tiempo Real para IRIS
Permite generar cualquier tipo de asset via chat
"""
import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.services.image_generation_service import ImageGenerationService
from app.services.web_generation_service import WebGenerationService

class AssetGenerationService:
    """Servicio especializado en generación de assets para IRIS"""
    
    def __init__(self, llm_router: LLMRouter = None):
        self.llm_router = llm_router
        self.image_service = ImageGenerationService()
        self.web_service = WebGenerationService()
        self.assets_dir = Path("/workspace/generated_assets")
        self.assets_dir.mkdir(exist_ok=True)
        
        # Categorías de assets disponibles
        self.asset_categories = {
            "branding": {
                "description": "Logos corporativos, iconos, identidad visual",
                "formats": ["svg", "png", "ai", "psd"],
                "templates": ["logo_corporativo", "icono_app", "tarjetas_presentacion"]
            },
            "mobile_ui": {
                "description": "Interfaces de aplicaciones móviles, app icons",
                "formats": ["svg", "png", "figma", "sketch"],
                "templates": ["app_icon", "wireframe_mobile", "ui_kit"]
            },
            "marketing": {
                "description": "Landing pages, banners, contenido marketing",
                "formats": ["html", "css", "png", "jpg"],
                "templates": ["landing_page", "banner_social", "newsletter"]
            },
            "saas_platform": {
                "description": "Dashboards, interfaces SaaS, analíticas",
                "formats": ["html", "css", "js", "png"],
                "templates": ["dashboard_analytics", "admin_panel", "métricas"]
            },
            "ecommerce": {
                "description": "Páginas de producto, carritos, checkout",
                "formats": ["html", "css", "js", "png"],
                "templates": ["producto_page", "cart_page", "checkout"]
            },
            "executive": {
                "description": "Presentaciones ejecutivas, reportes",
                "formats": ["html", "css", "pdf", "pptx"],
                "templates": ["presentacion", "reporte", "pitch"]
            },
            "ai_stress_test": {
                "description": "Pruebas de IA, arquitecturas, demos técnicos",
                "formats": ["html", "css", "js", "py"],
                "templates": ["ai_demo", "arquitectura", "test_suite"]
            }
        }
    
    async def generate_asset(self, 
                           prompt: str, 
                           category: str = None,
                           format_type: str = None,
                           style: str = "modern",
                           requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Genera un asset basado en prompt y especificaciones
        
        Args:
            prompt: Descripción detallada del asset
            category: Categoría del asset (branding, marketing, etc.)
            format_type: Formato específico (svg, html, png, etc.)
            style: Estilo visual (modern, corporate, creative, etc.)
            requirements: Requerimientos específicos del usuario
            
        Returns:
            Dict con información del asset generado
        """
        try:
            # 1. Análisis del prompt con IA
            analysis = await self._analyze_prompt(prompt)
            
            # 2. Detectar categoría automáticamente si no se proporciona
            if not category:
                category = analysis.get("detected_category", "marketing")
            
            # 3. Determinar formato óptimo
            if not format_type:
                format_type = self._determine_optimal_format(category, analysis)
            
            # 4. Generar el asset
            generation_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            result = {
                "generation_id": generation_id,
                "timestamp": timestamp,
                "original_prompt": prompt,
                "analysis": analysis,
                "category": category,
                "format": format_type,
                "style": style,
                "requirements": requirements or {},
                "status": "generating",
                "files": [],
                "metadata": {}
            }
            
            # 5. Generar según el tipo
            if format_type in ["svg", "png", "jpg", "jpeg"]:
                # Asset visual (imagen)
                generated_file = await self._generate_visual_asset(
                    prompt, format_type, style, generation_id, timestamp
                )
                result["files"].append(generated_file)
                result["type"] = "visual"
                
            elif format_type == "html":
                # Página web
                generated_files = await self._generate_web_asset(
                    prompt, style, requirements, generation_id, timestamp
                )
                result["files"].extend(generated_files)
                result["type"] = "web"
                
            elif format_type in ["py", "js", "ts"]:
                # Código/aplicación
                generated_file = await self._generate_code_asset(
                    prompt, format_type, style, requirements, generation_id, timestamp
                )
                result["files"].append(generated_file)
                result["type"] = "code"
            
            result["status"] = "completed"
            result["generation_time"] = result["metadata"].get("generation_time", 0)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "generation_id": generation_id if 'generation_id' in locals() else str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analiza el prompt para extraer información clave"""
        if not self.llm_router:
            # Fallback básico sin LLM
            return self._basic_prompt_analysis(prompt)
        
        analysis_prompt = f"""
        Analiza este prompt para generar un asset y extrae la siguiente información:
        
        PROMPT: {prompt}
        
        Proporciona un análisis JSON con:
        - detected_category: Una de las categorías: branding, mobile_ui, marketing, saas_platform, ecommerce, executive, ai_stress_test
        - asset_type: Tipo específico (logo, icon, landing_page, dashboard, etc.)
        - complexity: simple, medium, complex
        - colors: Lista de colores sugeridos
        - style_indicators: Lista de palabras clave de estilo
        - target_audience: Audiencia objetivo
        - key_features: Lista de características principales
        
        Responde solo en formato JSON válido.
        """
        
        try:
            response = await self.llm_router.chat_completion(analysis_prompt)
            # Intentar parsear JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Error en análisis LLM: {e}")
        
        return self._basic_prompt_analysis(prompt)
    
    def _basic_prompt_analysis(self, prompt: str) -> Dict[str, Any]:
        """Análisis básico sin LLM"""
        prompt_lower = prompt.lower()
        
        # Detectar categoría por palabras clave
        category_keywords = {
            "branding": ["logo", "branding", "identidad", "marca", "corporativo"],
            "mobile_ui": ["app", "móvil", "mobile", "icono", "ui", "interfaz"],
            "marketing": ["landing", "marketing", "publicidad", "banner", "promocional"],
            "saas_platform": ["dashboard", "analytics", "métricas", "plataforma", "saas"],
            "ecommerce": ["ecommerce", "tienda", "producto", "compra", "carrito"],
            "executive": ["presentación", "ejecutivo", "reporte", "pitch", "business"],
            "ai_stress_test": ["ia", "ai", "inteligencia", "artificial", "test", "demo"]
        }
        
        detected_category = "marketing"  # default
        for category, keywords in category_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_category = category
                break
        
        return {
            "detected_category": detected_category,
            "asset_type": "custom",
            "complexity": "medium",
            "colors": ["#2563EB", "#64748B"],
            "style_indicators": ["modern", "clean"],
            "target_audience": "general",
            "key_features": ["responsive", "professional"]
        }
    
    def _determine_optimal_format(self, category: str, analysis: Dict[str, Any]) -> str:
        """Determina el formato óptimo basado en categoría y análisis"""
        format_map = {
            "branding": "svg",
            "mobile_ui": "svg", 
            "marketing": "html",
            "saas_platform": "html",
            "ecommerce": "html",
            "executive": "html",
            "ai_stress_test": "html"
        }
        return format_map.get(category, "html")
    
    async def _generate_visual_asset(self, prompt: str, format_type: str, 
                                   style: str, generation_id: str, timestamp: str) -> Dict[str, Any]:
        """Genera asset visual (imagen/SVG)"""
        try:
            # Generar imagen con el servicio de imágenes
            image_result = await self.image_service.generate_image(
                prompt=prompt,
                style=style,
                format=format_type
            )
            
            # Guardar en directorio de assets
            filename = f"asset_{generation_id}_{timestamp}.{format_type}"
            filepath = self.assets_dir / filename
            
            # Copiar archivo generado
            if os.path.exists(image_result.get("filepath", "")):
                import shutil
                shutil.copy2(image_result["filepath"], filepath)
            
            return {
                "filename": filename,
                "filepath": str(filepath),
                "format": format_type,
                "size": os.path.getsize(filepath) if filepath.exists() else 0,
                "url": f"/assets/{filename}",
                "metadata": {
                    "prompt": prompt,
                    "style": style,
                    "generation_id": generation_id,
                    "timestamp": timestamp
                }
            }
            
        except Exception as e:
            # Fallback: crear SVG básico
            svg_content = self._create_fallback_svg(prompt, style)
            filename = f"asset_{generation_id}_{timestamp}.svg"
            filepath = self.assets_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            return {
                "filename": filename,
                "filepath": str(filepath),
                "format": "svg",
                "size": len(svg_content),
                "url": f"/assets/{filename}",
                "metadata": {
                    "prompt": prompt,
                    "style": style,
                    "generation_id": generation_id,
                    "timestamp": timestamp,
                    "fallback": True
                }
            }
    
    async def _generate_web_asset(self, prompt: str, style: str, 
                                requirements: Dict[str, Any], 
                                generation_id: str, timestamp: str) -> List[Dict[str, Any]]:
        """Genera asset web (HTML/CSS/JS)"""
        try:
            # Generar página web
            web_result = await self.web_service.generate_webpage(
                prompt=prompt,
                style=style,
                requirements=requirements
            )
            
            files = []
            
            # Guardar HTML
            if "html_content" in web_result:
                html_filename = f"asset_{generation_id}_{timestamp}.html"
                html_filepath = self.assets_dir / html_filename
                
                with open(html_filepath, 'w', encoding='utf-8') as f:
                    f.write(web_result["html_content"])
                
                files.append({
                    "filename": html_filename,
                    "filepath": str(html_filepath),
                    "format": "html",
                    "size": len(web_result["html_content"]),
                    "url": f"/assets/{html_filename}",
                    "type": "main"
                })
            
            # Guardar CSS si existe
            if "css_content" in web_result:
                css_filename = f"asset_{generation_id}_{timestamp}.css"
                css_filepath = self.assets_dir / css_filename
                
                with open(css_filepath, 'w', encoding='utf-8') as f:
                    f.write(web_result["css_content"])
                
                files.append({
                    "filename": css_filename,
                    "filepath": str(css_filepath),
                    "format": "css",
                    "size": len(web_result["css_content"]),
                    "url": f"/assets/{css_filename}",
                    "type": "style"
                })
            
            # Guardar JS si existe
            if "js_content" in web_result:
                js_filename = f"asset_{generation_id}_{timestamp}.js"
                js_filepath = self.assets_dir / js_filename
                
                with open(js_filepath, 'w', encoding='utf-8') as f:
                    f.write(web_result["js_content"])
                
                files.append({
                    "filename": js_filename,
                    "filepath": str(js_filepath),
                    "format": "js",
                    "size": len(web_result["js_content"]),
                    "url": f"/assets/{js_filename}",
                    "type": "script"
                })
            
            return files
            
        except Exception as e:
            # Fallback: crear página HTML básica
            basic_html = self._create_fallback_html(prompt, style)
            html_filename = f"asset_{generation_id}_{timestamp}.html"
            html_filepath = self.assets_dir / html_filename
            
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(basic_html)
            
            return [{
                "filename": html_filename,
                "filepath": str(html_filepath),
                "format": "html",
                "size": len(basic_html),
                "url": f"/assets/{html_filename}",
                "type": "main",
                "metadata": {
                    "prompt": prompt,
                    "style": style,
                    "generation_id": generation_id,
                    "timestamp": timestamp,
                    "fallback": True
                }
            }]
    
    async def _generate_code_asset(self, prompt: str, format_type: str, 
                                 style: str, requirements: Dict[str, Any],
                                 generation_id: str, timestamp: str) -> Dict[str, Any]:
        """Genera asset de código (Python, JS, etc.)"""
        # Implementación básica - expandir según necesidades
        code_content = f"""
# Asset generado por IRIS
# Prompt: {prompt}
# Style: {style}
# Generated: {timestamp}

def main():
    print("Asset generated by IRIS")
    # TODO: Implementar lógica específica

if __name__ == "__main__":
    main()
        """
        
        filename = f"asset_{generation_id}_{timestamp}.{format_type}"
        filepath = self.assets_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code_content)
        
        return {
            "filename": filename,
            "filepath": str(filepath),
            "format": format_type,
            "size": len(code_content),
            "url": f"/assets/{filename}",
            "metadata": {
                "prompt": prompt,
                "style": style,
                "generation_id": generation_id,
                "timestamp": timestamp
            }
        }
    
    def _create_fallback_svg(self, prompt: str, style: str) -> str:
        """Crea un SVG básico como fallback"""
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
    <rect width="200" height="200" fill="#2563EB" rx="10"/>
    <text x="100" y="100" text-anchor="middle" fill="white" font-family="Arial" font-size="14">
        Asset: {prompt[:20]}...
    </text>
    <text x="100" y="120" text-anchor="middle" fill="white" font-family="Arial" font-size="12">
        Generated by IRIS
    </text>
</svg>"""
    
    def _create_fallback_html(self, prompt: str, style: str) -> str:
        """Crea una página HTML básica como fallback"""
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asset Generado por IRIS</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #2563EB, #64748B);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        h1 {{ text-align: center; margin-bottom: 30px; }}
        .prompt {{ 
            background: rgba(255, 255, 255, 0.2); 
            padding: 20px; 
            border-radius: 10px; 
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Asset Generado por IRIS</h1>
        <div class="prompt">
            <h3>📝 Prompt:</h3>
            <p>{prompt}</p>
        </div>
        <div class="prompt">
            <h3>🎨 Estilo:</h3>
            <p>{style}</p>
        </div>
        <div class="prompt">
            <h3>⚡ Estado:</h3>
            <p>Generado exitosamente con IRIS Chat</p>
        </div>
    </div>
</body>
</html>"""
    
    def get_asset_categories(self) -> Dict[str, Any]:
        """Obtiene las categorías de assets disponibles"""
        return self.asset_categories
    
    def get_generation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene el historial de generaciones"""
        # TODO: Implementar con base de datos
        return []
    
    async def regenerate_asset(self, generation_id: str, new_prompt: str = None) -> Dict[str, Any]:
        """Regenera un asset existente con nuevas especificaciones"""
        # TODO: Implementar regeneración
        return {"status": "not_implemented"}
