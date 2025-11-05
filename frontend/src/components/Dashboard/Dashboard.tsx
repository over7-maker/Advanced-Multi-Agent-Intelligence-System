import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  Button,
  IconButton,
  Fab,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  Group as GroupIcon,
  Assessment as AssessmentIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

import { WorkflowExecution, Agent } from '../../types/agent';
import { WorkflowCard } from './WorkflowCard';
import { AgentStatusGrid } from './AgentStatusGrid';
import { PerformanceMetrics } from './PerformanceMetrics';
import { RecentActivity } from './RecentActivity';

interface DashboardProps {
  onCreateWorkflow: () => void;
}

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

const Dashboard: React.FC<DashboardProps> = ({ onCreateWorkflow }) => {
  const theme = useTheme();
  const [stats, setStats] = useState<DashboardStats>({
    totalWorkflows: 0,
    activeWorkflows: 0,
    completedToday: 0,
    agentsOnline: 0,
    totalAgents: 0,
    avgQualityScore: 0,
    costSavedToday: 0,
    tasksCompletedToday: 0,
  });
  
  const [activeExecutions, setActiveExecutions] = useState<WorkflowExecution[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load dashboard data
    loadDashboardData();
    
    // Set up real-time updates
    const interval = setInterval(loadDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      // In real implementation, these would be API calls
      // For now, simulate with realistic data
      
      setStats({
        totalWorkflows: 156,
        activeWorkflows: 8,
        completedToday: 23,
        agentsOnline: 45,
        totalAgents: 52,
        avgQualityScore: 0.92,
        costSavedToday: 2840.50,
        tasksCompletedToday: 89,
      });
      
      // Simulate active executions
      const mockExecutions: WorkflowExecution[] = [
        {
          executionId: "exec_001",
          workflowId: "workflow_market_analysis",
          status: "executing",
          progressPercentage: 75,
          tasksCompleted: 6,
          tasksInProgress: 2,
          tasksPending: 0,
          estimatedRemainingHours: 0.5,
          overallHealth: "healthy",
          currentPhase: "content_creation_and_formatting",
          startedAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
        },
        {
          executionId: "exec_002",
          workflowId: "workflow_competitor_intel",
          status: "executing",
          progressPercentage: 40,
          tasksCompleted: 3,
          tasksInProgress: 4,
          tasksPending: 1,
          estimatedRemainingHours: 1.2,
          overallHealth: "healthy",
          currentPhase: "data_analysis_and_modeling",
          startedAt: new Date(Date.now() - 1 * 60 * 60 * 1000), // 1 hour ago
        },
      ];
      
      setActiveExecutions(mockExecutions);
      
      // Simulate agent data
      setAgents([
        {
          id: "agent_001",
          specialty: "academic_researcher" as any,
          status: "busy",
          currentTasks: ["task_001", "task_002"],
          maxConcurrentTasks: 3,
          capabilities: {
            skills: ["academic_search", "citation_management"],
            tools: ["google_scholar", "arxiv_search"],
            avgTaskDuration: 1.5,
            maxParallelTasks: 3,
            qualityScore: 0.95,
            costPerHour: 0.15,
          },
          loadPercentage: 67,
          successRate: 0.94,
          avgCompletionTime: 1.3,
          qualityScore: 0.95,
        },
        // Add more mock agents...
      ]);
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setLoading(false);
    }
  };

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    trend?: number;
  }> = ({ title, value, icon, color, trend }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card 
        sx={{ 
          background: `linear-gradient(135deg, ${alpha(color, 0.1)} 0%, ${alpha(color, 0.05)} 100%)`,
          border: `1px solid ${alpha(color, 0.2)}`,
          height: '100%'
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography color="textSecondary" gutterBottom variant="body2">
                {title}
              </Typography>
              <Typography variant="h4" component="div" color={color}>
                {typeof value === 'number' && value > 1000 ? 
                  `${(value / 1000).toFixed(1)}k` : value}
              </Typography>
              {trend !== undefined && (
                <Typography 
                  variant="caption" 
                  color={trend >= 0 ? "success.main" : "error.main"}
                  display="flex"
                  alignItems="center"
                >
                  <TrendingUpIcon fontSize="small" sx={{ mr: 0.5 }} />
                  {trend >= 0 ? '+' : ''}{trend}%
                </Typography>
              )}
            </Box>
            <Box 
              sx={{ 
                backgroundColor: alpha(color, 0.1),
                borderRadius: '50%',
                padding: 1.5,
                color: color 
              }}
            >
              {icon}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" height="60vh">
          <Typography>Loading dashboard...</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h3" component="h1" gutterBottom>
            🤖 AMAS Intelligence Dashboard
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Advanced Multi-Agent Intelligence System - Autonomous Operation Center
          </Typography>
        </Box>
        <Box>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
            onClick={onCreateWorkflow}
            sx={{ mr: 2 }}
          >
            New Workflow
          </Button>
          <IconButton color="inherit">
            <SettingsIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Key Performance Stats */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Workflows"
            value={stats.activeWorkflows}
            icon={<AssessmentIcon />}
            color={theme.palette.primary.main}
            trend={12}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Agents Online"
            value={`${stats.agentsOnline}/${stats.totalAgents}`}
            icon={<GroupIcon />}
            color={theme.palette.success.main}
            trend={8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Quality Score"
            value={`${(stats.avgQualityScore * 100).toFixed(1)}%`}
            icon={<TrendingUpIcon />}
            color={theme.palette.info.main}
            trend={3}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Cost Saved Today"
            value={`$${stats.costSavedToday.toLocaleString()}`}
            icon={<ScheduleIcon />}
            color={theme.palette.warning.main}
            trend={25}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Active Workflows */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom display="flex" alignItems="center">
              <AssessmentIcon sx={{ mr: 1 }} />
              Active Workflows
            </Typography>
            
            <AnimatePresence>
              {activeExecutions.length > 0 ? (
                <Box>
                  {activeExecutions.map((execution, index) => (
                    <motion.div
                      key={execution.executionId}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <WorkflowCard execution={execution} />
                    </motion.div>
                  ))}
                </Box>
              ) : (
                <Box 
                  display="flex" 
                  flexDirection="column" 
                  alignItems="center" 
                  py={6}
                  color="text.secondary"
                >
                  <AssessmentIcon sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
                  <Typography variant="h6" gutterBottom>
                    No Active Workflows
                  </Typography>
                  <Typography variant="body2" color="textSecondary" mb={2}>
                    Start a new workflow to see real-time progress here
                  </Typography>
                  <Button 
                    variant="outlined" 
                    startIcon={<AddIcon />}
                    onClick={onCreateWorkflow}
                  >
                    Create Workflow
                  </Button>
                </Box>
              )}
            </AnimatePresence>
          </Paper>
        </Grid>

        {/* Agent Status */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom display="flex" alignItems="center">
              <GroupIcon sx={{ mr: 1 }} />
              Agent Status
            </Typography>
            <AgentStatusGrid agents={agents} />
          </Paper>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom display="flex" alignItems="center">
              <TrendingUpIcon sx={{ mr: 1 }} />
              Performance Metrics
            </Typography>
            <PerformanceMetrics stats={stats} />
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom display="flex" alignItems="center">
              <NotificationsIcon sx={{ mr: 1 }} />
              Recent Activity
            </Typography>
            <RecentActivity />
          </Paper>
        </Grid>
      </Grid>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 24, right: 24 }}
        onClick={onCreateWorkflow}
      >
        <AddIcon />
      </Fab>
    </Container>
  );
};

export default Dashboard;
