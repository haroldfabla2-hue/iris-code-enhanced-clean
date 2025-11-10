import React from 'react';
import { useAppStore } from '../../stores/appStore';
import { useProjectStore } from '../../stores/projectStore';
import { 
  Activity, 
  MessageSquare, 
  FolderOpen, 
  Code2, 
  TrendingUp, 
  TrendingDown,
  Plus,
  Zap,
  Clock,
  Users,
  FileText,
  ArrowRight
} from 'lucide-react';
import { cn } from '../../lib/utils';

const Dashboard: React.FC = () => {
  const { metrics } = useAppStore();
  const { projects } = useProjectStore();

  // Mock trending data
  const trends = {
    tokens: { value: '+15%', isPositive: true },
    projects: { value: '+2', isPositive: true },
    conversations: { value: '+8', isPositive: true },
    responseTime: { value: '-12ms', isPositive: true }
  };

  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ComponentType<{ className?: string }>;
    trend?: { value: string; isPositive: boolean };
    sparkline?: number[];
    description?: string;
  }> = ({ title, value, icon: Icon, trend, sparkline, description }) => (
    <div className="iris-card-hover p-8">
      <div className="flex items-center justify-between mb-6">
        <div className="w-12 h-12 rounded-2xl bg-brand-100 flex items-center justify-center">
          <Icon className="w-6 h-6 text-brand-500" />
        </div>
        {trend && (
          <div className={cn(
            "flex items-center gap-1 text-sm font-medium",
            trend.isPositive ? "text-semantic-success" : "text-semantic-error"
          )}>
            {trend.isPositive ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            {trend.value}
          </div>
        )}
      </div>
      
      <div className="space-y-2">
        <h3 className="text-caption font-medium text-neutral-500">{title}</h3>
        <p className="text-3xl font-bold text-neutral-900 dark:text-neutral-100">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        {description && (
          <p className="text-caption text-neutral-500">{description}</p>
        )}
      </div>

      {sparkline && (
        <div className="mt-4">
          <svg className="w-full h-8" viewBox="0 0 100 20">
            <polyline
              fill="none"
              stroke="#0066FF"
              strokeWidth="2"
              points={sparkline.map((point, index) => 
                `${(index / (sparkline.length - 1)) * 100},${20 - (point / Math.max(...sparkline)) * 15}`
              ).join(' ')}
            />
          </svg>
        </div>
      )}
    </div>
  );

  const ProjectCard: React.FC<{
    project: any;
    onClick?: () => void;
  }> = ({ project, onClick }) => (
    <div 
      className="iris-card-hover p-6 cursor-pointer group"
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center">
          <FolderOpen className="w-6 h-6 text-white" />
        </div>
        <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-brand-500 transition-colors" />
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
        
        <div className="flex items-center justify-between text-sm text-neutral-500">
          <span className="flex items-center gap-1">
            <FileText className="w-4 h-4" />
            {project.files} archivos
          </span>
          <span className="flex items-center gap-1">
            <MessageSquare className="w-4 h-4" />
            {project.conversations} chats
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-neutral-500">
            {project.lastActivity}
          </span>
          <button className="text-sm text-brand-500 hover:text-brand-600 font-medium">
            Abrir →
          </button>
        </div>
      </div>
    </div>
  );

  const QuickActionButton: React.FC<{
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    onClick?: () => void;
    variant?: 'primary' | 'secondary';
  }> = ({ icon: Icon, label, onClick, variant = 'primary' }) => (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center space-x-3 px-6 py-4 rounded-xl font-medium transition-all duration-200",
        variant === 'primary' 
          ? "iris-button-primary" 
          : "iris-button-secondary"
      )}
    >
      <Icon className="w-5 h-5" />
      <span>{label}</span>
    </button>
  );

  // Mock activity data
  const recentActivity = [
    {
      id: '1',
      type: 'project',
      title: 'Nuevo proyecto creado',
      description: 'data-analytics-dashboard',
      time: 'Hace 5 minutos',
      icon: FolderOpen
    },
    {
      id: '2',
      type: 'chat',
      title: 'Conversación actualizada',
      description: 'Implementación del Monaco Editor',
      time: 'Hace 12 minutos',
      icon: MessageSquare
    },
    {
      id: '3',
      type: 'file',
      title: 'Archivo modificado',
      description: 'src/components/Dashboard.tsx',
      time: 'Hace 18 minutos',
      icon: Code2
    },
    {
      id: '4',
      type: 'template',
      title: 'Template aplicado',
      description: 'React Dashboard Template',
      time: 'Hace 25 minutos',
      icon: FileText
    }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-12">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-hero font-bold text-neutral-900 dark:text-neutral-100 mb-3">
              Dashboard Principal
            </h1>
            <p className="text-body-large text-neutral-600 dark:text-neutral-400 max-w-2xl">
              Control central de tu agente IRIS. Monitorea métricas en tiempo real, 
              gestiona proyectos y accede a herramientas de desarrollo.
            </p>
          </div>
          <div className="hidden lg:block">
            <div className="flex items-center space-x-3 text-sm text-neutral-500">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-semantic-success rounded-full"></div>
                Sistema conectado
              </div>
              <span>•</span>
              <span>Última actualización: hace 2 min</span>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <MetricCard
          title="Tokens Utilizados"
          value={`${metrics.tokensUsed.toLocaleString()} / ${metrics.tokensAvailable.toLocaleString()}`}
          icon={Zap}
          trend={trends.tokens}
          sparkline={[65, 70, 68, 75, 72, 78, 85]}
          description="Consumo de contexto IA"
        />
        <MetricCard
          title="Proyectos Activos"
          value={metrics.activeProjects}
          icon={FolderOpen}
          trend={trends.projects}
          sparkline={[8, 10, 9, 12, 11, 12, 12]}
        />
        <MetricCard
          title="Conversaciones"
          value={metrics.activeConversations}
          icon={MessageSquare}
          trend={trends.conversations}
          sparkline={[25, 28, 32, 29, 34, 38, 34]}
        />
        <MetricCard
          title="Tiempo de Respuesta"
          value={`${metrics.responseTime}ms`}
          icon={Clock}
          trend={trends.responseTime}
          sparkline={[280, 275, 270, 260, 250, 245, 245]}
          description="Latencia promedio"
        />
      </div>

      {/* Quick Actions */}
      <div className="mb-12">
        <h2 className="text-subtitle font-semibold text-neutral-900 dark:text-neutral-100 mb-6">
          Acciones Rápidas
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <QuickActionButton
            icon={Plus}
            label="Nuevo Proyecto"
            onClick={() => {}}
          />
          <QuickActionButton
            icon={MessageSquare}
            label="Nueva Conversación"
            variant="secondary"
            onClick={() => {}}
          />
          <QuickActionButton
            icon={Code2}
            label="Abrir Editor"
            variant="secondary"
            onClick={() => {}}
          />
          <QuickActionButton
            icon={FileText}
            label="Crear Template"
            variant="secondary"
            onClick={() => {}}
          />
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Projects Section */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-subtitle font-semibold text-neutral-900 dark:text-neutral-100">
              Proyectos Destacados
            </h2>
            <button className="text-brand-500 hover:text-brand-600 font-medium text-sm">
              Ver todos →
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {projects.slice(0, 4).map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onClick={() => {}}
              />
            ))}
          </div>
        </div>

        {/* Activity Feed */}
        <div className="space-y-6">
          <div>
            <h2 className="text-subtitle font-semibold text-neutral-900 dark:text-neutral-100 mb-6">
              Actividad Reciente
            </h2>
            <div className="iris-card p-6">
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-3">
                    <div className="w-8 h-8 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center flex-shrink-0">
                      <activity.icon className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                        {activity.title}
                      </p>
                      <p className="text-sm text-neutral-600 dark:text-neutral-400 truncate">
                        {activity.description}
                      </p>
                      <p className="text-xs text-neutral-500 mt-1">
                        {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* System Status */}
          <div>
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
              Estado del Sistema
            </h3>
            <div className="iris-card p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-neutral-600 dark:text-neutral-400">MCP Server</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-semantic-success rounded-full"></div>
                    <span className="text-sm font-medium text-semantic-success">Conectado</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-neutral-600 dark:text-neutral-400">Base de Datos</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-semantic-success rounded-full"></div>
                    <span className="text-sm font-medium text-semantic-success">Activa</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-neutral-600 dark:text-neutral-400">IA Modelos</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-semantic-success rounded-full"></div>
                    <span className="text-sm font-medium text-semantic-success">Listo</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;