// frontend/src/components/Tasks/TaskExecutionView.tsx
import {
  CheckCircle as CheckCircleIcon,
  PlayArrow as PlayArrowIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  LinearProgress,
  Paper,
  Step,
  StepContent,
  StepLabel,
  Stepper,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Typography,
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiService, Task } from '../../services/api';
import { websocketService } from '../../services/websocket';
import { TaskResultsViewer } from './TaskResultsViewer';

interface ExecutionEvent {
  timestamp: string;
  event_type: string;
  message: string;
  agent_id?: string;
  agent_name?: string;
  data?: any;
}

export const TaskExecutionView: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<Task | null>(null);
  const [events, setEvents] = useState<ExecutionEvent[]>([]);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTask = async () => {
      try {
        setLoading(true);
        if (taskId && taskId !== 'create') {
          const taskData = await apiService.getTask(taskId);
          setTask(taskData);
        } else if (taskId === 'create') {
          // Redirect to create page if somehow we get here with 'create' as taskId
          navigate('/tasks/create', { replace: true });
        }
      } catch (error) {
        console.error('Failed to fetch task:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  useEffect(() => {
    if (!taskId) return;

    websocketService.subscribeToTask(taskId);

    const unsubscribeTaskUpdate = websocketService.on('task_update', (data) => {
      if (data.task_id === taskId) {
        setTask((prev) => (prev ? { ...prev, ...data } : null));
      }
    });

    const unsubscribeTaskProgress = websocketService.on('task_progress', (data) => {
      if (data.task_id === taskId) {
        setProgress(data.progress || 0);
        setEvents((prev) => [
          ...prev,
          {
            timestamp: data.timestamp || new Date().toISOString(),
            event_type: 'progress',
            message: `${data.current_step || 'Progress'}: ${data.progress}%`,
            data,
          },
        ]);
      }
    });
    
    const unsubscribeTaskExecutionStarted = websocketService.on('task_execution_started', (data) => {
      if (data.task_id === taskId) {
        setEvents((prev) => [
          ...prev,
          {
            timestamp: data.timestamp || new Date().toISOString(),
            event_type: 'execution_started',
            message: 'Task execution started',
            data,
          },
        ]);
      }
    });

    const unsubscribeAgentStart = websocketService.on('agent_started', (data) => {
      if (data.task_id === taskId) {
        setEvents((prev) => [
          ...prev,
          {
            timestamp: new Date().toISOString(),
            event_type: 'agent_started',
            message: `Agent ${data.agent_name || data.agent_id} started execution`,
            agent_id: data.agent_id,
            agent_name: data.agent_name,
            data,
          },
        ]);
      }
    });

    const unsubscribeAgentComplete = websocketService.on('agent_completed', (data) => {
      if (data.task_id === taskId) {
        setEvents((prev) => [
          ...prev,
          {
            timestamp: new Date().toISOString(),
            event_type: 'agent_completed',
            message: `Agent ${data.agent_name || data.agent_id} completed`,
            agent_id: data.agent_id,
            agent_name: data.agent_name,
            data,
          },
        ]);
      }
    });

    const unsubscribeTaskComplete = websocketService.on('task_completed', (data) => {
      if (data.task_id === taskId) {
        setProgress(100);
        setTask((prev) => (prev ? { ...prev, status: 'completed', ...data } : null));
      }
    });

    const unsubscribeTaskFailed = websocketService.on('task_failed', (data) => {
      if (data.task_id === taskId) {
        setTask((prev) => (prev ? { ...prev, status: 'failed', ...data } : null));
      }
    });

    return () => {
      websocketService.unsubscribeFromTask(taskId);
      unsubscribeTaskUpdate();
      unsubscribeTaskProgress();
      unsubscribeAgentStart();
      unsubscribeAgentComplete();
      unsubscribeTaskComplete();
      unsubscribeTaskFailed();
      if (unsubscribeTaskExecutionStarted) {
        unsubscribeTaskExecutionStarted();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  const getStatusColor = (status: string): 'default' | 'success' | 'error' | 'warning' | 'info' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'executing':
        return 'warning';
      default:
        return 'info';
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  if (!task) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Task not found</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Typography variant="h4" component="h1">
            {task.title}
          </Typography>
          <Chip label={task.status} color={getStatusColor(task.status)} />
          <Chip label={task.task_type} variant="outlined" />
        </Box>
        <Typography variant="body2" color="text.secondary">
          Task ID: {task.task_id}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          {task.status === 'executing' && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Execution Progress
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                  <Box sx={{ width: '100%', mr: 1 }}>
                    <LinearProgress variant="determinate" value={progress} sx={{ height: 10, borderRadius: 5 }} />
                  </Box>
                  <Box sx={{ minWidth: 35 }}>
                    <Typography variant="body2" color="text.secondary">
                      {progress}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )}

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Execution Timeline
              </Typography>
              {events.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  No execution events yet
                </Typography>
              ) : (
                <Stepper orientation="vertical" sx={{ mt: 2 }}>
                  {events.map((event, index) => (
                    <Step key={index} active={true} completed={event.event_type === 'agent_completed'}>
                      <StepLabel
                        icon={
                          event.event_type === 'agent_completed' ? (
                            <CheckCircleIcon color="success" />
                          ) : event.event_type === 'agent_started' ? (
                            <PlayArrowIcon color="primary" />
                          ) : (
                            <ScheduleIcon color="action" />
                          )
                        }
                      >
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {event.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Box>
                      </StepLabel>
                      {event.data && (
                        <StepContent>
                          <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                            {event.data.provider && (
                              <Typography variant="caption" display="block">
                                Provider: {event.data.provider}
                              </Typography>
                            )}
                            {event.data.tokens && (
                              <Typography variant="caption" display="block">
                                Tokens: {event.data.tokens}
                              </Typography>
                            )}
                            {event.data.cost && (
                              <Typography variant="caption" display="block">
                                Cost: ${event.data.cost.toFixed(4)}
                              </Typography>
                            )}
                          </Paper>
                        </StepContent>
                      )}
                    </Step>
                  ))}
                </Stepper>
              )}
            </CardContent>
          </Card>

          {/* Show results if completed OR if we have valuable outputs even if failed */}
          {(task.status === 'completed' || (task.status === 'failed' && (task.result || task.output || task.agent_results))) && (
            <Box>
              <TaskResultsViewer 
                result={task.result || task.output || { 
                  agent_results: task.agent_results || {},
                  success: task.status === 'completed',
                  quality_score: task.quality_score || 0,
                  execution_time: task.duration_seconds || 0,
                  total_cost_usd: task.total_cost_usd || 0
                }} 
                taskType={task.task_type} 
              />
            </Box>
          )}

          {task.status === 'failed' && !task.result && !task.output && !task.agent_results && task.error_details && (
            <Alert severity="error">
              <Typography variant="subtitle2" gutterBottom>
                Execution Failed
              </Typography>
              <Typography variant="body2">{JSON.stringify(task.error_details)}</Typography>
            </Alert>
          )}
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Task Information
              </Typography>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Target</TableCell>
                    <TableCell>{task.target}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Priority</TableCell>
                    <TableCell>
                      <Chip label={task.priority} size="small" color={task.priority >= 8 ? 'error' : 'default'} />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Created</TableCell>
                    <TableCell>{new Date(task.created_at).toLocaleString()}</TableCell>
                  </TableRow>
                  {task.started_at && (
                    <TableRow>
                      <TableCell>Started</TableCell>
                      <TableCell>{new Date(task.started_at).toLocaleString()}</TableCell>
                    </TableRow>
                  )}
                  {task.completed_at && (
                    <TableRow>
                      <TableCell>Completed</TableCell>
                      <TableCell>{new Date(task.completed_at).toLocaleString()}</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {(task.duration_seconds || task.quality_score || task.cost_usd) && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance
                </Typography>
                <Table size="small">
                  <TableBody>
                    {task.duration_seconds && (
                      <TableRow>
                        <TableCell>Duration</TableCell>
                        <TableCell>{task.duration_seconds.toFixed(2)}s</TableCell>
                      </TableRow>
                    )}
                    {task.quality_score && (
                      <TableRow>
                        <TableCell>Quality Score</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <LinearProgress
                              variant="determinate"
                              value={task.quality_score * 100}
                              sx={{ width: 60, mr: 1 }}
                              color={task.quality_score >= 0.8 ? 'success' : 'warning'}
                            />
                            {(task.quality_score * 100).toFixed(0)}%
                          </Box>
                        </TableCell>
                      </TableRow>
                    )}
                    {task.cost_usd !== undefined && (
                      <TableRow>
                        <TableCell>Cost</TableCell>
                        <TableCell>${task.cost_usd.toFixed(4)}</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}

          {task.assigned_agents && task.assigned_agents.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Assigned Agents
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {task.assigned_agents.map((agentId, index) => (
                    <Chip key={index} label={agentId} size="small" variant="outlined" />
                  ))}
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default TaskExecutionView;

