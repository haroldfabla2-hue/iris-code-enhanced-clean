// Servicio de API unificado para IRIS Code + Silhouette V4.0
import { getApiUrl, getConfig } from './config';
import { API_CONFIG } from './api';

export interface UnifiedAPIConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  gateway: {
    enabled: boolean;
    version: string;
    endpoints: {
      fallback: string;
      silhouette: string;
      assets: string;
      mcp: string;
      unified: {
        llm: string;
        chat: string;
        images: string;
        workflows: string;
        teams: string;
        metrics: string;
      };
    };
  };
}

class UnifiedAPIService {
  private config: UnifiedAPIConfig;
  private cache: Map<string, any> = new Map();

  constructor() {
    const appConfig = getConfig();
    this.config = {
      ...appConfig.api,
      gateway: {
        enabled: true,
        version: '4.0.0',
        endpoints: {
          fallback: '/api/fallback',
          silhouette: '/api/silhouette',
          assets: '/api/assets', 
          mcp: '/api/mcp',
          unified: {
            llm: '/api/llm/generate',
            chat: '/api/chat',
            images: '/api/images/generate',
            workflows: '/api/workflows/execute',
            teams: '/api/teams',
            metrics: '/api/metrics/unified'
          }
        }
      }
    } as UnifiedAPIConfig;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = getApiUrl(endpoint);
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Version': this.config.gateway.version,
        'X-Unified-Gateway': 'IRIS+Silhouette'
      },
      ...options
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // ===== SISTEMA DE FALLBACK INTELIGENTE (IRIS Code Original) =====
  
  async generateWithFallback(prompt: string, options: any = {}) {
    return this.request(this.config.gateway.unified.llm, {
      method: 'POST',
      body: JSON.stringify({
        prompt,
        provider: 'auto', // Auto-select best provider
        ...options
      })
    });
  }

  async generateImage(prompt: string, style: string = 'default', category: string = 'general') {
    return this.request(this.config.gateway.unified.images, {
      method: 'POST',
      body: JSON.stringify({
        prompt,
        style,
        category
      })
    });
  }

  // ===== FRAMEWORK SILHOUETTE V4.0 (78+ Equipos Especializados) =====

  async getAvailableTeams() {
    return this.request(this.config.gateway.unified.teams);
  }

  async executeTeam(teamId: string, task: string, parameters: any = {}) {
    return this.request(`/api/teams/${teamId}/execute`, {
      method: 'POST',
      body: JSON.stringify({
        task,
        parameters
      })
    });
  }

  async executeWorkflow(workflowName: string, parameters: any = {}) {
    return this.request(this.config.gateway.unified.workflows, {
      method: 'POST',
      body: JSON.stringify({
        workflow: workflowName,
        parameters
      })
    });
  }

  // ===== SISTEMA DE CHAT UNIFICADO =====

  async sendMessage(message: string, context: any = {}, stream: boolean = false) {
    return this.request(this.config.gateway.unified.chat, {
      method: 'POST',
      body: JSON.stringify({
        message,
        context,
        stream
      })
    });
  }

  // ===== GENERACIÓN DE ASSETS ESPECIALIZADA =====

  async generateBrandingAssets(requirements: any) {
    return this.request('/api/assets/branding', {
      method: 'POST',
      body: JSON.stringify({ requirements })
    });
  }

  async generateMarketingAssets(requirements: any) {
    return this.request('/api/assets/marketing', {
      method: 'POST',
      body: JSON.stringify({ requirements })
    });
  }

  async generateMobileAssets(requirements: any) {
    return this.request('/api/assets/mobile', {
      method: 'POST',
      body: JSON.stringify({ requirements })
    });
  }

  // ===== MONITOREO Y MÉTRICAS =====

  async getUnifiedMetrics() {
    return this.request(this.config.gateway.unified.metrics);
  }

  async getSystemStatus() {
    return this.request('/status');
  }

  async getHealthCheck() {
    return this.request('/health');
  }

  // ===== EQUIPOS ESPECIALIZADOS PREDEFINIDOS =====

