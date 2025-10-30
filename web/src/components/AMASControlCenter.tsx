import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Shield, 
  Search, 
  Zap, 
  FileText, 
  TestTube, 
  Network,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users
} from 'lucide-react';
import { Line, Doughnut } from 'react-chartjs-2';
import VoiceCommandInterface from './VoiceCommandInterface';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement
);

interface Agent {
  name: string;
  status: 'active' | 'idle' | 'busy' | 'error';
  tasksCompleted: number;
  avgResponseTime: number;
  icon: React.ReactNode;
}

interface SystemMetrics {
  timestamp: string;
  cpuPercent: number;
  memoryPercent: number;
  activeAgents: number;
  taskQueueLength: number;
  throughputPerSecond: number;
  systemHealth: {
    score: number;
    status: string;
    color: string;
  };
}

interface Task {
  id: string;
  type: string;
  target: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  startTime: string;
  agentsInvolved: string[];
}

interface AMASControlCenterProps {
  onViewChange?: (view: 'dashboard' | 'agents' | 'tasks' | 'metrics' | 'voice') => void;
  onAgentSelect?: (agent: any) => void;
  onTaskSelect?: (task: any) => void;
  onVoiceCommand?: (command: any) => void;
  onLogout?: () => void;
  systemHealth?: any;
}

