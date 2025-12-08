# **🎯 AMAS PROJECT: PART 7 - FRONTEND COMPLETE INTEGRATION**
## **React Dashboard with Real-Time Updates & Full Backend Integration**

---

## **PART 7: FRONTEND COMPLETE INTEGRATION**

### **Step 7.1: Enhanced API Service with All Endpoints**

**File**: `frontend/src/services/api.ts` (COMPLETE VERSION)

```typescript
// frontend/src/services/api.ts (PRODUCTION-READY API SERVICE)
import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';

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
  result?: any;
  error_details?: any;
  created_at: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  success_rate?: number;
  quality_score?: number;
  tokens_used?: number;
  cost_usd?: number;
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
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired - redirect to login
          this.clearToken();
          window.location.href = '/login';
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
    localStorage.setItem('access_token', token);
  }

  clearToken(): void {
    this.accessToken = null;
    localStorage.removeItem('access_token');
  }

  loadToken(): void {
    const token = localStorage.getItem('access_token');
    if (token) {
      this.accessToken = token;
    }
  }

  async login(username: string, password: string): Promise<{ access_token: string; user: User }> {
    const response = await this.client.post('/auth/login', { username, password });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout');
    this.clearToken();
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/auth/me');
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
    const response = await this.client.get('/tasks', { params });
    return response.data;
  }

  async getTask(taskId: string): Promise<Task> {
    const response = await this.client.get(`/tasks/${taskId}`);
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
    const response = await this.client.post('/tasks', taskData);
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

  async getAgent(agentId: string): Promise<Agent> {
    const response = await this.client.get(`/agents/${agentId}`);
    return response.data;
  }

  async getAgentPerformance(): Promise<Agent[]> {
    const response = await this.client.get('/agents/performance');
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
}

// Export singleton instance
export const apiService = new APIService();

// Export class for testing
export default APIService;
```

***

### **Step 7.2: Enhanced WebSocket Service with Reconnection**

**File**: `frontend/src/services/websocket.ts` (PRODUCTION-READY)

```typescript
// frontend/src/services/websocket.ts (PRODUCTION-READY WEBSOCKET)
import { apiService } from './api';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface WebSocketMessage {
  event: string;
  data?: any;
  task_id?: string;
  agent_id?: string;
  timestamp: string;
}

export type WebSocketEventHandler = (data: any) => void;

// ============================================================================
// WEBSOCKET SERVICE CLASS
// ============================================================================

class WebSocketService {
  private ws: WebSocket | null = null;
  private eventHandlers: Map<string, Set<WebSocketEventHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private isConnecting = false;
  private shouldReconnect = true;
  private pingInterval: NodeJS.Timeout | null = null;
  private connectionUrl: string;

  constructor() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = process.env.REACT_APP_WS_URL || window.location.host;
    this.connectionUrl = `${wsProtocol}//${wsHost}/ws`;
  }

  // ========================================================================
  // CONNECTION MANAGEMENT
  // ========================================================================

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      console.log('WebSocket already connected or connecting');
      return;
    }

    this.isConnecting = true;
    this.shouldReconnect = true;

    try {
      // Get auth token
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('No auth token found for WebSocket connection');
        this.isConnecting = false;
        return;
      }

      // Create WebSocket connection with auth token
      const wsUrl = `${this.connectionUrl}?token=${token}`;
      this.ws = new WebSocket(wsUrl);

      // Connection opened
      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.startHeartbeat();

        // Notify connection handlers
        this.emit('connected', { timestamp: new Date().toISOString() });
      };

      // Message received
      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('📨 WebSocket message:', message.event);

          // Handle heartbeat
          if (message.event === 'heartbeat') {
            return; // Ignore heartbeat messages
          }

          // Emit to registered handlers
          this.emit(message.event, message.data || message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      // Connection closed
      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        this.isConnecting = false;
        this.stopHeartbeat();

        // Notify disconnection handlers
        this.emit('disconnected', { timestamp: new Date().toISOString() });

        // Attempt reconnection
        if (this.shouldReconnect) {
          this.scheduleReconnect();
        }
      };

      // Connection error
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;

        // Notify error handlers
        this.emit('error', { error, timestamp: new Date().toISOString() });
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    this.shouldReconnect = false;
    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max WebSocket reconnection attempts reached');
      this.emit('reconnect_failed', {
        attempts: this.reconnectAttempts,
        timestamp: new Date().toISOString(),
      });
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );

    console.log(`Reconnecting WebSocket in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      if (this.shouldReconnect) {
        console.log('Attempting WebSocket reconnection...');
        this.connect();
      }
    }, delay);
  }

  private startHeartbeat(): void {
    this.pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send('ping', {});
      }
    }, 30000); // Ping every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  // ========================================================================
  // EVENT HANDLING
  // ========================================================================

  on(event: string, handler: WebSocketEventHandler): () => void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }

    this.eventHandlers.get(event)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.off(event, handler);
    };
  }

  off(event: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.eventHandlers.delete(event);
      }
    }
  }

  private emit(event: string, data: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in WebSocket event handler for '${event}':`, error);
        }
      });
    }
  }

  // ========================================================================
  // MESSAGE SENDING
  // ========================================================================

  send(command: string, data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          command,
          ...data,
        })
      );
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  subscribeToTask(taskId: string): void {
    this.send('subscribe_task', { task_id: taskId });
  }

  unsubscribeFromTask(taskId: string): void {
    this.send('unsubscribe_task', { task_id: taskId });
  }

  // ========================================================================
  // UTILITY METHODS
  // ========================================================================

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getReadyState(): number | null {
    return this.ws?.readyState ?? null;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();

// Export class for testing
export default WebSocketService;
```

***

### **Step 7.3: Real-Time Dashboard Component**

**File**: `frontend/src/components/Dashboard/Dashboard.tsx` (CREATE NEW)

```tsx
// frontend/src/components/Dashboard/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { apiService } from '../../services/api';
import { websocketService } from '../../services/websocket';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
);

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface DashboardStats {
  totalTasks: number;
  activeTasks: number;
  completedTasks: number;
  failedTasks: number;
  queueDepth: number;
  avgDuration: number;
  successRate: number;
  totalCost: number;
  cpuUsage: number;
  memoryUsage: number;
  activeAgents: number;
}

