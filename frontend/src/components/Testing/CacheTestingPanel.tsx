// frontend/src/components/Testing/CacheTestingPanel.tsx
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Typography,
  Alert,
} from '@mui/material';
import { Refresh as RefreshIcon, CheckCircle as CheckCircleIcon, Error as ErrorIcon } from '@mui/icons-material';
import React, { useState } from 'react';
import { testingService, CacheTestResponse } from '../../services/testing';

export const CacheTestingPanel: React.FC = () => {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<CacheTestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTest = async () => {
    try {
      setTesting(true);
      setError(null);
      setTestResult(null);
      const result = await testingService.testCacheStatus();
      setTestResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to test cache');
      setTestResult({
        connected: false,
        test_result: {
          test_name: 'Cache connection',
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

          <Button
            variant="outlined"
            startIcon={testing ? <CircularProgress size={20} /> : <RefreshIcon />}
            onClick={handleTest}
            disabled={testing}
            fullWidth
          >
            {testing ? 'Testing...' : 'Test Cache Connection'}
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
                      Cache {testResult.connected ? 'Connected' : 'Disconnected'}
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
                      {testResult.operations && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" fontWeight="bold">
                            Operations:
                          </Typography>
                          <pre style={{ fontSize: '0.75rem', overflow: 'auto' }}>
                            {JSON.stringify(testResult.operations, null, 2)}
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
        </Box>
      </CardContent>
    </Card>
  );
};

