import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Terminal, Plus, X, Minimize2, Maximize2, Zap, Settings } from 'lucide-react';
import { Terminal as XTerm } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import { WebGLAddon } from '@xterm/addon-webgl';

// Types
interface MultiTerminalManagerProps {
  projectId: string;
  onCommand?: (terminalId: string, command: string) => void;
  onTerminalOutput?: (terminalId: string, output: string) => void;
  isProjectRunning?: boolean;
}

interface TerminalConfig {
  id: string;
  name: string;
  type: 'main' | 'build' | 'test' | 'debug' | 'logs' | 'custom';
  cwd?: string;
  env?: Record<string, string>;
  autoStart?: boolean;
  fontSize?: number;
  theme?: 'dark' | 'light' | 'green' | 'blue';
  maxLines?: number;
}

interface TerminalInstance {
  config: TerminalConfig;
  terminal: XTerm | null;
  fitAddon: FitAddon | null;
  webglAddon: WebGLAddon | null;
  isVisible: boolean;
  isMaximized: boolean;
  isConnected: boolean;
  output: string[];
  error: string | null;
}

const DEFAULT_TERMINAL_CONFIGS: TerminalConfig[] = [
  {
    id: 'main',
    name: 'Main Terminal',
    type: 'main',
    cwd: '/workspace',
    autoStart: true,
    fontSize: 14,
    theme: 'dark'
  },
  {
    id: 'build',
    name: 'Build Terminal',
    type: 'build',
    cwd: '/workspace',
    autoStart: false,
    fontSize: 12,
    theme: 'dark'
  },
  {
    id: 'test',
    name: 'Test Terminal',
    type: 'test',
    cwd: '/workspace',
    autoStart: false,
    fontSize: 12,
    theme: 'dark'
  },
  {
    id: 'debug',
    name: 'Debug Terminal',
    type: 'debug',
    cwd: '/workspace',
    autoStart: false,
    fontSize: 12,
    theme: 'dark'
  },
  {
    id: 'logs',
    name: 'Logs Terminal',
    type: 'logs',
    cwd: '/workspace',
    autoStart: false,
    fontSize: 11,
    theme: 'dark'
  }
];

const THEME_COLORS = {
  dark: {
    background: '#1a1a1a',
    foreground: '#ffffff',
    cursor: '#ffffff',
    selection: '#3a3a3a'
  },
  light: {
    background: '#ffffff',
    foreground: '#000000',
    cursor: '#000000',
    selection: '#e0e0e0'
  },
  green: {
    background: '#0a0a0a',
    foreground: '#00ff00',
    cursor: '#00ff00',
    selection: '#1a3a1a'
  },
  blue: {
    background: '#0a0a1a',
    foreground: '#00aaff',
    cursor: '#00aaff',
    selection: '#1a2a3a'
  }
};

