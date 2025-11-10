// Sistema de persistencia para configuraciones y datos
import { Project, FileItem, ChatMessage } from './api';

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

export interface StoredProject extends Project {
  conversations: StoredConversation[];
  files: StoredFile[];
}

export interface StoredConversation {
  id: string;
  projectId: string;
  title: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
  last_activity: string;
}

export interface StoredFile extends FileItem {
  content: string;
}

class StorageManager {
  private readonly SETTINGS_KEY = 'iris-user-settings';
  private readonly PROJECTS_KEY = 'iris-projects';
  private readonly CONVERSATIONS_KEY = 'iris-conversations';
  private readonly FILES_KEY = 'iris-files';
  private readonly RECENT_KEYS_KEY = 'iris-recent-keys';

  // Settings
  saveSettings(settings: UserSettings): void {
    try {
      localStorage.setItem(this.SETTINGS_KEY, JSON.stringify(settings));
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }

  loadSettings(): UserSettings {
    try {
      const stored = localStorage.getItem(this.SETTINGS_KEY);
      if (stored) {
        return { ...this.getDefaultSettings(), ...JSON.parse(stored) };
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
    return this.getDefaultSettings();
  }

  private getDefaultSettings(): UserSettings {
    return {
      theme: 'system',
      language: 'es',
      mcpServerUrl: 'http://localhost:8000',
      notifications: {
        email: true,
        push: true,
        desktop: true,
      },
      ai: {
        model: 'gpt-4',
        temperature: 0.7,
        maxTokens: 4000,
      },
      editor: {
        fontSize: 14,
        tabSize: 2,
        wordWrap: true,
        minimap: true,
      },
      shortcuts: {
        'save': 'Ctrl+S',
        'find': 'Ctrl+F',
        'run': 'F5',
        'terminal': 'Ctrl+`',
      },
    };
  }

  // Projects
  saveProjects(projects: Project[]): void {
    try {
      localStorage.setItem(this.PROJECTS_KEY, JSON.stringify(projects));
    } catch (error) {
      console.error('Failed to save projects:', error);
    }
  }

  loadProjects(): Project[] {
    try {
      const stored = localStorage.getItem(this.PROJECTS_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
    return [];
  }

  saveProject(project: Project): void {
    try {
      const projects = this.loadProjects();
      const existingIndex = projects.findIndex(p => p.id === project.id);
      
      if (existingIndex >= 0) {
        projects[existingIndex] = project;
      } else {
        projects.push(project);
      }
      
      localStorage.setItem(this.PROJECTS_KEY, JSON.stringify(projects));
    } catch (error) {
      console.error('Failed to save project:', error);
    }
  }

  deleteProject(projectId: string): void {
    try {
      const projects = this.loadProjects();
      const filtered = projects.filter(p => p.id !== projectId);
      localStorage.setItem(this.PROJECTS_KEY, JSON.stringify(filtered));
      
      // Also delete conversations and files for this project
      this.deleteConversationsByProject(projectId);
      this.deleteFilesByProject(projectId);
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  }

  // Conversations
  saveConversation(conversation: StoredConversation): void {
    try {
      const conversations = this.loadConversations();
      const existingIndex = conversations.findIndex(c => c.id === conversation.id);
      
      if (existingIndex >= 0) {
        conversations[existingIndex] = conversation;
      } else {
        conversations.push(conversation);
      }
      
      localStorage.setItem(this.CONVERSATIONS_KEY, JSON.stringify(conversations));
    } catch (error) {
      console.error('Failed to save conversation:', error);
    }
  }

  loadConversations(): StoredConversation[] {
    try {
      const stored = localStorage.getItem(this.CONVERSATIONS_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
    return [];
  }

  getConversationsByProject(projectId: string): StoredConversation[] {
    return this.loadConversations().filter(c => c.projectId === projectId);
  }

  deleteConversation(conversationId: string): void {
    try {
      const conversations = this.loadConversations();
      const filtered = conversations.filter(c => c.id !== conversationId);
      localStorage.setItem(this.CONVERSATIONS_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  }

  private deleteConversationsByProject(projectId: string): void {
    try {
      const conversations = this.loadConversations();
      const filtered = conversations.filter(c => c.projectId !== projectId);
      localStorage.setItem(this.CONVERSATIONS_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete project conversations:', error);
    }
  }

  // Files
  saveFile(file: StoredFile): void {
    try {
      const files = this.loadFiles();
      const existingIndex = files.findIndex(f => f.id === file.id);
      
      if (existingIndex >= 0) {
        files[existingIndex] = file;
      } else {
        files.push(file);
      }
      
      localStorage.setItem(this.FILES_KEY, JSON.stringify(files));
    } catch (error) {
      console.error('Failed to save file:', error);
    }
  }

  loadFiles(): StoredFile[] {
    try {
      const stored = localStorage.getItem(this.FILES_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('Failed to load files:', error);
    }
    return [];
  }

  getFilesByProject(projectId: string): StoredFile[] {
    return this.loadFiles().filter(f => f.project_id === projectId);
  }

  deleteFile(fileId: string): void {
    try {
      const files = this.loadFiles();
      const filtered = files.filter(f => f.id !== fileId);
      localStorage.setItem(this.FILES_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  }

  private deleteFilesByProject(projectId: string): void {
    try {
      const files = this.loadFiles();
      const filtered = files.filter(f => f.project_id !== projectId);
      localStorage.setItem(this.FILES_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete project files:', error);
    }
  }

  // Recent items
  addRecentItem(key: string, type: 'project' | 'file' | 'conversation'): void {
    try {
      const recent = this.getRecentItems();
      const existing = recent.find(item => item.key === key);
      
      if (existing) {
        existing.lastAccess = new Date().toISOString();
        existing.count += 1;
      } else {
        recent.push({
          key,
          type,
          lastAccess: new Date().toISOString(),
          count: 1
        });
      }
      
      // Sort by last access and limit to 20 items
      recent.sort((a, b) => new Date(b.lastAccess).getTime() - new Date(a.lastAccess).getTime());
      const limited = recent.slice(0, 20);
      
      localStorage.setItem(this.RECENT_KEYS_KEY, JSON.stringify(limited));
    } catch (error) {
      console.error('Failed to save recent item:', error);
    }
  }

  getRecentItems() {
    try {
      const stored = localStorage.getItem(this.RECENT_KEYS_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('Failed to load recent items:', error);
    }
    return [];
  }

  // File content search
  searchInFiles(query: string, projectId?: string): StoredFile[] {
    try {
      const files = this.loadFiles();
      const searchQuery = query.toLowerCase();
      
      return files.filter(file => {
        if (projectId && file.project_id !== projectId) {
          return false;
        }
        
        return file.content?.toLowerCase().includes(searchQuery) ||
               file.name.toLowerCase().includes(searchQuery);
      });
    } catch (error) {
      console.error('Failed to search in files:', error);
      return [];
    }
  }

  // Export/Import settings
  exportData(): string {
    try {
      const data = {
        settings: this.loadSettings(),
        projects: this.loadProjects(),
        conversations: this.loadConversations(),
        files: this.loadFiles(),
        recent: this.getRecentItems(),
        exportDate: new Date().toISOString()
      };
      return JSON.stringify(data, null, 2);
    } catch (error) {
      console.error('Failed to export data:', error);
      return '';
    }
  }

  importData(jsonData: string): boolean {
    try {
      const data = JSON.parse(jsonData);
      
      if (data.settings) this.saveSettings(data.settings);
      if (data.projects) this.saveProjects(data.projects);
      if (data.conversations) localStorage.setItem(this.CONVERSATIONS_KEY, JSON.stringify(data.conversations));
      if (data.files) localStorage.setItem(this.FILES_KEY, JSON.stringify(data.files));
      if (data.recent) localStorage.setItem(this.RECENT_KEYS_KEY, JSON.stringify(data.recent));
      
      return true;
    } catch (error) {
      console.error('Failed to import data:', error);
      return false;
    }
  }

  // Clear all data
  clearAllData(): void {
    try {
      localStorage.removeItem(this.SETTINGS_KEY);
      localStorage.removeItem(this.PROJECTS_KEY);
      localStorage.removeItem(this.CONVERSATIONS_KEY);
      localStorage.removeItem(this.FILES_KEY);
      localStorage.removeItem(this.RECENT_KEYS_KEY);
    } catch (error) {
      console.error('Failed to clear data:', error);
    }
  }

  // Get storage usage
  getStorageUsage(): { used: number; total: number; percentage: number } {
    try {
      let total = 0;
      const keys = [
        this.SETTINGS_KEY,
        this.PROJECTS_KEY,
        this.CONVERSATIONS_KEY,
        this.FILES_KEY,
        this.RECENT_KEYS_KEY
      ];

      for (const key of keys) {
        const value = localStorage.getItem(key);
        if (value) {
          total += value.length;
        }
      }

      const used = total;
      const percentage = Math.round((used / (5 * 1024 * 1024)) * 100); // Assume 5MB limit

      return {
        used,
        total: 5 * 1024 * 1024,
        percentage: Math.min(percentage, 100)
      };
    } catch (error) {
      console.error('Failed to get storage usage:', error);
      return { used: 0, total: 5 * 1024 * 1024, percentage: 0 };
    }
  }
}

export interface RecentItem {
  key: string;
  type: 'project' | 'file' | 'conversation';
  lastAccess: string;
  count: number;
}

export const storage = new StorageManager();
export default storage;