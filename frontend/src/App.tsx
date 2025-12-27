import { Box, Button } from '@mui/material';
import { useEffect, useState } from 'react';
import { Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom';
// Dashboard component - using DashboardNew in routes
import { AgentList } from './components/Agents/AgentList';
import { Login } from './components/Auth/Login';
import { ProtectedRoute } from './components/Auth/ProtectedRoute';
import { DashboardNew as DashboardNewComponent } from './components/Dashboard/DashboardNew';
import { IntegrationList } from './components/Integrations/IntegrationList';
import { MainLayout } from './components/Layout/MainLayout';
import { ProgressTracker } from './components/ProgressTracker/ProgressTracker';
import { SystemHealth } from './components/System/SystemHealth';
import { TestingDashboard } from './components/Testing/TestingDashboard';
import { CreateTask } from './components/Tasks/CreateTask';
import { TaskExecutionView } from './components/Tasks/TaskExecutionView';
import { TaskList } from './components/Tasks/TaskList';
import { AgentTeamBuilder } from './components/WorkflowBuilder/AgentTeamBuilder';
import { WorkflowTemplates } from './components/WorkflowBuilder/WorkflowTemplates';
import { apiService } from './services/api';
import { websocketService } from './services/websocket';
import { TaskComplexity, TeamComposition, WorkflowExecution } from './types/agent';

// Template type definition (matches WorkflowTemplates component)
interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  taskTemplate: string;
  suggestedAgents: string[];
  complexity: TaskComplexity;
  successRate: number;
  avgDurationHours: number;
  avgCost: number;
  qualityScore: number;
  usageCount: number;
  tags: string[];
  createdBy: string;
  createdAt: Date;
  lastUsed?: Date;
  isFavorite: boolean;
  isCustom: boolean;
}

// Using MainLayout and ProtectedRoute from components

function App(): JSX.Element {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Navigate to="/dashboard" replace />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <MainLayout>
              <DashboardNewComponent />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/tasks"
        element={
          <ProtectedRoute>
            <MainLayout>
              <TaskList />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/tasks/create"
        element={
          <ProtectedRoute>
            <MainLayout>
              <CreateTask />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/tasks/:taskId"
        element={
          <ProtectedRoute>
            <MainLayout>
              <TaskExecutionView />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/agents"
        element={
          <ProtectedRoute>
            <MainLayout>
              <AgentList />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/integrations"
        element={
          <ProtectedRoute>
            <MainLayout>
              <IntegrationList />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/health"
        element={
          <ProtectedRoute>
            <MainLayout>
              <SystemHealth />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/testing"
        element={
          <ProtectedRoute>
            <MainLayout>
              <TestingDashboard />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/workflow-builder"
        element={
          <ProtectedRoute>
            <MainLayout>
              <WorkflowBuilderPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/workflow/:id"
        element={
          <ProtectedRoute>
            <MainLayout>
              <WorkflowDetailPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

// Dashboard Page Component - using DashboardNew instead
// Old Dashboard component kept for backward compatibility

// Workflow Builder Page Component
function WorkflowBuilderPage(): JSX.Element {
  const navigate = useNavigate();
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);
  const [teamComposition, setTeamComposition] = useState<TeamComposition | null>(null);

  const handleTemplateSelect = (template: WorkflowTemplate): void => {
    setSelectedTemplate(template);
  };

  const handleTeamCompositionChange = (composition: TeamComposition): void => {
    setTeamComposition(composition);
  };

  const handleStartWorkflow = async (): Promise<void> => {
    if (selectedTemplate && teamComposition) {
      try {
        // Create workflow via API
        const workflowData = {
          template_id: selectedTemplate.id,
          task_template: selectedTemplate.taskTemplate,
          team_composition: teamComposition,
          complexity: selectedTemplate.complexity,
        };
        
        // Note: createWorkflow method needs to be added to API service
        // For now, using createTask as a workaround
        const response = await apiService.createTask({
          title: workflowData.template_id,
          task_type: 'workflow',
          target: '',
          parameters: workflowData,
        });
        
        console.log('Workflow created successfully:', response);
        navigate('/dashboard');
      } catch (error) {
        console.error('Error creating workflow:', error);
        alert('Failed to create workflow. Please try again.');
      }
    }
  };

  return (
    <Box>
      {!selectedTemplate ? (
        <WorkflowTemplates onSelectTemplate={handleTemplateSelect} />
      ) : (
        <Box>
          <AgentTeamBuilder
            taskRequest={selectedTemplate.taskTemplate}
            onTeamCompositionChange={handleTeamCompositionChange}
            suggestedComplexity={selectedTemplate.complexity}
          />
          <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button variant="outlined" onClick={() => setSelectedTemplate(null)}>
              Back to Templates
            </Button>
            <Button 
              variant="contained" 
              onClick={handleStartWorkflow} 
              disabled={!teamComposition}
            >
              Start Workflow
            </Button>
          </Box>
        </Box>
      )}
    </Box>
  );
}

// Workflow Detail Page Component
function WorkflowDetailPage(): JSX.Element {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [execution, setExecution] = useState<WorkflowExecution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setError('No workflow ID provided');
      setLoading(false);
      return;
    }

    const loadWorkflow = async (): Promise<void> => {
      try {
        // Note: getWorkflowExecution method needs to be added to API service
        // For now, using getTask as a workaround
        const response = await apiService.getTask(id);
        
        // Convert task response to workflow execution format
        const task = response as any;
        const exec: WorkflowExecution = {
          executionId: task.task_id || id,
          workflowId: task.workflow_id || 'unknown',
          status: task.status || 'executing',
          progressPercentage: task.progress || 0,
          tasksCompleted: task.tasks_completed || 0,
          tasksInProgress: task.tasks_in_progress || 0,
          tasksPending: task.tasks_pending || 0,
          estimatedRemainingHours: task.estimated_hours || 0.5,
          overallHealth: task.health || 'healthy',
          currentPhase: task.current_phase || 'processing',
          startedAt: task.started_at ? new Date(task.started_at) : new Date(),
          completedAt: task.completed_at ? new Date(task.completed_at) : undefined,
        };
        setExecution(exec);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load workflow');
        setLoading(false);
      }
    };

    loadWorkflow();

    // Subscribe to real-time updates
    websocketService.connect();
    const unsubscribe = websocketService.on('workflow_update', (data) => {
      if (data.id === id || data.executionId === id) {
        setExecution((prev) => prev ? { ...prev, ...data } : null);
      }
    });

    return () => {
      unsubscribe();
    };
  }, [id]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Box>Loading workflow...</Box>
      </Box>
    );
  }

  if (error || !execution) {
    return (
      <Box>
        <Button 
          variant="outlined" 
          onClick={() => navigate('/dashboard')}
          sx={{ mb: 3 }}
        >
          ← Back to Dashboard
        </Button>
        <Box color="error.main">
          {error || 'Workflow not found'}
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Button 
        variant="outlined" 
        onClick={() => navigate('/dashboard')}
        sx={{ mb: 3 }}
      >
        ← Back to Dashboard
      </Button>
      <ProgressTracker execution={execution} realTimeUpdates={true} />
    </Box>
  );
}

export default App;

