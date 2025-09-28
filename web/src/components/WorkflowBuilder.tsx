/**
 * AMAS Workflow Builder Component
 * 
 * Visual workflow design and monitoring interface:
 * - Drag-and-drop workflow creation
 * - Real-time workflow execution visualization
 * - Node status monitoring and progress tracking
 * - Interactive workflow editing and management
 * - Performance metrics and analytics
 * 
 * Provides intuitive visual interface for complex workflow orchestration.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  LinearProgress,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Tooltip,
  Paper,
  CircularProgress
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Pause,
  Refresh,
  Add,
  Delete,
  Edit,
  Visibility,
  Timeline,
  AccountTree,
  Speed,
  CheckCircle,
  Error,
  Warning,
  Schedule,
  Memory,
  Settings
} from '@mui/icons-material';

// Services
import { AMASApiService } from '../services/api';
import { useRealTimeSystem } from '../hooks/useRealTimeUpdates';

// Types
interface WorkflowNode {
  node_id: string;
  node_type: string;
  name: string;
  description: string;
  agent_type?: string;
  action?: string;
  status: string;
  position: { x: number; y: number };
  result?: any;
  error?: string;
  execution_time?: number;
}

interface WorkflowEdge {
  edge_id: string;
  from_node: string;
  to_node: string;
  edge_type: string;
  condition?: string;
}

interface WorkflowDefinition {
  workflow_id: string;
  name: string;
  description: string;
  version: string;
  nodes: Record<string, WorkflowNode>;
  edges: Record<string, WorkflowEdge>;
  timeout_minutes?: number;
}

interface WorkflowExecution {
  execution_id: string;
  workflow_id: string;
  status: string;
  progress: {
    total_nodes: number;
    completed_nodes: number;
    failed_nodes: number;
    current_nodes: string[];
    completion_percentage: number;
  };
  started_at: string;
  execution_time: number;
  initiated_by: string;
  error?: string;
  node_results: Record<string, any>;
}

const WorkflowBuilder: React.FC = () => {
  // State
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);
  const [activeExecutions, setActiveExecutions] = useState<WorkflowExecution[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowDefinition | null>(null);
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Dialog states
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false);
  const [executionContext, setExecutionContext] = useState<Record<string, any>>({});

  // Services
  const apiService = new AMASApiService();
  const { systemStatus, connectionStatus } = useRealTimeSystem();

  // Load workflows and executions
  useEffect(() => {
    loadWorkflowData();
    
    // Refresh every 30 seconds
    const interval = setInterval(loadWorkflowData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadWorkflowData = async () => {
    try {
      setLoading(true);
      
      // Load available workflows and active executions
      const [workflowsData, executionsData] = await Promise.all([
        apiService.getWorkflows(),
        apiService.getActiveWorkflowExecutions()
      ]);
      
      setWorkflows(workflowsData || []);
      setActiveExecutions(executionsData || []);
      setError(null);
      
    } catch (err) {
      console.error('Failed to load workflow data:', err);
      setError('Failed to load workflow data');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteWorkflow = async (workflowId: string, context: Record<string, any>) => {
    try {
      const result = await apiService.executeWorkflow(workflowId, context);
      
      if (result.execution_id) {
        // Refresh executions to show new execution
        await loadWorkflowData();
        
        // Show success message
        console.log(`Workflow execution started: ${result.execution_id}`);
      }
      
    } catch (err) {
      console.error('Failed to execute workflow:', err);
      setError('Failed to execute workflow');
    }
  };

  const handleCancelExecution = async (executionId: string) => {
    try {
      await apiService.cancelWorkflowExecution(executionId);
      await loadWorkflowData();
    } catch (err) {
      console.error('Failed to cancel execution:', err);
      setError('Failed to cancel execution');
    }
  };

  const getNodeStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'running':
        return <CircularProgress size={20} />;
      case 'failed':
        return <Error color="error" />;
      case 'pending':
        return <Schedule color="disabled" />;
      case 'ready':
        return <PlayArrow color="primary" />;
      default:
        return <Memory color="disabled" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" color="primary">
          Workflow Orchestration
        </Typography>
        
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadWorkflowData}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => {/* TODO: Open workflow creation dialog */}}
          >
            Create Workflow
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Available Workflows */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Available Workflows
              </Typography>
              
              <List>
                {workflows.map((workflow) => (
                  <React.Fragment key={workflow.workflow_id}>
                    <ListItem>
                      <ListItemIcon>
                        <AccountTree color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={workflow.name}
                        secondary={`${Object.keys(workflow.nodes).length} nodes • Version ${workflow.version}`}
                      />
                      <Box display="flex" gap={1}>
                        <Tooltip title="View Workflow">
                          <IconButton
                            size="small"
                            onClick={() => setSelectedWorkflow(workflow)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Execute Workflow">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => {
                              setSelectedWorkflow(workflow);
                              setExecuteDialogOpen(true);
                            }}
                          >
                            <PlayArrow />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
                
                {workflows.length === 0 && (
                  <ListItem>
                    <ListItemText
                      primary="No workflows available"
                      secondary="Create a workflow to get started"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Active Executions */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Executions
              </Typography>
              
              <List>
                {activeExecutions.map((execution) => {
                  const workflow = workflows.find(w => w.workflow_id === execution.workflow_id);
                  
                  return (
                    <React.Fragment key={execution.execution_id}>
                      <ListItem>
                        <ListItemIcon>
                          {getNodeStatusIcon(execution.status)}
                        </ListItemIcon>
                        <ListItemText
                          primary={workflow?.name || execution.workflow_id}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                Status: <Chip 
                                  label={execution.status} 
                                  size="small" 
                                  color={getStatusColor(execution.status) as any}
                                />
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={execution.progress.completion_percentage}
                                sx={{ mt: 1, mb: 1 }}
                              />
                              <Typography variant="caption" color="textSecondary">
                                {execution.progress.completed_nodes}/{execution.progress.total_nodes} nodes completed
                                • {Math.round(execution.execution_time)}s runtime
                              </Typography>
                            </Box>
                          }
                        />
                        <Box display="flex" gap={1}>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => setSelectedExecution(execution)}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          {execution.status === 'running' && (
                            <Tooltip title="Cancel Execution">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleCancelExecution(execution.execution_id)}
                              >
                                <Stop />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  );
                })}
                
                {activeExecutions.length === 0 && (
                  <ListItem>
                    <ListItemText
                      primary="No active executions"
                      secondary="Execute a workflow to see progress here"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Workflow Details */}
        {selectedWorkflow && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Workflow Details: {selectedWorkflow.name}
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Workflow Information
                    </Typography>
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {selectedWorkflow.description}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Version:</strong> {selectedWorkflow.version}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Nodes:</strong> {Object.keys(selectedWorkflow.nodes).length}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Edges:</strong> {Object.keys(selectedWorkflow.edges).length}
                    </Typography>
                    {selectedWorkflow.timeout_minutes && (
                      <Typography variant="body2">
                        <strong>Timeout:</strong> {selectedWorkflow.timeout_minutes} minutes
                      </Typography>
                    )}
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Workflow Nodes
                    </Typography>
                    <List dense>
                      {Object.values(selectedWorkflow.nodes).map((node) => (
                        <ListItem key={node.node_id}>
                          <ListItemIcon>
                            {getNodeStatusIcon(node.status)}
                          </ListItemIcon>
                          <ListItemText
                            primary={node.name}
                            secondary={`${node.node_type} • ${node.agent_type || 'System'}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Execution Details */}
        {selectedExecution && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Execution Details: {selectedExecution.execution_id}
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2" gutterBottom>
                      Execution Status
                    </Typography>
                    <Box mb={2}>
                      <Chip 
                        label={selectedExecution.status} 
                        color={getStatusColor(selectedExecution.status) as any}
                        size="medium"
                      />
                    </Box>
                    <Typography variant="body2">
                      <strong>Started:</strong> {new Date(selectedExecution.started_at).toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Runtime:</strong> {Math.round(selectedExecution.execution_time)}s
                    </Typography>
                    <Typography variant="body2">
                      <strong>Initiated by:</strong> {selectedExecution.initiated_by}
                    </Typography>
                    {selectedExecution.error && (
                      <Alert severity="error" sx={{ mt: 2 }}>
                        {selectedExecution.error}
                      </Alert>
                    )}
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2" gutterBottom>
                      Progress Overview
                    </Typography>
                    <Box mb={2}>
                      <LinearProgress
                        variant="determinate"
                        value={selectedExecution.progress.completion_percentage}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                      <Typography variant="caption" color="textSecondary">
                        {selectedExecution.progress.completed_nodes}/{selectedExecution.progress.total_nodes} nodes completed
                      </Typography>
                    </Box>
                    
                    <Box display="flex" gap={2}>
                      <Box textAlign="center">
                        <Typography variant="h6" color="success.main">
                          {selectedExecution.progress.completed_nodes}
                        </Typography>
                        <Typography variant="caption">Completed</Typography>
                      </Box>
                      <Box textAlign="center">
                        <Typography variant="h6" color="primary.main">
                          {selectedExecution.progress.current_nodes.length}
                        </Typography>
                        <Typography variant="caption">Running</Typography>
                      </Box>
                      <Box textAlign="center">
                        <Typography variant="h6" color="error.main">
                          {selectedExecution.progress.failed_nodes}
                        </Typography>
                        <Typography variant="caption">Failed</Typography>
                      </Box>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2" gutterBottom>
                      Current Nodes
                    </Typography>
                    {selectedExecution.progress.current_nodes.length > 0 ? (
                      <List dense>
                        {selectedExecution.progress.current_nodes.map((nodeId) => {
                          const workflow = workflows.find(w => w.workflow_id === selectedExecution.workflow_id);
                          const node = workflow?.nodes[nodeId];
                          
                          return (
                            <ListItem key={nodeId}>
                              <ListItemIcon>
                                <CircularProgress size={16} />
                              </ListItemIcon>
                              <ListItemText
                                primary={node?.name || nodeId}
                                secondary={node?.agent_type || 'System'}
                              />
                            </ListItem>
                          );
                        })}
                      </List>
                    ) : (
                      <Typography variant="body2" color="textSecondary">
                        No nodes currently executing
                      </Typography>
                    )}
                  </Grid>
                </Grid>

                {/* Node Results */}
                {Object.keys(selectedExecution.node_results).length > 0 && (
                  <Box mt={3}>
                    <Typography variant="subtitle2" gutterBottom>
                      Node Results
                    </Typography>
                    <Grid container spacing={2}>
                      {Object.entries(selectedExecution.node_results).map(([nodeId, result]) => {
                        const workflow = workflows.find(w => w.workflow_id === selectedExecution.workflow_id);
                        const node = workflow?.nodes[nodeId];
                        
                        return (
                          <Grid item xs={12} md={6} key={nodeId}>
                            <Paper elevation={1} sx={{ p: 2 }}>
                              <Box display="flex" alignItems="center" mb={1}>
                                {getNodeStatusIcon(result.success ? 'completed' : 'failed')}
                                <Typography variant="subtitle2" sx={{ ml: 1 }}>
                                  {node?.name || nodeId}
                                </Typography>
                              </Box>
                              
                              {result.success ? (
                                <Typography variant="body2" color="success.main">
                                  ✓ Completed successfully
                                </Typography>
                              ) : (
                                <Typography variant="body2" color="error.main">
                                  ✗ Failed: {result.error || 'Unknown error'}
                                </Typography>
                              )}
                              
                              {result.confidence && (
                                <Typography variant="caption" display="block">
                                  Confidence: {(result.confidence * 100).toFixed(1)}%
                                </Typography>
                              )}
                            </Paper>
                          </Grid>
                        );
                      })}
                    </Grid>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Execute Workflow Dialog */}
      <Dialog
        open={executeDialogOpen}
        onClose={() => setExecuteDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Execute Workflow: {selectedWorkflow?.name}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" paragraph>
            {selectedWorkflow?.description}
          </Typography>
          
          <Typography variant="subtitle2" gutterBottom>
            Execution Context
          </Typography>
          
          <TextField
            fullWidth
            multiline
            rows={6}
            label="Context (JSON)"
            value={JSON.stringify(executionContext, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                setExecutionContext(parsed);
              } catch (err) {
                // Invalid JSON - keep current state
              }
            }}
            helperText="Provide execution context and parameters in JSON format"
            sx={{ mt: 2 }}
          />
          
          {/* Predefined context templates */}
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              Quick Templates
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              <Button
                size="small"
                variant="outlined"
                onClick={() => setExecutionContext({
                  target: "example.com",
                  priority: "high",
                  sources: ["osint", "social_media", "threat_feeds"]
                })}
              >
                Intelligence Collection
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() => setExecutionContext({
                  threat_type: "malware",
                  urgency: "high",
                  analysis_depth: "comprehensive"
                })}
              >
                Threat Assessment
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() => setExecutionContext({
                  evidence_source: "/path/to/evidence",
                  investigation_type: "digital_forensics",
                  timeline_required: true
                })}
              >
                Investigation
              </Button>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecuteDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              if (selectedWorkflow) {
                handleExecuteWorkflow(selectedWorkflow.workflow_id, executionContext);
                setExecuteDialogOpen(false);
              }
            }}
            disabled={!selectedWorkflow}
          >
            Execute Workflow
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkflowBuilder;