/**
 * AMAS Dashboard Component
 * 
 * Main dashboard providing real-time overview of the intelligence system
 * including agent status, task metrics, system health, and recent activities
 */

import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  SmartToy,
  Assignment,
  Speed,
  Security,
  TrendingUp,
  Warning,
  CheckCircle,
  Error,
  Info,
  Refresh,
  PlayArrow,
  Pause,
  Stop
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Services
import { AMASApiService } from '../services/api';

// Types
interface DashboardMetrics {
  agents: {
    total: number;
    active: number;
    idle: number;
    error: number;
  };
  tasks: {
    total: number;
    active: number;
    completed: number;
    failed: number;
  };
  system: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    uptime: string;
  };
  performance: {
    avg_task_time: number;
    tasks_per_hour: number;
    success_rate: number;
  };
}

interface ActivityItem {
  id: string;
  type: 'task' | 'agent' | 'system';
  message: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const apiService = new AMASApiService();

  useEffect(() => {
    loadDashboardData();
    
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load metrics and activities
      const [metricsData, activitiesData] = await Promise.all([
        apiService.getDashboardMetrics(),
        apiService.getRecentActivities()
      ]);
      
      setMetrics(metricsData);
      setActivities(activitiesData);
      setError(null);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadDashboardData();
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  if (loading && !metrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error && !metrics) {
    return (
      <Alert severity="error" action={
        <IconButton color="inherit" size="small" onClick={handleRefresh}>
          <Refresh />
        </IconButton>
      }>
        {error}
      </Alert>
    );
  }

  const agentStatusData = metrics ? [
    { name: 'Active', value: metrics.agents.active, color: '#4caf50' },
    { name: 'Idle', value: metrics.agents.idle, color: '#ff9800' },
    { name: 'Error', value: metrics.agents.error, color: '#f44336' }
  ] : [];

  const taskStatusData = metrics ? [
    { name: 'Completed', value: metrics.tasks.completed, color: '#4caf50' },
    { name: 'Active', value: metrics.tasks.active, color: '#00bcd4' },
    { name: 'Failed', value: metrics.tasks.failed, color: '#f44336' }
  ] : [];

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" color="primary">
          Intelligence Dashboard
        </Typography>
        
        <Box display="flex" gap={1}>
          <IconButton 
            onClick={toggleAutoRefresh} 
            color={autoRefresh ? "primary" : "default"}
            title={autoRefresh ? "Disable auto-refresh" : "Enable auto-refresh"}
          >
            {autoRefresh ? <Pause /> : <PlayArrow />}
          </IconButton>
          <IconButton onClick={handleRefresh} title="Refresh now">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Key Metrics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Agents
                  </Typography>
                  <Typography variant="h4">
                    {metrics?.agents.active || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    of {metrics?.agents.total || 0} total
                  </Typography>
                </Box>
                <SmartToy color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Tasks
                  </Typography>
                  <Typography variant="h4">
                    {metrics?.tasks.active || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {metrics?.tasks.total || 0} total processed
                  </Typography>
                </Box>
                <Assignment color="secondary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Success Rate
                  </Typography>
                  <Typography variant="h4">
                    {metrics?.performance.success_rate || 0}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Last 24 hours
                  </Typography>
                </Box>
                <TrendingUp color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Task Time
                  </Typography>
                  <Typography variant="h4">
                    {metrics?.performance.avg_task_time || 0}s
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Processing time
                  </Typography>
                </Box>
                <Speed color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Health */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Health
              </Typography>
              
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">CPU Usage</Typography>
                  <Typography variant="body2">{metrics?.system.cpu_usage || 0}%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={metrics?.system.cpu_usage || 0} 
                  color={metrics?.system.cpu_usage && metrics.system.cpu_usage > 80 ? "error" : "primary"}
                />
              </Box>

              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">Memory Usage</Typography>
                  <Typography variant="body2">{metrics?.system.memory_usage || 0}%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={metrics?.system.memory_usage || 0}
                  color={metrics?.system.memory_usage && metrics.system.memory_usage > 85 ? "warning" : "primary"}
                />
              </Box>

              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">Disk Usage</Typography>
                  <Typography variant="body2">{metrics?.system.disk_usage || 0}%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={metrics?.system.disk_usage || 0}
                  color={metrics?.system.disk_usage && metrics.system.disk_usage > 90 ? "error" : "primary"}
                />
              </Box>

              <Typography variant="body2" color="textSecondary">
                Uptime: {metrics?.system.uptime || 'Unknown'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Agent Status Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Status Distribution
              </Typography>
              
              <Box height={200}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={agentStatusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {agentStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
              
              <Box display="flex" justifyContent="center" gap={2} mt={1}>
                {agentStatusData.map((entry) => (
                  <Chip
                    key={entry.name}
                    label={`${entry.name}: ${entry.value}`}
                    size="small"
                    sx={{ backgroundColor: entry.color, color: 'white' }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activities */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activities
              </Typography>
              
              <List>
                {activities.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem>
                      <ListItemIcon>
                        {activity.status === 'success' && <CheckCircle color="success" />}
                        {activity.status === 'warning' && <Warning color="warning" />}
                        {activity.status === 'error' && <Error color="error" />}
                        {activity.status === 'info' && <Info color="info" />}
                      </ListItemIcon>
                      <ListItemText
                        primary={activity.message}
                        secondary={`${activity.type.toUpperCase()} • ${new Date(activity.timestamp).toLocaleString()}`}
                      />
                    </ListItem>
                    {index < activities.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
                
                {activities.length === 0 && (
                  <ListItem>
                    <ListItemText
                      primary="No recent activities"
                      secondary="System activities will appear here"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;