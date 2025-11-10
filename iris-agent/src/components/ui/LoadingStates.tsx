import React from 'react';
import { Loader2, RefreshCw } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  message?: string;
  showRefresh?: boolean;
  onRefresh?: () => void;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  className = '',
  message,
  showRefresh = false,
  onRefresh
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <div className={`flex flex-col items-center justify-center gap-3 p-4 ${className}`}>
      <div className="flex items-center gap-2">
        <Loader2 className={`${sizeClasses[size]} animate-spin text-blue-500`} />
        {message && (
          <span className={`${textSizeClasses[size]} text-gray-600 dark:text-gray-300`}>
            {message}
          </span>
        )}
      </div>
      
      {showRefresh && onRefresh && (
        <button
          onClick={onRefresh}
          className="flex items-center gap-2 px-3 py-1 text-sm text-blue-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition-colors"
        >
          <RefreshCw className="h-3 w-3" />
          Reintentar
        </button>
      )}
    </div>
  );
};

interface SkeletonProps {
  className?: string;
  lines?: number;
  height?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ 
  className = '', 
  lines = 1, 
  height = 'h-4' 
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={`${height} bg-gray-200 dark:bg-gray-700 rounded animate-pulse`}
        />
      ))}
    </div>
  );
};