const MultiTerminalManager: React.FC<MultiTerminalManagerProps> = ({
  projectId,
  onCommand,
  onTerminalOutput,
  isProjectRunning = false
}) => {
  // State
  const [terminals, setTerminals] = useState<Map<string, TerminalInstance>>(new Map());
  const [activeTerminalId, setActiveTerminalId] = useState<string>('main');
  const [showConfig, setShowConfig] = useState(false);
  const [newTerminalName, setNewTerminalName] = useState('');
  const [newTerminalType, setNewTerminalType] = useState<TerminalConfig['type']>('custom');
  const [globalSettings, setGlobalSettings] = useState({
    enableWebGL: true,
    fontSize: 14,
    fontFamily: 'Monaco, Menlo, monospace',
    cursorBlink: true,
    scrollback: 1000
  });

  const containerRefs = useRef<Map<string, HTMLDivElement>>(new Map());
  const wsConnections = useRef<Map<string, WebSocket>>(new Map());

  // Initialize default terminals
  useEffect(() => {
    const initialTerminals = new Map<string, TerminalInstance>();
    
    DEFAULT_TERMINAL_CONFIGS.forEach(config => {
      initialTerminals.set(config.id, {
        config,
        terminal: null,
        fitAddon: null,
        webglAddon: null,
        isVisible: config.id === 'main',
        isMaximized: false,
        isConnected: false,
        output: [],
        error: null
      });
    });

    setTerminals(initialTerminals);
  }, []);

  // Initialize terminals when they become visible
  useEffect(() => {
    terminals.forEach((terminalInstance, id) => {
      if (terminalInstance.isVisible && !terminalInstance.terminal) {
        initializeTerminal(id, terminalInstance.config);
      }
    });
  }, [terminals]);

  // Initialize terminal
  const initializeTerminal = useCallback(async (terminalId: string, config: TerminalConfig) => {
    const container = containerRefs.current.get(terminalId);
    if (!container) return;

    try {
      // Create terminal instance
      const terminal = new XTerm({
        fontSize: config.fontSize || globalSettings.fontSize,
        fontFamily: globalSettings.fontFamily,
        cursorBlink: globalSettings.cursorBlink,
        scrollback: globalSettings.scrollback,
        theme: THEME_COLORS[config.theme || 'dark'],
        convertEol: true,
        cursorStyle: 'block'
      });

      // Addons
      const fitAddon = new FitAddon();
      const webglAddon = globalSettings.enableWebGL ? new WebGLAddon() : null;
      
      terminal.loadAddon(fitAddon);
      if (webglAddon) {
        terminal.loadAddon(webglAddon);
      }
      terminal.loadAddon(new WebLinksAddon());

      // Open terminal
      terminal.open(container);

      // Fit to container
      setTimeout(() => fitAddon.fit(), 100);

      // Add welcome message
      terminal.writeln(`\x1b[36m╔══════════════════════════════════════════════════════════════╗\x1b[0m`);
      terminal.writeln(`\x1b[36m║                    IRIS Agent Terminal                      ║\x1b[0m`);
      terminal.writeln(`\x1b[36m║                  Multi-Terminal Manager                       ║\x1b[0m`);
      terminal.writeln(`\x1b[36m╚══════════════════════════════════════════════════════════════╝\x1b[0m`);
      terminal.writeln(`\x1b[32m✓ Terminal: ${config.name} (${config.type})\x1b[0m`);
      terminal.writeln(`\x1b[33m📁 Working Directory: ${config.cwd || '/workspace'}\x1b[0m`);
      terminal.writeln(`\x1b[35m🚀 Project ID: ${projectId}\x1b[0m`);
      terminal.writeln('');
      
      if (config.type === 'main') {
        terminal.writeln(`\x1b[32mReady for commands. Type 'help' for available commands.\x1b[0m`);
      } else if (config.type === 'build') {
        terminal.writeln(`\x1b[32mBuild terminal ready. Use for compilation and bundling tasks.\x1b[0m`);
      } else if (config.type === 'test') {
        terminal.writeln(`\x1b[32mTest terminal ready. Run test suites and debugging.\x1b[0m`);
      } else if (config.type === 'debug') {
        terminal.writeln(`\x1b[32mDebug terminal ready. Run debugging tools and inspectors.\x1b[0m`);
      } else if (config.type === 'logs') {
        terminal.writeln(`\x1b[32mLogs terminal ready. Monitor application logs in real-time.\x1b[0m`);
      }
      
      terminal.writeln('');
      terminal.write(`\x1b[33m${config.name}>\x1b[0m `);

      // Handle user input
      let currentLine = '';
      terminal.onData((data) => {
        const code = data.charCodeAt(0);

        if (code === 13) { // Enter
          terminal.write('\r\n');
          handleCommand(terminalId, currentLine.trim());
          currentLine = '';
          terminal.write(`\x1b[33m${config.name}>\x1b[0m `);
        } else if (code === 127) { // Backspace
          if (currentLine.length > 0) {
            currentLine = currentLine.slice(0, -1);
            terminal.write('\b \b');
          }
        } else if (code >= 32) { // Printable characters
          currentLine += data;
          terminal.write(data);
        }
      });

      // Handle resize
      const handleResize = () => {
        fitAddon.fit();
      };
      window.addEventListener('resize', handleResize);

      // Update terminal instance
      setTerminals(prev => {
        const newTerminals = new Map(prev);
        const instance = newTerminals.get(terminalId);
        if (instance) {
          newTerminals.set(terminalId, {
            ...instance,
            terminal,
            fitAddon,
            webglAddon,
            isConnected: true
          });
        }
        return newTerminals;
      });

      // Connect WebSocket for real-time communication
      if (onCommand) {
        connectWebSocket(terminalId, terminal, config);
      }

      return () => {
        window.removeEventListener('resize', handleResize);
        terminal.dispose();
      };

    } catch (error) {
      console.error(`Failed to initialize terminal ${terminalId}:`, error);
      setTerminals(prev => {
        const newTerminals = new Map(prev);
        const instance = newTerminals.get(terminalId);
        if (instance) {
          newTerminals.set(terminalId, {
            ...instance,
            error: error instanceof Error ? error.message : 'Unknown error'
          });
        }
        return newTerminals;
      });
    }
  }, [globalSettings, projectId, onCommand]);

  // Connect WebSocket for real-time terminal communication
  const connectWebSocket = useCallback((terminalId: string, terminal: XTerm, config: TerminalConfig) => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/v1/terminals/${projectId}/${terminalId}`;
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        terminal.writeln('\x1b[32m✓ Connected to terminal service\x1b[0m');
        terminal.writeln('');
        terminal.write(`\x1b[33m${config.name}>\x1b[0m `);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          terminal.write(message.output);
          
          // Store output for logging
          setTerminals(prev => {
            const newTerminals = new Map(prev);
            const instance = newTerminals.get(terminalId);
            if (instance) {
              const maxLines = instance.config.maxLines || 1000;
              const newOutput = [...instance.output, message.output].slice(-maxLines);
              newTerminals.set(terminalId, {
                ...instance,
                output: newOutput
              });
            }
            return newTerminals;
          });

          // Notify parent component
          onTerminalOutput?.(terminalId, message.output);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        terminal.writeln('\x1b[31m✗ WebSocket connection error\x1b[0m');
        terminal.writeln('');
      };

      ws.onclose = () => {
        terminal.writeln('\x1b[33m⚠ Terminal service disconnected\x1b[0m');
        terminal.writeln('');
        terminal.write(`\x1b[33m${config.name}>\x1b[0m `);
      };

      wsConnections.current.set(terminalId, ws);
    } catch (error) {
      console.error(`Failed to connect WebSocket for terminal ${terminalId}:`, error);
    }
  }, [projectId, onTerminalOutput]);

  // Handle terminal commands
  const handleCommand = useCallback((terminalId: string, command: string) => {
    if (!command) return;

    const terminal = terminals.get(terminalId);
    if (!terminal || !terminal.terminal) return;

    // Log command
    onCommand?.(terminalId, command);

    // Handle built-in commands
    if (command === 'help') {
      terminal.terminal.writeln('\x1b[36m=== Available Commands ===\x1b[0m');
      terminal.terminal.writeln('\x1b[32mhelp\x1b[0m         - Show this help');
      terminal.terminal.writeln('\x1b[32mclear\x1b[0m        - Clear terminal');
      terminal.terminal.writeln('\x1b[32mstatus\x1b[0m       - Show terminal status');
      terminal.terminal.writeln('\x1b[32mpwd\x1b[0m          - Print working directory');
      terminal.terminal.writeln('\x1b[32mproject\x1b[0m      - Show project info');
      terminal.terminal.writeln('\x1b[32mlogs\x1b[0m         - Show recent logs');
      terminal.terminal.writeln('\x1b[32mbreak\x1b[0m        - Break running process');
      terminal.terminal.writeln('');
      terminal.terminal.write(`\x1b[33m${terminal.config.name}>\x1b[0m `);
      return;
    }

    if (command === 'clear') {
      terminal.terminal.clear();
      terminal.terminal.write(`\x1b[33m${terminal.config.name}>\x1b[0m `);
      return;
    }

    if (command === 'status') {
      terminal.terminal.writeln('\x1b[36m=== Terminal Status ===\x1b[0m');
      terminal.terminal.writeln(`\x1b[32mID:\x1b[0m ${terminalId}`);
      terminal.terminal.writeln(`\x1b[32mName:\x1b[0m ${terminal.config.name}`);
      terminal.terminal.writeln(`\x1b[32mType:\x1b[0m ${terminal.config.type}`);
      terminal.terminal.writeln(`\x1b[32mConnected:\x1b[0m ${terminal.isConnected ? 'Yes' : 'No'}`);
      terminal.terminal.writeln(`\x1b[32mVisible:\x1b[0m ${terminal.isVisible ? 'Yes' : 'No'}`);
      terminal.terminal.writeln(`\x1b[32mCWD:\x1b[0m ${terminal.config.cwd || '/workspace'}`);
      terminal.terminal.writeln(`\x1b[32mProject:\x1b[0m ${projectId}`);
      terminal.terminal.writeln(`\x1b[32mRunning:\x1b[0m ${isProjectRunning ? 'Yes' : 'No'}`);
      terminal.terminal.writeln('');
      terminal.terminal.write(`\x1b[33m${terminal.config.name}>\x1b[0m `);
      return;
    }

    if (command === 'pwd') {
      terminal.terminal.writeln(`\x1b[32m${terminal.config.cwd || '/workspace'}\x1b[0m`);
      terminal.terminal.writeln('');
      terminal.terminal.write(`\x1b[33m${terminal.config.name}>\x1b[0m `);
      return;
    }

    if (command === 'project') {
      terminal.terminal.writeln('\x1b[36m=== Project Information ===\x1b[0m');
      terminal.terminal.writeln(`\x1b[32mProject ID:\x1b[0m ${projectId}`);
      terminal.terminal.writeln(`\x1b[32mActive:\x1b[0m ${isProjectRunning ? 'Yes' : 'No'}`);
      terminal.terminal.writeln(`\x1b[32mTerminals:\x1b[0m ${terminals.size}`);
      terminal.terminal.writeln('');
      terminal.terminal.write(`\x1b[33m${terminal.config.name}>\x1b[0m `);
      return;
    }

    if (command === 'break') {
      // Send break signal to WebSocket
      const ws = wsConnections.current.get(terminalId);
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'break' }));
        terminal.terminal.writeln('\x1b[33m⚠ Break signal sent\x1b[0m');
      } else {
        terminal.terminal.writeln('\x1b[31m✗ No active process to break\x1b[0m');
      }
      terminal.terminal.writeln('');
      terminal.terminal.write(`\x1b[33m${terminal.config.name}>\x1b[0m `);
      return;
    }

    // For other commands, send to backend
    const ws = wsConnections.current.get(terminalId);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'command', command }));
    } else {
      terminal.terminal.writeln('\x1b[31m✗ Not connected to terminal service\x1b[0m');
      terminal.terminal.writeln('');
      terminal.terminal.write(`\x1b[33m${terminal.config.name}>\x1b[0m `);
    }
  }, [terminals, projectId, isProjectRunning, onCommand]);

  // Show/hide terminal
  const toggleTerminal = useCallback((terminalId: string) => {
    setTerminals(prev => {
      const newTerminals = new Map(prev);
      const instance = newTerminals.get(terminalId);
      if (instance) {
        newTerminals.set(terminalId, {
          ...instance,
          isVisible: !instance.isVisible
        });
      }
      return newTerminals;
    });
  }, []);

  // Maximize/minimize terminal
  const toggleMaximize = useCallback((terminalId: string) => {
    setTerminals(prev => {
      const newTerminals = new Map(prev);
      const instance = newTerminals.get(terminalId);
      if (instance) {
        newTerminals.set(terminalId, {
          ...instance,
          isMaximized: !instance.isMaximized
        });
      }
      return newTerminals;
    });
  }, []);

  // Add new terminal
  const addTerminal = useCallback(() => {
    if (!newTerminalName.trim()) return;

    const terminalId = `custom_${Date.now()}`;
    const config: TerminalConfig = {
      id: terminalId,
      name: newTerminalName,
      type: newTerminalType,
      cwd: '/workspace',
      autoStart: true,
      fontSize: 14,
      theme: 'dark'
    };

    setTerminals(prev => {
      const newTerminals = new Map(prev);
      newTerminals.set(terminalId, {
        config,
        terminal: null,
        fitAddon: null,
        webglAddon: null,
        isVisible: true,
        isMaximized: false,
        isConnected: false,
        output: [],
        error: null
      });
      return newTerminals;
    });

    setNewTerminalName('');
    setNewTerminalType('custom');
  }, [newTerminalName, newTerminalType]);

  // Close terminal
  const closeTerminal = useCallback((terminalId: string) => {
    if (terminalId === 'main') return; // Don't close main terminal

    setTerminals(prev => {
      const newTerminals = new Map(prev);
      const ws = wsConnections.current.get(terminalId);
      if (ws) {
        ws.close();
        wsConnections.current.delete(terminalId);
      }
      newTerminals.delete(terminalId);
      return newTerminals;
    });

    if (activeTerminalId === terminalId) {
      setActiveTerminalId('main');
    }
  }, [activeTerminalId]);

  // Cleanup
  useEffect(() => {
    return () => {
      wsConnections.current.forEach(ws => ws.close());
      wsConnections.current.clear();
    };
  }, []);

  const terminalTypes = [
    { value: 'main', label: 'Main Terminal', description: 'Primary development terminal' },
    { value: 'build', label: 'Build Terminal', description: 'For compilation and bundling' },
    { value: 'test', label: 'Test Terminal', description: 'For running tests and debugging' },
    { value: 'debug', label: 'Debug Terminal', description: 'For debugging tools' },
    { value: 'logs', label: 'Logs Terminal', description: 'For monitoring logs' },
    { value: 'custom', label: 'Custom Terminal', description: 'Custom configuration' }
  ];

  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between p-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <Terminal className="w-5 h-5 text-blue-400" />
          <h3 className="text-white font-semibold">Multi-Terminal Manager</h3>
          <span className="text-sm text-gray-400">({terminals.size} terminals)</span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          <div className="flex items-center space-x-1">
            <input
              type="text"
              value={newTerminalName}
              onChange={(e) => setNewTerminalName(e.target.value)}
              placeholder="Terminal name"
              className="w-32 px-2 py-1 text-sm bg-gray-700 text-white border border-gray-600 rounded"
              onKeyPress={(e) => e.key === 'Enter' && addTerminal()}
            />
            <select
              value={newTerminalType}
              onChange={(e) => setNewTerminalType(e.target.value as TerminalConfig['type'])}
              className="px-2 py-1 text-sm bg-gray-700 text-white border border-gray-600 rounded"
            >
              {terminalTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
            <button
              onClick={addTerminal}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
              title="Add terminal"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Terminal Tabs */}
      <div className="flex items-center bg-gray-800 border-b border-gray-700 overflow-x-auto">
        {Array.from(terminals.entries()).map(([id, terminal]) => (
          <div
            key={id}
            className={`flex items-center px-3 py-2 border-r border-gray-700 cursor-pointer hover:bg-gray-700 transition-colors ${
              id === activeTerminalId ? 'bg-gray-700' : ''
            }`}
            onClick={() => setActiveTerminalId(id)}
          >
            <div className={`w-2 h-2 rounded-full mr-2 ${
              terminal.isConnected ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-sm text-white font-medium">{terminal.config.name}</span>
            {id !== 'main' && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  closeTerminal(id);
                }}
                className="ml-2 p-1 text-gray-400 hover:text-red-400 rounded"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Terminal Content */}
      <div className="flex-1 relative">
        {Array.from(terminals.entries()).map(([id, terminal]) => {
          if (id !== activeTerminalId) return null;
          
          return (
            <div
              key={id}
              className={`absolute inset-0 ${terminal.isMaximized ? 'z-10' : 'z-0'}`}
            >
              {/* Terminal Controls */}
              <div className="flex items-center justify-between p-2 bg-gray-800 border-b border-gray-700">
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-white font-medium">{terminal.config.name}</span>
                  <span className="text-xs text-gray-400">({terminal.config.type})</span>
                  <span className="text-xs text-gray-400">{terminal.config.cwd || '/workspace'}</span>
                </div>

                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => toggleTerminal(id)}
                    className="p-1 text-gray-400 hover:text-white rounded"
                    title={terminal.isVisible ? 'Hide' : 'Show'}
                  >
                    <Minimize2 className="w-3 h-3" />
                  </button>
                  
                  <button
                    onClick={() => toggleMaximize(id)}
                    className="p-1 text-gray-400 hover:text-white rounded"
                    title="Maximize"
                  >
                    <Maximize2 className="w-3 h-3" />
                  </button>

                  {terminal.error && (
                    <span className="text-xs text-red-400" title={terminal.error}>
                      Error
                    </span>
                  )}
                </div>
              </div>

              {/* Terminal Container */}
              <div
                ref={(el) => {
                  if (el) containerRefs.current.set(id, el);
                }}
                className="w-full h-full bg-gray-900"
                style={{ height: terminal.isMaximized ? 'calc(100vh - 80px)' : 'calc(100% - 40px)' }}
              />
            </div>
          );
        })}
      </div>

      {/* Configuration Panel */}
      {showConfig && (
        <div className="absolute top-16 right-4 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-20">
          <div className="p-4">
            <h4 className="text-white font-medium mb-3">Global Settings</h4>
            
            <div className="space-y-3">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={globalSettings.enableWebGL}
                  onChange={(e) => setGlobalSettings(prev => ({ ...prev, enableWebGL: e.target.checked }))}
                  className="text-blue-600"
                />
                <span className="text-sm text-white">Enable WebGL</span>
              </label>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={globalSettings.cursorBlink}
                  onChange={(e) => setGlobalSettings(prev => ({ ...prev, cursorBlink: e.target.checked }))}
                  className="text-blue-600"
                />
                <span className="text-sm text-white">Cursor Blink</span>
              </label>

              <div>
                <label className="text-sm text-white">Font Size</label>
                <input
                  type="number"
                  value={globalSettings.fontSize}
                  onChange={(e) => setGlobalSettings(prev => ({ ...prev, fontSize: parseInt(e.target.value) }))}
                  className="w-full mt-1 px-2 py-1 bg-gray-700 text-white border border-gray-600 rounded text-sm"
                  min="10"
                  max="24"
                />
              </div>

              <div>
                <label className="text-sm text-white">Scrollback Lines</label>
                <input
                  type="number"
                  value={globalSettings.scrollback}
                  onChange={(e) => setGlobalSettings(prev => ({ ...prev, scrollback: parseInt(e.target.value) }))}
                  className="w-full mt-1 px-2 py-1 bg-gray-700 text-white border border-gray-600 rounded text-sm"
                  min="100"
                  max="10000"
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiTerminalManager;