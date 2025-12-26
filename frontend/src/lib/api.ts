// Mock API client for development
// Replace with real API calls when backend is ready

export interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  activeAgents: number;
  completedTasks: number;
  successRate: number;
  avgLatency: number;
}

export interface Agent {
  id: string;
  name: string;
  status: 'idle' | 'running' | 'error';
  tasksCompleted: number;
  efficiency: number;
  lastActive: string;
}

// Mock system metrics
const mockSystemMetrics: SystemMetrics = {
  cpuUsage: 42,
  memoryUsage: 58,
  activeAgents: 12,
  completedTasks: 1543,
  successRate: 98.7,
  avgLatency: 23,
};

// Mock agents
const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'DataProcessor',
    status: 'running',
    tasksCompleted: 342,
    efficiency: 96.5,
    lastActive: 'now',
  },
  {
    id: '2',
    name: 'TaskOrchestrator',
    status: 'running',
    tasksCompleted: 287,
    efficiency: 94.2,
    lastActive: 'now',
  },
  {
    id: '3',
    name: 'AnalysisAgent',
    status: 'idle',
    tasksCompleted: 156,
    efficiency: 97.8,
    lastActive: '2m ago',
  },
];

/**
 * Fetch system metrics from API
 * @returns Promise resolving to SystemMetrics
 */
export async function fetchSystemMetrics(): Promise<SystemMetrics> {
  // Mock delay
  await new Promise(resolve => setTimeout(resolve, 300));
  return mockSystemMetrics;
}

/**
 * Fetch agent status from API
 * @returns Promise resolving to array of Agents
 */
export async function fetchAgentStatus(): Promise<Agent[]> {
  // Mock delay
  await new Promise(resolve => setTimeout(resolve, 300));
  return mockAgents;
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
    'metrics': `Active agents: ${mockSystemMetrics.activeAgents} | Tasks: ${mockSystemMetrics.completedTasks} | Success: ${mockSystemMetrics.successRate}%`,
    'ping': 'pong',
    'agents': `Active agents: ${mockAgents.filter(a => a.status === 'running').length} / ${mockAgents.length}`,
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
