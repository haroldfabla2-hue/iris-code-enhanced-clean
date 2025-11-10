import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { mcpClient, Project as APIProject, FileItem } from '../lib/api';
import { storage, StoredFile } from '../lib/storage';
import { useAppStore } from './appStore';
import { useChatStore } from './chatStore';

interface Project extends APIProject {
  isExpanded?: boolean;
  isSelected?: boolean;
  isActive?: boolean;
}

interface FileNode extends FileItem {
  children?: FileNode[];
  isExpanded?: boolean;
  isSelected?: boolean;
  content?: string;
}

interface ProjectState {
  // Projects
  projects: Project[];
  activeProject: Project | null;
  activeProjectId: string | null;
  
  // File Management
  openFiles: FileNode[];
  activeFileId: string | null;
  fileTree: FileNode[];
  selectedFiles: Set<string>;
  
  // UI State
  viewMode: 'grid' | 'list' | 'tree';
  isLoading: boolean;
  searchQuery: string;
  sortBy: 'name' | 'date' | 'size' | 'type' | 'created' | 'activity';
  sortOrder: 'asc' | 'desc';
  
  // Actions
  setActiveProject: (projectId: string | null) => void;
  createProject: (name: string, description?: string) => Promise<string | null>;
  updateProject: (projectId: string, updates: Partial<Project>) => void;
  deleteProject: (projectId: string) => void;
  duplicateProject: (projectId: string) => Promise<string | null>;
  
  // File Operations
  loadProjects: () => Promise<void>;
  loadProjectFiles: (projectId: string) => Promise<void>;
  uploadFile: (projectId: string, file: File) => Promise<FileNode | null>;
  createFile: (projectId: string, name: string, content: string, type: string) => Promise<FileNode | null>;
  updateFile: (fileId: string, content: string) => Promise<boolean>;
  deleteFile: (fileId: string) => Promise<boolean>;
  renameFile: (fileId: string, newName: string) => Promise<boolean>;
  moveFile: (fileId: string, newPath: string) => Promise<boolean>;
  
  // File Management
  openFile: (file: FileNode) => void;
  closeFile: (fileId: string) => void;
  saveFile: (fileId: string) => Promise<boolean>;
  saveAllFiles: () => Promise<boolean>;
  
  // File Tree Operations
  toggleFileExpansion: (fileId: string) => void;
  selectFile: (fileId: string, multiSelect?: boolean) => void;
  selectMultipleFiles: (fileIds: string[]) => void;
  clearFileSelection: () => void;
  getFileById: (fileId: string) => FileNode | null;
  getFilePath: (fileId: string) => string;
  
  // Search and Filter
  setSearchQuery: (query: string) => void;
  setSortBy: (sortBy: 'name' | 'date' | 'size' | 'type' | 'created' | 'activity') => void;
  setSortOrder: (order: 'asc' | 'desc') => void;
  setViewMode: (mode: 'grid' | 'list' | 'tree') => void;
  getFilteredFiles: () => FileNode[];
  
  // Import/Export
  exportProject: (projectId: string) => Promise<string>;
  importProject: (projectData: string) => Promise<string | null>;
  
  // Quick Actions
  addProject: (name: string, description?: string) => Promise<string | null>;
  filterBy: string;
  setFilterBy: (filter: string) => void;
  
  // Sync with storage
  syncWithStorage: () => void;
  saveProjectToStorage: (project: Project) => void;
  loadProjectsFromStorage: () => void;
  
  // Helper methods
  buildFileTree: (files: FileNode[]) => FileNode[];
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      // Initial State
      projects: [],
      activeProject: null,
      activeProjectId: null,
      
      openFiles: [],
      activeFileId: null,
      fileTree: [],
      selectedFiles: new Set(),
      
      viewMode: 'tree',
      isLoading: false,
      searchQuery: '',
      sortBy: 'name',
      sortOrder: 'asc',
      
      // Quick Actions
      addProject: async (name, description) => {
        return await get().createProject(name, description);
      },
      
      filterBy: 'all',
      setFilterBy: (filter) => {
        set({ filterBy: filter });
      },
      
      // Actions
      setActiveProject: (projectId) => {
        const { projects } = get();
        const project = projects.find(p => p.id === projectId) || null;
        set({ 
          activeProject: project,
          activeProjectId: projectId,
        });
        
        // Load project files
        if (projectId) {
          get().loadProjectFiles(projectId);
        }
        
        // Update chat context
        const chatStore = useChatStore.getState();
        chatStore.setContext({
          projectId: projectId,
          conversationId: chatStore.activeConversationId,
        });
      },
      
