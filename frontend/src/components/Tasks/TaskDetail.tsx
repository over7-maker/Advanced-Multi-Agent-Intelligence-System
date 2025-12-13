// frontend/src/components/Tasks/TaskDetail.tsx
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Button,
  Grid,
  Paper,
  Divider,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  PlayArrow as PlayIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { apiService, Task } from '../../services/api';
import { websocketService } from '../../services/websocket';

export const TaskDetail: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!taskId) return;

    const fetchTask = async () => {
      try {
        setLoading(true);
        const taskData = await apiService.getTask(taskId);
        setTask(taskData);

        // Fetch progress if task is executing
        if (taskData.status === 'executing') {
          const progressData = await apiService.getTaskProgress(taskId);
          setProgress(progressData.progress || 0);
        }
      } catch (error) {
        console.error('Failed to fetch task:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTask();

    // Subscribe to real-time updates
    const unsubscribe = websocketService.on('task_update', (data) => {
      if (data.task_id === taskId) {
        setTask((prev) => (prev ? { ...prev, ...data } : null));
        if (data.progress !== undefined) {
          setProgress(data.progress);
        }
      }
    });

    return () => {
      unsubscribe();
    };
  }, [taskId]);

  const handleExecute = async () => {
    if (!taskId) return;
    try {
      await apiService.executeTask(taskId);
      const taskData = await apiService.getTask(taskId);
      setTask(taskData);
    } catch (error) {
      console.error('Failed to execute task:', error);
    }
  };

  const handleCancel = async () => {
    if (!taskId) return;
    try {
      await apiService.cancelTask(taskId);
      const taskData = await apiService.getTask(taskId);
      setTask(taskData);
    } catch (error) {
      console.error('Failed to cancel task:', error);
    }
  };

  if (loading) {
    return <Typography>Loading...</Typography>;
  }

  if (!task) {
    return <Typography>Task not found</Typography>;
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'executing':
        return 'warning';
      case 'pending':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/tasks')}
        sx={{ mb: 2 }}
      >
        Back to Tasks
      </Button>

      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h4">{task.title}</Typography>
            <Chip
              label={task.status}
              color={getStatusColor(task.status) as any}
            />
          </Box>

          {task.status === 'executing' && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Progress: {progress}%
              </Typography>
              <LinearProgress variant="determinate" value={progress} />
            </Box>
          )}

          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Task Information
                </Typography>
                <Divider sx={{ my: 1 }} />
                <Typography variant="body2">
                  <strong>ID:</strong> {task.task_id}
                </Typography>
                <Typography variant="body2">
                  <strong>Type:</strong> {task.task_type}
                </Typography>
                <Typography variant="body2">
                  <strong>Priority:</strong> {task.priority}
                </Typography>
                <Typography variant="body2">
                  <strong>Created:</strong>{' '}
                  {new Date(task.created_at).toLocaleString()}
                </Typography>
                {task.started_at && (
                  <Typography variant="body2">
                    <strong>Started:</strong>{' '}
                    {new Date(task.started_at).toLocaleString()}
                  </Typography>
                )}
                {task.completed_at && (
                  <Typography variant="body2">
                    <strong>Completed:</strong>{' '}
                    {new Date(task.completed_at).toLocaleString()}
                  </Typography>
                )}
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Performance Metrics
                </Typography>
                <Divider sx={{ my: 1 }} />
                {task.duration_seconds && (
                  <Typography variant="body2">
                    <strong>Duration:</strong> {task.duration_seconds.toFixed(2)}s
                  </Typography>
                )}
                {task.success_rate !== undefined && (
                  <Typography variant="body2">
                    <strong>Success Rate:</strong>{' '}
                    {(task.success_rate * 100).toFixed(1)}%
                  </Typography>
                )}
                {task.quality_score !== undefined && (
                  <Typography variant="body2">
                    <strong>Quality Score:</strong>{' '}
                    {(task.quality_score * 100).toFixed(1)}%
                  </Typography>
                )}
                {task.cost_usd !== undefined && (
                  <Typography variant="body2">
                    <strong>Cost:</strong> ${task.cost_usd.toFixed(4)}
                  </Typography>
                )}
                {task.tokens_used && (
                  <Typography variant="body2">
                    <strong>Tokens Used:</strong> {task.tokens_used.toLocaleString()}
                  </Typography>
                )}
              </Paper>
            </Grid>

            {task.description && (
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Description
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="body2">{task.description}</Typography>
                </Paper>
              </Grid>
            )}

            {task.result && (
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Result
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {JSON.stringify(task.result, null, 2)}
                  </pre>
                </Paper>
              </Grid>
            )}

            {task.error_details && (
              <Grid item xs={12}>
                <Paper sx={{ p: 2, bgcolor: 'error.light' }}>
                  <Typography variant="subtitle2" color="error">
                    Error Details
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {JSON.stringify(task.error_details, null, 2)}
                  </pre>
                </Paper>
              </Grid>
            )}
          </Grid>

          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            {task.status === 'pending' && (
              <Button
                variant="contained"
                startIcon={<PlayIcon />}
                onClick={handleExecute}
              >
                Execute Task
              </Button>
            )}
            {(task.status === 'executing' || task.status === 'pending') && (
              <Button
                variant="outlined"
                color="error"
                startIcon={<CancelIcon />}
                onClick={handleCancel}
              >
                Cancel Task
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

