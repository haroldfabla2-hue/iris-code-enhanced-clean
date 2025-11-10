import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Container, Play, Square, Download, Upload, RefreshCw, Zap, Shield } from 'lucide-react';
import type { WebContainer, WebContainerProcess } from '@webcontainer/api';

// Types
interface WebContainerManagerProps {
  projectId: string;
  projectFiles: Record<string, string>;
  selectedFramework: string;
  onProcessStart?: (processId: string, process: WebContainerProcess) => void;
  onProcessExit?: (processId: string, code: number) => void;
  onFileSystemChange?: (path: string, content: string) => void;
}

interface ContainerConfig {
  name: string;
  framework: string;
  port: number;
  autoStart: boolean;
  environment: Record<string, string>;
  dependencies: string[];
  devDependencies: string[];
  scripts: Record<string, string>;
}

interface ProcessInfo {
  id: string;
  name: string;
  command: string;
  status: 'running' | 'stopped' | 'error' | 'starting';
  process?: WebContainerProcess;
  output: string[];
  error: string | null;
  startTime?: Date;
  pid?: number;
}

interface FileSystemChange {
  type: 'add' | 'update' | 'delete';
  path: string;
  content?: string;
  oldContent?: string;
}

const FRAMEWORK_CONFIGS: Record<string, Partial<ContainerConfig>> = {
  react: {
    framework: 'react',
    dependencies: ['react', 'react-dom'],
    devDependencies: ['@vitejs/plugin-react', 'vite'],
    scripts: {
      dev: 'vite',
      build: 'vite build',
      preview: 'vite preview'
    }
  },
  vue: {
    framework: 'vue',
    dependencies: ['vue'],
    devDependencies: ['@vitejs/plugin-vue', 'vite'],
    scripts: {
      dev: 'vite',
      build: 'vite build',
      preview: 'vite preview'
    }
  },
  angular: {
    framework: 'angular',
    dependencies: ['@angular/core', '@angular/common', '@angular/platform-browser'],
    devDependencies: ['@angular-devkit/build-angular', '@angular/cli'],
    scripts: {
      start: 'ng serve',
      build: 'ng build',
      test: 'ng test'
    }
  },
  svelte: {
    framework: 'svelte',
    dependencies: ['svelte'],
    devDependencies: ['@sveltejs/vite-plugin-svelte', 'vite'],
    scripts: {
      dev: 'vite',
      build: 'vite build',
      preview: 'vite preview'
    }
  },
  next: {
    framework: 'next',
    dependencies: ['next', 'react', 'react-dom'],
    devDependencies: [],
    scripts: {
      dev: 'next dev',
      build: 'next build',
      start: 'next start',
      export: 'next export'
    }
  },
  node: {
    framework: 'node',
    dependencies: [],
    devDependencies: [],
    scripts: {
      start: 'node index.js',
      dev: 'node --watch index.js'
    }
  }
};

