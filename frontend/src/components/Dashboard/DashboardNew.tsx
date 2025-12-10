// frontend/src/components/Dashboard/DashboardNew.tsx
import {
  CheckCircle as CheckCircleIcon,
  Memory as MemoryIcon,
  Refresh as RefreshIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  LinearProgress,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  CategoryScale,
  Chart as ChartJS,
  Tooltip as ChartTooltip,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
} from 'chart.js';
import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { apiService } from '../../services/api';
import { websocketService } from '../../services/websocket';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
);

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface DashboardStats {
  totalTasks: number;
  activeTasks: number;
  completedTasks: number;
  failedTasks: number;
  queueDepth: number;
  avgDuration: number;
  successRate: number;
  totalCost: number;
  cpuUsage: number;
  memoryUsage: number;
  activeAgents: number;
}

interface MetricHistory {
  timestamp: string;
  value: number;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const DashboardNew: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalTasks: 0,
    activeTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    queueDepth: 0,
    avgDuration: 0,
    successRate: 0,
    totalCost: 0,
    cpuUsage: 0,
    memoryUsage: 0,
    activeAgents: 0,
  });

  const [cpuHistory, setCpuHistory] = useState<MetricHistory[]>([]);
  const [memoryHistory, setMemoryHistory] = useState<MetricHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // ========================================================================
  // DATA FETCHING
  // ========================================================================

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch metrics
      const [systemMetrics, taskAnalytics] = await Promise.all([
        apiService.getSystemMetrics(),
        apiService.getTaskAnalytics(),
      ]);

      // Update stats with safe defaults
      setStats({
        totalTasks: taskAnalytics.total_tasks || 0,
        activeTasks: systemMetrics.active_tasks || 0,
        completedTasks: taskAnalytics.completed_tasks || 0,
        failedTasks: taskAnalytics.failed_tasks || 0,
        queueDepth: systemMetrics.queue_depth || 0,
        avgDuration: taskAnalytics.avg_duration || 0,
        successRate: taskAnalytics.success_rate || 0,
        totalCost: taskAnalytics.total_cost || 0,
        cpuUsage: systemMetrics.cpu_usage_percent || 0,
        memoryUsage: systemMetrics.memory_usage_percent || 0,
        activeAgents: systemMetrics.active_agents || 0,
      });

      // Update metric history
      const now = new Date().toISOString();
      setCpuHistory((prev) => [...prev.slice(-29), { timestamp: now, value: systemMetrics.cpu_usage_percent }]);
      setMemoryHistory((prev) => [...prev.slice(-29), { timestamp: now, value: systemMetrics.memory_usage_percent }]);

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // ========================================================================
  // REAL-TIME UPDATES
  // ========================================================================

  useEffect(() => {
    // Initial fetch
    fetchDashboardData();

    // Set up polling
    const pollInterval = setInterval(fetchDashboardData, 15000); // Every 15 seconds

    // Set up WebSocket listeners
    const unsubscribeTaskUpdate = websocketService.on('task_update', (data) => {
      console.log('Task update received:', data);
      // Update relevant stats
      fetchDashboardData();
    });

    const unsubscribeSystemUpdate = websocketService.on('system_metrics', (data) => {
      console.log('System metrics update:', data);
      setStats((prev) => ({
        ...prev,
        cpuUsage: data.cpu_usage || prev.cpuUsage,
        memoryUsage: data.memory_usage || prev.memoryUsage,
      }));
    });

    // Cleanup
    return () => {
      clearInterval(pollInterval);
      unsubscribeTaskUpdate();
      unsubscribeSystemUpdate();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ========================================================================
  // CHART CONFIGURATION
  // ========================================================================

  const cpuChartData = {
    labels: cpuHistory.map((h) => new Date(h.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'CPU Usage %',
        data: cpuHistory.map((h) => h.value),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4,
      },
    ],
  };

  const memoryChartData = {
    labels: memoryHistory.map((h) => new Date(h.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Memory Usage %',
        data: memoryHistory.map((h) => h.value),
        borderColor: 'rgb(153, 102, 255)',
        backgroundColor: 'rgba(153, 102, 255, 0.2)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        min: 0,
        max: 100,
      },
    },
  };

  // ========================================================================
  // RENDER
  // ========================================================================

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Refresh">
            <span>
              <IconButton onClick={fetchDashboardData} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </span>
          </Tooltip>
        </Box>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3}>
        {/* Task Stats */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography color="text.secondary" variant="body2">
                  Total Tasks
                </Typography>
                <CheckCircleIcon color="primary" />
              </Box>
              <Typography variant="h4">{stats.totalTasks}</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Chip
                  label={`${(stats.successRate ?? 0).toFixed(1)}% success`}
                  size="small"
                  color="success"
                  sx={{ mr: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {stats.completedTasks} completed
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Active Tasks */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography color="text.secondary" variant="body2">
                  Active Tasks
                </Typography>
                <SpeedIcon color="warning" />
              </Box>
              <Typography variant="h4">{stats.activeTasks}</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Chip label={`${stats.queueDepth} queued`} size="small" color="info" sx={{ mr: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  in queue
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* CPU Usage */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography color="text.secondary" variant="body2">
                  CPU Usage
                </Typography>
                <MemoryIcon color="error" />
              </Box>
              <Typography variant="h4">{(stats.cpuUsage ?? 0).toFixed(1)}%</Typography>
              <LinearProgress
                variant="determinate"
                value={stats.cpuUsage}
                sx={{ mt: 1, height: 8, borderRadius: 4 }}
                color={stats.cpuUsage > 80 ? 'error' : stats.cpuUsage > 60 ? 'warning' : 'success'}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Memory Usage */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography color="text.secondary" variant="body2">
                  Memory Usage
                </Typography>
                <StorageIcon color="secondary" />
              </Box>
              <Typography variant="h4">{(stats.memoryUsage ?? 0).toFixed(1)}%</Typography>
              <LinearProgress
                variant="determinate"
                value={stats.memoryUsage}
                sx={{ mt: 1, height: 8, borderRadius: 4 }}
                color={stats.memoryUsage > 85 ? 'error' : stats.memoryUsage > 70 ? 'warning' : 'success'}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* CPU Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                CPU Usage History
              </Typography>
              <Box sx={{ height: 300 }}>
                {cpuHistory.length > 0 ? (
                  <Line data={cpuChartData} options={chartOptions} />
                ) : (
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                    <Typography variant="body2" color="text.secondary">
                      No data yet
                    </Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Memory Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Memory Usage History
              </Typography>
              <Box sx={{ height: 300 }}>
                {memoryHistory.length > 0 ? (
                  <Line data={memoryChartData} options={chartOptions} />
                ) : (
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                    <Typography variant="body2" color="text.secondary">
                      No data yet
                    </Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Avg Duration
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {(stats.avgDuration ?? 0).toFixed(1)}s
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Success Rate
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    {(stats.successRate ?? 0).toFixed(1)}%
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Failed Tasks
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" color="error.main">
                    {stats.failedTasks}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Cost Metrics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cost Analysis
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Total Cost
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${(stats.totalCost ?? 0).toFixed(2)}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Avg Cost/Task
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${(stats.totalTasks ?? 0) > 0 ? ((stats.totalCost ?? 0) / (stats.totalTasks ?? 1)).toFixed(4) : '0.00'}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {stats.totalCost > 100 ? (
                    <TrendingUpIcon color="error" fontSize="small" sx={{ mr: 1 }} />
                  ) : (
                    <TrendingDownIcon color="success" fontSize="small" sx={{ mr: 1 }} />
                  )}
                  <Typography variant="body2" color="text.secondary">
                    {stats.totalCost > 100 ? 'High usage' : 'Normal usage'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Agent Status */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Status
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Active Agents
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {stats.activeAgents}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Utilization
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {stats.activeTasks > 0 && stats.activeAgents > 0 ? ((stats.activeTasks / stats.activeAgents) * 100).toFixed(0) : '0'}%
                  </Typography>
                </Box>
                <Chip
                  label={stats.activeAgents > 0 ? 'All systems operational' : 'No agents active'}
                  color={stats.activeAgents > 0 ? 'success' : 'error'}
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardNew;

