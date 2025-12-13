import {
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    PlayArrow as PlayIcon,
    Schedule as ScheduleIcon,
} from '@mui/icons-material';
import {
    alpha,
    Avatar,
    Box,
    Chip,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    Typography,
    useTheme,
} from '@mui/material';
import { AnimatePresence, motion } from 'framer-motion';
import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';
import { websocketService } from '../../services/websocket';

interface ActivityItem {
  id: string;
  type: 'workflow_completed' | 'workflow_started' | 'workflow_failed' | 'agent_online' | 'task_completed';
  message: string;
  timestamp: Date;
  workflowId?: string;
  agentId?: string;
}

export const RecentActivity: React.FC = () => {
  const theme = useTheme();
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadActivities = async (): Promise<void> => {
      try {
        // Try to get recent activities from API
        const tasksResponse = await apiService.listTasks({ limit: 10 });
        if (tasksResponse.tasks) {
          const recentTasks: ActivityItem[] = tasksResponse.tasks.map((task: any) => ({
            id: task.id,
            type: 'task_completed' as ActivityItem['type'],
            message: `${task.description || 'Task'} ${task.status === 'completed' ? 'completed' : task.status === 'in_progress' ? 'started' : 'created'}`,
            timestamp: task.updated_at ? new Date(task.updated_at) : task.created_at ? new Date(task.created_at) : new Date(),
          }));
          setActivities(recentTasks);
        }
        setLoading(false);
      } catch (error) {
        console.error('Error loading activities:', error);
        // Fallback to mock data
        setActivities([
          {
            id: 'act_001',
            type: 'workflow_completed',
            message: 'Market Analysis workflow completed successfully',
            timestamp: new Date(Date.now() - 5 * 60 * 1000),
            workflowId: 'workflow_market_analysis',
          },
          {
            id: 'act_002',
            type: 'workflow_started',
            message: 'Competitor Intelligence workflow started',
            timestamp: new Date(Date.now() - 15 * 60 * 1000),
            workflowId: 'workflow_competitor_intel',
          },
        ]);
        setLoading(false);
      }
    };

    loadActivities();

    // Subscribe to real-time activity updates
    websocketService.connect();
    const unsubscribe = websocketService.on('activity', (data: any) => {
      const newActivity: ActivityItem = {
        id: data.id || `act_${Date.now()}`,
        type: data.type || 'task_completed',
        message: data.message || 'Activity update',
        timestamp: data.timestamp ? new Date(data.timestamp) : new Date(),
        workflowId: data.workflowId,
        agentId: data.agentId,
      };
      setActivities((prev) => [newActivity, ...prev].slice(0, 10));
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const getActivityIcon = (type: ActivityItem['type']) => {
    switch (type) {
      case 'workflow_completed':
        return <CheckCircleIcon color="success" />;
      case 'workflow_started':
        return <PlayIcon color="primary" />;
      case 'workflow_failed':
        return <ErrorIcon color="error" />;
      case 'agent_online':
        return <ScheduleIcon color="info" />;
      case 'task_completed':
        return <CheckCircleIcon color="success" />;
      default:
        return <ScheduleIcon />;
    }
  };

  const getActivityColor = (type: ActivityItem['type']) => {
    switch (type) {
      case 'workflow_completed':
      case 'task_completed':
        return theme.palette.success.main;
      case 'workflow_started':
        return theme.palette.primary.main;
      case 'workflow_failed':
        return theme.palette.error.main;
      case 'agent_online':
        return theme.palette.info.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const formatTimestamp = (timestamp: Date | string) => {
    const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <Box>
      <AnimatePresence>
        <List sx={{ p: 0 }}>
          {loading ? (
            <Box textAlign="center" py={2}>
              <Typography variant="body2" color="textSecondary">
                Loading activities...
              </Typography>
            </Box>
          ) : activities.length === 0 ? (
            <Box textAlign="center" py={2}>
              <Typography variant="body2" color="textSecondary">
                No recent activity
              </Typography>
            </Box>
          ) : (
            activities.map((activity, index) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <ListItem
                sx={{
                  mb: 1,
                  border: `1px solid ${alpha(getActivityColor(activity.type), 0.2)}`,
                  borderRadius: 2,
                  backgroundColor: alpha(getActivityColor(activity.type), 0.05),
                  '&:hover': {
                    backgroundColor: alpha(getActivityColor(activity.type), 0.1),
                  },
                }}
              >
                <ListItemAvatar>
                  <Avatar
                    sx={{
                      backgroundColor: alpha(getActivityColor(activity.type), 0.1),
                      color: getActivityColor(activity.type),
                    }}
                  >
                    {getActivityIcon(activity.type)}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Typography variant="body2" component="span">
                        {activity.message}
                      </Typography>
                      <Chip
                        size="small"
                        label={formatTimestamp(activity.timestamp)}
                        variant="outlined"
                        sx={{ ml: 1 }}
                      />
                    </Box>
                  }
                  secondary={
                    activity.workflowId && (
                      <Typography variant="caption" color="textSecondary">
                        {activity.workflowId}
                      </Typography>
                    )
                  }
                />
              </ListItem>
            </motion.div>
            ))
          )}
        </List>
      </AnimatePresence>
    </Box>
  );
};
