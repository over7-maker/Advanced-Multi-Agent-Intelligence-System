import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Clock, 
  Play, 
  Pause, 
  CheckCircle, 
  AlertTriangle, 
  Loader,
  Trash2,
  Eye,
  RotateCcw,
  Zap,
  Calendar,
  User,
  Target
} from 'lucide-react';
import { apiService, Task } from '../services/api';
import { wsService } from '../services/websocket';
import { toast } from 'react-hot-toast';
import { formatDistanceToNow } from 'date-fns';

interface TaskQueueVisualizationProps {
  onTaskSelect?: (task: Task) => void;
  selectedTaskId?: string;
  showCompleted?: boolean;
}

const TaskQueueVisualization: React.FC<TaskQueueVisualizationProps> = ({ 
  onTaskSelect, 
  selectedTaskId,
  showCompleted = false
}) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'pending' | 'running' | 'completed' | 'failed'>('all');
  const [sortBy, setSortBy] = useState<'created' | 'priority' | 'status'>('created');
  const [taskProgress, setTaskProgress] = useState<Record<string, number>>({});

  useEffect(() => {
    loadTasks();
    setupWebSocketListeners();
    
    // Refresh tasks every 10 seconds
    const interval = setInterval(loadTasks, 10000);
    
    return () => {
      clearInterval(interval);
      wsService.unsubscribe('taskUpdate', handleTaskUpdate);
    };
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const tasksData = await apiService.getTasks();
      setTasks(tasksData);
      setError(null);
      
      // Load progress for running tasks
      for (const task of tasksData) {
        if (task.status === 'running') {
          try {
            const status = await apiService.getTaskStatus(task.id);
            setTaskProgress(prev => ({
              ...prev,
              [task.id]: status.progress || 0
            }));
          } catch (err) {
            console.warn(`Failed to load progress for task ${task.id}:`, err);
          }
        }
      }
    } catch (err) {
      setError('Failed to load tasks');
      console.error('Error loading tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocketListeners = () => {
    wsService.subscribe('taskUpdate', handleTaskUpdate);
  };

  const handleTaskUpdate = (update: any) => {
    setTaskProgress(prev => ({
      ...prev,
      [update.task_id]: update.progress || 0
    }));
  };

  const handleTaskAction = async (taskId: string, action: 'start' | 'stop' | 'delete') => {
    try {
      switch (action) {
        case 'start':
          await apiService.startTask(taskId);
          toast.success('Task started successfully');
          break;
        case 'stop':
          await apiService.stopTask(taskId);
          toast.success('Task stopped successfully');
          break;
        case 'delete':
          await apiService.deleteTask(taskId);
          toast.success('Task deleted successfully');
          break;
      }
      loadTasks(); // Refresh the list
    } catch (err) {
      toast.error(`Failed to ${action} task`);
      console.error(`Error ${action}ing task:`, err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-500 bg-yellow-500/20 border-yellow-500/30';
      case 'running':
        return 'text-blue-500 bg-blue-500/20 border-blue-500/30';
      case 'completed':
        return 'text-green-500 bg-green-500/20 border-green-500/30';
      case 'failed':
        return 'text-red-500 bg-red-500/20 border-red-500/30';
      default:
        return 'text-gray-500 bg-gray-500/20 border-gray-500/30';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4" />;
      case 'running':
        return <Loader className="w-4 h-4 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'failed':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-400 bg-red-500/20';
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/20';
      case 'low':
        return 'text-green-400 bg-green-500/20';
      default:
        return 'text-gray-400 bg-gray-500/20';
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true;
    if (filter === 'completed' && !showCompleted) return false;
    return task.status === filter;
  });

  const sortedTasks = [...filteredTasks].sort((a, b) => {
    switch (sortBy) {
      case 'created':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      case 'priority':
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        return (priorityOrder[b.priority as keyof typeof priorityOrder] || 0) - 
               (priorityOrder[a.priority as keyof typeof priorityOrder] || 0);
      case 'status':
        return a.status.localeCompare(b.status);
      default:
        return 0;
    }
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Loader className="w-6 h-6 animate-spin text-blue-500" />
          <span className="text-gray-300">Loading tasks...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={loadTasks}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Task Queue</h2>
          <p className="text-gray-400">Monitor and manage task execution</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-400">
            {tasks.filter(t => t.status === 'running').length} running, {tasks.filter(t => t.status === 'pending').length} pending
          </div>
          <button
            onClick={loadTasks}
            className="p-2 bg-slate-700 text-gray-300 rounded-lg hover:bg-slate-600 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex space-x-2">
          {(['all', 'pending', 'running', 'completed', 'failed'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
        
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="px-3 py-1 bg-slate-700 text-gray-300 rounded-lg border border-gray-600"
        >
          <option value="created">Sort by Created</option>
          <option value="priority">Sort by Priority</option>
          <option value="status">Sort by Status</option>
        </select>
      </div>

      {/* Task List */}
      <div className="space-y-3">
        <AnimatePresence>
          {sortedTasks.map((task) => {
            const isSelected = selectedTaskId === task.id;
            const progress = taskProgress[task.id] || 0;
            
            return (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                whileHover={{ scale: 1.01 }}
                className={`relative bg-gradient-to-r from-slate-800/50 to-slate-700/50 rounded-lg p-4 border transition-all duration-200 cursor-pointer ${
                  isSelected 
                    ? 'border-blue-500 shadow-lg shadow-blue-500/20' 
                    : 'border-gray-700/50 hover:border-blue-500/50'
                }`}
                onClick={() => onTaskSelect?.(task)}
              >
                {/* Selection Indicator */}
                {isSelected && (
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-3 h-3 text-white" />
                  </div>
                )}

                <div className="flex items-center justify-between">
                  {/* Task Info */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className={`p-2 rounded-lg ${getStatusColor(task.status)}`}>
                        {getStatusIcon(task.status)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-white">{task.description}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-400">
                          <span>Agent: {task.agent_id}</span>
                          <span className={`px-2 py-1 rounded ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                          </span>
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>{formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}</span>
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Progress Bar for Running Tasks */}
                    {task.status === 'running' && (
                      <div className="mb-2">
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                          <span>Progress</span>
                          <span>{Math.round(progress)}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <motion.div
                            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ duration: 0.5 }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Task Configuration */}
                    {task.config && Object.keys(task.config).length > 0 && (
                      <div className="text-xs text-gray-400">
                        Config: {Object.entries(task.config).map(([key, value]) => 
                          `${key}: ${value}`
                        ).join(', ')}
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center space-x-2">
                    {task.status === 'pending' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleTaskAction(task.id, 'start');
                        }}
                        className="p-2 bg-green-600/20 text-green-400 rounded-lg hover:bg-green-600/30 transition-colors"
                        title="Start Task"
                      >
                        <Play className="w-4 h-4" />
                      </button>
                    )}
                    
                    {task.status === 'running' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleTaskAction(task.id, 'stop');
                        }}
                        className="p-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors"
                        title="Stop Task"
                      >
                        <Pause className="w-4 h-4" />
                      </button>
                    )}
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTaskAction(task.id, 'delete');
                      }}
                      className="p-2 bg-gray-600/20 text-gray-400 rounded-lg hover:bg-gray-600/30 transition-colors"
                      title="Delete Task"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Empty State */}
      {sortedTasks.length === 0 && (
        <div className="text-center py-12">
          <Zap className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-400 mb-2">No Tasks Found</h3>
          <p className="text-gray-500 mb-4">
            {filter === 'all' 
              ? 'No tasks are currently available.'
              : `No ${filter} tasks found.`
            }
          </p>
          <button
            onClick={loadTasks}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      )}
    </div>
  );
};

export default TaskQueueVisualization;