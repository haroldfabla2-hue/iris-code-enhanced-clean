// Cliente de API para MCP Server
import { getApiUrl, getConfig } from './config';

export interface APIConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
}

const config = getConfig();

// Real API Config using our IRIS Code backend
export const API_CONFIG: APIConfig = {
  baseUrl: config.api.baseUrl,
  timeout: config.api.timeout,
  retryAttempts: config.api.retryAttempts
};

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  uptime: number;
  version: string;
  timestamp: string;
}

export interface MetricsResponse {
  total_conversations: number;
  active_projects: number;
  tokens_used: number;
  system_load: number;
  memory_usage: number;
  last_updated: string;
  server_status: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  tokens?: number;
  project_id?: string;
}

export interface ChatResponse {
  id: string;
  message: ChatMessage;
  streaming: boolean;
}

// Assets API Interfaces
export interface AssetGenerationRequest {
  prompt: string;
  category?: string;
  format_type?: string;
  style?: string;
  requirements?: Record<string, any>;
  stream?: boolean;
}

export interface AssetFile {
  filename: string;
  content: string;
  type: string;
  size?: number;
  url?: string;
}

export interface AssetResponse {
  generation_id: string;
  status: string;
  timestamp: string;
  category: string;
  format: string;
  files: AssetFile[];
  metadata: Record<string, any>;
  error?: string;
  preview_url?: string;
}

export interface VideoGenerationResponse {
  video_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  prompt: string;
  video_url?: string;
  duration?: number;
  format: string;
  created_at: string;
  thumbnail_url?: string;
  metadata?: {
    width: number;
    height: number;
    fps: number;
    duration: number;
  };
}

export interface VideoGenerationRequest {
  prompt: string;
  style?: 'reel' | 'short' | 'standard';
  duration?: number; // seconds
  aspect_ratio?: '9:16' | '16:9' | '1:1';
  quality?: 'standard' | 'hd' | '4k';
  voiceover?: boolean;
  music?: boolean;
}

export interface VideoGenerationLimit {
  used_count: number;
  remaining_count: number;
  reset_date: string;
  weekly_limit: number;
}

export interface AssetCategoryResponse {
  status: string;
  categories: string[];
  total: number;
}

export interface AssetChatMessage {
  message: string;
  conversation_id?: string;
  context?: Record<string, any>;
}

export interface AssetChatResponse {
  conversation_id: string;
  message_id: string;
  response: string;
  asset_generated?: AssetResponse;
  suggestions: string[];
  timestamp: string;
}

export interface FreepikConfig {
  api_key: string;
  secret: string;
  base_url: string;
}

// Memory API Interfaces
export interface MemorySearchRequest {
  query: string;
  search_type: 'semantic' | 'keyword' | 'hybrid';
  limit?: number;
  time_range?: string;
  conversation_id?: string;
  content_type?: string;
  user_id?: string;
}

export interface MemorySearchResult {
  content: string;
  content_type: string;
  relevance_score?: number;
  stored_at: string;
  memory_id: string;
  metadata: Record<string, any>;
  tags?: string[];
}

export interface MemorySearchResponse {
  query: string;
  search_type: string;
  total_results: number;
  results: MemorySearchResult[];
  search_metadata: Record<string, any>;
  execution_time_ms: number;
}

export interface MemoryStoreRequest {
  content: string;
  content_type: string;
  conversation_id?: string;
  user_id?: string;
  metadata?: Record<string, any>;
  tags?: string[];
}

export interface MemoryStoreResponse {
  memory_id: string;
  status: string;
  stored_at: string;
  metadata: Record<string, any>;
}

export interface MemoryStatsResponse {
  total_memories: number;
  memories_by_type: Record<string, number>;
  memories_by_user: Record<string, number>;
  recent_activity: Record<string, any>;
  storage_stats: Record<string, any>;
}

export interface StoreDocumentRequest {
  content: string;
  title: string;
  source_type: string;
  source_url?: string;
  source_file?: string;
  tags?: string[];
  chunking_strategy?: string;
  document_type?: string;
  metadata?: Record<string, any>;
}

export interface MemoryClearRequest {
  user_id?: string;
  conversation_id?: string;
  older_than?: string;
  content_type?: string;
}

export interface MemoryClearResponse {
  status: string;
  cleared_count: number;
  cleared_memories: string[];
  execution_time_ms: number;
  timestamp: string;
}

// Tools API Interfaces
export interface ToolRequest {
  tool_name: string;
  parameters: Record<string, any>;
  executor_type: string;
  user_id?: string;
  timeout?: number;
  async_mode?: boolean;
}

export interface ToolInfo {
  name: string;
  description: string;
  parameters: string[];
  executor_type: string;
}

export interface ToolResponse {
  execution_id: string;
  tool_name: string;
  status: 'success' | 'error' | 'timeout' | 'started';
  result?: Record<string, any>;
  error?: string;
  execution_time_ms: number;
  metadata?: Record<string, any>;
}

