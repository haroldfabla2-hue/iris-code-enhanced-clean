// types/store.ts - Shared types for IRIS stores

// User Settings for persistence
export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: 'es' | 'en';
  mcpServerUrl: string;
  notifications: {
    email: boolean;
    push: boolean;
    desktop: boolean;
  };
  ai: {
    model: string;
    temperature: number;
    maxTokens: number;
  };
  editor: {
    fontSize: number;
    tabSize: number;
    wordWrap: boolean;
    minimap: boolean;
  };
  shortcuts: {
    [key: string]: string;
  };
}

// App Metrics interface (matching API response)
export interface AppMetrics {
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

// Chat interfaces
export interface Conversation {
  id: string;
  projectId: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_activity: string;
  messageCount: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  tokens?: number;
  projectId?: string;
  conversationId?: string;
  isStreaming?: boolean;
}

export interface ContextState {
  projectId: string | null;
  conversationId: string | null;
  files: string[];
  instructions: string;
}

// Project interfaces
export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  files_count: number;
  conversations_count: number;
  last_activity: string;
  isExpanded?: boolean;
  isSelected?: boolean;
}

export interface FileItem {
  id: string;
  name: string;
  path: string;
  size: number;
  type: string;
  created_at: string;
  updated_at: string;
  content?: string;
  project_id: string;
}

// Editor interfaces
export interface OpenFile {
  id: string;
  name: string;
  path: string;
  content: string;
  language: string;
  isDirty: boolean;
  isActive: boolean;
  lastModified: string;
  encoding: 'utf-8' | 'utf-16' | 'ascii';
  readonly?: boolean;
}

export interface TerminalSession {
  id: string;
  name: string;
  type: 'bash' | 'node' | 'python' | 'powershell';
  isActive: boolean;
  history: TerminalLine[];
  currentWorkingDirectory: string;
  pid?: number;
  isRunning: boolean;
}

export interface TerminalLine {
  id: string;
  type: 'output' | 'error' | 'input';
  content: string;
  timestamp: string;
}

export interface LSPDiagnostic {
  id: string;
  message: string;
  severity: 'error' | 'warning' | 'info' | 'hint';
  range: {
    start: { line: number; column: number };
    end: { line: number; column: number };
  };
  source: string;
  code?: string;
}

// Template interfaces
export interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  files: FileItem[];
  tags: string[];
  created_at: string;
  preview?: string;
}

// Notification interfaces
export interface Notification {
  id: string;
  type: 'system' | 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  persistent?: boolean;
}

// Canvas interfaces
export interface CanvasElement {
  id: string;
  type: 'rectangle' | 'circle' | 'text' | 'image' | 'code' | 'markdown';
  x: number;
  y: number;
  width: number;
  height: number;
  content?: string;
  style?: {
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
    fontSize?: number;
    fontFamily?: string;
    opacity?: number;
  };
}

export interface CanvasState {
  elements: CanvasElement[];
  selectedElementId: string | null;
  zoom: number;
  panX: number;
  panY: number;
  gridSize: number;
  showGrid: boolean;
  snapToGrid: boolean;
}

// Search interfaces
export interface SearchResult {
  id: string;
  type: 'file' | 'project' | 'conversation';
  title: string;
  content: string;
  path?: string;
  projectId?: string;
  lineNumber?: number;
  score: number;
  matches: {
    line: number;
    column: number;
    text: string;
  }[];
}

// Statistics interfaces
export interface ProjectStats {
  totalFiles: number;
  totalSize: number;
  languages: Record<string, number>;
  lastModified: string;
  contributors: string[];
  commits: number;
  branches: string[];
}

export interface UsageStats {
  totalProjects: number;
  totalFiles: number;
  totalConversations: number;
  tokensUsed: number;
  mostUsedLanguages: string[];
  favoriteTemplates: string[];
  averageSessionDuration: number;
}

// Settings interfaces
export interface EditorSettings {
  fontSize: number;
  tabSize: number;
  wordWrap: boolean;
  minimap: boolean;
  theme: 'vs-dark' | 'vs-light' | 'hc-black';
  showWhitespace: boolean;
  showLineNumbers: boolean;
  highlightActiveLine: boolean;
  renderLineHighlight: 'none' | 'line' | 'all' | 'gutter';
  autoSave: boolean;
  autoSaveDelay: number;
  formatOnSave: boolean;
}

export interface TerminalSettings {
  fontSize: number;
  theme: 'dark' | 'light';
  bell: boolean;
  historyLimit: number;
  copyOnSelect: boolean;
  pasteOnMiddleClick: boolean;
  fontFamily: string;
  lineHeight: number;
}

export interface AiSettings {
  model: string;
  temperature: number;
  maxTokens: number;
  suggestions: boolean;
  inlineCompletions: boolean;
  autoComplete: boolean;
  codeSuggestions: boolean;
  explanationMode: 'hover' | 'panel' | 'inline';
}

// File system interfaces
export interface FileSystemNode {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'folder';
  size?: number;
  modified: string;
  children?: FileSystemNode[];
  permissions?: {
    read: boolean;
    write: boolean;
    execute: boolean;
  };
}

// Error handling interfaces
export interface ErrorInfo {
  id: string;
  message: string;
  stack?: string;
  timestamp: string;
  context?: {
    component?: string;
    action?: string;
    userId?: string;
    projectId?: string;
  };
  severity: 'low' | 'medium' | 'high' | 'critical';
  resolved: boolean;
  resolvedAt?: string;
  resolvedBy?: string;
}

// Plugin interfaces
export interface Plugin {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  enabled: boolean;
  settings?: Record<string, any>;
  permissions?: string[];
}

export interface PluginManifest {
  name: string;
  version: string;
  description: string;
  author: string;
  main: string;
  permissions?: string[];
  dependencies?: Record<string, string>;
}

// Workspace interfaces
export interface Workspace {
  id: string;
  name: string;
  description?: string;
  projects: string[];
  settings: {
    theme: string;
    layout: 'split' | 'tabs' | 'floating';
    activeProject?: string;
    openFiles: string[];
    activeFile?: string;
    terminalSessions: string[];
    activeTerminal?: string;
  };
  created: string;
  lastOpened: string;
}

// Export/Import interfaces
export interface ExportData {
  version: string;
  timestamp: string;
  type: 'project' | 'workspace' | 'settings' | 'full';
  data: any;
  metadata?: {
    userId?: string;
    projectName?: string;
    description?: string;
  };
}

export interface ImportResult {
  success: boolean;
  data?: any;
  errors?: string[];
  warnings?: string[];
  importedItems?: {
    projects: number;
    files: number;
    conversations: number;
    templates: number;
  };
}

// API Response interfaces
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
}

// Theme interfaces
export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: {
    primary: string;
    secondary: string;
    disabled: string;
  };
  border: string;
  error: string;
  warning: string;
  success: string;
  info: string;
}

export interface Theme {
  id: string;
  name: string;
  colors: ThemeColors;
  isDark: boolean;
  isCustom: boolean;
  author?: string;
}

// Keyboard shortcuts
export interface KeyboardShortcut {
  id: string;
  name: string;
  description: string;
  key: string;
  category: string;
  action: string;
  when?: string;
  args?: any[];
}

// Context menu
export interface ContextMenuItem {
  id: string;
  label: string;
  icon?: string;
  shortcut?: string;
  disabled?: boolean;
  separator?: boolean;
  submenu?: ContextMenuItem[];
  action: () => void;
}

export interface ContextMenu {
  items: ContextMenuItem[];
  position: { x: number; y: number };
  target: HTMLElement;
}