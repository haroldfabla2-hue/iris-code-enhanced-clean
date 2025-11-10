import React, { useState, useEffect } from 'react';
import { 
  ClockIcon, 
  PhotoIcon, 
  CodeBracketIcon,
  ArrowPathIcon,
  EyeIcon,
  TrashIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { AssetResponse } from '../../lib/api';
import mcpClient from '../../lib/api';

interface AssetHistoryProps {
  className?: string;
  onAssetSelect?: (asset: AssetResponse) => void;
  limit?: number;
}

const AssetHistory: React.FC<AssetHistoryProps> = ({ 
  className = '', 
  onAssetSelect,
  limit = 20
}) => {
  const [assets, setAssets] = useState<AssetResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Cargar historial
  useEffect(() => {
    loadAssetHistory();
  }, [limit]);

  const loadAssetHistory = async () => {
    setIsLoading(true);
    try {
      const history = await mcpClient.getAssetHistory(limit);
      setAssets(history);
    } catch (error) {
      console.error('Error loading asset history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Filtrar assets
  const filteredAssets = assets.filter(asset => {
    const matchesSearch = searchTerm === '' || 
      asset.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.format.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.metadata?.prompt?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || asset.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  // Obtener categorías únicas
  const categories = ['all', ...Array.from(new Set(assets.map(asset => asset.category)))];

  // Obtener icono del tipo de archivo
  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'image':
      case 'jpg':
      case 'jpeg':
      case 'png':
        return <PhotoIcon className="w-4 h-4 text-blue-500" />;
      case 'code':
      case 'html':
      case 'css':
      case 'svg':
        return <CodeBracketIcon className="w-4 h-4 text-green-500" />;
      default:
        return <PhotoIcon className="w-4 h-4 text-gray-500" />;
    }
  };

  // Formatear fecha
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return 'Hace unos minutos';
    } else if (diffInHours < 24) {
      return `Hace ${Math.floor(diffInHours)} horas`;
    } else {
      return date.toLocaleDateString();
    }
  };

  // Regenerar asset
  const handleRegenerate = async (asset: AssetResponse) => {
    try {
      const newAsset = await mcpClient.regenerateAsset(asset.generation_id);
      if (newAsset) {
        setAssets(prev => [newAsset, ...prev.filter(a => a.generation_id !== asset.generation_id)]);
      }
    } catch (error) {
      console.error('Error regenerating asset:', error);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <ClockIcon className="w-5 h-5 text-purple-600" />
            Historial de Assets
          </h2>
          <button
            onClick={loadAssetHistory}
            disabled={isLoading}
            className="flex items-center gap-1 px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-md hover:bg-purple-200 transition-colors"
          >
            <ArrowPathIcon className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
        </div>

        {/* Filtros */}
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar assets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category === 'all' ? 'Todas' : category.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            <span className="ml-2 text-gray-600">Cargando historial...</span>
          </div>
        ) : filteredAssets.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <ClockIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No hay assets en el historial</p>
            <p className="text-sm mt-1">Genera tu primer asset para verlo aquí</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredAssets.map((asset) => (
              <div
                key={asset.generation_id}
                className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors"
              >
                <div className="flex items-start gap-3">
                  {/* Preview */}
                  {asset.preview_url ? (
                    <img
                      src={asset.preview_url}
                      alt="Asset preview"
                      className="w-16 h-16 object-cover rounded border border-gray-200 flex-shrink-0"
                    />
                  ) : (
                    <div className="w-16 h-16 bg-gray-100 rounded border border-gray-200 flex items-center justify-center flex-shrink-0">
                      {getFileIcon(asset.format)}
                    </div>
                  )}

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-gray-500 uppercase">
                        {asset.category}
                      </span>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-gray-500 uppercase">
                        {asset.format}
                      </span>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        asset.status === 'completed' 
                          ? 'bg-green-100 text-green-800'
                          : asset.status === 'processing'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {asset.status}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-900 line-clamp-2">
                      {asset.metadata?.prompt || 'Asset generado'}
                    </p>
                    
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                      <span>{formatDate(asset.timestamp)}</span>
                      <span>{asset.files.length} archivo{asset.files.length !== 1 ? 's' : ''}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-1">
                    <button
                      onClick={() => onAssetSelect?.(asset)}
                      className="p-1 text-gray-400 hover:text-purple-600 transition-colors"
                      title="Ver detalles"
                    >
                      <EyeIcon className="w-4 h-4" />
                    </button>
                    {asset.status === 'completed' && (
                      <button
                        onClick={() => handleRegenerate(asset)}
                        className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                        title="Regenerar"
                      >
                        <ArrowPathIcon className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Files list */}
                {asset.files.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <div className="flex flex-wrap gap-2">
                      {asset.files.slice(0, 3).map((file, index) => (
                        <a
                          key={index}
                          href={file.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs text-gray-700 hover:bg-gray-200 transition-colors"
                        >
                          {getFileIcon(file.type)}
                          {file.filename}
                        </a>
                      ))}
                      {asset.files.length > 3 && (
                        <span className="inline-flex items-center px-2 py-1 bg-gray-100 rounded text-xs text-gray-500">
                          +{asset.files.length - 3} más
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AssetHistory;