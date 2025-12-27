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
// Landing page components (from PR #276)
import HeroSection from './components/landing/HeroSection';
import ArchitectureSection from './components/landing/ArchitectureSection';
import FeaturesSection from './components/landing/FeaturesSection';
import MonitoringDashboard from './components/landing/MonitoringDashboard';
import InteractiveDemo from './components/landing/InteractiveDemo';
import CTASection from './components/landing/CTASection';
import Footer from './components/landing/Footer';
import Header from './components/landing/Header';
import { apiService } from './services/api';
import { websocketService } from './services/websocket';
import { TaskComplexity, TeamComposition, WorkflowExecution } from './types/agent';

// Landing Page Component (Public - no authentication required)
function LandingPage() {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  return (
    <div className={darkMode ? 'dark' : 'light'}>
      <Header isDark={darkMode} onToggleDarkMode={toggleDarkMode} />
      <main>
        <HeroSection />
        <ArchitectureSection />
        <FeaturesSection />
        <MonitoringDashboard />
        <InteractiveDemo />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}

// Using MainLayout and ProtectedRoute from components

function App(): JSX.Element {
  return (
    <Routes>
      {/* Public Landing Page Route */}
      <Route path="/landing" element={<LandingPage />} />
      
      {/* Authentication */}
      <Route path="/login" element={<Login />} />
      
      {/* Protected Routes */}
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
        <WorkflowTemplates onSelect={handleTemplateSelect} />
      ) : (
        <AgentTeamBuilder
          template={selectedTemplate}
          teamComposition={teamComposition}
          onTeamCompositionChange={handleTeamCompositionChange}
          onStart={handleStartWorkflow}
          onBack={() => setSelectedTemplate(null)}
        />
      )}
    </Box>
  );
}

// Workflow Detail Page Component
function WorkflowDetailPage(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const [workflow, setWorkflow] = useState<WorkflowExecution | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWorkflow = async () => {
      if (!id) return;
      
      try {
        // TODO: Implement workflow fetching from API
        // For now, using mock data
        setWorkflow(null);
      } catch (error) {
        console.error('Error fetching workflow:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkflow();
  }, [id]);

  if (loading) {
    return <Box>Loading workflow...</Box>;
  }

  if (!workflow) {
    return <Box>Workflow not found</Box>;
  }

  return (
    <Box>
      <Typography variant="h4">Workflow {id}</Typography>
      <ProgressTracker workflowId={id} />
    </Box>
  );
}

export default App;
