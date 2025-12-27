// frontend/src/components/Testing/AgentTestingPanel.tsx
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Select,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import { PlayArrow as PlayArrowIcon, CheckCircle as CheckCircleIcon, Error as ErrorIcon } from '@mui/icons-material';
import React, { useEffect, useState } from 'react';
import { testingService, AgentTestResponse } from '../../services/testing';

export const AgentTestingPanel: React.FC = () => {
  const [agents, setAgents] = useState<AgentTestResponse[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [testTarget, setTestTarget] = useState<string>('example.com');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<AgentTestResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const agentsList = await testingService.listAgents();
      setAgents(agentsList);
      if (agentsList.length > 0 && !selectedAgent) {
        setSelectedAgent(agentsList[0].agent_id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    if (!selectedAgent || !testTarget) {
      setError('Please select an agent and enter a target');
      return;
    }

    try {
      setTesting(true);
      setError(null);
      setTestResult(null);
      const result = await testingService.testAgent(selectedAgent, testTarget);
      setTestResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to test agent');
      setTestResult({
        agent_id: selectedAgent,
        agent_name: selectedAgent,
        available: false,
        test_result: {
          test_name: 'Agent execution',
          success: false,
          message: err.message || 'Test failed',
          duration: 0,
          error: err.message,
        },
      });
    } finally {
      setTesting(false);
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
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <FormControl fullWidth>
            <InputLabel>Select Agent</InputLabel>
            <Select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              label="Select Agent"
            >
              {agents.map((agent) => (
                <MenuItem key={agent.agent_id} value={agent.agent_id}>
                  {agent.agent_name} ({agent.agent_id})
                  {agent.available && <CheckCircleIcon sx={{ ml: 1, fontSize: 16, color: 'success.main' }} />}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              label="Test Target"
              value={testTarget}
              onChange={(e) => setTestTarget(e.target.value)}
              placeholder="example.com"
              fullWidth
              sx={{ flex: 1 }}
            />
            <Button
              variant="contained"
              startIcon={testing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
              onClick={handleTest}
              disabled={testing || !selectedAgent || !testTarget}
              sx={{ minWidth: 150 }}
            >
              {testing ? 'Testing...' : 'Test Agent'}
            </Button>
          </Box>
          
          {selectedAgent && (
            <Alert severity="info" sx={{ mt: 1 }}>
              Testing <strong>{agents.find(a => a.agent_id === selectedAgent)?.agent_name || selectedAgent}</strong> with target: <strong>{testTarget}</strong>
            </Alert>
          )}

          {testResult && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Test Result:
              </Typography>
              <Card variant="outlined" sx={{ bgcolor: testResult.test_result?.success ? 'success.light' : 'error.light' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    {testResult.test_result?.success ? (
                      <CheckCircleIcon color="success" />
                    ) : (
                      <ErrorIcon color="error" />
                    )}
                    <Typography variant="body1" fontWeight="bold">
                      {testResult.test_result?.test_name}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {testResult.test_result?.message}
                  </Typography>
                  {testResult.test_result?.duration && (
                    <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                      Duration: {testResult.test_result.duration.toFixed(2)}s
                    </Typography>
                  )}
                  {testResult.test_result?.error && (
                    <Alert severity="error" sx={{ mt: 1 }}>
                      {testResult.test_result.error}
                    </Alert>
                  )}
                  {testResult.test_result?.data && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" fontWeight="bold">
                        Test Data:
                      </Typography>
                      <pre style={{ fontSize: '0.75rem', overflow: 'auto', maxHeight: '200px' }}>
                        {JSON.stringify(testResult.test_result.data, null, 2)}
                      </pre>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Box>
          )}

          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Available Agents ({agents.length}):
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }, gap: 1.5 }}>
              {agents.map((agent) => (
                <Card 
                  key={agent.agent_id} 
                  variant="outlined" 
                  sx={{ 
                    p: 1.5,
                    cursor: agent.available ? 'pointer' : 'not-allowed',
                    opacity: agent.available ? 1 : 0.6,
                    '&:hover': agent.available ? { bgcolor: 'action.hover' } : {},
                    borderColor: agent.available ? 'success.main' : 'error.main',
                    borderWidth: 1,
                    borderStyle: 'solid'
                  }}
                  onClick={() => agent.available && setSelectedAgent(agent.agent_id)}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" fontWeight="bold" noWrap sx={{ flex: 1, mr: 1 }}>
                      {agent.agent_name}
                    </Typography>
                    {agent.available ? (
                      <CheckCircleIcon sx={{ fontSize: 16, color: 'success.main' }} />
                    ) : (
                      <ErrorIcon sx={{ fontSize: 16, color: 'error.main' }} />
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary" noWrap>
                    {agent.agent_id}
                  </Typography>
                  <Chip
                    label={agent.available ? 'Available' : 'Unavailable'}
                    color={agent.available ? 'success' : 'error'}
                    size="small"
                    sx={{ mt: 0.5 }}
                  />
                </Card>
              ))}
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

