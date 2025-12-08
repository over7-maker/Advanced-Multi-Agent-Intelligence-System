// frontend/src/components/System/SystemHealth.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  LinearProgress,
  CircularProgress,
} from '@mui/material';
import {
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { apiService, SystemMetrics } from '../../services/api';
import { websocketService } from '../../services/websocket';

export const SystemHealth: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await apiService.getSystemMetrics();
        setMetrics(data);
      } catch (error) {
        console.error('Failed to fetch system metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();

    // Poll for updates every 5 seconds
    const interval = setInterval(fetchMetrics, 5000);

    // Subscribe to real-time updates
    const unsubscribe = websocketService.on('system_metrics', (data) => {
      setMetrics((prev) => (prev ? { ...prev, ...data } : null));
    });

    return () => {
      clearInterval(interval);
      unsubscribe();
    };
  }, []);

  if (loading || !metrics) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        System Health
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <SpeedIcon color="primary" />
                <Typography variant="h6">CPU Usage</Typography>
              </Box>
              <Typography variant="h3" gutterBottom>
                {metrics.cpu_usage_percent.toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics.cpu_usage_percent}
                color={metrics.cpu_usage_percent > 80 ? 'error' : metrics.cpu_usage_percent > 60 ? 'warning' : 'success'}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <MemoryIcon color="secondary" />
                <Typography variant="h6">Memory Usage</Typography>
              </Box>
              <Typography variant="h3" gutterBottom>
                {metrics.memory_usage_percent.toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics.memory_usage_percent}
                color={metrics.memory_usage_percent > 85 ? 'error' : metrics.memory_usage_percent > 70 ? 'warning' : 'success'}
                sx={{ height: 10, borderRadius: 5 }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {(metrics.memory_usage_bytes / 1024 / 1024 / 1024).toFixed(2)} GB used
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <StorageIcon color="info" />
                <Typography variant="h6">Disk Usage</Typography>
              </Box>
              <Typography variant="h3" gutterBottom>
                {(metrics.disk_usage_bytes / 1024 / 1024 / 1024).toFixed(2)} GB
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Disk space used
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <CheckCircleIcon color="success" />
                <Typography variant="h6">Task Statistics</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Active Tasks
                  </Typography>
                  <Typography variant="h5">{metrics.active_tasks}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Queue Depth
                  </Typography>
                  <Typography variant="h5">{metrics.queue_depth}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Tasks
                  </Typography>
                  <Typography variant="h5">{metrics.total_tasks}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Completed Tasks
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {metrics.completed_tasks}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Failed Tasks
                  </Typography>
                  <Typography variant="h5" color="error.main">
                    {metrics.failed_tasks}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Active Agents
                  </Typography>
                  <Typography variant="h5">{metrics.active_agents}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last updated: {new Date(metrics.timestamp).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

