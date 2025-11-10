import React, { useState } from 'react';
import { 
  Layers as TemplateIcon, 
  Search, 
  Plus, 
  Star, 
  Eye, 
  Copy, 
  Edit,
  Code,
  FileText,
  FolderOpen,
  MessageSquare,
  MoreVertical,
  X
} from 'lucide-react';
import { cn } from '../../lib/utils';

const Templates: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'code' | 'document' | 'project' | 'prompt'>('all');
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);

  const templates = [
    {
      id: '1',
      name: 'React Dashboard Template',
      description: 'Template completo para dashboards con componentes reutilizables',
      category: 'code',
      language: 'TypeScript',
      preview: 'import React from "react";\nimport { Dashboard } from "./components/Dashboard";\n\nexport default function App() {\n  return (\n    <div className="min-h-screen bg-gray-50">\n      <Dashboard />\n    </div>\n  );\n}',
      variables: ['projectName', 'componentName'],
      isBuiltIn: true,
      usage: 24,
      rating: 4.8,
    },
    {
      id: '2',
      name: 'Documentación Técnica',
      description: 'Template para documentación técnica de proyectos',
      category: 'document',
      language: 'Markdown',
      preview: '# Documentación Técnica\n\n## Resumen\n\n## Instalación\n\n## Uso\n\n## API Reference',
      variables: ['projectName', 'author', 'version'],
      isBuiltIn: true,
      usage: 18,
      rating: 4.9,
    },
    {
      id: '3',
      name: 'Proyecto Full-Stack',
      description: 'Estructura completa para proyectos full-stack',
      category: 'project',
      language: 'Multiple',
      preview: 'my-project/\n├── frontend/\n├── backend/\n├── database/\n└── docs/',
      variables: ['projectName', 'technologies'],
      isBuiltIn: false,
      usage: 12,
      rating: 4.7,
    },
    {
      id: '4',
      name: 'Prompt de Análisis de Código',
      description: 'Prompt para análisis automatizado de código',
      category: 'prompt',
      language: 'Text',
      preview: 'Analiza el siguiente código y proporciona:\n1. Funcionalidad\n2. Posibles mejoras\n3. Problemas de seguridad',
      variables: ['analysisType', 'focusArea'],
      isBuiltIn: true,
      usage: 45,
      rating: 4.6,
    },
  ];

  const categories = [
    { id: 'all', label: 'Todos', icon: TemplateIcon, count: templates.length },
    { id: 'code', label: 'Código', icon: Code, count: templates.filter(t => t.category === 'code').length },
    { id: 'document', label: 'Documentos', icon: FileText, count: templates.filter(t => t.category === 'document').length },
    { id: 'project', label: 'Proyectos', icon: FolderOpen, count: templates.filter(t => t.category === 'project').length },
    { id: 'prompt', label: 'Prompts', icon: MessageSquare, count: templates.filter(t => t.category === 'prompt').length },
  ];

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'code': return Code;
      case 'document': return FileText;
      case 'project': return FolderOpen;
      case 'prompt': return MessageSquare;
      default: return TemplateIcon;
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-title font-bold text-neutral-900 dark:text-neutral-100 mb-2">
              Templates
            </h1>
            <p className="text-body-large text-neutral-600 dark:text-neutral-400">
              Plantillas predefinidas y personalizadas para acelerar tu desarrollo
            </p>
          </div>
          
          <button className="iris-button-primary">
            <Plus className="w-5 h-5 mr-2" />
            Crear Template
          </button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <input
              type="text"
              placeholder="Buscar templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-10 pl-10 pr-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500 focus:bg-background transition-all"
            />
          </div>

          <div className="flex space-x-1">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id as any)}
                  className={cn(
                    "flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors",
                    selectedCategory === category.id
                      ? "bg-brand-500 text-white"
                      : "hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-600 dark:text-neutral-400"
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span>{category.label}</span>
                  <span className="bg-white/20 px-2 py-0.5 rounded-full text-xs">
                    {category.count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Templates Grid */}
      {filteredTemplates.length === 0 ? (
        <div className="text-center py-12">
          <TemplateIcon className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-neutral-600 dark:text-neutral-400 mb-2">
            No se encontraron templates
          </h3>
          <p className="text-neutral-500">
            Intenta con otros términos de búsqueda
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => {
            const CategoryIcon = getCategoryIcon(template.category);
            return (
              <div key={template.id} className="iris-card-hover p-6 cursor-pointer group">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg bg-brand-100 flex items-center justify-center">
                      <CategoryIcon className="w-5 h-5 text-brand-500" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
                        {template.name}
                      </h3>
                      <p className="text-sm text-neutral-500">{template.language}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    {template.isBuiltIn && (
                      <Star className="w-4 h-4 text-yellow-500" />
                    )}
                    <button className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4 line-clamp-2">
                  {template.description}
                </p>

                {/* Preview */}
                <div className="bg-neutral-900 rounded-lg p-3 mb-4">
                  <pre className="text-xs text-green-400 overflow-hidden">
                    <code>{template.preview}</code>
                  </pre>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-neutral-500">
                    <span>{template.usage} usos</span>
                    <span>•</span>
                    <div className="flex items-center space-x-1">
                      <Star className="w-3 h-3 text-yellow-500 fill-current" />
                      <span>{template.rating}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button className="p-1.5 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 opacity-0 group-hover:opacity-100">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="p-1.5 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 opacity-0 group-hover:opacity-100">
                      <Copy className="w-4 h-4" />
                    </button>
                    <button className="p-1.5 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700 opacity-0 group-hover:opacity-100">
                      <Edit className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Template Preview Modal */}
      {selectedTemplate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="iris-card w-full max-w-4xl m-4 max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-border">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-title font-semibold">{selectedTemplate.name}</h2>
                  <p className="text-neutral-600 dark:text-neutral-400 mt-1">
                    {selectedTemplate.description}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedTemplate(null)}
                  className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-96">
              <pre className="bg-neutral-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                <code>{selectedTemplate.preview}</code>
              </pre>
            </div>
            
            <div className="p-6 border-t border-border flex justify-end space-x-3">
              <button className="iris-button-secondary">
                Editar
              </button>
              <button className="iris-button-primary">
                Usar Template
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Templates;