const AMASControlCenter: React.FC<AMASControlCenterProps> = ({
  onViewChange,
  onTaskSelect,
  onVoiceCommand,
  onLogout,
}) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [activeTasks, setActiveTasks] = useState<Task[]>([]);
  const [command, setCommand] = useState('');
  // Command history not tracked currently

  // Mock data initialization
  useEffect(() => {
    const mockAgents: Agent[] = [
      {
        name: 'Security Expert',
        status: 'active',
        tasksCompleted: 142,
        avgResponseTime: 2.3,
        icon: <Shield className="w-5 h-5" />
      },
      {
        name: 'Code Analysis',
        status: 'active', 
        tasksCompleted: 89,
        avgResponseTime: 1.8,
        icon: <Brain className="w-5 h-5" />
      },
      {
        name: 'Intelligence Gathering',
        status: 'busy',
        tasksCompleted: 67,
        avgResponseTime: 3.1,
        icon: <Search className="w-5 h-5" />
      },
      {
        name: 'Performance Monitor',
        status: 'active',
        tasksCompleted: 156,
        avgResponseTime: 1.2,
        icon: <Activity className="w-5 h-5" />
      },
      {
        name: 'Documentation',
        status: 'idle',
        tasksCompleted: 23,
        avgResponseTime: 2.7,
        icon: <FileText className="w-5 h-5" />
      },
      {
        name: 'Testing Coordinator',
        status: 'active',
        tasksCompleted: 45,
        avgResponseTime: 3.5,
        icon: <TestTube className="w-5 h-5" />
      },
      {
        name: 'Integration Manager',
        status: 'active',
        tasksCompleted: 78,
        avgResponseTime: 2.1,
        icon: <Network className="w-5 h-5" />
      }
    ];

    setAgents(mockAgents);

    // Mock real-time metrics updates
    const updateMetrics = () => {
      setMetrics({
        timestamp: new Date().toISOString(),
        cpuPercent: Math.random() * 50 + 30,
        memoryPercent: Math.random() * 40 + 40,
        activeAgents: 7,
        taskQueueLength: Math.floor(Math.random() * 10),
        throughputPerSecond: Math.random() * 5 + 2,
        systemHealth: {
          score: 92.5,
          status: 'excellent',
          color: 'green'
        }
      });
    };

    updateMetrics();
    const interval = setInterval(updateMetrics, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleCommandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim()) return;

    // History tracking disabled

    // Mock task creation
    const newTask: Task = {
      id: `task_${Date.now()}`,
      type: detectTaskType(command),
      target: extractTarget(command),
      status: 'running',
      progress: 0,
      startTime: new Date().toISOString(),
      agentsInvolved: getRequiredAgents(command)
    };

    setActiveTasks(prev => [...prev, newTask]);
    
    // Notify parent component
    onTaskSelect?.(newTask);

    // Simulate task progress
    simulateTaskProgress(newTask.id);

    setCommand('');
  };

  const detectTaskType = (cmd: string): string => {
    const lower = cmd.toLowerCase();
    if (lower.includes('scan') || lower.includes('security')) return 'security_scan';
    if (lower.includes('analyze') || lower.includes('code')) return 'code_analysis';
    if (lower.includes('research') || lower.includes('investigate')) return 'intelligence_gathering';
    return 'general_analysis';
  };

  const extractTarget = (cmd: string): string => {
    const urlMatch = cmd.match(/https?:\/\/[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
    if (urlMatch) return urlMatch[0];
    
    const quotedMatch = cmd.match(/"([^"]+)"/);
    if (quotedMatch) return quotedMatch[1];
    
    return 'general';
  };

  const getRequiredAgents = (cmd: string): string[] => {
    const type = detectTaskType(cmd);
    switch (type) {
      case 'security_scan':
        return ['Security Expert', 'Intelligence Gathering'];
      case 'code_analysis':
        return ['Code Analysis', 'Security Expert'];
      case 'intelligence_gathering':
        return ['Intelligence Gathering', 'Security Expert'];
      default:
        return ['Code Analysis'];
    }
  };

  const simulateTaskProgress = (taskId: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 20;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        
        // Update task to completed
        setActiveTasks(prev => 
          prev.map(task => 
            task.id === taskId 
              ? { ...task, status: 'completed', progress: 100 }
              : task
          )
        );
        
        // Remove completed task after 5 seconds
        setTimeout(() => {
          setActiveTasks(prev => prev.filter(task => task.id !== taskId));
        }, 5000);
      } else {
        setActiveTasks(prev => 
          prev.map(task => 
            task.id === taskId 
              ? { ...task, progress: Math.min(progress, 100) }
              : task
          )
        );
      }
    }, 1000);
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active': return 'text-green-500';
      case 'busy': return 'text-yellow-500';
      case 'idle': return 'text-gray-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string): React.ReactNode => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'busy': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'idle': return <Activity className="w-4 h-4 text-gray-500" />;
      case 'error': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  // Chart data
  const systemHealthData = {
    labels: ['CPU', 'Memory', 'Queue', 'Errors'],
    datasets: [{
      data: [75, 60, 85, 95],
      backgroundColor: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6'],
      borderWidth: 0
    }]
  };

  const performanceData = {
    labels: ['Last 24h', '12h', '6h', '3h', '1h', 'Now'],
    datasets: [{
      label: 'Response Time (s)',
      data: [2.1, 1.9, 2.3, 2.0, 1.8, metrics?.cpuPercent ? metrics.cpuPercent / 20 : 2.2],
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }]
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      {/* Neural Network Background */}
      <div className="absolute inset-0 opacity-10">
        <svg className="w-full h-full" viewBox="0 0 1000 1000">
          {/* Animated neural network pattern */}
          <defs>
            <radialGradient id="neuralGrad">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#1e40af" stopOpacity="0.2" />
            </radialGradient>
          </defs>
          
          {/* Neural nodes */}
          {[...Array(20)].map((_, i) => (
            <circle
              key={i}
              cx={Math.random() * 1000}
              cy={Math.random() * 1000}
              r="3"
              fill="url(#neuralGrad)"
              className="animate-pulse"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
          
          {/* Connecting lines */}
          {[...Array(15)].map((_, i) => (
            <line
              key={i}
              x1={Math.random() * 1000}
              y1={Math.random() * 1000}
              x2={Math.random() * 1000}
              y2={Math.random() * 1000}
              stroke="#3b82f6"
              strokeWidth="0.5"
              strokeOpacity="0.3"
              className="animate-pulse"
            />
          ))}
        </svg>
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-blue-800/30 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  AMAS Control Center
                </h1>
                <p className="text-sm text-blue-300">Advanced Multi-Agent Intelligence System</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              {/* Navigation Buttons */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onViewChange?.('agents')}
                  className="px-4 py-2 bg-slate-700/50 text-gray-300 rounded-lg hover:bg-slate-600/50 transition-colors"
                >
                  Agents
                </button>
                <button
                  onClick={() => onViewChange?.('tasks')}
                  className="px-4 py-2 bg-slate-700/50 text-gray-300 rounded-lg hover:bg-slate-600/50 transition-colors"
                >
                  Tasks
                </button>
                <button
                  onClick={() => onViewChange?.('metrics')}
                  className="px-4 py-2 bg-slate-700/50 text-gray-300 rounded-lg hover:bg-slate-600/50 transition-colors"
                >
                  Metrics
                </button>
                <button
                  onClick={() => onViewChange?.('voice')}
                  className="px-4 py-2 bg-slate-700/50 text-gray-300 rounded-lg hover:bg-slate-600/50 transition-colors"
                >
                  Voice
                </button>
              </div>

              {/* Voice Command Interface */}
              <VoiceCommandInterface 
                onCommandProcessed={onVoiceCommand}
                compact={true}
              />

              {/* System Health */}
              {metrics && (
                <div className="flex items-center space-x-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">{metrics.systemHealth.score}%</div>
                    <div className="text-xs text-gray-400">Health Score</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">{metrics.activeAgents}</div>
                    <div className="text-xs text-gray-400">Active Agents</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">{metrics.throughputPerSecond.toFixed(1)}</div>
                    <div className="text-xs text-gray-400">Tasks/sec</div>
                  </div>
                </div>
              )}

              {/* Logout Button */}
              {onLogout && (
                <button
                  onClick={onLogout}
                  className="px-4 py-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors"
                >
                  Logout
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Command Interface */}
        <div className="mb-8">
          <form onSubmit={handleCommandSubmit} className="relative">
            <div className="relative">
              <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="Tell AMAS what you want to accomplish..."
                className="w-full px-6 py-4 bg-black/40 border border-blue-600/30 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 backdrop-blur-xl"
              />
              <button
                type="submit"
                className="absolute right-2 top-2 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center space-x-2"
              >
                <Zap className="w-4 h-4" />
                <span>Execute</span>
              </button>
            </div>
          </form>
          
          {/* Command suggestions */}
          <div className="mt-2 flex flex-wrap gap-2">
            {[
              'scan google.com for vulnerabilities',
              'analyze code quality of github.com/example/repo',
              'research latest AI security trends'
            ].map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => setCommand(suggestion)}
                className="px-3 py-1 text-xs bg-blue-600/20 text-blue-300 rounded-full hover:bg-blue-600/30 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Agents Panel */}
          <div className="lg:col-span-8">
            <div className="bg-black/40 backdrop-blur-xl rounded-xl border border-blue-600/30 p-6">
              <h2 className="text-xl font-semibold mb-6 flex items-center">
                <Users className="w-5 h-5 mr-2 text-blue-400" />
                AI Agent Orchestra
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {agents.map((agent, idx) => (
                  <div key={idx} className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-lg p-4 border border-gray-700/50 hover:border-blue-500/50 transition-all duration-200">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <div className={`${getStatusColor(agent.status)}`}>
                          {agent.icon}
                        </div>
                        <h3 className="font-medium text-sm">{agent.name}</h3>
                      </div>
                      {getStatusIcon(agent.status)}
                    </div>
                    
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Tasks:</span>
                        <span className="text-white">{agent.tasksCompleted}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Avg Time:</span>
                        <span className="text-white">{agent.avgResponseTime}s</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Active Tasks */}
            {activeTasks.length > 0 && (
              <div className="mt-8 bg-black/40 backdrop-blur-xl rounded-xl border border-blue-600/30 p-6">
                <h2 className="text-xl font-semibold mb-6 flex items-center">
                  <Activity className="w-5 h-5 mr-2 text-green-400" />
                  Active Tasks
                </h2>
                
                <div className="space-y-4">
                  {activeTasks.map((task) => (
                    <div key={task.id} className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 rounded-lg p-4 border border-gray-700/50">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h3 className="font-medium">{task.type.replace('_', ' ').toUpperCase()}</h3>
                          <p className="text-sm text-gray-400">{task.target}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-blue-400">{Math.round(task.progress)}%</div>
                          <div className="text-xs text-gray-400">{task.status}</div>
                        </div>
                      </div>
                      
                      <div className="mb-2">
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${task.progress}%` }}
                          ></div>
                        </div>
                      </div>
                      
                      <div className="text-xs text-gray-400">
                        Agents: {task.agentsInvolved.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Metrics Sidebar */}
          <div className="lg:col-span-4 space-y-6">
            {/* System Health */}
            <div className="bg-black/40 backdrop-blur-xl rounded-xl border border-blue-600/30 p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Activity className="w-4 h-4 mr-2 text-green-400" />
                System Health
              </h3>
              
              <div className="w-40 h-40 mx-auto">
                <Doughnut 
                  data={systemHealthData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false }
                    }
                  }}
                />
              </div>
              
              {metrics && (
                <div className="mt-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">CPU:</span>
                    <span>{metrics.cpuPercent.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Memory:</span>
                    <span>{metrics.memoryPercent.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Queue:</span>
                    <span>{metrics.taskQueueLength} tasks</span>
                  </div>
                </div>
              )}
            </div>

            {/* Performance Chart */}
            <div className="bg-black/40 backdrop-blur-xl rounded-xl border border-blue-600/30 p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Zap className="w-4 h-4 mr-2 text-yellow-400" />
                Performance Trends
              </h3>
              
              <div className="h-40">
                <Line 
                  data={performanceData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false }
                    },
                    scales: {
                      x: { 
                        display: false,
                        grid: { display: false }
                      },
                      y: { 
                        display: false,
                        grid: { display: false }
                      }
                    }
                  }}
                />
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-black/40 backdrop-blur-xl rounded-xl border border-blue-600/30 p-6">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              
              <div className="space-y-2">
                {[
                  { icon: <Shield className="w-4 h-4" />, label: 'Security Scan', cmd: 'scan example.com' },
                  { icon: <Brain className="w-4 h-4" />, label: 'Code Analysis', cmd: 'analyze code quality' },
                  { icon: <Search className="w-4 h-4" />, label: 'Intelligence', cmd: 'research target' }
                ].map((action, idx) => (
                  <button
                    key={idx}
                    onClick={() => setCommand(action.cmd)}
                    className="w-full flex items-center space-x-3 px-3 py-2 bg-gradient-to-r from-slate-700/50 to-slate-600/50 rounded-lg hover:from-blue-600/20 hover:to-purple-600/20 transition-all duration-200"
                  >
                    <div className="text-blue-400">{action.icon}</div>
                    <span className="text-sm">{action.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AMASControlCenter;