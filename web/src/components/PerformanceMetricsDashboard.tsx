import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  MemoryStick, 
  Network,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react';
import { Line, Bar, Doughnut, Area } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { apiService } from '../services/api';
import { wsService } from '../services/websocket';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface PerformanceMetricsDashboardProps {
  refreshInterval?: number;
}

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_connections: number;
  timestamp: number;
}

interface HistoricalData {
  timestamp: number;
  cpu: number;
  memory: number;
  disk: number;
  connections: number;
}

const PerformanceMetricsDashboard: React.FC<PerformanceMetricsDashboardProps> = ({ 
  refreshInterval = 5000 
}) => {
  const [currentMetrics, setCurrentMetrics] = useState<SystemMetrics | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('1h');

  useEffect(() => {
    loadMetrics();
    setupWebSocketListeners();
    
    const interval = setInterval(loadMetrics, refreshInterval);
    
    return () => {
      clearInterval(interval);
      wsService.unsubscribe('metricsUpdate', handleMetricsUpdate);
    };
  }, [refreshInterval]);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const metrics = await apiService.getMetrics();
      setCurrentMetrics(metrics);
      setError(null);
      
      // Add to historical data
      setHistoricalData(prev => {
        const newData = {
          timestamp: metrics.timestamp,
          cpu: metrics.cpu_usage,
          memory: metrics.memory_usage,
          disk: metrics.disk_usage,
          connections: metrics.active_connections,
        };
        
        const updated = [...prev, newData];
        
        // Keep only data within time range
        const cutoff = Date.now() - getTimeRangeMs(timeRange);
        return updated.filter(data => data.timestamp > cutoff);
      });
    } catch (err) {
      setError('Failed to load metrics');
      console.error('Error loading metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocketListeners = () => {
    wsService.subscribe('metricsUpdate', handleMetricsUpdate);
  };

  const handleMetricsUpdate = (update: any) => {
    setCurrentMetrics(prev => ({
      ...prev,
      ...update,
      timestamp: Date.now()
    }));
  };

  const getTimeRangeMs = (range: string): number => {
    switch (range) {
      case '1h': return 60 * 60 * 1000;
      case '6h': return 6 * 60 * 60 * 1000;
      case '24h': return 24 * 60 * 60 * 1000;
      case '7d': return 7 * 24 * 60 * 60 * 1000;
      default: return 60 * 60 * 1000;
    }
  };

  const getHealthStatus = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return { status: 'critical', color: 'text-red-500', icon: AlertTriangle };
    if (value >= thresholds.warning) return { status: 'warning', color: 'text-yellow-500', icon: AlertTriangle };
    return { status: 'healthy', color: 'text-green-500', icon: CheckCircle };
  };

  const formatBytes = (bytes: number): string => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Chart data
  const cpuChartData = {
    labels: historicalData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [{
      label: 'CPU Usage (%)',
      data: historicalData.map(d => d.cpu),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true,
      tension: 0.4
    }]
  };

  const memoryChartData = {
    labels: historicalData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [{
      label: 'Memory Usage (%)',
      data: historicalData.map(d => d.memory),
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      fill: true,
      tension: 0.4
    }]
  };

  const diskChartData = {
    labels: historicalData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [{
      label: 'Disk Usage (%)',
      data: historicalData.map(d => d.disk),
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245, 158, 11, 0.1)',
      fill: true,
      tension: 0.4
    }]
  };

  const connectionsChartData = {
    labels: historicalData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [{
      label: 'Active Connections',
      data: historicalData.map(d => d.connections),
      borderColor: '#8b5cf6',
      backgroundColor: 'rgba(139, 92, 246, 0.1)',
      fill: true,
      tension: 0.4
    }]
  };

  const systemHealthData = {
    labels: ['CPU', 'Memory', 'Disk', 'Connections'],
    datasets: [{
      data: currentMetrics ? [
        currentMetrics.cpu_usage,
        currentMetrics.memory_usage,
        currentMetrics.disk_usage,
        Math.min(currentMetrics.active_connections * 10, 100) // Scale connections to 0-100
      ] : [0, 0, 0, 0],
      backgroundColor: [
        '#3b82f6',
        '#10b981',
        '#f59e0b',
        '#8b5cf6'
      ],
      borderWidth: 0
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      x: {
        display: false,
        grid: { display: false }
      },
      y: {
        display: false,
        grid: { display: false },
        min: 0,
        max: 100
      }
    },
    elements: {
      point: {
        radius: 0
      }
    }
  };

  if (loading && !currentMetrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Activity className="w-6 h-6 animate-spin text-blue-500" />
          <span className="text-gray-300">Loading metrics...</span>
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
            onClick={loadMetrics}
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
          <h2 className="text-2xl font-bold text-white">Performance Metrics</h2>
          <p className="text-gray-400">Real-time system performance monitoring</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="px-3 py-1 bg-slate-700 text-gray-300 rounded-lg border border-gray-600"
          >
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
          <div className="text-sm text-gray-400">
            Updated {currentMetrics ? new Date(currentMetrics.timestamp).toLocaleTimeString() : 'Never'}
          </div>
        </div>
      </div>

      {/* Current Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* CPU Usage */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-blue-600/30"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Cpu className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h3 className="font-semibold text-white">CPU Usage</h3>
                <p className="text-sm text-gray-400">Processor utilization</p>
              </div>
            </div>
            {currentMetrics && (() => {
              const health = getHealthStatus(currentMetrics.cpu_usage, { warning: 70, critical: 90 });
              const Icon = health.icon;
              return <Icon className={`w-5 h-5 ${health.color}`} />;
            })()}
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {currentMetrics?.cpu_usage.toFixed(1) || 0}%
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${currentMetrics?.cpu_usage || 0}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </motion.div>

        {/* Memory Usage */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-green-600/30"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <MemoryStick className="w-5 h-5 text-green-400" />
              </div>
              <div>
                <h3 className="font-semibold text-white">Memory Usage</h3>
                <p className="text-sm text-gray-400">RAM utilization</p>
              </div>
            </div>
            {currentMetrics && (() => {
              const health = getHealthStatus(currentMetrics.memory_usage, { warning: 80, critical: 95 });
              const Icon = health.icon;
              return <Icon className={`w-5 h-5 ${health.color}`} />;
            })()}
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {currentMetrics?.memory_usage.toFixed(1) || 0}%
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-green-500 to-green-400 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${currentMetrics?.memory_usage || 0}%` }}
              transition={{ duration: 0.5, delay: 0.1 }}
            />
          </div>
        </motion.div>

        {/* Disk Usage */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-yellow-600/30"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-yellow-500/20 rounded-lg">
                <HardDrive className="w-5 h-5 text-yellow-400" />
              </div>
              <div>
                <h3 className="font-semibold text-white">Disk Usage</h3>
                <p className="text-sm text-gray-400">Storage utilization</p>
              </div>
            </div>
            {currentMetrics && (() => {
              const health = getHealthStatus(currentMetrics.disk_usage, { warning: 85, critical: 95 });
              const Icon = health.icon;
              return <Icon className={`w-5 h-5 ${health.color}`} />;
            })()}
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {currentMetrics?.disk_usage.toFixed(1) || 0}%
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-yellow-500 to-yellow-400 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${currentMetrics?.disk_usage || 0}%` }}
              transition={{ duration: 0.5, delay: 0.2 }}
            />
          </div>
        </motion.div>

        {/* Active Connections */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-600/30"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Network className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <h3 className="font-semibold text-white">Connections</h3>
                <p className="text-sm text-gray-400">Active connections</p>
              </div>
            </div>
            <CheckCircle className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {currentMetrics?.active_connections || 0}
          </div>
          <div className="text-sm text-gray-400">
            Active sessions
          </div>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CPU Chart */}
        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-blue-600/30">
          <h3 className="text-lg font-semibold text-white mb-4">CPU Usage Over Time</h3>
          <div className="h-64">
            <Line data={cpuChartData} options={chartOptions} />
          </div>
        </div>

        {/* Memory Chart */}
        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-green-600/30">
          <h3 className="text-lg font-semibold text-white mb-4">Memory Usage Over Time</h3>
          <div className="h-64">
            <Line data={memoryChartData} options={chartOptions} />
          </div>
        </div>

        {/* Disk Chart */}
        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-yellow-600/30">
          <h3 className="text-lg font-semibold text-white mb-4">Disk Usage Over Time</h3>
          <div className="h-64">
            <Line data={diskChartData} options={chartOptions} />
          </div>
        </div>

        {/* System Health Overview */}
        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-600/30">
          <h3 className="text-lg font-semibold text-white mb-4">System Health Overview</h3>
          <div className="h-64 flex items-center justify-center">
            <Doughnut 
              data={systemHealthData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                      color: '#ffffff',
                      font: { size: 12 }
                    }
                  }
                }
              }} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetricsDashboard;