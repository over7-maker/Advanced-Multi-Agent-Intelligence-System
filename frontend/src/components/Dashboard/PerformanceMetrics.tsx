import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Grid,
  useTheme,
  alpha,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  AttachMoney as CostIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

interface DashboardStats {
  totalWorkflows: number;
  activeWorkflows: number;
  completedToday: number;
  agentsOnline: number;
  totalAgents: number;
  avgQualityScore: number;
  costSavedToday: number;
  tasksCompletedToday: number;
}

interface PerformanceMetricsProps {
  stats: DashboardStats;
}

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ stats }) => {
  const theme = useTheme();

  const metrics = [
    {
      label: 'Workflow Completion Rate',
      value: stats.totalWorkflows > 0 
        ? ((stats.completedToday / stats.totalWorkflows) * 100).toFixed(1)
        : '0',
      unit: '%',
      icon: <AssessmentIcon />,
      color: theme.palette.primary.main,
      progress: stats.totalWorkflows > 0 
        ? (stats.completedToday / stats.totalWorkflows) * 100
        : 0,
    },
    {
      label: 'Agent Utilization',
      value: stats.totalAgents > 0
        ? ((stats.agentsOnline / stats.totalAgents) * 100).toFixed(1)
        : '0',
      unit: '%',
      icon: <SpeedIcon />,
      color: theme.palette.success.main,
      progress: stats.totalAgents > 0
        ? (stats.agentsOnline / stats.totalAgents) * 100
        : 0,
    },
    {
      label: 'Average Quality Score',
      value: (stats.avgQualityScore * 100).toFixed(1),
      unit: '%',
      icon: <TrendingUpIcon />,
      color: theme.palette.info.main,
      progress: stats.avgQualityScore * 100,
    },
    {
      label: 'Cost Efficiency',
      value: stats.costSavedToday > 0 ? stats.costSavedToday.toFixed(0) : '0',
      unit: '$',
      icon: <CostIcon />,
      color: theme.palette.warning.main,
      progress: Math.min((stats.costSavedToday / 5000) * 100, 100), // Assuming $5000 as max
    },
  ];

  return (
    <Box>
      <Grid container spacing={2}>
        {metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Box
              sx={{
                p: 2,
                border: `1px solid ${alpha(metric.color, 0.2)}`,
                borderRadius: 2,
                backgroundColor: alpha(metric.color, 0.05),
              }}
            >
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                <Box display="flex" alignItems="center">
                  <Box
                    sx={{
                      backgroundColor: alpha(metric.color, 0.1),
                      borderRadius: '50%',
                      padding: 1,
                      color: metric.color,
                      mr: 1,
                    }}
                  >
                    {metric.icon}
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    {metric.label}
                  </Typography>
                </Box>
                <Typography variant="h6" color={metric.color} fontWeight="bold">
                  {metric.value}{metric.unit}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={metric.progress}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: alpha(metric.color, 0.1),
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: metric.color,
                  },
                }}
              />
            </Box>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