      createProject: async (name, description) => {
        const appStore = useAppStore.getState();
        
        try {
          set({ isLoading: true });
          
          // Try to create via MCP Server
          const createdProject = await mcpClient.createProject(name, description);
          
          if (createdProject) {
            const project: Project = {
              ...createdProject,
              isExpanded: false,
              isSelected: false,
              isActive: true,
            };
            
            set(state => ({
              projects: [project, ...state.projects],
              activeProject: project,
              activeProjectId: project.id,
              fileTree: [],
              openFiles: [],
            }));
            
            // Save to storage
            storage.saveProject(project);
            
            appStore.addNotification({
              type: 'success',
              title: 'Proyecto creado',
              message: `El proyecto "${name}" ha sido creado exitosamente`,
              isRead: false,
            });
            
            return project.id;
          } else {
            // Fallback: create locally
            const projectId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
            const project: Project = {
              id: projectId,
              name,
              description: description || '',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              files_count: 0,
              conversations_count: 0,
              last_activity: new Date().toISOString(),
              isExpanded: false,
              isSelected: false,
              isActive: true,
            };
            
            set(state => ({
              projects: [project, ...state.projects],
              activeProject: project,
              activeProjectId: project.id,
              fileTree: [],
              openFiles: [],
            }));
            
            storage.saveProject(project);
            
            appStore.addNotification({
              type: 'info',
              title: 'Proyecto creado localmente',
              message: `El proyecto "${name}" ha sido creado en modo local (sin conexión al servidor)`,
              isRead: false,
            });
            
            return project.id;
          }
        } catch (error) {
          console.error('Failed to create project:', error);
          
          appStore.addNotification({
            type: 'error',
            title: 'Error al crear proyecto',
            message: 'No se pudo crear el proyecto. Verifica la conexión con el servidor.',
            isRead: false,
          });
          
          return null;
        } finally {
          set({ isLoading: false });
        }
      },
      
      updateProject: (projectId, updates) => {
        set(state => ({
          projects: state.projects.map(p => 
            p.id === projectId 
              ? { ...p, ...updates, updated_at: new Date().toISOString() }
              : p
          ),
          activeProject: state.activeProject?.id === projectId
            ? { ...state.activeProject, ...updates, updated_at: new Date().toISOString() }
            : state.activeProject
        }));
        
        // Save to storage
        const project = get().projects.find(p => p.id === projectId);
        if (project) {
          storage.saveProject(project);
        }
      },
      
      deleteProject: async (projectId) => {
        const appStore = useAppStore.getState();
        
        try {
          set({ isLoading: true });
          
          // Remove from state
          set(state => ({
            projects: state.projects.filter(p => p.id !== projectId),
            activeProject: state.activeProject?.id === projectId ? null : state.activeProject,
            activeProjectId: state.activeProjectId === projectId ? null : state.activeProjectId,
          }));
          
          // Delete from storage
          storage.deleteProject(projectId);
          
          // Close any open files from this project
          set(state => ({
            openFiles: state.openFiles.filter(f => f.project_id !== projectId),
            fileTree: [],
          }));
          
          appStore.addNotification({
            type: 'info',
            title: 'Proyecto eliminado',
            message: 'El proyecto ha sido eliminado exitosamente',
            isRead: true,
          });
        } catch (error) {
          console.error('Failed to delete project:', error);
          
          appStore.addNotification({
            type: 'error',
            title: 'Error al eliminar proyecto',
            message: 'No se pudo eliminar el proyecto',
            isRead: false,
          });
        } finally {
          set({ isLoading: false });
        }
      },
      
      duplicateProject: async (projectId) => {
        const { projects, fileTree, openFiles } = get();
        const project = projects.find(p => p.id === projectId);
        
        if (!project) return null;
        
        const newProjectId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
        const newName = `${project.name} (Copia)`;
        
        const newProject: Project = {
          ...project,
          id: newProjectId,
          name: newName,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_activity: new Date().toISOString(),
          isExpanded: false,
          isSelected: false,
        };
        
        // Duplicate files
        const projectFiles = fileTree.filter(f => f.project_id === projectId);
        const duplicatedFiles: FileNode[] = projectFiles.map(file => ({
          ...file,
          id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
          project_id: newProjectId,
        }));
        
        set(state => ({
          projects: [newProject, ...state.projects],
        }));
        
        // Save to storage
        storage.saveProject(newProject);
        duplicatedFiles.forEach(file => {
          storage.saveFile(file as StoredFile);
        });
        
        return newProjectId;
      },
      
      loadProjects: async () => {
        const appStore = useAppStore.getState();
        
        try {
          set({ isLoading: true });
          
          // Load from storage first
          get().loadProjectsFromStorage();
          
          // Try to sync with server
          if (appStore.isConnected) {
            const serverProjects = await mcpClient.getProjects();
            
            if (serverProjects && serverProjects.length > 0) {
              const updatedProjects: Project[] = serverProjects.map(p => ({
                ...p,
                isExpanded: false,
                isSelected: false,
                isActive: true,
              }));
              
              set({ projects: updatedProjects });
              
              // Save to storage
              storage.saveProjects(serverProjects);
            }
          }
        } catch (error) {
          console.error('Failed to load projects:', error);
        } finally {
          set({ isLoading: false });
        }
      },
      
      loadProjectFiles: async (projectId) => {
        try {
          const projectFiles = await mcpClient.getProjectFiles(projectId);
          
          // Convert to FileNode format and add to tree
          const fileNodes: FileNode[] = projectFiles.map(file => ({
            ...file,
            isExpanded: false,
            isSelected: false,
          }));
          
          // Build file tree structure
          const tree = get().buildFileTree(fileNodes);
          
          set({ fileTree: tree });
        } catch (error) {
          console.error('Failed to load project files:', error);
          
          // Fallback: load from storage
          const storedFiles = storage.getFilesByProject(projectId);
          const fileNodes: FileNode[] = storedFiles.map(file => ({
            ...file,
            isExpanded: false,
            isSelected: false,
          }));
          
          const tree = get().buildFileTree(fileNodes);
          set({ fileTree: tree });
        }
      },
      
      uploadFile: async (projectId, file) => {
        try {
          const uploadedFile = await mcpClient.uploadFile(projectId, file);
          
          if (uploadedFile) {
            const fileNode: FileNode = {
              ...uploadedFile,
              isExpanded: false,
              isSelected: false,
            };
            
            // Add to file tree
            set(state => ({
              fileTree: [...state.fileTree, fileNode],
            }));
            
            // Save to storage
            storage.saveFile(fileNode as StoredFile);
            
            return fileNode;
          }
          
          return null;
        } catch (error) {
          console.error('Failed to upload file:', error);
          return null;
        }
      },
      
      createFile: async (projectId, name, content, type) => {
        try {
          // Create file locally first
          const fileId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
          const fileNode: FileNode = {
            id: fileId,
            name,
            path: `/${name}`,
            size: content.length,
            type,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            content,
            project_id: projectId,
            isExpanded: false,
            isSelected: false,
          };
          
          // Try to save to server
          const saved = await mcpClient.saveFile(fileId, content);
          
          if (saved) {
            set(state => ({
              fileTree: [...state.fileTree, fileNode],
            }));
            
            storage.saveFile(fileNode as StoredFile);
            return fileNode;
          }
          
          return null;
        } catch (error) {
          console.error('Failed to create file:', error);
          return null;
        }
      },
      
      updateFile: async (fileId, content) => {
        try {
          // Update in storage first
          const { fileTree } = get();
          const file = fileTree.find(f => f.id === fileId);
          
          if (!file) return false;
          
          const updatedFile = {
            ...file,
            content,
            size: content.length,
            updated_at: new Date().toISOString(),
          };
          
          // Update in tree
          set(state => ({
            fileTree: state.fileTree.map(f => f.id === fileId ? updatedFile : f),
            openFiles: state.openFiles.map(f => f.id === fileId ? updatedFile : f),
          }));
          
          // Save to storage
          storage.saveFile(updatedFile as StoredFile);
          
          // Try to save to server
          const serverSaved = await mcpClient.saveFile(fileId, content);
          
          return serverSaved !== false;
        } catch (error) {
          console.error('Failed to update file:', error);
          return false;
        }
      },
      
      deleteFile: async (fileId) => {
        try {
          set(state => ({
            fileTree: state.fileTree.filter(f => f.id !== fileId),
            openFiles: state.openFiles.filter(f => f.id !== fileId),
            activeFileId: state.activeFileId === fileId ? null : state.activeFileId,
          }));
          
          storage.deleteFile(fileId);
          return true;
        } catch (error) {
          console.error('Failed to delete file:', error);
          return false;
        }
      },
      
