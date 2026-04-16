/**
 * Orchestrator Status Dashboard Component (Phase 6.1)
 * Displays orchestrator health, active tasks, agent utilization, and system metrics
 */

import { Box, Card, CardContent, Chip, CircularProgress, Grid, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { apiService } from '../../services/api';

interface OrchestratorStatus {
  orchestrator_status: string;
  active_agents: number;
  active_tasks: number;
  total_tasks: number;
  metrics: {
    tasks_processed: number;
    tasks_completed: number;
    tasks_failed: number;
    average_task_time: number;
    active_agents: number;
    active_tasks: number;
  };
  agent_health: Record<string, {
    name: string;
    status: string;
    circuit_breaker_state: string;
    can_execute: boolean;
  }>;
  timestamp: string;
}

export const OrchestratorStatus = () => {
  const [status, setStatus] = useState<OrchestratorStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        const data = await apiService.getOrchestratorStatus();
        setStatus(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch orchestrator status');
        console.error('Failed to fetch orchestrator status:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    // Poll every 5 seconds for real-time updates
    const interval = setInterval(fetchStatus, 5000);

    return () => clearInterval(interval);
  }, []);

  if (loading && !status) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Typography color="error">Error: {error}</Typography>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  const successRate = status.metrics.tasks_processed > 0
    ? (status.metrics.tasks_completed / status.metrics.tasks_processed) * 100
    : 0;

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Orchestrator Status
      </Typography>

      <Grid container spacing={2} sx={{ mt: 1 }}>
        {/* Status Overview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Chip
                  label={status.orchestrator_status.toUpperCase()}
                  color={status.orchestrator_status === 'active' ? 'success' : 'warning'}
                  sx={{ mb: 2 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Last updated: {new Date(status.timestamp).toLocaleString()}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Agent Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agents
              </Typography>
              <Typography variant="h4" color="primary">
                {status.active_agents}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active agents
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Task Statistics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Tasks
              </Typography>
              <Typography variant="h4" color="primary">
                {status.active_tasks}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Currently executing
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Tasks
              </Typography>
              <Typography variant="h4" color="primary">
                {status.total_tasks}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All time
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Success Rate
              </Typography>
              <Typography variant="h4" color="success.main">
                {successRate.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {status.metrics.tasks_completed} / {status.metrics.tasks_processed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Metrics */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Tasks Processed
                  </Typography>
                  <Typography variant="h6">
                    {status.metrics.tasks_processed}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Tasks Completed
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    {status.metrics.tasks_completed}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Tasks Failed
                  </Typography>
                  <Typography variant="h6" color="error">
                    {status.metrics.tasks_failed}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Avg Task Time
                  </Typography>
                  <Typography variant="h6">
                    {status.metrics.average_task_time.toFixed(2)}s
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Agent Health */}
        {Object.keys(status.agent_health).length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Agent Health
                </Typography>
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  {Object.entries(status.agent_health).map(([agentId, health]) => (
                    <Grid item xs={12} sm={6} md={4} key={agentId}>
                      <Box
                        sx={{
                          p: 2,
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 1,
                        }}
                      >
                        <Typography variant="subtitle2">{health.name}</Typography>
                        <Chip
                          label={health.status}
                          size="small"
                          color={health.status === 'idle' ? 'success' : 'default'}
                          sx={{ mt: 1, mr: 1 }}
                        />
                        <Chip
                          label={health.can_execute ? 'Ready' : 'Blocked'}
                          size="small"
                          color={health.can_execute ? 'success' : 'error'}
                          sx={{ mt: 1 }}
                        />
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

