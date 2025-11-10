import React from 'react';
import { AlertCircle, RefreshCw, X } from 'lucide-react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error; resetError: () => void }>;
}

interface ErrorState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return <FallbackComponent error={this.state.error} resetError={this.resetError} />;
      }

      return <DefaultErrorFallback error={this.state.error} resetError={this.resetError} />;
    }

    return this.props.children;
  }
}

interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
  title?: string;
  message?: string;
  showDetails?: boolean;
}

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetError,
  title = 'Oops! Something went wrong',
  message = 'We encountered an unexpected error. Please try again.',
  showDetails = false
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
      
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {title}
      </h3>
      
      <p className="text-gray-600 dark:text-gray-300 mb-4 max-w-md">
        {message}
      </p>

      {showDetails && (
        <details className="text-left w-full max-w-md mb-4">
          <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
            Technical Details
          </summary>
          <pre className="mt-2 p-3 bg-gray-100 dark:bg-gray-700 rounded text-xs text-red-600 dark:text-red-400 overflow-auto">
            {error.message}
            {error.stack && `\n\n${error.stack}`}
          </pre>
        </details>
      )}

      <div className="flex gap-3">
        <button
          onClick={resetError}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Try Again
        </button>
      </div>
    </div>
  );
};

const DefaultErrorFallback: React.FC<ErrorFallbackProps> = (props) => (
  <ErrorFallback {...props} />
);

interface NetworkErrorProps {
  error: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export const NetworkError: React.FC<NetworkErrorProps> = ({
  error,
  onRetry,
  onDismiss
}) => {
  return (
    <div className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
      <div className="flex items-center gap-2">
        <AlertCircle className="h-4 w-4 text-red-500" />
        <span className="text-sm text-red-700 dark:text-red-300">
          {error}
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 underline"
          >
            Reintentar
          </button>
        )}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};