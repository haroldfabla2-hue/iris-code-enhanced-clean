import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Zap, Settings, HelpCircle } from 'lucide-react';
import LivePreview from '../components/live/LivePreview';

// Hook para obtener datos del proyecto
const useProjectData = (projectId: string) => {
  const [projectData, setProjectData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjectData = async () => {
      try {
        setLoading(true);
        
        // Simular datos del proyecto (en implementación real vendría del API)
        const mockProjectData = {
          id: projectId,
          name: `Proyecto ${projectId}`,
          framework: 'react',
          files: {
            'package.json': JSON.stringify({
              name: "mi-proyecto",
              version: "1.0.0",
              type: "module",
              scripts: {
                dev: "vite",
                build: "vite build",
                preview: "vite preview"
              },
              dependencies: {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
              },
              devDependencies: {
                "@vitejs/plugin-react": "^4.0.3",
                "vite": "^4.4.5"
              }
            }, null, 2),
            'index.html': `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Mi Proyecto</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>`,
            'src/main.tsx': `import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)`,
            'src/App.tsx': `import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <header className="App-header">
        <h1>Vite + React</h1>
        <p>
          <button type="button" onClick={() => setCount((count) => count + 1)}>
            count is {count}
          </button>
        </p>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
        <p className="read-the-docs">
          Click on the Vite and React logos to learn more
        </p>
      </header>
    </div>
  )
}

export default App`,
            'src/App.css': `.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
}

button {
  font-size: calc(10px + 2vmin);
}`,
            'src/index.css': `:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;

  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

#root {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}`
          }
        };
        
        setProjectData(mockProjectData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  return { projectData, loading, error };
};

// Componente principal de la página
const LivePreviewPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const { projectData, loading, error } = useProjectData(projectId || '');
  
  const [showHelp, setShowHelp] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // Estados de configuración
  const [settings, setSettings] = useState({
    autoSave: true,
    hotReload: true,
    autoDeploy: false,
    showLineNumbers: true,
    theme: 'dark' as 'light' | 'dark' | 'auto',
    fontSize: 14,
    collaborationMode: true,
    notifications: true
  });

  // Cargar configuración del localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('iris-live-preview-settings');
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (e) {
        console.warn('Failed to parse saved settings');
      }
    }
  }, []);

  // Guardar configuración en localStorage
  useEffect(() => {
    localStorage.setItem('iris-live-preview-settings', JSON.stringify(settings));
  }, [settings]);

  // Función para manejar cierre
  const handleClose = () => {
    navigate('/projects');
  };

  // Función para manejar despliegue
  const handleDeploy = (projectId: string) => {
    console.log('Deploying project:', projectId);
    // Aquí se implementaría la lógica de deployment
    alert(`🚀 Deployment iniciado para el proyecto ${projectId}`);
  };

  // Funciones de utilidad
  const toggleSettings = () => {
    setShowSettings(!showSettings);
  };

  const toggleHelp = () => {
    setShowHelp(!showHelp);
  };

  // Estado de carga
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Zap className="w-12 h-12 text-blue-500 mx-auto mb-4 animate-pulse" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Cargando Live Preview</h2>
          <p className="text-gray-600">Preparando entorno de desarrollo...</p>
        </div>
      </div>
    );
  }

  // Estado de error
  if (error) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-red-600 text-2xl">⚠️</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error al cargar proyecto</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/projects')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Volver a Proyectos
          </button>
        </div>
      </div>
    );
  }

  // Estado de proyecto no encontrado
  if (!projectData) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-gray-400 text-2xl">📂</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Proyecto no encontrado</h2>
          <p className="text-gray-600 mb-4">El proyecto solicitado no existe o no tienes permisos para acceder a él.</p>
          <button
            onClick={() => navigate('/projects')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Volver a Proyectos
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header de la página */}
      <div className="flex items-center justify-between p-4 bg-white border-b shadow-sm">
        <div className="flex items-center space-x-4">
          <button
            onClick={handleClose}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="Volver a proyectos"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          
          <div className="flex items-center space-x-3">
            <Zap className="w-6 h-6 text-yellow-500" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">Live Preview</h1>
              <p className="text-sm text-gray-600">{projectData.name}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Indicador de estado */}
          <div className="flex items-center space-x-2 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>Activo</span>
          </div>

          {/* Botones de ayuda y configuración */}
          <button
            onClick={toggleHelp}
            className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="Ayuda"
          >
            <HelpCircle className="w-5 h-5" />
          </button>

          <button
            onClick={toggleSettings}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="Configuración"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Panel de ayuda */}
      {showHelp && (
        <div className="bg-blue-50 border-b border-blue-200 p-4">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">🚀 Guía de Live Preview</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <h4 className="font-medium text-blue-800 mb-1">Vista de Previsualización</h4>
                <p className="text-blue-700">Cambios reflejados instantáneamente. Hot reload automático.</p>
              </div>
              <div>
                <h4 className="font-medium text-blue-800 mb-1">Múltiples Terminales</h4>
                <p className="text-blue-700">Terminales simultáneas para desarrollo, testing y debugging.</p>
              </div>
              <div>
                <h4 className="font-medium text-blue-800 mb-1">WebContainers</h4>
                <p className="text-blue-700">Ejecución segura en navegador. Zero configuración.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Componente principal de Live Preview */}
      <div className="flex-1">
        <LivePreview
          projectId={projectData.id}
          projectFiles={projectData.files}
          initialFramework={projectData.framework}
          onClose={handleClose}
          onDeploy={handleDeploy}
          isCollaborationMode={settings.collaborationMode}
        />
      </div>

      {/* Panel de configuración */}
      {showSettings && (
        <div className="absolute top-20 right-4 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-30 p-4 max-h-96 overflow-y-auto">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuración</h3>
          
          <div className="space-y-4">
            {/* Configuraciones generales */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">General</h4>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.autoSave}
                    onChange={(e) => setSettings(prev => ({ ...prev, autoSave: e.target.checked }))}
                    className="text-blue-600"
                  />
                  <span className="text-sm text-gray-600">Auto guardar cambios</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.hotReload}
                    onChange={(e) => setSettings(prev => ({ ...prev, hotReload: e.target.checked }))}
                    className="text-blue-600"
                  />
                  <span className="text-sm text-gray-600">Hot reload automático</span>
                </label>

                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.autoDeploy}
                    onChange={(e) => setSettings(prev => ({ ...prev, autoDeploy: e.target.checked }))}
                    className="text-blue-600"
                  />
                  <span className="text-sm text-gray-600">Auto deployment</span>
                </label>
              </div>
            </div>

            {/* Configuraciones de colaboración */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Colaboración</h4>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.collaborationMode}
                    onChange={(e) => setSettings(prev => ({ ...prev, collaborationMode: e.target.checked }))}
                    className="text-blue-600"
                  />
                  <span className="text-sm text-gray-600">Modo colaboración</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={settings.notifications}
                    onChange={(e) => setSettings(prev => ({ ...prev, notifications: e.target.checked }))}
                    className="text-blue-600"
                  />
                  <span className="text-sm text-gray-600">Notificaciones</span>
                </label>
              </div>
            </div>

            {/* Configuraciones de editor */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Editor</h4>
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-gray-600">Tema</label>
                  <select
                    value={settings.theme}
                    onChange={(e) => setSettings(prev => ({ ...prev, theme: e.target.value as 'light' | 'dark' | 'auto' }))}
                    className="w-full mt-1 px-2 py-1 text-sm border border-gray-300 rounded"
                  >
                    <option value="dark">Oscuro</option>
                    <option value="light">Claro</option>
                    <option value="auto">Automático</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs text-gray-600">Tamaño de fuente</label>
                  <input
                    type="number"
                    value={settings.fontSize}
                    onChange={(e) => setSettings(prev => ({ ...prev, fontSize: parseInt(e.target.value) }))}
                    className="w-full mt-1 px-2 py-1 text-sm border border-gray-300 rounded"
                    min="10"
                    max="24"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-2 mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => setShowSettings(false)}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
            >
              Cerrar
            </button>
            <button
              onClick={() => {
                // Restablecer configuración por defecto
                setSettings({
                  autoSave: true,
                  hotReload: true,
                  autoDeploy: false,
                  showLineNumbers: true,
                  theme: 'dark',
                  fontSize: 14,
                  collaborationMode: true,
                  notifications: true
                });
              }}
              className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Restablecer
            </button>
          </div>
        </div>
      )}

      {/* Overlay para cerrar paneles */}
      {(showHelp || showSettings) && (
        <div
          className="fixed inset-0 bg-black bg-opacity-10 z-20"
          onClick={() => {
            setShowHelp(false);
            setShowSettings(false);
          }}
        />
      )}
    </div>
  );
};

export default LivePreviewPage;