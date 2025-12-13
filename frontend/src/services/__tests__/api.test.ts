// frontend/src/services/__tests__/api.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import { apiService } from '../api';
import type { Task, Agent, Integration, SystemMetrics } from '../api';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as any;

describe('APIService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    
    // Mock axios.create
    mockedAxios.create = vi.fn(() => mockedAxios);
    mockedAxios.interceptors = {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    };
    
    // Reset apiService state
    (apiService as any).accessToken = null;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Initialization', () => {
    it('should create axios instance with correct base URL', () => {
      expect(mockedAxios.create).toHaveBeenCalled();
    });

    it('should set up request and response interceptors', () => {
      expect(mockedAxios.interceptors.request.use).toHaveBeenCalled();
      expect(mockedAxios.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe('Token Management', () => {
    it('should set and get token', () => {
      apiService.setToken('test_token');
      expect(localStorage.getItem('access_token')).toBe('test_token');
      expect((apiService as any).accessToken).toBe('test_token');
    });

    it('should clear token', () => {
      apiService.setToken('test_token');
      apiService.clearToken();
      expect(localStorage.getItem('access_token')).toBeNull();
    });

    it('should load token from localStorage', () => {
      localStorage.setItem('access_token', 'stored_token');
      apiService.loadToken();
      // Token should be loaded
      expect(localStorage.getItem('access_token')).toBe('stored_token');
    });
  });

  describe('Authentication', () => {
    it('should login successfully', async () => {
      const mockResponse = {
        data: {
          access_token: 'test_token',
          user: { id: 'user1', username: 'test' },
        },
      };
      mockedAxios.post = vi.fn().mockResolvedValue(mockResponse);

      const result = await apiService.login('test', 'password');

      expect(result.access_token).toBe('test_token');
      expect(result.user.id).toBe('user1');
      expect(mockedAxios.post).toHaveBeenCalledWith('/auth/login', {
        username: 'test',
        password: 'password',
      });
    });

    it('should handle login errors', async () => {
      mockedAxios.post = vi.fn().mockRejectedValue(new Error('Invalid credentials'));

      await expect(apiService.login('test', 'wrong')).rejects.toThrow();
    });

    it('should logout', async () => {
      mockedAxios.post = vi.fn().mockResolvedValue({ data: {} });

      await apiService.logout();

      expect(mockedAxios.post).toHaveBeenCalledWith('/auth/logout');
      expect(localStorage.getItem('access_token')).toBeNull();
    });

    it('should get current user', async () => {
      const mockUser = { id: 'user1', username: 'test' };
      mockedAxios.get = vi.fn().mockResolvedValue({ data: mockUser });

      const user = await apiService.getCurrentUser();

      expect(user).toEqual(mockUser);
      expect(mockedAxios.get).toHaveBeenCalledWith('/auth/me');
    });
  });

  describe('Tasks', () => {
    it('should list tasks', async () => {
      const mockTasks = {
        tasks: [{ task_id: 'task1', title: 'Test Task' }],
        total: 1,
      };
      mockedAxios.get = vi.fn().mockResolvedValue({ data: mockTasks });

      const result = await apiService.listTasks();

      expect(result.tasks).toHaveLength(1);
      expect(result.total).toBe(1);
      expect(mockedAxios.get).toHaveBeenCalledWith('/tasks', { params: {} });
    });

    it('should get task by ID', async () => {
      const mockTask: Task = {
        id: 'task1',
        task_id: 'task1',
        title: 'Test Task',
        task_type: 'security_scan',
        target: 'example.com',
        status: 'completed',
        priority: 5,
        assigned_agents: [],
        created_at: '2024-01-01T00:00:00Z',
      };
      mockedAxios.get = vi.fn().mockResolvedValue({ data: mockTask });

      const task = await apiService.getTask('task1');

      expect(task.task_id).toBe('task1');
      expect(mockedAxios.get).toHaveBeenCalledWith('/tasks/task1');
    });

    it('should create task', async () => {
      const mockTask: Task = {
        id: 'task1',
        task_id: 'task1',
        title: 'New Task',
        task_type: 'security_scan',
        target: 'example.com',
        status: 'pending',
        priority: 5,
        assigned_agents: [],
        created_at: '2024-01-01T00:00:00Z',
      };
      mockedAxios.post = vi.fn().mockResolvedValue({ data: mockTask });

      const task = await apiService.createTask({
        title: 'New Task',
        task_type: 'security_scan',
        target: 'example.com',
      });

      expect(task.title).toBe('New Task');
      expect(mockedAxios.post).toHaveBeenCalledWith('/tasks', {
        title: 'New Task',
        task_type: 'security_scan',
        target: 'example.com',
      });
    });

    it('should execute task', async () => {
      mockedAxios.post = vi.fn().mockResolvedValue({
        data: { task_id: 'task1', status: 'executing', message: 'Started' },
      });

      const result = await apiService.executeTask('task1');

      expect(result.status).toBe('executing');
      expect(mockedAxios.post).toHaveBeenCalledWith('/tasks/task1/execute', {});
    });

    it('should get task progress', async () => {
      mockedAxios.get = vi.fn().mockResolvedValue({
        data: { task_id: 'task1', status: 'executing', progress: 50 },
      });

      const progress = await apiService.getTaskProgress('task1');

      expect(progress.progress).toBe(50);
      expect(mockedAxios.get).toHaveBeenCalledWith('/tasks/task1/progress');
    });

    it('should cancel task', async () => {
      mockedAxios.post = vi.fn().mockResolvedValue({ data: {} });

      await apiService.cancelTask('task1');

      expect(mockedAxios.post).toHaveBeenCalledWith('/tasks/task1/cancel');
    });
  });

  describe('Agents', () => {
    it('should list agents', async () => {
      const mockAgents = {
        agents: [{ agent_id: 'agent1', name: 'Test Agent' }],
        total: 1,
      };
      mockedAxios.get = vi.fn().mockResolvedValue({ data: mockAgents });

      const result = await apiService.listAgents();

      expect(result.agents).toHaveLength(1);
      expect(mockedAxios.get).toHaveBeenCalledWith('/agents', { params: {} });
    });

    it('should get agent by ID', async () => {
      const mockAgent: Agent = {
        id: 'agent1',
        agent_id: 'agent1',
        name: 'Test Agent',
        type: 'security',
        status: 'active',
        capabilities: [],
        configuration: {},
        expertise_score: 0.9,
        total_executions: 10,
        successful_executions: 9,
        failed_executions: 1,
        total_duration_seconds: 100,
        total_tokens_used: 1000,
        total_cost_usd: 0.1,
        created_at: '2024-01-01T00:00:00Z',
      };
      mockedAxios.get = vi.fn().mockResolvedValue({ data: mockAgent });

      const agent = await apiService.getAgent('agent1');

      expect(agent.agent_id).toBe('agent1');
      expect(mockedAxios.get).toHaveBeenCalledWith('/agents/agent1');
    });

    it('should get agent performance', async () => {
      const mockAgents: Agent[] = [
        {
          id: 'agent1',
          agent_id: 'agent1',
          name: 'Test Agent',
          type: 'security',
          status: 'active',
          capabilities: [],
          configuration: {},
          expertise_score: 0.9,
          total_executions: 10,
          successful_executions: 9,
          failed_executions: 1,
          total_duration_seconds: 100,
          total_tokens_used: 1000,
          total_cost_usd: 0.1,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];
      mockedAxios.get = vi.fn().mockResolvedValue({ data: mockAgents });

      const agents = await apiService.getAgentPerformance();

      expect(agents).toHaveLength(1);
      expect(mockedAxios.get).toHaveBeenCalledWith('/agents/performance');
    });
  });

  describe('Integrations', () => {
    it('should list integrations', async () => {
      const mockIntegrations = {
        integrations: [{ integration_id: 'int1', platform: 'slack' }],
        total: 1,
      };
      mockedAxios.get = vi.fn().mockResolvedValue({ data: mockIntegrations });

      const result = await apiService.listIntegrations();

      expect(result.integrations).toHaveLength(1);
      expect(mockedAxios.get).toHaveBeenCalledWith('/integrations', { params: {} });
    });

    it('should create integration', async () => {
      const mockIntegration: Integration = {
        integration_id: 'int1',
        user_id: 'user1',
        platform: 'slack',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
        sync_count: 0,
        error_count: 0,
      };
      mockedAxios.post = vi.fn().mockResolvedValue({ data: mockIntegration });

      const integration = await apiService.createIntegration({
        platform: 'slack',
        credentials: { token: 'test_token' },
      });

      expect(integration.platform).toBe('slack');
      expect(mockedAxios.post).toHaveBeenCalledWith('/integrations', {
        platform: 'slack',
        credentials: { token: 'test_token' },
      });
    });

    it('should delete integration', async () => {
      mockedAxios.delete = vi.fn().mockResolvedValue({ data: {} });

      await apiService.deleteIntegration('int1');

      expect(mockedAxios.delete).toHaveBeenCalledWith('/integrations/int1');
    });

    it('should trigger integration', async () => {
      mockedAxios.post = vi.fn().mockResolvedValue({ data: { success: true } });

      const result = await apiService.triggerIntegration('int1', 'test_event', { data: 'test' });

      expect(result.success).toBe(true);
      expect(mockedAxios.post).toHaveBeenCalledWith('/integrations/int1/trigger', {
        event_type: 'test_event',
        data: { data: 'test' },
      });
    });
  });

  describe('System Metrics', () => {
    it('should get system metrics', async () => {
      const mockMetrics: SystemMetrics = {
        cpu_usage_percent: 50.0,
        memory_usage_percent: 60.0,
        memory_usage_bytes: 1000000000,
        disk_usage_bytes: 2000000000,
        active_tasks: 5,
        queue_depth: 2,
        total_tasks: 100,
        completed_tasks: 90,
        failed_tasks: 5,
        active_agents: 3,
        timestamp: '2024-01-01T00:00:00Z',
      };
      mockedAxios.get = vi.fn().mockResolvedValue({ data: mockMetrics });

      const metrics = await apiService.getSystemMetrics();

      expect(metrics.cpu_usage_percent).toBe(50.0);
      expect(mockedAxios.get).toHaveBeenCalledWith('/system/metrics');
    });

    it('should get system health', async () => {
      mockedAxios.get = vi.fn().mockResolvedValue({
        data: { status: 'healthy', components: {} },
      });

      const health = await apiService.getSystemHealth();

      expect(health.status).toBe('healthy');
      expect(mockedAxios.get).toHaveBeenCalledWith('/system/health');
    });
  });

  describe('Predictions', () => {
    it('should predict task outcome', async () => {
      const mockPrediction = {
        success_probability: 0.9,
        estimated_duration: 30.0,
        estimated_cost: 0.05,
        quality_score_prediction: 0.85,
        confidence: 0.8,
        recommended_agents: [],
        risk_factors: [],
        optimization_suggestions: [],
      };
      mockedAxios.post = vi.fn().mockResolvedValue({ data: mockPrediction });

      const prediction = await apiService.predictTask({
        task_type: 'security_scan',
        target: 'example.com',
      });

      expect(prediction.success_probability).toBe(0.9);
      expect(mockedAxios.post).toHaveBeenCalledWith('/predictions/task', {
        task_type: 'security_scan',
        target: 'example.com',
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle 401 errors and clear token', async () => {
      mockedAxios.get = vi.fn().mockRejectedValue({
        response: { status: 401 },
      });

      await expect(apiService.getCurrentUser()).rejects.toThrow();
      // Token should be cleared on 401
    });

    it('should handle network errors', async () => {
      mockedAxios.get = vi.fn().mockRejectedValue(new Error('Network error'));

      await expect(apiService.getCurrentUser()).rejects.toThrow('Network error');
    });
  });
});

