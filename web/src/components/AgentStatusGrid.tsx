import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Brain,
  Shield,
  Search,
  FileText,
  TestTube,
  Network,
  Settings,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';
import { apiService, Agent } from '../services/api';
import { wsService } from '../services/websocket';
import { toast } from 'react-hot-toast';

interface AgentStatusGridProps {
  onAgentSelect?: (agent: Agent) => void;
  selectedAgentId?: string;
}

const AgentStatusGrid: React.FC<AgentStatusGridProps> = ({ 
  onAgentSelect, 
  selectedAgentId 
}) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [agentMetrics, setAgentMetrics] = useState<Record<string, any>>({});

  const setupWebSocketListeners = useCallback(() => {
    wsService.subscribe('agentUpdate', handleAgentUpdate);
  }, []);

  useEffect(() => {
    loadAgents();
    setupWebSocketListeners();
    const interval = setInterval(loadAgents, 30000);
    return () => {
      clearInterval(interval);
      wsService.unsubscribe('agentUpdate', handleAgentUpdate);
    };
  }, [setupWebSocketListeners]);

  const loadAgents = async () => {
    try {
      setLoading(true);
      const agentsData = await apiService.getAgents();
      setAgents(agentsData);
      setError(null);
      
      // Load metrics for each agent
      for (const agent of agentsData) {
        try {
          const metrics = await apiService.getAgentStatus(agent.id);
          setAgentMetrics(prev => ({
            ...prev,
            [agent.id]: metrics
          }));
        } catch (err) {
          console.warn(`Failed to load metrics for agent ${agent.id}:`, err);
        }
      }
    } catch (err) {
      setError('Failed to load agents');
      console.error('Error loading agents:', err);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocketListeners = () => {
    wsService.subscribe('agentUpdate', handleAgentUpdate);
  };

  const handleAgentUpdate = (update: any) => {
    setAgentMetrics(prev => ({
      ...prev,
      [update.agent_id]: {
        ...prev[update.agent_id],
        ...update
      }
    }));
  };

  const handleAgentAction = async (agentId: string, action: 'start' | 'stop' | 'restart') => {
    try {
      switch (action) {
        case 'start':
          await apiService.startAgent(agentId);
          toast.success('Agent started successfully');
          break;
        case 'stop':
          await apiService.stopAgent(agentId);
          toast.success('Agent stopped successfully');
          break;
        case 'restart':
          await apiService.stopAgent(agentId);
          await new Promise(resolve => setTimeout(resolve, 1000));
          await apiService.startAgent(agentId);
          toast.success('Agent restarted successfully');
          break;
      }
      loadAgents(); // Refresh the list
    } catch (err) {
      toast.error(`Failed to ${action} agent`);
      console.error(`Error ${action}ing agent:`, err);
    }
  };

  const getAgentIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'security':
        return <Shield className="w-5 h-5" />;
      case 'analysis':
      case 'code_analysis':
        return <Brain className="w-5 h-5" />;
      case 'research':
      case 'intelligence':
        return <Search className="w-5 h-5" />;
      case 'monitoring':
      case 'performance':
        return <Activity className="w-5 h-5" />;
      case 'documentation':
        return <FileText className="w-5 h-5" />;
      case 'testing':
        return <TestTube className="w-5 h-5" />;
      case 'integration':
        return <Network className="w-5 h-5" />;
      default:
        return <Settings className="w-5 h-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-500 bg-green-500/20';
      case 'busy':
        return 'text-yellow-500 bg-yellow-500/20';
      case 'idle':
        return 'text-blue-500 bg-blue-500/20';
      case 'error':
        return 'text-red-500 bg-red-500/20';
      default:
        return 'text-gray-500 bg-gray-500/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4" />;
      case 'busy':
        return <Clock className="w-4 h-4" />;
      case 'idle':
        return <Activity className="w-4 h-4" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Activity className="w-6 h-6 animate-spin text-blue-500" />
          <span className="text-gray-300">Loading agents...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={loadAgents}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">AI Agent Orchestra</h2>
          <p className="text-gray-400">Monitor and manage your AI agents</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="text-sm text-gray-400">
            {agents.filter(a => a.status === 'active').length} of {agents.length} active
          </div>
          <button
            onClick={loadAgents}
            className="p-2 bg-slate-700 text-gray-300 rounded-lg hover:bg-slate-600 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <AnimatePresence>
          {agents.map((agent) => {
            const metrics = agentMetrics[agent.id] || {};
            const isSelected = selectedAgentId === agent.id;
            
            return (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border transition-all duration-200 cursor-pointer ${
                  isSelected 
                    ? 'border-blue-500 shadow-lg shadow-blue-500/20' 
                    : 'border-gray-700/50 hover:border-blue-500/50'
                }`}
                onClick={() => onAgentSelect?.(agent)}
              >
                {/* Selection Indicator */}
                {isSelected && (
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-3 h-3 text-white" />
                  </div>
                )}

                {/* Agent Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${getStatusColor(agent.status)}`}>
                      {getAgentIcon(agent.type)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-white text-sm">{agent.name}</h3>
                      <p className="text-xs text-gray-400 capitalize">{agent.type}</p>
                    </div>
                  </div>
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${getStatusColor(agent.status)}`}>
                    {getStatusIcon(agent.status)}
                    <span className="capitalize">{agent.status}</span>
                  </div>
                </div>

                {/* Agent Metrics */}
                <div className="space-y-3 mb-4">
                  {metrics.uptime && (
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-400">Uptime:</span>
                      <span className="text-white">{Math.floor(metrics.uptime / 3600)}h</span>
                    </div>
                  )}
                  
                  {metrics.tasks_completed !== undefined && (
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-400">Tasks:</span>
                      <span className="text-white">{metrics.tasks_completed}</span>
                    </div>
                  )}
                  
                  {metrics.performance_metrics && (
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-400">CPU:</span>
                        <span className="text-white">{metrics.performance_metrics.cpu_usage?.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-400">Memory:</span>
                        <span className="text-white">{metrics.performance_metrics.memory_usage}MB</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-400">Response:</span>
                        <span className="text-white">{metrics.performance_metrics.response_time?.toFixed(2)}s</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Capabilities */}
                <div className="mb-4">
                  <div className="text-xs text-gray-400 mb-2">Capabilities:</div>
                  <div className="flex flex-wrap gap-1">
                    {agent.capabilities.slice(0, 3).map((capability, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-slate-700 text-xs text-gray-300 rounded"
                      >
                        {capability}
                      </span>
                    ))}
                    {agent.capabilities.length > 3 && (
                      <span className="px-2 py-1 bg-slate-700 text-xs text-gray-300 rounded">
                        +{agent.capabilities.length - 3}
                      </span>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  {agent.status === 'active' ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAgentAction(agent.id, 'stop');
                      }}
                      className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors text-xs"
                    >
                      <Pause className="w-3 h-3" />
                      <span>Stop</span>
                    </button>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAgentAction(agent.id, 'start');
                      }}
                      className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-green-600/20 text-green-400 rounded-lg hover:bg-green-600/30 transition-colors text-xs"
                    >
                      <Play className="w-3 h-3" />
                      <span>Start</span>
                    </button>
                  )}
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAgentAction(agent.id, 'restart');
                    }}
                    className="flex items-center justify-center px-3 py-2 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors text-xs"
                  >
                    <RotateCcw className="w-3 h-3" />
                  </button>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Empty State */}
      {agents.length === 0 && (
        <div className="text-center py-12">
          <Brain className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-400 mb-2">No Agents Found</h3>
          <p className="text-gray-500 mb-4">No agents are currently available or configured.</p>
          <button
            onClick={loadAgents}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      )}
    </div>
  );
};

export default AgentStatusGrid;