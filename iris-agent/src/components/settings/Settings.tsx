import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  User, 
  Bell, 
  Shield, 
  Code, 
  Palette, 
  Globe,
  Monitor,
  Moon,
  Sun,
  Laptop,
  Save,
  Download,
  Trash2,
  Key,
  Database,
  Cpu,
  Wifi,
  AlertTriangle
} from 'lucide-react';
import { cn } from '../../lib/utils';

const Settings: React.FC = () => {
  const [activeSection, setActiveSection] = useState('general');
  const [theme, setTheme] = useState('dark');
  const [language, setLanguage] = useState('es');
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    desktop: false,
  });

  const sections = [
    { id: 'general', label: 'General', icon: SettingsIcon },
    { id: 'appearance', label: 'Apariencia', icon: Palette },
    { id: 'notifications', label: 'Notificaciones', icon: Bell },
    { id: 'ai', label: 'Configuración IA', icon: Cpu },
    { id: 'editor', label: 'Editor', icon: Code },
    { id: 'privacy', label: 'Privacidad', icon: Shield },
    { id: 'account', label: 'Cuenta', icon: User },
    { id: 'advanced', label: 'Avanzado', icon: Database },
  ];

  const GeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Configuración General</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Idioma</label>
            <select 
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full h-10 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500"
            >
              <option value="es">Español</option>
              <option value="en">English</option>
              <option value="fr">Français</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Zona Horaria</label>
            <select className="w-full h-10 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500">
              <option value="America/Mexico_City">Ciudad de México (GMT-6)</option>
              <option value="America/New_York">Nueva York (GMT-5)</option>
              <option value="Europe/Madrid">Madrid (GMT+1)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Formato de Fecha</label>
            <select className="w-full h-10 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500">
              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  const AppearanceSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Apariencia</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3">Tema</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'light', label: 'Claro', icon: Sun },
                { id: 'dark', label: 'Oscuro', icon: Moon },
                { id: 'system', label: 'Sistema', icon: Monitor },
              ].map((option) => {
                const Icon = option.icon;
                return (
                  <button
                    key={option.id}
                    onClick={() => setTheme(option.id)}
                    className={cn(
                      "flex flex-col items-center space-y-2 p-4 rounded-xl border-2 transition-all",
                      theme === option.id
                        ? "border-brand-500 bg-brand-50 dark:bg-brand-900/20"
                        : "border-neutral-200 dark:border-neutral-700 hover:border-brand-300"
                    )}
                  >
                    <Icon className="w-6 h-6" />
                    <span className="text-sm font-medium">{option.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Densidad de la interfaz</label>
            <select className="w-full h-10 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500">
              <option value="compact">Compacta</option>
              <option value="comfortable">Cómoda</option>
              <option value="spacious">Espaciosa</option>
            </select>
          </div>

          <div>
            <label className="flex items-center space-x-3">
              <input type="checkbox" className="rounded" />
              <span className="text-sm">Animaciones suaves</span>
            </label>
          </div>

          <div>
            <label className="flex items-center space-x-3">
              <input type="checkbox" className="rounded" />
              <span className="text-sm">Efectos de glassmorphism</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const NotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Notificaciones</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800 rounded-xl">
            <div>
              <h4 className="font-medium">Notificaciones por Email</h4>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Recibe actualizaciones importantes por correo
              </p>
            </div>
            <input
              type="checkbox"
              checked={notifications.email}
              onChange={(e) => setNotifications(prev => ({ ...prev, email: e.target.checked }))}
              className="rounded"
            />
          </div>

          <div className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800 rounded-xl">
            <div>
              <h4 className="font-medium">Notificaciones Push</h4>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Notificaciones en el navegador
              </p>
            </div>
            <input
              type="checkbox"
              checked={notifications.push}
              onChange={(e) => setNotifications(prev => ({ ...prev, push: e.target.checked }))}
              className="rounded"
            />
          </div>

          <div className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800 rounded-xl">
            <div>
              <h4 className="font-medium">Notificaciones de Escritorio</h4>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Notificaciones del sistema operativo
              </p>
            </div>
            <input
              type="checkbox"
              checked={notifications.desktop}
              onChange={(e) => setNotifications(prev => ({ ...prev, desktop: e.target.checked }))}
              className="rounded"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const AISettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Configuración de IA</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Modelo Principal</label>
            <select className="w-full h-10 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500">
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-3.5">GPT-3.5 Turbo</option>
              <option value="claude-3">Claude 3 Opus</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Temperatura</label>
            <input 
              type="range" 
              min="0" 
              max="2" 
              step="0.1" 
              defaultValue="0.7"
              className="w-full"
            />
            <div className="flex justify-between text-xs text-neutral-500 mt-1">
              <span>Conservador</span>
              <span>0.7</span>
              <span>Creativo</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Máximo de Tokens</label>
            <select className="w-full h-10 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500">
              <option value="1000">1,000 tokens</option>
              <option value="2000">2,000 tokens</option>
              <option value="4000">4,000 tokens</option>
              <option value="8000">8,000 tokens</option>
            </select>
          </div>

          <div>
            <label className="flex items-center space-x-3">
              <input type="checkbox" className="rounded" defaultChecked />
              <span className="text-sm">Sugerencias automáticas</span>
            </label>
          </div>

          <div>
            <label className="flex items-center space-x-3">
              <input type="checkbox" className="rounded" defaultChecked />
              <span className="text-sm">Completado en línea (Inline completions)</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const EditorSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Configuración del Editor</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Tamaño de Fuente</label>
            <input 
              type="range" 
              min="10" 
              max="24" 
              defaultValue="14"
              className="w-full"
            />
            <div className="flex justify-between text-xs text-neutral-500 mt-1">
              <span>10px</span>
              <span>14px</span>
              <span>24px</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Tamaño de Tab</label>
            <select className="w-full h-10 px-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500">
              <option value="2">2 espacios</option>
              <option value="4">4 espacios</option>
              <option value="8">8 espacios</option>
            </select>
          </div>

          <div>
            <label className="flex items-center space-x-3">
              <input type="checkbox" className="rounded" defaultChecked />
              <span className="text-sm">Ajuste de línea automático</span>
            </label>
          </div>

          <div>
            <label className="flex items-center space-x-3">
              <input type="checkbox" className="rounded" defaultChecked />
              <span className="text-sm">Mostrar minimapa</span>
            </label>
          </div>

          <div>
            <label className="flex items-center space-x-3">
              <input type="checkbox" className="rounded" />
              <span className="text-sm">Mostrar espacios en blanco</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const PrivacySettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Privacidad y Datos</h3>
        
        <div className="space-y-4">
          <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl">
            <div className="flex items-center space-x-2 mb-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              <h4 className="font-medium text-yellow-800 dark:text-yellow-200">Importante</h4>
            </div>
            <p className="text-sm text-yellow-700 dark:text-yellow-300">
              Estas configuraciones afectan la privacidad de tus datos. Revisa cuidadosamente antes de hacer cambios.
            </p>
          </div>

          <div className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800 rounded-xl">
            <div>
              <h4 className="font-medium">Compartir uso anónimo</h4>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Ayuda a mejorar IRIS compartiendo datos de uso
              </p>
            </div>
            <input type="checkbox" className="rounded" defaultChecked />
          </div>

          <div className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800 rounded-xl">
            <div>
              <h4 className="font-medium">Guardar conversaciones</h4>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Mantener historial de chat para mejorar respuestas
              </p>
            </div>
            <input type="checkbox" className="rounded" defaultChecked />
          </div>

          <div className="space-y-3">
            <h4 className="font-medium">Gestión de Datos</h4>
            <div className="flex space-x-3">
              <button className="iris-button-secondary">
                <Download className="w-4 h-4 mr-2" />
                Exportar Datos
              </button>
              <button className="iris-button-secondary text-semantic-error hover:bg-semantic-error hover:text-white">
                <Trash2 className="w-4 h-4 mr-2" />
                Eliminar Cuenta
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSectionContent = () => {
    switch (activeSection) {
      case 'general': return <GeneralSettings />;
      case 'appearance': return <AppearanceSettings />;
      case 'notifications': return <NotificationSettings />;
      case 'ai': return <AISettings />;
      case 'editor': return <EditorSettings />;
      case 'privacy': return <PrivacySettings />;
      default: return <GeneralSettings />;
    }
  };

  return (
    <div className="h-full flex">
      {/* Settings Sidebar */}
      <div className="w-64 border-r border-border bg-background p-4">
        <h2 className="text-lg font-semibold mb-6">Configuración</h2>
        
        <nav className="space-y-1">
          {sections.map((section) => {
            const Icon = section.icon;
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={cn(
                  "flex items-center space-x-3 w-full px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                  activeSection === section.id
                    ? "bg-brand-500 text-white"
                    : "hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-700 dark:text-neutral-300"
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{section.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Settings Content */}
      <div className="flex-1 overflow-y-auto p-8">
        {renderSectionContent()}
        
        {/* Save Button */}
        <div className="flex justify-end pt-8 border-t border-border mt-8">
          <button className="iris-button-primary">
            <Save className="w-4 h-4 mr-2" />
            Guardar Configuración
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;