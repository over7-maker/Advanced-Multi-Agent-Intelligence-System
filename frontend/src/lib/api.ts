// Mock data for development
const USE_MOCK_DATA = true; // Set to false when backend is ready

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
  status: 'healthy' | 'warning' | 'error';
  tasksCompleted: number;
  uptime: number;
}

export interface DemoResponse {
  output: string;
  executionTime: number;
  status: 'success' | 'error';
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Mock data generators
function generateMockMetrics(): SystemMetrics {
  return {
    cpu: Math.floor(Math.random() * 60) + 20,
    memory: Math.floor(Math.random() * 30) + 50,
    activeAgents: Math.floor(Math.random() * 5) + 10,
    tasksCompleted: Math.floor(Math.random() * 100) + 1800,
    uptime: 99.97,
    latency: Math.floor(Math.random() * 15) + 18,
  };
}

function generateMockAgents(): Agent[] {
  const agentNames = [
    'SecurityAgent',
    'CodeAgent',
    'ResearchAgent',
    'DataAgent',
    'AnalyticsAgent',
    'OrchestratorAgent',
    'CacheAgent',
    'MonitorAgent',
    'DeploymentAgent',
    'IntegrationAgent',
    'ValidationAgent',
    'OptimizationAgent',
  ];

  return agentNames.map((name, index) => ({
    id: `agent-${index}`,
    name,
    status: Math.random() > 0.95 ? 'warning' : 'healthy',
    tasksCompleted: Math.floor(Math.random() * 1000),
    uptime: 99.9 + Math.random() * 0.07,
  }));
}

function generateMockDemoOutput(command: string): string {
  const outputs: Record<string, string> = {
    'spawn-agent': `
✓ Agent spawned successfully
Agent ID: agent_20241226_001
Type: CodeAgent
Memory: 256MB
Status: RUNNING
Initialization time: 145ms
    `,
    'execute-task': `
✓ Task execution started
Task ID: task_20241226_001
Agent: CodeAgent_01
Command: analyze_code
Progress: [████████░░] 80%
Estimated time remaining: 2.3s
    `,
    'query-database': `
✓ Database query executed
Query time: 234ms
Results returned: 42 rows
Data size: 512KB
Cache hit: Yes
Cache duration: 3600s
    `,
    'check-health': `
✓ System health check complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: HEALTHY
Uptime: 99.97%
Active Agents: 12
Memory Usage: 68%
CPU Usage: 42%
Latency (avg): 23ms
ErrorsLast24h: 0
    `,
    'list-agents': `
✓ Agent list retrieved
Total agents: 12
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. SecurityAgent      [HEALTHY] - 847 tasks
2. CodeAgent         [HEALTHY] - 923 tasks
3. ResearchAgent     [HEALTHY] - 612 tasks
4. DataAgent         [HEALTHY] - 445 tasks
5. AnalyticsAgent    [HEALTHY] - 234 tasks
6. OrchestratorAgent [HEALTHY] - 1847 tasks
7. CacheAgent        [HEALTHY] - 89 tasks
8. MonitorAgent      [HEALTHY] - 234 tasks
9. DeploymentAgent   [HEALTHY] - 156 tasks
10. IntegrationAgent [HEALTHY] - 423 tasks
11. ValidationAgent  [HEALTHY] - 567 tasks
12. OptimizationAgent[HEALTHY] - 345 tasks
    `,
  };

  return outputs[command] || `
✓ Command executed successfully
Command: ${command}
Execution time: ${Math.floor(Math.random() * 500) + 100}ms
Status: COMPLETE
  `;
}

// API functions
export async function fetchSystemMetrics(): Promise<SystemMetrics> {
  if (USE_MOCK_DATA) {
    await new Promise(r => setTimeout(r, 500));
    return generateMockMetrics();
  }

  try {
    const response = await fetch(`${API_BASE}/metrics`);
    if (!response.ok) throw new Error('Failed to fetch metrics');
    return response.json();
  } catch (error) {
    console.error('Error fetching metrics:', error);
    return generateMockMetrics();
  }
}

export async function fetchAgentStatus(): Promise<Agent[]> {
  if (USE_MOCK_DATA) {
    await new Promise(r => setTimeout(r, 600));
    return generateMockAgents();
  }

  try {
    const response = await fetch(`${API_BASE}/agents`);
    if (!response.ok) throw new Error('Failed to fetch agents');
    return response.json();
  } catch (error) {
    console.error('Error fetching agents:', error);
    return generateMockAgents();
  }
}

export async function executeDemo(command: string): Promise<DemoResponse> {
  if (USE_MOCK_DATA) {
    const executionTime = Math.floor(Math.random() * 800) + 200;
    await new Promise(r => setTimeout(r, executionTime));
    return {
      output: generateMockDemoOutput(command),
      executionTime,
      status: 'success',
    };
  }

  try {
    const response = await fetch(`${API_BASE}/demo/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command }),
    });
    if (!response.ok) throw new Error('Failed to execute demo');
    return response.json();
  } catch (error) {
    console.error('Error executing demo:', error);
    return {
      output: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      executionTime: 0,
      status: 'error',
    };
  }
}

export async function healthCheck(): Promise<boolean> {
  if (USE_MOCK_DATA) {
    return true;
  }

  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export async function submitFeedback(feedback: {
  email: string;
  message: string;
  type: 'feedback' | 'bug' | 'feature';
}): Promise<{ success: boolean; message: string }> {
  if (USE_MOCK_DATA) {
    await new Promise(r => setTimeout(r, 300));
    return {
      success: true,
      message: 'Thank you for your feedback! We appreciate your input.',
    };
  }

  try {
    const response = await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(feedback),
    });
    if (!response.ok) throw new Error('Failed to submit feedback');
    return response.json();
  } catch (error) {
    console.error('Error submitting feedback:', error);
    return {
      success: false,
      message: 'Failed to submit feedback. Please try again.',
    };
  }
}
