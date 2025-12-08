import {
    Chat as ChatIcon,
    CheckCircle as CompletedIcon,
    Error as ErrorIcon,
    ExpandLess as ExpandLessIcon,
    ExpandMore as ExpandMoreIcon,
    Group as GroupIcon,
    PlayArrow as PlayIcon,
    Schedule as ScheduleIcon,
    Visibility as ViewIcon,
} from '@mui/icons-material';
import {
    Timeline,
    TimelineConnector,
    TimelineContent,
    TimelineDot,
    TimelineItem,
    TimelineSeparator,
} from '@mui/lab';
import {
    Alert,
    alpha,
    Avatar,
    Box,
    Card,
    CardContent,
    Chip,
    Collapse,
    Grid,
    IconButton,
    LinearProgress,
    Paper,
    Typography,
    useTheme
} from '@mui/material';
import { AnimatePresence, motion } from 'framer-motion';
import React, { useEffect, useState } from 'react';

import { websocketService } from '../../services/websocket';
import { AgentSpecialty, SubTask, TaskStatus, WorkflowExecution } from '../../types/agent';

interface ProgressTrackerProps {
  execution: WorkflowExecution;
  realTimeUpdates?: boolean;
}

interface AgentActivity {
  agentId: string;
  agentName: string;
  specialty: string;
  activity: string;
  timestamp: Date;
  type: 'started' | 'progress' | 'completed' | 'help_request' | 'communication';
  details?: Record<string, unknown>;
}

