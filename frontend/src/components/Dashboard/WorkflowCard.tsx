import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  IconButton,
  Avatar,
  AvatarGroup,
  Tooltip,
  useTheme,
  alpha,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  MoreVert as MoreVertIcon,
  AccessTime as TimeIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { WorkflowExecution } from '../../types/agent';

interface WorkflowCardProps {
  execution: WorkflowExecution;
}

export const WorkflowCard: React.FC<WorkflowCardProps> = ({ execution }) => {
  const theme = useTheme();
  
  const getStatusColor = (status: string, health: string) => {
    if (health === 'degraded') return theme.palette.warning.main;
    if (status === 'failed') return theme.palette.error.main;
    if (status === 'completed') return theme.palette.success.main;
    return theme.palette.primary.main;
  };
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'executing':
        return <PlayIcon />;
      case 'paused':
        return <PauseIcon />;
      case 'completed':
        return <PlayIcon color="success" />;
      case 'failed':
        return <StopIcon color="error" />;
      default:
        return <PlayIcon />;
    }
  };
  
  const formatDuration = (hours: number) => {
    if (hours < 1) {
      return `${Math.round(hours * 60)}m`;
    }
    return `${hours.toFixed(1)}h`;
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card 
        sx={{ 
          mb: 2,
          border: `1px solid ${alpha(getStatusColor(execution.status, execution.overallHealth), 0.3)}`,
          '&:hover': {
            boxShadow: theme.shadows[8],
          }
        }}
      >
        <CardContent>
          <Box display="flex" justifyContent="between" alignItems="flex-start" mb={2}>
            <Box flex={1}>
              <Box display="flex" alignItems="center" mb={1}>
                <Avatar 
                  sx={{ 
                    width: 32, 
                    height: 32, 
                    mr: 2,
                    backgroundColor: getStatusColor(execution.status, execution.overallHealth)
                  }}
                >
                  {getStatusIcon(execution.status)}
                </Avatar>
                <Box>
                  <Typography variant="h6" component="div">
                    {execution.workflowId.replace('workflow_', '').replace('_', ' ')}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {execution.executionId}
                  </Typography>
                </Box>
              </Box>
              
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Chip 
                  label={execution.status.toUpperCase()}
                  size="small"
                  color={execution.status === 'executing' ? 'primary' : 
                         execution.status === 'completed' ? 'success' :
                         execution.status === 'failed' ? 'error' : 'default'}
                />
                <Chip 
                  label={execution.overallHealth.toUpperCase()}
                  size="small"
                  variant="outlined"
                  color={execution.overallHealth === 'healthy' ? 'success' :
                         execution.overallHealth === 'warning' ? 'warning' : 'error'}
                />
                <Chip 
                  label={execution.currentPhase.replace('_', ' ')}
                  size="small"
                  variant="outlined"
                />
              </Box>
            </Box>
            
            <IconButton size="small">
              <MoreVertIcon />
            </IconButton>
          </Box>

          {/* Progress Bar */}
          <Box mb={2}>
            <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
              <Typography variant="body2" color="textSecondary">
                Progress
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {execution.progressPercentage.toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={execution.progressPercentage}
              sx={{ 
                height: 8, 
                borderRadius: 4,
                backgroundColor: alpha(getStatusColor(execution.status, execution.overallHealth), 0.1),
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getStatusColor(execution.status, execution.overallHealth),
                }
              }} 
            />
          </Box>

          {/* Task Status */}
          <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
            <Box display="flex" alignItems="center" gap={2}>
              <Box display="flex" alignItems="center">
                <Box 
                  width={12} 
                  height={12} 
                  borderRadius="50%" 
                  bgcolor="success.main" 
                  mr={0.5} 
                />
                <Typography variant="caption">
                  {execution.tasksCompleted} completed
                </Typography>
              </Box>
              <Box display="flex" alignItems="center">
                <Box 
                  width={12} 
                  height={12} 
                  borderRadius="50%" 
                  bgcolor="warning.main" 
                  mr={0.5} 
                />
                <Typography variant="caption">
                  {execution.tasksInProgress} in progress
                </Typography>
              </Box>
              <Box display="flex" alignItems="center">
                <Box 
                  width={12} 
                  height={12} 
                  borderRadius="50%" 
                  bgcolor="grey.400" 
                  mr={0.5} 
                />
                <Typography variant="caption">
                  {execution.tasksPending} pending
                </Typography>
              </Box>
            </Box>
            
            <Box display="flex" alignItems="center" color="textSecondary">
              <TimeIcon fontSize="small" sx={{ mr: 0.5 }} />
              <Typography variant="caption">
                {formatDuration(execution.estimatedRemainingHours)} remaining
              </Typography>
            </Box>
          </Box>

          {/* Timeline */}
          {execution.startedAt && (
            <Box>
              <Typography variant="caption" color="textSecondary">
                Started {new Date(execution.startedAt).toLocaleTimeString()}
                {execution.completedAt && 
                  ` • Completed ${new Date(execution.completedAt).toLocaleTimeString()}`
                }
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};
