// frontend/src/components/Testing/IntegrationTestingPanel.tsx
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
  Alert,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { PlayArrow as PlayArrowIcon, CheckCircle as CheckCircleIcon, Error as ErrorIcon } from '@mui/icons-material';
import React, { useState } from 'react';
import { testingService, IntegrationTestResponse } from '../../services/testing';

const AVAILABLE_PLATFORMS = ['github', 'slack', 'n8n', 'notion', 'jira', 'salesforce'];

export const IntegrationTestingPanel: React.FC = () => {
  const [selectedPlatform, setSelectedPlatform] = useState<string>('');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<IntegrationTestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTest = async () => {
    if (!selectedPlatform) {
      setError('Please select a platform');
      return;
    }

    try {
      setTesting(true);
      setError(null);
      setTestResult(null);
      const result = await testingService.testIntegration(selectedPlatform);
      setTestResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to test integration');
      setTestResult({
        platform: selectedPlatform,
        connected: false,
        test_result: {
          test_name: `Integration ${selectedPlatform}`,
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
            <InputLabel>Select Platform</InputLabel>
            <Select
              value={selectedPlatform}
              onChange={(e) => setSelectedPlatform(e.target.value)}
              label="Select Platform"
            >
              {AVAILABLE_PLATFORMS.map((platform) => (
                <MenuItem key={platform} value={platform}>
                  {platform.charAt(0).toUpperCase() + platform.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            startIcon={testing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
            onClick={handleTest}
            disabled={testing || !selectedPlatform}
            fullWidth
          >
            {testing ? 'Testing...' : 'Test Integration'}
          </Button>

          {testResult && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Test Result:
              </Typography>
              <Card variant="outlined" sx={{ bgcolor: testResult.connected ? 'success.light' : 'error.light' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    {testResult.connected ? (
                      <CheckCircleIcon color="success" />
                    ) : (
                      <ErrorIcon color="error" />
                    )}
                    <Typography variant="body1" fontWeight="bold">
                      {testResult.platform} Integration
                    </Typography>
                  </Box>
                  {testResult.test_result && (
                    <>
                      <Typography variant="body2" color="text.secondary">
                        {testResult.test_result.message}
                      </Typography>
                      {testResult.test_result.duration && (
                        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                          Duration: {testResult.test_result.duration.toFixed(2)}s
                        </Typography>
                      )}
                      {testResult.test_result.data && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" fontWeight="bold">
                            Test Data:
                          </Typography>
                          <pre style={{ fontSize: '0.75rem', overflow: 'auto', maxHeight: '200px' }}>
                            {JSON.stringify(testResult.test_result.data, null, 2)}
                          </pre>
                        </Box>
                      )}
                      {testResult.test_result.error && (
                        <Alert severity="error" sx={{ mt: 1 }}>
                          {testResult.test_result.error}
                        </Alert>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>
            </Box>
          )}

          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Available Platforms:
            </Typography>
            <List dense>
              {AVAILABLE_PLATFORMS.map((platform) => (
                <ListItem key={platform}>
                  <ListItemText primary={platform.charAt(0).toUpperCase() + platform.slice(1)} />
                </ListItem>
              ))}
            </List>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

