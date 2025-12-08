// frontend/src/components/Agents/AgentList.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  LinearProgress,
  CircularProgress,
} from '@mui/material';
import {
  Build as BuildIcon,
} from '@mui/icons-material';
import { apiService, Agent } from '../../services/api';
import { websocketService } from '../../services/websocket';

export const AgentList: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const response = await apiService.listAgents();
        setAgents(response.agents || []);
      } catch (error) {
        console.error('Failed to fetch agents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();

    // Subscribe to real-time updates
    const unsubscribe = websocketService.on('agent_status_changed', (data) => {
      setAgents((prev) =>
        prev.map((agent) =>
          agent.agent_id === data.agent_id ? { ...agent, ...data } : agent
        )
      );
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'error':
        return 'error';
      case 'maintenance':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Agents
      </Typography>
      <Grid container spacing={3}>
        {(agents || []).map((agent) => (
          <Grid item xs={12} sm={6} md={4} key={agent.agent_id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <BuildIcon />
                    <Typography variant="h6">{agent.name}</Typography>
                  </Box>
                  <Chip
                    label={agent.status}
                    color={getStatusColor(agent.status) as any}
                    size="small"
                  />
                </Box>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {agent.type}
                </Typography>

                {agent.performance_metrics && (
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Success Rate</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {(agent.performance_metrics.success_rate * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={agent.performance_metrics.success_rate * 100}
                      sx={{ mb: 2 }}
                    />

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Avg Duration</Typography>
                      <Typography variant="body2">
                        {agent.performance_metrics.avg_duration.toFixed(2)}s
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Total Executions</Typography>
                      <Typography variant="body2">
                        {agent.total_executions}
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Total Cost</Typography>
                      <Typography variant="body2">
                        ${agent.total_cost_usd.toFixed(4)}
                      </Typography>
                    </Box>
                  </Box>
                )}

                {agent.capabilities && agent.capabilities.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Capabilities:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {agent.capabilities.slice(0, 3).map((cap, idx) => (
                        <Chip key={idx} label={cap} size="small" variant="outlined" />
                      ))}
                      {agent.capabilities.length > 3 && (
                        <Chip
                          label={`+${agent.capabilities.length - 3}`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