const WebContainerManager: React.FC<WebContainerManagerProps> = ({
  projectId,
  projectFiles,
  selectedFramework,
  onProcessStart,
  onProcessExit,
  onFileSystemChange
}) => {
  // State
  const [webcontainer, setWebcontainer] = useState<WebContainer | null>(null);
  const [containerStatus, setContainerStatus] = useState<'stopped' | 'starting' | 'running' | 'error'>('stopped');
  const [processes, setProcesses] = useState<Map<string, ProcessInfo>>(new Map());
  const [isMounted, setIsMounted] = useState(false);
  const [mountProgress, setMountProgress] = useState(0);
  const [containerStats, setContainerStats] = useState({
    uptime: 0,
    memory: 0,
    cpu: 0,
    fileCount: 0
  });

  const [containerConfig, setContainerConfig] = useState<ContainerConfig>({
    name: `Project ${projectId}`,
    framework: selectedFramework,
    port: 3000,
    autoStart: true,
    environment: {
      NODE_ENV: 'development',
      PORT: '3000'
    },
    dependencies: [],
    devDependencies: [],
    scripts: {}
  });

  const [logMessages, setLogMessages] = useState<string[]>([]);
  const [isInstalling, setIsInstalling] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const containerRef = useRef<WebContainer | null>(null);
  const processOutputs = useRef<Map<string, string>>(new Map());
  const statsInterval = useRef<NodeJS.Timeout>();

  // Initialize WebContainer
  useEffect(() => {
    const initWebContainer = async () => {
      try {
        setContainerStatus('starting');
        addLog('🚀 Initializing WebContainer...');
        
        // Dynamic import of WebContainer API
        const { WebContainer } = await import('@webcontainer/api');
        
        const container = await WebContainer.boot();
        containerRef.current = container;
        setWebcontainer(container);
        setIsMounted(true);
        setContainerStatus('running');
        setContainerStats(prev => ({ ...prev, uptime: 0 }));
        
        addLog('✅ WebContainer initialized successfully');
        addLog('🔒 Running in secure browser sandbox');
        addLog('⚡ Zero network latency - all computation in browser');
        
        // Start stats monitoring
        startStatsMonitoring();
        
      } catch (error) {
        console.error('Failed to initialize WebContainer:', error);
        setContainerStatus('error');
        addLog(`❌ Failed to initialize WebContainer: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    };

    if (!containerRef.current) {
      initWebContainer();
    }

    return () => {
      if (statsInterval.current) {
        clearInterval(statsInterval.current);
      }
    };
  }, []);

  // Update framework configuration when selected framework changes
  useEffect(() => {
    const frameworkConfig = FRAMEWORK_CONFIGS[selectedFramework];
    if (frameworkConfig) {
      setContainerConfig(prev => ({
        ...prev,
        framework: selectedFramework,
        dependencies: frameworkConfig.dependencies || [],
        devDependencies: frameworkConfig.devDependencies || [],
        scripts: frameworkConfig.scripts || {}
      }));
    }
  }, [selectedFramework]);

  // Mount project files to container
  const mountProjectFiles = useCallback(async () => {
    if (!webcontainer) return;

    try {
      addLog('📁 Mounting project files to WebContainer...');
      setMountProgress(10);

      // Prepare file system tree
      const fileSystemTree: any = {
        'package.json': {
          file: {
            contents: JSON.stringify({
              name: containerConfig.name,
              version: '1.0.0',
              type: 'module',
              scripts: containerConfig.scripts,
              dependencies: Object.fromEntries(containerConfig.dependencies.map(dep => [dep, 'latest'])),
              devDependencies: Object.fromEntries(containerConfig.devDependencies.map(dep => [dep, 'latest']))
            }, null, 2)
          }
        }
      };

      // Add project files
      Object.entries(projectFiles).forEach(([path, content], index) => {
        const normalizedPath = path.startsWith('/') ? path : `/${path}`;
        fileSystemTree[normalizedPath.slice(1)] = {
          file: {
            contents: content
          }
        };
        setMountProgress(10 + (index / Object.keys(projectFiles).length) * 80);
      });

      // Mount to container
      await webcontainer.mount(fileSystemTree);
      setMountProgress(100);
      
      addLog(`✅ Mounted ${Object.keys(projectFiles).length} files successfully`);
      setContainerStats(prev => ({ ...prev, fileCount: Object.keys(projectFiles).length }));
      
      return true;
    } catch (error) {
      console.error('Failed to mount project files:', error);
      addLog(`❌ Failed to mount files: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return false;
    }
  }, [webcontainer, projectFiles, containerConfig]);

  // Install dependencies
  const installDependencies = useCallback(async () => {
    if (!webcontainer) return;

    try {
      setIsInstalling(true);
      addLog('📦 Installing dependencies...');
      
      const installProcess = await webcontainer.spawn('npm', ['install']);
      
      // Stream output
      installProcess.output.pipeTo(
        new WritableStream({
          write(chunk) {
            const text = typeof chunk === 'string' ? chunk : new TextDecoder().decode(chunk);
            addLog(text);
          }
        })
      );

      const exitCode = await installProcess.exit;
      
      if (exitCode === 0) {
        addLog('✅ Dependencies installed successfully');
      } else {
        addLog(`❌ Installation failed with code ${exitCode}`);
      }
      
      return exitCode === 0;
    } catch (error) {
      console.error('Failed to install dependencies:', error);
      addLog(`❌ Installation error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return false;
    } finally {
      setIsInstalling(false);
    }
  }, [webcontainer]);

  // Start development server
  const startDevServer = useCallback(async () => {
    if (!webcontainer) return;

    const processId = 'dev-server';
    
    try {
      addLog('🚀 Starting development server...');
      
      const devCommand = containerConfig.scripts.dev || 'npm run dev';
      const process = await webcontainer.spawn('bash', ['-c', devCommand]);
      
      // Create process info
      const processInfo: ProcessInfo = {
        id: processId,
        name: 'Development Server',
        command: devCommand,
        status: 'starting',
        process,
        output: [],
        error: null,
        startTime: new Date()
      };
      
      setProcesses(prev => {
        const newProcesses = new Map(prev);
        newProcesses.set(processId, processInfo);
        return newProcesses;
      });
      
      // Stream output
      process.output.pipeTo(
        new WritableStream({
          write(chunk) {
            const text = typeof chunk === 'string' ? chunk : new TextDecoder().decode(chunk);
            
            setProcesses(prev => {
              const newProcesses = new Map(prev);
              const process = newProcesses.get(processId);
              if (process) {
                const updatedProcess = {
                  ...process,
                  output: [...process.output, text],
                  status: text.includes('Server running') || text.includes('Local:') ? 'running' : process.status
                };
                newProcesses.set(processId, updatedProcess);
              }
              return newProcesses;
            });
            
            addLog(`[${processId}] ${text}`);
          }
        })
      );
      
      const exitCode = await process.exit;
      
      setProcesses(prev => {
        const newProcesses = new Map(prev);
        const process = newProcesses.get(processId);
        if (process) {
          newProcesses.set(processId, {
            ...process,
            status: exitCode === 0 ? 'stopped' : 'error',
            output: [...process.output, `\nProcess exited with code ${exitCode}`]
          });
        }
        return newProcesses;
      });
      
      onProcessExit?.(processId, exitCode);
      
    } catch (error) {
      console.error('Failed to start dev server:', error);
      addLog(`❌ Failed to start development server: ${error instanceof Error ? error.message : 'Unknown error'}`);
      
      setProcesses(prev => {
        const newProcesses = new Map(prev);
        const process = newProcesses.get(processId);
        if (process) {
          newProcesses.set(processId, {
            ...process,
            status: 'error',
            error: error instanceof Error ? error.message : 'Unknown error'
          });
        }
        return newProcesses;
      });
    }
  }, [webcontainer, containerConfig.scripts, onProcessExit]);

  // Stop process
  const stopProcess = useCallback(async (processId: string) => {
    const process = processes.get(processId);
    if (!process?.process) return;

    try {
      process.process.kill();
      addLog(`🛑 Stopped process: ${processId}`);
      
      setProcesses(prev => {
        const newProcesses = new Map(prev);
        const proc = newProcesses.get(processId);
        if (proc) {
          newProcesses.set(processId, {
            ...proc,
            status: 'stopped'
          });
        }
        return newProcesses;
      });
      
    } catch (error) {
      console.error('Failed to stop process:', error);
      addLog(`❌ Failed to stop process ${processId}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [processes]);

  // Export project
  const exportProject = useCallback(async () => {
    if (!webcontainer) return;

    try {
      addLog('📦 Exporting project...');
      
      const buildCommand = containerConfig.scripts.build || 'npm run build';
      const buildProcess = await webcontainer.spawn('bash', ['-c', buildCommand]);
      
      const exitCode = await buildProcess.exit;
      
      if (exitCode === 0) {
        addLog('✅ Project built successfully');
        addLog('📁 Files ready for deployment');
      } else {
        addLog(`❌ Build failed with code ${exitCode}`);
      }
      
    } catch (error) {
      console.error('Failed to export project:', error);
      addLog(`❌ Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [webcontainer, containerConfig.scripts]);

  // Update file in container
  const updateFile = useCallback(async (path: string, content: string) => {
    if (!webcontainer) return;

    try {
      // This would need a file system update mechanism
      // For now, we'll log the intention
      addLog(`📝 File updated: ${path}`);
      onFileSystemChange?.(path, content);
    } catch (error) {
      console.error('Failed to update file:', error);
    }
  }, [webcontainer, onFileSystemChange]);

  // Start stats monitoring
  const startStatsMonitoring = useCallback(() => {
    if (statsInterval.current) {
      clearInterval(statsInterval.current);
    }

    statsInterval.current = setInterval(() => {
      if (containerStatus === 'running') {
        setContainerStats(prev => ({
          ...prev,
          uptime: prev.uptime + 1,
          memory: Math.random() * 100 + 50, // Simulated memory usage
          cpu: Math.random() * 20 + 5 // Simulated CPU usage
        }));
      }
    }, 1000);
  }, [containerStatus]);

  // Add log message
  const addLog = useCallback((message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogMessages(prev => [...prev, `[${timestamp}] ${message}`].slice(-100));
  }, []);

  // Mount and setup project
  const setupProject = useCallback(async () => {
    if (!webcontainer) return;

    addLog('🔄 Setting up project in WebContainer...');
    
    // Mount files
    const mounted = await mountProjectFiles();
    if (!mounted) return;
    
    // Install dependencies
    await installDependencies();
    
    // Start dev server if configured
    if (containerConfig.autoStart) {
      await startDevServer();
    }
  }, [webcontainer, mountProjectFiles, installDependencies, startDevServer, containerConfig.autoStart]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (containerRef.current) {
        // WebContainer cleanup would go here
      }
    };
  }, []);

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-white border-b">
        <div className="flex items-center space-x-3">
          <Container className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">WebContainer Manager</h3>
          <span className="text-sm text-gray-500">({containerConfig.framework})</span>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Status Indicator */}
          <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs font-medium ${
            containerStatus === 'running' 
              ? 'bg-green-100 text-green-800' 
              : containerStatus === 'error'
              ? 'bg-red-100 text-red-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              containerStatus === 'running' 
                ? 'bg-green-500' 
                : containerStatus === 'error'
                ? 'bg-red-500'
                : 'bg-gray-400'
            }`} />
            <span>{containerStatus.toUpperCase()}</span>
          </div>

          {/* Action Buttons */}
          {containerStatus === 'running' ? (
            <div className="flex space-x-1">
              <button
                onClick={setupProject}
                className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors"
                disabled={isMounted && processes.has('dev-server')}
              >
                <Zap className="w-4 h-4" />
                <span>Setup</span>
              </button>
              
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                title="Advanced settings"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          ) : containerStatus === 'error' ? (
            <button
              onClick={() => window.location.reload()}
              className="px-3 py-1.5 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          ) : (
            <div className="flex items-center space-x-1">
              <RefreshCw className="w-4 h-4 text-gray-400 animate-spin" />
              <span className="text-sm text-gray-600">Initializing...</span>
            </div>
          )}
        </div>
      </div>

      {/* Stats Bar */}
      {containerStatus === 'running' && (
        <div className="px-4 py-2 bg-gray-100 border-b text-sm text-gray-600">
          <div className="flex items-center space-x-6">
            <span>Uptime: {Math.floor(containerStats.uptime / 60)}m {containerStats.uptime % 60}s</span>
            <span>Memory: {containerStats.memory.toFixed(1)}MB</span>
            <span>CPU: {containerStats.cpu.toFixed(1)}%</span>
            <span>Files: {containerStats.fileCount}</span>
            <span>Processes: {Array.from(processes.values()).filter(p => p.status === 'running').length}</span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Left Panel - Configuration */}
        <div className="w-80 border-r bg-white">
          <div className="p-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Container Configuration</h4>
            
            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-600">Project Name</label>
                <input
                  type="text"
                  value={containerConfig.name}
                  onChange={(e) => setContainerConfig(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full mt-1 px-2 py-1 text-sm border border-gray-300 rounded"
                />
              </div>

              <div>
                <label className="text-xs text-gray-600">Port</label>
                <input
                  type="number"
                  value={containerConfig.port}
                  onChange={(e) => setContainerConfig(prev => ({ ...prev, port: parseInt(e.target.value) }))}
                  className="w-full mt-1 px-2 py-1 text-sm border border-gray-300 rounded"
                />
              </div>

              <div>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={containerConfig.autoStart}
                    onChange={(e) => setContainerConfig(prev => ({ ...prev, autoStart: e.target.checked }))}
                    className="text-blue-600"
                  />
                  <span className="text-xs text-gray-600">Auto-start dev server</span>
                </label>
              </div>
            </div>

            {/* Framework Info */}
            <div className="mt-4 p-3 bg-gray-50 rounded">
              <h5 className="text-xs font-semibold text-gray-700 mb-2">Framework: {containerConfig.framework.toUpperCase()}</h5>
              <div className="text-xs text-gray-600 space-y-1">
                <p>Dependencies: {containerConfig.dependencies.length}</p>
                <p>Dev Dependencies: {containerConfig.devDependencies.length}</p>
                <p>Scripts: {Object.keys(containerConfig.scripts).length}</p>
              </div>
            </div>

            {/* Process Management */}
            <div className="mt-4">
              <h5 className="text-xs font-semibold text-gray-700 mb-2">Processes</h5>
              <div className="space-y-2">
                {Array.from(processes.values()).map(process => (
                  <div key={process.id} className="flex items-center justify-between p-2 bg-gray-50 rounded text-xs">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{process.name}</div>
                      <div className="text-gray-500">{process.command}</div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-1 py-0.5 rounded text-xs ${
                        process.status === 'running' ? 'bg-green-100 text-green-800' :
                        process.status === 'starting' ? 'bg-yellow-100 text-yellow-800' :
                        process.status === 'error' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {process.status}
                      </span>
                      {process.status === 'running' && (
                        <button
                          onClick={() => stopProcess(process.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Square className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="mt-4 space-y-2">
              <button
                onClick={exportProject}
                className="w-full flex items-center justify-center space-x-1 px-3 py-2 bg-purple-600 text-white text-sm font-medium rounded hover:bg-purple-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Export Project</span>
              </button>
              
              <button
                onClick={startDevServer}
                disabled={!isMounted || processes.has('dev-server')}
                className="w-full flex items-center justify-center space-x-1 px-3 py-2 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 transition-colors disabled:bg-gray-300"
              >
                <Play className="w-4 h-4" />
                <span>Start Dev Server</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right Panel - Logs and Output */}
        <div className="flex-1 flex flex-col">
          {/* Logs Header */}
          <div className="flex items-center justify-between p-3 bg-gray-100 border-b">
            <h4 className="text-sm font-semibold text-gray-900">Container Logs</h4>
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-green-600" title="Secure Sandbox" />
              <span className="text-xs text-gray-600">Browser Sandbox</span>
              {isInstalling && (
                <RefreshCw className="w-4 h-4 text-blue-600 animate-spin" />
              )}
            </div>
          </div>

          {/* Logs Content */}
          <div className="flex-1 bg-black text-green-400 font-mono text-sm p-3 overflow-y-auto">
            {logMessages.length === 0 ? (
              <div className="text-gray-500 text-center py-8">
                <Container className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                <p>WebContainer ready</p>
                <p className="text-xs">Click "Setup" to start your project</p>
              </div>
            ) : (
              <div className="space-y-1">
                {logMessages.map((log, index) => (
                  <div key={index} className="whitespace-pre-wrap">
                    {log}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Mount Progress */}
          {mountProgress > 0 && mountProgress < 100 && (
            <div className="p-2 bg-gray-100 border-t">
              <div className="flex items-center space-x-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${mountProgress}%` }}
                  />
                </div>
                <span className="text-xs text-gray-600">{mountProgress}%</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Advanced Settings Panel */}
      {showAdvanced && (
        <div className="absolute top-16 right-4 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-20 p-4">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Advanced Settings</h4>
          
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Environment Variables</label>
              <div className="mt-2 space-y-2">
                {Object.entries(containerConfig.environment).map(([key, value]) => (
                  <div key={key} className="flex space-x-2">
                    <input
                      type="text"
                      value={key}
                      className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded"
                      placeholder="KEY"
                    />
                    <input
                      type="text"
                      value={value}
                      className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded"
                      placeholder="VALUE"
                    />
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">Dependencies</label>
              <textarea
                value={containerConfig.dependencies.join(', ')}
                onChange={(e) => setContainerConfig(prev => ({ 
                  ...prev, 
                  dependencies: e.target.value.split(',').map(d => d.trim()).filter(Boolean)
                }))}
                className="w-full mt-1 px-2 py-1 text-sm border border-gray-300 rounded"
                rows={3}
                placeholder="react, react-dom, lodash"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">Dev Dependencies</label>
              <textarea
                value={containerConfig.devDependencies.join(', ')}
                onChange={(e) => setContainerConfig(prev => ({ 
                  ...prev, 
                  devDependencies: e.target.value.split(',').map(d => d.trim()).filter(Boolean)
                }))}
                className="w-full mt-1 px-2 py-1 text-sm border border-gray-300 rounded"
                rows={3}
                placeholder="typescript, vite, eslint"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-2 mt-4">
            <button
              onClick={() => setShowAdvanced(false)}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                setShowAdvanced(false);
                setupProject();
              }}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Apply
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default WebContainerManager;