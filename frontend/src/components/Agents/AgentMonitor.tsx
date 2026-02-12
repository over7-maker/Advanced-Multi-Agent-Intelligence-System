/**
 * Agent Execution Monitoring Component (Phase 6.4)
 * Real-time agent status, current tasks per agent, and performance metrics
 */

import {
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { apiService, Agent } from '../../services/api';
import { websocketService } from '../../services/websocket';

interface AgentStatus {
  agent_id: string;
  name: string;
  status: 'idle' | 'busy' | 'error' | 'offline';
  current_task?: string;
  executions_today: number;
  success_rate: number;
  avg_response_time: number;
  utilization: number;
}

export const AgentMonitor = () => {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const response = await apiService.listAgents();
        const agentList = response.agents || [];
        
        // Transform to AgentStatus format
        const agentStatuses: AgentStatus[] = agentList.map((agent: Agent) => ({
          agent_id: agent.agent_id || agent.id,
          name: agent.name,
          status: agent.status === 'active' ? 'idle' : (agent.status as any),
          executions_today: agent.total_executions || 0,
          success_rate: agent.performance_metrics?.success_rate || 0.95,
          avg_response_time: agent.performance_metrics?.avg_duration || 2.5,
          utilization: 0, // Calculate from current tasks
        }));
        
        setAgents(agentStatuses);
      } catch (err) {
        console.error('Failed to fetch agents:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();

    // Subscribe to agent updates via WebSocket
    const handleAgentUpdate = (data: any) => {
      if (data.event === 'agent_update' || data.event === 'agent_started' || data.event === 'agent_completed') {
        setAgents((prev) => {
          const updated = [...prev];
          const agentIndex = updated.findIndex((a) => a.agent_id === data.data?.agent_id);
          
          if (agentIndex >= 0) {
            updated[agentIndex] = {
              ...updated[agentIndex],
              status: data.data?.status || updated[agentIndex].status,
              current_task: data.data?.current_task || updated[agentIndex].current_task,
            };
          }
          
          return updated;
        });
      }
    };

    const unsubscribeAgentUpdate = websocketService.on('agent_update', handleAgentUpdate);
    const unsubscribeAgentStarted = websocketService.on('agent_started', handleAgentUpdate);
    const unsubscribeAgentCompleted = websocketService.on('agent_completed', handleAgentUpdate);

    // Poll for updates every 5 seconds
    const interval = setInterval(fetchAgents, 5000);

    return () => {
      if (unsubscribeAgentUpdate) unsubscribeAgentUpdate();
      if (unsubscribeAgentStarted) unsubscribeAgentStarted();
      if (unsubscribeAgentCompleted) unsubscribeAgentCompleted();
      clearInterval(interval);
    };
  }, []);

  if (loading && agents.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'success';
      case 'busy':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const busyAgents = agents.filter((a) => a.status === 'busy').length;
  const idleAgents = agents.filter((a) => a.status === 'idle').length;

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Agent Execution Monitoring
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mt: 1, mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Total Agents
              </Typography>
              <Typography variant="h4">{agents.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Active Agents
              </Typography>
              <Typography variant="h4" color="warning.main">
                {busyAgents}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Idle Agents
              </Typography>
              <Typography variant="h4" color="success.main">
                {idleAgents}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Agent Table */}
      <TableContainer component={Card}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Agent Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Current Task</TableCell>
              <TableCell>Executions Today</TableCell>
              <TableCell>Success Rate</TableCell>
              <TableCell>Avg Response Time</TableCell>
              <TableCell>Utilization</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {agents.map((agent) => (
              <TableRow key={agent.agent_id}>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {agent.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {agent.agent_id}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={agent.status.toUpperCase()}
                    color={getStatusColor(agent.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {agent.current_task ? (
                    <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                      {agent.current_task}
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      None
                    </Typography>
                  )}
                </TableCell>
                <TableCell>{agent.executions_today}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={agent.success_rate * 100}
                      sx={{ width: 60, height: 6, borderRadius: 3 }}
                      color={agent.success_rate >= 0.9 ? 'success' : 'warning'}
                    />
                    <Typography variant="body2">
                      {(agent.success_rate * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {agent.avg_response_time.toFixed(2)}s
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={agent.utilization}
                      sx={{ width: 60, height: 6, borderRadius: 3 }}
                    />
                    <Typography variant="body2">{agent.utilization}%</Typography>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

