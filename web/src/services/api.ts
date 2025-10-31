import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '30000');

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('amas_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('amas_token');
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Request timeout. Please check your connection.');
    }
    return Promise.reject(error);
  }
);

// API Types
export interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'busy' | 'error';
  capabilities: string[];
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  agent_id: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high';
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface SystemHealth {
  status: 'healthy' | 'unhealthy';
  timestamp: number;
  version: string;
  uptime: number;
  services: {
    database: string;
    redis: string;
    neo4j: string;
  };
}

export interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_connections: number;
  timestamp: number;
}

export interface TaskStatus {
  task_id: string;
  status: string;
  progress: number;
  started_at: string;
  estimated_completion: string;
  current_step: string;
  logs: string[];
}

export interface TaskResult {
  task_id: string;
  status: string;
  result: {
    data: any;
    metrics: {
      processing_time: number;
      accuracy: number;
      confidence: number;
    };
  };
  completed_at: string;
}

// API Service Class
class APIService {
  // Health & System
  async getHealth(): Promise<SystemHealth> {
    const response = await api.get('/health');
    return response.data;
  }

  async getReadiness(): Promise<SystemHealth> {
    const response = await api.get('/ready');
    return response.data;
  }

  async getMetrics(): Promise<SystemMetrics> {
    const response = await api.get('/health/metrics');
    return response.data;
  }

  async getDetailedHealth(): Promise<any> {
    const response = await api.get('/health/detailed');
    return response.data;
  }

  // Agents
  async getAgents(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    agent_type?: string;
  }): Promise<Agent[]> {
    const response = await api.get('/agents', { params });
    return response.data;
  }

  async getAgent(agentId: string): Promise<Agent> {
    const response = await api.get(`/agents/${agentId}`);
    return response.data;
  }

  async createAgent(agent: Omit<Agent, 'id' | 'created_at' | 'updated_at'>): Promise<Agent> {
    const response = await api.post('/agents', agent);
    return response.data;
  }

  async updateAgent(agentId: string, updates: Partial<Agent>): Promise<Agent> {
    const response = await api.put(`/agents/${agentId}`, updates);
    return response.data;
  }

  async deleteAgent(agentId: string): Promise<void> {
    await api.delete(`/agents/${agentId}`);
  }

  async startAgent(agentId: string): Promise<void> {
    await api.post(`/agents/${agentId}/start`);
  }

  async stopAgent(agentId: string): Promise<void> {
    await api.post(`/agents/${agentId}/stop`);
  }

  async getAgentStatus(agentId: string): Promise<any> {
    const response = await api.get(`/agents/${agentId}/status`);
    return response.data;
  }

  // Tasks
  async getTasks(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    agent_id?: string;
    priority?: string;
  }): Promise<Task[]> {
    const response = await api.get('/tasks', { params });
    return response.data;
  }

  async getTask(taskId: string): Promise<Task> {
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  }

  async createTask(task: Omit<Task, 'id' | 'created_at' | 'updated_at'>): Promise<Task> {
    const response = await api.post('/tasks', task);
    return response.data;
  }

  async updateTask(taskId: string, updates: Partial<Task>): Promise<Task> {
    const response = await api.put(`/tasks/${taskId}`, updates);
    return response.data;
  }

  async deleteTask(taskId: string): Promise<void> {
    await api.delete(`/tasks/${taskId}`);
  }

  async startTask(taskId: string): Promise<void> {
    await api.post(`/tasks/${taskId}/start`);
  }

  async stopTask(taskId: string): Promise<void> {
    await api.post(`/tasks/${taskId}/stop`);
  }

  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    const response = await api.get(`/tasks/${taskId}/status`);
    return response.data;
  }

  async getTaskResult(taskId: string): Promise<TaskResult> {
    const response = await api.get(`/tasks/${taskId}/result`);
    return response.data;
  }

  // Voice Commands
  async processVoiceCommand(command: string): Promise<any> {
    const response = await api.post('/voice/process', { command });
    return response.data;
  }

  // Authentication
  async login(username: string, password: string): Promise<{ token: string }> {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  }

  async logout(): Promise<void> {
    await api.post('/auth/logout');
    localStorage.removeItem('amas_token');
  }

  async getProfile(): Promise<any> {
    const response = await api.get('/auth/profile');
    return response.data;
  }

  // WebSocket connection
  connectWebSocket(): WebSocket {
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
    return new WebSocket(wsUrl);
  }
}

// Export singleton instance
export const apiService = new APIService();
export default api;