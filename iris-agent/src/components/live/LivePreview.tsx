import React, { useState, useEffect, useCallback } from 'react';
import { 
  Monitor, 
  Terminal, 
  Container, 
  Code, 
  Play, 
  Square, 
  Settings, 
  Eye, 
  EyeOff, 
  Maximize2, 
  Minimize2,
  Zap,
  Download,
  Share2,
  Users,
  RotateCcw
} from 'lucide-react';

// Import individual components
import LivePreviewEngine from './LivePreviewEngine';
import MultiTerminalManager from './MultiTerminalManager';
import WebContainerManager from './WebContainerManager';

// Types
interface LivePreviewProps {
  projectId: string;
  projectFiles: Record<string, string>;
  initialFramework?: string;
  onClose?: () => void;
  onDeploy?: (projectId: string) => void;
  isCollaborationMode?: boolean;
}

interface ViewLayout {
  preview: 'main' | 'split' | 'minimized';
  terminals: 'main' | 'split' | 'minimized';
  container: 'main' | 'split' | 'minimized';
  editor: 'main' | 'split' | 'minimized';
}

interface PreviewStats {
  activeTerminals: number;
  containerUptime: number;
  previewUrl: string | null;
  lastActivity: Date;
  buildTime: number;
  memoryUsage: number;
}

