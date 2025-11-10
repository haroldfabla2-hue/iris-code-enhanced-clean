import React from 'react';
import { useAppStore } from '../../stores/appStore';
import { Wifi, WifiOff, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

interface ConnectionStatusProps {
  className?: string;
  showDetails?: boolean;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ 
  className = '', 
  showDetails = false 
}) => {
  const { isConnected, serverHealth, lastConnectionCheck } = useAppStore();

  const getStatusIcon = () => {
    if (!serverHealth) {
      return <Loader2 className="h-4 w-4 animate-spin" />;
    }
    
    switch (serverHealth.status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return <WifiOff className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusText = () => {
    if (!serverHealth) {
      return 'Conectando...';
    }
    
    switch (serverHealth.status) {
      case 'healthy':
        return 'Conectado';
      case 'degraded':
        return 'Conexión limitada';
      default:
        return 'Desconectado';
    }
  };

  const getStatusColor = () => {
    if (!serverHealth) {
      return 'text-yellow-500';
    }
    
    switch (serverHealth.status) {
      case 'healthy':
        return 'text-green-500';
      case 'degraded':
        return 'text-yellow-500';
      default:
        return 'text-red-500';
    }
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Status Icon */}
      <div className="flex items-center gap-1">
        {isConnected ? <Wifi className="h-4 w-4 text-blue-500" /> : <WifiOff className="h-4 w-4 text-red-500" />}
        {getStatusIcon()}
      </div>

      {/* Status Text */}
      <span className={`text-sm font-medium ${getStatusColor()}`}>
        {getStatusText()}
      </span>

      {/* Details (optional) */}
      {showDetails && serverHealth && (
        <div className="text-xs text-gray-500 ml-2">
          v{serverHealth.version}
          {serverHealth.llm_stats && (
            <span className="ml-2">
              LLM: {serverHealth.llm_stats.active_provider || 'N/A'}
            </span>
          )}
        </div>
      )}
    </div>
  );
};