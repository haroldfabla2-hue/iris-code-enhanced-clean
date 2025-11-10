"""
BridgeManager Component
Complete interface for Bridge API with 11 endpoints
Handles IRIS-Silhouette integration and multi-agent coordination
"""

import React, { useState, useEffect } from 'react';
import { 
  NetworkIcon, 
  CpuChipIcon, 
  ChatBubbleLeftRightIcon,
  Cog6ToothIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { useAppStore } from '../../stores/appStore';
import { mcpClient } from '../../lib/api';

interface BridgeStatus {
  status: 'connected' | 'disconnected' | 'degraded';
  iris_agents_active: number;
  silhouette_teams_active: number;
  processing_queue: number;
  last_heartbeat: string;
  uptime: number;
}

interface Agent {
  agent_id: string;
  name: string;
  type: string;
  capabilities: string[];
  status: 'active' | 'idle' | 'busy' | 'offline';
  performance_metrics: {
    tasks_completed: number;
    average_response_time: number;
    success_rate: number;
  };
}

interface ProcessingMode {
  mode_id: string;
  name: string;
  description: string;
  available: boolean;
  performance_score: number;
  best_for: string[];
}

interface AIModel {
  model_id: string;
  name: string;
  provider: string;
  type: 'generation' | 'analysis' | 'multimodal';
  performance_metrics: {
    speed: number;
    quality: number;
    cost_efficiency: number;
  };
}

const BridgeManager: React.FC = () => {
  const { isConnected } = useAppStore();
  const [bridgeStatus, setBridgeStatus] = useState<BridgeStatus | null>(null);
  const [irisAgents, setIrisAgents] = useState<Agent[]>([]);
  const [silhouetteTeams, setSilhouetteTeams] = useState<Agent[]>([]);
  const [processingModes, setProcessingModes] = useState<ProcessingMode[]>([]);
  const [currentMode, setCurrentMode] = useState<ProcessingMode | null>(null);
  const [aiModels, setAiModels] = useState<AIModel[]>([]);
  const [integrationInfo, setIntegrationInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'status' | 'agents' | 'modes' | 'models' | 'chat'>('status');
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [taskType, setTaskType] = useState('');
  const [routingInfo, setRoutingInfo] = useState<any>(null);

  useEffect(() => {
    if (isConnected) {
      loadBridgeData();
      // Refresh data every 30 seconds
      const interval = setInterval(loadBridgeData, 30000);
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const loadBridgeData = async () => {
    setIsLoading(true);
    try {
      // Load all bridge data in parallel
      const [
        statusData,
        agentsData,
        teamsData,
        modesData,
        currentModeData,
        modelsData,
        integrationData
      ] = await Promise.allSettled([
        mcpClient.getBridgeStatus(),
        mcpClient.getBridgeAgents(),
        mcpClient.getSilhouetteTeams(),
        mcpClient.getProcessingModes(),
        mcpClient.getCurrentMode(),
        mcpClient.getAIProcessInfo(),
        mcpClient.getIntegrationInfo()
      ]);

      // Process results
      if (statusData.status === 'fulfilled' && statusData.value) {
        setBridgeStatus(statusData.value);
      }

      if (agentsData.status === 'fulfilled' && agentsData.value) {
        setIrisAgents(agentsData.value.agents || []);
      }

      if (teamsData.status === 'fulfilled' && teamsData.value) {
        setSilhouetteTeams(teamsData.value.teams || []);
      }

      if (modesData.status === 'fulfilled' && modesData.value) {
        setProcessingModes(modesData.value.modes || []);
      }

      if (currentModeData.status === 'fulfilled' && currentModeData.value) {
        setCurrentMode(currentModeData.value);
      }

      if (modelsData.status === 'fulfilled' && modelsData.value) {
        setAiModels(modelsData.value.models || []);
      }

      if (integrationData.status === 'fulfilled' && integrationData.value) {
        setIntegrationInfo(integrationData.value);
      }
    } catch (error) {
      console.error('Error loading bridge data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const processTask = async () => {
    if (!chatMessage.trim() || !isConnected) return;

    try {
      const response = await mcpClient.processTaskThroughBridge(chatMessage, {});
      if (response) {
        setChatHistory(prev => [...prev, {
          type: 'user',
          message: chatMessage,
          timestamp: new Date()
        }, {
          type: 'system',
          message: response.message,
          timestamp: new Date()
        }]);
        setChatMessage('');
      }
    } catch (error) {
      console.error('Error processing task:', error);
      alert('Error processing task. Please try again.');
    }
  };

  const getTaskRouting = async () => {
    if (!taskType.trim() || !isConnected) return;

    try {
      const response = await mcpClient.getTaskRouting(taskType);
      if (response) {
        setRoutingInfo(response);
      }
    } catch (error) {
      console.error('Error getting task routing:', error);
      alert('Error getting task routing. Please try again.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': case 'active': return 'text-green-600 bg-green-100';
      case 'degraded': case 'idle': return 'text-yellow-600 bg-yellow-100';
      case 'disconnected': case 'offline': return 'text-red-600 bg-red-100';
      case 'busy': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': case 'active': return <CheckCircleIcon className="w-5 h-5" />;
      case 'degraded': case 'idle': return <ExclamationTriangleIcon className="w-5 h-5" />;
      case 'disconnected': case 'offline': return <XCircleIcon className="w-5 h-5" />;
      case 'busy': return <ArrowPathIcon className="w-5 h-5 animate-spin" />;
      default: return <InformationCircleIcon className="w-5 h-5" />;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Bridge Manager</h1>
            <p className="text-gray-600 mt-1">
              IRIS-Silhouette integration and multi-agent coordination
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={loadBridgeData}
              disabled={isLoading}
              className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              <ArrowPathIcon className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Status Cards */}
      {bridgeStatus && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <NetworkIcon className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Bridge Status</p>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(bridgeStatus.status)}`}>
                  {getStatusIcon(bridgeStatus.status)}
                  <span className="ml-1 capitalize">{bridgeStatus.status}</span>
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <CpuChipIcon className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">IRIS Agents</p>
                <p className="text-2xl font-semibold text-gray-900">{bridgeStatus.iris_agents_active}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Cog6ToothIcon className="w-8 h-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Silhouette Teams</p>
                <p className="text-2xl font-semibold text-gray-900">{bridgeStatus.silhouette_teams_active}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <InformationCircleIcon className="w-8 h-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Queue</p>
                <p className="text-2xl font-semibold text-gray-900">{bridgeStatus.processing_queue}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {[
              { id: 'status', name: 'System Status', icon: NetworkIcon },
              { id: 'agents', name: 'Agents & Teams', icon: CpuChipIcon },
              { id: 'modes', name: 'Processing Modes', icon: Cog6ToothIcon },
              { id: 'models', name: 'AI Models', icon: InformationCircleIcon },
              { id: 'chat', name: 'Unified Chat', icon: ChatBubbleLeftRightIcon }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* System Status Tab */}
          {activeTab === 'status' && (
            <div className="space-y-6">
              {bridgeStatus && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-medium mb-4">Connection Status</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Status</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(bridgeStatus.status)}`}>
                          {bridgeStatus.status}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Uptime</span>
                        <span className="text-gray-900">{Math.floor(bridgeStatus.uptime / 3600)}h</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Last Heartbeat</span>
                        <span className="text-gray-900">
                          {new Date(bridgeStatus.last_heartbeat).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-medium mb-4">Performance Metrics</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">IRIS Agents</span>
                        <span className="text-gray-900">{bridgeStatus.iris_agents_active}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Silhouette Teams</span>
                        <span className="text-gray-900">{bridgeStatus.silhouette_teams_active}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Processing Queue</span>
                        <span className="text-gray-900">{bridgeStatus.processing_queue}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Agents & Teams Tab */}
          {activeTab === 'agents' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">IRIS Agents</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {irisAgents.map((agent) => (
                    <div key={agent.agent_id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{agent.name}</h4>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(agent.status)}`}>
                          {agent.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{agent.type}</p>
                      <div className="text-xs text-gray-500">
                        <p>Tasks: {agent.performance_metrics.tasks_completed}</p>
                        <p>Success Rate: {(agent.performance_metrics.success_rate * 100).toFixed(1)}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-4">Silhouette Teams</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {silhouetteTeams.map((team) => (
                    <div key={team.agent_id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{team.name}</h4>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(team.status)}`}>
                          {team.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{team.type}</p>
                      <div className="text-xs text-gray-500">
                        <p>Tasks: {team.performance_metrics.tasks_completed}</p>
                        <p>Success Rate: {(team.performance_metrics.success_rate * 100).toFixed(1)}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Processing Modes Tab */}
          {activeTab === 'modes' && (
            <div className="space-y-6">
              {currentMode && (
                <div className="bg-blue-50 p-4 rounded-lg mb-6">
                  <h3 className="text-lg font-medium mb-2">Current Mode</h3>
                  <div className="flex items-center">
                    <span className="text-2xl font-bold text-blue-900">{currentMode.name}</span>
                    <span className={`ml-3 px-2 py-1 rounded text-xs font-medium ${getStatusColor(currentMode.available ? 'active' : 'offline')}`}>
                      {currentMode.available ? 'Available' : 'Unavailable'}
                    </span>
                  </div>
                  <p className="text-blue-700 mt-1">{currentMode.description}</p>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {processingModes.map((mode) => (
                  <div key={mode.mode_id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{mode.name}</h4>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(mode.available ? 'active' : 'offline')}`}>
                        {mode.available ? 'Available' : 'Unavailable'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{mode.description}</p>
                    <div className="text-xs text-gray-500">
                      <p>Performance Score: {mode.performance_score}/10</p>
                      <div className="mt-1">
                        <p className="font-medium">Best for:</p>
                        <ul className="list-disc list-inside">
                          {mode.best_for.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Models Tab */}
          {activeTab === 'models' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {aiModels.map((model) => (
                  <div key={model.model_id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{model.name}</h4>
                      <span className="text-xs text-gray-500">{model.provider}</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Type: {model.type}</p>
                    <div className="text-xs text-gray-500 space-y-1">
                      <div className="flex justify-between">
                        <span>Speed:</span>
                        <span>{model.performance_metrics.speed}/10</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Quality:</span>
                        <span>{model.performance_metrics.quality}/10</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Cost Efficiency:</span>
                        <span>{model.performance_metrics.cost_efficiency}/10</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 p-4 border rounded-lg">
                <h4 className="font-medium mb-4">Get Task Routing</h4>
                <div className="flex space-x-4">
                  <input
                    type="text"
                    value={taskType}
                    onChange={(e) => setTaskType(e.target.value)}
                    placeholder="Enter task type (e.g., 'code_generation', 'data_analysis')"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={getTaskRouting}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Get Routing
                  </button>
                </div>
                {routingInfo && (
                  <div className="mt-4 bg-gray-50 p-4 rounded">
                    <h5 className="font-medium mb-2">Routing Information</h5>
                    <pre className="text-sm overflow-x-auto">{JSON.stringify(routingInfo, null, 2)}</pre>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Unified Chat Tab */}
          {activeTab === 'chat' && (
            <div className="space-y-6">
              <div className="border rounded-lg h-96 flex flex-col">
                <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
                  {chatHistory.length === 0 ? (
                    <div className="text-center text-gray-500 mt-20">
                      <ChatBubbleLeftRightIcon className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>Start a conversation with the unified bridge</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {chatHistory.map((message, index) => (
                        <div
                          key={index}
                          className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                              message.type === 'user'
                                ? 'bg-blue-600 text-white'
                                : 'bg-white border'
                            }`}
                          >
                            <p className="text-sm">{message.message}</p>
                            <p className={`text-xs mt-1 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                              {message.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="p-4 border-t">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={chatMessage}
                      onChange={(e) => setChatMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && processTask()}
                      placeholder="Type your message..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={processTask}
                      disabled={!chatMessage.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BridgeManager;