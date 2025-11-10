import React, { useState } from 'react';
import { 
  Wand2, 
  Copy, 
  Save, 
  Download, 
  RotateCcw,
  Type, 
  Code,
  Image,
  FileText,
  Settings,
  Share,
  History,
  Eye,
  Sparkles,
  RefreshCw,
  Target,
  Scissors
} from 'lucide-react';
import { cn } from '../../lib/utils';

const Canvas: React.FC = () => {
  const [canvasType, setCanvasType] = useState<'text' | 'code'>('text');
  const [language, setLanguage] = useState('typescript');
  const [content, setContent] = useState(`# Canvas Interactivo IRIS

Este es un espacio de trabajo visual donde puedes:

1. **Desarrollar ideas** - Escribe y refina tus conceptos
2. **Generar código** - Crea y modifica código con IA
3. **Iterar visualmente** - Ve cambios en tiempo real
4. **Colaborar** - Comparte y recibe feedback

## Comienza a escribir aquí...

¿Cuál es tu próxima gran idea?`);
  const [selectedTool, setSelectedTool] = useState<'select' | 'text' | 'code'>('text');
  const [aiMode, setAiMode] = useState(false);
  const [history, setHistory] = useState([
    { id: 1, timestamp: '2024-11-05 11:30', description: 'Canvas inicializado' },
    { id: 2, timestamp: '2024-11-05 11:35', description: 'Contenido inicial agregado' },
  ]);

  const tools = [
    { id: 'select', icon: Target, name: 'Seleccionar' },
    { id: 'text', icon: Type, name: 'Texto' },
    { id: 'code', icon: Code, name: 'Código' },
  ];

  const aiActions = [
    { id: 'improve', label: 'Mejorar', icon: Wand2, description: 'Mejora el contenido actual' },
    { id: 'expand', label: 'Expandir', icon: FileText, description: 'Añade más detalles' },
    { id: 'simplify', label: 'Simplificar', icon: Scissors, description: 'Reduce la complejidad' },
    { id: 'translate', label: 'Traducir', icon: RefreshCw, description: 'Traduce a otro idioma' },
    { id: 'generate', label: 'Generar', icon: Sparkles, description: 'Genera contenido nuevo' },
  ];

  const handleToolAction = (actionId: string) => {
    // Mock AI action processing
    const responses = {
      improve: 'Contenido mejorado con mejores estructuras y claridad.',
      expand: 'Contenido expandido con información adicional y contexto.',
      simplify: 'Contenido simplificado manteniendo la información esencial.',
      translate: 'Contenido traducido manteniendo el significado original.',
      generate: 'Nuevo contenido generado basado en el contexto existente.',
    };

    setContent(prev => prev + '\n\n' + responses[actionId as keyof typeof responses]);
  };

  const ActionButton: React.FC<{
    action: any;
    onClick?: () => void;
  }> = ({ action, onClick }) => (
    <button
      onClick={onClick}
      className="flex items-center space-x-2 px-4 py-2 bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 rounded-lg transition-colors text-sm"
    >
      <action.icon className="w-4 h-4" />
      <span>{action.label}</span>
    </button>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Canvas Header */}
      <div className="border-b border-border bg-background p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-title font-semibold">Canvas Interactivo</h1>
            
            {/* Canvas Type Selector */}
            <div className="flex space-x-1 bg-neutral-100 dark:bg-neutral-800 rounded-lg p-1">
              <button
                onClick={() => setCanvasType('text')}
                className={cn(
                  "px-3 py-1.5 text-sm font-medium rounded transition-colors flex items-center gap-2",
                  canvasType === 'text' 
                    ? "bg-white dark:bg-neutral-700 shadow-sm" 
                    : "hover:bg-neutral-200 dark:hover:bg-neutral-700"
                )}
              >
                <Type className="w-4 h-4" />
                Texto
              </button>
              <button
                onClick={() => setCanvasType('code')}
                className={cn(
                  "px-3 py-1.5 text-sm font-medium rounded transition-colors flex items-center gap-2",
                  canvasType === 'code' 
                    ? "bg-white dark:bg-neutral-700 shadow-sm" 
                    : "hover:bg-neutral-200 dark:hover:bg-neutral-700"
                )}
              >
                <Code className="w-4 h-4" />
                Código
              </button>
            </div>

            {canvasType === 'code' && (
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="h-8 px-3 bg-neutral-100 dark:bg-neutral-800 rounded border-0 focus:ring-2 focus:ring-brand-500"
              >
                <option value="typescript">TypeScript</option>
                <option value="javascript">JavaScript</option>
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
              </select>
            )}
          </div>

          <div className="flex items-center space-x-2">
            {/* History */}
            <button className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Historial">
              <History className="w-5 h-5" />
            </button>
            
            {/* Share */}
            <button className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Compartir">
              <Share className="w-5 h-5" />
            </button>
            
            {/* Export */}
            <button className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Exportar">
              <Download className="w-5 h-5" />
            </button>
            
            {/* Save */}
            <button className="iris-button-primary">
              <Save className="w-4 h-4 mr-2" />
              Guardar
            </button>
          </div>
        </div>

        {/* Tool Selection */}
        <div className="flex items-center space-x-2 mt-4">
          <span className="text-sm text-neutral-600 dark:text-neutral-400">Herramientas:</span>
          {tools.map((tool) => (
            <button
              key={tool.id}
              onClick={() => setSelectedTool(tool.id as any)}
              className={cn(
                "flex items-center space-x-2 px-3 py-1.5 text-sm font-medium rounded-lg transition-colors",
                selectedTool === tool.id
                  ? "bg-brand-500 text-white"
                  : "hover:bg-neutral-100 dark:hover:bg-neutral-800"
              )}
            >
              <tool.icon className="w-4 h-4" />
              <span>{tool.name}</span>
            </button>
          ))}
          
          {/* AI Mode Toggle */}
          <button
            onClick={() => setAiMode(!aiMode)}
            className={cn(
              "flex items-center space-x-2 px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ml-auto",
              aiMode
                ? "bg-brand-500 text-white"
                : "hover:bg-neutral-100 dark:hover:bg-neutral-800 border border-neutral-300 dark:border-neutral-600"
            )}
          >
            <Sparkles className="w-4 h-4" />
            <span>Modo IA</span>
          </button>
        </div>
      </div>

      {/* Main Canvas Area */}
      <div className="flex-1 flex">
        {/* Canvas Content */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 p-6">
            {canvasType === 'text' ? (
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full h-full p-6 bg-neutral-50 dark:bg-neutral-900 rounded-xl border-0 focus:ring-2 focus:ring-brand-500 resize-none font-mono text-sm leading-relaxed"
                placeholder="Comienza a escribir tu contenido aquí..."
              />
            ) : (
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full h-full p-6 bg-neutral-900 text-green-400 rounded-xl border-0 focus:ring-2 focus:ring-brand-500 resize-none font-mono text-sm leading-relaxed"
                placeholder={`// Escribe código ${language} aquí...`}
              />
            )}
          </div>

          {/* Canvas Footer */}
          <div className="border-t border-border bg-background p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4 text-sm text-neutral-500">
                <span>{content.length} caracteres</span>
                <span>•</span>
                <span>{content.split('\n').length} líneas</span>
                {canvasType === 'code' && (
                  <>
                    <span>•</span>
                    <span>Lenguaje: {language}</span>
                  </>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <button className="p-2 rounded hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Vista previa">
                  <Eye className="w-4 h-4" />
                </button>
                <button className="p-2 rounded hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Copiar">
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* AI Actions Panel */}
        {aiMode && (
          <div className="w-80 border-l border-border bg-background p-4">
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-medium mb-3">Acciones con IA</h3>
                <div className="space-y-2">
                  {aiActions.map((action) => (
                    <ActionButton
                      key={action.id}
                      action={action}
                      onClick={() => handleToolAction(action.id)}
                    />
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium mb-3">Historial</h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {history.map((item) => (
                    <div key={item.id} className="p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                      <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                        {item.description}
                      </p>
                      <p className="text-xs text-neutral-500 mt-1">
                        {item.timestamp}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium mb-3">Configuración</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm">Modelo de IA</label>
                    <select className="w-full mt-1 h-8 px-3 bg-neutral-100 dark:bg-neutral-800 rounded border-0">
                      <option>GPT-4</option>
                      <option>Claude 3</option>
                      <option>GPT-3.5</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm">Creatividad</label>
                    <input 
                      type="range" 
                      min="0" 
                      max="100" 
                      defaultValue="70"
                      className="w-full mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-sm">Longitud</label>
                    <select className="w-full mt-1 h-8 px-3 bg-neutral-100 dark:bg-neutral-800 rounded border-0">
                      <option>Corto</option>
                      <option>Medio</option>
                      <option>Largo</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Canvas;