// Mock API service
import { vi } from 'vitest';

export const mockApiService = {
  getCurrentUser: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
  listTasks: vi.fn(),
  getTask: vi.fn(),
  createTask: vi.fn(),
  executeTask: vi.fn(),
  cancelTask: vi.fn(),
  getSystemMetrics: vi.fn(),
  getTaskAnalytics: vi.fn(),
  getAgentPerformance: vi.fn(),
  getSystemHealth: vi.fn(),
  predictTask: vi.fn(),
};

export const mockUser = {
  id: '1',
  user_id: 'user_1',
  username: 'testuser',
  email: 'test@example.com',
  roles: ['user'],
  permissions: ['read'],
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
};

export const mockTask = {
  id: '1',
  task_id: 'task_1',
  title: 'Test Task',
  description: 'Test Description',
  task_type: 'security_scan',
  target: 'https://example.com',
  status: 'pending' as const,
  priority: 5,
  assigned_agents: [],
  created_at: '2024-01-01T00:00:00Z',
};

export const mockSystemMetrics = {
  cpu_usage_percent: 45.5,
  memory_usage_percent: 62.3,
  memory_usage_bytes: 1024 * 1024 * 1024,
  disk_usage_bytes: 10 * 1024 * 1024 * 1024,
  active_tasks: 5,
  queue_depth: 2,
  total_tasks: 100,
  completed_tasks: 90,
  failed_tasks: 5,
  active_agents: 8,
  timestamp: new Date().toISOString(),
};

export const mockTaskAnalytics = {
  total_tasks: 100,
  completed_tasks: 90,
  failed_tasks: 5,
  avg_duration: 15.5,
  avg_quality_score: 0.85,
  total_cost: 125.50,
  success_rate: 0.95,
  task_distribution: {
    security_scan: 30,
    code_analysis: 40,
    intelligence_gathering: 20,
    performance_analysis: 10,
  },
};

export const mockTaskPrediction = {
  success_probability: 0.85,
  estimated_duration: 20,
  estimated_cost: 0.05,
  quality_score_prediction: 0.88,
  confidence: 0.9,
  recommended_agents: [
    {
      agent_id: 'agent_1',
      agent_name: 'Security Agent',
      expertise_score: 0.95,
      estimated_duration: 18,
      historical_success_rate: 0.92,
      recommendation_confidence: 0.9,
      reason: 'High expertise in security scanning',
    },
  ],
  risk_factors: [],
  optimization_suggestions: [],
};

