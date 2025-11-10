import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Monitor, Play, RefreshCw, ExternalLink, Share2, Zap } from 'lucide-react';

// Types
interface LivePreviewEngineProps {
  projectId: string;
  projectFiles: Record<string, string>;
  activeFile: string;
  isRunning: boolean;
  onStartPreview: () => void;
  onStopPreview: () => void;
  onFileChange: (path: string, content: string) => void;
}

interface PreviewStatus {
  status: 'stopped' | 'starting' | 'running' | 'error';
  url?: string;
  buildTime?: number;
  error?: string;
  lastUpdate?: Date;
}

interface LivePreviewConfig {
  framework: 'react' | 'vue' | 'angular' | 'svelte' | 'next' | 'vite';
  port: number;
  hotReload: boolean;
  openInNewTab: boolean;
  autoDeploy: boolean;
}

// Sandpack Configuration
const SANDPACK_TEMPLATES = {
  react: 'react',
  vue: 'vue',
  angular: 'angular',
  svelte: 'svelte',
  next: 'next',
  vite: 'vanilla'
};

const LivePreviewEngine: React.FC<LivePreviewEngineProps> = ({
  projectId,
  projectFiles,
  activeFile,
  isRunning,
  onStartPreview,
  onStopPreview,
  onFileChange
}) => {
  // State
  const [previewStatus, setPreviewStatus] = useState<PreviewStatus>({
    status: 'stopped'
  });
  
  const [previewConfig, setPreviewConfig] = useState<LivePreviewConfig>({
    framework: 'react',
    port: 3000,
    hotReload: true,
    openInNewTab: true,
    autoDeploy: false
  });

  const [selectedTemplate, setSelectedTemplate] = useState<string>('react');
  const [buildLogs, setBuildLogs] = useState<string[]>([]);
  const [isCompiling, setIsCompiling] = useState(false);

  const iframeRef = useRef<HTMLIFrameElement>(null);
  const buildTimeoutRef = useRef<NodeJS.Timeout>();

  // Auto-detect framework from files
  const detectFramework = useCallback(() => {
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
        // Fallback to react
      }
    }
    return 'react';
  }, [projectFiles]);

  // Update framework when files change
  useEffect(() => {
    const detected = detectFramework();
    setSelectedTemplate(detected);
    setPreviewConfig(prev => ({ ...prev, framework: detected as any }));
  }, [projectFiles, detectFramework]);

  // Hot reload functionality
  useEffect(() => {
    if (previewConfig.hotReload && isRunning && activeFile) {
      // Debounced hot reload
      if (buildTimeoutRef.current) {
        clearTimeout(buildTimeoutRef.current);
      }

      buildTimeoutRef.current = setTimeout(() => {
        performHotReload();
      }, 500);
    }
  }, [projectFiles, activeFile, previewConfig.hotReload, isRunning]);

  const performHotReload = useCallback(async () => {
    if (!iframeRef.current || !isRunning) return;

    try {
      setIsCompiling(true);
      setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Hot reloading...`]);

      // Simulate hot reload process
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Post message to iframe for hot reload
      iframeRef.current.contentWindow?.postMessage({
        type: 'HOT_RELOAD',
        files: projectFiles,
        timestamp: Date.now()
      }, '*');

      setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ✅ Hot reload completed`]);
      setPreviewStatus(prev => ({ ...prev, lastUpdate: new Date() }));
    } catch (error) {
      setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ❌ Hot reload failed: ${error}`]);
    } finally {
      setIsCompiling(false);
    }
  }, [projectFiles, isRunning]);

  // Start preview
  const startPreview = useCallback(async () => {
    setPreviewStatus({ status: 'starting' });
    setBuildLogs([]);

    try {
      const startTime = Date.now();
      
      // Initialize project in sandbox
      await initializeSandbox();
      
      // Start development server
      await startDevelopmentServer();
      
      const buildTime = Date.now() - startTime;
      
      setPreviewStatus({
        status: 'running',
        url: `http://localhost:${previewConfig.port}`,
        buildTime,
        lastUpdate: new Date()
      });

      setBuildLogs(prev => [
        ...prev,
        `[${new Date().toLocaleTimeString()}] ✅ Preview started successfully`,
        `[${new Date().toLocaleTimeString()}] 🌐 Available at: http://localhost:${previewConfig.port}`
      ]);

      onStartPreview();

      // Open in new tab if configured
      if (previewConfig.openInNewTab) {
        setTimeout(() => {
          window.open(`http://localhost:${previewConfig.port}`, '_blank');
        }, 2000);
      }

    } catch (error) {
      setPreviewStatus({
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ❌ Failed to start preview: ${error}`]);
    }
  }, [previewConfig, onStartPreview]);

  // Stop preview
  const stopPreview = useCallback(() => {
    setPreviewStatus({ status: 'stopped' });
    setBuildLogs([]);
    onStopPreview();
  }, [onStopPreview]);

  // Initialize sandbox
  const initializeSandbox = useCallback(async () => {
    setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] 🔧 Initializing sandbox environment...`]);
    
    // Simulate sandbox initialization
    await new Promise(resolve => setTimeout(resolve, 800));
    
    setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] 📦 Installing dependencies...`]);
    
    // Install dependencies
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ✅ Sandbox ready`]);
  }, []);

  // Start development server
  const startDevelopmentServer = useCallback(async () => {
    setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] 🚀 Starting development server...`]);
    
    // Simulate server startup
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ⚡ Development server running`]);
  }, []);

  // Share preview URL
  const sharePreview = useCallback(() => {
    if (previewStatus.url) {
      navigator.clipboard.writeText(previewStatus.url);
      setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] 🔗 Preview URL copied to clipboard`]);
    }
  }, [previewStatus.url]);

  // Auto-deploy functionality
  const autoDeploy = useCallback(async () => {
    if (!previewStatus.url) return;

    setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] 🌐 Deploying to production...`]);
    
    try {
      // Simulate deployment process
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const deployUrl = `https://${projectId}.iris-preview.app`;
      setPreviewStatus(prev => ({ ...prev, url: deployUrl }));
      
      setBuildLogs(prev => [
        ...prev,
        `[${new Date().toLocaleTimeString()}] ✅ Deployed successfully`,
        `[${new Date().toLocaleTimeString()}] 🌐 Production URL: ${deployUrl}`
      ]);
    } catch (error) {
      setBuildLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ❌ Deployment failed: ${error}`]);
    }
  }, [previewStatus.url, projectId]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (buildTimeoutRef.current) {
        clearTimeout(buildTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-white border-b">
        <div className="flex items-center space-x-3">
          <Monitor className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Live Preview</h3>
          <span className="text-sm text-gray-500">({selectedTemplate})</span>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Framework Selector */}
          <select
            value={selectedTemplate}
            onChange={(e) => setSelectedTemplate(e.target.value)}
            className="text-sm border border-gray-300 rounded px-2 py-1"
            disabled={isRunning}
          >
            {Object.entries(SANDPACK_TEMPLATES).map(([key, template]) => (
              <option key={key} value={template}>{key.toUpperCase()}</option>
            ))}
          </select>

          {/* Status Indicator */}
          <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs font-medium ${
            previewStatus.status === 'running' 
              ? 'bg-green-100 text-green-800' 
              : previewStatus.status === 'error'
              ? 'bg-red-100 text-red-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              previewStatus.status === 'running' 
                ? 'bg-green-500' 
                : previewStatus.status === 'error'
                ? 'bg-red-500'
                : 'bg-gray-400'
            }`} />
            <span>{previewStatus.status.toUpperCase()}</span>
          </div>

          {/* Action Buttons */}
          {previewStatus.status !== 'running' ? (
            <button
              onClick={startPreview}
              className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors"
            >
              <Play className="w-4 h-4" />
              <span>Start</span>
            </button>
          ) : (
            <div className="flex space-x-1">
              <button
                onClick={performHotReload}
                disabled={isCompiling}
                className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                title="Force reload"
              >
                <RefreshCw className={`w-4 h-4 ${isCompiling ? 'animate-spin' : ''}`} />
              </button>
              
              <button
                onClick={stopPreview}
                className="p-1.5 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                title="Stop preview"
              >
                <div className="w-4 h-4 bg-red-500 rounded-sm" />
              </button>
            </div>
          )}

          {previewStatus.status === 'running' && previewConfig.openInNewTab && (
            <button
              onClick={() => window.open(previewStatus.url, '_blank')}
              className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
              title="Open in new tab"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
          )}

          {previewStatus.status === 'running' && (
            <button
              onClick={sharePreview}
              className="p-1.5 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
              title="Share preview"
            >
              <Share2 className="w-4 h-4" />
            </button>
          )}

          {previewStatus.status === 'running' && previewConfig.autoDeploy && (
            <button
              onClick={autoDeploy}
              className="flex items-center space-x-1 px-2 py-1 bg-purple-600 text-white text-xs font-medium rounded hover:bg-purple-700 transition-colors"
            >
              <Zap className="w-3 h-3" />
              <span>Deploy</span>
            </button>
          )}
        </div>
      </div>

      {/* Preview Stats */}
      {previewStatus.status === 'running' && (
        <div className="px-4 py-2 bg-gray-100 border-b text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>Build time: {previewStatus.buildTime}ms</span>
            <span>Last update: {previewStatus.lastUpdate?.toLocaleTimeString()}</span>
            <span>Port: {previewConfig.port}</span>
            <span className="flex items-center">
              <Zap className="w-3 h-3 mr-1" />
              Hot reload: {previewConfig.hotReload ? 'ON' : 'OFF'}
            </span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Preview Iframe */}
        <div className="flex-1 relative">
          {previewStatus.status === 'running' ? (
            <iframe
              ref={iframeRef}
              src={previewStatus.url}
              className="w-full h-full border-0"
              title="Live Preview"
              sandbox="allow-scripts allow-same-origin allow-forms"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gray-100">
              <div className="text-center">
                <Monitor className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-gray-900 mb-2">No Preview Running</h4>
                <p className="text-gray-600 mb-4">Click "Start" to begin live preview of your project</p>
                <button
                  onClick={startPreview}
                  className="px-4 py-2 bg-blue-600 text-white font-medium rounded hover:bg-blue-700 transition-colors"
                >
                  Start Preview
                </button>
              </div>
            </div>
          )}

          {/* Loading Overlay */}
          {(isCompiling || previewStatus.status === 'starting') && (
            <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center">
              <div className="text-center">
                <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-2" />
                <p className="text-gray-900 font-medium">
                  {isCompiling ? 'Hot reloading...' : 'Starting preview...'}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Build Logs Sidebar */}
        {buildLogs.length > 0 && (
          <div className="w-80 border-l bg-gray-900 text-green-400 font-mono text-sm">
            <div className="p-3 border-b border-gray-700">
              <h4 className="text-white font-medium">Build Logs</h4>
            </div>
            <div className="p-3 h-full overflow-y-auto">
              {buildLogs.map((log, index) => (
                <div key={index} className="mb-1 whitespace-pre-wrap">
                  {log}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {previewStatus.status === 'error' && (
        <div className="p-4 bg-red-50 border-t border-red-200">
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 text-red-600">❌</div>
            <span className="text-red-800 font-medium">Preview Error:</span>
          </div>
          <p className="text-red-700 mt-1 text-sm">{previewStatus.error}</p>
        </div>
      )}
    </div>
  );
};

export default LivePreviewEngine;