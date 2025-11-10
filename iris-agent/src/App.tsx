import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAppStore } from './stores/appStore';
import { useConnection } from './hooks/useConnection';
import { useToast } from './hooks/useToast';
import { ErrorBoundary, ErrorFallback } from './components/ui/ErrorHandling';
import { ToastManager } from './components/ui/Toast';
import Layout from './components/layout/Layout';
import Dashboard from './components/dashboard/Dashboard';
import Chat from './components/chat/Chat';
import Editor from './components/editor/Editor';
import Projects from './components/projects/Projects';
import Canvas from './components/canvas/Canvas';
import Files from './components/files/Files';
import Templates from './components/templates/Templates';
import Settings from './components/settings/Settings';
import Notifications from './components/notifications/Notifications';
import AssetsPage from './pages/AssetsPage';
import MemoryPage from './pages/MemoryPage';
import ToolsPage from './pages/ToolsPage';
import TaskPage from './pages/TaskPage';
import BridgePage from './pages/BridgePage';
import LivePreviewPage from './pages/LivePreviewPage';
import { LoadingSpinner } from './components/ui/LoadingStates';
import { ConnectionStatus } from './components/ui/ConnectionStatus';
import './index.css';

function App() {
  const { theme, activeModal } = useAppStore();
  const { toasts, removeToast, connectionError } = useToast();
  
  // Connection management
  const {
    isConnected,
    isReconnecting,
    healthStatus,
    shouldReconnect,
    forceReconnect
  } = useConnection({
    autoReconnect: true,
    maxAttempts: 3,
    retryDelay: 2000,
    onConnect: () => {
      // Show success toast when connected
      console.log('Connected to IRIS Code server');
    },
    onDisconnect: () => {
      connectionError('Se perdió la conexión con el servidor');
    },
    onReconnect: () => {
      console.log('Successfully reconnected to IRIS Code server');
    }
  });

  // Apply theme to document
  React.useEffect(() => {
    if (theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Show initial loading state
  if (!isConnected && !isReconnecting) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <LoadingSpinner 
          size="lg" 
          message="Conectando con IRIS Code..."
          showRefresh 
          onRefresh={forceReconnect}
        />
      </div>
    );
  }

  const AppContent = () => (
    <Router>
      <div className="min-h-screen bg-background text-foreground">
        {/* Connection Status Bar */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                IRIS Code - Sistema Multi-Agente
              </h1>
              <ConnectionStatus showDetails />
            </div>
            
            {isReconnecting && (
              <div className="flex items-center gap-2 text-sm text-yellow-600 dark:text-yellow-400">
                <LoadingSpinner size="sm" />
                <span>Reconectando...</span>
              </div>
            )}
          </div>
        </div>

        <Layout>
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/assets" element={<AssetsPage />} />
              <Route path="/memory" element={<MemoryPage />} />
              <Route path="/tools" element={<ToolsPage />} />
              <Route path="/tasks" element={<TaskPage />} />
              <Route path="/bridge" element={<BridgePage />} />
              <Route path="/live-preview/:projectId" element={<LivePreviewPage />} />
              <Route path="/editor" element={<Editor />} />
              <Route path="/canvas" element={<Canvas />} />
              <Route path="/files" element={<Files />} />
              <Route path="/templates" element={<Templates />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </ErrorBoundary>
        </Layout>

        {/* Modals */}
        {activeModal === 'notifications' && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="iris-card w-full max-w-2xl m-4 max-h-[80vh] overflow-hidden">
              <Notifications onClose={() => useAppStore.getState().setActiveModal(null)} />
            </div>
          </div>
        )}

        {/* Toast Notifications */}
        <ToastManager toasts={toasts} onClose={removeToast} />
      </div>
    </Router>
  );

  // Wrap everything in error boundary
  return (
    <ErrorBoundary
      fallback={({ error, resetError }) => (
        <ErrorFallback
          error={error}
          resetError={resetError}
          title="Error en la aplicación"
          message="Se produjo un error inesperado en IRIS Code"
          showDetails={process.env.NODE_ENV === 'development'}
        />
      )}
    >
      <AppContent />
    </ErrorBoundary>
  );
}

export default App;