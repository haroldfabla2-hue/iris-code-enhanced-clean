import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
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

interface ToastProps {
  toast: Toast;
  onClose: (id: string) => void;
}

const toastIcons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info
};

const toastStyles = {
  success: 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-200',
  error: 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-200',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-200',
  info: 'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-200'
};

const iconStyles = {
  success: 'text-green-500',
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500'
};

export const ToastItem: React.FC<ToastProps> = ({ toast, onClose }) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isLeaving, setIsLeaving] = useState(false);

  const Icon = toastIcons[toast.type];

  useEffect(() => {
    if (toast.duration && toast.duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, toast.duration);

      return () => clearTimeout(timer);
    }
  }, [toast.duration]);

  const handleClose = () => {
    setIsLeaving(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose(toast.id);
    }, 300); // Animation duration
  };

  if (!isVisible) return null;

  return (
    <div
      className={`
        flex items-start gap-3 p-4 border rounded-lg shadow-lg max-w-sm
        transform transition-all duration-300 ease-in-out
        ${toastStyles[toast.type]}
        ${isLeaving ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'}
      `}
    >
      <Icon className={`h-5 w-5 flex-shrink-0 mt-0.5 ${iconStyles[toast.type]}`} />
      
      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-sm">
          {toast.title}
        </h4>
        {toast.message && (
          <p className="text-sm opacity-90 mt-1">
            {toast.message}
          </p>
        )}
        
        {toast.actions && toast.actions.length > 0 && (
          <div className="flex gap-2 mt-3">
            {toast.actions.map((action, index) => (
              <button
                key={index}
                onClick={action.onClick}
                className={`
                  text-xs px-3 py-1 rounded-md font-medium transition-colors
                  ${action.style === 'primary' 
                    ? 'bg-white/20 hover:bg-white/30 text-current' 
                    : 'bg-white/10 hover:bg-white/20 text-current'
                  }
                `}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={handleClose}
        className="flex-shrink-0 p-1 rounded-md hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};

interface ToastContainerProps {
  toasts: Toast[];
  onClose: (id: string) => void;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
}

export const ToastContainer: React.FC<ToastContainerProps> = ({
  toasts,
  onClose,
  position = 'top-right'
}) => {
  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2'
  };

  return (
    <div className={`fixed z-50 flex flex-col gap-2 ${positionClasses[position]}`}>
      {toasts.map((toast) => (
        <ToastItem
          key={toast.id}
          toast={toast}
          onClose={onClose}
        />
      ))}
    </div>
  );
};

interface ToastManagerProps {
  toasts: Toast[];
  onClose: (id: string) => void;
}

export const ToastManager: React.FC<ToastManagerProps> = ({ toasts, onClose }) => {
  if (toasts.length === 0) return null;

  return (
    <>
      {/* Desktop Toast Container */}
      <div className="hidden md:block">
        <ToastContainer toasts={toasts} onClose={onClose} position="top-right" />
      </div>
      
      {/* Mobile Toast Container */}
      <div className="block md:hidden">
        <ToastContainer toasts={toasts} onClose={onClose} position="bottom-center" />
      </div>
    </>
  );
};