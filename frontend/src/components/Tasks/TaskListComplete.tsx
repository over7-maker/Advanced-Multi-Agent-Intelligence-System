// frontend/src/components/Tasks/TaskListComplete.tsx
// Complete TaskList component per PART_7 specifications
import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  LinearProgress,
  MenuItem,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Tooltip,
  Typography,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  Cancel as CancelIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { apiService, Task, TaskPrediction } from '../../services/api';
import { websocketService } from '../../services/websocket';
import { useNavigate } from 'react-router-dom';

export const TaskListComplete: React.FC = () => {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalTasks, setTotalTasks] = useState(0);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterTaskType, setFilterTaskType] = useState<string>('all');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const params: any = {
        limit: rowsPerPage,
        offset: page * rowsPerPage,
      };

      if (filterStatus !== 'all') {
        params.status = filterStatus;
      }

      if (filterTaskType !== 'all') {
        params.task_type = filterTaskType;
      }

      const response = await apiService.listTasks(params);
      setTasks(response.tasks);
      setTotalTasks(response.total);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchTasks();
    setRefreshing(false);
  };

  useEffect(() => {
    fetchTasks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage, filterStatus, filterTaskType]);

  useEffect(() => {
    const unsubscribe = websocketService.on('task_update', (data) => {
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.task_id === data.task_id
            ? { ...task, status: data.status, updated_at: data.timestamp }
            : task
        )
      );
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const handleExecuteTask = async (taskId: string) => {
    try {
      await apiService.executeTask(taskId);
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.task_id === taskId ? { ...task, status: 'executing' } : task
        )
      );
    } catch (error) {
      console.error('Failed to execute task:', error);
    }
  };

  const handleCancelTask = async (taskId: string) => {
    try {
      await apiService.cancelTask(taskId);
      await fetchTasks();
    } catch (error) {
      console.error('Failed to cancel task:', error);
    }
  };

  const handleViewTask = (taskId: string) => {
    navigate(`/tasks/${taskId}`);
  };

  const getStatusColor = (status: string): 'default' | 'success' | 'error' | 'warning' | 'info' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
      case 'timeout':
        return 'error';
      case 'executing':
        return 'warning';
      case 'pending':
      case 'assigned':
        return 'info';
      case 'cancelled':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string): React.ReactElement | null => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon fontSize="small" />;
      case 'failed':
      case 'timeout':
        return <ErrorIcon fontSize="small" />;
      case 'executing':
        return <PlayIcon fontSize="small" />;
      case 'pending':
      case 'assigned':
        return <ScheduleIcon fontSize="small" />;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Tasks
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} disabled={refreshing}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Task
          </Button>
        </Box>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  label="Status"
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="executing">Executing</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="failed">Failed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Task Type</InputLabel>
                <Select
                  value={filterTaskType}
                  label="Task Type"
                  onChange={(e) => setFilterTaskType(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="security_scan">Security Scan</MenuItem>
                  <MenuItem value="code_analysis">Code Analysis</MenuItem>
                  <MenuItem value="intelligence_gathering">Intelligence Gathering</MenuItem>
                  <MenuItem value="performance_analysis">Performance Analysis</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Quality</TableCell>
                <TableCell>Cost</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9}>
                    <LinearProgress />
                  </TableCell>
                </TableRow>
              ) : tasks.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No tasks found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                tasks.map((task) => (
                  <TableRow key={task.task_id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {task.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {task.task_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={task.task_type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={task.status}
                        size="small"
                        color={getStatusColor(task.status)}
                        icon={getStatusIcon(task.status) || undefined}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={task.priority}
                        size="small"
                        color={task.priority >= 8 ? 'error' : task.priority >= 5 ? 'warning' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      {task.duration_seconds ? `${task.duration_seconds.toFixed(1)}s` : '-'}
                    </TableCell>
                    <TableCell>
                      {task.quality_score ? (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <LinearProgress
                            variant="determinate"
                            value={task.quality_score * 100}
                            sx={{ width: 60, mr: 1 }}
                            color={task.quality_score >= 0.8 ? 'success' : 'warning'}
                          />
                          <Typography variant="caption">{(task.quality_score * 100).toFixed(0)}%</Typography>
                        </Box>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      {task.cost_usd !== undefined ? `$${task.cost_usd.toFixed(4)}` : '-'}
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {new Date(task.created_at).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton size="small" onClick={() => handleViewTask(task.task_id)}>
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {task.status === 'pending' && (
                        <Tooltip title="Execute">
                          <IconButton size="small" onClick={() => handleExecuteTask(task.task_id)}>
                            <PlayIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      {task.status === 'executing' && (
                        <Tooltip title="Cancel">
                          <IconButton size="small" onClick={() => handleCancelTask(task.task_id)}>
                            <CancelIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={totalTasks}
          page={page}
          onPageChange={(_e, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(_e) => {
            setRowsPerPage(parseInt(_e.target.value, 10));
            setPage(0);
          }}
        />
      </Card>

      <CreateTaskDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onTaskCreated={fetchTasks}
      />
    </Box>
  );
};

interface CreateTaskDialogProps {
  open: boolean;
  onClose: () => void;
  onTaskCreated: () => void;
}

const CreateTaskDialog: React.FC<CreateTaskDialogProps> = ({ open, onClose, onTaskCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    task_type: 'security_scan',
    target: '',
    priority: 5,
    parameters: {},
  });
  const [prediction, setPrediction] = useState<TaskPrediction | null>(null);
  const [predicting, setPredicting] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setPrediction(null);
  };

  const handlePredict = async () => {
    try {
      setPredicting(true);
      setError(null);
      const predictionResult = await apiService.predictTask({
        task_type: formData.task_type,
        target: formData.target,
        parameters: formData.parameters,
      });
      setPrediction(predictionResult);
    } catch (err) {
      setError('Failed to generate prediction');
      console.error('Prediction failed:', err);
    } finally {
      setPredicting(false);
    }
  };

  const handleCreate = async () => {
    try {
      setCreating(true);
      setError(null);
      await apiService.createTask(formData);
      setFormData({
        title: '',
        description: '',
        task_type: 'security_scan',
        target: '',
        priority: 5,
        parameters: {},
      });
      setPrediction(null);
      onTaskCreated();
      onClose();
    } catch (err) {
      setError('Failed to create task');
      console.error('Task creation failed:', err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Task</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Title"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              required
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              multiline
              rows={3}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Task Type</InputLabel>
              <Select
                value={formData.task_type}
                label="Task Type"
                onChange={(e) => handleInputChange('task_type', e.target.value)}
              >
                <MenuItem value="security_scan">Security Scan</MenuItem>
                <MenuItem value="code_analysis">Code Analysis</MenuItem>
                <MenuItem value="intelligence_gathering">Intelligence Gathering</MenuItem>
                <MenuItem value="performance_analysis">Performance Analysis</MenuItem>
                <MenuItem value="documentation">Documentation</MenuItem>
                <MenuItem value="testing">Testing</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Priority"
              type="number"
              value={formData.priority}
              onChange={(e) => handleInputChange('priority', parseInt(e.target.value))}
              inputProps={{ min: 1, max: 10 }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Target"
              value={formData.target}
              onChange={(e) => handleInputChange('target', e.target.value)}
              placeholder="e.g., https://example.com or github.com/user/repo"
              required
            />
          </Grid>

          {prediction && (
            <Grid item xs={12}>
              <Card variant="outlined" sx={{ bgcolor: 'background.default' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    AI Prediction
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">
                        Success Probability
                      </Typography>
                      <Typography variant="h6" color={prediction.success_probability >= 0.7 ? 'success.main' : 'warning.main'}>
                        {(prediction.success_probability * 100).toFixed(0)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">
                        Est. Duration
                      </Typography>
                      <Typography variant="h6">{prediction.estimated_duration.toFixed(0)}s</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">
                        Est. Quality
                      </Typography>
                      <Typography variant="h6">{(prediction.quality_score_prediction * 100).toFixed(0)}%</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary">
                        Est. Cost
                      </Typography>
                      <Typography variant="h6">${prediction.estimated_cost.toFixed(4)}</Typography>
                    </Grid>
                  </Grid>
                  {prediction.recommended_agents.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Recommended Agents
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {prediction.recommended_agents.slice(0, 3).map((agent) => (
                          <Chip
                            key={agent.agent_id}
                            label={agent.agent_name}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={creating}>
          Cancel
        </Button>
        <Button onClick={handlePredict} disabled={predicting || !formData.target} variant="outlined">
          {predicting ? 'Predicting...' : 'Predict'}
        </Button>
        <Button onClick={handleCreate} disabled={creating || !formData.title || !formData.target} variant="contained">
          {creating ? 'Creating...' : 'Create Task'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TaskListComplete;