  // Equipos de Marketing (25+ equipos)
  async executeMarketingCampaign(campaign: any) {
    return this.executeTeam('marketing_team', 'create_campaign', campaign);
  }

  async generateContent(contentType: string, requirements: any) {
    return this.executeTeam('content_team', 'generate_content', { contentType, ...requirements });
  }

  async performSEO(website: any) {
    return this.executeTeam('seo_team', 'analyze_website', website);
  }

  async manageSocialMedia(platform: string, content: any) {
    return this.executeTeam('social_media_team', 'manage_platform', { platform, ...content });
  }

  // Equipos Financieros (10+ equipos)
  async analyzeFinancials(data: any) {
    return this.executeTeam('financial_analysis_team', 'analyze_financials', data);
  }

  async generateReport(reportType: string, data: any) {
    return this.executeTeam('reporting_team', 'generate_report', { reportType, ...data });
  }

  // Equipos Técnicos (15+ equipos)
  async codeReview(code: any) {
    return this.executeTeam('code_review_team', 'review_code', code);
  }

  async generateTests(testType: string, code: any) {
    return this.executeTeam('testing_team', 'generate_tests', { testType, ...code });
  }

  async deployApplication(appConfig: any) {
    return this.executeTeam('devops_team', 'deploy_application', appConfig);
  }

  // Equipos de Audiovisual (15+ equipos)
  async generateVideo(videoConfig: any) {
    return this.executeTeam('video_production_team', 'generate_video', videoConfig);
  }

  async createPresentation(presentation: any) {
    return this.executeTeam('presentation_team', 'create_presentation', presentation);
  }

  async editImage(imageConfig: any) {
    return this.executeTeam('image_editing_team', 'edit_image', imageConfig);
  }

  // ===== WORKFLOWS PREDEFINIDOS =====

  async executeFullMarketingWorkflow(requirements: any) {
    const workflow = 'complete_marketing_campaign';
    return this.executeWorkflow(workflow, requirements);
  }

  async executeProductLaunchWorkflow(requirements: any) {
    const workflow = 'product_launch';
    return this.executeWorkflow(workflow, requirements);
  }

  async executeWebsiteDevelopmentWorkflow(requirements: any) {
    const workflow = 'website_development';
    return this.executeWorkflow(workflow, requirements);
  }

  async executeBrandCreationWorkflow(requirements: any) {
    const workflow = 'brand_creation';
    return this.executeWorkflow(workflow, requirements);
  }

  // ===== INTEGRACIÓN CON APIS EXISTENTES =====

  // Usar OpenRouter con fallback inteligente
  async generateTextAdvanced(prompt: string, options: any = {}) {
    return this.generateWithFallback(prompt, {
      model: 'meta-llama/llama-3.1-70b-instruct:free',
      max_tokens: 4000,
      ...options
    });
  }

  // Generar imágenes con Freepik como principal
  async generateProfessionalImage(prompt: string, style: string = 'professional') {
    return this.generateImage(prompt, style, 'professional');
  }

  // Chat con contexto persistente
  async chatWithContext(message: string, conversationId?: string) {
    return this.sendMessage(message, { conversationId }, true);
  }

  // ===== UTILIDADES =====

  // Cache management
  setCache(key: string, value: any, ttl: number = 300000) { // 5 minutos
    this.cache.set(key, {
      value,
      expires: Date.now() + ttl
    });
  }

  getCache(key: string) {
    const cached = this.cache.get(key);
    if (cached && cached.expires > Date.now()) {
      return cached.value;
    }
    this.cache.delete(key);
    return null;
  }

  clearCache() {
    this.cache.clear();
  }

  // Utility para verificar conectividad
  async ping() {
    try {
      await this.getHealthCheck();
      return { status: 'connected', latency: 0 };
    } catch (error) {
      return { status: 'disconnected', error: error.message };
    }
  }
}

// Export singleton instance
export const unifiedAPI = new UnifiedAPIService();
export default unifiedAPI;