const LivePreview: React.FC<LivePreviewProps> = ({
  projectId,
  projectFiles,
  initialFramework = 'react',
  onClose,
  onDeploy,
  isCollaborationMode = false
}) => {
  // Main state
  const [isRunning, setIsRunning] = useState(false);
  const [selectedFramework, setSelectedFramework] = useState(initialFramework);
  const [activeView, setActiveView] = useState<'preview' | 'terminals' | 'container' | 'overview'>('overview');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Layout and UI state
  const [layout, setLayout] = useState<ViewLayout>({
    preview: 'main',
    terminals: 'split',
    container: 'split',
    editor: 'main'
  });

  const [previewStats, setPreviewStats] = useState<PreviewStats>({
    activeTerminals: 0,
    containerUptime: 0,
    previewUrl: null,
    lastActivity: new Date(),
    buildTime: 0,
    memoryUsage: 0
  });

  const [collaborators, setCollaborators] = useState<string[]>([]);
  const [isCollaborating, setIsCollaborating] = useState(isCollaborationMode);

  // Settings
  const [settings, setSettings] = useState({
    autoSave: true,
    hotReload: true,
    autoDeploy: false,
    showLineNumbers: true,
    theme: 'dark',
    fontSize: 14,
    terminalCount: 5,
    maxMemory: 512,
    debugMode: false
  });

  // Auto-save functionality
  useEffect(() => {
    if (!settings.autoSave) return;

    const saveTimeout = setTimeout(() => {
      // Auto-save would go here
      console.log('Auto-saving project changes...');
    }, 2000);

    return () => clearTimeout(saveTimeout);
  }, [projectFiles, settings.autoSave]);

  // Start live preview session
  const startPreview = useCallback(async () => {
    setIsLoading(true);
    
    try {
      setIsRunning(true);
      setPreviewStats(prev => ({ 
        ...prev, 
        lastActivity: new Date(),
        containerUptime: 0
      }));
      
      // Initialize collaboration if enabled
      if (isCollaborating) {
        setCollaborators(['You', 'IRIS Agent']);
      }
      
    } catch (error) {
      console.error('Failed to start preview:', error);
    } finally {
      setIsLoading(false);
    }
  }, [isCollaborating]);

  // Stop live preview session
  const stopPreview = useCallback(() => {
    setIsRunning(false);
    setIsLoading(false);
    setCollaborators([]);
    
    setPreviewStats(prev => ({
      ...prev,
      previewUrl: null,
      containerUptime: 0
    }));
  }, []);

  // Toggle layout view
  const toggleView = useCallback((view: keyof ViewLayout) => {
    setLayout(prev => ({
      ...prev,
      [view]: prev[view] === 'minimized' ? 'main' : 'minimized'
    }));
  }, []);

  // Switch active view
  const switchView = useCallback((view: typeof activeView) => {
    setActiveView(view);
  }, []);

  // Deploy project
  const handleDeploy = useCallback(() => {
    if (onDeploy) {
      onDeploy(projectId);
    } else {
      // Fallback deployment
      const deployUrl = `https://${projectId}.iris-preview.app`;
      setPreviewStats(prev => ({ ...prev, previewUrl: deployUrl }));
      window.open(deployUrl, '_blank');
    }
  }, [projectId, onDeploy]);

  // Share session
  const shareSession = useCallback(() => {
    const shareUrl = `${window.location.origin}/share/${projectId}`;
    navigator.clipboard.writeText(shareUrl);
    alert('Session link copied to clipboard!');
  }, [projectId]);

  // Reset session
  const resetSession = useCallback(() => {
    if (confirm('Are you sure you want to reset the session? All changes will be lost.')) {
      stopPreview();
      setTimeout(() => {
        startPreview();
      }, 1000);
    }
  }, [stopPreview, startPreview]);

  // Framework detection
  const detectedFramework = React.useMemo(() => {
    if (projectFiles['package.json']) {
      try {
        const pkg = JSON.parse(projectFiles['package.json']);
        const deps = { ...pkg.dependencies, ...pkg.devDependencies };
        
        if (deps.next) return 'next';
        if (deps.vue) return 'vue';
        if (deps['@angular/core']) return 'angular';
        if (deps.svelte) return 'svelte';
        if (deps.vite) return 'vite';
      } catch (e) {
        // Fallback
      }
    }
    return 'react';
  }, [projectFiles]);

  useEffect(() => {
    if (detectedFramework !== selectedFramework) {
      setSelectedFramework(detectedFramework);
    }
  }, [detectedFramework, selectedFramework]);

  // Get view size classes
  const getViewSizeClass = (view: keyof ViewLayout) => {
    switch (layout[view]) {
      case 'main':
        return 'flex-1';
      case 'split':
        return 'flex-1';
      case 'minimized':
        return 'h-12';
      default:
        return 'flex-1';
    }
  };

  // Get visibility for views
  const getViewVisibility = (view: typeof activeView) => {
    if (activeView === 'overview') return true;
    return activeView === view;
  };

  // Framework icons
  const frameworkIcons: Record<string, React.ReactNode> = {
    react: <div className="w-4 h-4 bg-blue-500 rounded" />,
    vue: <div className="w-4 h-4 bg-green-500 rounded" />,
    angular: <div className="w-4 h-4 bg-red-500 rounded" />,
    svelte: <div className="w-4 h-4 bg-orange-500 rounded" />,
    next: <div className="w-4 h-4 bg-gray-800 rounded" />,
    vite: <div className="w-4 h-4 bg-purple-500 rounded" />
  };

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50' : 'h-full'} bg-gray-100 flex flex-col`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-white border-b shadow-sm">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Zap className="w-6 h-6 text-yellow-500" />
            <h1 className="text-xl font-bold text-gray-900">Live Preview</h1>
          </div>
          
          <div className="flex items-center space-x-2">
            {frameworkIcons[selectedFramework]}
            <span className="text-sm font-medium text-gray-700">
              {selectedFramework.toUpperCase()}
            </span>
          </div>

          {isCollaborating && (
            <div className="flex items-center space-x-1 text-sm text-gray-600">
              <Users className="w-4 h-4" />
              <span>{collaborators.length} active</span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {/* Session Stats */}
          {isRunning && (
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>Terminals: {previewStats.activeTerminals}</span>
              <span>Uptime: {Math.floor(previewStats.containerUptime / 60)}m</span>
              {previewStats.previewUrl && (
                <span className="text-green-600">• Live</span>
              )}
            </div>
          )}

          {/* Control Buttons */}
          {!isRunning ? (
            <button
              onClick={startPreview}
              disabled={isLoading}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              <Play className="w-4 h-4" />
              <span>{isLoading ? 'Starting...' : 'Start Preview'}</span>
            </button>
          ) : (
            <div className="flex space-x-2">
              <button
                onClick={resetSession}
                className="p-2 text-gray-600 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                title="Reset session"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              
              <button
                onClick={shareSession}
                className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Share session"
              >
                <Share2 className="w-4 h-4" />
              </button>

              {previewStats.previewUrl && (
                <button
                  onClick={handleDeploy}
                  className="flex items-center space-x-1 px-3 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Deploy</span>
                </button>
              )}
              
              <button
                onClick={stopPreview}
                className="flex items-center space-x-1 px-3 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
              >
                <Square className="w-4 h-4" />
                <span>Stop</span>
              </button>
            </div>
          )}

          <div className="w-px h-6 bg-gray-300" />

          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Settings className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>

          {onClose && (
            <button
              onClick={onClose}
              className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Square className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center bg-white border-b">
        {[
          { id: 'overview', label: 'Overview', icon: Monitor },
          { id: 'preview', label: 'Preview', icon: Eye },
          { id: 'terminals', label: 'Terminals', icon: Terminal },
          { id: 'container', label: 'Container', icon: Container }
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => switchView(id as any)}
            className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors ${
              activeView === id
                ? 'border-blue-500 text-blue-600 bg-blue-50'
                : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50'
            }`}
          >
            <Icon className="w-4 h-4" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex">
        {/* Sidebar - View Controls */}
        {getViewVisibility('overview') && (
          <div className="w-64 bg-white border-r">
            <div className="p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">View Controls</h3>
              
              <div className="space-y-2">
                {[
                  { key: 'preview', label: 'Live Preview', icon: Eye },
                  { key: 'terminals', label: 'Terminals', icon: Terminal },
                  { key: 'container', label: 'Container', icon: Container }
                ].map(({ key, label, icon: Icon }) => (
                  <div
                    key={key}
                    className={`flex items-center justify-between p-2 rounded cursor-pointer transition-colors ${
                      layout[key as keyof ViewLayout] !== 'minimized'
                        ? 'bg-blue-50 text-blue-700'
                        : 'hover:bg-gray-50'
                    }`}
                    onClick={() => toggleView(key as keyof ViewLayout)}
                  >
                    <div className="flex items-center space-x-2">
                      <Icon className="w-4 h-4" />
                      <span className="text-sm">{label}</span>
                    </div>
                    {layout[key as keyof ViewLayout] === 'minimized' ? (
                      <EyeOff className="w-3 h-3" />
                    ) : (
                      <Eye className="w-3 h-3" />
                    )}
                  </div>
                ))}
              </div>

              {/* Collaboration Panel */}
              {isCollaborating && (
                <div className="mt-6">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3">Collaborators</h4>
                  <div className="space-y-2">
                    {collaborators.map((collaborator, index) => (
                      <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
                        <div className="w-2 h-2 bg-green-500 rounded-full" />
                        <span className="text-sm text-gray-700">{collaborator}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Session Info */}
              {isRunning && (
                <div className="mt-6 p-3 bg-gray-50 rounded">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Session Info</h4>
                  <div className="space-y-1 text-xs text-gray-600">
                    <div>Project: {projectId}</div>
                    <div>Framework: {selectedFramework}</div>
                    <div>Files: {Object.keys(projectFiles).length}</div>
                    <div>Uptime: {Math.floor(previewStats.containerUptime / 60)}m {previewStats.containerUptime % 60}s</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Overview Dashboard */}
          {activeView === 'overview' && (
            <div className="flex-1 p-6 bg-white">
              <div className="max-w-4xl mx-auto">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Live Preview Dashboard</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Preview Card */}
                  <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-xl text-white">
                    <div className="flex items-center justify-between mb-4">
                      <Eye className="w-8 h-8" />
                      <span className="text-blue-200">Live</span>
                    </div>
                    <h3 className="text-xl font-semibold mb-2">Live Preview</h3>
                    <p className="text-blue-100 mb-4">Instant preview with hot reloading</p>
                    <button
                      onClick={() => switchView('preview')}
                      className="px-4 py-2 bg-white text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors"
                    >
                      Open Preview
                    </button>
                  </div>

                  {/* Terminals Card */}
                  <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-xl text-white">
                    <div className="flex items-center justify-between mb-4">
                      <Terminal className="w-8 h-8" />
                      <span className="text-green-200">{previewStats.activeTerminals}</span>
                    </div>
                    <h3 className="text-xl font-semibold mb-2">Multi-Terminal</h3>
                    <p className="text-green-100 mb-4">Simultaneous terminal sessions</p>
                    <button
                      onClick={() => switchView('terminals')}
                      className="px-4 py-2 bg-white text-green-600 rounded-lg font-medium hover:bg-green-50 transition-colors"
                    >
                      Open Terminals
                    </button>
                  </div>

                  {/* Container Card */}
                  <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 rounded-xl text-white">
                    <div className="flex items-center justify-between mb-4">
                      <Container className="w-8 h-8" />
                      <span className="text-purple-200">Secure</span>
                    </div>
                    <h3 className="text-xl font-semibold mb-2">WebContainer</h3>
                    <p className="text-purple-100 mb-4">Browser-based development environment</p>
                    <button
                      onClick={() => switchView('container')}
                      className="px-4 py-2 bg-white text-purple-600 rounded-lg font-medium hover:bg-purple-50 transition-colors"
                    >
                      Open Container
                    </button>
                  </div>
                </div>

                {/* Project Information */}
                <div className="mt-8 p-6 bg-gray-50 rounded-xl">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Project ID:</span>
                      <span className="ml-2 text-gray-600">{projectId}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Framework:</span>
                      <span className="ml-2 text-gray-600">{selectedFramework}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Files:</span>
                      <span className="ml-2 text-gray-600">{Object.keys(projectFiles).length} files</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Status:</span>
                      <span className={`ml-2 ${isRunning ? 'text-green-600' : 'text-gray-600'}`}>
                        {isRunning ? 'Running' : 'Stopped'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Live Preview Engine */}
          {activeView === 'preview' && getViewVisibility('preview') && layout.preview !== 'minimized' && (
            <div className={getViewSizeClass('preview')}>
              <LivePreviewEngine
                projectId={projectId}
                projectFiles={projectFiles}
                activeFile={Object.keys(projectFiles)[0] || ''}
                isRunning={isRunning}
                onStartPreview={() => setIsRunning(true)}
                onStopPreview={stopPreview}
                onFileChange={(path, content) => {
                  // File change handling would go here
                }}
              />
            </div>
          )}

          {/* Multi-Terminal Manager */}
          {activeView === 'terminals' && getViewVisibility('terminals') && layout.terminals !== 'minimized' && (
            <div className={getViewSizeClass('terminals')}>
              <MultiTerminalManager
                projectId={projectId}
                isProjectRunning={isRunning}
                onCommand={(terminalId, command) => {
                  console.log('Command:', terminalId, command);
                }}
                onTerminalOutput={(terminalId, output) => {
                  // Update terminal count
                  setPreviewStats(prev => ({ ...prev, activeTerminals: prev.activeTerminals + 1 }));
                }}
              />
            </div>
          )}

          {/* WebContainer Manager */}
          {activeView === 'container' && getViewVisibility('container') && layout.container !== 'minimized' && (
            <div className={getViewSizeClass('container')}>
              <WebContainerManager
                projectId={projectId}
                projectFiles={projectFiles}
                selectedFramework={selectedFramework}
                onProcessStart={(processId, process) => {
                  console.log('Process started:', processId);
                }}
                onProcessExit={(processId, code) => {
                  console.log('Process exited:', processId, code);
                }}
                onFileSystemChange={(path, content) => {
                  // File system change handling
                }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="absolute top-16 right-4 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-20 p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Preview Settings</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm text-gray-700">Auto Save</label>
              <input
                type="checkbox"
                checked={settings.autoSave}
                onChange={(e) => setSettings(prev => ({ ...prev, autoSave: e.target.checked }))}
                className="text-blue-600"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-sm text-gray-700">Hot Reload</label>
              <input
                type="checkbox"
                checked={settings.hotReload}
                onChange={(e) => setSettings(prev => ({ ...prev, hotReload: e.target.checked }))}
                className="text-blue-600"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-sm text-gray-700">Auto Deploy</label>
              <input
                type="checkbox"
                checked={settings.autoDeploy}
                onChange={(e) => setSettings(prev => ({ ...prev, autoDeploy: e.target.checked }))}
                className="text-blue-600"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-sm text-gray-700">Collaboration</label>
              <input
                type="checkbox"
                checked={isCollaborating}
                onChange={(e) => setIsCollaborating(e.target.checked)}
                className="text-blue-600"
              />
            </div>

            <div>
              <label className="text-sm text-gray-700">Theme</label>
              <select
                value={settings.theme}
                onChange={(e) => setSettings(prev => ({ ...prev, theme: e.target.value }))}
                className="w-full mt-1 px-2 py-1 text-sm border border-gray-300 rounded"
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
                <option value="auto">Auto</option>
              </select>
            </div>

            <div>
              <label className="text-sm text-gray-700">Font Size</label>
              <input
                type="number"
                value={settings.fontSize}
                onChange={(e) => setSettings(prev => ({ ...prev, fontSize: parseInt(e.target.value) }))}
                className="w-full mt-1 px-2 py-1 text-sm border border-gray-300 rounded"
                min="10"
                max="24"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-2 mt-4">
            <button
              onClick={() => setShowSettings(false)}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={() => setShowSettings(false)}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Save
            </button>
          </div>
        </div>
      )}

      {/* Minimized View Indicators */}
      {Object.entries(layout).some(([_, value]) => value === 'minimized') && (
        <div className="absolute bottom-4 left-4 flex space-x-2 z-10">
          {Object.entries(layout).filter(([_, value]) => value === 'minimized').map(([key, _]) => (
            <button
              key={key}
              onClick={() => {
                setLayout(prev => ({ ...prev, [key]: 'main' }));
                switchView(key as any);
              }}
              className="p-2 bg-white border border-gray-200 rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
              title={`Show ${key}`}
            >
              {key === 'preview' && <Eye className="w-4 h-4" />}
              {key === 'terminals' && <Terminal className="w-4 h-4" />}
              {key === 'container' && <Container className="w-4 h-4" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default LivePreview;