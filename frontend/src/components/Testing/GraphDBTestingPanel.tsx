// frontend/src/components/Testing/GraphDBTestingPanel.tsx
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Typography,
  Alert,
  Chip,
} from '@mui/material';
import { Refresh as RefreshIcon, CheckCircle as CheckCircleIcon, Error as ErrorIcon, AccountTree as AccountTreeIcon } from '@mui/icons-material';
import React, { useState } from 'react';
import { testingService, GraphDBTestResponse } from '../../services/testing';

export const GraphDBTestingPanel: React.FC = () => {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<GraphDBTestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTest = async () => {
    try {
      setTesting(true);
      setError(null);
      setTestResult(null);
      const result = await testingService.testGraphDBStatus();
      setTestResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to test Neo4j');
      setTestResult({
        connected: false,
        test_result: {
          test_name: 'Neo4j connection',
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

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <AccountTreeIcon color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Neo4j Graph Database Testing
            </Typography>
          </Box>

          <Button
            variant="outlined"
            startIcon={testing ? <CircularProgress size={20} /> : <RefreshIcon />}
            onClick={handleTest}
            disabled={testing}
            fullWidth
          >
            {testing ? 'Testing...' : 'Test Neo4j Connection'}
          </Button>

          {testResult && (
            <Box sx={{ mt: 2 }}>
              <Card variant="outlined" sx={{ bgcolor: testResult.connected ? 'success.light' : 'error.light' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    {testResult.connected ? (
                      <CheckCircleIcon color="success" />
                    ) : (
                      <ErrorIcon color="error" />
                    )}
                    <Typography variant="body1" fontWeight="bold">
                      Neo4j {testResult.connected ? 'Connected' : 'Disconnected'}
                    </Typography>
                  </Box>
                  {testResult.test_result && (
                    <>
                      <Typography variant="body2" color="text.secondary">
                        {testResult.test_result.message}
                      </Typography>
                      {testResult.test_result.duration && (
                        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                          Test Duration: {testResult.test_result.duration.toFixed(2)}s
                        </Typography>
                      )}
                      {testResult.node_count !== null && testResult.node_count !== undefined && (
                        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip
                            icon={<AccountTreeIcon />}
                            label={`${testResult.node_count} nodes`}
                            color="primary"
                            variant="outlined"
                          />
                        </Box>
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
        </Box>
      </CardContent>
    </Card>
  );
};


