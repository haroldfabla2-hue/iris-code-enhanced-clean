/**
 * Enhanced IRIS Interface
 * Unified interface with 3 modes: Traditional | Enhanced | Enterprise
 * Preserves 100% of original IRIS Code functionality
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  apiService, 
  TaskRequest, 
  TaskResponse, 
  SystemStats 
} from '../services/api';

interface ProcessingMode {
  id: string;
  name: string;
  description: string;
  features: string[];
}

interface BridgeStatus {
  iris_code: {
    status: string;
    agents: number;
    backwards_compatibility: string;
    original_functionality: string;
  };
  ai_gateway: {
    status: string;
    models: {
      multimodal: string;
      coding: string;
    };
    cost: string;
  };
  silhouette_enterprise: {
    status: string;
    teams: number;
    categories: number;
    capabilities: string;
  };
  bridge_layer: {
    status: string;
    modes: string[];
    current_mode: string;
    coordination: string;
  };
  unification: string;
}

const EnhancedIRISInterface: React.FC = () => {
  // State management
  const [objective, setObjective] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TaskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [health, setHealth] = useState<any>(null);
  
  // Enhanced state
  const [processingMode, setProcessingMode] = useState('traditional');
  const [availableModes, setAvailableModes] = useState<ProcessingMode[]>([]);
  const [bridgeStatus, setBridgeStatus] = useState<BridgeStatus | null>(null);
  const [unifiedResponse, setUnifiedResponse] = useState<any>(null);
  const [currentInterface, setCurrentInterface] = useState('traditional');
  const [isEnhanced, setIsEnhanced] = useState(false);

  // Load system information
  useEffect(() => {
    loadSystemInfo();
    loadBridgeInfo();
  }, []);

  const loadSystemInfo = useCallback(async () => {
    try {
      const [healthData, statsData] = await Promise.all([
        apiService.healthCheck(),
        apiService.getSystemStats(),
      ]);
      setHealth(healthData);
      setStats(statsData);
    } catch (err: any) {
      console.error('Error cargando información del sistema:', err);
      setError('Error cargando información del sistema');
    }
  }, []);

  const loadBridgeInfo = useCallback(async () => {
    try {
      const [statusData, modesData] = await Promise.all([
        apiService.getBridgeStatus(),
        apiService.getProcessingModes(),
      ]);
      setBridgeStatus(statusData);
      setAvailableModes(modesData.modes);
      setProcessingMode(modesData.current_mode);
    } catch (err: any) {
      console.error('Error cargando información del bridge:', err);
    }
  }, []);

  // Handle task submission with enhanced processing
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!objective.trim()) {
      setError('Por favor ingresa un objetivo');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setUnifiedResponse(null);

    try {
      // Try enhanced processing first
      if (processingMode !== 'traditional') {
        try {
          const unifiedResult = await apiService.unifiedChat(
            objective.trim(),
            processingMode,
            { timestamp: new Date().toISOString() }
          );
          setUnifiedResponse(unifiedResult);
          setIsEnhanced(true);
          setCurrentInterface(processingMode);
        } catch (enhancedError) {
          console.warn('Enhanced processing failed, falling back to traditional:', enhancedError);
          // Fallback to traditional processing
          const request: TaskRequest = {
            objetivo: objective.trim(),
            contexto: {
              timestamp: new Date().toISOString(),
              fallback_reason: 'enhanced_failed',
            },
          };
          const response = await apiService.createTask(request);
          setResult(response);
        }
      } else {
        // Traditional processing
        const request: TaskRequest = {
          objetivo: objective.trim(),
          contexto: {
            timestamp: new Date().toISOString(),
            mode: 'traditional'
          },
        };
        const response = await apiService.createTask(request);
        setResult(response);
        setIsEnhanced(false);
        setCurrentInterface('traditional');
      }
    } catch (err: any) {
      console.error('Error procesando tarea:', err);
      setError(`Error procesando tarea: ${err.message || 'Error desconocido'}`);
    } finally {
      setLoading(false);
    }
  }, [objective, processingMode]);

  // Change processing mode
  const handleModeChange = useCallback(async (newMode: string) => {
    try {
      await apiService.setProcessingMode(newMode);
      setProcessingMode(newMode);
      console.log(`Modo cambiado a: ${newMode}`);
    } catch (err: any) {
      console.error('Error cambiando modo:', err);
      setError(`Error cambiando modo: ${err.message}`);
    }
  }, []);

  // Get interface styling based on current mode
  const getInterfaceStyle = () => {
    const baseClasses = "min-h-screen transition-all duration-300";
    
    switch (currentInterface) {
      case 'traditional':
        return `${baseClasses} bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900`;
      case 'enhanced':
        return `${baseClasses} bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900`;
      case 'enterprise':
        return `${baseClasses} bg-gradient-to-br from-emerald-900 via-teal-900 to-cyan-900`;
      case 'hybrid':
        return `${baseClasses} bg-gradient-to-br from-orange-900 via-red-900 to-pink-900`;
      default:
        return `${baseClasses} bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900`;
    }
  };

  // Get mode badge color
  const getModeBadgeColor = (mode: string) => {
    switch (mode) {
      case 'traditional': return 'bg-slate-600 text-slate-100';
      case 'enhanced': return 'bg-blue-600 text-blue-100';
      case 'enterprise': return 'bg-emerald-600 text-emerald-100';
      case 'hybrid': return 'bg-orange-600 text-orange-100';
      default: return 'bg-gray-600 text-gray-100';
    }
  };

  return (
    <div className={getInterfaceStyle()}>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                IRIS Code
                <span className="text-blue-400 ml-2">Enterprise</span>
              </h1>
              <p className="text-slate-300 text-lg">
                Sistema Multi-Agente Superior con Capacidades Empresariales
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-green-400 font-medium">Sistema Activo</span>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getModeBadgeColor(currentInterface)}`}>
                {currentInterface.toUpperCase()}
              </div>
            </div>
          </div>

          {/* Mode Selector */}
          <div className="mb-6">
            <label className="block text-white text-sm font-medium mb-3">
              Modo de Procesamiento
            </label>
            <div className="flex flex-wrap gap-3">
              {availableModes.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => handleModeChange(mode.id)}
                  disabled={loading}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    processingMode === mode.id
                      ? 'bg-blue-600 text-white shadow-lg scale-105'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {mode.name}
                </button>
              ))}
            </div>
          </div>

          {/* Mode Description */}
          {availableModes.find(m => m.id === processingMode) && (
            <div className="bg-slate-800/50 rounded-lg p-4 mb-6">
              <h3 className="text-white font-semibold mb-2">
                {availableModes.find(m => m.id === processingMode)?.name}
              </h3>
              <p className="text-slate-300 text-sm mb-3">
                {availableModes.find(m => m.id === processingMode)?.description}
              </p>
              <div className="flex flex-wrap gap-2">
                {availableModes.find(m => m.id === processingMode)?.features.map((feature, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded"
                  >
                    {feature}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* System Status */}
          {bridgeStatus && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-slate-800/50 rounded-lg p-4">
                <h4 className="text-white font-semibold mb-2">IRIS Code</h4>
                <p className="text-green-400 text-sm">✅ {bridgeStatus.iris_code.backwards_compatibility}</p>
                <p className="text-slate-400 text-xs">{bridgeStatus.iris_code.agents} agentes preservados</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4">
                <h4 className="text-white font-semibold mb-2">AI Gateway</h4>
                <p className="text-blue-400 text-sm">🧠 {bridgeStatus.ai_gateway.cost}</p>
                <p className="text-slate-400 text-xs">Multimodal + Coding</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4">
                <h4 className="text-white font-semibold mb-2">Enterprise</h4>
                <p className="text-emerald-400 text-sm">🏢 {bridgeStatus.silhouette_enterprise.teams} equipos</p>
                <p className="text-slate-400 text-xs">{bridgeStatus.silhouette_enterprise.categories} categorías</p>
              </div>
            </div>
          )}
        </div>

        {/* Main Interface */}
        <div className="max-w-4xl mx-auto">
          {/* Task Input Form */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 mb-6 border border-slate-700/50">
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label htmlFor="objective" className="block text-white text-sm font-medium mb-2">
                  ¿Qué te gustaría lograr?
                </label>
                <textarea
                  id="objective"
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                  placeholder="Describe tu objetivo, proyecto o tarea que quieras realizar..."
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={3}
                  disabled={loading}
                />
              </div>
              <button
                type="submit"
                disabled={loading || !objective.trim()}
                className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    Procesando con {currentInterface}...
                  </div>
                ) : (
                  `Ejecutar con ${currentInterface} mode`
                )}
              </button>
            </form>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 mb-6">
              <h4 className="text-red-400 font-semibold mb-2">Error</h4>
              <p className="text-red-300">{error}</p>
            </div>
          )}

          {/* Traditional Response */}
          {result && (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 mb-6 border border-slate-700/50">
              <div className="flex items-center mb-4">
                <div className="w-3 h-3 bg-blue-400 rounded-full mr-3"></div>
                <h3 className="text-white font-semibold">Respuesta Traditional IRIS</h3>
                <span className="ml-auto text-sm text-slate-400">#{result.conversation_id}</span>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4 mb-4">
                <p className="text-slate-300">
                  {result.result?.content || 'Procesamiento completado'}
                </p>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className={`px-2 py-1 rounded ${
                  result.status === 'completed' ? 'bg-green-700 text-green-300' : 'bg-yellow-700 text-yellow-300'
                }`}>
                  {result.status}
                </span>
                <span className="text-slate-400">
                  Agentes: Reasoner → Planner → Executor → Verifier → Memory
                </span>
              </div>
            </div>
          )}

          {/* Enhanced Response */}
          {unifiedResponse && (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 mb-6 border border-slate-700/50">
              <div className="flex items-center mb-4">
                <div className="w-3 h-3 bg-emerald-400 rounded-full mr-3"></div>
                <h3 className="text-white font-semibold">
                  Respuesta {unifiedResponse.mode?.toUpperCase() || 'ENHANCED'}
                </h3>
                <span className="ml-auto text-sm text-slate-400">
                  {unifiedResponse.processing_info?.timestamp}
                </span>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4 mb-4">
                <p className="text-slate-300">{unifiedResponse.response}</p>
              </div>
              
              {/* Processing Info */}
              {unifiedResponse.processing_info && (
                <div className="bg-slate-900/30 rounded-lg p-4">
                  <h4 className="text-white font-medium mb-2">Información de Procesamiento</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    {unifiedResponse.processing_info.agents_used && (
                      <div>
                        <span className="text-slate-400">Agentes IRIS:</span>
                        <span className="text-white ml-2">{unifiedResponse.processing_info.agents_used.join(', ')}</span>
                      </div>
                    )}
                    {unifiedResponse.processing_info.ai_provider && (
                      <div>
                        <span className="text-slate-400">AI Provider:</span>
                        <span className="text-white ml-2">{unifiedResponse.processing_info.ai_provider}</span>
                      </div>
                    )}
                    {unifiedResponse.processing_info.enterprise_team && (
                      <div>
                        <span className="text-slate-400">Enterprise Team:</span>
                        <span className="text-white ml-2">{unifiedResponse.processing_info.enterprise_team}</span>
                      </div>
                    )}
                    {unifiedResponse.processing_info.routing && (
                      <div>
                        <span className="text-slate-400">Routing:</span>
                        <span className="text-white ml-2">{unifiedResponse.processing_info.routing.mode}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* System Stats */}
          {stats && (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
              <h3 className="text-white font-semibold mb-4">Estadísticas del Sistema</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <h4 className="text-slate-300 font-medium mb-2">Versión</h4>
                  <p className="text-white">{stats.system.version}</p>
                </div>
                {stats.llm && (
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <h4 className="text-slate-300 font-medium mb-2">LLM Stats</h4>
                    <p className="text-white">{stats.llm.total_calls} llamadas</p>
                  </div>
                )}
                {stats.orchestrator && (
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <h4 className="text-slate-300 font-medium mb-2">Sesiones Activas</h4>
                    <p className="text-white">{stats.orchestrator.active_sessions}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedIRISInterface;