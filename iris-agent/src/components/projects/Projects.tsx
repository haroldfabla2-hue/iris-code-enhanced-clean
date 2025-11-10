import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjectStore } from '../../stores/projectStore';
import { 
  Plus, 
  Search, 
  Filter, 
  Grid, 
  List, 
  FolderOpen, 
  MoreVertical, 
  Calendar, 
  FileText, 
  MessageSquare,
  Star,
  Archive,
  Trash2,
  Edit,
  Share,
  Clock,
  Zap
} from 'lucide-react';
import { cn } from '../../lib/utils';

const Projects: React.FC = () => {
  const navigate = useNavigate();
  const { 
    projects, 
    activeProject, 
    setActiveProject, 
    addProject,
    updateProject,
    deleteProject,
    searchQuery,
    setSearchQuery,
    sortBy,
    setSortBy,
    filterBy,
    setFilterBy
  } = useProjectStore();

  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: ''
  });

  // Handler para abrir Live Preview
  const handleLivePreview = (project: any, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevenir que se active el click en la tarjeta
    navigate(`/live-preview/${project.id}`);
  };

  // Handler para editar proyecto
  const handleEditProject = (project: any, e: React.MouseEvent) => {
    e.stopPropagation();
    // Aquí se implementaría la lógica de edición
    console.log('Edit project:', project.id);
  };

  // Handler para compartir proyecto
  const handleShareProject = (project: any, e: React.MouseEvent) => {
    e.stopPropagation();
    // Aquí se implementaría la lógica de compartir
    console.log('Share project:', project.id);
  };

  const filteredProjects = projects
    .filter(project => {
      if (searchQuery && !project.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !project.description.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      if (filterBy === 'active') {
        return project.isActive;
      }
      if (filterBy === 'recent') {
        const daysDiff = (Date.now() - new Date(project.updated_at).getTime()) / (1000 * 60 * 60 * 24);
        return daysDiff <= 7;
      }
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'created':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'date':
        case 'activity':
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        case 'size':
          return a.files_count - b.files_count;
        case 'type':
          return 0; // Projects don't have a type property
        default:
          return 0;
      }
    });

  const handleCreateProject = () => {
    if (!newProject.name.trim()) return;

    addProject(newProject.name, newProject.description);
    setNewProject({ name: '', description: '' });
    setShowNewProject(false);
  };

  const ProjectCard: React.FC<{
    project: any;
    onSelect?: () => void;
  }> = ({ project, onSelect }) => (
    <div 
      className="iris-card-hover p-6 cursor-pointer group relative"
      onClick={onSelect}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center">
          <FolderOpen className="w-6 h-6 text-white" />
        </div>
        <div className="flex items-center space-x-1">
          {project.isActive && (
            <div className="w-2 h-2 bg-semantic-success rounded-full" title="Proyecto activo" />
          )}
          <button className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700">
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-1">
            {project.name}
          </h3>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 line-clamp-2">
            {project.description}
          </p>
        </div>

        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4 text-neutral-500">
            <span className="flex items-center gap-1">
              <FileText className="w-4 h-4" />
              {project.files}
            </span>
            <span className="flex items-center gap-1">
              <MessageSquare className="w-4 h-4" />
              {project.conversations}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-neutral-500">
            <Clock className="w-3 h-3" />
            <span>{project.lastActivity}</span>
          </div>
          <div className="flex items-center space-x-1">
            <button 
              onClick={(e) => handleLivePreview(project, e)}
              className="p-1 rounded hover:bg-yellow-200 dark:hover:bg-yellow-800 opacity-0 group-hover:opacity-100 transition-colors"
              title="Live Preview"
            >
              <Zap className="w-4 h-4 text-yellow-600" />
            </button>
            <button className="p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 opacity-0 group-hover:opacity-100">
              <Star className="w-4 h-4" />
            </button>
            <button 
              onClick={(e) => handleShareProject(project, e)}
              className="p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 opacity-0 group-hover:opacity-100"
            >
              <Share className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const ProjectListItem: React.FC<{
    project: any;
    onSelect?: () => void;
  }> = ({ project, onSelect }) => (
    <div 
      className="flex items-center justify-between p-4 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 rounded-lg cursor-pointer group"
      onClick={onSelect}
    >
      <div className="flex items-center space-x-4 flex-1 min-w-0">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center flex-shrink-0">
          <FolderOpen className="w-5 h-5 text-white" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <h3 className="font-medium text-neutral-900 dark:text-neutral-100 truncate">
              {project.name}
            </h3>
            {project.isActive && (
              <div className="w-2 h-2 bg-semantic-success rounded-full flex-shrink-0" />
            )}
          </div>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 truncate">
            {project.description}
          </p>
          <div className="flex items-center space-x-4 mt-1 text-xs text-neutral-500">
            <span className="flex items-center gap-1">
              <FileText className="w-3 h-3" />
              {project.files} archivos
            </span>
            <span className="flex items-center gap-1">
              <MessageSquare className="w-3 h-3" />
              {project.conversations} chats
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {project.lastActivity}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <button 
          onClick={(e) => handleLivePreview(project, e)}
          className="p-1 rounded hover:bg-yellow-200 dark:hover:bg-yellow-800 opacity-0 group-hover:opacity-100 transition-colors"
          title="Live Preview"
        >
          <Zap className="w-4 h-4 text-yellow-600" />
        </button>
        <button 
          onClick={(e) => handleEditProject(project, e)}
          className="p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 opacity-0 group-hover:opacity-100"
        >
          <Edit className="w-4 h-4" />
        </button>
        <button className="p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 opacity-0 group-hover:opacity-100">
          <MoreVertical className="w-4 h-4" />
        </button>
      </div>
    </div>
  );

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-title font-bold text-neutral-900 dark:text-neutral-100 mb-2">
              Proyectos
            </h1>
            <p className="text-body-large text-neutral-600 dark:text-neutral-400">
              Organiza y administra todos tus proyectos de desarrollo
            </p>
          </div>
          
          <button 
            onClick={() => setShowNewProject(true)}
            className="iris-button-primary"
          >
            <Plus className="w-5 h-5 mr-2" />
            Nuevo Proyecto
          </button>
        </div>

        {/* Controls */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          {/* Search and Filter */}
          <div className="flex items-center space-x-4 flex-1">
            <div className="relative max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <input
                type="text"
                placeholder="Buscar proyectos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full h-10 pl-10 pr-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500 focus:bg-background transition-all"
              />
            </div>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="h-10 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500"
            >
              <option value="activity">Última actividad</option>
              <option value="name">Nombre</option>
              <option value="created">Fecha de creación</option>
            </select>

            <div className="flex space-x-1">
              {(['all', 'recent', 'active'] as const).map((filter) => (
                <button
                  key={filter}
                  onClick={() => setFilterBy(filter)}
                  className={cn(
                    "px-3 py-1.5 text-sm font-medium rounded-lg transition-colors",
                    filterBy === filter
                      ? "bg-brand-500 text-white"
                      : "hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-600 dark:text-neutral-400"
                  )}
                >
                  {filter === 'all' ? 'Todos' : filter === 'recent' ? 'Recientes' : 'Activos'}
                </button>
              ))}
            </div>
          </div>

          {/* View Toggle */}
          <div className="flex items-center space-x-2 bg-neutral-100 dark:bg-neutral-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                "p-2 rounded transition-colors",
                viewMode === 'grid' 
                  ? "bg-white dark:bg-neutral-700 shadow-sm" 
                  : "hover:bg-neutral-200 dark:hover:bg-neutral-700"
              )}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                "p-2 rounded transition-colors",
                viewMode === 'list' 
                  ? "bg-white dark:bg-neutral-700 shadow-sm" 
                  : "hover:bg-neutral-200 dark:hover:bg-neutral-700"
              )}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Projects Grid/List */}
      {filteredProjects.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-neutral-100 dark:bg-neutral-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FolderOpen className="w-8 h-8 text-neutral-400" />
          </div>
          <h3 className="text-lg font-medium text-neutral-600 dark:text-neutral-400 mb-2">
            {searchQuery ? 'No se encontraron proyectos' : 'No hay proyectos'}
          </h3>
          <p className="text-neutral-500 mb-6">
            {searchQuery 
              ? 'Intenta con otros términos de búsqueda'
              : 'Crea tu primer proyecto para comenzar'
            }
          </p>
          {!searchQuery && (
            <button 
              onClick={() => setShowNewProject(true)}
              className="iris-button-primary"
            >
              <Plus className="w-5 h-5 mr-2" />
              Crear Proyecto
            </button>
          )}
        </div>
      ) : (
        <div className={cn(
          viewMode === 'grid' 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            : "space-y-3"
        )}>
          {filteredProjects.map((project) => (
            viewMode === 'grid' ? (
              <ProjectCard
                key={project.id}
                project={project}
                onSelect={() => setActiveProject(project.id)}
              />
            ) : (
              <ProjectListItem
                key={project.id}
                project={project}
                onSelect={() => setActiveProject(project.id)}
              />
            )
          ))}
        </div>
      )}

      {/* New Project Modal */}
      {showNewProject && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="iris-card w-full max-w-md m-4 p-6">
            <h2 className="text-title font-semibold mb-6">Nuevo Proyecto</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nombre del proyecto</label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  placeholder="Mi proyecto"
                  className="w-full h-12 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500 focus:bg-background transition-all"
                  autoFocus
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Descripción (opcional)</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  placeholder="Descripción del proyecto..."
                  rows={3}
                  className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500 focus:bg-background transition-all resize-none"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowNewProject(false);
                  setNewProject({ name: '', description: '' });
                }}
                className="iris-button-secondary"
              >
                Cancelar
              </button>
              <button
                onClick={handleCreateProject}
                disabled={!newProject.name.trim()}
                className="iris-button-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Crear Proyecto
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Projects;