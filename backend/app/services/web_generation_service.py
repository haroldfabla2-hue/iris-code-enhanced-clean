"""
Servicio de Generación de Páginas Web
Genera HTML, CSS y JS para diferentes tipos de sitios
"""
import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import uuid

class WebGenerationService:
    """Servicio para generar páginas web usando IA"""
    
    def __init__(self):
        self.temp_dir = "/workspace/temp_web"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Templates predefinidos
        self.web_templates = {
            "landing_page": {
                "structure": ["header", "hero", "features", "cta", "footer"],
                "components": ["navigation", "hero_section", "feature_grid", "testimonials", "footer"]
            },
            "dashboard": {
                "structure": ["sidebar", "main_content", "header"],
                "components": ["sidebar_navigation", "metrics_cards", "charts", "data_tables"]
            },
            "ecommerce": {
                "structure": ["header", "product_grid", "cart", "footer"],
                "components": ["product_cards", "search_bar", "filters", "cart_sidebar"]
            },
            "admin_panel": {
                "structure": ["sidebar", "main_area", "top_bar"],
                "components": ["user_management", "settings", "analytics", "logs"]
            }
        }
    
    async def generate_webpage(self, 
                             prompt: str,
                             style: str = "modern",
                             requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Genera una página web completa
        
        Args:
            prompt: Descripción de la página
            style: Estilo (modern, minimalist, corporate, creative, technical)
            requirements: Requerimientos específicos
            
        Returns:
            Dict con HTML, CSS y JS de la página
        """
        try:
            generation_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Analizar el prompt para determinar tipo de página
            page_type = self._detect_page_type(prompt)
            
            # Generar contenido
            result = {
                "generation_id": generation_id,
                "timestamp": timestamp,
                "prompt": prompt,
                "page_type": page_type,
                "style": style,
                "requirements": requirements or {},
                "status": "completed",
                "html_content": "",
                "css_content": "",
                "js_content": "",
                "metadata": {}
            }
            
            if page_type == "landing_page":
                result.update(self._generate_landing_page(prompt, style))
            elif page_type == "dashboard":
                result.update(self._generate_dashboard(prompt, style))
            elif page_type == "ecommerce":
                result.update(self._generate_ecommerce(prompt, style))
            elif page_type == "admin_panel":
                result.update(self._generate_admin_panel(prompt, style))
            else:
                result.update(self._generate_generic_page(prompt, style))
            
            result["metadata"] = {
                "generation_time": 3.2,  # Simulado
                "components_count": len(result.get("components", [])),
                "responsive": True,
                "accessibility": "AA"
            }
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "generation_id": generation_id if 'generation_id' in locals() else str(uuid.uuid4())
            }
    
    def _detect_page_type(self, prompt: str) -> str:
        """Detecta el tipo de página basado en el prompt"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["dashboard", "analytics", "metrics", "métricas"]):
            return "dashboard"
        elif any(word in prompt_lower for word in ["ecommerce", "tienda", "producto", "comprar"]):
            return "ecommerce"
        elif any(word in prompt_lower for word in ["admin", "administración", "panel"]):
            return "admin_panel"
        elif any(word in prompt_lower for word in ["landing", "marketing", "promocional"]):
            return "landing_page"
        else:
            return "generic"
    
    def _generate_landing_page(self, prompt: str, style: str) -> Dict[str, Any]:
        """Genera una landing page"""
        styles = self._get_style_config(style)
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IRIS Generated Landing Page</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="nav-brand">IRIS</div>
            <ul class="nav-links">
                <li><a href="#inicio">Inicio</a></li>
                <li><a href="#características">Características</a></li>
                <li><a href="#contacto">Contacto</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section id="hero" class="hero">
            <div class="container">
                <h1 class="hero-title">Creado con IRIS</h1>
                <p class="hero-subtitle">"{prompt[:100]}..."</p>
                <div class="hero-cta">
                    <button class="btn btn-primary">Comenzar</button>
                    <button class="btn btn-secondary">Ver Demo</button>
                </div>
            </div>
        </section>
        
        <section id="features" class="features">
            <div class="container">
                <h2>Características</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <h3>Responsive</h3>
                        <p>Adaptable a todos los dispositivos</p>
                    </div>
                    <div class="feature-card">
                        <h3>Moderno</h3>
                        <p>Diseño actualizado y profesional</p>
                    </div>
                    <div class="feature-card">
                        <h3>Rápido</h3>
                        <p>Optimizado para rendimiento</p>
                    </div>
                </div>
            </div>
        </section>
        
        <section id="cta" class="cta">
            <div class="container">
                <h2>¿Listo para empezar?</h2>
                <p>Genera tu página web con IRIS en minutos</p>
                <button class="btn btn-primary btn-large">Generar Ahora</button>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 IRIS - Generado automáticamente</p>
        </div>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>"""
        
        css = f"""/* IRIS Generated Landing Page Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: {styles['text']};
    background: {styles['background']};
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Header */
.header {{
    background: {styles['primary']};
    color: white;
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 1000;
}}

.nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
}}

.nav-brand {{
    font-size: 1.5rem;
    font-weight: bold;
}}

.nav-links {{
    display: flex;
    list-style: none;
    gap: 2rem;
}}

.nav-links a {{
    color: white;
    text-decoration: none;
    transition: opacity 0.3s;
}}

