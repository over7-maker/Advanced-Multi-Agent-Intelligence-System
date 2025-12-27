import { useState, useEffect } from 'react';
import { Activity, Cpu, HardDrive, TrendingUp, CheckCircle, AlertCircle } from 'lucide-react';
import { fetchSystemMetrics, fetchAgentStatus, type SystemMetrics, type Agent } from '@/lib/api';

export default function MonitoringDashboard() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const loadData = async () => {
    try {
      setError(null);
      const [metricsData, agentsData] = await Promise.all([
        fetchSystemMetrics(),
        fetchAgentStatus()
      ]);
      setMetrics(metricsData);
      setAgents(agentsData);
      setRetryCount(0); // Reset retry count on success
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load dashboard data';
      console.error('Failed to load dashboard data:', err);
      setError(errorMessage);
      
      // Use fallback data if available (from mock)
      // The API already falls back to mock data, so we just show error message
      if (retryCount < 3) {
        setRetryCount(prev => prev + 1);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading && !metrics) {
    return (
      <section id="monitoring" className="py-20 px-6">
        <div className="container-custom text-center">
          <div className="animate-pulse text-gray-600 dark:text-gray-400">
            Loading dashboard...
          </div>
        </div>
      </section>
    );
  }

  if (error && !metrics) {
    return (
      <section id="monitoring" className="py-20 px-6">
        <div className="container-custom text-center">
          <div className="card max-w-md mx-auto">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold mb-2">Failed to Load Dashboard</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
            <button
              onClick={loadData}
              className="btn-primary"
              disabled={retryCount >= 3}
            >
              {retryCount >= 3 ? 'Max retries reached' : 'Retry'}
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section id="monitoring" className="py-20 px-6">
      <div className="container-custom">
        <div className="section-header text-center">
          <h2 className="section-title">Real-time Monitoring</h2>
          <p className="section-subtitle mx-auto">
            Live metrics and performance data from your agent systems
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card animate-fadeInUp">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
                <Cpu className="w-5 h-5 text-primary-500" />
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">CPU</span>
            </div>
            <div className="text-3xl font-bold mb-1">{metrics.cpu}%</div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-500"
                style={{ width: `${metrics.cpu}%` }}
              />
            </div>
          </div>

          <div className="card animate-fadeInUp" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-lg bg-accent-500/10 flex items-center justify-center">
                <HardDrive className="w-5 h-5 text-accent-500" />
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Memory</span>
            </div>
            <div className="text-3xl font-bold mb-1">{metrics.memory}%</div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-accent-500 to-accent-600 transition-all duration-500"
                style={{ width: `${metrics.memory}%` }}
              />
            </div>
          </div>

          <div className="card animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
                <Activity className="w-5 h-5 text-primary-500" />
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Agents</span>
            </div>
            <div className="text-3xl font-bold">{metrics.activeAgents}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Active</div>
          </div>

          <div className="card animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-lg bg-accent-500/10 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-accent-500" />
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Tasks</span>
            </div>
            <div className="text-3xl font-bold">{metrics.tasksCompleted.toLocaleString()}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Completed</div>
          </div>
        </div>

        {/* System Health */}
        <div className="card mb-8 animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold">System Health</h3>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm text-gray-600 dark:text-gray-400">All systems operational</span>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Uptime</div>
              <div className="text-2xl font-bold text-green-500">{metrics.uptime}%</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Avg Latency</div>
              <div className="text-2xl font-bold text-primary-500">{metrics.latency}ms</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Status</div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-lg font-semibold text-green-500">Healthy</span>
              </div>
            </div>
          </div>
        </div>

        {/* Agent List */}
        <div className="card animate-fadeInUp" style={{ animationDelay: '0.5s' }}>
          <h3 className="text-xl font-bold mb-6">Active Agents</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.slice(0, 6).map((agent) => (
              <div key={agent.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                <div className="flex items-center gap-3">
                  {agent.status === 'healthy' ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-yellow-500" />
                  )}
                  <div>
                    <div className="font-medium text-sm">{agent.name}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      {agent.tasksCompleted} tasks
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  {agent.uptime.toFixed(2)}%
                </div>
              </div>
            ))}
          </div>
          {agents.length > 6 && (
            <div className="mt-4 text-center">
              <button className="btn-outline">
                View All {agents.length} Agents
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}