export interface ToolsListResponse {
  tools: ToolInfo[];
  executors: string[];
  total_tools: number;
}

export interface ExecutionStatus {
  execution_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'timeout' | 'not_implemented';
  message?: string;
  result?: Record<string, any>;
  error?: string;
  execution_time_ms?: number;
  started_at?: string;
  completed_at?: string;
}

// Chat API Interfaces
export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tokens?: number;
  is_streaming?: boolean;
  stream_completed?: boolean;
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface Conversation {
  id: string;
  user_id?: string;
  project_id?: string;
  title?: string;
  context_summary?: string;
  is_active: boolean;
  message_count: number;
  created_at: string;
  updated_at: string;
  last_message_at: string;
  metadata?: Record<string, any>;
}

export interface SendMessageRequest {
  content: string;
  role?: 'user' | 'assistant' | 'system';
  stream?: boolean;
}

export interface SendMessageResponse {
  message: ChatMessage;
  conversation_id: string;
  streaming?: boolean;
}

export interface StreamMessageChunk {
  type: 'message' | 'error' | 'done';
  content?: string;
  message_id?: string;
  error?: string;
  done?: boolean;
}

// Projects API Interfaces
export interface Project {
  id: string;
  name: string;
  description?: string;
  user_id?: string;
  project_type?: string;
  created_at: string;
  updated_at: string;
  last_activity: string;
  metadata?: Record<string, any>;
  is_deleted?: boolean;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  user_id?: string;
  project_type?: string;
  metadata?: Record<string, any>;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  project_type?: string;
  metadata?: Record<string, any>;
}

export interface ProjectAnalytics {
  total_files: number;
  total_conversations: number;
  total_messages: number;
  project_size_mb: number;
  last_activity_date?: string;
  activity_summary: {
    files_created_this_week: number;
    conversations_this_week: number;
    most_active_day: string;
  };
}

export interface ProjectConversation {
  id: string;
  title?: string;
  message_count: number;
  created_at: string;
  last_message_at: string;
  is_active: boolean;
}

export interface ProjectSummary {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'archived';
  stats: {
    files_count: number;
    conversations_count: number;
    total_messages: number;
    last_activity: string;
  };
  created_at: string;
  updated_at: string;
}

// Tasks API Interfaces
export interface TaskRequest {
  task_id?: string;
  task_type: 'generation' | 'analysis' | 'processing' | 'automation';
  title?: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  parameters?: Record<string, any>;
  dependencies?: string[];
  metadata?: Record<string, any>;
  budget?: {
    tokens?: number;
    time_seconds?: number;
    tools_max?: number;
  };
}

export interface TaskResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'timeout';
  result?: Record<string, any>;
  error?: string;
  execution_time_ms: number;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'timeout';
  progress: number; // 0-100
  current_step?: string;
  estimated_completion?: string;
  execution_time_ms: number;
  error?: string;
  metadata?: Record<string, any>;
}

export interface TaskResult {
  task_id: string;
  result: Record<string, any>;
  execution_time_ms: number;
  metadata?: Record<string, any>;
  created_at: string;
  completed_at: string;
}

export interface TaskList {
  tasks: TaskResponse[];
  total: number;
  pending: number;
  processing: number;
  completed: number;
  failed: number;
}

// Bridge API Interfaces
export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  services: {
    iris_agents: boolean;
    silhouette_teams: boolean;
    processing_modes: boolean;
  };
  uptime: number;
  last_check: string;
}

export interface AgentInfo {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'inactive' | 'busy';
  capabilities: string[];
  load: number;
  last_activity: string;
}

export interface TeamInfo {
  id: string;
  name: string;
  members: AgentInfo[];
  status: 'active' | 'inactive';
  specialization: string;
  current_task?: string;
}

export interface ProcessingMode {
  id: string;
  name: string;
  description: string;
  performance: 'low' | 'medium' | 'high';
  resource_usage: number;
  supported_agents: string[];
}

export interface UnifiedChatRequest {
  message: string;
  context?: Record<string, any>;
  agent_type?: string;
  team_id?: string;
  mode?: string;
}

export interface UnifiedChatResponse {
  response: string;
  agent_used?: string;
  team_used?: string;
  processing_time_ms: number;
  confidence: number;
  suggestions?: string[];
}

export interface AIModel {
  id: string;
  name: string;
  provider: string;
  type: 'llm' | 'embedding' | 'generation';
  status: 'active' | 'inactive' | 'training';
  performance_metrics: {
    speed: number;
    accuracy: number;
    cost: number;
  };
}

export interface TaskRoutingResponse {
  recommended_agents: string[];
  recommended_team?: string;
  estimated_completion: string;
  routing_score: number;
  alternative_options: string[];
}

export interface IntegrationInfo {
  system_name: string;
  version: string;
  capabilities: string[];
  endpoints: string[];
  health_status: 'healthy' | 'degraded' | 'unhealthy';
  last_sync: string;
}
  max_tokens?: number;
}

