# IRIS Agent - Frontend Integrado

Frontend React TypeScript completamente integrado con el backend IRIS Code, implementando las mejores prácticas de UI/UX de 2025.

## 🚀 Inicio Rápido

### Prerrequisitos
- Node.js 18+ 
- pnpm
- Backend IRIS Code ejecutándose en `http://localhost:8001`

### Instalación y Desarrollo

```bash
# Instalar dependencias
npm run install-deps

# Ejecutar en modo desarrollo
npm run dev

# El frontend estará disponible en http://localhost:3000
# Se conectará automáticamente al backend en http://localhost:8001
```

### Verificación de Conexión

```bash
# Probar conectividad con el backend
npm run test:health

# Test completo de integración
npm run test:integration

# Test con URL específica
npm run test:integration:url --url=http://localhost:8001
```

## 🏗️ Arquitectura

### Estructura del Proyecto
```
src/
├── components/
│   ├── ui/                  # Componentes UI reutilizables
│   │   ├── ConnectionStatus.tsx
│   │   ├── ErrorHandling.tsx
│   │   ├── LoadingStates.tsx
│   │   └── Toast.tsx
│   ├── chat/
│   ├── dashboard/
│   ├── editor/
│   ├── files/
│   ├── layout/
│   ├── projects/
│   ├── settings/
│   └── templates/
├── hooks/                   # Hooks personalizados
│   ├── useConnection.ts
│   └── useToast.ts
├── lib/                     # Utilidades y configuración
│   ├── api.ts              # Cliente API integrado
│   ├── config.ts           # Configuración centralizada
│   └── storage.ts          # Persistencia local
└── stores/                  # Estado global (Zustand)
    ├── appStore.ts
    ├── chatStore.ts
    ├── editorStore.ts
    └── projectStore.ts
```

### Integración con Backend

#### API Endpoints Utilizados
- **Health Check**: `/health`
- **Métricas**: `/metrics`  
- **Proyectos**: `/api/v1/projects`
  - `GET /` - Listar proyectos
  - `POST /` - Crear proyecto
  - `PUT /{id}` - Actualizar proyecto
  - `DELETE /{id}` - Eliminar proyecto
- **Archivos**: `/api/v1/projects/{id}/files`
  - `GET /` - Listar archivos
  - `POST /` - Subir archivo
- **Chat**: `/api/v1/chat`
  - `POST /` - Enviar mensaje
  - `POST /stream` - Streaming de respuestas
- **Templates**: `/api/v1/templates`

#### Características de Integración
- **Auto-reconexión** con exponential backoff
- **Fallback a datos locales** cuando el backend no está disponible
- **Manejo robusto de errores** con UI amigable
- **Sincronización en tiempo real** de estado

## 🛠️ Comandos de Desarrollo

### Scripts Disponibles
```bash
# Desarrollo
npm run dev                  # Ejecutar en modo desarrollo
npm run build               # Construir para producción
npm run build:prod          # Construir optimizado para producción
npm run preview             # Previsualizar build de producción

# Testing
npm run test:integration    # Test completo de integración
npm run test:api            # Test de endpoints API
npm run test:health         # Verificar salud del backend

# Utilidades
npm run lint                # Verificar código con ESLint
npm run clean               # Limpiar dependencias
npm run install-deps        # Reinstalar dependencias
npm run setup:dev           # Setup completo para desarrollo
```

### Variables de Entorno
```env
# Configuración API
REACT_APP_API_URL=http://localhost:8001

# Features Flags
REACT_APP_ENABLE_DEBUG=true
REACT_APP_ENABLE_ANALYTICS=false

# Backend Configuration
REACT_APP_BACKEND_TIMEOUT=30000
REACT_APP_RETRY_ATTEMPTS=3
```

## 🎨 UI/UX Features

### Mejores Prácticas Implementadas

#### 1. **Estados de Carga**
- Loading spinners configurables
- Skeleton components para contenido
- Progress indicators para operaciones largas
- Animaciones suaves (deshabilitadas en producción)

#### 2. **Manejo de Errores**
- Error boundaries para aislamiento de errores
- UI amigable para diferentes tipos de error
- Opciones de recuperación (reintentar, reload)
- Detalles técnicos en modo desarrollo

#### 3. **Sistema de Notificaciones**
- Toasts con 4 tipos: success, error, warning, info
- Posicionamiento responsive (top-right desktop, bottom-center mobile)
- Auto-dismiss configurable
- Acciones personalizables

#### 4. **Gestión de Conexión**
- Indicador visual de estado de conexión
- Reconexión automática con exponential backoff
- Fallback a modo offline con datos locales
- Feedback detallado del estado del servidor

### Componentes UI Destacados

#### `ConnectionStatus`
```tsx
<ConnectionStatus showDetails />
```
- Muestra estado actual de conexión
- Información del servidor (versión, LLM stats)
- Indicadores visuales (conectado/desconectado/reconectando)

