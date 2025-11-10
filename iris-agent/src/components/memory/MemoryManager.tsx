import React, { useState, useEffect, useCallback } from 'react';
import { 
  BeakerIcon, 
  MagnifyingGlassIcon, 
  DocumentTextIcon,
  PlusIcon,
  ChartBarIcon,
  TrashIcon,
  ClockIcon,
  UserIcon,
  TagIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import { 
  MemorySearchRequest, 
  MemorySearchResponse, 
  MemoryStoreRequest,
  MemoryStatsResponse,
  MemorySearchResult
} from '../../lib/api';
import mcpClient from '../../lib/api';

interface MemoryManagerProps {
  className?: string;
}

type TabType = 'search' | 'store' | 'stats' | 'documents';

const MemoryManager: React.FC<MemoryManagerProps> = ({ className = '' }) => {
  const [activeTab, setActiveTab] = useState<TabType>('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<MemorySearchResult[]>([]);
  const [searchType, setSearchType] = useState<'semantic' | 'keyword' | 'hybrid'>('semantic');
  const [isSearching, setIsSearching] = useState(false);
  const [stats, setStats] = useState<MemoryStatsResponse | null>(null);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [storeForm, setStoreForm] = useState<MemoryStoreRequest>({
    content: '',
    content_type: 'text',
    tags: []
  });
  const [isStoring, setIsStoring] = useState(false);
  const [newTag, setNewTag] = useState('');

  // Load stats on component mount
  useEffect(() => {
    loadMemoryStats();
  }, []);

  // Cargar estadísticas de memoria
  const loadMemoryStats = async () => {
    setIsLoadingStats(true);
    try {
      const statsData = await mcpClient.getMemoryStats();
      setStats(statsData);
    } catch (error) {
      console.error('Error loading memory stats:', error);
    } finally {
      setIsLoadingStats(false);
    }
  };

  // Búsqueda en memoria
  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const result = await mcpClient.searchMemory({
        query: searchQuery.trim(),
        search_type: searchType,
        limit: 10
      });

      if (result) {
        setSearchResults(result.results);
      }
    } catch (error) {
      console.error('Error searching memory:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, [searchQuery, searchType]);

  // Almacenar en memoria
  const handleStore = async () => {
    if (!storeForm.content.trim()) return;

    setIsStoring(true);
    try {
      const result = await mcpClient.storeMemory(storeForm);
      if (result) {
        // Reset form
        setStoreForm({
          content: '',
          content_type: 'text',
          tags: []
        });
        setNewTag('');
        // Refresh stats
        loadMemoryStats();
        // Show success message
        alert('Información almacenada en memoria exitosamente');
      }
    } catch (error) {
      console.error('Error storing memory:', error);
      alert('Error almacenando en memoria');
    } finally {
      setIsStoring(false);
    }
  };

  // Agregar tag
  const addTag = () => {
    if (newTag.trim() && !storeForm.tags?.includes(newTag.trim())) {
      setStoreForm({
        ...storeForm,
        tags: [...(storeForm.tags || []), newTag.trim()]
      });
      setNewTag('');
    }
  };

  // Remover tag
  const removeTag = (tagToRemove: string) => {
    setStoreForm({
      ...storeForm,
      tags: storeForm.tags?.filter(tag => tag !== tagToRemove) || []
    });
  };

  // Limpiar memoria
  const handleClearMemory = async () => {
    if (confirm('¿Estás seguro de que quieres limpiar toda la memoria?')) {
      try {
        const result = await mcpClient.clearMemory({});
        if (result) {
          alert(`Memoria limpiada: ${result.cleared_count} elementos eliminados`);
          loadMemoryStats();
        }
      } catch (error) {
        console.error('Error clearing memory:', error);
        alert('Error limpiando memoria');
      }
    }
  };

  // Formatear fecha
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  // Configuración de tabs
  const tabs = [
    {
      id: 'search' as TabType,
      name: 'Buscar',
      icon: MagnifyingGlassIcon,
      description: 'Buscar en memoria'
    },
    {
      id: 'store' as TabType,
      name: 'Almacenar',
      icon: PlusIcon,
      description: 'Guardar información'
    },
    {
      id: 'stats' as TabType,
      name: 'Estadísticas',
      icon: ChartBarIcon,
      description: 'Ver estadísticas'
    },
    {
      id: 'documents' as TabType,
      name: 'Documentos',
      icon: DocumentTextIcon,
      description: 'Gestionar documentos'
    }
  ];

  return (
    <div className={`bg-gray-50 min-h-screen ${className}`}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BeakerIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Memory Manager</h1>
                <p className="text-gray-600">Sistema de memoria y búsqueda RAG</p>
              </div>
            </div>

            {/* Stats quick view */}
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="text-blue-600 text-2xl font-bold">{stats.total_memories}</div>
                  <div className="text-blue-700 text-sm">Total Memories</div>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <div className="text-green-600 text-2xl font-bold">
                    {Object.keys(stats.memories_by_type).length}
                  </div>
                  <div className="text-green-700 text-sm">Tipos de Contenido</div>
                </div>
                <div className="bg-purple-50 p-3 rounded-lg">
                  <div className="text-purple-600 text-2xl font-bold">
                    {Object.keys(stats.memories_by_user).length}
                  </div>
                  <div className="text-purple-700 text-sm">Usuarios Activos</div>
                </div>
                <div className="bg-orange-50 p-3 rounded-lg">
                  <div className="text-orange-600 text-2xl font-bold">RAG</div>
                  <div className="text-orange-700 text-sm">Búsqueda Semántica</div>
                </div>
              </div>
            )}
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
                      ? 'border-blue-500 text-blue-600'
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
        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Búsqueda en Memoria</h3>
                
                {/* Search Form */}
                <div className="space-y-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Consulta de Búsqueda
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Buscar en la memoria... ej: 'proyectos de React' o 'configuración de API'"
                        className="flex-1 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                      />
                      <button
                        onClick={handleSearch}
                        disabled={isSearching || !searchQuery.trim()}
                        className={`px-4 py-3 rounded-md flex items-center gap-2 transition-colors ${
                          isSearching || !searchQuery.trim()
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                        }`}
                      >
                        {isSearching ? (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        ) : (
                          <MagnifyingGlassIcon className="w-4 h-4" />
                        )}
                        Buscar
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Tipo de Búsqueda
                      </label>
                      <select
                        value={searchType}
                        onChange={(e) => setSearchType(e.target.value as any)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="semantic">Semántica (IA)</option>
                        <option value="keyword">Palabras Clave</option>
                        <option value="hybrid">Híbrida</option>
                      </select>
                    </div>
                    <div className="flex items-end">
                      <button
                        onClick={loadMemoryStats}
                        disabled={isLoadingStats}
                        className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                      >
                        <ChartBarIcon className="w-4 h-4" />
                        Actualizar Stats
                      </button>
                    </div>
                  </div>
                </div>

                {/* Search Results */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900">
                    Resultados ({searchResults.length})
                  </h4>
                  
                  {searchResults.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <BeakerIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                      <p>No hay resultados</p>
                      <p className="text-sm mt-1">Realiza una búsqueda para ver resultados</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {searchResults.map((result, index) => (
                        <div key={result.memory_id || index} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-medium text-gray-500 uppercase">
                                {result.content_type}
                              </span>
                              {result.relevance_score && (
                                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                  {(result.relevance_score * 100).toFixed(1)}% relevante
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-gray-500">
                              {formatDate(result.stored_at)}
                            </div>
                          </div>
                          
                          <p className="text-gray-900 mb-3 line-clamp-3">
                            {result.content}
                          </p>
                          
                          {result.tags && result.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mb-2">
                              {result.tags.map((tag, tagIndex) => (
                                <span
                                  key={tagIndex}
                                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                                >
                                  <TagIcon className="w-3 h-3" />
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                          
                          <div className="text-xs text-gray-500">
                            ID: {result.memory_id}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div>
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Filtros de Búsqueda</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tipo de Contenido
                    </label>
                    <select className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500">
                      <option value="">Todos</option>
                      <option value="text">Texto</option>
                      <option value="code">Código</option>
                      <option value="document">Documento</option>
                      <option value="result">Resultado</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Rango Temporal
                    </label>
                    <select className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500">
                      <option value="">Todos</option>
                      <option value="1h">Última hora</option>
                      <option value="1d">Último día</option>
                      <option value="1w">Última semana</option>
                      <option value="1m">Último mes</option>
                    </select>
                  </div>
                  
                  <button
                    onClick={handleClearMemory}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
                  >
                    <TrashIcon className="w-4 h-4" />
                    Limpiar Memoria
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Store Tab */}
        {activeTab === 'store' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Almacenar en Memoria</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contenido a Almacenar
                  </label>
                  <textarea
                    value={storeForm.content}
                    onChange={(e) => setStoreForm({ ...storeForm, content: e.target.value })}
                    placeholder="Escribe la información que quieres recordar..."
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows={6}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tipo de Contenido
                    </label>
                    <select
                      value={storeForm.content_type}
                      onChange={(e) => setStoreForm({ ...storeForm, content_type: e.target.value })}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="text">Texto</option>
                      <option value="code">Código</option>
                      <option value="document">Documento</option>
                      <option value="result">Resultado</option>
                      <option value="config">Configuración</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      ID de Conversación (Opcional)
                    </label>
                    <input
                      type="text"
                      value={storeForm.conversation_id || ''}
                      onChange={(e) => setStoreForm({ ...storeForm, conversation_id: e.target.value })}
                      placeholder="conv_123"
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Etiquetas
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      placeholder="Agregar etiqueta..."
                      className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                    />
                    <button
                      onClick={addTag}
                      className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
                    >
                      <PlusIcon className="w-4 h-4" />
                    </button>
                  </div>
                  
                  {storeForm.tags && storeForm.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {storeForm.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                        >
                          {tag}
                          <button
                            onClick={() => removeTag(tag)}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={handleStore}
                    disabled={isStoring || !storeForm.content.trim()}
                    className={`flex items-center gap-2 px-6 py-3 rounded-md font-medium transition-colors ${
                      isStoring || !storeForm.content.trim()
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 hover:bg-blue-700 text-white'
                    }`}
                  >
                    {isStoring ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Almacenando...
                      </>
                    ) : (
                      <>
                        <PlusIcon className="w-4 h-4" />
                        Almacenar en Memoria
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stats Tab */}
        {activeTab === 'stats' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Estadísticas Generales</h3>
              {isLoadingStats ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : stats ? (
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">{stats.total_memories}</div>
                    <div className="text-gray-600">Total de Memorias</div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Por Tipo de Contenido</h4>
                    <div className="space-y-2">
                      {Object.entries(stats.memories_by_type).map(([type, count]) => (
                        <div key={type} className="flex justify-between">
                          <span className="text-gray-600 capitalize">{type}</span>
                          <span className="font-medium">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No se pudieron cargar las estadísticas</p>
                </div>
              )}
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Actividad Reciente</h3>
              {stats?.recent_activity && (
                <div className="space-y-3">
                  {Object.entries(stats.recent_activity).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                      <span className="font-medium">{value as any}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Documents Tab */}
        {activeTab === 'documents' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Gestión de Documentos</h3>
            <div className="text-center py-12 text-gray-500">
              <DocumentTextIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p>Funcionalidad de gestión de documentos</p>
              <p className="text-sm mt-1">Carga y almacena documentos completos con chunking inteligente</p>
              <button className="mt-4 px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors">
                Próximamente
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MemoryManager;