// frontend/src/services/api.ts (PRODUCTION-READY API SERVICE)
import axios, { AxiosError, AxiosInstance } from 'axios';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface Task {
  id: string;
  task_id: string;
  title: string;
  description?: string;
  task_type: string;
  target: string;
  status: 'pending' | 'assigned' | 'executing' | 'completed' | 'failed' | 'timeout' | 'cancelled';
  priority: number;
  assigned_agents: string[];
  prediction?: TaskPrediction;
  result?: any;  // Full result object with agent_results
  output?: any;  // Agent outputs
  agent_results?: Record<string, any>;  // Individual agent results
  summary?: string;  // Task summary
  error_details?: any;
  created_at: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  execution_time?: number;  // Alternative name for duration
  success_rate?: number;
  quality_score?: number;
  tokens_used?: number;
  cost_usd?: number;
  total_cost_usd?: number;  // Total cost from all agents
}

export interface TaskPrediction {
  success_probability: number;
  estimated_duration: number;
  estimated_cost: number;
  quality_score_prediction: number;
  confidence: number;
  recommended_agents: RecommendedAgent[];
  risk_factors: string[];
  optimization_suggestions: string[];
  feature_importance?: Record<string, number>;
  model_version?: string;
}

export interface RecommendedAgent {
  agent_id: string;
  agent_name: string;
  expertise_score: number;
  estimated_duration: number;
  historical_success_rate: number;
  recommendation_confidence: number;
  reason: string;
}

export interface Agent {
  id: string;
  agent_id: string;
  name: string;
  type: string;
  status: 'active' | 'inactive' | 'maintenance' | 'error';
  capabilities: string[];
  configuration: Record<string, any>;
  system_prompt?: string;
  model_preference?: string;
  strategy?: string;
  performance_metrics?: AgentPerformanceMetrics;
  expertise_score: number;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  total_duration_seconds: number;
  total_tokens_used: number;
  total_cost_usd: number;
  last_execution_at?: string;
  created_at: string;
}

export interface AgentPerformanceMetrics {
  success_rate: number;
  avg_duration: number;
  avg_quality: number;
  total_cost: number;
}

export interface Integration {
  integration_id: string;
  user_id: string;
  platform: string;
  status: 'active' | 'inactive' | 'error' | 'pending';
  webhook_url?: string;
  created_at: string;
  last_sync?: string;
  sync_count: number;
  error_count: number;
}

export interface SystemMetrics {
  cpu_usage_percent: number;
  memory_usage_percent: number;
  memory_usage_bytes: number;
  disk_usage_bytes: number;
  active_tasks: number;
  queue_depth: number;
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  active_agents: number;
  timestamp: string;
}

export interface MLModelMetrics {
  model_name: string;
  accuracy: number;
  r2_score: number;
  mean_absolute_error: number;
  training_samples: number;
  last_training_date: string;
  feature_count: number;
  prediction_count_since_training: number;
}

export interface User {
  id: string;
  user_id: string;
  username: string;
  email: string;
  roles: string[];
  permissions: string[];
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
}

// ============================================================================
// API CLIENT CLASS
// ============================================================================

class APIService {
  private client: AxiosInstance;
  private accessToken: string | null = null;

