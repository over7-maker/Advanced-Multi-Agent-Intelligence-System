import {
    Add as AddIcon,
    Assessment as AssessmentIcon,
    Group as GroupIcon,
    Notifications as NotificationsIcon,
    Schedule as ScheduleIcon,
    Settings as SettingsIcon,
    TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import {
    alpha,
    Box,
    Button,
    Card,
    CardContent,
    Container,
    Fab,
    Grid,
    IconButton,
    Paper,
    Typography,
    useTheme,
} from '@mui/material';
import { AnimatePresence, motion } from 'framer-motion';
import React, { useEffect, useState } from 'react';

import { apiService } from '../../services/api';
import { websocketService } from '../../services/websocket';
import { Agent, AgentSpecialty, WorkflowExecution } from '../../types/agent';
import { AgentStatusGrid } from './AgentStatusGrid';
import { PerformanceMetrics } from './PerformanceMetrics';
import { RecentActivity } from './RecentActivity';
import { WorkflowCard } from './WorkflowCard';

interface DashboardProps {
  onCreateWorkflow: () => void;
  onWorkflowSelect?: (execution: WorkflowExecution) => void;
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

const Dashboard: React.FC<DashboardProps> = ({ onCreateWorkflow, onWorkflowSelect }) => {
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
    
    // Connect WebSocket for real-time updates
    websocketService.connect();
    
    // Subscribe to real-time updates
    const unsubscribeWorkflow = websocketService.on('workflow_update', (data: any) => {
      if (data.executionId) {
        setActiveExecutions((prev) =>
          prev.map((exec) =>
            exec.executionId === data.executionId
              ? { ...exec, ...data }
              : exec
          )
        );
      }
    });

    const unsubscribeAgent = websocketService.on('agent_update', (data: any) => {
      if (data.id) {
        setAgents((prev) =>
          prev.map((agent) =>
            agent.id === data.id ? { ...agent, ...data } : agent
          )
        );
      }
    });

    const unsubscribeStats = websocketService.on('stats_update', (data: any) => {
      setStats((prev) => ({ ...prev, ...data }));
    });

    // Fallback polling if WebSocket not available
    const interval = setInterval(loadDashboardData, 10000);
    
    return () => {
      clearInterval(interval);
      unsubscribeWorkflow();
      unsubscribeAgent();
      unsubscribeStats();
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load data from API
      const [agentsResponse, tasksResponse] = await Promise.all([
        apiService.listAgents(),
        apiService.listTasks({ limit: 100 }),
      ]);

      // Calculate stats from API data
      const agents = agentsResponse.agents || [];
      const tasks = tasksResponse.tasks || [];
      const activeTasks = tasks.filter((t: any) => t.status === 'in_progress' || t.status === 'executing');
      const completedToday = tasks.filter((t: any) => {
        if (!t.completed_at) return false;
        const completed = new Date(t.completed_at);
        const today = new Date();
        return completed.toDateString() === today.toDateString();
      });

      const onlineAgents = agents.filter((a: any) => a.status === 'active' || a.status === 'busy');
      const avgQuality = agents.length > 0
        ? agents.reduce((sum: number, a: any) => sum + (a.qualityScore || 0.9), 0) / agents.length
        : 0.92;

      setStats({
        totalWorkflows: 156, // TODO: Get from workflows API
        activeWorkflows: activeTasks.length,
        completedToday: completedToday.length,
        agentsOnline: onlineAgents.length,
        totalAgents: agents.length,
        avgQualityScore: avgQuality,
        costSavedToday: 2840.50, // TODO: Calculate from actual data
        tasksCompletedToday: completedToday.length,
      });

      // Convert tasks to workflow executions format
      const executions: WorkflowExecution[] = activeTasks.slice(0, 10).map((task: any, index: number) => ({
        executionId: task.id || `exec_${index}`,
        workflowId: task.workflow_id || `workflow_${index}`,
        status: task.status === 'in_progress' ? 'executing' : task.status,
        progressPercentage: task.progress || Math.floor(Math.random() * 100),
        tasksCompleted: task.completed_tasks || 0,
        tasksInProgress: task.in_progress_tasks || 1,
        tasksPending: task.pending_tasks || 0,
        estimatedRemainingHours: task.estimated_hours || 0.5,
        overallHealth: 'healthy',
        currentPhase: task.current_phase || 'processing',
        startedAt: task.created_at ? new Date(task.created_at) : new Date(),
      }));

      setActiveExecutions(executions);

      // Convert API agents to frontend format
      const formattedAgents: Agent[] = agents.slice(0, 20).map((agent: any) => ({
        id: agent.id,
        specialty: agent.specialty || AgentSpecialty.ACADEMIC_RESEARCHER,
        status: agent.status || 'idle',
        currentTasks: agent.current_tasks || [],
        maxConcurrentTasks: agent.max_concurrent_tasks || 3,
        capabilities: {
          skills: agent.capabilities?.skills || [],
          tools: agent.capabilities?.tools || [],
          avgTaskDuration: agent.capabilities?.avg_task_duration || 1.5,
          maxParallelTasks: agent.capabilities?.max_parallel_tasks || 3,
          qualityScore: agent.quality_score || 0.9,
          costPerHour: agent.cost_per_hour || 0.15,
        },
        loadPercentage: agent.load_percentage || 0,
        successRate: agent.success_rate || 0.9,
        avgCompletionTime: agent.avg_completion_time || 1.3,
        qualityScore: agent.quality_score || 0.9,
      }));

      setAgents(formattedAgents);
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Fallback to mock data if API fails
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
          startedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
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
          startedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
        },
      ];
      
      setActiveExecutions(mockExecutions);
      setAgents([]);
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
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
                      <Box 
                        onClick={() => onWorkflowSelect?.(execution)}
                        sx={{ cursor: 'pointer' }}
                      >
                        <WorkflowCard execution={execution} />
                      </Box>
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
