// frontend/src/components/Testing/DatabaseTestingPanel.tsx
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import { PlayArrow as PlayArrowIcon, CheckCircle as CheckCircleIcon, Error as ErrorIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import React, { useState } from 'react';
import { testingService, DatabaseTestResponse, TestResult } from '../../services/testing';

export const DatabaseTestingPanel: React.FC = () => {
  const [testingStatus, setTestingStatus] = useState(false);
  const [testingQuery, setTestingQuery] = useState(false);
  const [statusResult, setStatusResult] = useState<DatabaseTestResponse | null>(null);
  const [queryResult, setQueryResult] = useState<TestResult | null>(null);
  const [testQuery, setTestQuery] = useState<string>('SELECT COUNT(*) FROM tasks');
  const [error, setError] = useState<string | null>(null);

  const handleTestStatus = async () => {
    try {
      setTestingStatus(true);
      setError(null);
      setStatusResult(null);
      const result = await testingService.testDatabaseStatus();
      setStatusResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to test database status');
    } finally {
      setTestingStatus(false);
    }
  };

  const handleTestQuery = async () => {
    if (!testQuery.trim()) {
      setError('Please enter a SQL query');
      return;
    }

    try {
      setTestingQuery(true);
      setError(null);
      setQueryResult(null);
      const result = await testingService.testDatabaseQuery(testQuery);
      setQueryResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to test database query');
      setQueryResult({
        test_name: 'Database query execution',
        success: false,
        message: err.message || 'Query failed',
        duration: 0,
        error: err.message,
      });
    } finally {
      setTestingQuery(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Database Status Test */}
          <Box>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Connection Status
            </Typography>
            <Button
              variant="outlined"
              startIcon={testingStatus ? <CircularProgress size={20} /> : <RefreshIcon />}
              onClick={handleTestStatus}
              disabled={testingStatus}
            >
              {testingStatus ? 'Testing...' : 'Test Connection'}
            </Button>

            {statusResult && (
              <Box sx={{ mt: 2 }}>
                <Card variant="outlined" sx={{ bgcolor: statusResult.connected ? 'success.light' : 'error.light' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      {statusResult.connected ? (
                        <CheckCircleIcon color="success" />
                      ) : (
                        <ErrorIcon color="error" />
                      )}
                      <Typography variant="body1" fontWeight="bold">
                        Database {statusResult.connected ? 'Connected' : 'Disconnected'}
                      </Typography>
                    </Box>
                    {statusResult.test_result && (
                      <>
                        <Typography variant="body2" color="text.secondary">
                          {statusResult.test_result.message}
                        </Typography>
                        {statusResult.query_time && (
                          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                            Query Time: {statusResult.query_time.toFixed(3)}s
                          </Typography>
                        )}
                        {statusResult.test_result.duration && (
                          <Typography variant="caption" display="block">
                            Test Duration: {statusResult.test_result.duration.toFixed(2)}s
                          </Typography>
                        )}
                      </>
                    )}
                  </CardContent>
                </Card>
              </Box>
            )}
          </Box>

          {/* Database Query Test */}
          <Box>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Query Execution
            </Typography>
            <TextField
              label="SQL Query"
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              placeholder="SELECT COUNT(*) FROM tasks"
              fullWidth
              multiline
              rows={3}
              sx={{ mb: 2 }}
            />
            <Button
              variant="contained"
              startIcon={testingQuery ? <CircularProgress size={20} /> : <PlayArrowIcon />}
              onClick={handleTestQuery}
              disabled={testingQuery || !testQuery.trim()}
              fullWidth
            >
              {testingQuery ? 'Executing...' : 'Execute Query'}
            </Button>

            {queryResult && (
              <Box sx={{ mt: 2 }}>
                <Card variant="outlined" sx={{ bgcolor: queryResult.success ? 'success.light' : 'error.light' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      {queryResult.success ? (
                        <CheckCircleIcon color="success" />
                      ) : (
                        <ErrorIcon color="error" />
                      )}
                      <Typography variant="body1" fontWeight="bold">
                        {queryResult.test_name}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {queryResult.message}
                    </Typography>
                    {queryResult.duration && (
                      <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                        Duration: {queryResult.duration.toFixed(2)}s
                      </Typography>
                    )}
                    {queryResult.data && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" fontWeight="bold">
                          Result Data:
                        </Typography>
                        <pre style={{ fontSize: '0.75rem', overflow: 'auto', maxHeight: '200px' }}>
                          {JSON.stringify(queryResult.data, null, 2)}
                        </pre>
                      </Box>
                    )}
                    {queryResult.error && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        {queryResult.error}
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              </Box>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