      renameFile: async (fileId, newName) => {
        try {
          const { fileTree } = get();
          const file = fileTree.find(f => f.id === fileId);
          
          if (!file) return false;
          
          const pathParts = file.path.split('/');
          pathParts[pathParts.length - 1] = newName;
          const newPath = pathParts.join('/');
          
          const updatedFile = {
            ...file,
            name: newName,
            path: newPath,
            updated_at: new Date().toISOString(),
          };
          
          set(state => ({
            fileTree: state.fileTree.map(f => f.id === fileId ? updatedFile : f),
            openFiles: state.openFiles.map(f => f.id === fileId ? updatedFile : f),
          }));
          
          storage.saveFile(updatedFile as StoredFile);
          return true;
        } catch (error) {
          console.error('Failed to rename file:', error);
          return false;
        }
      },
      
      moveFile: async (fileId, newPath) => {
        try {
          const { fileTree } = get();
          const file = fileTree.find(f => f.id === fileId);
          
          if (!file) return false;
          
          const updatedFile = {
            ...file,
            path: newPath,
            name: newPath.split('/').pop() || file.name,
            updated_at: new Date().toISOString(),
          };
          
          set(state => ({
            fileTree: state.fileTree.map(f => f.id === fileId ? updatedFile : f),
            openFiles: state.openFiles.map(f => f.id === fileId ? updatedFile : f),
          }));
          
          storage.saveFile(updatedFile as StoredFile);
          return true;
        } catch (error) {
          console.error('Failed to move file:', error);
          return false;
        }
      },
      
      openFile: (file) => {
        const { openFiles } = get();
        const alreadyOpen = openFiles.find(f => f.id === file.id);
        
        if (!alreadyOpen) {
          set(state => ({
            openFiles: [...state.openFiles, file],
            activeFileId: file.id,
          }));
        } else {
          set({ activeFileId: file.id });
        }
        
        // Mark as selected
        get().selectFile(file.id);
        
        // Add to recent items
        storage.addRecentItem(file.id, 'file');
      },
      
      closeFile: (fileId) => {
        set(state => ({
          openFiles: state.openFiles.filter(f => f.id !== fileId),
          activeFileId: state.activeFileId === fileId 
            ? (state.openFiles.length > 1 ? state.openFiles[0].id : null)
            : state.activeFileId,
        }));
      },
      
      saveFile: async (fileId) => {
        const { openFiles } = get();
        const file = openFiles.find(f => f.id === fileId);
        
        if (!file || !file.content) return false;
        
        return await get().updateFile(fileId, file.content);
      },
      
      saveAllFiles: async () => {
        const { openFiles } = get();
        const results = await Promise.all(
          openFiles.map(file => 
            file.content ? get().updateFile(file.id, file.content) : Promise.resolve(false)
          )
        );
        
        return results.every(result => result);
      },
      
      toggleFileExpansion: (fileId) => {
        set(state => ({
          fileTree: state.fileTree.map(f => 
            f.id === fileId ? { ...f, isExpanded: !f.isExpanded } : f
          ),
        }));
      },
      
      selectFile: (fileId, multiSelect = false) => {
        set(state => {
          const newSelected = new Set(state.selectedFiles);
          
          if (multiSelect) {
            if (newSelected.has(fileId)) {
              newSelected.delete(fileId);
            } else {
              newSelected.add(fileId);
            }
          } else {
            newSelected.clear();
            newSelected.add(fileId);
          }
          
          return { selectedFiles: newSelected };
        });
      },
      
      selectMultipleFiles: (fileIds) => {
        set({ selectedFiles: new Set(fileIds) });
      },
      
      clearFileSelection: () => {
        set({ selectedFiles: new Set() });
      },
      
      getFileById: (fileId) => {
        const { fileTree, openFiles } = get();
        
        // Check open files first
        const openFile = openFiles.find(f => f.id === fileId);
        if (openFile) return openFile;
        
        // Search in file tree
        const searchInTree = (nodes: FileNode[]): FileNode | null => {
          for (const node of nodes) {
            if (node.id === fileId) return node;
            if (node.children) {
              const found = searchInTree(node.children);
              if (found) return found;
            }
          }
          return null;
        };
        
        return searchInTree(fileTree);
      },
      
      getFilePath: (fileId) => {
        const file = get().getFileById(fileId);
        return file?.path || '';
      },
      
      setSearchQuery: (query) => {
        set({ searchQuery: query });
      },
      
