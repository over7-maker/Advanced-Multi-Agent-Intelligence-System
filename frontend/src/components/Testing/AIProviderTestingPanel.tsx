// frontend/src/components/Testing/AIProviderTestingPanel.tsx
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
import { testingService, ProviderTestResponse } from '../../services/testing';

export const AIProviderTestingPanel: React.FC = () => {
  const [providers, setProviders] = useState<ProviderTestResponse[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [testPrompt, setTestPrompt] = useState<string>('Hello, this is a test');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<ProviderTestResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      setLoading(true);
      setError(null);
      const providersList = await testingService.listProviders();
      setProviders(providersList);
      if (providersList.length > 0 && !selectedProvider) {
        setSelectedProvider(providersList[0].provider);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load providers');
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    if (!selectedProvider || !testPrompt) {
      setError('Please select a provider and enter a test prompt');
      return;
    }

    try {
      setTesting(true);
      setError(null);
      setTestResult(null);
      const result = await testingService.testProvider(selectedProvider, testPrompt);
      setTestResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to test provider');
      setTestResult({
        provider: selectedProvider,
        available: false,
        test_result: {
          test_name: 'Provider connection',
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
            <InputLabel>Select Provider</InputLabel>
            <Select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              label="Select Provider"
            >
              {providers.map((provider) => (
                <MenuItem key={provider.provider} value={provider.provider}>
                  {provider.provider}
                  {provider.available && <CheckCircleIcon sx={{ ml: 1, fontSize: 16, color: 'success.main' }} />}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Test Prompt"
            value={testPrompt}
            onChange={(e) => setTestPrompt(e.target.value)}
            placeholder="Hello, this is a test"
            fullWidth
            multiline
            rows={3}
          />

          <Button
            variant="contained"
            startIcon={testing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
            onClick={handleTest}
            disabled={testing || !selectedProvider || !testPrompt}
            fullWidth
          >
            {testing ? 'Testing...' : 'Test Provider'}
          </Button>

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
                  {testResult.latency && (
                    <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                      Latency: {testResult.latency.toFixed(2)}s
                    </Typography>
                  )}
                  {testResult.test_result?.duration && (
                    <Typography variant="caption" display="block">
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
            <Typography variant="subtitle2" gutterBottom>
              Available Providers ({providers.length}):
            </Typography>
            <List dense>
              {providers.map((provider) => (
                <ListItem key={provider.provider}>
                  <ListItemText primary={provider.provider} />
                  <Chip
                    label={provider.available ? 'Available' : 'Unavailable'}
                    color={provider.available ? 'success' : 'error'}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

