import { useState, useEffect, useCallback, useRef } from 'react';
import { useAppStore } from '../stores/appStore';
import { useToast } from './useToast';

interface ConnectionState {
  isConnected: boolean;
  isReconnecting: boolean;
  lastConnected: string | null;
  reconnectAttempts: number;
  maxReconnectAttempts: number;
  shouldReconnect: boolean;
}

interface UseConnectionOptions {
  autoReconnect?: boolean;
  maxAttempts?: number;
  retryDelay?: number;
  exponentialBackoff?: boolean;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onReconnect?: () => void;
}

export const useConnection = (options: UseConnectionOptions = {}) => {
  const {
    autoReconnect = true,
    maxAttempts = 5,
    retryDelay = 2000,
    exponentialBackoff = true,
    onConnect,
    onDisconnect,
    onReconnect
  } = options;

  const { isConnected, serverHealth, checkServerHealth } = useAppStore();
  const { connectionError } = useToast();
  
  const [connectionState, setConnectionState] = useState<ConnectionState>({
    isConnected,
    isReconnecting: false,
    lastConnected: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: maxAttempts,
    shouldReconnect: true
  });

  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!mountedRef.current) return;

    setConnectionState(prev => ({
      ...prev,
      isConnected
    }));

    if (isConnected && !connectionState.isConnected) {
      // Just connected
      if (onConnect) onConnect();
      setConnectionState(prev => ({
        ...prev,
        lastConnected: new Date().toISOString(),
        reconnectAttempts: 0
      }));
    } else if (!isConnected && connectionState.isConnected) {
      // Just disconnected
      if (onDisconnect) onDisconnect();
      if (autoReconnect && connectionState.shouldReconnect) {
        handleReconnect();
      }
    }
  }, [isConnected, connectionState.isConnected, autoReconnect, onConnect, onDisconnect, connectionState.shouldReconnect]);

  const calculateRetryDelay = useCallback((attempt: number) => {
    if (!exponentialBackoff) return retryDelay;
    return Math.min(retryDelay * Math.pow(2, attempt), 30000); // Max 30 seconds
  }, [retryDelay, exponentialBackoff]);

  const handleReconnect = useCallback(async () => {
    if (!mountedRef.current || !connectionState.shouldReconnect) return;

    if (connectionState.reconnectAttempts >= connectionState.maxReconnectAttempts) {
      connectionError(
        `No se pudo establecer conexión después de ${connectionState.reconnectAttempts} intentos. Verifica la configuración del servidor.`,
        () => {
          setConnectionState(prev => ({
            ...prev,
            reconnectAttempts: 0,
            shouldReconnect: true
          }));
          handleReconnect();
        }
      );
      return;
    }

    setConnectionState(prev => ({
      ...prev,
      isReconnecting: true,
      reconnectAttempts: prev.reconnectAttempts + 1
    }));

    try {
      await checkServerHealth();
      
      if (mountedRef.current && isConnected) {
        setConnectionState(prev => ({
          ...prev,
          isReconnecting: false
        }));
        if (onReconnect) onReconnect();
      } else {
        throw new Error('Connection failed');
      }
    } catch (error) {
      if (!mountedRef.current) return;

      setConnectionState(prev => ({
        ...prev,
        isReconnecting: false
      }));

      // Schedule next retry
      const delay = calculateRetryDelay(connectionState.reconnectAttempts);
      reconnectTimeoutRef.current = setTimeout(() => {
        if (mountedRef.current && connectionState.shouldReconnect) {
          handleReconnect();
        }
      }, delay);
    }
  }, [
    connectionState.reconnectAttempts,
    connectionState.maxReconnectAttempts,
    connectionState.shouldReconnect,
    checkServerHealth,
    isConnected,
    onReconnect,
    connectionError,
    calculateRetryDelay
  ]);

  const forceReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    setConnectionState(prev => ({
      ...prev,
      reconnectAttempts: 0,
      shouldReconnect: true
    }));
    
    handleReconnect();
  }, [handleReconnect]);

  const stopReconnecting = useCallback(() => {
    setConnectionState(prev => ({
      ...prev,
      shouldReconnect: false
    }));
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
  }, []);

  const startReconnecting = useCallback(() => {
    setConnectionState(prev => ({
      ...prev,
      shouldReconnect: true
    }));
    
    if (!isConnected) {
      handleReconnect();
    }
  }, [isConnected, handleReconnect]);

  return {
    isConnected: connectionState.isConnected,
    isReconnecting: connectionState.isReconnecting,
    lastConnected: connectionState.lastConnected,
    reconnectAttempts: connectionState.reconnectAttempts,
    maxReconnectAttempts: connectionState.maxReconnectAttempts,
    shouldReconnect: connectionState.shouldReconnect,
    healthStatus: serverHealth?.status || 'unknown',
    healthData: serverHealth,
    forceReconnect,
    stopReconnecting,
    startReconnecting,
    checkHealth: checkServerHealth
  };
};