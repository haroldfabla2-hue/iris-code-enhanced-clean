import { useState, useCallback } from 'react';
import { Toast, ToastType } from '../components/ui/Toast';

export interface CreateToastOptions {
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  actions?: Array<{
    label: string;
    onClick: () => void;
    style?: 'primary' | 'secondary';
  }>;
}

export const useToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((options: CreateToastOptions) => {
    const id = Math.random().toString(36).substr(2, 9);
    const toast: Toast = {
      id,
      ...options,
      duration: options.duration ?? 5000, // Default 5 seconds
    };

    setToasts(prev => [...prev, toast]);
    return id;
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  // Convenience methods
  const success = useCallback((title: string, message?: string, options?: Partial<CreateToastOptions>) => {
    return addToast({
      type: 'success',
      title,
      message,
      ...options
    });
  }, [addToast]);

  const error = useCallback((title: string, message?: string, options?: Partial<CreateToastOptions>) => {
    return addToast({
      type: 'error',
      title,
      message,
      duration: 0, // Don't auto-dismiss errors
      ...options
    });
  }, [addToast]);

  const warning = useCallback((title: string, message?: string, options?: Partial<CreateToastOptions>) => {
    return addToast({
      type: 'warning',
      title,
      message,
      duration: 7000, // Slightly longer for warnings
      ...options
    });
  }, [addToast]);

  const info = useCallback((title: string, message?: string, options?: Partial<CreateToastOptions>) => {
    return addToast({
      type: 'info',
      title,
      message,
      ...options
    });
  }, [addToast]);

  // Special method for connection errors
  const connectionError = useCallback((errorMessage: string, onRetry?: () => void) => {
    return error(
      'Error de conexión',
      errorMessage,
      {
        actions: onRetry ? [
          {
            label: 'Reintentar',
            onClick: () => {
              onRetry();
              removeToast(lastToastId);
            },
            style: 'primary' as const
          }
        ] : undefined
      }
    );
  }, [error, removeToast]);

  return {
    toasts,
    addToast,
    removeToast,
    clearToasts,
    success,
    error,
    warning,
    info,
    connectionError
  };
};

// Hook to track the last created toast ID (for action callbacks)
let lastToastId = '';

export const useLastToast = () => {
  return { getLastToastId: () => lastToastId };
};