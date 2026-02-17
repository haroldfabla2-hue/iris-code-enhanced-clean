<div align="center">

# 🔮 IRIS Code Enhanced

### Plataforma Inteligente de Desarrollo de Aplicaciones con Automatización

**Creado por [Alberto Farah](https://albertofarah.com) | [LinkedIn](https://www.linkedin.com/in/alberto-farah-blair-a7b1a45a)**

![Versión](https://img.shields.io/badge/Versión-3.1.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green.svg)

</div>

---

## 📋 Descripción

**IRIS Code Enhanced** es una plataforma de desarrollo multi-agente de grado empresarial. Combina una arquitectura híbrida con más de 50 herramientas reales integradas (Google Workspace, GitHub, bases de datos, web scraping) y capacidades de orquestación inteligente, auto-healing y despliegue sin tiempo de inactividad.

---

## ✨ Características Principales

| Característica | Descripción |
|---|---|
| **Agentes Especializados** | Git, Web Scraping, Base de Datos, Procesamiento de Archivos, Ejecución Python, Búsqueda |
| **Orquestador Multi-Agente** | Gestión de workflows, balanceo de carga y auto-healing |
| **RAG Avanzado** | PostgreSQL + pgvector para búsqueda semántica |
| **Router LLM Inteligente** | Enrutamiento automático entre múltiples modelos de IA |
| **Frontend Completo** | Dashboard unificado con React + TypeScript |
| **API Gateway** | FastAPI con documentación automática |

### 🤖 Agentes Especializados

| Agente | Herramientas | Descripción |
|--------|-------------|-------------|
| **Git Operations** | Git CLI, GitHub API, GitLab API | Gestión completa de repositorios |
| **Web Scraping** | Playwright, BeautifulSoup | Extracción de datos web con JS rendering |
| **Base de Datos** | PostgreSQL, SQLAlchemy, pgvector | Operaciones CRUD y búsqueda vectorial |
| **Archivos** | PDF, Excel, CSV, OCR | Procesamiento de documentos |
| **Python Executor** | Sandbox seguro | Ejecución segura de código |
| **Búsqueda** | Google, Bing, DuckDuckGo | Búsqueda web inteligente |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│              ORQUESTADOR MULTI-AGENTE               │
│  Workflow Management | Balanceo | Auto-Healing      │
└──────────────────────┬──────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
 ┌─────▼─────┐  ┌─────▼──────┐  ┌────▼────┐
 │ Razonador │  │Planificador│  │ Ejecutor│
 └─────┬─────┘  └─────┬──────┘  └────┬────┘
       └───────────────┼──────────────┘
                       │
 ┌─────────────────────▼──────────────────────────────┐
 │              MEMORIA Y RAG AVANZADO                │
 │  PostgreSQL + pgvector | Persistencia de contexto  │
 └────────────────────────────────────────────────────┘
```

---

## 🛠️ Instalación

### Requisitos Previos
- Python 3.8+
- Node.js 18+
- PostgreSQL (opcional, para RAG avanzado)
- Docker (opcional)

### Backend

```bash
# Clonar el repositorio
git clone https://github.com/haroldfabla2-hue/iris-code-enhanced-clean.git
cd iris-code-enhanced-clean/backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar el servidor
python main.py
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

### IRIS Agent (Dashboard Avanzado)

```bash
cd iris-agent

# Instalar dependencias
npm install

# Ejecutar
npm run dev
```

---

## 💻 Uso

### API REST

El backend expone una API REST documentada automáticamente:

```bash
# Acceder a la documentación interactiva
http://localhost:8000/docs

# Ejemplo: enviar una tarea al orquestador
curl -X POST http://localhost:8000/api/task \
  -H "Content-Type: application/json" \
  -d '{"query": "Busca información sobre React 19", "agent": "search"}'
```

### Interfaz Web

- **Frontend principal** — `http://localhost:3000`
- **IRIS Agent Dashboard** — `http://localhost:5173`

### Router de LLMs

IRIS incluye un router inteligente que selecciona el mejor modelo para cada tarea:

```python
# Soporta OpenRouter, modelos locales y más
# Configurar en .env:
OPENROUTER_API_KEY="tu-api-key"
DEFAULT_MODEL="anthropic/claude-3-sonnet"
```

---

## 📁 Estructura del Proyecto

```
iris-code-enhanced-clean/
├── backend/                  # Servidor FastAPI
│   ├── app/                 # Módulos de la aplicación
│   ├── database/            # Modelos y migraciones
│   ├── tools/               # Herramientas de agentes
│   ├── main.py              # Punto de entrada del servidor
│   ├── ai_gateway.py        # Gateway de IA
│   ├── intent_analyzer.py   # Analizador de intenciones
│   └── requirements.txt     # Dependencias Python
├── frontend/                 # Interfaz React
│   ├── src/                 # Código fuente
│   └── package.json         # Dependencias Node
├── iris-agent/               # Dashboard avanzado
│   ├── src/components/      # Componentes del dashboard
│   │   ├── chat/           # Chat con IA
│   │   ├── dashboard/      # Panel principal
│   │   ├── editor/         # Editor de código
│   │   ├── memory/         # Gestor de memoria
│   │   ├── tools/          # Gestor de herramientas
│   │   └── canvas/         # Canvas interactivo
│   └── vite.config.ts      # Configuración Vite
└── iris-code/                # Módulos adicionales
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|---|---|
| **Backend** | Python, FastAPI, LangGraph |
| **Frontend** | React 18, TypeScript, TailwindCSS |
| **Base de Datos** | PostgreSQL, pgvector |
| **Caché** | Redis |
| **IA** | OpenRouter, modelos locales |
| **Web Scraping** | Playwright, BeautifulSoup |
| **Contenedores** | Docker |

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

## 📬 Contacto

- **Alberto Farah** — [alberto.farah.b@gmail.com](mailto:alberto.farah.b@gmail.com)
- **GitHub** — [@haroldfabla2](https://github.com/haroldfabla2)
- **LinkedIn** — [Alberto Farah Blair](https://www.linkedin.com/in/alberto-farah-blair-a7b1a45a)

---

<div align="center">

⭐ **Si este proyecto te resulta interesante, considera dejar una estrella** ⭐

</div>
