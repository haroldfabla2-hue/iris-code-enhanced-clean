import React, { useRef, useEffect, useState } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import { useEditorStore } from '../../stores/editorStore';
import { 
  X, 
  Plus, 
  FolderOpen, 
  File, 
  Terminal, 
  Settings,
  Save,
  Download,
  Upload,
  Play,
  Square,
  MoreVertical,
  ChevronDown,
  Folder,
  FolderOpen as FolderOpenIcon,
  Code
} from 'lucide-react';
import { cn } from '../../lib/utils';

const CodeEditor: React.FC = () => {
  const {
    openFiles,
    activeFileId,
    terminalSessions,
    activeTerminalId,
    unsavedFiles,
    lspStatus,
    lspErrors,
    lspWarnings,
    fontSize,
    tabSize,
    wordWrap,
    minimap,
    theme,
    showWhitespace,
    showLineNumbers,
    highlightActiveLine,
    aiSuggestions,
    inlineCompletions,
    setActiveFile,
    openFile,
    closeFile,
    updateFileContent,
    saveFile,
    saveAllFiles,
    createTerminalSession,
    setActiveTerminal,
    addTerminalOutput,
    clearTerminal,
    getActiveFile,
    getActiveTerminal,
    hasUnsavedChanges,
    createNewFile,
  } = useEditorStore();

  const editorRef = useRef<any>(null);
  const [terminalInput, setTerminalInput] = useState('');
  const [terminalActive, setTerminalActive] = useState(false);
  const [fileExplorerCollapsed, setFileExplorerCollapsed] = useState(false);
  const [terminalCollapsed, setTerminalCollapsed] = useState(false);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    
    // Configure editor options
    editor.updateOptions({
      fontSize,
      tabSize,
      wordWrap: wordWrap ? 'on' : 'off',
      minimap: { enabled: minimap },
      // showWhitespace, // Removed as it's not a valid Monaco option
      lineNumbers: showLineNumbers ? 'on' : 'off',
      // highlightActiveLine, // Replaced with renderLineHighlight
      theme: theme === 'vs-dark' ? 'vs-dark' : theme,
      fontFamily: 'JetBrains Mono, Consolas, monospace',
      fontLigatures: true,
      scrollBeyondLastLine: false,
      automaticLayout: true,
      renderWhitespace: 'selection',
      renderControlCharacters: true,
      roundedSelection: false,
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: 'on',
      contextmenu: true,
      mouseWheelZoom: true,
    });

    // Register AI completion provider (mock implementation)
    if (aiSuggestions) {
      monaco.languages.registerCompletionItemProvider('typescript', {
        provideCompletionItems: (model, position) => {
          const word = model.getWordUntilPosition(position);
          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn,
          };

          const suggestions = [
            {
              label: 'console.log',
              kind: monaco.languages.CompletionItemKind.Function,
              insertText: 'console.log(${1:message})',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              range: range,
              detail: 'AI Suggestion: Log to console',
              command: { id: 'editor.action.triggerSuggest', title: 'Trigger Suggest' }
            },
            {
              label: 'useState',
              kind: monaco.languages.CompletionItemKind.Function,
              insertText: 'useState(${1:initialValue})',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              range: range,
              detail: 'AI Suggestion: React useState hook',
            },
          ];

          return { suggestions };
        }
      });
    }
  };

  const handleFileChange = (value: string | undefined) => {
    if (activeFileId && value !== undefined) {
      updateFileContent(activeFileId, value);
    }
  };

  const FileTab: React.FC<{
    file: any;
    isActive: boolean;
    onClose: () => void;
  }> = ({ file, isActive, onClose }) => (
    <div
      className={cn(
        "flex items-center px-4 py-2 border-r border-border cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors group",
        isActive ? "bg-background border-b-2 border-brand-500" : "bg-neutral-50 dark:bg-neutral-900"
      )}
      onClick={() => setActiveFile(file.id)}
    >
      <span className="text-sm font-medium truncate flex-1">
        {file.name}
      </span>
      {unsavedFiles.has(file.id) && (
        <div className="w-2 h-2 bg-orange-500 rounded-full mx-2 flex-shrink-0" />
      )}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onClose();
        }}
        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-all"
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  );

  const FileExplorer: React.FC = () => {
    const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['src']));
    
    const toggleFolder = (folderId: string) => {
      setExpandedFolders(prev => {
        const newSet = new Set(prev);
        if (newSet.has(folderId)) {
          newSet.delete(folderId);
        } else {
          newSet.add(folderId);
        }
        return newSet;
      });
    };

    const mockFileTree = [
      {
        id: 'src',
        name: 'src',
        type: 'folder',
        path: '/src',
        children: [
          {
            id: 'components',
            name: 'components',
            type: 'folder' as const,
            path: '/src/components',
            children: [
              { id: 'dashboard', name: 'Dashboard.tsx', type: 'file' as const, path: '/src/components/Dashboard.tsx' },
              { id: 'chat', name: 'Chat.tsx', type: 'file' as const, path: '/src/components/Chat.tsx' },
              { id: 'editor', name: 'Editor.tsx', type: 'file' as const, path: '/src/components/Editor.tsx' },
            ]
          },
          { id: 'stores', name: 'stores', type: 'folder' as const, path: '/src/stores', children: [] },
          { id: 'types', name: 'types', type: 'folder' as const, path: '/src/types', children: [] },
          { id: 'App.tsx', name: 'App.tsx', type: 'file' as const, path: '/src/App.tsx' },
          { id: 'index.css', name: 'index.css', type: 'file' as const, path: '/src/index.css' },
        ]
      },
      { id: 'public', name: 'public', type: 'folder' as const, path: '/public', children: [] },
      { id: 'package.json', name: 'package.json', type: 'file' as const, path: '/package.json' },
      { id: 'README.md', name: 'README.md', type: 'file' as const, path: '/README.md' },
    ];

    const FileTreeNode: React.FC<{
      node: any;
      depth: number;
    }> = ({ node, depth }) => {
      const isExpanded = expandedFolders.has(node.id);
      const isFolder = node.type === 'folder';
      const Icon = isFolder ? (isExpanded ? FolderOpenIcon : Folder) : File;
      
      return (
        <div>
          <div
            className="flex items-center px-2 py-1.5 hover:bg-neutral-100 dark:hover:bg-neutral-800 cursor-pointer group"
            style={{ paddingLeft: `${depth * 16 + 8}px` }}
            onClick={() => {
              if (isFolder) {
                toggleFolder(node.id);
              } else {
                const existingFile = openFiles.find(f => f.path === node.path);
                if (existingFile) {
                  setActiveFile(existingFile.id);
                } else {
                  const fileId = createNewFile(
                    node.name,
                    getMockFileContent(node.name),
                    getLanguageFromExtension(node.name)
                  );
                  setActiveFile(fileId);
                }
              }
            }}
          >
            <Icon className="w-4 h-4 mr-2 text-neutral-500" />
            <span className="text-sm truncate">{node.name}</span>
          </div>
          
          {isFolder && isExpanded && node.children && (
            <div>
              {node.children.map((child: any) => (
                <FileTreeNode key={child.id} node={child} depth={depth + 1} />
              ))}
            </div>
          )}
        </div>
      );
    };

    return (
      <div className="w-64 border-r border-border bg-background flex flex-col">
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-sm">Explorador</h3>
            <button
              onClick={() => setFileExplorerCollapsed(!fileExplorerCollapsed)}
              className="p-1 rounded hover:bg-neutral-100 dark:hover:bg-neutral-800"
            >
              <ChevronDown className={cn(
                "w-4 h-4 transition-transform",
                fileExplorerCollapsed && "rotate-180"
              )} />
            </button>
          </div>
          
          <div className="flex space-x-1">
            <button className="p-1.5 rounded hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Nuevo archivo">
              <File className="w-4 h-4" />
            </button>
            <button className="p-1.5 rounded hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Nueva carpeta">
              <FolderOpen className="w-4 h-4" />
            </button>
            <button className="p-1.5 rounded hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Subir archivo">
              <Upload className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {mockFileTree.map(node => (
            <FileTreeNode key={node.id} node={node} depth={0} />
          ))}
        </div>
      </div>
    );
  };

  const TerminalPanel: React.FC = () => {
    const activeTerminal = getActiveTerminal();
    
    const handleTerminalSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      if (!terminalInput.trim() || !activeTerminal) return;
      
      // Add input to terminal history
      addTerminalOutput(activeTerminal.id, `$ ${terminalInput}`, 'output');
      
      // Mock terminal command response
      setTimeout(() => {
        const responses: { [key: string]: string } = {
          'pwd': '/workspace/iris-agent/src',
          'ls': 'components  stores  types  App.tsx  index.css',
          'ls -la': 'total 24\ndrwxr-xr-x 5 iris staff 160 Nov 5 11:44 .\ndrwxr-xr-x 3 iris staff  96 Nov 5 11:44 components\n-rw-r--r-- 1 iris staff  1247 Nov 5 11:44 App.tsx\n-rw-r--r-- 1 iris staff  2341 Nov 5 11:44 index.css',
          'npm run dev': '🚀  VITE v4.5.0  ready in 1.2s\n\n➜  Local:   http://localhost:5173/\n➜  Network: http://192.168.1.100:5173/\n\npress h + enter to show help',
          'help': 'Comandos disponibles:\n  pwd     - Mostrar directorio actual\n  ls      - Listar archivos\n  ls -la  - Listar archivos con detalles\n  npm run dev - Iniciar servidor de desarrollo\n  clear   - Limpiar terminal\n  help    - Mostrar ayuda',
          'clear': 'Terminal limpiado',
        };
        
        const response = responses[terminalInput] || `Comando '${terminalInput}' no encontrado. Escribe 'help' para ver comandos disponibles.`;
        addTerminalOutput(activeTerminal.id, response);
      }, 500);
      
      setTerminalInput('');
    };

    return (
      <div className={cn(
        "border-t border-border bg-neutral-900 text-green-400 transition-all duration-200",
        terminalCollapsed ? "h-10" : "h-64"
      )}>
        {/* Terminal Header */}
        <div className="flex items-center justify-between h-10 px-4 bg-neutral-800">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4" />
            <span className="text-sm font-medium">
              Terminal - {activeTerminal?.name || 'bash'}
            </span>
            <div className={cn(
              "w-2 h-2 rounded-full",
              lspStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
            )} />
          </div>
          <div className="flex items-center space-x-1">
            <button
              onClick={() => createTerminalSession('node')}
              className="p-1 rounded hover:bg-neutral-700 text-xs"
            >
              +
            </button>
            <button
              onClick={() => setTerminalCollapsed(!terminalCollapsed)}
              className="p-1 rounded hover:bg-neutral-700"
            >
              <ChevronDown className={cn(
                "w-4 h-4 transition-transform",
                terminalCollapsed && "rotate-180"
              )} />
            </button>
          </div>
        </div>

        {/* Terminal Content */}
        {!terminalCollapsed && (
          <div className="flex-1 flex flex-col h-54">
            <div className="flex-1 overflow-y-auto p-4 font-mono text-sm">
              {activeTerminal?.history.map((line, index) => (
                <div key={line.id} className={cn(
                  "mb-1",
                  line.type === 'input' && "text-blue-400",
                  line.type === 'error' && "text-red-400"
                )}>
                  {line.type === 'input' && line.content}
                  {line.type !== 'input' && line.content}
                </div>
              ))}
            </div>
            
            {/* Terminal Input */}
            <form onSubmit={handleTerminalSubmit} className="p-4 pt-0">
              <div className="flex items-center space-x-2">
                <span className="text-green-400 font-mono">$</span>
                <input
                  type="text"
                  value={terminalInput}
                  onChange={(e) => setTerminalInput(e.target.value)}
                  className="flex-1 bg-transparent border-none outline-none text-green-400 font-mono text-sm"
                  placeholder="Escribe un comando..."
                  autoFocus
                />
              </div>
            </form>
          </div>
        )}
      </div>
    );
  };

  const StatusBar: React.FC = () => {
    const activeFile = getActiveFile();
    
    return (
      <div className="h-8 bg-neutral-950 text-neutral-400 text-xs flex items-center justify-between px-4 border-t border-neutral-800">
        <div className="flex items-center space-x-4">
          <span>UTF-8</span>
          <span>LF</span>
          {activeFile && (
            <>
              <span>{activeFile.language}</span>
              <span>Ln 1, Col 1</span>
            </>
          )}
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <div className={cn(
              "w-2 h-2 rounded-full",
              lspStatus === 'connected' ? 'bg-green-500' : 
              lspStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
            )} />
            <span>TypeScript</span>
            {lspErrors > 0 && (
              <span className="text-red-400">• {lspErrors} errores</span>
            )}
            {lspWarnings > 0 && (
              <span className="text-yellow-400">• {lspWarnings} advertencias</span>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* Editor Header */}
      <div className="h-12 bg-background border-b border-border flex items-center justify-between px-4">
        {/* File Tabs */}
        <div className="flex items-center flex-1 overflow-x-auto">
          {openFiles.map(file => (
            <FileTab
              key={file.id}
              file={file}
              isActive={file.id === activeFileId}
              onClose={() => closeFile(file.id)}
            />
          ))}
          
          {openFiles.length === 0 && (
            <div className="flex items-center px-4 text-neutral-500">
              <File className="w-4 h-4 mr-2" />
              <span className="text-sm">Sin archivos abiertos</span>
            </div>
          )}
        </div>

        {/* Editor Actions */}
        <div className="flex items-center space-x-2">
          {hasUnsavedChanges() && (
            <button
              onClick={saveAllFiles}
              className="p-2 rounded hover:bg-neutral-100 dark:hover:bg-neutral-800"
              title="Guardar todos (Ctrl+S)"
            >
              <Save className="w-4 h-4" />
            </button>
          )}
          <button className="p-2 rounded hover:bg-neutral-100 dark:hover:bg-neutral-800">
            <Download className="w-4 h-4" />
          </button>
          <button className="p-2 rounded hover:bg-neutral-100 dark:hover:bg-neutral-800">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Editor Area */}
      <div className="flex-1 flex">
        {/* File Explorer */}
        {!fileExplorerCollapsed && <FileExplorer />}
        
        {/* Monaco Editor */}
        <div className="flex-1 flex flex-col">
          {activeFileId ? (
            <Editor
              height="calc(100% - 32px)"
              language={getActiveFile()?.language || 'typescript'}
              value={getActiveFile()?.content || ''}
              onChange={handleFileChange}
              onMount={handleEditorDidMount}
              options={{
                fontSize,
                tabSize,
                wordWrap: wordWrap ? 'on' : 'off',
                minimap: { enabled: minimap },
                theme: theme === 'vs-dark' ? 'vs-dark' : theme,
              }}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center bg-neutral-50 dark:bg-neutral-900">
              <div className="text-center">
                <div className="w-16 h-16 bg-neutral-200 dark:bg-neutral-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Code className="w-8 h-8 text-neutral-400" />
                </div>
                <h3 className="text-lg font-medium text-neutral-600 dark:text-neutral-400 mb-2">
                  Selecciona un archivo para editar
                </h3>
                <p className="text-sm text-neutral-500">
                  Usa el explorador de archivos para abrir un archivo existente
                </p>
              </div>
            </div>
          )}
          
          <StatusBar />
          <TerminalPanel />
        </div>
      </div>
    </div>
  );
};

