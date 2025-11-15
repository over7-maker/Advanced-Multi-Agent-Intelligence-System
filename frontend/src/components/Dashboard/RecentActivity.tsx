import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Chip,
  useTheme,
  alpha,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  PlayArrow as PlayIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

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

  useEffect(() => {
    // Simulate recent activities
    const mockActivities: ActivityItem[] = [
      {
        id: 'act_001',
        type: 'workflow_completed',
        message: 'Market Analysis workflow completed successfully',
        timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
        workflowId: 'workflow_market_analysis',
      },
      {
        id: 'act_002',
        type: 'workflow_started',
        message: 'Competitor Intelligence workflow started',
        timestamp: new Date(Date.now() - 15 * 60 * 1000), // 15 minutes ago
        workflowId: 'workflow_competitor_intel',
      },
      {
        id: 'act_003',
        type: 'task_completed',
        message: 'Data analysis task completed by Data Analyst agent',
        timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
        agentId: 'agent_data_analyst_001',
      },
      {
        id: 'act_004',
        type: 'agent_online',
        message: 'Graphics Designer agent came online',
        timestamp: new Date(Date.now() - 45 * 60 * 1000), // 45 minutes ago
        agentId: 'agent_graphics_designer_001',
      },
      {
        id: 'act_005',
        type: 'workflow_completed',
        message: 'Research Report workflow completed',
        timestamp: new Date(Date.now() - 60 * 60 * 1000), // 1 hour ago
        workflowId: 'workflow_research_report',
      },
    ];

    setActivities(mockActivities);

    // Simulate real-time updates
    const interval = setInterval(() => {
      // In real implementation, this would fetch from API
    }, 10000);

    return () => clearInterval(interval);
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

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - timestamp.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return timestamp.toLocaleDateString();
  };

  return (
    <Box>
      <AnimatePresence>
        <List sx={{ p: 0 }}>
          {activities.map((activity, index) => (
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
          ))}
        </List>
      </AnimatePresence>

      {activities.length === 0 && (
        <Box textAlign="center" py={4} color="text.secondary">
          <ScheduleIcon sx={{ fontSize: 48, opacity: 0.3, mb: 2 }} />
          <Typography variant="body2">
            No recent activity
          </Typography>
        </Box>
      )}
    </Box>
  );
};
