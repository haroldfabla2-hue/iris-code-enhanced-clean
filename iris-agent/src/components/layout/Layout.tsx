import React from 'react';
import { useAppStore } from '../../stores/appStore';
import { 
  LayoutDashboard, 
  FolderOpen, 
  MessageSquare, 
  Code2, 
  Layers, 
  FileText, 
  Layers as TemplateIcon, 
  Settings,
  ChevronLeft,
  ChevronRight,
  Menu,
  Search,
  Bell,
  User,
  X,
  Sparkles,
  Beaker,
  Wrench,
  Network,
  CheckSquare
} from 'lucide-react';
import { cn } from '../../lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  badge?: number;
}

const navigationItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/' },
  { id: 'projects', label: 'Proyectos', icon: FolderOpen, path: '/projects' },
  { id: 'chat', label: 'Chat', icon: MessageSquare, path: '/chat' },
  { id: 'assets', label: 'Assets', icon: Sparkles, path: '/assets' },
  { id: 'memory', label: 'Memory', icon: Beaker, path: '/memory' },
  { id: 'tools', label: 'Herramientas', icon: Wrench, path: '/tools' },
  { id: 'tasks', label: 'Tareas', icon: CheckSquare, path: '/tasks' },
  { id: 'bridge', label: 'Bridge', icon: Network, path: '/bridge' },
  { id: 'editor', label: 'Editor', icon: Code2, path: '/editor' },
  { id: 'canvas', label: 'Canvas', icon: Layers, path: '/canvas' },
  { id: 'files', label: 'Archivos', icon: FileText, path: '/files' },
  { id: 'templates', label: 'Templates', icon: TemplateIcon, path: '/templates' },
  { id: 'settings', label: 'Configuración', icon: Settings, path: '/settings' },
];

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { 
    sidebarCollapsed, 
    contextPanelCollapsed,
    unreadCount,
    setSidebarCollapsed, 
    setContextPanelCollapsed,
    setActiveModal,
    theme,
  } = useAppStore();

  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');

  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen);

  const NavItemComponent: React.FC<{ 
    item: NavItem; 
    isActive?: boolean; 
    onClick?: () => void;
  }> = ({ item, isActive, onClick }) => (
    <button
      onClick={onClick}
      className={cn(
        'iris-nav-item w-full text-left',
        isActive ? 'iris-nav-item-active' : 'hover:bg-neutral-100 dark:hover:bg-neutral-800'
      )}
    >
      <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
      {!sidebarCollapsed && (
        <span className="truncate">{item.label}</span>
      )}
      {item.badge && !sidebarCollapsed && (
        <span className="ml-auto bg-brand-500 text-white text-xs px-2 py-0.5 rounded-full">
          {item.badge}
        </span>
      )}
    </button>
  );

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo Area */}
      <div className="flex items-center justify-center h-16 border-b border-border">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-brand-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">IRIS</span>
          </div>
          {!sidebarCollapsed && (
            <span className="font-semibold text-lg">Agente IRIS</span>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navigationItems.slice(0, 6).map((item) => (
          <NavItemComponent
            key={item.id}
            item={item}
            onClick={() => {
              // Navigation logic will be handled by React Router
              setMobileMenuOpen(false);
            }}
          />
        ))}
      </nav>

      {/* Divider */}
      <div className="border-t border-border mx-3" />

      {/* Secondary Navigation */}
      <nav className="px-3 py-4 space-y-1">
        {navigationItems.slice(6).map((item) => (
          <NavItemComponent
            key={item.id}
            item={item}
            onClick={() => {
              setMobileMenuOpen(false);
            }}
          />
        ))}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-border">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-neutral-300 dark:bg-neutral-600 rounded-full flex items-center justify-center">
            <User className="w-4 h-4" />
          </div>
          {!sidebarCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">Usuario IRIS</p>
              <p className="text-xs text-neutral-500 truncate">usuario@iris.dev</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-screen flex bg-background text-foreground">
      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={toggleMobileMenu}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed lg:relative z-50 h-full bg-background border-r border-border transition-all duration-200 ease-out',
          'lg:translate-x-0',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
          sidebarCollapsed ? 'w-16' : 'w-60'
        )}
      >
        <SidebarContent />
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 bg-background/80 backdrop-blur-md border-b border-border sticky top-0 z-30">
          <div className="flex items-center justify-between h-full px-6">
            {/* Left Section */}
            <div className="flex items-center space-x-4">
              {/* Mobile Menu Button */}
              <button
                onClick={toggleMobileMenu}
                className="lg:hidden p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
              >
                <Menu className="w-5 h-5" />
              </button>

              {/* Desktop Sidebar Toggle */}
              <button
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                className="hidden lg:block p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
              >
                <ChevronLeft className={cn(
                  "w-5 h-5 transition-transform",
                  sidebarCollapsed && "rotate-180"
                )} />
              </button>

              {/* Breadcrumbs */}
              <nav className="hidden md:flex items-center space-x-2 text-sm text-neutral-500">
                <span>IRIS</span>
                <span>/</span>
                <span>Dashboard</span>
              </nav>
            </div>

            {/* Center Section - Search */}
            <div className="flex-1 max-w-lg mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
                <input
                  type="text"
                  placeholder="Buscar proyectos, conversaciones, archivos..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full h-10 pl-10 pr-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500 focus:bg-background transition-all"
                />
              </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center space-x-2">
              {/* Notifications */}
              <button
                onClick={() => setActiveModal('notifications')}
                className="relative p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-semantic-error text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Theme Toggle */}
              <button
                onClick={() => {
                  // Theme toggle logic
                  const newTheme = theme === 'dark' ? 'light' : 'dark';
                  document.documentElement.classList.toggle('dark', newTheme === 'dark');
                }}
                className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
              >
                {theme === 'dark' ? '🌙' : '☀️'}
              </button>

              {/* User Menu */}
              <button className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800">
                <User className="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>

      {/* Context Panel */}
      <aside
        className={cn(
          'fixed lg:relative right-0 top-16 bottom-0 bg-background border-l border-border transition-all duration-200 ease-out z-20',
          'translate-x-0',
          contextPanelCollapsed ? 'w-12' : 'w-90'
        )}
      >
        {/* Context Panel Content */}
        <div className="h-full flex flex-col">
          {/* Toggle Button */}
          <button
            onClick={() => setContextPanelCollapsed(!contextPanelCollapsed)}
            className="absolute -left-3 top-4 w-6 h-6 bg-background border border-border rounded-full flex items-center justify-center hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
          >
            <ChevronRight className={cn(
              "w-3 h-3 transition-transform",
              contextPanelCollapsed && "rotate-180"
            )} />
          </button>

          {!contextPanelCollapsed && (
            <div className="flex-1 p-4 space-y-4">
              {/* Token Counter */}
              <div className="iris-card p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Contexto</span>
                  <span className="text-xs text-neutral-500">1.2k / 5k</span>
                </div>
                <div className="w-full bg-neutral-200 dark:bg-neutral-800 rounded-full h-2">
                  <div 
                    className="bg-brand-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: '24%' }}
                  />
                </div>
              </div>

              {/* Active Files */}
              <div className="iris-card p-4">
                <h3 className="text-sm font-medium mb-3">Archivos Activos</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 bg-neutral-100 dark:bg-neutral-800 rounded">
                    <span className="text-xs truncate">App.tsx</span>
                    <button className="text-neutral-400 hover:text-neutral-600">
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-neutral-100 dark:bg-neutral-800 rounded">
                    <span className="text-xs truncate">Dashboard.tsx</span>
                    <button className="text-neutral-400 hover:text-neutral-600">
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Active Instructions */}
              <div className="iris-card p-4">
                <h3 className="text-sm font-medium mb-3">Instrucciones</h3>
                <div className="space-y-2">
                  <div className="text-xs text-neutral-600 dark:text-neutral-400 p-2 bg-brand-50 dark:bg-brand-900/20 rounded">
                    Desarrollar con diseño minimalista premium
                  </div>
                  <div className="text-xs text-neutral-600 dark:text-neutral-400 p-2 bg-brand-50 dark:bg-brand-900/20 rounded">
                    Usar sistema de tokens IRIS
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
};

export default Layout;