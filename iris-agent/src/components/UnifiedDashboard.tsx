import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import unifiedAPI from '../lib/unified-api';
import { 
  Brain, 
  Zap, 
  Users, 
  BarChart3, 
  Image, 
  Video, 
  Code, 
  Megaphone,
  Activity,
  TrendingUp,
  Settings,
  RefreshCw
} from 'lucide-react';

interface SystemMetrics {
  gateway: {
    requests: number;
    responses: number;
    errors: number;
    uptime: number;
  };
  services: any;
  backend_metrics: {
    iris_fallback: {
      providers_available: number;
      success_rate: number;
    };
    silhouette_teams: {
      total_teams: number;
      active_teams: number;
      workflows_completed: number;
    };
    assets_generation: {
      images_generated: number;
      videos_generated: number;
      documents_generated: number;
    };
  };
}

const UnifiedDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [teams, setTeams] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      setRefreshing(true);
      
      // Fetch metrics and teams in parallel
      const [metricsData, teamsData] = await Promise.all([
        unifiedAPI.getUnifiedMetrics(),
        unifiedAPI.getAvailableTeams().catch(() => [])
      ]);

      setMetrics(metricsData);
      setTeams(teamsData || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const executeQuickAction = async (action: string, type: string) => {
    try {
      setRefreshing(true);
      
      switch (action) {
        case 'generate_text':
          const textResult = await unifiedAPI.generateWithFallback(
            'Genera un análisis de tendencias en IA para 2025'
          );
          console.log('Text generated:', textResult);
          break;
          
        case 'generate_image':
          const imageResult = await unifiedAPI.generateImage(
            'logo minimalista para una startup de IA',
            'minimalist',
            'branding'
          );
          console.log('Image generated:', imageResult);
          break;
          
        case 'execute_workflow':
          const workflowResult = await unifiedAPI.executeFullMarketingWorkflow({
            business_type: 'startup',
            target_audience: 'tech professionals'
          });
          console.log('Workflow executed:', workflowResult);
          break;
          
        case 'team_task':
          const teamResult = await unifiedAPI.executeMarketingCampaign({
            type: 'digital',
            budget: 'medium'
          });
          console.log('Team task executed:', teamResult);
          break;
      }
      
      // Refresh data after action
      setTimeout(fetchDashboardData, 2000);
    } catch (error) {
      console.error('Error executing action:', error);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>Cargando dashboard unificado...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">
              Dashboard Unificado IRIS + Silhouette
            </h1>
            <p className="text-lg text-gray-600 mt-2">
              Plataforma Integrada de Automatización Empresarial con 78+ Equipos Especializados
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Badge variant="outline" className="text-sm">
              Versión 4.0.0
            </Badge>
            <Button
              onClick={fetchDashboardData}
              disabled={refreshing}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Actualizar
            </Button>
          </div>
        </div>

        {/* Status Alert */}
        {metrics?.gateway && (
          <Alert className="border-green-200 bg-green-50">
            <Activity className="h-4 w-4" />
            <AlertDescription>
              <strong>Sistema Operativo:</strong> {metrics.gateway.uptime > 0 ? 'En Línea' : 'Desconectado'} • 
              <strong> Solicitudes:</strong> {metrics.gateway.requests} • 
              <strong> Tasa de Éxito:</strong> {((metrics.gateway.responses / Math.max(metrics.gateway.requests, 1)) * 100).toFixed(1)}%
            </AlertDescription>
          </Alert>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => executeQuickAction('generate_text', 'llm')}>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <Brain className="h-8 w-8 text-blue-600" />
                <div>
                  <h3 className="font-semibold">Generar Texto</h3>
                  <p className="text-sm text-gray-600">IA con Fallback Inteligente</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => executeQuickAction('generate_image', 'image')}>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <Image className="h-8 w-8 text-green-600" />
                <div>
                  <h3 className="font-semibold">Generar Imagen</h3>
                  <p className="text-sm text-gray-600">Freepik + VEO3 + HF</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => executeQuickAction('execute_workflow', 'workflow')}>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <Zap className="h-8 w-8 text-yellow-600" />
                <div>
                  <h3 className="font-semibold">Ejecutar Workflow</h3>
                  <p className="text-sm text-gray-600">78+ Equipos Coordinados</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => executeQuickAction('team_task', 'team')}>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <Users className="h-8 w-8 text-purple-600" />
                <div>
                  <h3 className="font-semibold">Tarea de Equipo</h3>
                  <p className="text-sm text-gray-600">Especialización Máxima</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Resumen</TabsTrigger>
            <TabsTrigger value="teams">Equipos</TabsTrigger>
            <TabsTrigger value="services">Servicios</TabsTrigger>
            <TabsTrigger value="assets">Assets</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Gateway Stats */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Activity className="h-5 w-5" />
                    <span>Gateway API</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {metrics?.gateway ? (
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm">Solicitudes</span>
                        <span className="font-semibold">{metrics.gateway.requests}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Respuestas</span>
                        <span className="font-semibold text-green-600">{metrics.gateway.responses}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Errores</span>
                        <span className="font-semibold text-red-600">{metrics.gateway.errors}</span>
                      </div>
                      <Progress 
                        value={((metrics.gateway.responses / Math.max(metrics.gateway.requests, 1)) * 100)} 
                        className="h-2"
                      />
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">Cargando...</p>
                  )}
                </CardContent>
              </Card>

              {/* Silhouette Teams */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Users className="h-5 w-5" />
                    <span>Equipos Silhouette</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {metrics?.backend_metrics?.silhouette_teams ? (
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm">Total</span>
                        <Badge variant="outline">{metrics.backend_metrics.silhouette_teams.total_teams}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Activos</span>
                        <Badge variant="secondary">{metrics.backend_metrics.silhouette_teams.active_teams}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Workflows</span>
                        <span className="font-semibold">{metrics.backend_metrics.silhouette_teams.workflows_completed}</span>
                      </div>
                      <Progress 
                        value={(metrics.backend_metrics.silhouette_teams.active_teams / metrics.backend_metrics.silhouette_teams.total_teams) * 100} 
                        className="h-2"
                      />
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">Cargando...</p>
                  )}
                </CardContent>
              </Card>

              {/* IRIS Fallback */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="h-5 w-5" />
                    <span>IRIS Fallback</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {metrics?.backend_metrics?.iris_fallback ? (
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm">Providers</span>
                        <Badge variant="outline">{metrics.backend_metrics.iris_fallback.providers_available}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Tasa de Éxito</span>
                        <span className="font-semibold text-green-600">
                          {(metrics.backend_metrics.iris_fallback.success_rate * 100).toFixed(1)}%
                        </span>
                      </div>
                      <Progress 
                        value={metrics.backend_metrics.iris_fallback.success_rate * 100} 
                        className="h-2"
                      />
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">Cargando...</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="teams" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Business Teams */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Megaphone className="h-5 w-5 text-blue-600" />
                    <span>Equipos de Negocio</span>
                  </CardTitle>
                  <CardDescription>25+ Equipos Especializados</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      Marketing Team
                    </Button>
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      Sales Team
                    </Button>
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      Finance Team
                    </Button>
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      HR Team
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Technical Teams */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Code className="h-5 w-5 text-green-600" />
                    <span>Equipos Técnicos</span>
                  </CardTitle>
                  <CardDescription>15+ Equipos Especializados</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      Development Team
                    </Button>
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      DevOps Team
                    </Button>
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      QA Team
                    </Button>
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      Security Team
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Audiovisual Teams */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Video className="h-5 w-5 text-purple-600" />
                    <span>Equipos Audiovisuales</span>
                  </CardTitle>
                  <CardDescription>15+ Equipos Especializados</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      Video Production
                    </Button>
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      Image Editing
                    </Button>
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      Audio Production
                    </Button>
                    <Button size="sm" variant="outline" className="w-full justify-start">
                      Animation Team
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="services" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Servicios Backend</CardTitle>
                  <CardDescription>Estado de todos los servicios integrados</CardDescription>
                </CardHeader>
                <CardContent>
                  {metrics?.services ? (
                    <div className="space-y-3">
                      {Object.entries(metrics.services).map(([name, service]: [string, any]) => (
                        <div key={name} className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${
                              service.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                            }`} />
                            <span className="capitalize">{name.replace('_', ' ')}</span>
                          </div>
                          <Badge variant={service.status === 'healthy' ? 'default' : 'destructive'}>
                            {service.status}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">Cargando servicios...</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>APIs Disponibles</CardTitle>
                  <CardDescription>Endpoints integrados en el gateway</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span>LLM con Fallback</span>
                      <Badge variant="outline">/api/llm/generate</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Generación de Imágenes</span>
                      <Badge variant="outline">/api/images/generate</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Workflows</span>
                      <Badge variant="outline">/api/workflows/execute</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Equipos</span>
                      <Badge variant="outline">/api/teams</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Chat</span>
                      <Badge variant="outline">/api/chat</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Métricas</span>
                      <Badge variant="outline">/api/metrics/unified</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="assets" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Image className="h-5 w-5 text-blue-600" />
                    <span>Imágenes</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {metrics?.backend_metrics?.assets_generation ? (
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600">
                        {metrics.backend_metrics.assets_generation.images_generated}
                      </div>
                      <p className="text-sm text-gray-600">Generadas</p>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">Cargando...</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Video className="h-5 w-5 text-green-600" />
                    <span>Videos</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {metrics?.backend_metrics?.assets_generation ? (
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600">
                        {metrics.backend_metrics.assets_generation.videos_generated}
                      </div>
                      <p className="text-sm text-gray-600">Generados</p>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">Cargando...</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="h-5 w-5 text-purple-600" />
                    <span>Documentos</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {metrics?.backend_metrics?.assets_generation ? (
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-600">
                        {metrics.backend_metrics.assets_generation.documents_generated}
                      </div>
                      <p className="text-sm text-gray-600">Creados</p>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">Cargando...</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default UnifiedDashboard;