interface QualityCheckpoint {
  id: string;
  name: string;
  status: 'pending' | 'in_progress' | 'passed' | 'failed';
  score?: number;
  threshold: number;
  details?: string;
  checkedAt?: Date;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  execution,
  realTimeUpdates = true
}) => {
  const theme = useTheme();
  const [currentExecution, setCurrentExecution] = useState<WorkflowExecution>(execution);
  const [subTasks, setSubTasks] = useState<SubTask[]>([]);
  const [agentActivities, setAgentActivities] = useState<AgentActivity[]>([]);
  const [qualityCheckpoints, setQualityCheckpoints] = useState<QualityCheckpoint[]>([]);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['progress']));
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  
  useEffect(() => {
    setCurrentExecution(execution);
  }, [execution]);
  
  useEffect(() => {
    loadExecutionDetails();
    
    if (realTimeUpdates) {
      websocketService.connect();
      const unsubscribe = websocketService.on('workflow_update', (data: any) => {
        if (data.executionId === execution.executionId || data.id === execution.executionId) {
          setCurrentExecution((prev) => ({
            ...prev,
            ...data,
            progressPercentage: data.progress !== undefined ? data.progress : prev.progressPercentage,
            status: data.status || prev.status,
            tasksCompleted: data.tasksCompleted !== undefined ? data.tasksCompleted : prev.tasksCompleted,
            tasksInProgress: data.tasksInProgress !== undefined ? data.tasksInProgress : prev.tasksInProgress,
            tasksPending: data.tasksPending !== undefined ? data.tasksPending : prev.tasksPending,
          }));
        }
      });
      
      const interval = setInterval(loadExecutionDetails, 2000); // Update every 2 seconds
      return () => {
        clearInterval(interval);
        unsubscribe();
      };
    }
  }, [execution.executionId, realTimeUpdates]);
  
  const loadExecutionDetails = async () => {
    try {
      // Simulate loading detailed execution data
      // In real implementation, this would be WebSocket or polling API
      
      const mockSubTasks: SubTask[] = [
        {
          id: "task_001",
          title: "Web Intelligence Gathering",
          description: "Gather competitive intelligence from web sources",
          assignedAgent: AgentSpecialty.WEB_INTELLIGENCE,
          estimatedDurationHours: 1.0,
          priority: 8,
          dependsOn: [],
          status: TaskStatus.COMPLETED,
          startedAt: new Date(Date.now() - 90 * 60 * 1000),
          completedAt: new Date(Date.now() - 30 * 60 * 1000),
          outputSummary: "Successfully gathered data from 15 competitor websites",
          successCriteria: ["Minimum 10 sources", "Recent data priority"],
          qualityCheckpoints: ["Source credibility", "Data accuracy"]
        },
        {
          id: "task_002",
          title: "Data Analysis & Modeling",
          description: "Process gathered data and identify trends",
          assignedAgent: AgentSpecialty.DATA_ANALYST,
          estimatedDurationHours: 1.5,
          priority: 7,
          dependsOn: ["task_001"],
          status: TaskStatus.IN_PROGRESS,
          startedAt: new Date(Date.now() - 30 * 60 * 1000),
          successCriteria: ["Statistical significance validated", "Trends identified"],
          qualityCheckpoints: ["Data quality", "Analysis methodology"]
        },
        {
          id: "task_003",
          title: "Graphics Design & Visualization",
          description: "Create professional charts and infographics",
          assignedAgent: AgentSpecialty.GRAPHICS_DESIGNER,
          estimatedDurationHours: 1.0,
          priority: 6,
          dependsOn: ["task_002"],
          status: TaskStatus.READY,
          successCriteria: ["Professional design quality", "Data accuracy in visuals"],
          qualityCheckpoints: ["Visual consistency", "Brand alignment"]
        },
        {
          id: "task_004",
          title: "Executive Summary Writing",
          description: "Create executive-ready content and recommendations",
          assignedAgent: AgentSpecialty.CONTENT_WRITER,
          estimatedDurationHours: 1.2,
          priority: 6,
          dependsOn: ["task_002"],
          status: TaskStatus.PENDING,
          successCriteria: ["Professional writing standards", "Actionable recommendations"],
          qualityCheckpoints: ["Grammar and style", "Technical accuracy"]
        },
        {
          id: "task_005",
          title: "Fact Checking & Validation",
          description: "Verify all claims and validate sources",
          assignedAgent: AgentSpecialty.FACT_CHECKER,
          estimatedDurationHours: 0.8,
          priority: 9,
          dependsOn: ["task_001", "task_002", "task_003", "task_004"],
          status: TaskStatus.PENDING,
          successCriteria: ["All claims verified", "Sources validated"],
          qualityCheckpoints: ["Accuracy assessment", "Bias detection"]
        }
      ];
      
      setSubTasks(mockSubTasks);
      
      // Simulate agent activities
      const mockActivities: AgentActivity[] = [
        {
          agentId: "agent_web_001",
          agentName: "Web Intelligence Agent 001",
          specialty: "Web Intelligence Gatherer",
          activity: "Completed competitive analysis of 5 major competitors",
          timestamp: new Date(Date.now() - 5 * 60 * 1000),
          type: 'completed',
          details: { sourcesGathered: 15, credibilityScore: 0.91 }
        },
        {
          agentId: "agent_data_001", 
          agentName: "Data Analysis Agent 001",
          specialty: "Data Analyst",
          activity: "Processing competitive pricing data - 60% complete",
          timestamp: new Date(Date.now() - 2 * 60 * 1000),
          type: 'progress',
          details: { progressPercentage: 60, trendsIdentified: 3 }
        },
        {
          agentId: "agent_data_001",
          agentName: "Data Analysis Agent 001", 
          specialty: "Data Analyst",
          activity: "Requested help from Financial Analyzer for pricing model validation",
          timestamp: new Date(Date.now() - 1 * 60 * 1000),
          type: 'help_request',
          details: { helpType: 'financial_modeling', urgency: 'normal' }
        }
      ];
      
      setAgentActivities(mockActivities);
      
      // Simulate quality checkpoints
      const mockCheckpoints: QualityCheckpoint[] = [
        {
          id: "checkpoint_001",
          name: "Research Completeness Gate",
          status: 'passed',
          score: 0.92,
          threshold: 0.85,
          details: "All research requirements satisfied",
          checkedAt: new Date(Date.now() - 25 * 60 * 1000)
        },
        {
          id: "checkpoint_002",
          name: "Data Analysis Accuracy Gate",
          status: 'in_progress',
          threshold: 0.90,
          details: "Statistical validation in progress"
        },
        {
          id: "checkpoint_003",
          name: "Output Quality Gate",
          status: 'pending',
          threshold: 0.92,
          details: "Waiting for content completion"
        }
      ];
      
      setQualityCheckpoints(mockCheckpoints);
      setLastUpdate(new Date());
      
    } catch (error) {
      console.error('Error loading execution details:', error);
    }
  };
  
  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };
  
  const getTaskStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return <CompletedIcon color="success" />;
      case TaskStatus.IN_PROGRESS:
        return <PlayIcon color="primary" />;
      case TaskStatus.FAILED:
        return <ErrorIcon color="error" />;
      default:
        return <ScheduleIcon color="action" />;
    }
  };
  
  const getTaskStatusColor = (status: TaskStatus): 'success' | 'primary' | 'error' | 'warning' | 'inherit' => {
    switch (status) {
      case TaskStatus.COMPLETED: return 'success';
      case TaskStatus.IN_PROGRESS: return 'primary';
      case TaskStatus.FAILED: return 'error';
      case TaskStatus.BLOCKED: return 'warning';
      default: return 'inherit';
    }
  };
  
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'completed': return <CompletedIcon color="success" />;
      case 'started': return <PlayIcon color="primary" />;
      case 'progress': return <PlayIcon color="info" />;
      case 'help_request': return <GroupIcon color="warning" />;
      case 'communication': return <ChatIcon color="secondary" />;
      default: return <ScheduleIcon color="action" />;
    }
  };

  return (
    <Box>
      {/* Real-time Status Header */}
      <Paper sx={{ p: 2, mb: 3, backgroundColor: alpha(theme.palette.primary.main, 0.02) }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6">Live Progress Tracking</Typography>
            <Typography variant="caption" color="textSecondary">
              Execution: {currentExecution.executionId} • Last updated: {lastUpdate.toLocaleTimeString()}
            </Typography>
          </Box>
          
          <Box textAlign="right">
            <Typography variant="h4" color="primary.main" fontWeight="bold">
              {currentExecution.progressPercentage.toFixed(1)}%
            </Typography>
            <Typography variant="caption" color="textSecondary">
              {currentExecution.currentPhase.replace('_', ' ')}
            </Typography>
          </Box>
        </Box>
        
        <LinearProgress 
          variant="determinate" 
          value={currentExecution.progressPercentage}
          sx={{ 
            mt: 2, 
            height: 8, 
            borderRadius: 4,
            backgroundColor: alpha(theme.palette.primary.main, 0.1)
          }} 
        />
      </Paper>

      <Grid container spacing={3}>
        {/* Task Progress Timeline */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box 
              display="flex" 
              justifyContent="space-between" 
              alignItems="center" 
              mb={2}
              onClick={() => toggleSection('tasks')}
              sx={{ cursor: 'pointer' }}
            >
              <Typography variant="h6" display="flex" alignItems="center">
                <ScheduleIcon sx={{ mr: 1 }} />
                Task Progress ({subTasks.filter(t => t.status === TaskStatus.COMPLETED).length}/{subTasks.length})
              </Typography>
              <IconButton>
                {expandedSections.has('tasks') ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
            
            <Collapse in={expandedSections.has('tasks')}>
              <Timeline>
                {subTasks.map((task, index) => (
                  <TimelineItem key={task.id}>
                    <TimelineSeparator>
                      <TimelineDot 
                        color={getTaskStatusColor(task.status)}
                        variant={task.status === TaskStatus.COMPLETED ? "filled" : "outlined"}
                      >
                        {getTaskStatusIcon(task.status)}
                      </TimelineDot>
                      {index < subTasks.length - 1 && <TimelineConnector />}
                    </TimelineSeparator>
                    
                    <TimelineContent>
                      <Box mb={2}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {task.title}
                        </Typography>
                        
                        <Box display="flex" alignItems="center" gap={1} my={1}>
                          <Chip 
                            size="small" 
                            label={task.status.replace('_', ' ').toUpperCase()}
                            color={
                              (() => {
                                const color = getTaskStatusColor(task.status);
                                return color === 'inherit' ? 'default' : color as 'success' | 'primary' | 'error' | 'warning' | 'default';
                              })()
                            }
                          />
                          <Chip 
                            size="small" 
                            label={task.assignedAgent.replace('_', ' ')}
                            variant="outlined"
                          />
                          <Typography variant="caption" color="textSecondary">
                            {task.estimatedDurationHours}h estimated
                          </Typography>
                        </Box>
                        
                        <Typography variant="caption" color="textSecondary" display="block">
                          {task.description}
                        </Typography>
                        
                        {task.outputSummary && (
                          <Typography variant="caption" display="block" mt={1} 
                            sx={{ 
                              p: 1, 
                              backgroundColor: alpha(theme.palette.success.main, 0.1),
                              borderRadius: 1,
                              border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`
                            }}
                          >
                            ✅ {task.outputSummary}
                          </Typography>
                        )}
                        
                        {task.dependsOn.length > 0 && (
                          <Typography variant="caption" color="textSecondary" display="block" mt={0.5}>
                            Depends on: {task.dependsOn.join(', ')}
                          </Typography>
                        )}
                        
                        {/* Task timing */}
                        {task.startedAt && (
                          <Typography variant="caption" color="textSecondary" display="block" mt={0.5}>
                            Started: {new Date(task.startedAt).toLocaleTimeString()}
                            {task.completedAt && 
                              ` • Completed: ${new Date(task.completedAt).toLocaleTimeString()}`
                            }
                          </Typography>
                        )}
                      </Box>
                    </TimelineContent>
                  </TimelineItem>
                ))}
              </Timeline>
            </Collapse>
          </Paper>
        </Grid>
        
        {/* Agent Activity Feed */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box 
              display="flex" 
              justifyContent="space-between" 
              alignItems="center" 
              mb={2}
              onClick={() => toggleSection('activity')}
              sx={{ cursor: 'pointer' }}
            >
              <Typography variant="h6" display="flex" alignItems="center">
                <ChatIcon sx={{ mr: 1 }} />
                Agent Activity Feed
              </Typography>
              <IconButton>
                {expandedSections.has('activity') ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
            
            <Collapse in={expandedSections.has('activity')}>
              <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                <AnimatePresence>
                  {agentActivities.map((activity) => (
                    <motion.div
                      key={`${activity.agentId}_${activity.timestamp.getTime()}`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Box 
                        display="flex" 
                        alignItems="flex-start" 
                        mb={2}
                        p={2}
                        sx={{
                          borderRadius: 2,
                          backgroundColor: alpha(
                            activity.type === 'completed' ? theme.palette.success.main :
                            activity.type === 'help_request' ? theme.palette.warning.main :
                            theme.palette.info.main, 0.05
                          ),
                          border: `1px solid ${alpha(
                            activity.type === 'completed' ? theme.palette.success.main :
                            activity.type === 'help_request' ? theme.palette.warning.main :
                            theme.palette.info.main, 0.2
                          )}`
                        }}
                      >
                        <Avatar sx={{ width: 32, height: 32, mr: 2 }}>
                          {getActivityIcon(activity.type)}
                        </Avatar>
                        
                        <Box flex={1}>
                          <Typography variant="subtitle2" fontWeight="bold">
                            {activity.agentName}
                          </Typography>
                          <Typography variant="caption" color="textSecondary" display="block">
                            {activity.specialty} • {activity.timestamp.toLocaleTimeString()}
                          </Typography>
                          <Typography variant="body2" mt={0.5}>
                            {activity.activity}
                          </Typography>
                          
                          {activity.details && (
                            <Box mt={1}>
                              {activity.type === 'completed' && 
                               typeof activity.details.sourcesGathered === 'number' && (
                                <Chip size="small" label={`${activity.details.sourcesGathered} sources`} />
                              )}
                              {activity.type === 'progress' && 
                               typeof activity.details.progressPercentage === 'number' && (
                                <LinearProgress 
                                  variant="determinate" 
                                  value={activity.details.progressPercentage as number}
                                  sx={{ width: 100, mr: 1, display: 'inline-block' }}
                                />
                              )}
                            </Box>
                          )}
                        </Box>
                      </Box>
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                {agentActivities.length === 0 && (
                  <Box textAlign="center" py={4} color="text.secondary">
                    <ChatIcon sx={{ fontSize: 48, opacity: 0.3, mb: 2 }} />
                    <Typography variant="body2">
                      No agent activity yet
                    </Typography>
                  </Box>
                )}
              </Box>
            </Collapse>
          </Paper>
        </Grid>
        
        {/* Quality Checkpoints */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box 
              display="flex" 
              justifyContent="space-between" 
              alignItems="center" 
              mb={2}
              onClick={() => toggleSection('quality')}
              sx={{ cursor: 'pointer' }}
            >
              <Typography variant="h6" display="flex" alignItems="center">
                <ViewIcon sx={{ mr: 1 }} />
                Quality Checkpoints
              </Typography>
              <IconButton>
                {expandedSections.has('quality') ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
            
            <Collapse in={expandedSections.has('quality')}>
              <Grid container spacing={2}>
                {qualityCheckpoints.map((checkpoint) => (
                  <Grid item xs={12} md={4} key={checkpoint.id}>
                    <Card 
                      sx={{
                        border: `1px solid ${alpha(
                          checkpoint.status === 'passed' ? theme.palette.success.main :
                          checkpoint.status === 'failed' ? theme.palette.error.main :
                          checkpoint.status === 'in_progress' ? theme.palette.primary.main :
                          theme.palette.grey[300], 0.3
                        )}`,
                        backgroundColor: alpha(
                          checkpoint.status === 'passed' ? theme.palette.success.main :
                          checkpoint.status === 'failed' ? theme.palette.error.main :
                          checkpoint.status === 'in_progress' ? theme.palette.primary.main :
                          theme.palette.grey[300], 0.05
                        )
                      }}
                    >
                      <CardContent sx={{ p: 2 }}>
                        <Box display="flex" alignItems="center" mb={1}>
                          {checkpoint.status === 'passed' && <CompletedIcon color="success" sx={{ mr: 1 }} />}
                          {checkpoint.status === 'failed' && <ErrorIcon color="error" sx={{ mr: 1 }} />}
                          {checkpoint.status === 'in_progress' && <PlayIcon color="primary" sx={{ mr: 1 }} />}
                          {checkpoint.status === 'pending' && <ScheduleIcon color="action" sx={{ mr: 1 }} />}
                          
                          <Typography variant="subtitle2" fontWeight="bold">
                            {checkpoint.name}
                          </Typography>
                        </Box>
                        
                        <Typography variant="caption" color="textSecondary" display="block" mb={1}>
                          {checkpoint.details}
                        </Typography>
                        
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="caption">
                            Threshold: {(checkpoint.threshold * 100).toFixed(0)}%
                          </Typography>
                          
                          {checkpoint.score && (
                            <Typography 
                              variant="caption" 
                              fontWeight="bold"
                              color={checkpoint.score >= checkpoint.threshold ? 'success.main' : 'error.main'}
                            >
                              Score: {(checkpoint.score * 100).toFixed(0)}%
                            </Typography>
                          )}
                        </Box>
                        
                        {checkpoint.checkedAt && (
                          <Typography variant="caption" color="textSecondary" display="block" mt={0.5}>
                            Checked: {checkpoint.checkedAt.toLocaleTimeString()}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Collapse>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Health Status Alert */}
      {currentExecution.overallHealth !== 'healthy' && (
        <Alert 
          severity={currentExecution.overallHealth === 'warning' ? 'warning' : 'error'}
          sx={{ mt: 2 }}
        >
          <Typography fontWeight="bold">
            Workflow Health: {currentExecution.overallHealth.toUpperCase()}
          </Typography>
          {currentExecution.overallHealth === 'warning' && 
            "Some tasks are running longer than expected. Monitoring for potential issues."
          }
          {currentExecution.overallHealth === 'degraded' && 
            "Multiple agents experiencing issues. System is attempting automatic recovery."
          }
        </Alert>
      )}
    </Box>
  );
};

export default ProgressTracker;
