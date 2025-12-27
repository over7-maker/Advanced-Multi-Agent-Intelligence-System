/// <reference types="../vite-env" />
// Mock API client for development
// Replace with real API calls when backend is ready

export interface SystemMetrics {
  cpu: number;
  memory: number;
  activeAgents: number;
  tasksCompleted: number;
  uptime: number;
  latency: number;
}

export interface Agent {
  id: string;
  name: string;
  status: 'healthy' | 'running' | 'error' | 'idle';
  tasksCompleted: number;
  uptime: number;
  lastActive: string;
}

// Mock system metrics
const mockSystemMetrics: SystemMetrics = {
  cpu: 42,
  memory: 58,
  activeAgents: 12,
  tasksCompleted: 1543,
  uptime: 99.97,
  latency: 23,
};

// Mock agents
const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'DataProcessor',
    status: 'healthy',
    tasksCompleted: 342,
    uptime: 99.8,
    lastActive: 'now',
  },
  {
    id: '2',
    name: 'TaskOrchestrator',
    status: 'healthy',
    tasksCompleted: 287,
    uptime: 99.9,
    lastActive: 'now',
  },
  {
    id: '3',
    name: 'AnalysisAgent',
    status: 'healthy',
    tasksCompleted: 156,
    uptime: 98.5,
    lastActive: '2m ago',
  },
  {
    id: '4',
    name: 'ValidationBot',
    status: 'healthy',
    tasksCompleted: 421,
    uptime: 99.7,
    lastActive: 'now',
  },
  {
    id: '5',
    name: 'ReportGenerator',
    status: 'healthy',
    tasksCompleted: 189,
    uptime: 99.2,
    lastActive: '5m ago',
  },
  {
    id: '6',
    name: 'APIGateway',
    status: 'healthy',
    tasksCompleted: 512,
    uptime: 99.99,
    lastActive: 'now',
  },
];

/**
 * Fetch system metrics from API
 * Uses real landing API endpoint when available, falls back to mock data
 * @returns Promise resolving to SystemMetrics
 */
export async function fetchSystemMetrics(): Promise<SystemMetrics> {
  try {
    const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    const response = await fetch(`${apiUrl}/landing/metrics`, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    const data = await response.json();
    
    // Validate response structure
    if (typeof data.cpu_usage_percent !== 'number' || 
        typeof data.memory_usage_percent !== 'number') {
      throw new Error('Invalid response format from API');
    }
    
    // Transform landing API response to frontend format
    return {
      cpu: Math.max(0, Math.min(100, data.cpu_usage_percent || 0)),
      memory: Math.max(0, Math.min(100, data.memory_usage_percent || 0)),
      activeAgents: Math.max(0, Math.floor(data.active_agents || 0)),
      tasksCompleted: Math.max(0, Math.floor(data.completed_tasks || 0)),
      uptime: Math.max(0, data.uptime_hours || 0),
      latency: Math.max(0, data.avg_task_duration || 0),
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    // Don't log AbortError (timeout) as warning, it's expected
    if (error instanceof Error && error.name !== 'AbortError') {
      console.warn('Failed to fetch real metrics, using mock data:', errorMessage);
    }
    
    // Fallback to mock data
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockSystemMetrics;
  }
}

/**
 * Fetch agent status from API
 * Uses real landing API endpoint when available, falls back to mock data
 * @returns Promise resolving to array of Agents
 */
export async function fetchAgentStatus(): Promise<Agent[]> {
  try {
    const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    const response = await fetch(`${apiUrl}/landing/agents-status`, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    const data = await response.json();
    
    // Validate response is an array
    if (!Array.isArray(data)) {
      throw new Error('Invalid response format: expected array');
    }
    
    // Transform landing API response to frontend format with validation
    return data.map((agent: any, index: number) => {
      const agentId = agent.agent_id || agent.id || `agent-${index}`;
      const agentName = agent.name || 'Unknown Agent';
      const agentStatus = agent.status === 'active' ? 'healthy' : 
                         agent.status === 'error' ? 'error' : 'idle';
      const tasksCompleted = Math.max(0, Math.floor(agent.executions_today || 0));
      const successRate = agent.success_rate ? Math.max(0, Math.min(100, agent.success_rate * 100)) : 99.0;
      
      return {
        id: agentId,
        name: agentName,
        status: agentStatus,
        tasksCompleted: tasksCompleted,
        uptime: successRate,
        lastActive: 'now',
      };
    });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    // Don't log AbortError (timeout) as warning, it's expected
    if (error instanceof Error && error.name !== 'AbortError') {
      console.warn('Failed to fetch real agent status, using mock data:', errorMessage);
    }
    
    // Fallback to mock data
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockAgents;
  }
}

/**
 * Execute demo command (mock)
 * @param command Command to execute
 * @returns Promise resolving to command output
 */
export async function executeDemoCommand(command: string): Promise<string> {
  // Mock delay
  await new Promise(resolve => setTimeout(resolve, 200));
  
  const commands: Record<string, string> = {
    'help': 'Available commands: help, status, metrics, ping, agents',
    'status': 'System status: ✅ All systems operational',
    'metrics': `Active agents: ${mockSystemMetrics.activeAgents} | Tasks: ${mockSystemMetrics.tasksCompleted} | Uptime: ${mockSystemMetrics.uptime}%`,
    'ping': 'pong',
    'agents': `Active agents: ${mockAgents.filter(a => a.status === 'healthy').length} / ${mockAgents.length}`,
  };
  
  return commands[command.toLowerCase()] || `❌ Command not found: ${command}. Type 'help' for available commands.`;
}

/**
 * Submit feedback (mock)
 * @param feedback Feedback message
 * @returns Promise resolving when feedback is submitted
 */
export async function submitFeedback(feedback: string): Promise<void> {
  // Mock delay
  await new Promise(resolve => setTimeout(resolve, 500));
  console.log('Feedback submitted:', feedback);
}

/**
 * Health check (mock)
 * @returns Promise resolving to health status
 */
export async function healthCheck(): Promise<{ status: string }> {
  // Mock delay
  await new Promise(resolve => setTimeout(resolve, 100));
  return { status: 'healthy' };
}

// For real API integration, uncomment and configure:
// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
// 
// export async function fetchSystemMetrics(): Promise<SystemMetrics> {
//   const response = await fetch(`${API_BASE_URL}/metrics`);
//   return response.json();
// }
// 
// export async function fetchAgentStatus(): Promise<Agent[]> {
//   const response = await fetch(`${API_BASE_URL}/agents`);
//   return response.json();
// }
