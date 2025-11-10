import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserSettings as StorageSettings, storage } from '../lib/storage';
import { mcpClient, MetricsResponse, HealthResponse } from '../lib/api';

interface AppMetrics {
  tokensUsed: number;
  tokensAvailable: number;
  activeProjects: number;
  activeConversations: number;
  systemStatus: 'healthy' | 'unhealthy' | 'connecting';
  responseTime: number;
  requestsTotal: number;
  requestsPerMinute: number;
  successRate: number;
  averageLatency: number;
  p95Latency: number;
  p99Latency: number;
}

interface Notification {
  id: string;
  type: 'system' | 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  persistent?: boolean;
}

interface AppState {
  // UI State
  sidebarCollapsed: boolean;
  contextPanelCollapsed: boolean;
  activeModal: string | null;
  
  // Theme & Settings
  theme: 'light' | 'dark' | 'system';
  userSettings: StorageSettings;
  
  // Metrics & Status
  metrics: AppMetrics;
  isConnected: boolean;
  lastConnectionCheck: string;
  serverHealth: HealthResponse | null;
  
  // Notifications
  notifications: Notification[];
  unreadCount: number;
  
  // Actions
  setSidebarCollapsed: (collapsed: boolean) => void;
  setContextPanelCollapsed: (collapsed: boolean) => void;
  setActiveModal: (modal: string | null) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  updateUserSettings: (settings: Partial<StorageSettings>) => void;
  updateMetrics: (metrics: Partial<AppMetrics>) => void;
  setConnectionStatus: (connected: boolean) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
  checkServerHealth: () => Promise<void>;
  updateMetricsFromServer: () => Promise<void>;
  syncSettingsWithStorage: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => {
      // Load initial settings from storage
      const storedSettings = storage.loadSettings();
      
      return {
        // Initial State
        sidebarCollapsed: false,
        contextPanelCollapsed: false,
        activeModal: null,
        theme: storedSettings.theme,
        userSettings: storedSettings,
        
        metrics: {
          tokensUsed: 0,
          tokensAvailable: 5000000,
          activeProjects: 0,
          activeConversations: 0,
          systemStatus: 'connecting',
          responseTime: 0,
          requestsTotal: 0,
          requestsPerMinute: 0,
          successRate: 0,
          averageLatency: 0,
          p95Latency: 0,
          p99Latency: 0,
        },
        
        isConnected: false,
        lastConnectionCheck: new Date().toISOString(),
        serverHealth: null,
        
        notifications: [
          {
            id: '1',
            type: 'system',
            title: 'IRIS Agent iniciado',
            message: 'Aplicación lista para usar',
            timestamp: new Date().toISOString(),
            isRead: false,
          }
        ],
        unreadCount: 1,
        
        // Actions
        setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
        
        setContextPanelCollapsed: (collapsed) => set({ contextPanelCollapsed: collapsed }),
        
        setActiveModal: (modal) => set({ activeModal: modal }),
        
        setTheme: (theme) => {
          set({ theme });
          // Update settings in storage
          const { userSettings } = get();
          const newSettings = { ...userSettings, theme };
          storage.saveSettings(newSettings);
          set({ userSettings: newSettings });
          
          // Apply theme to document
          if (theme === 'system') {
            document.documentElement.classList.remove('light', 'dark');
          } else {
            document.documentElement.classList.remove('light', 'dark');
            document.documentElement.classList.add(theme);
          }
        },
        
        updateUserSettings: (settings) => {
          const { userSettings } = get();
          const newSettings = { ...userSettings, ...settings };
          storage.saveSettings(newSettings);
          set({ userSettings: newSettings });
          
          // Update MCP client URL if changed
          if (settings.mcpServerUrl) {
            mcpClient.setServerUrl(settings.mcpServerUrl);
          }
        },
        
        updateMetrics: (newMetrics) => {
          const { metrics } = get();
          set({ metrics: { ...metrics, ...newMetrics } });
        },
        
        setConnectionStatus: (connected) => {
          set({ 
            isConnected: connected,
            lastConnectionCheck: new Date().toISOString(),
            serverHealth: connected ? get().serverHealth : null
          });
          
          if (connected) {
            get().addNotification({
              type: 'success',
              title: 'Conexión establecida',
              message: 'Conectado al MCP Server correctamente',
              isRead: false,
            });
          } else {
            get().addNotification({
              type: 'warning',
              title: 'Conexión perdida',
              message: 'No se puede conectar al MCP Server',
              isRead: false,
            });
          }
        },
        
        addNotification: (notification) => {
          const { notifications, unreadCount } = get();
          const newNotification: Notification = {
            ...notification,
            id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toISOString(),
          };
          
          set({ 
            notifications: [newNotification, ...notifications],
            unreadCount: unreadCount + 1
          });
          
          // Show desktop notification if enabled
          if (get().userSettings.notifications.desktop && 'Notification' in window) {
            if (Notification.permission === 'granted') {
              new Notification(notification.title, {
                body: notification.message,
                icon: '/favicon.ico'
              });
            }
          }
        },
        
        markNotificationRead: (id) => {
          const { notifications, unreadCount } = get();
          const updated = notifications.map(n => 
            n.id === id ? { ...n, isRead: true } : n
          );
          set({ 
            notifications: updated,
            unreadCount: Math.max(0, unreadCount - 1)
          });
        },
        
        clearNotifications: () => {
          set({ notifications: [], unreadCount: 0 });
        },
        
        checkServerHealth: async () => {
          try {
            const health = await mcpClient.checkHealth();
            if (health) {
              set({
                isConnected: true,
                serverHealth: health,
                lastConnectionCheck: new Date().toISOString(),
              });
              
              // Update system status
              const { metrics } = get();
              set({
                metrics: {
                  ...metrics,
                  systemStatus: health.status === 'healthy' ? 'healthy' : 'unhealthy'
                }
              });
            } else {
              set({
                isConnected: false,
                serverHealth: null,
                lastConnectionCheck: new Date().toISOString(),
              });
              
              // Update system status
              const { metrics } = get();
              set({
                metrics: {
                  ...metrics,
                  systemStatus: 'unhealthy'
                }
              });
            }
          } catch (error) {
            console.error('Health check failed:', error);
            set({
              isConnected: false,
              serverHealth: null,
              lastConnectionCheck: new Date().toISOString(),
            });
          }
        },
        
        updateMetricsFromServer: async () => {
          try {
            const metricsData = await mcpClient.getMetrics();
            if (metricsData) {
              const { metrics } = get();
              set({
                metrics: {
                  ...metrics,
                  tokensUsed: metricsData.tokens_used,
                  tokensAvailable: metricsData.tokens_used * 3, // Estimate available tokens
                  activeProjects: metricsData.active_projects,
                  activeConversations: metricsData.total_conversations,
                  responseTime: 250 + metricsData.system_load * 100, // Calculate from system load
                  requestsTotal: metricsData.tokens_used / 10, // Estimate from tokens
                  requestsPerMinute: Math.floor(metricsData.tokens_used / 60), // Approximate
                  successRate: 95 + (1 - metricsData.system_load) * 5, // Calculate from load
                  averageLatency: 200 + metricsData.system_load * 200, // Calculate from load
                  p95Latency: 350 + metricsData.system_load * 300, // Calculate from load
                  p99Latency: 500 + metricsData.system_load * 400, // Calculate from load
                  systemStatus: get().isConnected ? 'healthy' : 'unhealthy',
                }
              });
            }
          } catch (error) {
            console.error('Failed to update metrics:', error);
          }
        },
        
        syncSettingsWithStorage: () => {
          const currentSettings = storage.loadSettings();
          set({ userSettings: currentSettings });
          
          // Update theme if changed
          if (currentSettings.theme !== get().theme) {
            set({ theme: currentSettings.theme });
            if (currentSettings.theme === 'system') {
              document.documentElement.classList.remove('light', 'dark');
            } else {
              document.documentElement.classList.remove('light', 'dark');
              document.documentElement.classList.add(currentSettings.theme);
            }
          }
          
          // Update MCP client URL
          if (currentSettings.mcpServerUrl) {
            mcpClient.setServerUrl(currentSettings.mcpServerUrl);
          }
        },
      };
    },
    {
      name: 'iris-app-store',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        contextPanelCollapsed: state.contextPanelCollapsed,
        theme: state.theme,
        userSettings: state.userSettings,
      }),
    }
  )
);

// Initialize theme on app start
if (typeof window !== 'undefined') {
  const store = useAppStore.getState();
  
  // Sync settings with storage
  store.syncSettingsWithStorage();
  
  // Set initial theme
  if (store.theme === 'system') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.classList.toggle('dark', prefersDark);
    document.documentElement.classList.toggle('light', !prefersDark);
  } else {
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(store.theme);
  }
  
  // Check server health on startup
  setTimeout(() => {
    store.checkServerHealth();
    store.updateMetricsFromServer();
  }, 2000);
  
  // Set up periodic health checks
  setInterval(() => {
    store.checkServerHealth();
  }, 30000); // Every 30 seconds
  
  // Set up periodic metrics updates
  setInterval(() => {
    if (store.isConnected) {
      store.updateMetricsFromServer();
    }
  }, 60000); // Every minute
}

// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
  Notification.requestPermission();
}