      setSortBy: (sortBy) => {
        set({ sortBy });
      },
      
      setSortOrder: (sortOrder) => {
        set({ sortOrder });
      },
      
      setViewMode: (mode) => {
        set({ viewMode: mode });
      },
      
      getFilteredFiles: () => {
        const { fileTree, searchQuery, sortBy, sortOrder } = get();
        
        let files: FileNode[] = [];
        
        const collectFiles = (nodes: FileNode[]): void => {
          for (const node of nodes) {
            files.push(node);
            if (node.children) {
              collectFiles(node.children);
            }
          }
        };
        
        collectFiles(fileTree);
        
        // Filter by search query
        if (searchQuery) {
          const query = searchQuery.toLowerCase();
          files = files.filter(file => 
            file.name.toLowerCase().includes(query) ||
            file.path.toLowerCase().includes(query) ||
            file.content?.toLowerCase().includes(query)
          );
        }
        
        // Sort files
        files.sort((a, b) => {
          let comparison = 0;
          
          switch (sortBy) {
            case 'name':
              comparison = a.name.localeCompare(b.name);
              break;
            case 'date':
              comparison = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
              break;
            case 'size':
              comparison = a.size - b.size;
              break;
            case 'type':
              comparison = a.type.localeCompare(b.type);
              break;
          }
          
          return sortOrder === 'asc' ? comparison : -comparison;
        });
        
        return files;
      },
      
      exportProject: async (projectId) => {
        const { projects, fileTree } = get();
        const project = projects.find(p => p.id === projectId);
        const projectFiles = fileTree.filter(f => f.project_id === projectId);
        
        if (!project) return '';
        
        const exportData = {
          project,
          files: projectFiles,
          exportedAt: new Date().toISOString(),
          version: '1.0',
        };
        
        return JSON.stringify(exportData, null, 2);
      },
      
      importProject: async (projectData) => {
        try {
          const data = JSON.parse(projectData);
          const project = data.project as Project;
          const files = data.files as FileNode[];
          
          if (!project || !files) return null;
          
          // Generate new IDs to avoid conflicts
          const newProjectId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
          
          const newProject: Project = {
            ...project,
            id: newProjectId,
            name: `${project.name} (Importado)`,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            last_activity: new Date().toISOString(),
          };
          
          const newFiles = files.map(file => ({
            ...file,
            id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
            project_id: newProjectId,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }));
          
          set(state => ({
            projects: [newProject, ...state.projects],
            fileTree: [...state.fileTree, ...newFiles],
          }));
          
          storage.saveProject(newProject);
          newFiles.forEach(file => {
            storage.saveFile(file as StoredFile);
          });
          
          return newProjectId;
        } catch (error) {
          console.error('Failed to import project:', error);
          return null;
        }
      },
      
      syncWithStorage: () => {
        get().loadProjectsFromStorage();
      },
      
      saveProjectToStorage: (project) => {
        storage.saveProject(project);
      },
      
      loadProjectsFromStorage: () => {
        const storedProjects = storage.loadProjects();
        const projects: Project[] = storedProjects.map(p => ({
          ...p,
          isExpanded: false,
          isSelected: false,
        }));
        
        set({ projects });
      },
      
      // Helper method to build file tree structure
      buildFileTree: (files: FileNode[]): FileNode[] => {
        const tree: FileNode[] = [];
        const fileMap = new Map<string, FileNode>();
        
        // Create map of all files
        files.forEach(file => {
          fileMap.set(file.path, { ...file, children: [] });
        });
        
        // Build tree structure
        files.forEach(file => {
          const pathParts = file.path.split('/').filter(Boolean);
          const fileName = pathParts[pathParts.length - 1];
          const parentPath = pathParts.slice(0, -1).join('/');
          
          if (parentPath) {
            const parent = fileMap.get(parentPath);
            if (parent) {
              parent.children = parent.children || [];
              parent.children.push(fileMap.get(file.path)!);
            }
          } else {
            tree.push(fileMap.get(file.path)!);
          }
        });
        
        return tree;
      },
    }),
    {
      name: 'iris-project-store',
      partialize: (state) => ({
        projects: state.projects,
        activeProjectId: state.activeProjectId,
        viewMode: state.viewMode,
        sortBy: state.sortBy,
        sortOrder: state.sortOrder,
      }),
    }
  )
);

// Initialize projects on load
if (typeof window !== 'undefined') {
  setTimeout(() => {
    const store = useProjectStore.getState();
    store.loadProjects();
  }, 1500);
}