export interface MemoryClearRequest {
  user_id?: string;
  conversation_id?: string;
  older_than?: string;
}

export interface MemoryClearResponse {
  status: string;
  cleared_count: number;
  cleared_at: string;
  criteria: Record<string, any>;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  files_count: number;
  conversations_count: number;
  last_activity: string;
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

class MCPClient {
  private config: APIConfig;
  private baseUrl: string;
  private isOnline: boolean = false;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;

  constructor() {
    const defaultUrl = localStorage.getItem('mcp-server-url') || getApiUrl('/');
    this.config = {
      baseUrl: defaultUrl,
      timeout: config.api.timeout,
      retryAttempts: config.api.retryAttempts
    };
    this.baseUrl = this.config.baseUrl;
  }

  // Configuración
  setServerUrl(url: string) {
    this.baseUrl = url;
    localStorage.setItem('mcp-server-url', url);
    this.config.baseUrl = url;
  }

  getServerUrl(): string {
    return this.baseUrl;
  }

  // Health Check
  async checkHealth(): Promise<HealthResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      this.isOnline = true;
      this.reconnectAttempts = 0;
      
      // Map backend response to our interface
      return {
        status: data.status || 'healthy',
        uptime: Date.now(), // Approximate uptime
        version: data.version || '1.0.0',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Health check failed:', error);
      this.isOnline = false;
      this.handleReconnection();
      return null;
    }
  }

