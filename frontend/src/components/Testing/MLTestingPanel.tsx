// frontend/src/components/Testing/MLTestingPanel.tsx
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
import { PlayArrow as PlayArrowIcon, CheckCircle as CheckCircleIcon, Error as ErrorIcon } from '@mui/icons-material';
import React, { useState } from 'react';
import { testingService, MLTestResponse } from '../../services/testing';

export const MLTestingPanel: React.FC = () => {
  const [taskType, setTaskType] = useState<string>('security_scan');
  const [target, setTarget] = useState<string>('example.com');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<MLTestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTest = async () => {
    if (!taskType || !target) {
      setError('Please enter task type and target');
      return;
    }

    try {
      setTesting(true);
      setError(null);
      setTestResult(null);
      const result = await testingService.testMLPrediction(taskType, target);
      setTestResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to test ML prediction');
      setTestResult({
        available: false,
        test_result: {
          test_name: 'ML prediction',
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

          <TextField
            label="Task Type"
            value={taskType}
            onChange={(e) => setTaskType(e.target.value)}
            placeholder="security_scan"
            fullWidth
          />

          <TextField
            label="Target"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="example.com"
            fullWidth
          />

          <Button
            variant="contained"
            startIcon={testing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
            onClick={handleTest}
            disabled={testing || !taskType || !target}
            fullWidth
          >
            {testing ? 'Testing...' : 'Test ML Prediction'}
          </Button>

          {testResult && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Test Result:
              </Typography>
              <Card variant="outlined" sx={{ bgcolor: testResult.available ? 'success.light' : 'error.light' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    {testResult.available ? (
                      <CheckCircleIcon color="success" />
                    ) : (
                      <ErrorIcon color="error" />
                    )}
                    <Typography variant="body1" fontWeight="bold">
                      ML Prediction {testResult.available ? 'Available' : 'Unavailable'}
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
                      {testResult.prediction && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" fontWeight="bold">
                            Prediction:
                          </Typography>
                          <pre style={{ fontSize: '0.75rem', overflow: 'auto', maxHeight: '300px' }}>
                            {JSON.stringify(testResult.prediction, null, 2)}
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

