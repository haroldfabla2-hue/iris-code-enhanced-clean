import React, { useState } from 'react';
import { 
  Bell, 
  X, 
  Check, 
  CheckCheck, 
  Trash2, 
  Filter,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  Clock,
  MoreVertical,
  Settings,
  Archive,
  Search,
  Star
} from 'lucide-react';
import { cn } from '../../lib/utils';

interface NotificationsProps {
  onClose?: () => void;
}

const Notifications: React.FC<NotificationsProps> = ({ onClose }) => {
  const [filter, setFilter] = useState<'all' | 'unread' | 'system' | 'project' | 'error'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNotifications, setSelectedNotifications] = useState<string[]>([]);

  const notifications = [
    {
      id: '1',
      type: 'system' as const,
      title: 'Sistema conectado',
      message: 'MCP Server funcionando correctamente. Todas las funciones están disponibles.',
      timestamp: '2024-11-05T11:30:00Z',
      isRead: false,
      priority: 'info',
      actions: [],
    },
    {
      id: '2',
      type: 'project' as const,
      title: 'Proyecto actualizado',
      message: 'iris-chat-app tiene 3 nuevos archivos y 2 conversaciones activas.',
      timestamp: '2024-11-05T10:45:00Z',
      isRead: false,
      priority: 'info',
      actions: [{ label: 'Ver proyecto', href: '/projects/1' }],
    },
    {
      id: '3',
      type: 'error' as const,
      title: 'Error de conexión',
      message: 'Se perdió la conexión con el servidor. Reintentando automáticamente...',
      timestamp: '2024-11-05T09:20:00Z',
      isRead: true,
      priority: 'error',
      actions: [{ label: 'Reintentar', action: 'retry' }],
    },
    {
      id: '4',
      type: 'system' as const,
      title: 'Actualización disponible',
      message: 'IRIS v2.1.0 está disponible. Incluye mejoras en el editor y nuevas funcionalidades de IA.',
      timestamp: '2024-11-04T16:00:00Z',
      isRead: true,
      priority: 'info',
      actions: [{ label: 'Actualizar', action: 'update' }],
    },
    {
      id: '5',
      type: 'project' as const,
      title: 'Template aplicado',
      message: 'Se aplicó exitosamente el template "React Dashboard" al proyecto data-analytics.',
      timestamp: '2024-11-04T14:30:00Z',
      isRead: true,
      priority: 'success',
      actions: [],
    },
    {
      id: '6',
      type: 'error' as const,
      title: 'Límite de tokens alcanzado',
      message: 'Has alcanzado el 90% de tu límite de tokens mensual. Considera optimizar tus prompts.',
      timestamp: '2024-11-04T11:15:00Z',
      isRead: false,
      priority: 'warning',
      actions: [{ label: 'Ver uso', action: 'view_usage' }],
    },
  ];

  const getNotificationIcon = (type: string, priority: string) => {
    if (priority === 'error') return XCircle;
    if (priority === 'warning') return AlertTriangle;
    if (priority === 'success') return CheckCircle;
    return Info;
  };

  const getNotificationColor = (type: string, priority: string) => {
    if (priority === 'error') return 'text-semantic-error bg-semantic-error/10';
    if (priority === 'warning') return 'text-semantic-warning bg-semantic-warning/10';
    if (priority === 'success') return 'text-semantic-success bg-semantic-success/10';
    return 'text-brand-500 bg-brand-100';
  };

  const getPriorityBadge = (priority: string) => {
    const badges = {
      error: { label: 'Error', className: 'bg-semantic-error/10 text-semantic-error' },
      warning: { label: 'Advertencia', className: 'bg-semantic-warning/10 text-semantic-warning' },
      info: { label: 'Info', className: 'bg-brand-100 text-brand-600' },
      success: { label: 'Éxito', className: 'bg-semantic-success/10 text-semantic-success' },
    };
    
    return badges[priority as keyof typeof badges] || badges.info;
  };

  const filteredNotifications = notifications.filter(notification => {
    const matchesSearch = notification.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         notification.message.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filter === 'all' || 
                         (filter === 'unread' && !notification.isRead) ||
                         notification.type === filter;
    return matchesSearch && matchesFilter;
  });

  const markAsRead = (id: string) => {
    // Update notification read status
  };

  const markAllAsRead = () => {
    // Mark all notifications as read
  };

  const deleteNotification = (id: string) => {
    // Delete notification
  };

  const NotificationItem: React.FC<{
    notification: any;
    isSelected: boolean;
    onSelect: () => void;
    onMarkAsRead: () => void;
    onDelete: () => void;
  }> = ({ notification, isSelected, onSelect, onMarkAsRead, onDelete }) => {
    const Icon = getNotificationIcon(notification.type, notification.priority);
    const colorClass = getNotificationColor(notification.type, notification.priority);
    const badge = getPriorityBadge(notification.priority);
    
    return (
      <div 
        className={cn(
          "flex items-start space-x-4 p-4 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 rounded-lg transition-colors cursor-pointer",
          !notification.isRead && "bg-brand-50/50 dark:bg-brand-900/10 border-l-4 border-brand-500",
          isSelected && "bg-brand-100 dark:bg-brand-900/30"
        )}
        onClick={onSelect}
      >
        <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0", colorClass)}>
          <Icon className="w-5 h-5" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <h4 className={cn(
              "font-medium",
              !notification.isRead ? "text-neutral-900 dark:text-neutral-100" : "text-neutral-700 dark:text-neutral-300"
            )}>
              {notification.title}
            </h4>
            <div className="flex items-center space-x-2 ml-4">
              <span className={cn("text-xs px-2 py-1 rounded-full font-medium", badge.className)}>
                {badge.label}
              </span>
              <button className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-700">
                <MoreVertical className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <p className={cn(
            "text-sm mb-3",
            !notification.isRead ? "text-neutral-800 dark:text-neutral-200" : "text-neutral-600 dark:text-neutral-400"
          )}>
            {notification.message}
          </p>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs text-neutral-500">
              <Clock className="w-3 h-3" />
              <span>{new Date(notification.timestamp).toLocaleString()}</span>
            </div>
            
            <div className="flex items-center space-x-2">
              {notification.actions.map((action: any, index: number) => (
                <button
                  key={index}
                  className="text-xs text-brand-500 hover:text-brand-600 font-medium"
                >
                  {action.label}
                </button>
              ))}
              
              {!notification.isRead && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onMarkAsRead();
                  }}
                  className="text-xs text-neutral-500 hover:text-neutral-700"
                >
                  Marcar como leído
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Bell className="w-6 h-6 text-brand-500" />
            <h2 className="text-title font-semibold">Notificaciones</h2>
            <span className="bg-brand-500 text-white text-xs px-2 py-1 rounded-full">
              {notifications.filter(n => !n.isRead).length}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={markAllAsRead}
              className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
              title="Marcar todas como leídas"
            >
              <CheckCheck className="w-4 h-4" />
            </button>
            <button className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800" title="Configuración">
              <Settings className="w-4 h-4" />
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <input
              type="text"
              placeholder="Buscar notificaciones..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-10 pl-10 pr-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500 focus:bg-background transition-all"
            />
          </div>

          <div className="flex space-x-1">
            {(['all', 'unread', 'system', 'project', 'error'] as const).map((filterOption) => (
              <button
                key={filterOption}
                onClick={() => setFilter(filterOption)}
                className={cn(
                  "px-3 py-1.5 text-sm font-medium rounded-lg transition-colors",
                  filter === filterOption
                    ? "bg-brand-500 text-white"
                    : "hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-600 dark:text-neutral-400"
                )}
              >
                {filterOption === 'all' ? 'Todas' : 
                 filterOption === 'unread' ? 'Sin leer' :
                 filterOption === 'system' ? 'Sistema' :
                 filterOption === 'project' ? 'Proyectos' : 'Errores'}
              </button>
            ))}
          </div>
        </div>

        {/* Bulk Actions */}
        {selectedNotifications.length > 0 && (
          <div className="mt-4 p-3 bg-brand-50 dark:bg-brand-900/20 rounded-lg flex items-center justify-between">
            <span className="text-sm font-medium text-brand-700 dark:text-brand-300">
              {selectedNotifications.length} seleccionada{selectedNotifications.length > 1 ? 's' : ''}
            </span>
            <div className="flex items-center space-x-2">
              <button className="text-sm text-brand-600 hover:text-brand-700 font-medium">
                Marcar como leídas
              </button>
              <button className="text-sm text-semantic-error hover:text-semantic-error/80 font-medium">
                Eliminar
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Notifications List */}
      <div className="flex-1 overflow-y-auto p-6">
        {filteredNotifications.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-neutral-600 dark:text-neutral-400 mb-2">
              No hay notificaciones
            </h3>
            <p className="text-neutral-500">
              {searchQuery ? 'No se encontraron resultados' : 'Estás al día con todas tus notificaciones'}
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredNotifications.map((notification) => (
              <div key={notification.id} className="group">
                <NotificationItem
                  notification={notification}
                  isSelected={selectedNotifications.includes(notification.id)}
                  onSelect={() => {
                    setSelectedNotifications(prev =>
                      prev.includes(notification.id)
                        ? prev.filter(id => id !== notification.id)
                        : [...prev, notification.id]
                    );
                  }}
                  onMarkAsRead={() => markAsRead(notification.id)}
                  onDelete={() => deleteNotification(notification.id)}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border bg-neutral-50 dark:bg-neutral-900/50">
        <div className="flex items-center justify-between text-sm text-neutral-500">
          <span>
            Mostrando {filteredNotifications.length} de {notifications.length} notificaciones
          </span>
          <div className="flex items-center space-x-4">
            <span>Actualizado hace 2 min</span>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-semantic-success rounded-full"></div>
              <span>Sincronizado</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Notifications;