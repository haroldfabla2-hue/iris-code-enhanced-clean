import React, { useState, useEffect, useCallback } from 'react';
import { 
  SparklesIcon, 
  PhotoIcon, 
  CodeBracketIcon,
  DocumentTextIcon,
  PresentationChartLineIcon,
  DevicePhoneMobileIcon,
  BuildingOfficeIcon,
  ChartBarIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';
import { 
  AssetGenerationRequest, 
  AssetResponse, 
  AssetCategoryResponse 
} from '../../lib/api';
import mcpClient from '../../lib/api';

interface AssetGeneratorProps {
  className?: string;
  onAssetGenerated?: (asset: AssetResponse) => void;
}

const AssetGenerator: React.FC<AssetGeneratorProps> = ({ 
  className = '', 
  onAssetGenerated 
}) => {
  const [prompt, setPrompt] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('branding');
  const [selectedFormat, setSelectedFormat] = useState<string>('svg');
  const [selectedStyle, setSelectedStyle] = useState<string>('modern');
  const [isGenerating, setIsGenerating] = useState(false);
  const [categories, setCategories] = useState<string[]>([]);
  const [generationProgress, setGenerationProgress] = useState<string>('');
  const [lastGenerated, setLastGenerated] = useState<AssetResponse | null>(null);
  const [useFreepikFallback, setUseFreepikFallback] = useState(false);

  // Cargar categorías al montar el componente
  useEffect(() => {
    const loadCategories = async () => {
      const response = await mcpClient.getAssetCategories();
      if (response) {
        setCategories(response.categories);
      }
    };
    loadCategories();
  }, []);

  // Iconos para categorías
  const getCategoryIcon = (category: string) => {
    const iconClass = "w-6 h-6";
    switch (category) {
      case 'branding': return <BuildingOfficeIcon className={iconClass} />;
      case 'mobile_ui': return <DevicePhoneMobileIcon className={iconClass} />;
      case 'marketing': return <PresentationChartLineIcon className={iconClass} />;
      case 'saas_platform': return <ChartBarIcon className={iconClass} />;
      case 'ecommerce': return <PhotoIcon className={iconClass} />;
      case 'executive': return <DocumentTextIcon className={iconClass} />;
      case 'ai_stress_test': return <CpuChipIcon className={iconClass} />;
      default: return <SparklesIcon className={iconClass} />;
    }
  };

  // Formatos disponibles por categoría
  const getFormatsForCategory = (category: string) => {
    const formatMap: Record<string, string[]> = {
      'branding': ['svg', 'png', 'jpg'],
      'mobile_ui': ['svg', 'html', 'css'],
      'marketing': ['jpg', 'png', 'svg'],
      'saas_platform': ['html', 'svg', 'png'],
      'ecommerce': ['html', 'svg', 'jpg'],
      'executive': ['html', 'pdf', 'svg'],
      'ai_stress_test': ['svg', 'html', 'png']
    };
    return formatMap[category] || ['svg', 'png', 'html'];
  };

  // Estilos disponibles
  const styles = [
    { value: 'modern', label: 'Moderno' },
    { value: 'minimalist', label: 'Minimalista' },
    { value: 'corporate', label: 'Corporativo' },
    { value: 'creative', label: 'Creativo' },
    { value: 'technical', label: 'Técnico' }
  ];

  // Generar asset
  const handleGenerate = useCallback(async () => {
    if (!prompt.trim()) {
      alert('Por favor, ingresa una descripción del asset');
      return;
    }

    setIsGenerating(true);
    setGenerationProgress('Iniciando generación...');
    setLastGenerated(null);

    try {
      const request: AssetGenerationRequest = {
        prompt: prompt.trim(),
        category: selectedCategory,
        format_type: selectedFormat,
        style: selectedStyle,
        requirements: {},
        stream: true
      };

      let result: AssetResponse | null = null;

      if (useFreepikFallback) {
        // Usar Freepik como fallback directo
        setGenerationProgress('Buscando en Freepik...');
        result = await mcpClient.generateWithFreepik(prompt, selectedStyle);
      } else {
        // Usar IRIS con streaming
        setGenerationProgress('Generando con IRIS...');
        result = await mcpClient.generateAssetStream(
          request,
          (progress) => {
            setGenerationProgress(progress.message || 'Procesando...');
          }
        );
      }

      if (result) {
        setLastGenerated(result);
        setGenerationProgress('¡Generación completada!');
        onAssetGenerated?.(result);
      } else {
        // Fallback a Freepik si falla IRIS
        setGenerationProgress('Generando con Freepik...');
        result = await mcpClient.generateWithFreepik(prompt, selectedStyle);
        
        if (result) {
          setLastGenerated(result);
          setGenerationProgress('¡Generado con Freepik!');
          onAssetGenerated?.(result);
        } else {
          setGenerationProgress('Error en la generación');
        }
      }
    } catch (error) {
      console.error('Error generating asset:', error);
      setGenerationProgress('Error en la generación');
    } finally {
      setIsGenerating(false);
    }
  }, [prompt, selectedCategory, selectedFormat, selectedStyle, useFreepikFallback, onAssetGenerated]);

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <SparklesIcon className="w-6 h-6 text-purple-600" />
          Generador de Assets
        </h2>
        <p className="text-gray-600">
          Crea assets increíbles con IRIS o Freepik
        </p>
      </div>

      {/* Configuración de generación */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Descripción del Asset
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe el asset que quieres generar... ej: 'Logo moderno para startup de tecnología'"
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            rows={3}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Categoría
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setSelectedFormat(getFormatsForCategory(e.target.value)[0]);
              }}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500"
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category.replace('_', ' ').toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Formato
            </label>
            <select
              value={selectedFormat}
              onChange={(e) => setSelectedFormat(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500"
            >
              {getFormatsForCategory(selectedCategory).map((format) => (
                <option key={format} value={format}>
                  {format.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estilo
            </label>
            <select
              value={selectedStyle}
              onChange={(e) => setSelectedStyle(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500"
            >
              {styles.map((style) => (
                <option key={style.value} value={style.value}>
                  {style.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="useFreepik"
            checked={useFreepikFallback}
            onChange={(e) => setUseFreepikFallback(e.target.checked)}
            className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
          />
          <label htmlFor="useFreepik" className="text-sm text-gray-600">
            Usar Freepik como alternativa
          </label>
        </div>
      </div>

      {/* Botón de generación */}
      <div className="mb-6">
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim()}
          className={`w-full flex items-center justify-center gap-2 px-6 py-3 rounded-md font-medium transition-colors ${
            isGenerating || !prompt.trim()
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-purple-600 hover:bg-purple-700 text-white'
          }`}
        >
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Generando...
            </>
          ) : (
            <>
              <SparklesIcon className="w-5 h-5" />
              Generar Asset
            </>
          )}
        </button>
      </div>

      {/* Progreso */}
      {isGenerating && (
        <div className="mb-6 p-4 bg-blue-50 rounded-md">
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="text-blue-800">{generationProgress}</span>
          </div>
        </div>
      )}

      {/* Resultado generado */}
      {lastGenerated && lastGenerated.status === 'completed' && (
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Asset Generado</h3>
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-green-800 font-medium">Generación Exitosa</span>
              <span className="text-green-600 text-sm">
                • {lastGenerated.category} • {lastGenerated.format.toUpperCase()}
              </span>
            </div>
            
            {lastGenerated.preview_url && (
              <div className="mb-3">
                <img 
                  src={lastGenerated.preview_url} 
                  alt="Preview" 
                  className="max-w-full h-48 object-contain border border-gray-200 rounded"
                />
              </div>
            )}
            
            <div className="space-y-2">
              <div className="text-sm text-gray-600">
                <strong>Archivos generados:</strong>
              </div>
              {lastGenerated.files.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                  <div className="flex items-center gap-2">
                    {file.type === 'image' ? (
                      <PhotoIcon className="w-4 h-4 text-gray-500" />
                    ) : (
                      <CodeBracketIcon className="w-4 h-4 text-gray-500" />
                    )}
                    <span className="text-sm font-medium">{file.filename}</span>
                  </div>
                  {file.url && (
                    <a
                      href={file.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-600 hover:text-purple-800 text-sm"
                    >
                      Ver
                    </a>
                  )}
                </div>
              ))}
            </div>
            
            {lastGenerated.metadata?.source && (
              <div className="mt-3 text-xs text-gray-500">
                Generado con: {lastGenerated.metadata.source}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error */}
      {lastGenerated?.error && (
        <div className="border-t pt-6">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span className="text-red-800 font-medium">Error en la generación</span>
            </div>
            <p className="text-red-700 text-sm mt-1">{lastGenerated.error}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AssetGenerator;