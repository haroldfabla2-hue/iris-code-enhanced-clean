import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  Search, 
  Filter, 
  Grid, 
  List, 
  FileText, 
  Image, 
  Video, 
  Music, 
  Archive,
  Download,
  Trash2,
  Copy,
  MoreVertical,
  FolderPlus,
  FilePlus,
  SortAsc,
  SortDesc,
  Calendar,
  HardDrive
} from 'lucide-react';
import { cn } from '../../lib/utils';

const Files: React.FC = () => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterBy, setFilterBy] = useState<'all' | 'images' | 'documents' | 'code' | 'media'>('all');
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

  // Mock files data
  const files = [
    { id: '1', name: 'project-architecture.png', type: 'image', size: '2.4 MB', date: '2024-11-05', path: '/images/project-architecture.png' },
    { name: 'requirements.md', type: 'document', size: '12 KB', date: '2024-11-04', path: '/docs/requirements.md' },
    { name: 'App.tsx', type: 'code', size: '3.2 KB', date: '2024-11-05', path: '/src/App.tsx' },
    { name: 'dashboard-demo.mp4', type: 'video', size: '45.6 MB', date: '2024-11-03', path: '/videos/dashboard-demo.mp4' },
    { name: 'design-system.pdf', type: 'document', size: '8.9 MB', date: '2024-11-02', path: '/docs/design-system.pdf' },
    { name: 'components.zip', type: 'archive', size: '15.3 MB', date: '2024-11-01', path: '/archives/components.zip' },
    { name: 'interface-sound.mp3', type: 'audio', size: '3.7 MB', date: '2024-10-31', path: '/audio/interface-sound.mp3' },
  ];

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'image': return Image;
      case 'video': return Video;
      case 'audio': return Music;
      case 'archive': return Archive;
      case 'document': return FileText;
      case 'code': return FileText;
      default: return FileText;
    }
  };

  const getFileColor = (type: string) => {
    switch (type) {
      case 'image': return 'text-green-500';
      case 'video': return 'text-blue-500';
      case 'audio': return 'text-purple-500';
      case 'document': return 'text-red-500';
      case 'code': return 'text-yellow-500';
      case 'archive': return 'text-orange-500';
      default: return 'text-gray-500';
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    console.log('Files uploaded:', acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': [],
      'video/*': [],
      'audio/*': [],
      'application/pdf': [],
      'text/*': [],
    }
  } as any);

  const FileCard: React.FC<{
    file: any;
    onSelect?: () => void;
  }> = ({ file, onSelect }) => {
    const Icon = getFileIcon(file.type);
    const isSelected = selectedFiles.includes(file.id);

    return (
      <div 
        className={cn(
          "iris-card-hover p-4 cursor-pointer relative group",
          isSelected && "ring-2 ring-brand-500"
        )}
        onClick={onSelect}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="w-12 h-12 rounded-xl bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
            <Icon className={cn("w-6 h-6", getFileColor(file.type))} />
          </div>
          <button className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700">
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-2">
          <h3 className="font-medium text-sm truncate">{file.name}</h3>
          <div className="text-xs text-neutral-500 space-y-1">
            <div>{file.size}</div>
            <div>{file.date}</div>
          </div>
        </div>

        {isSelected && (
          <div className="absolute top-2 right-2 w-5 h-5 bg-brand-500 rounded-full flex items-center justify-center">
            <div className="w-2 h-2 bg-white rounded-full" />
          </div>
        )}
      </div>
    );
  };

  const FileListItem: React.FC<{
    file: any;
    onSelect?: () => void;
  }> = ({ file, onSelect }) => {
    const Icon = getFileIcon(file.type);
    const isSelected = selectedFiles.includes(file.id);

    return (
      <div 
        className={cn(
          "flex items-center space-x-4 p-3 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 rounded-lg cursor-pointer",
          isSelected && "bg-brand-50 dark:bg-brand-900/20"
        )}
        onClick={onSelect}
      >
        <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center flex-shrink-0">
          <Icon className={cn("w-5 h-5", getFileColor(file.type))} />
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-sm text-neutral-900 dark:text-neutral-100 truncate">
            {file.name}
          </h3>
          <p className="text-xs text-neutral-500 truncate">
            {file.type} • {file.size}
          </p>
        </div>

        <div className="flex items-center space-x-4 text-xs text-neutral-500">
          <span>{file.date}</span>
          <button className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700">
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-title font-bold text-neutral-900 dark:text-neutral-100 mb-2">
              Gestor de Archivos
            </h1>
            <p className="text-body-large text-neutral-600 dark:text-neutral-400">
              Organiza, sube y gestiona todos tus archivos
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button className="iris-button-secondary">
              <FolderPlus className="w-4 h-4 mr-2" />
              Nueva Carpeta
            </button>
            <button className="iris-button-secondary">
              <FilePlus className="w-4 h-4 mr-2" />
              Subir Archivos
            </button>
          </div>
        </div>

        {/* Upload Zone */}
        <div 
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer",
            isDragActive 
              ? "border-brand-500 bg-brand-50 dark:bg-brand-900/20" 
              : "border-neutral-300 dark:border-neutral-600 hover:border-brand-400"
          )}
        >
          <input {...(getInputProps() as any)} />
          <Upload className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">
            {isDragActive ? 'Suelta los archivos aquí' : 'Arrastra archivos aquí o haz clic para seleccionar'}
          </h3>
          <p className="text-neutral-500">
            Soporte para imágenes, videos, documentos, código y más
          </p>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between mb-8">
        <div className="flex items-center space-x-4 flex-1">
          {/* Search */}
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <input
              type="text"
              placeholder="Buscar archivos..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-10 pl-10 pr-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500 focus:bg-background transition-all"
            />
          </div>

          {/* Filters */}
          <select
            value={filterBy}
            onChange={(e) => setFilterBy(e.target.value as any)}
            className="h-10 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500"
          >
            <option value="all">Todos los archivos</option>
            <option value="images">Imágenes</option>
            <option value="documents">Documentos</option>
            <option value="code">Código</option>
            <option value="media">Media</option>
          </select>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="h-10 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500"
          >
            <option value="date">Fecha</option>
            <option value="name">Nombre</option>
            <option value="size">Tamaño</option>
          </select>
        </div>

        {/* View Toggle & Actions */}
        <div className="flex items-center space-x-3">
          {selectedFiles.length > 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-neutral-500">
                {selectedFiles.length} seleccionado{selectedFiles.length > 1 ? 's' : ''}
              </span>
              <button className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Descargar">
                <Download className="w-4 h-4" />
              </button>
              <button className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Copiar">
                <Copy className="w-4 h-4" />
              </button>
              <button className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 text-semantic-error" title="Eliminar">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          )}
          
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

      {/* Storage Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="iris-card p-6">
          <div className="flex items-center justify-between mb-4">
            <HardDrive className="w-8 h-8 text-brand-500" />
            <span className="text-sm text-neutral-500">Actualizado hace 5 min</span>
          </div>
          <h3 className="text-lg font-semibold mb-1">Almacenamiento</h3>
          <p className="text-2xl font-bold mb-2">2.4 GB / 5 GB</p>
          <div className="w-full bg-neutral-200 rounded-full h-2">
            <div className="bg-brand-500 h-2 rounded-full" style={{ width: '48%' }} />
          </div>
        </div>
        
        <div className="iris-card p-6">
          <div className="flex items-center justify-between mb-4">
            <FileText className="w-8 h-8 text-semantic-success" />
          </div>
          <h3 className="text-lg font-semibold mb-1">Archivos Totales</h3>
          <p className="text-2xl font-bold">{files.length}</p>
          <p className="text-sm text-neutral-500">En 3 carpetas</p>
        </div>
        
        <div className="iris-card p-6">
          <div className="flex items-center justify-between mb-4">
            <Calendar className="w-8 h-8 text-semantic-warning" />
          </div>
          <h3 className="text-lg font-semibold mb-1">Esta Semana</h3>
          <p className="text-2xl font-bold">12</p>
          <p className="text-sm text-neutral-500">Archivos subidos</p>
        </div>
      </div>

      {/* Files Grid/List */}
      {files.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-neutral-600 dark:text-neutral-400 mb-2">
            No hay archivos
          </h3>
          <p className="text-neutral-500 mb-6">
            Comienza subiendo tus primeros archivos
          </p>
        </div>
      ) : (
        <div className={cn(
          viewMode === 'grid' 
            ? "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
            : "space-y-2"
        )}>
          {files.map((file) => (
            viewMode === 'grid' ? (
              <FileCard
                key={file.id}
                file={file}
                onSelect={() => {
                  setSelectedFiles(prev => 
                    prev.includes(file.id) 
                      ? prev.filter(id => id !== file.id)
                      : [...prev, file.id]
                  );
                }}
              />
            ) : (
              <FileListItem
                key={file.id}
                file={file}
                onSelect={() => {
                  setSelectedFiles(prev => 
                    prev.includes(file.id) 
                      ? prev.filter(id => id !== file.id)
                      : [...prev, file.id]
                  );
                }}
              />
            )
          ))}
        </div>
      )}
    </div>
  );
};

export default Files;