// Utility functions
const getLanguageFromExtension = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase();
  const languageMap: { [key: string]: string } = {
    'ts': 'typescript',
    'tsx': 'typescript',
    'js': 'javascript',
    'jsx': 'javascript',
    'py': 'python',
    'java': 'java',
    'cpp': 'cpp',
    'c': 'c',
    'css': 'css',
    'html': 'html',
    'json': 'json',
    'md': 'markdown',
    'yaml': 'yaml',
    'yml': 'yaml',
  };
  return languageMap[ext || ''] || 'plaintext';
};

const getMockFileContent = (filename: string): string => {
  const contents: { [key: string]: string } = {
    'App.tsx': `import { useState } from 'react'\nimport { BrowserRouter as Router, Routes, Route } from 'react-router-dom'\nimport Dashboard from './components/Dashboard'\nimport Projects from './components/Projects'\nimport Chat from './components/Chat'\n\nfunction App() {\n  const [theme, setTheme] = useState('dark')\n\n  return (\n    <Router>\n      <div className="min-h-screen bg-background text-foreground">\n        <Routes>\n          <Route path="/" element={<Dashboard />} />\n          <Route path="/projects" element={<Projects />} />\n          <Route path="/chat" element={<Chat />} />\n        </Routes>\n      </div>\n    </Router>\n  )\n}\n\nexport default App`,
    'Dashboard.tsx': `import React from 'react'\nimport { useAppStore } from '../stores/appStore'\n\nconst Dashboard: React.FC = () => {\n  const { metrics } = useAppStore()\n\n  return (\n    <div className="p-8">\n      <h1 className="text-title font-bold mb-4\">Dashboard Principal</h1>\n      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">\n        {/* Metric cards */}\n      </div>\n    </div>\n  )\n}\n\nexport default Dashboard`,
  };
  return contents[filename] || `// Archivo ${filename}\n// Contenido del archivo...`;
};

export default CodeEditor;