  // Metrics
  async getMetrics(): Promise<MetricsResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/metrics`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return {
        total_conversations: data.total_conversations || 0,
        active_projects: data.active_projects || 0,
        tokens_used: data.tokens_used || 0,
        system_load: data.system_load || 0,
        memory_usage: data.memory_usage || 0,
        last_updated: data.last_updated || new Date().toISOString(),
        server_status: data.status || 'unknown'
      };
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      return this.getFallbackMetrics();
    }
  }

  // Chat
  async sendMessage(
    message: string, 
    projectId?: string, 
    conversationId?: string
  ): Promise<ChatResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          project_id: projectId,
          conversation_id: conversationId
        }),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to send message:', error);
      return null;
    }
  }

  // Streaming Chat
  async sendMessageStream(
    message: string,
    projectId?: string,
    conversationId?: string,
    onChunk?: (chunk: string) => void
  ): Promise<{ success: boolean; messageId?: string; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
        },
        body: JSON.stringify({
          message,
          project_id: projectId,
          conversation_id: conversationId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let messageId = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                return { success: true, messageId };
              }
              
              try {
                const parsed = JSON.parse(data);
                if (parsed.id) messageId = parsed.id;
                if (parsed.content && onChunk) {
                  onChunk(parsed.content);
                }
              } catch (e) {
                // Ignore parsing errors for non-JSON chunks
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      return { success: true, messageId };
    } catch (error) {
      console.error('Streaming failed:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  }

  // Projects
  async getProjects(): Promise<Project[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      // Handle both direct array and wrapped response
      return Array.isArray(data) ? data : (data.projects || data.items || []);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      return this.getFallbackProjects();
    }
  }

  async updateProject(projectId: string, updates: { name?: string; description?: string }): Promise<Project | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.project;
    } catch (error) {
      console.error('Failed to update project:', error);
      return null;
    }
  }

  async deleteProject(projectId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to delete project:', error);
      return false;
    }
  }

  async createProject(name: string, description?: string): Promise<Project | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          description: description || ''
        }),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.project || data;
    } catch (error) {
      console.error('Failed to create project:', error);
      return null;
    }
  }

  // Files
  async getProjectFiles(projectId: string): Promise<FileItem[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}/files`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.files || [];
    } catch (error) {
      console.error('Failed to fetch project files:', error);
      return [];
    }
  }

  async uploadFile(projectId: string, file: File): Promise<FileItem | null> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}/files`, {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.file;
    } catch (error) {
      console.error('Failed to upload file:', error);
      return null;
    }
  }

  async getFile(fileId: string): Promise<FileItem | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/files/${fileId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.file;
    } catch (error) {
      console.error('Failed to fetch file:', error);
      return null;
    }
  }

  async deleteFile(fileId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/files/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to delete file:', error);
      return false;
    }
  }

  async saveFile(fileId: string, content: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/files/${fileId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to save file:', error);
      return false;
    }
  }

  // Templates
  async getTemplates(): Promise<Template[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/templates`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.templates || [];
    } catch (error) {
      console.error('Failed to fetch templates:', error);
      return this.getFallbackTemplates();
    }
  }

  async createFromTemplate(templateId: string, projectName: string): Promise<Project | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/templates/${templateId}/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project_name: projectName }),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.project;
    } catch (error) {
      console.error('Failed to create project from template:', error);
      return null;
    }
  }

  // Assets API Methods
  async getAssetCategories(): Promise<AssetCategoryResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/categories`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to fetch asset categories:', error);
      return {
        status: 'success',
        categories: ['branding', 'mobile_ui', 'marketing', 'saas_platform', 'ecommerce', 'executive'],
        total: 6
      };
    }
  }

  async generateAsset(request: AssetGenerationRequest): Promise<AssetResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.timeout * 3) // Longer timeout for generation
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to generate asset:', error);
      return null;
    }
  }

  async generateAssetStream(
    request: AssetGenerationRequest,
    onProgress?: (data: any) => void
  ): Promise<AssetResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/generate/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ...request, stream: true }),
        signal: AbortSignal.timeout(this.config.timeout * 3)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) return null;

      const decoder = new TextDecoder();
      let accumulatedData = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        accumulatedData += decoder.decode(value, { stream: true });
        const lines = accumulatedData.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onProgress?.(data);
              
              if (data.status === 'completed' && data.result) {
                return data.result;
              }
            } catch (e) {
              // Ignore parse errors for incomplete data
            }
          }
        }
        accumulatedData = lines[lines.length - 1] || '';
      }

      return null;
    } catch (error) {
      console.error('Failed to generate asset with stream:', error);
      return null;
    }
  }

  async chatWithAssetGeneration(message: string, conversationId?: string): Promise<AssetChatResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          context: {}
        }),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to chat with asset generation:', error);
      return null;
    }
  }

  async getAssetHistory(limit: number = 50): Promise<AssetResponse[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/history?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data || [];
    } catch (error) {
      console.error('Failed to fetch asset history:', error);
      return [];
    }
  }

  async getAssetStatus(generationId: string): Promise<AssetResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/generate/${generationId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get asset status:', error);
      return null;
    }
  }

  async regenerateAsset(generationId: string, newPrompt?: string): Promise<AssetResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/regenerate/${generationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ new_prompt: newPrompt }),
        signal: AbortSignal.timeout(this.config.timeout * 3)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to regenerate asset:', error);
      return null;
    }
  }

  // Freepik Integration (Fallback)
  async generateWithFreepik(
    prompt: string, 
    style: string = 'modern'
  ): Promise<AssetResponse | null> {
    try {
      const freepikConfig: FreepikConfig = {
        api_key: 'FPSXced2121aef64ce573bf7ee02917e2402',
        secret: '4cf3111eacf53b0cecac878145f6e940',
        base_url: 'https://api.freepik.com/v1'
      };

      const response = await fetch(`${freepikConfig.base_url}/images/search`, {
        method: 'GET',
        headers: {
          'X-Freepik-Api-Key': freepikConfig.api_key,
          'X-Freepik-Secret': freepikConfig.secret,
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`Freepik API HTTP ${response.status}`);
      }

      const data = await response.json();
      
      // Convert Freepik response to our AssetResponse format
      const timestamp = new Date().toISOString();
      const generationId = `freepik_${Date.now()}`;
      
      return {
        generation_id: generationId,
        status: 'completed',
        timestamp,
        category: 'marketing',
        format: 'jpg',
        files: data?.results?.slice(0, 3).map((img: any, index: number) => ({
          filename: `freepik_${index + 1}.jpg`,
          content: img.url,
          type: 'image',
          url: img.url,
          size: img.size || 0
        })) || [],
        metadata: {
          source: 'freepik',
          prompt,
          style,
          search_count: data?.total || 0
        },
        preview_url: data?.results?.[0]?.url
      };
    } catch (error) {
      console.error('Failed to generate with Freepik:', error);
      return null;
    }
  }

  // Memory API Methods
  async searchMemory(request: MemorySearchRequest): Promise<MemorySearchResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/memory/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to search memory:', error);
      return {
        query: request.query,
        search_type: request.search_type,
        total_results: 0,
        results: [],
        search_metadata: { error: 'search_failed' },
        execution_time_ms: 0
      };
    }
  }

  async searchMemoryGet(
    query: string, 
    searchType: string = 'semantic',
    limit: number = 10,
    timeRange?: string,
    conversationId?: string,
    contentType?: string,
    userId?: string
  ): Promise<MemorySearchResponse | null> {
    try {
      const params = new URLSearchParams({
        query,
        search_type: searchType,
        limit: limit.toString()
      });

      if (timeRange) params.append('time_range', timeRange);
      if (conversationId) params.append('conversation_id', conversationId);
      if (contentType) params.append('content_type', contentType);
      if (userId) params.append('user_id', userId);

      const response = await fetch(`${this.baseUrl}/api/v1/memory/search?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to search memory (GET):', error);
      return null;
    }
  }

  async storeMemory(request: MemoryStoreRequest): Promise<MemoryStoreResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/memory/store`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to store memory:', error);
      return null;
    }
  }

  async getMemoryStats(): Promise<MemoryStatsResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/memory/stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get memory stats:', error);
      return {
        total_memories: 0,
        memories_by_type: {},
        memories_by_user: {},
        recent_activity: {},
        storage_stats: { error: 'stats_unavailable' }
      };
    }
  }

  async clearMemory(request: MemoryClearRequest): Promise<MemoryClearResponse | null> {
    try {
      const params = new URLSearchParams();
      if (request.user_id) params.append('user_id', request.user_id);
      if (request.conversation_id) params.append('conversation_id', request.conversation_id);
      if (request.older_than) params.append('older_than', request.older_than);

      const response = await fetch(`${this.baseUrl}/api/v1/memory/clear?${params}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to clear memory:', error);
      return null;
    }
  }

  async storeDocument(request: StoreDocumentRequest): Promise<any | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/memory/store-document`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.timeout * 2) // Longer timeout for documents
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to store document:', error);
      return null;
    }
  }

  // Quick memory helpers
  async remember(
    content: string, 
    contentType: string = 'text', 
    conversationId?: string,
    tags?: string[]
  ): Promise<MemoryStoreResponse | null> {
    return this.storeMemory({
      content,
      content_type: contentType,
      conversation_id: conversationId,
      tags: tags || []
    });
  }

  // Tools API Methods
  async listAvailableTools(): Promise<ToolsListResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/tools/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to list tools:', error);
      return {
        tools: [],
        executors: [],
        total_tools: 0
      };
    }
  }

  async executeTool(request: ToolRequest): Promise<ToolResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/tools/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.timeout * 2) // Longer timeout for tool execution
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to execute tool:', error);
      return {
        execution_id: 'error',
        tool_name: request.tool_name,
        status: 'error',
        error: 'tool_execution_failed',
        execution_time_ms: 0
      };
    }
  }

  async getExecutionStatus(executionId: string): Promise<ExecutionStatus | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/tools/execute/${executionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get execution status:', error);
      return {
        execution_id: executionId,
        status: 'failed',
        message: 'status_check_failed'
      };
    }
  }

  // Tools API Quick Helpers
  async runWebSearch(
    query: string, 
    numResults: number = 5,
    userId?: string
  ): Promise<ToolResponse | null> {
    return this.executeTool({
      tool_name: 'web_search',
      parameters: { query, num_results: numResults },
      executor_type: 'general',
      user_id: userId,
      async_mode: false
    });
  }

  async executePython(
    code: string, 
    timeout: number = 30,
    userId?: string
  ): Promise<ToolResponse | null> {
    return this.executeTool({
      tool_name: 'python_execute',
      parameters: { code, timeout },
      executor_type: 'code',
      user_id: userId,
      async_mode: false
    });
  }

  async scrapeWebsite(
    url: string, 
    selector?: string,
    userId?: string
  ): Promise<ToolResponse | null> {
    return this.executeTool({
      tool_name: 'web_scrape',
      parameters: { url, selector },
      executor_type: 'web',
      user_id: userId,
      async_mode: false
    });
  }

  async extractPDF(
    filePath: string, 
    pages?: number,
    userId?: string
  ): Promise<ToolResponse | null> {
    return this.executeTool({
      tool_name: 'pdf_extract',
      parameters: { file_path: filePath, pages },
      executor_type: 'docs',
      user_id: userId,
      async_mode: false
    });
  }

  async analyzeText(
    text: string, 
    analysisType: string = 'general',
    userId?: string
  ): Promise<ToolResponse | null> {
    return this.executeTool({
      tool_name: 'text_analysis',
      parameters: { text, analysis_type: analysisType },
      executor_type: 'general',
      user_id: userId,
      async_mode: false
    });
  }

  // Chat API Methods
  async createConversation(
    userId?: string,
    projectId?: string,
    title?: string
  ): Promise<Conversation | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          project_id: projectId,
          title
        }),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      return {
        id: 'error',
        user_id: userId,
        project_id: projectId,
        title: title || 'Conversación de error',
        context_summary: '',
        is_active: false,
        message_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_message_at: new Date().toISOString(),
        metadata: { error: 'create_failed' }
      };
    }
  }

  async sendMessage(
    conversationId: string,
    content: string,
    role: 'user' | 'assistant' | 'system' = 'user',
    stream: boolean = false,
    userId?: string
  ): Promise<SendMessageResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/${conversationId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          role,
          stream,
          user_id: userId
        }),
        signal: AbortSignal.timeout(this.config.timeout * 2) // Longer for chat
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to send message:', error);
      return {
        message: {
          role,
          content,
          is_streaming: false,
          stream_completed: false,
          metadata: { error: 'send_failed' }
        },
        conversation_id: conversationId,
        streaming: false
      };
    }
  }

  async getMessages(
    conversationId: string
  ): Promise<ChatMessage[] | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/${conversationId}/messages`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get messages:', error);
      return [];
    }
  }

  async getConversations(
    userId?: string,
    projectId?: string,
    limit: number = 20
  ): Promise<Conversation[] | null> {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('user_id', userId);
      if (projectId) params.append('project_id', projectId);
      if (limit) params.append('limit', limit.toString());

      const response = await fetch(`${this.baseUrl}/api/v1/chat/conversations?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get conversations:', error);
      return [];
    }
  }

  async deleteConversation(
    conversationId: string
  ): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/${conversationId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return true;
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      return false;
    }
  }

  // Chat API Quick Helpers
  async startChat(
    userId?: string,
    projectId?: string,
    initialMessage?: string
  ): Promise<{ conversation: Conversation | null; firstMessage: SendMessageResponse | null }> {
    try {
      // Create conversation
      const conversation = await this.createConversation(userId, projectId);
      if (!conversation) {
        return { conversation: null, firstMessage: null };
      }

      // Send first message if provided
      let firstMessage = null;
      if (initialMessage) {
        firstMessage = await this.sendMessage(conversation.id, initialMessage, 'user', false, userId);
      }

      return { conversation, firstMessage };
    } catch (error) {
      console.error('Failed to start chat:', error);
      return { conversation: null, firstMessage: null };
    }
  }

  // Projects API Methods
  async getProjects(
    userId?: string,
    limit: number = 20
  ): Promise<Project[] | null> {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('user_id', userId);
      if (limit) params.append('limit', limit.toString());

      const response = await fetch(`${this.baseUrl}/api/v1/projects/?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get projects:', error);
      return [];
    }
  }

  async createProject(request: CreateProjectRequest): Promise<Project | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to create project:', error);
      return {
        id: 'error',
        name: request.name,
        description: request.description,
        user_id: request.user_id,
        project_type: request.project_type,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_activity: new Date().toISOString(),
        metadata: { error: 'create_failed' }
      };
    }
  }

  async getProject(projectId: string): Promise<Project | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get project:', error);
      return null;
    }
  }

  async updateProject(
    projectId: string, 
    request: UpdateProjectRequest
  ): Promise<Project | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to update project:', error);
      return null;
    }
  }

  async deleteProject(projectId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return true;
    } catch (error) {
      console.error('Failed to delete project:', error);
      return false;
    }
  }

  async getProjectAnalytics(projectId: string): Promise<ProjectAnalytics | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}/analytics`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get project analytics:', error);
      return {
        total_files: 0,
        total_conversations: 0,
        total_messages: 0,
        project_size_mb: 0,
        activity_summary: {
          files_created_this_week: 0,
          conversations_this_week: 0,
          most_active_day: 'N/A'
        }
      };
    }
  }

  async getProjectConversations(
    projectId: string,
    limit: number = 20
  ): Promise<ProjectConversation[] | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}/conversations?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get project conversations:', error);
      return [];
    }
  }

  async getProjectSummary(projectId: string): Promise<ProjectSummary | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/projects/${projectId}/summary`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get project summary:', error);
      return {
        id: projectId,
        name: 'Proyecto de Error',
        description: 'No se pudo cargar la información del proyecto',
        status: 'inactive',
        stats: {
          files_count: 0,
          conversations_count: 0,
          total_messages: 0,
          last_activity: new Date().toISOString()
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
    }
  }

  // Projects API Quick Helpers
  async createQuickProject(
    name: string,
    description?: string,
    projectType: string = 'web-app',
    userId?: string
  ): Promise<Project | null> {
    return this.createProject({
      name,
      description,
      project_type: projectType,
      user_id: userId
    });
  }

  async getUserProjects(
    userId?: string,
    includeAnalytics: boolean = false
  ): Promise<Project[] | null> {
    try {
      const projects = await this.getProjects(userId);
      if (!projects || !includeAnalytics) {
        return projects;
      }

      // Add analytics to each project
      const projectsWithAnalytics = await Promise.all(
        projects.map(async (project) => {
          const analytics = await this.getProjectAnalytics(project.id);
          return {
            ...project,
            analytics
          };
        })
      );

      return projectsWithAnalytics;
    } catch (error) {
      console.error('Failed to get user projects with analytics:', error);
      return projects;
    }
  }

  // Tasks API Methods
  async createTask(request: TaskRequest): Promise<TaskResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/tasks/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to create task:', error);
      return {
        task_id: 'error',
        status: 'failed',
        error: 'task_creation_failed',
        execution_time_ms: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
    }
  }

  async executeTask(request: TaskRequest): Promise<TaskResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/tasks/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.timeout * 3) // Longer timeout for task execution
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to execute task:', error);
      return {
        task_id: 'error',
        status: 'failed',
        error: 'task_execution_failed',
        execution_time_ms: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
    }
  }

  async getTaskStatus(taskId: string): Promise<TaskStatus | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/tasks/${taskId}/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get task status:', error);
      return {
        task_id: taskId,
        status: 'failed',
        progress: 0,
        execution_time_ms: 0,
        error: 'status_check_failed'
      };
    }
  }

  async getTaskResult(taskId: string): Promise<TaskResult | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/tasks/${taskId}/results`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get task result:', error);
      return {
        task_id: taskId,
        result: { error: 'result_unavailable' },
        execution_time_ms: 0,
        created_at: new Date().toISOString(),
        completed_at: new Date().toISOString()
      };
    }
  }

  async deleteTask(taskId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return true;
    } catch (error) {
      console.error('Failed to delete task:', error);
      return false;
    }
  }

  async listTasks(
    status?: 'pending' | 'processing' | 'completed' | 'failed',
    limit: number = 20
  ): Promise<TaskList | null> {
    try {
      const params = new URLSearchParams();
      if (status) params.append('status', status);
      if (limit) params.append('limit', limit.toString());

      const response = await fetch(`${this.baseUrl}/api/v1/tasks/list?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to list tasks:', error);
      return {
        tasks: [],
        total: 0,
        pending: 0,
        processing: 0,
        completed: 0,
        failed: 0
      };
    }
  }

  async getTaskStream(taskId: string): Promise<EventSource | null> {
    try {
      const eventSource = new EventSource(`${this.baseUrl}/api/v1/tasks/${taskId}/stream`);
      return eventSource;
    } catch (error) {
      console.error('Failed to get task stream:', error);
      return null;
    }
  }

  // Tasks API Quick Helpers
  async createAndExecuteTask(
    taskType: 'generation' | 'analysis' | 'processing' | 'automation',
    title: string,
    description: string,
    parameters: Record<string, any> = {},
    priority: 'low' | 'medium' | 'high' | 'urgent' = 'medium'
  ): Promise<TaskResponse | null> {
    return this.executeTask({
      task_type: taskType,
      title,
      description,
      priority,
      parameters
    });
  }

  async generateAsset(
    prompt: string,
    category: string = 'general',
    format: string = 'svg'
  ): Promise<TaskResponse | null> {
    return this.createAndExecuteTask(
      'generation',
      'Generar Asset',
      `Generar asset ${format} para categoría ${category}`,
      { prompt, category, format },
      'high'
    );
  }

  async analyzeData(
    data: any,
    analysisType: string = 'summary'
  ): Promise<TaskResponse | null> {
    return this.createAndExecuteTask(
      'analysis',
      'Análisis de Datos',
      `Realizar análisis ${analysisType} de datos`,
      { data, analysis_type: analysisType },
      'medium'
    );
  }

  async processDocument(
    filePath: string,
    operation: string = 'extract_text'
  ): Promise<TaskResponse | null> {
    return this.createAndExecuteTask(
      'processing',
      'Procesar Documento',
      `Procesar documento: ${filePath}`,
      { file_path: filePath, operation },
      'low'
    );
  }

  async automateWorkflow(
    workflow: string,
    parameters: Record<string, any> = {}
  ): Promise<TaskResponse | null> {
    return this.createAndExecuteTask(
      'automation',
      'Automatización',
      `Ejecutar workflow: ${workflow}`,
      { workflow, ...parameters },
      'high'
    );
  }

  // Bridge API Methods
  async getSystemStatus(): Promise<SystemStatus | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get system status:', error);
      return {
        status: 'degraded',
        services: {
          iris_agents: false,
          silhouette_teams: false,
          processing_modes: false
        },
        uptime: 0,
        last_check: new Date().toISOString()
      };
    }
  }

  async getIRISAgents(): Promise<AgentInfo[] | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/iris-agents`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get IRIS agents:', error);
      return [];
    }
  }

  async getSilhouetteTeams(): Promise<TeamInfo[] | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/silhouette-teams`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get Silhouette teams:', error);
      return [];
    }
  }

  async getProcessingModes(): Promise<ProcessingMode[] | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/processing-modes`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get processing modes:', error);
      return [];
    }
  }

  async selectProcessingMode(modeId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/mode`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mode_id: modeId }),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return true;
    } catch (error) {
      console.error('Failed to select processing mode:', error);
      return false;
    }
  }

  async processTaskThroughBridge(
    task: string,
    parameters: Record<string, any> = {}
  ): Promise<any | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/process-task`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task, parameters }),
        signal: AbortSignal.timeout(this.config.timeout * 2)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to process task through bridge:', error);
      return null;
    }
  }

  async getAIModels(): Promise<AIModel[] | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/ai-models`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get AI models:', error);
      return [];
    }
  }

  async processWithAI(
    prompt: string,
    modelId?: string,
    parameters: Record<string, any> = {}
  ): Promise<any | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/ai-process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt, model_id: modelId, parameters }),
        signal: AbortSignal.timeout(this.config.timeout * 2)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to process with AI:', error);
      return null;
    }
  }

  async getTaskRouting(
    taskType: string,
    requirements: Record<string, any> = {}
  ): Promise<TaskRoutingResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/routing/${taskType}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get task routing:', error);
      return {
        recommended_agents: [],
        routing_score: 0,
        alternative_options: []
      };
    }
  }

  async getIntegrationInfo(): Promise<IntegrationInfo[] | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/integration-info`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get integration info:', error);
      return [];
    }
  }

  async unifiedChat(request: UnifiedChatRequest): Promise<UnifiedChatResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/bridge/unified-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.timeout * 2)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed unified chat:', error);
      return {
        response: 'Error en comunicación unificada',
        processing_time_ms: 0,
        confidence: 0
      };
    }
  }

  // Bridge API Quick Helpers
  async getAvailableAgents(): Promise<AgentInfo[] | null> {
    return this.getIRISAgents();
  }

  async getBestAgentForTask(taskType: string): Promise<AgentInfo | null> {
    const agents = await this.getIRISAgents();
    if (!agents) return null;
    
    // Encontrar el agente más adecuado
    return agents.find(agent => 
      agent.status === 'active' && 
      agent.capabilities.includes(taskType)
    ) || agents[0];
  }

  async executeWithOptimalAgent(
    task: string,
    parameters: Record<string, any> = {}
  ): Promise<any | null> {
    const agent = await this.getBestAgentForTask(task);
    if (!agent) return null;
    
    return this.processTaskThroughBridge(task, {
      ...parameters,
      preferred_agent: agent.id
    });
  }

  async intelligentChat(
    message: string,
    context: Record<string, any> = {}
  ): Promise<UnifiedChatResponse | null> {
    // Determinar el mejor modo de procesamiento
    const modes = await this.getProcessingModes();
    const bestMode = modes?.find(mode => mode.performance === 'high');
    
    return this.unifiedChat({
      message,
      context,
      mode: bestMode?.id
    });
  }

  async recall(
    query: string, 
    searchType: 'semantic' | 'keyword' | 'hybrid' = 'semantic',
    limit: number = 5
  ): Promise<MemorySearchResponse | null> {
    return this.searchMemory({
      query,
      search_type: searchType,
      limit
    });
  }

  // Status
  isServerOnline(): boolean {
    return this.isOnline;
  }

  // VEO3 Video Generation
  async generateVideoVEO3(request: VideoGenerationRequest): Promise<VideoGenerationResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/video/veo3`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: request.prompt,
          style: request.style || 'reel',
          duration: request.duration || 30,
          aspect_ratio: request.aspect_ratio || '9:16',
          quality: request.quality || 'hd',
          voiceover: request.voiceover || false,
          music: request.music || false,
          api_key: 'AIzaSyBlqzSr6sv65rsQmNjNMGDZ5sz72DCpP38'
        }),
        signal: AbortSignal.timeout(this.config.timeout * 5) // Longer timeout for video generation
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Failed to generate video with VEO3:', error);
      return {
        video_id: 'error',
        status: 'failed',
        prompt: request.prompt,
        format: 'mp4',
        created_at: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  async getVideoGenerationStatus(videoId: string): Promise<VideoGenerationResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/video/veo3/${videoId}/status`, {
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Failed to get video generation status:', error);
      return null;
    }
  }

  async getVideoGenerationLimit(): Promise<VideoGenerationLimit | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/video/veo3/limit`, {
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Failed to get video generation limit:', error);
      return null;
    }
  }

  async getVideoGenerationHistory(limit: number = 10): Promise<VideoGenerationResponse[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assets/video/veo3/history?limit=${limit}`, {
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result.videos || [];
    } catch (error) {
      console.error('Failed to get video generation history:', error);
      return [];
    }
  }

  // Fallback data cuando el servidor no está disponible
  private getFallbackMetrics(): MetricsResponse {
    return {
      total_conversations: 42,
      active_projects: 8,
      tokens_used: 156789,
      system_load: 0.35,
      memory_usage: 0.68,
      last_updated: new Date().toISOString(),
      server_status: 'fallback'
    };
  }

  private getFallbackProjects(): Project[] {
    return [
      {
        id: '1',
        name: 'Proyecto React Dashboard',
        description: 'Dashboard interactivo con métricas en tiempo real',
        created_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-20T14:30:00Z',
        files_count: 24,
        conversations_count: 8,
        last_activity: '2024-01-20T14:30:00Z'
      },
      {
        id: '2',
        name: 'API REST Service',
        description: 'Microservicio con endpoints RESTful',
        created_at: '2024-01-10T09:15:00Z',
        updated_at: '2024-01-18T16:45:00Z',
        files_count: 18,
        conversations_count: 12,
        last_activity: '2024-01-18T16:45:00Z'
      }
    ];
  }

  private getFallbackTemplates(): Template[] {
    return [
      {
        id: '1',
        name: 'React Dashboard Template',
        description: 'Template completo para dashboards React',
        category: 'dashboard',
        files: [
          {
            id: '1',
            name: 'App.tsx',
            path: '/src/App.tsx',
            size: 2048,
            type: 'typescript',
            created_at: '2024-01-15T10:00:00Z',
            updated_at: '2024-01-15T10:00:00Z',
            content: 'import React from \'react\';\\nfunction App() { return <div>Dashboard</div>; }\\nexport default App;',
            project_id: 'template'
          }
        ],
        tags: ['react', 'dashboard', 'typescript'],
        created_at: '2024-01-15T10:00:00Z'
      }
    ];
  }

  private handleReconnection() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff

    setTimeout(() => {
      console.log(`Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      this.checkHealth();
    }, delay);
  }
}

// Singleton instance
export const mcpClient = new MCPClient();
export default mcpClient;