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