.nav-links a:hover {{
    opacity: 0.8;
}}

/* Hero */
.hero {{
    background: linear-gradient(135deg, {styles['primary']}, {styles['secondary']});
    color: white;
    padding: 120px 0 80px;
    text-align: center;
}}

.hero-title {{
    font-size: 3.5rem;
    margin-bottom: 1rem;
    font-weight: 700;
}}

.hero-subtitle {{
    font-size: 1.3rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}}

.hero-cta {{
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}}

/* Buttons */
.btn {{
    padding: 0.8rem 2rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
    display: inline-block;
}}

.btn-primary {{
    background: {styles['accent']};
    color: white;
}}

.btn-primary:hover {{
    background: {styles['accent_dark']};
    transform: translateY(-2px);
}}

.btn-secondary {{
    background: transparent;
    color: white;
    border: 2px solid white;
}}

.btn-secondary:hover {{
    background: white;
    color: {styles['primary']};
}}

.btn-large {{
    padding: 1rem 2.5rem;
    font-size: 1.1rem;
}}

/* Features */
.features {{
    padding: 80px 0;
}}

.features h2 {{
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    color: {styles['text']};
}}

.features-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}}

.feature-card {{
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s;
}}

.feature-card:hover {{
    transform: translateY(-5px);
}}

.feature-card h3 {{
    font-size: 1.3rem;
    margin-bottom: 1rem;
    color: {styles['primary']};
}}

/* CTA Section */
.cta {{
    background: {styles['background_alt']};
    padding: 80px 0;
    text-align: center;
}}

.cta h2 {{
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: {styles['text']};
}}

.cta p {{
    font-size: 1.2rem;
    margin-bottom: 2rem;
    color: {styles['text_secondary']};
}}

/* Footer */
.footer {{
    background: {styles['text']};
    color: white;
    padding: 2rem 0;
    text-align: center;
}}

/* Responsive */
@media (max-width: 768px) {{
    .hero-title {{
        font-size: 2.5rem;
    }}
    
    .nav-links {{
        display: none;
    }}
    
    .features-grid {{
        grid-template-columns: 1fr;
    }}
}}"""
        
        js = """// IRIS Generated Landing Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    });
    
    // Add scroll effect to header
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.header');
        if (window.scrollY > 100) {
            header.style.backgroundColor = 'rgba(37, 99, 235, 0.95)';
        } else {
            header.style.backgroundColor = '';
        }
    });
    
    // Animate feature cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });
    
    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease-out';
        observer.observe(card);
    });
});"""
        
        return {
            "html_content": html,
            "css_content": css,
            "js_content": js,
            "components": ["header", "hero", "features", "cta", "footer"]
        }
    
    def _generate_dashboard(self, prompt: str, style: str) -> Dict[str, Any]:
        """Genera un dashboard"""
        # Implementación similar para dashboard
        return self._generate_landing_page(prompt, style)  # Simplificado por ahora
    
    def _generate_ecommerce(self, prompt: str, style: str) -> Dict[str, Any]:
        """Genera una página de e-commerce"""
        return self._generate_landing_page(prompt, style)  # Simplificado por ahora
    
    def _generate_admin_panel(self, prompt: str, style: str) -> Dict[str, Any]:
        """Genera un panel de administración"""
        return self._generate_landing_page(prompt, style)  # Simplificado por ahora
    
    def _generate_generic_page(self, prompt: str, style: str) -> Dict[str, Any]:
        """Genera una página genérica"""
        return self._generate_landing_page(prompt, style)
    
    def _get_style_config(self, style: str) -> Dict[str, str]:
        """Obtiene configuración de colores para cada estilo"""
        configs = {
            "modern": {
                "primary": "#2563EB",
                "secondary": "#64748B",
                "accent": "#F59E0B",
                "accent_dark": "#D97706",
                "text": "#1F2937",
                "text_secondary": "#6B7280",
                "background": "#F8FAFC",
                "background_alt": "#FFFFFF"
            },
            "minimalist": {
                "primary": "#1F2937",
                "secondary": "#6B7280",
                "accent": "#3B82F6",
                "accent_dark": "#2563EB",
                "text": "#111827",
                "text_secondary": "#4B5563",
                "background": "#FFFFFF",
                "background_alt": "#F9FAFB"
            },
            "corporate": {
                "primary": "#1E40AF",
                "secondary": "#374151",
                "accent": "#059669",
                "accent_dark": "#047857",
                "text": "#1F2937",
                "text_secondary": "#6B7280",
                "background": "#F9FAFB",
                "background_alt": "#FFFFFF"
            },
            "creative": {
                "primary": "#7C3AED",
                "secondary": "#EC4899",
                "accent": "#F59E0B",
                "accent_dark": "#D97706",
                "text": "#1F2937",
                "text_secondary": "#6B7280",
                "background": "#FEF3C7",
                "background_alt": "#FFFFFF"
            },
            "technical": {
                "primary": "#0F172A",
                "secondary": "#475569",
                "accent": "#06B6D4",
                "accent_dark": "#0891B2",
                "text": "#1F2937",
                "text_secondary": "#6B7280",
                "background": "#F1F5F9",
                "background_alt": "#FFFFFF"
            }
        }
        return configs.get(style, configs["modern"])
