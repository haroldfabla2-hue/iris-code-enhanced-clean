// Configuración centralizada de IRIS Code
export interface AppConfig {
  api: {
    baseUrl: string;
    timeout: number;
    retryAttempts: number;
    healthCheckInterval: number;
    enableCaching: boolean;
  };
  ui: {
    theme: 'light' | 'dark' | 'system';
    animationDuration: number;
    toastDuration: number;
    loadingDelay: number;
  };
  features: {
    autoSave: boolean;
    autoSaveInterval: number;
    streaming: boolean;
    realTimeCollaboration: boolean;
    offlineMode: boolean;
  };
  development: {
    debugMode: boolean;
    showConnectionStatus: boolean;
    logLevel: 'debug' | 'info' | 'warn' | 'error';
  };
}

const config: AppConfig = {
  api: {
    baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8020',
    timeout: 30000,
    retryAttempts: 3,
    healthCheckInterval: 30000, // 30 seconds
    enableCaching: true,
    // Nuevas configuraciones para Silhouette V4.0
    gateway: {
      enabled: true,
      version: '4.0.0',
      endpoints: {
        fallback: '/api/fallback',
        silhouette: '/api/silhouette', 
        assets: '/api/assets',
        mcp: '/api/mcp',
        unified: {
          llm: '/api/llm/generate',
          chat: '/api/chat',
          images: '/api/images/generate',
          workflows: '/api/workflows/execute',
          teams: '/api/teams',
          metrics: '/api/metrics/unified'
        }
      }
    }
  },
  ui: {
    theme: 'system',
    animationDuration: 200,
    toastDuration: 5000,
    loadingDelay: 1000,
  },
  features: {
    autoSave: true,
    autoSaveInterval: 30000, // 30 seconds
    streaming: true,
    realTimeCollaboration: false, // Future feature
    offlineMode: true,
  },
  development: {
    debugMode: process.env.NODE_ENV === 'development',
    showConnectionStatus: true,
    logLevel: process.env.NODE_ENV === 'development' ? 'debug' : 'info',
  }
};

// Environment-specific overrides
if (process.env.NODE_ENV === 'production') {
  config.ui.animationDuration = 0; // Disable animations in production for performance
  config.ui.toastDuration = 3000; // Shorter toasts in production
  config.development.showConnectionStatus = false;
}

// Utility functions
export const getApiUrl = (endpoint: string): string => {
  const base = config.api.baseUrl.endsWith('/') 
    ? config.api.baseUrl.slice(0, -1) 
    : config.api.baseUrl;
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${base}${path}`;
};

export const isConfigured = (): boolean => {
  return !!config.api.baseUrl;
};

export const getConfig = (): AppConfig => {
  return config;
};

// Validate configuration
export const validateConfig = (): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  if (!config.api.baseUrl) {
    errors.push('API base URL is required');
  }
  
  if (config.api.timeout < 1000) {
    errors.push('API timeout should be at least 1000ms');
  }
  
  if (config.api.retryAttempts < 0) {
    errors.push('Retry attempts cannot be negative');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// Log configuration in development
if (config.development.debugMode) {
  console.log('IRIS Code Configuration:', config);
  const validation = validateConfig();
  if (!validation.isValid) {
    console.warn('Configuration validation failed:', validation.errors);
  }
}

export default config;