interface MetricHistory {
  timestamp: string;
  value: number;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalTasks: 0,
    activeTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    queueDepth: 0,
    avgDuration: 0,
    successRate: 0,
    totalCost: 0,
    cpuUsage: 0,
    memoryUsage: 0,
    activeAgents: 0,
  });

  const [cpuHistory, setCpuHistory] = useState<MetricHistory[]>([]);
  const [memoryHistory, setMemoryHistory] = useState<MetricHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // ========================================================================
  // DATA FETCHING
  // ========================================================================

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch metrics
      const [systemMetrics, taskAnalytics, agentData] = await Promise.all([
        apiService.getSystemMetrics(),
        apiService.getTaskAnalytics(),
        apiService.getAgentPerformance(),
      ]);

      // Update stats
      setStats({
        totalTasks: taskAnalytics.total_tasks,
        activeTasks: systemMetrics.active_tasks,
        completedTasks: taskAnalytics.completed_tasks,
        failedTasks: taskAnalytics.failed_tasks,
        queueDepth: systemMetrics.queue_depth,
        avgDuration: taskAnalytics.avg_duration,
        successRate: taskAnalytics.success_rate,
        totalCost: taskAnalytics.total_cost,
        cpuUsage: systemMetrics.cpu_usage_percent,
        memoryUsage: systemMetrics.memory_usage_percent,
        activeAgents: systemMetrics.active_agents,
      });

      // Update metric history
      const now = new Date().toISOString();
      setCpuHistory((prev) => [...prev.slice(-29), { timestamp: now, value: systemMetrics.cpu_usage_percent }]);
      setMemoryHistory((prev) => [...prev.slice(-29), { timestamp: now, value: systemMetrics.memory_usage_percent }]);

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // ========================================================================
  // REAL-TIME UPDATES
  // ========================================================================

  useEffect(() => {
    // Initial fetch
    fetchDashboardData();

    // Set up polling
    const pollInterval = setInterval(fetchDashboardData, 15000); // Every 15 seconds

    // Set up WebSocket listeners
    const unsubscribeTaskUpdate = websocketService.on('task_update', (data) => {
      console.log('Task update received:', data);
      // Update relevant stats
      fetchDashboardData();
    });

    const unsubscribeSystemUpdate = websocketService.on('system_metrics', (data) => {
      console.log('System metrics update:', data);
      setStats((prev) => ({
        ...prev,
        cpuUsage: data.cpu_usage,
        memoryUsage: data.memory_usage,
      }));
    });

    // Cleanup
    return () => {
      clearInterval(pollInterval);
      unsubscribeTaskUpdate();
      unsubscribeSystemUpdate();
    };
  }, []);

  // ========================================================================
  // CHART CONFIGURATION
  // ========================================================================

  const cpuChartData = {
    labels: cpuHistory.map((h) => new Date(h.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'CPU Usage %',
        data: cpuHistory.map((h) => h.value),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4,
      },
    ],
  };

  const memoryChartData = {
    labels: memoryHistory.map((h) => new Date(h.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Memory Usage %',
        data: memoryHistory.map((h) => h.value),
        borderColor: 'rgb(153, 102, 255)',
        backgroundColor: 'rgba(153, 102, 255, 0.2)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        min: 0,
        max: 100,
      },
    },
  };

  // ========================================================================
  // RENDER
  // ========================================================================

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchDashboardData} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3}>
        {/* Task Stats */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography color="text.secondary" variant="body2">
                  Total Tasks
                </Typography>
                <CheckCircleIcon color="primary" />
              </Box>
              <Typography variant="h4">{stats.totalTasks}</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Chip
                  label={`${stats.successRate.toFixed(1)}% success`}
                  size="small"
                  color="success"
                  sx={{ mr: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {stats.completedTasks} completed
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Active Tasks */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography color="text.secondary" variant="body2">
                  Active Tasks
                </Typography>
                <SpeedIcon color="warning" />
              </Box>
              <Typography variant="h4">{stats.activeTasks}</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Chip label={`${stats.queueDepth} queued`} size="small" color="info" sx={{ mr: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  in queue
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* CPU Usage */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography color="text.secondary" variant="body2">
                  CPU Usage
                </Typography>
                <MemoryIcon color="error" />
              </Box>
              <Typography variant="h4">{stats.cpuUsage.toFixed(1)}%</Typography>
              <LinearProgress
                variant="determinate"
                value={stats.cpuUsage}
                sx={{ mt: 1, height: 8, borderRadius: 4 }}
                color={stats.cpuUsage > 80 ? 'error' : stats.cpuUsage > 60 ? 'warning' : 'success'}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Memory Usage */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography color="text.secondary" variant="body2">
                  Memory Usage
                </Typography>
                <StorageIcon color="secondary" />
              </Box>
              <Typography variant="h4">{stats.memoryUsage.toFixed(1)}%</Typography>
              <LinearProgress
                variant="determinate"
                value={stats.memoryUsage}
                sx={{ mt: 1, height: 8, borderRadius: 4 }}
                color={stats.memoryUsage > 85 ? 'error' : stats.memoryUsage > 70 ? 'warning' : 'success'}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* CPU Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                CPU Usage History
              </Typography>
              <Box sx={{ height: 300 }}>
                <Line data={cpuChartData} options={chartOptions} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Memory Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Memory Usage History
              </Typography>
              <Box sx={{ height: 300 }}>
                <Line data={memoryChartData} options={chartOptions} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Avg Duration
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {stats.avgDuration.toFixed(1)}s
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Success Rate
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    {stats.successRate.toFixed(1)}%
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Failed Tasks
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" color="error.main">
                    {stats.failedTasks}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Cost Metrics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cost Analysis
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Total Cost
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${stats.totalCost.toFixed(2)}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Avg Cost/Task
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${stats.totalTasks > 0 ? (stats.totalCost / stats.totalTasks).toFixed(4) : '0.00'}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {stats.totalCost > 100 ? (
                    <TrendingUpIcon color="error" fontSize="small" sx={{ mr: 1 }} />
                  ) : (
                    <TrendingDownIcon color="success" fontSize="small" sx={{ mr: 1 }} />
                  )}
                  <Typography variant="body2" color="text.secondary">
                    {stats.totalCost > 100 ? 'High usage' : 'Normal usage'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Agent Status */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Status
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Active Agents
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {stats.activeAgents}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Utilization
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {stats.activeTasks > 0 ? ((stats.activeTasks / stats.activeAgents) * 100).toFixed(0) : '0'}%
                  </Typography>
                </Box>
                <Chip
                  label={stats.activeAgents > 0 ? 'All systems operational' : 'No agents active'}
                  color={stats.activeAgents > 0 ? 'success' : 'error'}
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
```

***

**Due to length constraints, this is Part 7A**

**What's Implemented So Far**:
1. ✅ Complete API service (all endpoints)
2. ✅ Production-ready WebSocket service (reconnection, heartbeat)
3. ✅ Real-time dashboard with live metrics
4. ✅ Chart.js integration for visualizations
5. ✅ Material-UI components

now lets move into :
- Task Management UI (create, execute, monitor)
- Agent Management UI
- Integration Management UI
- Prediction UI
- Real-time task execution viewer

# **🎯 AMAS PROJECT: PART 7B - REMAINING UI COMPONENTS**
## **Task Management, Agent UI, Integrations & Real-Time Execution Viewer**

---

## **PART 7B: COMPLETE UI COMPONENTS**

### **Step 7B.1: Task List & Creation Component**

**File**: `frontend/src/components/Tasks/TaskList.tsx` (CREATE NEW)

```tsx
// frontend/src/components/Tasks/TaskList.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  LinearProgress,
  MenuItem,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Tooltip,
  Typography,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  Cancel as CancelIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { apiService, Task, TaskPrediction } from '../../services/api';
import { websocketService } from '../../services/websocket';
import { useNavigate } from 'react-router-dom';

// ============================================================================
// TASK LIST COMPONENT
// ============================================================================

export const TaskList: React.FC = () => {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalTasks, setTotalTasks] = useState(0);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterTaskType, setFilterTaskType] = useState<string>('all');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // ========================================================================
  // DATA FETCHING
  // ========================================================================

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const params: any = {
        limit: rowsPerPage,
        offset: page * rowsPerPage,
      };

      if (filterStatus !== 'all') {
        params.status = filterStatus;
      }

      if (filterTaskType !== 'all') {
        params.task_type = filterTaskType;
      }

      const response = await apiService.listTasks(params);
      setTasks(response.tasks);
      setTotalTasks(response.total);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchTasks();
    setRefreshing(false);
  };

  useEffect(() => {
    fetchTasks();
  }, [page, rowsPerPage, filterStatus, filterTaskType]);

  // ========================================================================
  // REAL-TIME UPDATES
  // ========================================================================

  useEffect(() => {
    // Listen for task updates via WebSocket
    const unsubscribe = websocketService.on('task_update', (data) => {
      console.log('Task update received:', data);

      // Update task in list
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.task_id === data.task_id
            ? { ...task, status: data.status, updated_at: data.timestamp }
            : task
        )
      );
    });

    return () => {
      unsubscribe();
    };
  }, []);

  // ========================================================================
  // ACTIONS
  // ========================================================================

  const handleExecuteTask = async (taskId: string) => {
    try {
      await apiService.executeTask(taskId);
      
      // Update task status optimistically
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.task_id === taskId ? { ...task, status: 'executing' } : task
        )
      );
    } catch (error) {
      console.error('Failed to execute task:', error);
    }
  };

  const handleCancelTask = async (taskId: string) => {
    try {
      await apiService.cancelTask(taskId);
      await fetchTasks();
    } catch (error) {
      console.error('Failed to cancel task:', error);
    }
  };

  const handleViewTask = (taskId: string) => {
    navigate(`/tasks/${taskId}`);
  };

  // ========================================================================
  // STATUS HELPERS
  // ========================================================================

  const getStatusColor = (status: string): 'default' | 'success' | 'error' | 'warning' | 'info' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
      case 'timeout':
        return 'error';
      case 'executing':
        return 'warning';
      case 'pending':
      case 'assigned':
        return 'info';
      case 'cancelled':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon fontSize="small" />;
      case 'failed':
      case 'timeout':
        return <ErrorIcon fontSize="small" />;
      case 'executing':
        return <PlayIcon fontSize="small" />;
      case 'pending':
      case 'assigned':
        return <ScheduleIcon fontSize="small" />;
      default:
        return null;
    }
  };

  // ========================================================================
  // RENDER
  // ========================================================================

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Tasks
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} disabled={refreshing}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Task
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  label="Status"
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="executing">Executing</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="failed">Failed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Task Type</InputLabel>
                <Select
                  value={filterTaskType}
                  label="Task Type"
                  onChange={(e) => setFilterTaskType(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="security_scan">Security Scan</MenuItem>
                  <MenuItem value="code_analysis">Code Analysis</MenuItem>
                  <MenuItem value="intelligence_gathering">Intelligence Gathering</MenuItem>
                  <MenuItem value="performance_analysis">Performance Analysis</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Task Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Quality</TableCell>
                <TableCell>Cost</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9}>
                    <LinearProgress />
                  </TableCell>
                </TableRow>
              ) : tasks.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No tasks found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                tasks.map((task) => (
                  <TableRow key={task.task_id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {task.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {task.task_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={task.task_type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={task.status}
                        size="small"
                        color={getStatusColor(task.status)}
                        icon={getStatusIcon(task.status)}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={task.priority}
                        size="small"
                        color={task.priority >= 8 ? 'error' : task.priority >= 5 ? 'warning' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      {task.duration_seconds ? `${task.duration_seconds.toFixed(1)}s` : '-'}
                    </TableCell>
                    <TableCell>
                      {task.quality_score ? (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <LinearProgress
                            variant="determinate"
                            value={task.quality_score * 100}
                            sx={{ width: 60, mr: 1 }}
                            color={task.quality_score >= 0.8 ? 'success' : 'warning'}
                          />
                          <Typography variant="caption">{(task.quality_score * 100).toFixed(0)}%</Typography>
                        </Box>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      {task.cost_usd !== undefined ? `$${task.cost_usd.toFixed(4)}` : '-'}
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {new Date(task.created_at).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton size="small" onClick={() => handleViewTask(task.task_id)}>
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {task.status === 'pending' && (
                        <Tooltip title="Execute">
                          <IconButton size="small" onClick={() => handleExecuteTask(task.task_id)}>
                            <PlayIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      {task.status === 'executing' && (
                        <Tooltip title="Cancel">
                          <IconButton size="small" onClick={() => handleCancelTask(task.task_id)}>
                            <CancelIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={totalTasks}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Card>

      {/* Create Task Dialog */}
      <CreateTaskDialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} onTaskCreated={fetchTasks} />
    </Box>
  );
};

// ============================================================================
// CREATE TASK DIALOG
// ============================================================================

interface CreateTaskDialogProps {
  open: boolean;
  onClose: () => void;
  onTaskCreated: () => void;
}

const CreateTaskDialog: React.FC<CreateTaskDialogProps> = ({ open, onClose, onTaskCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    task_type: 'security_scan',
    target: '',
    priority: 5,
    parameters: {},
  });
  const [prediction, setPrediction] = useState<TaskPrediction | null>(null);
  const [predicting, setPredicting] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setPrediction(null); // Clear prediction when inputs change
  };

  const handlePredict = async () => {
    try {
      setPredicting(true);
      setError(null);

      const predictionResult = await apiService.predictTask({
        task_type: formData.task_type,
        target: formData.target,
        parameters: formData.parameters,
      });

      setPrediction(predictionResult);
    } catch (err) {
      setError('Failed to generate prediction');
      console.error('Prediction failed:', err);
    } finally {
      setPredicting(false);
    }
  };

  const handleCreate = async () => {
    try {
      setCreating(true);
      setError(null);

      await apiService.createTask(formData);

      // Reset form
      setFormData({
        title: '',
        description: '',
        task_type: 'security_scan',
        target: '',
        priority: 5,
        parameters: {},
      });
      setPrediction(null);

      onTaskCreated();
      onClose();
    } catch (err) {
      setError('Failed to create task');
      console.error('Task creation failed:', err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Task</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Title"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              required
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              multiline
              rows={3}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Task Type</InputLabel>
              <Select
                value={formData.task_type}
                label="Task Type"
                onChange={(e) => handleInputChange('task_type', e.target.value)}
              >
                <MenuItem value="security_scan">Security Scan</MenuItem>
                <MenuItem value="code_analysis">Code Analysis</MenuItem>
                <MenuItem value="intelligence_gathering">Intelligence Gathering</MenuItem>
                <MenuItem value="performance_analysis">Performance Analysis</MenuItem>
                <MenuItem value="documentation">Documentation</MenuItem>
                <MenuItem value="testing">Testing</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Priority"
              type="number"
              value={formData.priority}
              onChange={(e) => handleInputChange('priority', parseInt(e.target.value))}
              inputProps={{ min: 1, max: 10 }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Target"
              value={formData.target}
              onChange={(e) => handleInputChange('target', e.target.value)}
              placeholder="e.g., https://example.com or github.com/user/repo"
              required
            />
          </Grid>

          {/* ML Prediction Section */}
          {prediction && (
            <Grid item xs={12}>
              <Card variant="outlined" sx={{ bgcolor: 'background.default' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    AI Prediction
                  </Typography>

                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">
                        Success Probability
                      </Typography>
                      <Typography variant="h6" color={prediction.success_probability >= 0.7 ? 'success.main' : 'warning.main'}>
                        {(prediction.success_probability * 100).toFixed(0)}%
                      </Typography>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">
                        Est. Duration
                      </Typography>
                      <Typography variant="h6">{prediction.estimated_duration.toFixed(0)}s</Typography>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">
                        Est. Quality
                      </Typography>
                      <Typography variant="h6">{(prediction.quality_score_prediction * 100).toFixed(0)}%</Typography>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">
                        Est. Cost
                      </Typography>
                      <Typography variant="h6">${prediction.estimated_cost.toFixed(4)}</Typography>
                    </Grid>
                  </Grid>

                  {prediction.recommended_agents.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Recommended Agents
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {prediction.recommended_agents.slice(0, 3).map((agent) => (
                          <Chip
                            key={agent.agent_id}
                            label={agent.agent_name}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {prediction.risk_factors.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" color="warning.main" gutterBottom>
                        Risk Factors
                      </Typography>
                      {prediction.risk_factors.slice(0, 2).map((risk, idx) => (
                        <Typography key={idx} variant="caption" display="block" color="text.secondary">
                          • {risk}
                        </Typography>
                      ))}
                    </Box>
                  )}

                  {prediction.optimization_suggestions.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" color="info.main" gutterBottom>
                        Optimization Suggestions
                      </Typography>
                      {prediction.optimization_suggestions.slice(0, 2).map((suggestion, idx) => (
                        <Typography key={idx} variant="caption" display="block" color="text.secondary">
                          • {suggestion}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={creating}>
          Cancel
        </Button>
        <Button onClick={handlePredict} disabled={predicting || !formData.target} variant="outlined">
          {predicting ? 'Predicting...' : 'Predict'}
        </Button>
        <Button onClick={handleCreate} disabled={creating || !formData.title || !formData.target} variant="contained">
          {creating ? 'Creating...' : 'Create Task'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TaskList;
```

***

### **Step 7B.2: Real-Time Task Execution Viewer**

**File**: `frontend/src/components/Tasks/TaskExecutionView.tsx` (CREATE NEW)

```tsx
// frontend/src/components/Tasks/TaskExecutionView.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  LinearProgress,
  Paper,
  Step,
  StepContent,
  StepLabel,
  Stepper,
  Typography,
  Alert,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableRow,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  PlayArrow as PlayArrowIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { apiService, Task } from '../../services/api';
import { websocketService } from '../../services/websocket';

// ============================================================================
// EXECUTION EVENT TYPES
// ============================================================================

interface ExecutionEvent {
  timestamp: string;
  event_type: string;
  message: string;
  agent_id?: string;
  agent_name?: string;
  data?: any;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const TaskExecutionView: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const [task, setTask] = useState<Task | null>(null);
  const [events, setEvents] = useState<ExecutionEvent[]>([]);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(true);

  // ========================================================================
  // DATA FETCHING
  // ========================================================================

  useEffect(() => {
    const fetchTask = async () => {
      try {
        setLoading(true);
        if (taskId) {
          const taskData = await apiService.getTask(taskId);
          setTask(taskData);
        }
      } catch (error) {
        console.error('Failed to fetch task:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [taskId]);

  // ========================================================================
  // REAL-TIME UPDATES
  // ========================================================================

  useEffect(() => {
    if (!taskId) return;

    // Subscribe to task-specific updates
    websocketService.subscribeToTask(taskId);

    // Listen for various execution events
    const unsubscribeTaskUpdate = websocketService.on('task_update', (data) => {
      if (data.task_id === taskId) {
        console.log('Task update:', data);
        setTask((prev) => (prev ? { ...prev, ...data } : null));
      }
    });

    const unsubscribeTaskProgress = websocketService.on('task_progress', (data) => {
      if (data.task_id === taskId) {
        console.log('Task progress:', data);
        setProgress(data.progress || 0);

        // Add progress event
        setEvents((prev) => [
          ...prev,
          {
            timestamp: new Date().toISOString(),
            event_type: 'progress',
            message: `Progress: ${data.progress}%`,
            data,
          },
        ]);
      }
    });

    const unsubscribeAgentStart = websocketService.on('agent_started', (data) => {
      if (data.task_id === taskId) {
        console.log('Agent started:', data);
        setEvents((prev) => [
          ...prev,
          {
            timestamp: new Date().toISOString(),
            event_type: 'agent_started',
            message: `Agent ${data.agent_name} started execution`,
            agent_id: data.agent_id,
            agent_name: data.agent_name,
            data,
          },
        ]);
      }
    });

    const unsubscribeAgentComplete = websocketService.on('agent_completed', (data) => {
      if (data.task_id === taskId) {
        console.log('Agent completed:', data);
        setEvents((prev) => [
          ...prev,
          {
            timestamp: new Date().toISOString(),
            event_type: 'agent_completed',
            message: `Agent ${data.agent_name} completed (${data.duration}s)`,
            agent_id: data.agent_id,
            agent_name: data.agent_name,
            data,
          },
        ]);
      }
    });

    const unsubscribeTaskComplete = websocketService.on('task_completed', (data) => {
      if (data.task_id === taskId) {
        console.log('Task completed:', data);
        setProgress(100);
        setTask((prev) => (prev ? { ...prev, status: 'completed', ...data } : null));
      }
    });

    const unsubscribeTaskFailed = websocketService.on('task_failed', (data) => {
      if (data.task_id === taskId) {
        console.log('Task failed:', data);
        setTask((prev) => (prev ? { ...prev, status: 'failed', ...data } : null));
      }
    });

    // Cleanup
    return () => {
      websocketService.unsubscribeFromTask(taskId);
      unsubscribeTaskUpdate();
      unsubscribeTaskProgress();
      unsubscribeAgentStart();
      unsubscribeAgentComplete();
      unsubscribeTaskComplete();
      unsubscribeTaskFailed();
    };
  }, [taskId]);

  // ========================================================================
  // RENDER HELPERS
  // ========================================================================

  const getStatusColor = (status: string): 'default' | 'success' | 'error' | 'warning' | 'info' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'executing':
        return 'warning';
      default:
        return 'info';
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  if (!task) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Task not found</Alert>
      </Box>
    );
  }

  // ========================================================================
  // RENDER
  // ========================================================================

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Typography variant="h4" component="h1">
            {task.title}
          </Typography>
          <Chip label={task.status} color={getStatusColor(task.status)} />
          <Chip label={task.task_type} variant="outlined" />
        </Box>
        <Typography variant="body2" color="text.secondary">
          Task ID: {task.task_id}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Left Column - Task Details */}
        <Grid item xs={12} md={8}>
          {/* Progress */}
          {task.status === 'executing' && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Execution Progress
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                  <Box sx={{ width: '100%', mr: 1 }}>
                    <LinearProgress variant="determinate" value={progress} sx={{ height: 10, borderRadius: 5 }} />
                  </Box>
                  <Box sx={{ minWidth: 35 }}>
                    <Typography variant="body2" color="text.secondary">
                      {progress}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Execution Timeline */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Execution Timeline
              </Typography>

              {events.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  No execution events yet
                </Typography>
              ) : (
                <Stepper orientation="vertical" sx={{ mt: 2 }}>
                  {events.map((event, index) => (
                    <Step key={index} active={true} completed={event.event_type === 'agent_completed'}>
                      <StepLabel
                        icon={
                          event.event_type === 'agent_completed' ? (
                            <CheckCircleIcon color="success" />
                          ) : event.event_type === 'agent_started' ? (
                            <PlayArrowIcon color="primary" />
                          ) : (
                            <ScheduleIcon color="action" />
                          )
                        }
                      >
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {event.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Box>
                      </StepLabel>
                      {event.data && (
                        <StepContent>
                          <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                            {event.data.provider && (
                              <Typography variant="caption" display="block">
                                Provider: {event.data.provider} ({event.data.model})
                              </Typography>
                            )}
                            {event.data.tokens && (
                              <Typography variant="caption" display="block">
                                Tokens: {event.data.tokens}
                              </Typography>
                            )}
                            {event.data.cost && (
                              <Typography variant="caption" display="block">
                                Cost: ${event.data.cost.toFixed(4)}
                              </Typography>
                            )}
                          </Paper>
                        </StepContent>
                      )}
                    </Step>
                  ))}
                </Stepper>
              )}
            </CardContent>
          </Card>

          {/* Results */}
          {task.status === 'completed' && task.result && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Results
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default', maxHeight: 400, overflow: 'auto' }}>
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {JSON.stringify(task.result, null, 2)}
                  </pre>
                </Paper>
              </CardContent>
            </Card>
          )}

          {/* Error Details */}
          {task.status === 'failed' && task.error_details && (
            <Alert severity="error">
              <Typography variant="subtitle2" gutterBottom>
                Execution Failed
              </Typography>
              <Typography variant="body2">{JSON.stringify(task.error_details)}</Typography>
            </Alert>
          )}
        </Grid>

        {/* Right Column - Metadata */}
        <Grid item xs={12} md={4}>
          {/* Task Info */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Task Information
              </Typography>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Target</TableCell>
                    <TableCell>{task.target}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Priority</TableCell>
                    <TableCell>
                      <Chip label={task.priority} size="small" color={task.priority >= 8 ? 'error' : 'default'} />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Created</TableCell>
                    <TableCell>{new Date(task.created_at).toLocaleString()}</TableCell>
                  </TableRow>
                  {task.started_at && (
                    <TableRow>
                      <TableCell>Started</TableCell>
                      <TableCell>{new Date(task.started_at).toLocaleString()}</TableCell>
                    </TableRow>
                  )}
                  {task.completed_at && (
                    <TableRow>
                      <TableCell>Completed</TableCell>
                      <TableCell>{new Date(task.completed_at).toLocaleString()}</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Performance Metrics */}
          {(task.duration_seconds || task.quality_score || task.cost_usd) && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance
                </Typography>
                <Table size="small">
                  <TableBody>
                    {task.duration_seconds && (
                      <TableRow>
                        <TableCell>Duration</TableCell>
                        <TableCell>{task.duration_seconds.toFixed(2)}s</TableCell>
                      </TableRow>
                    )}
                    {task.quality_score && (
                      <TableRow>
                        <TableCell>Quality Score</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <LinearProgress
                              variant="determinate"
                              value={task.quality_score * 100}
                              sx={{ width: 60, mr: 1 }}
                              color={task.quality_score >= 0.8 ? 'success' : 'warning'}
                            />
                            {(task.quality_score * 100).toFixed(0)}%
                          </Box>
                        </TableCell>
                      </TableRow>
                    )}
                    {task.success_rate !== undefined && (
                      <TableRow>
                        <TableCell>Success Rate</TableCell>
                        <TableCell>{(task.success_rate * 100).toFixed(0)}%</TableCell>
                      </TableRow>
                    )}
                    {task.tokens_used && (
                      <TableRow>
                        <TableCell>Tokens Used</TableCell>
                        <TableCell>{task.tokens_used.toLocaleString()}</TableCell>
                      </TableRow>
                    )}
                    {task.cost_usd !== undefined && (
                      <TableRow>
                        <TableCell>Cost</TableCell>
                        <TableCell>${task.cost_usd.toFixed(4)}</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}

          {/* Assigned Agents */}
          {task.assigned_agents && task.assigned_agents.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Assigned Agents
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {task.assigned_agents.map((agentId, index) => (
                    <Chip key={index} label={agentId} size="small" variant="outlined" />
                  ))}
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default TaskExecutionView;
```

***

### **Step 7B.3: Agent Management UI**

**File**: `frontend/src/components/Agents/AgentList.tsx` (CREATE NEW)

```tsx
// frontend/src/components/Agents/AgentList.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { apiService, Agent } from '../../services/api';
import { websocketService } from '../../services/websocket';

export const AgentList: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const response = await apiService.getAgentPerformance();
      setAgents(response);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();

    // Listen for agent updates
    const unsubscribe = websocketService.on('agent_update', (data) => {
      setAgents((prev) =>
        prev.map((agent) =>
          agent.agent_id === data.agent_id ? { ...agent, ...data } : agent
        )
      );
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const getStatusColor = (status: string): 'success' | 'error' | 'warning' | 'default' => {
    switch (status) {
      case 'active':
        return 'success';
      case 'error':
        return 'error';
      case 'maintenance':
        return 'warning';
      default:
        return 'default';
    }
  };

  const calculateSuccessRate = (agent: Agent): number => {
    if (agent.total_executions === 0) return 0;
    return (agent.successful_executions / agent.total_executions) * 100;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          AI Agents
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={fetchAgents}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Agent Cards Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {agents.slice(0, 4).map((agent) => (
          <Grid item xs={12} sm={6} md={3} key={agent.agent_id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {agent.name}
                    </Typography>
                    <Chip label={agent.status} size="small" color={getStatusColor(agent.status)} />
                  </Box>
                  {agent.status === 'active' ? (
                    <CheckCircleIcon color="success" />
                  ) : (
                    <ErrorIcon color="error" />
                  )}
                </Box>

                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Executions
                  </Typography>
                  <Typography variant="h6">{agent.total_executions}</Typography>
                </Box>

                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Success Rate
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={calculateSuccessRate(agent)}
                      sx={{ flex: 1, height: 8, borderRadius: 4 }}
                      color={calculateSuccessRate(agent) >= 90 ? 'success' : 'warning'}
                    />
                    <Typography variant="caption">{calculateSuccessRate(agent).toFixed(0)}%</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Agent Performance Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Agent Performance Details
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Agent</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Executions</TableCell>
                  <TableCell align="right">Success Rate</TableCell>
                  <TableCell align="right">Avg Duration</TableCell>
                  <TableCell align="right">Total Cost</TableCell>
                  <TableCell align="right">Expertise</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8}>
                      <LinearProgress />
                    </TableCell>
                  </TableRow>
                ) : (
                  agents.map((agent) => (
                    <TableRow key={agent.agent_id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {agent.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {agent.agent_id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={agent.type} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip label={agent.status} size="small" color={getStatusColor(agent.status)} />
                      </TableCell>
                      <TableCell align="right">{agent.total_executions}</TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                          <LinearProgress
                            variant="determinate"
                            value={calculateSuccessRate(agent)}
                            sx={{ width: 60, mr: 1 }}
                            color={calculateSuccessRate(agent) >= 90 ? 'success' : 'warning'}
                          />
                          {calculateSuccessRate(agent).toFixed(0)}%
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        {agent.total_executions > 0
                          ? (agent.total_duration_seconds / agent.successful_executions).toFixed(1)
                          : '0'}
                        s
                      </TableCell>
                      <TableCell align="right">${agent.total_cost_usd.toFixed(2)}</TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                          <TrendingUpIcon fontSize="small" color="success" sx={{ mr: 0.5 }} />
                          {(agent.expertise_score * 100).toFixed(0)}%
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AgentList;
```

***

**This completes the first section of Part 7B**

**What's Implemented**:
1. ✅ Task List with filters and pagination
2. ✅ Task Creation Dialog with ML predictions
3. ✅ Real-Time Task Execution Viewer
4. ✅ Agent Management UI with performance metrics
5. ✅ WebSocket integration for live updates
6. ✅ Material-UI components throughout

**now lets move into :**:
- Integration Management UI
- System Health Dashboard
- Routing configuration
- App Shell
# **🎯 AMAS PROJECT: PART 7B (CONTINUED) - FINAL UI COMPONENTS**
## **Integration Management, System Health, Routing & App Shell**

---

## **PART 7B (FINAL): COMPLETE UI IMPLEMENTATION**

### **Step 7B.4: Integration Management UI**

**File**: `frontend/src/components/Integrations/IntegrationList.tsx` (CREATE NEW)

```tsx
// frontend/src/components/Integrations/IntegrationList.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Tooltip,
  Typography,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  GitHub as GitHubIcon,
  Description as NotionIcon,
  BugReport as JiraIcon,
  Chat as SlackIcon,
  AccountTree as N8NIcon,
  Storage as SalesforceIcon,
} from '@mui/icons-material';
import { apiService, Integration } from '../../services/api';

// ============================================================================
// PLATFORM ICONS MAPPING
// ============================================================================

const platformIcons: Record<string, React.ReactElement> = {
  github: <GitHubIcon />,
  notion: <NotionIcon />,
  jira: <JiraIcon />,
  slack: <SlackIcon />,
  n8n: <N8NIcon />,
  salesforce: <SalesforceIcon />,
};

// ============================================================================
// INTEGRATION LIST COMPONENT
// ============================================================================

export const IntegrationList: React.FC = () => {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const fetchIntegrations = async () => {
    try {
      setLoading(true);
      const response = await apiService.listIntegrations();
      setIntegrations(response.integrations);
    } catch (error) {
      console.error('Failed to fetch integrations:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const handleDelete = async (integrationId: string) => {
    if (!window.confirm('Are you sure you want to delete this integration?')) {
      return;
    }

    try {
      await apiService.deleteIntegration(integrationId);
      await fetchIntegrations();
    } catch (error) {
      console.error('Failed to delete integration:', error);
    }
  };

  const getStatusColor = (status: string): 'success' | 'error' | 'warning' | 'default' => {
    switch (status) {
      case 'active':
        return 'success';
      case 'error':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Integrations
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchIntegrations}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateDialogOpen(true)}>
            Add Integration
          </Button>
        </Box>
      </Box>

      {/* Integration Cards */}
      {loading ? (
        <LinearProgress />
      ) : integrations.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center">
              No integrations configured. Add your first integration to get started.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {integrations.map((integration) => (
            <Grid item xs={12} sm={6} md={4} key={integration.integration_id}>
              <Card>
                <CardContent>
                  {/* Header */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {platformIcons[integration.platform] || <StorageIcon />}
                      <Box>
                        <Typography variant="h6">
                          {integration.platform.charAt(0).toUpperCase() + integration.platform.slice(1)}
                        </Typography>
                        <Chip label={integration.status} size="small" color={getStatusColor(integration.status)} />
                      </Box>
                    </Box>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(integration.integration_id)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>

                  {/* Stats */}
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Syncs
                      </Typography>
                      <Typography variant="caption" fontWeight="bold">
                        {integration.sync_count}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Errors
                      </Typography>
                      <Typography
                        variant="caption"
                        fontWeight="bold"
                        color={integration.error_count > 0 ? 'error.main' : 'text.primary'}
                      >
                        {integration.error_count}
                      </Typography>
                    </Box>
                    {integration.last_sync && (
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" color="text.secondary">
                          Last Sync
                        </Typography>
                        <Typography variant="caption">
                          {new Date(integration.last_sync).toLocaleString()}
                        </Typography>
                      </Box>
                    )}
                  </Box>

                  {/* Webhook URL */}
                  {integration.webhook_url && (
                    <Box sx={{ mt: 2, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                        Webhook URL
                      </Typography>
                      <Typography variant="caption" sx={{ wordBreak: 'break-all' }}>
                        {integration.webhook_url}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Integration Dialog */}
      <CreateIntegrationDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onIntegrationCreated={fetchIntegrations}
      />
    </Box>
  );
};

// ============================================================================
// CREATE INTEGRATION DIALOG
// ============================================================================

interface CreateIntegrationDialogProps {
  open: boolean;
  onClose: () => void;
  onIntegrationCreated: () => void;
}

const CreateIntegrationDialog: React.FC<CreateIntegrationDialogProps> = ({
  open,
  onClose,
  onIntegrationCreated,
}) => {
  const [platform, setPlatform] = useState('github');
  const [credentials, setCredentials] = useState<Record<string, string>>({});
  const [configuration, setConfiguration] = useState<Record<string, string>>({});
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const platformFields: Record<string, { credentials: string[]; configuration: string[] }> = {
    github: {
      credentials: ['access_token'],
      configuration: ['repository'],
    },
    slack: {
      credentials: ['bot_token', 'signing_secret'],
      configuration: ['channel'],
    },
    n8n: {
      credentials: ['base_url', 'api_key'],
      configuration: ['webhook_id'],
    },
    notion: {
      credentials: ['api_key'],
      configuration: ['parent_page_id', 'database_id'],
    },
    jira: {
      credentials: ['server', 'email', 'api_token'],
      configuration: ['project_key'],
    },
    salesforce: {
      credentials: ['username', 'password', 'security_token'],
      configuration: [],
    },
  };

  const handleCreate = async () => {
    try {
      setCreating(true);
      setError(null);

      await apiService.createIntegration({
        platform,
        credentials,
        configuration,
      });

      // Reset form
      setPlatform('github');
      setCredentials({});
      setConfiguration({});

      onIntegrationCreated();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create integration');
      console.error('Integration creation failed:', err);
    } finally {
      setCreating(false);
    }
  };

  const currentPlatformFields = platformFields[platform] || { credentials: [], configuration: [] };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add Integration</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <FormControl fullWidth sx={{ mt: 2, mb: 3 }}>
          <InputLabel>Platform</InputLabel>
          <Select value={platform} label="Platform" onChange={(e) => setPlatform(e.target.value)}>
            <MenuItem value="github">GitHub</MenuItem>
            <MenuItem value="slack">Slack</MenuItem>
            <MenuItem value="n8n">N8N</MenuItem>
            <MenuItem value="notion">Notion</MenuItem>
            <MenuItem value="jira">Jira</MenuItem>
            <MenuItem value="salesforce">Salesforce</MenuItem>
          </Select>
        </FormControl>

        {/* Credentials */}
        {currentPlatformFields.credentials.length > 0 && (
          <>
            <Typography variant="subtitle2" gutterBottom>
              Credentials
            </Typography>
            {currentPlatformFields.credentials.map((field) => (
              <TextField
                key={field}
                fullWidth
                label={field.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                type={field.includes('password') || field.includes('secret') || field.includes('token') ? 'password' : 'text'}
                value={credentials[field] || ''}
                onChange={(e) => setCredentials({ ...credentials, [field]: e.target.value })}
                sx={{ mb: 2 }}
                required
              />
            ))}
          </>
        )}

        {/* Configuration */}
        {currentPlatformFields.configuration.length > 0 && (
          <>
            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Configuration
            </Typography>
            {currentPlatformFields.configuration.map((field) => (
              <TextField
                key={field}
                fullWidth
                label={field.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                value={configuration[field] || ''}
                onChange={(e) => setConfiguration({ ...configuration, [field]: e.target.value })}
                sx={{ mb: 2 }}
              />
            ))}
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={creating}>
          Cancel
        </Button>
        <Button onClick={handleCreate} disabled={creating} variant="contained">
          {creating ? 'Creating...' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default IntegrationList;
```

***

### **Step 7B.5: System Health Dashboard**

**File**: `frontend/src/components/System/SystemHealth.tsx` (CREATE NEW)

```tsx
// frontend/src/components/System/SystemHealth.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  Storage as StorageIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import { apiService } from '../../services/api';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface SystemHealth {
  status: string;
  components: Record<string, ComponentHealth>;
  timestamp: string;
}

interface ComponentHealth {
  status: string;
  details?: any;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const SystemHealth: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      const response = await apiService.getSystemHealth();
      setHealth(response);
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();

    // Refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string): 'success' | 'error' | 'warning' => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return 'success';
      case 'unhealthy':
      case 'error':
        return 'error';
      default:
        return 'warning';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return <CheckCircleIcon color="success" />;
      case 'unhealthy':
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <WarningIcon color="warning" />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          System Health
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {health && (
            <Typography variant="body2" color="text.secondary">
              Last updated: {new Date(health.timestamp).toLocaleTimeString()}
            </Typography>
          )}
          <Tooltip title="Refresh">
            <IconButton onClick={fetchHealth} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {loading && !health ? (
        <LinearProgress />
      ) : health ? (
        <>
          {/* Overall Status */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {getStatusIcon(health.status)}
                <Box>
                  <Typography variant="h5">System Status</Typography>
                  <Chip label={health.status} color={getStatusColor(health.status)} size="small" sx={{ mt: 1 }} />
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Component Status Grid */}
          <Grid container spacing={3}>
            {Object.entries(health.components).map(([componentName, component]) => (
              <Grid item xs={12} sm={6} md={4} key={componentName}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          {componentName.charAt(0).toUpperCase() + componentName.slice(1)}
                        </Typography>
                        <Chip label={component.status} size="small" color={getStatusColor(component.status)} />
                      </Box>
                      {getStatusIcon(component.status)}
                    </Box>

                    {/* Component Details */}
                    {component.details && (
                      <Box sx={{ mt: 2 }}>
                        {component.details.latency_ms !== undefined && (
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              Latency
                            </Typography>
                            <Typography variant="body2">{component.details.latency_ms.toFixed(2)}ms</Typography>
                          </Box>
                        )}

                        {component.details.pool && (
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              Connection Pool
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={(component.details.pool.used / component.details.pool.size) * 100}
                                sx={{ flex: 1, height: 6, borderRadius: 3 }}
                              />
                              <Typography variant="caption">
                                {component.details.pool.used}/{component.details.pool.size}
                              </Typography>
                            </Box>
                          </Box>
                        )}

                        {component.details.version && (
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Version
                            </Typography>
                            <Typography variant="body2">{component.details.version}</Typography>
                          </Box>
                        )}

                        {component.details.used_memory_mb !== undefined && (
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Memory Usage
                            </Typography>
                            <Typography variant="body2">{component.details.used_memory_mb.toFixed(2)} MB</Typography>
                          </Box>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      ) : (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center">
              Unable to fetch system health
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default SystemHealth;
```

***

### **Step 7B.6: Main App Shell with Routing**

**File**: `frontend/src/App.tsx` (COMPLETE VERSION)

```tsx
// frontend/src/App.tsx (COMPLETE APP SHELL)
import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  CircularProgress,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Assignment as TaskIcon,
  Psychology as AgentIcon,
  Extension as IntegrationIcon,
  HealthAndSafety as HealthIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { apiService } from './services/api';
import { websocketService } from './services/websocket';

// Import components
import { Dashboard } from './components/Dashboard/Dashboard';
import { TaskList } from './components/Tasks/TaskList';
import { TaskExecutionView } from './components/Tasks/TaskExecutionView';
import { AgentList } from './components/Agents/AgentList';
import { IntegrationList } from './components/Integrations/IntegrationList';
import { SystemHealth } from './components/System/SystemHealth';
import { Login } from './components/Auth/Login';

// ============================================================================
// THEME CONFIGURATION
// ============================================================================

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#0a1929',
      paper: '#132f4c',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  shape: {
    borderRadius: 8,
  },
});

// ============================================================================
// PROTECTED ROUTE COMPONENT
// ============================================================================

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        await apiService.getCurrentUser();
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
      }
    };

    checkAuth();
  }, []);

  if (isAuthenticated === null) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

// ============================================================================
// MAIN LAYOUT COMPONENT
// ============================================================================

const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [user, setUser] = useState<any>(null);
  const [notifications, setNotifications] = useState<number>(0);

  useEffect(() => {
    // Fetch current user
    const fetchUser = async () => {
      try {
        const userData = await apiService.getCurrentUser();
        setUser(userData);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      }
    };

    fetchUser();

    // Connect WebSocket
    websocketService.connect();

    // Listen for notifications
    const unsubscribe = websocketService.on('notification', () => {
      setNotifications((prev) => prev + 1);
    });

    return () => {
      unsubscribe();
      websocketService.disconnect();
    };
  }, []);

  const handleLogout = async () => {
    try {
      await apiService.logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Tasks', icon: <TaskIcon />, path: '/tasks' },
    { text: 'Agents', icon: <AgentIcon />, path: '/agents' },
    { text: 'Integrations', icon: <IntegrationIcon />, path: '/integrations' },
    { text: 'System Health', icon: <HealthIcon />, path: '/health' },
  ];

  const drawerWidth = 240;

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AMAS - AI Multi-Agent System
          </Typography>

          {/* Notifications */}
          <IconButton color="inherit" sx={{ mr: 1 }}>
            <Badge badgeContent={notifications} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          {/* User Menu */}
          <IconButton
            color="inherit"
            onClick={(e) => setAnchorEl(e.currentTarget)}
          >
            <Avatar sx={{ width: 32, height: 32 }}>
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
          >
            <MenuItem disabled>
              <Typography variant="body2">{user?.email || 'User'}</Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => setAnchorEl(null)}>
              <ListItemIcon>
                <SettingsIcon fontSize="small" />
              </ListItemIcon>
              Settings
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Drawer
        variant="persistent"
        open={drawerOpen}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {menuItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton onClick={() => navigate(item.path)}>
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginLeft: drawerOpen ? 0 : `-${drawerWidth}px`,
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

// ============================================================================
// MAIN APP COMPONENT
// ============================================================================

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />

          {/* Protected Routes */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/tasks" element={<TaskList />} />
                    <Route path="/tasks/:taskId" element={<TaskExecutionView />} />
                    <Route path="/agents" element={<AgentList />} />
                    <Route path="/integrations" element={<IntegrationList />} />
                    <Route path="/health" element={<SystemHealth />} />
                  </Routes>
                </MainLayout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
```

***

### **Step 7B.7: Login Component**

**File**: `frontend/src/components/Auth/Login.tsx` (CREATE NEW)

```tsx
// frontend/src/components/Auth/Login.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Alert,
  Container,
  Avatar,
} from '@mui/material';
import { LockOutlined as LockIcon } from '@mui/icons-material';
import { apiService } from '../../services/api';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await apiService.login(username, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Card>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
              <Avatar sx={{ m: 1, bgcolor: 'primary.main', width: 56, height: 56 }}>
                <LockIcon />
              </Avatar>
              <Typography component="h1" variant="h4" gutterBottom>
                AMAS
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI Multi-Agent System
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                margin="normal"
                required
                autoFocus
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                margin="normal"
                required
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{ mt: 3, mb: 2 }}
              >
                {loading ? 'Signing In...' : 'Sign In'}
              </Button>

              <Typography variant="caption" color="text.secondary" display="block" align="center">
                Default credentials: admin / admin123
              </Typography>
            </form>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Login;
```

***

### **Step 7B.8: Package.json Dependencies**

**File**: `frontend/package.json` (COMPLETE VERSION)

```json
{
  "name": "amas-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@mui/material": "^5.14.0",
    "@mui/icons-material": "^5.14.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "axios": "^1.5.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.15.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "typescript": "^5.2.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/node": "^20.5.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "react-scripts": "5.0.1"
  }
}
```

***

### **Step 7B.9: Environment Configuration**

**File**: `frontend/.env.example` (CREATE NEW)

```env
# frontend/.env.example
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1

# WebSocket Configuration
REACT_APP_WS_URL=ws://localhost:8000

# Environment
REACT_APP_ENV=development

# Feature Flags
REACT_APP_ENABLE_PREDICTIONS=true
REACT_APP_ENABLE_INTEGRATIONS=true
```

***

### **Step 7B.10: Index & Main Entry Point**

**File**: `frontend/src/index.tsx` (COMPLETE VERSION)

```tsx
// frontend/src/index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**File**: `frontend/src/index.css` (COMPLETE VERSION)

```css
/* frontend/src/index.css */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #0a1929;
}

::-webkit-scrollbar-thumb {
  background: #3f51b5;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #5c6bc0;
}
```

***

**This completes Part 7B - Complete Frontend Implementation!** 🎉

**What's Fully Implemented**:
1. ✅ **Dashboard** - Real-time metrics with charts
2. ✅ **Task Management** - List, create, execute with ML predictions
3. ✅ **Real-Time Task Viewer** - Live execution monitoring
4. ✅ **Agent Management** - Performance tracking
5. ✅ **Integration Management** - All 6 platforms
6. ✅ **System Health** - Component status monitoring
7. ✅ **Authentication** - Login/logout flow
8. ✅ **App Shell** - Navigation, routing, layout
9. ✅ **WebSocket** - Real-time updates throughout
10. ✅ **Material-UI** - Professional dark theme

**Frontend Stack**:
- ✅ React 18 + TypeScript
- ✅ Material-UI v5 (Dark Theme)
- ✅ React Router v6
- ✅ Axios for API calls
- ✅ Chart.js for visualizations
- ✅ WebSocket for real-time updates

**Next Steps**:
- **Part 8**: Production Deployment Configuration
- **Part 9**: Testing Strategy & Implementation
- **Part 10**: Final Production Checklist