  constructor() {
    this.client = axios.create({
      // Use relative URL to work with any port (recommended)
      // Falls back to environment variable or absolute URL if needed
      baseURL: import.meta.env.VITE_API_URL || '/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - add auth token and logging
    this.client.interceptors.request.use(
      (config) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        // Log API request
        if (import.meta.env.DEV) {
          console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
            params: config.params,
            data: config.data,
            timestamp: new Date().toISOString()
          });
        }
        return config;
      },
      (error) => {
        console.error('[API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor - handle errors and logging
    this.client.interceptors.response.use(
      (response) => {
        // Log successful API response
        if (import.meta.env.DEV) {
          console.log(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`, {
            data: response.data,
            timestamp: new Date().toISOString()
          });
        }
        return response;
      },
      async (error: AxiosError) => {
        // Log API error
        console.error(`[API] ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${error.response?.status || 'ERROR'}`, {
          error: error.message,
          response: error.response?.data,
          timestamp: new Date().toISOString()
        });
        
        if (error.response?.status === 401) {
          // Token expired - redirect to login
          console.warn('[API] Authentication failed - redirecting to login');
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );

    // Load token from localStorage
    this.loadToken();
  }

  // ========================================================================
  // AUTHENTICATION
  // ========================================================================

  setToken(token: string): void {
    this.accessToken = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  clearToken(): void {
    this.accessToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  loadToken(): void {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        this.accessToken = token;
      }
    }
  }

  async login(username: string, password: string): Promise<{ access_token: string; user: User }> {
    const response = await this.client.post('/login', { username, password });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post('/logout');
    this.clearToken();
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/me');
    return response.data;
  }

  // ========================================================================
  // TASKS
  // ========================================================================

  async listTasks(params?: {
    status?: string;
    task_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ tasks: Task[]; total: number }> {
    console.log('[API] Listing tasks', { params, timestamp: new Date().toISOString() });
    const response = await this.client.get('/tasks', { params });
    console.log('[API] Tasks listed', { count: response.data.tasks?.length || 0, total: response.data.total, timestamp: new Date().toISOString() });
    return response.data;
  }

  async getTask(taskId: string): Promise<Task> {
    console.log('[API] Getting task', { taskId, timestamp: new Date().toISOString() });
    const response = await this.client.get(`/tasks/${taskId}`);
    console.log('[API] Task retrieved', { taskId, status: response.data.status, hasResult: !!response.data.result, timestamp: new Date().toISOString() });
    return response.data;
  }

  async createTask(taskData: {
    title: string;
    description?: string;
    task_type: string;
    target: string;
    parameters?: Record<string, any>;
    priority?: number;
  }): Promise<Task> {
    console.log('[API] Creating task', { task_type: taskData.task_type, target: taskData.target, timestamp: new Date().toISOString() });
    const response = await this.client.post('/tasks', taskData);
    console.log('[API] Task created', { taskId: response.data.id || response.data.task_id, status: response.data.status, timestamp: new Date().toISOString() });
    return response.data;
  }

  async executeTask(taskId: string, options?: Record<string, any>): Promise<{
    task_id: string;
    status: string;
    message: string;
  }> {
    const response = await this.client.post(`/tasks/${taskId}/execute`, options);
    return response.data;
  }

  async getTaskProgress(taskId: string): Promise<{
    task_id: string;
    status: string;
    progress: number;
    elapsed_time?: number;
    estimated_remaining?: number;
  }> {
    const response = await this.client.get(`/tasks/${taskId}/progress`);
    return response.data;
  }

  async cancelTask(taskId: string): Promise<void> {
    await this.client.post(`/tasks/${taskId}/cancel`);
  }

  // ========================================================================
  // PREDICTIONS
  // ========================================================================

  async predictTask(taskData: {
    task_type: string;
    target: string;
    parameters?: Record<string, any>;
  }): Promise<TaskPrediction> {
    const response = await this.client.post('/predictions/predict/task', taskData);
    return response.data;
  }

  async predictSystemResources(timeHorizonMinutes: number = 60): Promise<{
    time_horizon_minutes: number;
    predicted_cpu_usage: number;
    predicted_memory_usage: number;
    predicted_task_load: number;
    predicted_api_calls: number;
    predicted_cost_per_hour: number;
    bottleneck_predictions: string[];
    scaling_recommendations: string[];
    confidence: number;
  }> {
    const response = await this.client.get('/predictions/predict/resources', {
      params: { time_horizon: timeHorizonMinutes },
    });
    return response.data;
  }

  async getModelMetrics(): Promise<MLModelMetrics[]> {
    const response = await this.client.get('/predictions/models/metrics');
    return response.data;
  }

  // ========================================================================
  // AGENTS
  // ========================================================================

  async listAgents(params?: {
    status?: string;
    type?: string;
  }): Promise<{ agents: Agent[]; total: number }> {
    const response = await this.client.get('/agents', { params });
    return response.data;
  }

  // Agent Management
  async startAgent(agentId: string): Promise<{ message: string }> {
    const response = await this.client.post(`/agents/${agentId}/start`);
    return response.data;
  }

  async stopAgent(agentId: string): Promise<{ message: string }> {
    const response = await this.client.post(`/agents/${agentId}/stop`);
    return response.data;
  }

  async getAgent(agentId: string): Promise<Agent> {
    const response = await this.client.get(`/agents/${agentId}`);
    return response.data;
  }

  async getAgentPerformance(): Promise<Agent[]> {
    const response = await this.client.get('/agents/performance');
    return response.data;
  }

  // ========================================================================
  // AI PROVIDERS
  // ========================================================================

  async getAIProviders(): Promise<{
    providers: Array<{
      id: string;
      name: string;
      model: string;
      type: string;
      priority: number;
      enabled: boolean;
      base_url?: string;
      available: boolean;
      models?: string[];
    }>;
    total: number;
    available: number;
  }> {
    const response = await this.client.get('/agents/ai-providers');
    return response.data;
  }

  async enableAIProvider(providerId: string): Promise<{
    provider_id: string;
    status: string;
    message: string;
    models?: string[];
  }> {
    const response = await this.client.post(`/agents/ai-providers/${providerId}/enable`);
    return response.data;
  }

  async getOllamaModels(): Promise<{
    models: Array<{
      name: string;
      size: number;
      modified_at: string;
    }>;
    total: number;
    available: boolean;
    error?: string;
  }> {
    const response = await this.client.get('/agents/ai-providers/ollama/models');
    return response.data;
  }

  // ========================================================================
  // INTEGRATIONS
  // ========================================================================

  async listIntegrations(params?: {
    platform?: string;
    status?: string;
  }): Promise<{ integrations: Integration[]; total: number }> {
    const response = await this.client.get('/integrations', { params });
    return response.data;
  }

  async createIntegration(integrationData: {
    platform: string;
    credentials: Record<string, any>;
    configuration?: Record<string, any>;
  }): Promise<Integration> {
    const response = await this.client.post('/integrations', integrationData);
    return response.data;
  }

  async deleteIntegration(integrationId: string): Promise<void> {
    await this.client.delete(`/integrations/${integrationId}`);
  }

  async triggerIntegration(
    integrationId: string,
    event_type: string,
    data: Record<string, any>
  ): Promise<any> {
    const response = await this.client.post(`/integrations/${integrationId}/trigger`, {
      event_type,
      data,
    });
    return response.data;
  }

  // ========================================================================
  // SYSTEM METRICS
  // ========================================================================

  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await this.client.get('/system/metrics');
    return response.data;
  }

  async getSystemHealth(): Promise<{
    status: string;
    components: Record<string, { status: string; details?: any }>;
    timestamp: string;
  }> {
    const response = await this.client.get('/system/health');
    return response.data;
  }

  // ========================================================================
  // ANALYTICS
  // ========================================================================

  async getTaskAnalytics(params?: {
    start_date?: string;
    end_date?: string;
    task_type?: string;
  }): Promise<{
    total_tasks: number;
    completed_tasks: number;
    failed_tasks: number;
    avg_duration: number;
    avg_quality_score: number;
    total_cost: number;
    success_rate: number;
    task_distribution: Record<string, number>;
  }> {
    const response = await this.client.get('/analytics/tasks', { params });
    return response.data;
  }

  async getAgentAnalytics(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<{
    agents: Array<{
      agent_id: string;
      agent_name: string;
      executions: number;
      success_rate: number;
      avg_duration: number;
      total_cost: number;
    }>;
  }> {
    const response = await this.client.get('/analytics/agents', { params });
    return response.data;
  }

  async getCostAnalytics(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<{
    total_cost: number;
    cost_by_provider: Record<string, number>;
    cost_by_agent: Record<string, number>;
    cost_trend: Array<{ date: string; cost: number }>;
  }> {
    const response = await this.client.get('/analytics/cost', { params });
    return response.data;
  }
}

// Export singleton instance
export const apiService = new APIService();

// Export class for testing
export default APIService;
