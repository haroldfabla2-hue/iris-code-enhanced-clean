import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Zap, 
  Database, 
  History, 
  Play, 
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Cpu,
  FileText,
  Search,
  Code,
  Globe
} from 'lucide-react';
import { mcpClient, ToolRequest, ToolResponse, ToolsListResponse, ExecutionStatus } from '../../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { ScrollArea } from '../ui/scroll-area';

interface ExecutionHistory {
  id: string;
  tool_name: string;
  executor_type: string;
  status: string;
  result?: any;
  error?: string;
  execution_time_ms: number;
  started_at: string;
  parameters: Record<string, any>;
}

export default function ToolManager() {
  const [activeTab, setActiveTab] = useState('catalog');
  const [availableTools, setAvailableTools] = useState<ToolsListResponse | null>(null);
  const [isLoadingTools, setIsLoadingTools] = useState(false);
  const [executionHistory, setExecutionHistory] = useState<ExecutionHistory[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<ToolResponse | null>(null);

  // Form state for tool execution
  const [selectedTool, setSelectedTool] = useState('');
  const [selectedExecutor, setSelectedExecutor] = useState('general');
  const [toolParameters, setToolParameters] = useState('{}');
  const [customParameters, setCustomParameters] = useState('');
  const [asyncMode, setAsyncMode] = useState(false);
  const [userId, setUserId] = useState('');

  // Filters
  const [statusFilter, setStatusFilter] = useState('all');
  const [executorFilter, setExecutorFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadAvailableTools();
    loadExecutionHistory();
  }, []);

  const loadAvailableTools = async () => {
    setIsLoadingTools(true);
    try {
      const tools = await mcpClient.listAvailableTools();
      setAvailableTools(tools);
    } catch (error) {
      console.error('Failed to load tools:', error);
    } finally {
      setIsLoadingTools(false);
    }
  };

  const loadExecutionHistory = () => {
    // Load from localStorage for persistence
    const stored = localStorage.getItem('tool_execution_history');
    if (stored) {
      try {
        setExecutionHistory(JSON.parse(stored));
      } catch (error) {
        console.error('Failed to load execution history:', error);
      }
    }
  };

  const saveExecutionHistory = (history: ExecutionHistory[]) => {
    localStorage.setItem('tool_execution_history', JSON.stringify(history));
  };

  const executeTool = async () => {
    if (!selectedTool) return;

    setIsExecuting(true);
    setExecutionResult(null);

    try {
      let parameters = {};
      
      // Parse tool-specific parameters
      if (selectedTool === 'web_search') {
        parameters = {
          query: JSON.parse(toolParameters).query || '',
          num_results: JSON.parse(toolParameters).num_results || 5
        };
      } else if (selectedTool === 'python_execute') {
        parameters = {
          code: JSON.parse(toolParameters).code || '',
          timeout: JSON.parse(toolParameters).timeout || 30
        };
      } else if (selectedTool === 'web_scrape') {
        parameters = {
          url: JSON.parse(toolParameters).url || '',
          selector: JSON.parse(toolParameters).selector || ''
        };
      } else if (selectedTool === 'pdf_extract') {
        parameters = {
          file_path: JSON.parse(toolParameters).file_path || '',
          pages: JSON.parse(toolParameters).pages || 1
        };
      } else if (selectedTool === 'text_analysis') {
        parameters = {
          text: JSON.parse(toolParameters).text || '',
          analysis_type: JSON.parse(toolParameters).analysis_type || 'general'
        };
      }

      // Add custom parameters if provided
      if (customParameters.trim()) {
        try {
          const custom = JSON.parse(customParameters);
          parameters = { ...parameters, ...custom };
        } catch (error) {
          console.error('Invalid custom parameters JSON:', error);
          Alert('Error: Parámetros personalizados inválidos');
          return;
        }
      }

      const request: ToolRequest = {
        tool_name: selectedTool,
        parameters,
        executor_type: selectedExecutor,
        user_id: userId || undefined,
        async_mode: asyncMode
      };

      const result = await mcpClient.executeTool(request);
      
      if (result) {
        setExecutionResult(result);
        
        // Add to history
        const historyItem: ExecutionHistory = {
          id: result.execution_id,
          tool_name: result.tool_name,
          executor_type: selectedExecutor,
          status: result.status,
          result: result.result,
          error: result.error,
          execution_time_ms: result.execution_time_ms,
          started_at: new Date().toISOString(),
          parameters
        };

        const newHistory = [historyItem, ...executionHistory.slice(0, 99)]; // Keep last 100
        setExecutionHistory(newHistory);
        saveExecutionHistory(newHistory);
      }
    } catch (error) {
      console.error('Tool execution failed:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  const getExecutorIcon = (executor: string) => {
    switch (executor) {
      case 'code': return <Code className="h-4 w-4" />;
      case 'web': return <Globe className="h-4 w-4" />;
      case 'docs': return <FileText className="h-4 w-4" />;
      default: return <Settings className="h-4 w-4" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'timeout': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'started': return <Play className="h-4 w-4 text-blue-500" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-100 text-green-800';
      case 'error': return 'bg-red-100 text-red-800';
      case 'timeout': return 'bg-yellow-100 text-yellow-800';
      case 'started': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredHistory = executionHistory.filter(item => {
    if (statusFilter !== 'all' && item.status !== statusFilter) return false;
    if (executorFilter !== 'all' && item.executor_type !== executorFilter) return false;
    if (searchQuery && !item.tool_name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const renderParameterForm = () => {
    switch (selectedTool) {
      case 'web_search':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="query">Query de búsqueda</Label>
              <Input
                id="query"
                placeholder="Términos de búsqueda"
                onChange={(e) => {
                  const params = JSON.parse(toolParameters || '{}');
                  params.query = e.target.value;
                  setToolParameters(JSON.stringify(params));
                }}
              />
            </div>
            <div>
              <Label htmlFor="numResults">Número de resultados</Label>
              <Input
                id="numResults"
                type="number"
                min="1"
                max="20"
                defaultValue="5"
                onChange={(e) => {
                  const params = JSON.parse(toolParameters || '{}');
                  params.num_results = parseInt(e.target.value);
                  setToolParameters(JSON.stringify(params));
                }}
              />
            </div>
          </div>
        );
      
      case 'python_execute':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="code">Código Python</Label>
              <Textarea
                id="code"
                placeholder="print('Hello, World!')"
                rows={6}
                onChange={(e) => {
                  const params = JSON.parse(toolParameters || '{}');
                  params.code = e.target.value;
                  setToolParameters(JSON.stringify(params));
                }}
              />
            </div>
            <div>
              <Label htmlFor="timeout">Timeout (segundos)</Label>
              <Input
                id="timeout"
                type="number"
                min="1"
                max="300"
                defaultValue="30"
                onChange={(e) => {
                  const params = JSON.parse(toolParameters || '{}');
                  params.timeout = parseInt(e.target.value);
                  setToolParameters(JSON.stringify(params));
                }}
              />
            </div>
          </div>
        );
      
      case 'web_scrape':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="url">URL</Label>
              <Input
                id="url"
                placeholder="https://example.com"
                onChange={(e) => {
                  const params = JSON.parse(toolParameters || '{}');
                  params.url = e.target.value;
                  setToolParameters(JSON.stringify(params));
                }}
              />
            </div>
            <div>
              <Label htmlFor="selector">CSS Selector (opcional)</Label>
              <Input
                id="selector"
                placeholder=".content, #main, etc."
                onChange={(e) => {
                  const params = JSON.parse(toolParameters || '{}');
                  params.selector = e.target.value;
                  setToolParameters(JSON.stringify(params));
                }}
              />
            </div>
          </div>
        );
      
      case 'pdf_extract':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="filePath">Ruta del archivo PDF</Label>
              <Input
                id="filePath"
                placeholder="/path/to/document.pdf"
                onChange={(e) => {
                  const params = JSON.parse(toolParameters || '{}');
                  params.file_path = e.target.value;
                  setToolParameters(JSON.stringify(params));
                }}
              />
            </div>
            <div>
              <Label htmlFor="pages">Páginas a extraer</Label>
              <Input
                id="pages"
                type="number"
                min="1"
                defaultValue="1"
                onChange={(e) => {
                  const params = JSON.parse(toolParameters || '{}');
                  params.pages = parseInt(e.target.value);
                  setToolParameters(JSON.stringify(params));
                }}
              />
            </div>
          </div>
        );
      
      case 'text_analysis':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="text">Texto a analizar</Label>
              <Textarea
                id="text"
                placeholder="Texto para análisis..."
                rows={4}
                onChange={(e) => {
                  const params = JSON.parse(toolParameters || '{}');
                  params.text = e.target.value;
                  setToolParameters(JSON.stringify(params));
                }}
              />
            </div>
            <div>
              <Label htmlFor="analysisType">Tipo de análisis</Label>
              <Select onValueChange={(value) => {
                const params = JSON.parse(toolParameters || '{}');
                params.analysis_type = value;
                setToolParameters(JSON.stringify(params));
              }}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sentiment">Sentimiento</SelectItem>
                  <SelectItem value="keywords">Palabras clave</SelectItem>
                  <SelectItem value="summary">Resumen</SelectItem>
                  <SelectItem value="entities">Entidades</SelectItem>
                  <SelectItem value="general">General</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        );
      
      default:
        return (
          <div>
            <Label htmlFor="customParams">Parámetros (JSON)</Label>
            <Textarea
              id="customParams"
              placeholder='{"param1": "value1", "param2": "value2"}'
              rows={4}
              value={toolParameters}
              onChange={(e) => setToolParameters(e.target.value)}
            />
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Herramientas</h1>
        <p className="text-muted-foreground">
          Ejecuta herramientas especializadas para búsqueda web, análisis de código, scraping y más.
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="catalog" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            Catálogo
          </TabsTrigger>
          <TabsTrigger value="execute" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Ejecutar
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            Historial
          </TabsTrigger>
          <TabsTrigger value="monitor" className="flex items-center gap-2">
            <Cpu className="h-4 w-4" />
            Monitor
          </TabsTrigger>
        </TabsList>

        <TabsContent value="catalog" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Catálogo de Herramientas
              </CardTitle>
              <CardDescription>
                Herramientas disponibles organizadas por tipo de executor
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingTools ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : availableTools ? (
                <div className="space-y-6">
                  {availableTools.executors.map(executorType => (
                    <div key={executorType} className="space-y-3">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        {getExecutorIcon(executorType)}
                        {executorType.charAt(0).toUpperCase() + executorType.slice(1)}
                      </h3>
                      <div className="grid gap-3">
                        {availableTools.tools
                          .filter(tool => tool.executor_type === executorType)
                          .map(tool => (
                            <Card key={tool.name} className="p-4">
                              <div className="flex items-start justify-between">
                                <div className="space-y-1">
                                  <h4 className="font-medium">{tool.name}</h4>
                                  <p className="text-sm text-muted-foreground">{tool.description}</p>
                                  <div className="flex flex-wrap gap-1">
                                    {tool.parameters.map(param => (
                                      <Badge key={param} variant="secondary" className="text-xs">
                                        {param}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                                <Button
                                  size="sm"
                                  onClick={() => {
                                    setSelectedTool(tool.name);
                                    setSelectedExecutor(tool.executor_type);
                                    setActiveTab('execute');
                                  }}
                                >
                                  Usar
                                </Button>
                              </div>
                            </Card>
                          ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    No se pudieron cargar las herramientas disponibles.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="execute" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Ejecutar Herramienta
                </CardTitle>
                <CardDescription>
                  Configura y ejecuta una herramienta específica
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="tool">Herramienta</Label>
                  <Select value={selectedTool} onValueChange={setSelectedTool}>
                    <SelectTrigger>
                      <SelectValue placeholder="Seleccionar herramienta" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableTools?.tools.map(tool => (
                        <SelectItem key={tool.name} value={tool.name}>
                          {tool.name} - {tool.description}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="executor">Tipo de Executor</Label>
                  <Select value={selectedExecutor} onValueChange={setSelectedExecutor}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {availableTools?.executors.map(executor => (
                        <SelectItem key={executor} value={executor}>
                          {executor}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="userId">User ID (opcional)</Label>
                  <Input
                    id="userId"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="ID del usuario"
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="asyncMode"
                    checked={asyncMode}
                    onChange={(e) => setAsyncMode(e.target.checked)}
                    className="rounded"
                  />
                  <Label htmlFor="asyncMode">Modo asíncrono</Label>
                </div>

                {selectedTool && (
                  <div>
                    <Label>Parámetros</Label>
                    {renderParameterForm()}
                  </div>
                )}

                <Button 
                  onClick={executeTool} 
                  disabled={!selectedTool || isExecuting}
                  className="w-full"
                >
                  {isExecuting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Ejecutando...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Ejecutar Herramienta
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Resultado de Ejecución</CardTitle>
                <CardDescription>
                  Salida de la herramienta ejecutada
                </CardDescription>
              </CardHeader>
              <CardContent>
                {executionResult ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(executionResult.status)}
                        <span className="font-medium">{executionResult.status}</span>
                      </div>
                      <Badge className={getStatusColor(executionResult.status)}>
                        {executionResult.execution_time_ms}ms
                      </Badge>
                    </div>
                    
                    {executionResult.error && (
                      <Alert>
                        <XCircle className="h-4 w-4" />
                        <AlertDescription className="text-red-600">
                          {executionResult.error}
                        </AlertDescription>
                      </Alert>
                    )}
                    
                    {executionResult.result && (
                      <div>
                        <Label>Resultado</Label>
                        <ScrollArea className="h-40 w-full rounded border p-2">
                          <pre className="text-sm whitespace-pre-wrap">
                            {JSON.stringify(executionResult.result, null, 2)}
                          </pre>
                        </ScrollArea>
                      </div>
                    )}
                    
                    {executionResult.metadata && (
                      <div>
                        <Label>Metadatos</Label>
                        <ScrollArea className="h-32 w-full rounded border p-2">
                          <pre className="text-sm whitespace-pre-wrap">
                            {JSON.stringify(executionResult.metadata, null, 2)}
                          </pre>
                        </ScrollArea>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground py-8">
                    <Zap className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>Ejecuta una herramienta para ver el resultado</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" />
                Historial de Ejecuciones
              </CardTitle>
              <CardDescription>
                Historial de herramientas ejecutadas recientemente
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Buscar herramientas..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos</SelectItem>
                    <SelectItem value="success">Exitosas</SelectItem>
                    <SelectItem value="error">Errores</SelectItem>
                    <SelectItem value="timeout">Timeouts</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={executorFilter} onValueChange={setExecutorFilter}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos</SelectItem>
                    {availableTools?.executors.map(executor => (
                      <SelectItem key={executor} value={executor}>
                        {executor}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <ScrollArea className="h-96">
                <div className="space-y-3">
                  {filteredHistory.length === 0 ? (
                    <div className="text-center text-muted-foreground py-8">
                      <History className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>No hay ejecuciones en el historial</p>
                    </div>
                  ) : (
                    filteredHistory.map((item) => (
                      <Card key={item.id} className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              {getExecutorIcon(item.executor_type)}
                              <span className="font-medium">{item.tool_name}</span>
                              {getStatusIcon(item.status)}
                            </div>
                            <p className="text-sm text-muted-foreground">
                              {new Date(item.started_at).toLocaleString()}
                            </p>
                            <div className="flex flex-wrap gap-1">
                              <Badge className={getStatusColor(item.status)}>
                                {item.status}
                              </Badge>
                              <Badge variant="outline">
                                {item.execution_time_ms}ms
                              </Badge>
                            </div>
                          </div>
                        </div>
                        {item.result && (
                          <div className="mt-3">
                            <Label className="text-xs">Resultado</Label>
                            <ScrollArea className="h-24 w-full rounded border p-2">
                              <pre className="text-xs whitespace-pre-wrap">
                                {JSON.stringify(item.result, null, 2)}
                              </pre>
                            </ScrollArea>
                          </div>
                        )}
                        {item.error && (
                          <Alert className="mt-3">
                            <XCircle className="h-4 w-4" />
                            <AlertDescription className="text-red-600 text-sm">
                              {item.error}
                            </AlertDescription>
                          </Alert>
                        )}
                      </Card>
                    ))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="monitor" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cpu className="h-5 w-5" />
                Monitor de Sistema
              </CardTitle>
              <CardDescription>
                Estado de las herramientas y ejecutores
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Estado de Ejecutores</h3>
                  {availableTools?.executors.map(executor => {
                    const executorHistory = executionHistory.filter(h => h.executor_type === executor);
                    const recentExecutions = executorHistory.filter(h => 
                      new Date(h.started_at) > new Date(Date.now() - 24 * 60 * 60 * 1000)
                    );
                    const successRate = recentExecutions.length > 0 
                      ? (recentExecutions.filter(h => h.status === 'success').length / recentExecutions.length * 100).toFixed(1)
                      : '0';

                    return (
                      <Card key={executor} className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {getExecutorIcon(executor)}
                            <span className="font-medium capitalize">{executor}</span>
                          </div>
                          <div className="text-right text-sm">
                            <div>{recentExecutions.length} ejecuciones (24h)</div>
                            <div className="text-muted-foreground">{successRate}% éxito</div>
                          </div>
                        </div>
                      </Card>
                    );
                  })}
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Estadísticas</h3>
                  <Card className="p-4">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Total de ejecuciones</span>
                        <span className="font-medium">{executionHistory.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Ejecuciones exitosas</span>
                        <span className="font-medium text-green-600">
                          {executionHistory.filter(h => h.status === 'success').length}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Ejecuciones fallidas</span>
                        <span className="font-medium text-red-600">
                          {executionHistory.filter(h => h.status === 'error').length}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Tiempo promedio</span>
                        <span className="font-medium">
                          {executionHistory.length > 0 
                            ? Math.round(executionHistory.reduce((sum, h) => sum + h.execution_time_ms, 0) / executionHistory.length)
                            : 0}ms
                        </span>
                      </div>
                    </div>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}