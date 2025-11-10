import React, { useState } from 'react';
import { 
  PlusIcon, 
  ChatBubbleLeftRightIcon, 
  ClockIcon,
  SparklesIcon,
  FilmIcon
} from '@heroicons/react/24/outline';
import AssetGenerator from './AssetGenerator';
import AssetChat from './AssetChat';
import AssetHistory from './AssetHistory';
import VideoGenerator from './VideoGenerator';
import { AssetResponse } from '../../lib/api';

interface AssetManagerProps {
  className?: string;
}

type TabType = 'generate' | 'chat' | 'history' | 'video';

const AssetManager: React.FC<AssetManagerProps> = ({ className = '' }) => {
  const [activeTab, setActiveTab] = useState<TabType>('generate');
  const [generatedAssets, setGeneratedAssets] = useState<AssetResponse[]>([]);
  const [showGenerated, setShowGenerated] = useState(false);

  // Manejar asset generado
  const handleAssetGenerated = (asset: AssetResponse) => {
    setGeneratedAssets(prev => [asset, ...prev.filter(a => a.generation_id !== asset.generation_id)]);
    setShowGenerated(true);
    
    // Auto-cambiar al historial para ver el resultado
    setTimeout(() => {
      setActiveTab('history');
    }, 2000);
  };

  // Configuración de tabs
  const tabs = [
    {
      id: 'generate' as TabType,
      name: 'Generar',
      icon: PlusIcon,
      description: 'Crear assets desde cero'
    },
    {
      id: 'chat' as TabType,
      name: 'Chat IRIS',
      icon: ChatBubbleLeftRightIcon,
      description: 'Conversar para generar assets'
    },
    {
      id: 'history' as TabType,
      name: 'Historial',
      icon: ClockIcon,
      description: 'Ver assets anteriores'
    },
    {
      id: 'video' as TabType,
      name: 'Video VEO3',
      icon: FilmIcon,
      description: 'Generar videos con IA'
    }
  ];

  return (
    <div className={`bg-gray-50 min-h-screen ${className}`}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-purple-100 rounded-lg">
                <SparklesIcon className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">IRIS Assets</h1>
                <p className="text-gray-600">Sistema de generación inteligente de assets</p>
              </div>
            </div>
            
            {/* Estadísticas rápidas */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
              <div className="bg-purple-50 p-3 rounded-lg">
                <div className="text-purple-600 text-2xl font-bold">{generatedAssets.length}</div>
                <div className="text-purple-700 text-sm">Assets Generados</div>
              </div>
              <div className="bg-blue-50 p-3 rounded-lg">
                <div className="text-blue-600 text-2xl font-bold">7</div>
                <div className="text-blue-700 text-sm">Categorías</div>
              </div>
              <div className="bg-green-50 p-3 rounded-lg">
                <div className="text-green-600 text-2xl font-bold">2</div>
                <div className="text-green-700 text-sm">Motores (IRIS + Freepik)</div>
              </div>
              <div className="bg-orange-50 p-3 rounded-lg">
                <div className="text-orange-600 text-2xl font-bold">24/7</div>
                <div className="text-orange-700 text-sm">Disponibilidad</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-purple-500 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                  <span className="text-xs text-gray-400">({tab.description})</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'generate' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <AssetGenerator 
                onAssetGenerated={handleAssetGenerated}
                className="h-fit"
              />
            </div>
            <div>
              {/* Info panel */}
              <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Categorías Disponibles</h3>
                <div className="space-y-2">
                  {[
                    { name: 'branding', label: 'Branding', desc: 'Logos, identidad visual' },
                    { name: 'mobile_ui', label: 'Mobile UI', desc: 'Interfaces móviles' },
                    { name: 'marketing', label: 'Marketing', desc: 'Material promocional' },
                    { name: 'saas_platform', label: 'SaaS Platform', desc: 'Plataformas SaaS' },
                    { name: 'ecommerce', label: 'E-commerce', desc: 'Tiendas online' },
                    { name: 'executive', label: 'Executive', desc: 'Presentaciones ejecutivas' }
                  ].map((category) => (
                    <div key={category.name} className="flex items-center gap-2 p-2 rounded hover:bg-gray-50">
                      <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{category.label}</div>
                        <div className="text-xs text-gray-500">{category.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Últimos assets generados */}
              {generatedAssets.length > 0 && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Últimos Generados</h3>
                  <div className="space-y-3">
                    {generatedAssets.slice(0, 3).map((asset) => (
                      <div key={asset.generation_id} className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                        {asset.preview_url ? (
                          <img 
                            src={asset.preview_url} 
                            alt="Preview" 
                            className="w-12 h-12 object-cover rounded"
                          />
                        ) : (
                          <div className="w-12 h-12 bg-purple-200 rounded flex items-center justify-center">
                            <SparklesIcon className="w-6 h-6 text-purple-600" />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-gray-900 truncate">
                            {asset.category}
                          </div>
                          <div className="text-xs text-gray-500">
                            {asset.format.toUpperCase()} • {asset.files.length} archivo{asset.files.length !== 1 ? 's' : ''}
                          </div>
                        </div>
                        <div className={`w-2 h-2 rounded-full ${
                          asset.status === 'completed' ? 'bg-green-500' : 'bg-yellow-500'
                        }`}></div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <AssetChat 
                onAssetGenerated={handleAssetGenerated}
                className="h-fit"
              />
            </div>
            <div>
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Ejemplos de Prompts</h3>
                <div className="space-y-3">
                  {[
                    "Crea un logo moderno para mi startup de tecnología",
                    "Diseña una página de landing para un e-commerce de ropa",
                    "Genera un dashboard analytics para una SaaS",
                    "Haz una presentación de pitch para inversionistas"
                  ].map((example, index) => (
                    <div 
                      key={index}
                      className="p-3 bg-gray-50 rounded text-sm text-gray-700 cursor-pointer hover:bg-gray-100 transition-colors"
                      onClick={() => {
                        // Copy to clipboard logic would go here
                        console.log('Example clicked:', example);
                      }}
                    >
                      {example}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div>
            <AssetHistory 
              onAssetSelect={(asset) => {
                console.log('Selected asset:', asset);
              }}
              limit={50}
            />
          </div>
        )}

        {activeTab === 'video' && (
          <div>
            <VideoGenerator />
          </div>
        )}
      </div>

      {/* Notification for new assets */}
      {showGenerated && (
        <div className="fixed top-4 right-4 z-50 animate-slide-in">
          <div className="bg-green-500 text-white p-4 rounded-lg shadow-lg flex items-center gap-3">
            <SparklesIcon className="w-5 h-5" />
            <div>
              <div className="font-medium">¡Asset generado exitosamente!</div>
              <div className="text-sm opacity-90">Revisa el historial para ver más detalles</div>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        @keyframes slide-in {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default AssetManager;