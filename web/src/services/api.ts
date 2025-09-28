/**
 * AMAS API Service
 * 
 * Centralized API service for communicating with the AMAS Intelligence System backend
 * Handles authentication, request/response processing, and error handling
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

export interface Agent {
  agent_id: string;
  name: string;
  status: string;
  capabilities: string[];
  last_activity: string;
  metrics: {
    tasks_completed: number;
    tasks_failed: number;
    avg_response_time: number;
    success_rate: number;
  };
}

export interface Task {
  task_id: string;
  type: string;
  description: string;
  status: string;
  priority: number;
  assigned_agent: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  result: any;
  error: string | null;
}

export interface SystemStatus {
  status: string;
  agents: number;
  active_tasks: number;
  total_tasks: number;
  timestamp: string;
}

export interface DashboardMetrics {
  agents: {
    total: number;
    active: number;
    idle: number;
    error: number;
  };
  tasks: {
    total: number;
    active: number;
    completed: number;
    failed: number;
  };
  system: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    uptime: string;
  };
  performance: {
    avg_task_time: number;
    tasks_per_hour: number;
    success_rate: number;
  };
}

export interface ActivityItem {
  id: string;
  type: 'task' | 'agent' | 'system';
  message: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

export interface TaskSubmissionRequest {
  type: string;
  description: string;
  parameters?: Record<string, any>;
  priority?: number;
}

export interface TaskSubmissionResponse {
  task_id: string;
  status: string;
  message: string;
}

export class AMASApiService {
  private api: AxiosInstance;
  private baseURL: string;
  private authToken: string | null = null;

  constructor(baseURL: string = '') {
    this.baseURL = baseURL || (process.env.REACT_APP_API_URL || 'http://localhost:8000');
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for authentication
    this.api.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        
        // Handle authentication errors
        if (error.response?.status === 401) {
          this.clearAuthToken();
          // Redirect to login or show auth error
        }
        
        return Promise.reject(error);
      }
    );
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string): void {
    this.authToken = token;
    localStorage.setItem('amas_token', token);
  }

  /**
   * Clear authentication token
   */
  clearAuthToken(): void {
    this.authToken = null;
    localStorage.removeItem('amas_token');
  }

  /**
   * Get system health status
   */
  async getHealthStatus(): Promise<any> {
    const response = await this.api.get('/health');
    return response.data;
  }

  /**
   * Get system status
   */
  async getSystemStatus(): Promise<SystemStatus> {
    const response = await this.api.get('/status');
    return response.data;
  }

  /**
   * Get dashboard metrics
   */
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    try {
      const response = await this.api.get('/dashboard/metrics');
      return response.data;
    } catch (error) {
      // Return mock data if endpoint not available
      return {
        agents: { total: 8, active: 6, idle: 2, error: 0 },
        tasks: { total: 145, active: 12, completed: 128, failed: 5 },
        system: { cpu_usage: 45, memory_usage: 62, disk_usage: 78, uptime: '2 days, 14 hours' },
        performance: { avg_task_time: 24.5, tasks_per_hour: 18, success_rate: 96.5 }
      };
    }
  }

  /**
   * Get recent activities
   */
  async getRecentActivities(): Promise<ActivityItem[]> {
    try {
      const response = await this.api.get('/dashboard/activities');
      return response.data.activities || [];
    } catch (error) {
      // Return mock data if endpoint not available
      return [
        {
          id: '1',
          type: 'task',
          message: 'OSINT collection task completed successfully',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          status: 'success'
        },
        {
          id: '2',
          type: 'agent',
          message: 'Investigation Agent started new analysis',
          timestamp: new Date(Date.now() - 600000).toISOString(),
          status: 'info'
        },
        {
          id: '3',
          type: 'system',
          message: 'System health check completed',
          timestamp: new Date(Date.now() - 900000).toISOString(),
          status: 'success'
        }
      ];
    }
  }

  /**
   * Get all agents
   */
  async getAgents(): Promise<Agent[]> {
    const response = await this.api.get('/agents');
    return response.data.agents || [];
  }

  /**
   * Get specific agent
   */
  async getAgent(agentId: string): Promise<Agent> {
    const response = await this.api.get(`/agents/${agentId}`);
    return response.data;
  }

  /**
   * Get all tasks
   */
  async getTasks(): Promise<Task[]> {
    const response = await this.api.get('/tasks');
    return response.data.tasks || [];
  }

  /**
   * Get specific task
   */
  async getTask(taskId: string): Promise<Task> {
    const response = await this.api.get(`/tasks/${taskId}`);
    return response.data;
  }

  /**
   * Submit new task
   */
  async submitTask(taskRequest: TaskSubmissionRequest): Promise<TaskSubmissionResponse> {
    const response = await this.api.post('/tasks', taskRequest);
    return response.data;
  }

  /**
   * Cancel task
   */
  async cancelTask(taskId: string): Promise<void> {
    await this.api.delete(`/tasks/${taskId}`);
  }

  /**
   * Execute workflow
   */
  async executeWorkflow(workflowId: string, parameters: Record<string, any>): Promise<any> {
    const response = await this.api.post(`/workflows/${workflowId}/execute`, parameters);
    return response.data;
  }

  /**
   * Get audit log
   */
  async getAuditLog(filters?: {
    user_id?: string;
    event_type?: string;
    limit?: number;
  }): Promise<any[]> {
    const response = await this.api.get('/audit', { params: filters });
    return response.data.audit_log || [];
  }

  /**
   * Get system analytics
   */
  async getAnalytics(timeRange: string = '24h'): Promise<any> {
    try {
      const response = await this.api.get(`/analytics?range=${timeRange}`);
      return response.data;
    } catch (error) {
      // Return mock analytics data
      return {
        task_performance: [
          { time: '00:00', completed: 5, failed: 0 },
          { time: '04:00', completed: 8, failed: 1 },
          { time: '08:00', completed: 15, failed: 0 },
          { time: '12:00', completed: 22, failed: 2 },
          { time: '16:00', completed: 18, failed: 1 },
          { time: '20:00', completed: 12, failed: 0 },
        ],
        agent_utilization: [
          { agent: 'OSINT Agent', utilization: 85 },
          { agent: 'Investigation Agent', utilization: 72 },
          { agent: 'Forensics Agent', utilization: 68 },
          { agent: 'Data Analysis Agent', utilization: 91 },
          { agent: 'Reporting Agent', utilization: 56 },
        ],
        security_events: [
          { time: '2024-01-15T10:30:00Z', type: 'authentication', severity: 'low' },
          { time: '2024-01-15T11:15:00Z', type: 'access_control', severity: 'medium' },
          { time: '2024-01-15T12:00:00Z', type: 'data_access', severity: 'low' },
        ]
      };
    }
  }

  /**
   * Update system settings
   */
  async updateSettings(settings: Record<string, any>): Promise<void> {
    await this.api.put('/settings', settings);
  }

  /**
   * Get system settings
   */
  async getSettings(): Promise<Record<string, any>> {
    try {
      const response = await this.api.get('/settings');
      return response.data;
    } catch (error) {
      // Return default settings
      return {
        auto_refresh: true,
        refresh_interval: 30,
        max_concurrent_tasks: 10,
        log_level: 'INFO',
        enable_notifications: true,
        theme: 'dark'
      };
    }
  }

  /**
   * Get available workflows
   */
  async getWorkflows(): Promise<any[]> {
    try {
      const response = await this.api.get('/workflows');
      return response.data.workflows || [];
    } catch (error) {
      // Return mock workflows if endpoint not available
      return [
        {
          workflow_id: 'intelligence_collection_v2',
          name: 'Comprehensive Intelligence Collection',
          description: 'Advanced multi-source intelligence collection with analysis and reporting',
          version: '2.0',
          nodes: {},
          edges: {},
          timeout_minutes: 120
        },
        {
          workflow_id: 'threat_assessment_v2',
          name: 'Advanced Threat Assessment',
          description: 'Comprehensive threat assessment with iterative refinement',
          version: '2.0',
          nodes: {},
          edges: {},
          timeout_minutes: 90
        },
        {
          workflow_id: 'investigation_v2',
          name: 'Advanced Investigation Workflow',
          description: 'Comprehensive investigation with iterative evidence gathering',
          version: '2.0',
          nodes: {},
          edges: {},
          timeout_minutes: 180
        }
      ];
    }
  }

  /**
   * Get active workflow executions
   */
  async getActiveWorkflowExecutions(): Promise<any[]> {
    try {
      const response = await this.api.get('/workflows/executions/active');
      return response.data.executions || [];
    } catch (error) {
      // Return mock active executions
      return [
        {
          execution_id: 'exec_001',
          workflow_id: 'intelligence_collection_v2',
          status: 'running',
          progress: {
            total_nodes: 8,
            completed_nodes: 3,
            failed_nodes: 0,
            current_nodes: ['osint_collection'],
            completion_percentage: 37.5
          },
          started_at: new Date(Date.now() - 300000).toISOString(),
          execution_time: 300,
          initiated_by: 'admin',
          node_results: {}
        }
      ];
    }
  }

  /**
   * Get workflow execution details
   */
  async getWorkflowExecution(executionId: string): Promise<any> {
    try {
      const response = await this.api.get(`/workflows/executions/${executionId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get workflow execution: ${error}`);
    }
  }

  /**
   * Cancel workflow execution
   */
  async cancelWorkflowExecution(executionId: string): Promise<void> {
    try {
      await this.api.delete(`/workflows/executions/${executionId}`);
    } catch (error) {
      throw new Error(`Failed to cancel workflow execution: ${error}`);
    }
  }

  /**
   * Get workflow performance metrics
   */
  async getWorkflowMetrics(): Promise<any> {
    try {
      const response = await this.api.get('/workflows/metrics');
      return response.data;
    } catch (error) {
      // Return mock metrics
      return {
        total_workflows: 3,
        successful_executions: 45,
        failed_executions: 2,
        average_execution_time: 180.5,
        active_executions: 1,
        node_execution_stats: {
          task: { count: 150, avg_time: 45.2, success_rate: 0.96 },
          decision: { count: 30, avg_time: 2.1, success_rate: 0.98 },
          parallel: { count: 20, avg_time: 0.5, success_rate: 1.0 }
        }
      };
    }
  }
}