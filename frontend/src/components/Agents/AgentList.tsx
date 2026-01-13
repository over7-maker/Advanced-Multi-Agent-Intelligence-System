// frontend/src/components/Agents/AgentList.tsx
import {
  Build as BuildIcon,
  PlayArrow as PlayArrowIcon,
  Settings as SettingsIcon,
  SmartToy as SmartToyIcon,
  Stop as StopIcon,
} from '@mui/icons-material';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  LinearProgress,
  Tab,
  Tabs,
  Typography,
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import { Agent, apiService } from '../../services/api';
import { websocketService } from '../../services/websocket';
import { AIProvidersPanel } from './AIProvidersPanel';
import { AgentToolConfiguration } from './AgentToolConfiguration';
import { ToolStatusIndicator } from './ToolStatusIndicator';

export const AgentList: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [managingAgent, setManagingAgent] = useState<string | null>(null);
  const [configuringAgent, setConfiguringAgent] = useState<string | null>(null);

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

  if (!agents || agents.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Agents
        </Typography>
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No agents found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Agents will appear here once they are initialized by the orchestrator.
          </Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Agents
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab icon={<BuildIcon />} iconPosition="start" label={`Agents (${agents.length})`} />
          <Tab icon={<SmartToyIcon />} iconPosition="start" label="AI Providers" />
        </Tabs>
      </Box>

      {activeTab === 0 && (
        <>
          {!agents || agents.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No agents found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Agents will appear here once they are initialized by the orchestrator.
              </Typography>
            </Box>
          ) : (
            <Grid container spacing={3}>
              {(agents || []).map((agent) => (
                <>
                  {/* @ts-ignore Material-UI v7 Grid type issue - item prop not recognized */}
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
                              <Chip key={`${agent.agent_id}-cap-${idx}-${cap}`} label={cap} size="small" variant="outlined" />
                            ))}
                            {agent.capabilities.length > 3 && (
                              <Chip
                                key={`${agent.agent_id}-cap-more`}
                                label={`+${agent.capabilities.length - 3}`}
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </Box>
                        </Box>
                      )}

                      {/* Agent Management Controls */}
                      <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Button
                          variant="outlined"
                          size="small"
                          color="primary"
                          startIcon={<PlayArrowIcon />}
                          onClick={async () => {
                            try {
                              setManagingAgent(agent.agent_id);
                              await apiService.startAgent(agent.agent_id);
                              // Refresh agents list
                              const response = await apiService.listAgents();
                              setAgents(response.agents || []);
                            } catch (error) {
                              console.error('Failed to start agent:', error);
                              alert(`Failed to start agent: ${error instanceof Error ? error.message : 'Unknown error'}`);
                            } finally {
                              setManagingAgent(null);
                            }
                          }}
                          disabled={agent.status === 'active' || managingAgent === agent.agent_id}
                        >
                          {managingAgent === agent.agent_id ? <CircularProgress size={16} /> : 'Start'}
                        </Button>
                        <Button
                          variant="outlined"
                          size="small"
                          color="secondary"
                          startIcon={<StopIcon />}
                          onClick={async () => {
                            try {
                              setManagingAgent(agent.agent_id);
                              await apiService.stopAgent(agent.agent_id);
                              // Refresh agents list
                              const response = await apiService.listAgents();
                              setAgents(response.agents || []);
                            } catch (error) {
                              console.error('Failed to stop agent:', error);
                              alert(`Failed to stop agent: ${error instanceof Error ? error.message : 'Unknown error'}`);
                            } finally {
                              setManagingAgent(null);
                            }
                          }}
                          disabled={agent.status !== 'active' || managingAgent === agent.agent_id}
                        >
                          {managingAgent === agent.agent_id ? <CircularProgress size={16} /> : 'Stop'}
                        </Button>
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<SettingsIcon />}
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            console.log('[AgentList] ========== CONFIGURE BUTTON CLICKED ==========');
                            console.log('[AgentList] Agent ID:', agent.agent_id);
                            console.log('[AgentList] Agent Name:', agent.name);
                            console.log('[AgentList] Current configuringAgent state:', configuringAgent);
                            console.log('[AgentList] Setting configuringAgent to:', agent.agent_id);
                            
                            // FORCE STATE UPDATE
                            setConfiguringAgent(agent.agent_id);
                            
                            // VERIFY STATE WAS SET
                            setTimeout(() => {
                              console.log('[AgentList] State after update (checking):', agent.agent_id);
                            }, 100);
                            
                            console.log('[AgentList] ============================================');
                          }}
                        >
                          Configure Tools
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
                </>
              ))}
            </Grid>
          )}
        </>
      )}

      {activeTab === 1 && <AIProvidersPanel />}

      {/* Tool Configuration Dialog */}
      {configuringAgent ? (
        <>
          {(() => {
            const agentName = agents.find(a => a.agent_id === configuringAgent)?.name || 'Unknown';
            console.log('[AgentList] ========== RENDERING AgentToolConfiguration ==========');
            console.log('[AgentList] configuringAgent:', configuringAgent);
            console.log('[AgentList] Agent name:', agentName);
            console.log('[AgentList] Will render AgentToolConfiguration component NOW');
            console.log('[AgentList] ======================================================');
            return null;
          })()}
          <AgentToolConfiguration
            key={`config-${configuringAgent}-${Date.now()}`}
            agentId={configuringAgent}
            agentName={agents.find(a => a.agent_id === configuringAgent)?.name || 'Unknown'}
            open={true}
            onClose={() => {
              console.log('[AgentList] Closing configuration dialog');
              setConfiguringAgent(null);
            }}
          />
        </>
      ) : null}
    </Box>
  );
};