#### `LoadingSpinner`
```tsx
<LoadingSpinner 
  size="lg" 
  message="Conectando..."
  showRefresh 
  onRefresh={handleRefresh}
/>
```
- Loading configurable por tamaño
- Soporte para acciones de reintento
- Mensajes personalizados

#### `ToastManager`
```tsx
const { success, error, warning, info } = useToast();

success('Operación exitosa', 'Los datos se guardaron correctamente');
error('Error de conexión', 'No se pudo conectar al servidor');
```
- Hook personalizado para gestión de toasts
- Métodos de conveniencia para diferentes tipos
- Integración automática con el sistema

## 🧪 Testing

### Scripts de Testing
El proyecto incluye scripts de testing para verificar la integración:

```bash
# Test básico de conectividad
npm run test:health

# Test completo de integración
npm run test:integration

# Test con URL personalizada
npm run test:integration:url --url=http://localhost:8001
```

### Test Coverage
- ✅ Conectividad con backend
- ✅ Endpoints API críticos
- ✅ CORS configuration
- ✅ Health checks
- ✅ Manejo de errores de red
- ✅ Fallback mechanisms

### Running Tests Manually
```bash
# Verificar que el backend está ejecutándose
curl http://localhost:8001/health

# Probar endpoint de proyectos
curl http://localhost:8001/api/v1/projects

# Probar creación de proyecto
curl -X POST http://localhost:8001/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "Testing"}'
```

## 🔧 Configuración

### Configuración de Desarrollo
```typescript
// src/lib/config.ts
const config = {
  api: {
    baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8001',
    timeout: 30000,
    retryAttempts: 3,
    enableCaching: true
  },
  ui: {
    theme: 'system',
    animationDuration: 200,
    toastDuration: 5000
  },
  features: {
    autoSave: true,
    streaming: true,
    offlineMode: true
  }
};
```

### Configuración de Producción
```bash
# Variables de producción
REACT_APP_API_URL=https://tu-servidor.com
NODE_ENV=production
npm run build:prod
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

### Adaptaciones Mobile
- Toast notifications en bottom-center
- Navegación hamburger menu
- Touch-friendly button sizes
- Optimized layout para pantallas pequeñas

## 🐛 Debugging

### Modo Debug
```bash
# Habilita logs detallados
NODE_ENV=development npm run dev
```

### DevTools Útiles
- **React DevTools**: Para inspeccionar componentes
- **Redux DevTools**: Para Zustand stores
- **Network Tab**: Para verificar requests API
- **Console**: Para logs de debugging

### Logs de Conexión
```javascript
// Los logs aparecen en console en development
console.log('IRIS Code Configuration:', config);
console.log('Connection status:', isConnected);
console.log('API responses:', responseData);
```

## 🚀 Deployment

### Build para Producción
```bash
# Build optimizado
npm run build:prod

# Los archivos se generan en dist/
# Servir con cualquier servidor web estático
```

### Variables de Producción
- `REACT_APP_API_URL`: URL del backend en producción
- `NODE_ENV=production`: Optimizaciones automáticas
- `REACT_APP_ENABLE_DEBUG=false`: Deshabilita logs de desarrollo

### Docker Support
```dockerfile
# Multi-stage build optimizado
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build:prod

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔍 Troubleshooting

### Problemas Comunes

#### Backend No Disponible
```
Error: Network Error
```
**Solución**: Verificar que el backend esté ejecutándose en localhost:8001
```bash
curl http://localhost:8001/health
```

#### CORS Errors
```
Access to fetch at 'http://localhost:8001/api/v1/projects' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```
**Solución**: El backend debe tener CORS configurado para localhost:3000

#### Puerto Ya en Uso
```
Error: listen EADDRINUSE: address already in use :::3000
```
**Solución**: Cambiar puerto o terminar proceso existente
```bash
# Cambiar puerto en vite.config.ts
export default defineConfig({
  server: {
    port: 3001
  }
})
```

### Logs de Debugging
```javascript
// Habilitar logs en desarrollo
localStorage.setItem('debug', 'iris:*');

// Ver logs en console
console.log('API Base URL:', config.api.baseUrl);
console.log('Connection Status:', connectionState);
```

## 🤝 Contribución

### Guidelines
1. **TypeScript**: Usar tipos estrictos
2. **ESLint**: Seguir reglas de linting
3. **Testing**: Incluir tests para nuevas features
4. **UI/UX**: Seguir mejores prácticas implementadas
5. **Responsive**: Asegurar compatibilidad mobile

### Commits
- `feat:` - Nuevas features
- `fix:` - Bug fixes
- `docs:` - Documentación
- `style:` - Cambios de formato
- `refactor:` - Refactoring
- `test:` - Tests

## 📄 Licencia

IRIS Code - Sistema Multi-Agente Superior
Desarrollado con las mejores prácticas de 2025.

---

**🎉 ¡Frontend completamente integrado y listo para producción!**

Para más información, ver [INTEGRACION_FRONTEND_BACKEND.md](./INTEGRACION_FRONTEND_BACKEND.md)