// frontend/src/components/Tasks/TaskList.tsx
import {
  Add as AddIcon,
  Cancel as CancelIcon,
  PlayArrow as PlayIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import {
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  IconButton,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService, Task } from '../../services/api';
import { websocketService } from '../../services/websocket';

export const TaskList: React.FC = () => {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [taskTypeFilter, setTaskTypeFilter] = useState<string>('');

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await apiService.listTasks({
        status: statusFilter || undefined,
        task_type: taskTypeFilter || undefined,
        limit: rowsPerPage,
        offset: page * rowsPerPage,
      });
      setTasks(response.tasks || []);
      setTotal(response.total || 0);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();

    // Subscribe to real-time updates
    const unsubscribe = websocketService.on('task_update', (data) => {
      setTasks((prev) =>
        (prev || []).map((task) =>
          (task.task_id || task.id) === (data.task_id || data.id) ? { ...task, ...data } : task
        )
      );
    });

    return () => {
      unsubscribe();
    };
  }, [page, rowsPerPage, statusFilter, taskTypeFilter]);

  const handleExecute = async (taskId: string) => {
    try {
      await apiService.executeTask(taskId);
      fetchTasks();
    } catch (error) {
      console.error('Failed to execute task:', error);
    }
  };

  const handleCancel = async (taskId: string) => {
    try {
      await apiService.cancelTask(taskId);
      fetchTasks();
    } catch (error) {
      console.error('Failed to cancel task:', error);
    }
  };

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

  const handleCreateTask = () => {
    navigate('/tasks/create');
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h5">Tasks</Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <IconButton
              color="primary"
              onClick={handleCreateTask}
              title="Create New Task"
              sx={{ mr: 1 }}
            >
              <AddIcon />
            </IconButton>
            <TextField
              select
              label="Status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              size="small"
              sx={{ minWidth: 120 }}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="executing">Executing</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
            </TextField>
            <TextField
              label="Task Type"
              value={taskTypeFilter}
              onChange={(e) => setTaskTypeFilter(e.target.value)}
              size="small"
              sx={{ minWidth: 150 }}
            />
          </Box>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(tasks || []).map((task) => (
                    <TableRow key={task.task_id || task.id}>
                      <TableCell>{(task.task_id || task.id || '').slice(0, 8)}...</TableCell>
                      <TableCell>{task.title}</TableCell>
                      <TableCell>{task.task_type}</TableCell>
                      <TableCell>
                        <Chip
                          label={task.status}
                          color={getStatusColor(task.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{task.priority}</TableCell>
                      <TableCell>
                        {new Date(task.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/tasks/${task.task_id || task.id}`)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                        {task.status === 'pending' && (
                          <IconButton
                            size="small"
                            onClick={() => handleExecute(task.task_id || task.id)}
                          >
                            <PlayIcon />
                          </IconButton>
                        )}
                        {(task.status === 'executing' || task.status === 'pending') && (
                          <IconButton
                            size="small"
                            onClick={() => handleCancel(task.task_id || task.id)}
                          >
                            <CancelIcon />
                          </IconButton>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={total}
              page={page}
              onPageChange={(_, newPage) => setPage(newPage)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
            />
          </>
        )}
      </CardContent>
    </Card>
  );
};

