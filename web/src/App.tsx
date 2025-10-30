import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import { Suspense, lazy } from 'react';
const OnboardingWizard = lazy(() => import('./components/OnboardingWizard'));
const AMASControlCenter = lazy(() => import('./components/AMASControlCenter'));
const AgentStatusGrid = lazy(() => import('./components/AgentStatusGrid'));
const TaskQueueVisualization = lazy(() => import('./components/TaskQueueVisualization'));
const PerformanceMetricsDashboard = lazy(() => import('./components/PerformanceMetricsDashboard'));
const VoiceCommandInterface = lazy(() => import('./components/VoiceCommandInterface'));

// Services
import { apiService } from './services/api';
import { wsService } from './services/websocket';
import { voiceService } from './services/voice';

// Styles
import './App.css';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

interface AppState {
  isOnboardingComplete: boolean;
  isAuthenticated: boolean;
  currentView: 'dashboard' | 'agents' | 'tasks' | 'metrics' | 'voice';
  selectedAgent: any;
  selectedTask: any;
  systemHealth: any;
}

function App() {
  const [appState, setAppState] = useState<AppState>({
    isOnboardingComplete: false,
    isAuthenticated: false,
    currentView: 'dashboard',
    selectedAgent: null,
    selectedTask: null,
    systemHealth: null,
  });

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setIsLoading(true);
      
      // Check if onboarding is complete
      const onboardingComplete = localStorage.getItem('amas_onboarding_complete') === 'true';
      
      // Check authentication
      const token = localStorage.getItem('amas_token');
      let isAuthenticated = false;
      
      if (token) {
        try {
          await apiService.getProfile();
          isAuthenticated = true;
        } catch (err) {
          localStorage.removeItem('amas_token');
        }
      }
      
      // Check system health
      let systemHealth = null;
      try {
        systemHealth = await apiService.getHealth();
      } catch (err) {
        console.warn('Failed to get system health:', err);
      }
      
      setAppState(prev => ({
        ...prev,
        isOnboardingComplete: onboardingComplete,
        isAuthenticated,
        systemHealth,
      }));
      
    } catch (err) {
      setError('Failed to initialize application');
      console.error('App initialization error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOnboardingComplete = () => {
    localStorage.setItem('amas_onboarding_complete', 'true');
    setAppState(prev => ({
      ...prev,
      isOnboardingComplete: true,
    }));
  };

  const handleLogin = async (username: string, password: string) => {
    try {
      const { token } = await apiService.login(username, password);
      localStorage.setItem('amas_token', token);
      setAppState(prev => ({
        ...prev,
        isAuthenticated: true,
      }));
    } catch (err) {
      throw new Error('Login failed');
    }
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
    } catch (err) {
      console.warn('Logout error:', err);
    } finally {
      localStorage.removeItem('amas_token');
      setAppState(prev => ({
        ...prev,
        isAuthenticated: false,
      }));
    }
  };

  const handleViewChange = (view: AppState['currentView']) => {
    setAppState(prev => ({
      ...prev,
      currentView: view,
    }));
  };

  const handleAgentSelect = (agent: any) => {
    setAppState(prev => ({
      ...prev,
      selectedAgent: agent,
      currentView: 'agents',
    }));
  };

  const handleTaskSelect = (task: any) => {
    setAppState(prev => ({
      ...prev,
      selectedTask: task,
      currentView: 'tasks',
    }));
  };

  const handleVoiceCommand = (command: any) => {
    console.log('Voice command processed:', command);
    // Handle voice command processing
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-white mb-2">Initializing AMAS</h2>
          <p className="text-gray-400">Loading system components...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl">!</span>
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">Initialization Error</h2>
          <p className="text-gray-400 mb-4">{error}</p>
          <button
            onClick={initializeApp}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Show onboarding if not complete
  if (!appState.isOnboardingComplete) {
    return <OnboardingWizard onComplete={handleOnboardingComplete} />;
  }

  // Show login if not authenticated
  if (!appState.isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1e293b',
                color: '#ffffff',
                border: '1px solid #3b82f6',
              },
            }}
          />
          
          <Suspense fallback={<div className="p-6 text-gray-300">Loading...</div>}>
            <Routes>
              <Route path="/" element={<MainDashboard appState={appState} onViewChange={handleViewChange} onAgentSelect={handleAgentSelect} onTaskSelect={handleTaskSelect} onVoiceCommand={handleVoiceCommand} onLogout={handleLogout} />} />
              <Route path="/agents" element={<AgentView appState={appState} onAgentSelect={handleAgentSelect} onViewChange={handleViewChange} />} />
              <Route path="/tasks" element={<TaskView appState={appState} onTaskSelect={handleTaskSelect} onViewChange={handleViewChange} />} />
              <Route path="/metrics" element={<MetricsView appState={appState} onViewChange={handleViewChange} />} />
              <Route path="/voice" element={<VoiceView appState={appState} onVoiceCommand={handleVoiceCommand} onViewChange={handleViewChange} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

// Login Screen Component
const LoginScreen: React.FC<{ onLogin: (username: string, password: string) => Promise<void> }> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await onLogin(username, password);
    } catch (err) {
      setError('Invalid credentials');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-black/40 backdrop-blur-xl rounded-xl border border-blue-600/30 p-8"
      >
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl font-bold">A</span>
          </div>
          <h1 className="text-2xl font-bold text-white">AMAS Login</h1>
          <p className="text-gray-400">Advanced Multi-Agent Intelligence System</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-slate-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-slate-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none"
              required
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm text-center">{error}</div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-400 text-sm">
            Demo credentials: admin / admin
          </p>
        </div>
      </motion.div>
    </div>
  );
};

// Main Dashboard Component
const MainDashboard: React.FC<{
  appState: AppState;
  onViewChange: (view: AppState['currentView']) => void;
  onAgentSelect: (agent: any) => void;
  onTaskSelect: (task: any) => void;
  onVoiceCommand: (command: any) => void;
  onLogout: () => void;
}> = ({ appState, onViewChange, onAgentSelect, onTaskSelect, onVoiceCommand, onLogout }) => {
  return (
    <div className="min-h-screen">
      <AMASControlCenter 
        onViewChange={onViewChange}
        onAgentSelect={onAgentSelect}
        onTaskSelect={onTaskSelect}
        onVoiceCommand={onVoiceCommand}
        onLogout={onLogout}
        systemHealth={appState.systemHealth}
      />
    </div>
  );
};

// Agent View Component
const AgentView: React.FC<{
  appState: AppState;
  onAgentSelect: (agent: any) => void;
  onViewChange: (view: AppState['currentView']) => void;
}> = ({ appState, onAgentSelect, onViewChange }) => {
  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => onViewChange('dashboard')}
            className="text-blue-400 hover:text-blue-300 mb-4"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-white">Agent Management</h1>
        </div>
        <AgentStatusGrid 
          onAgentSelect={onAgentSelect}
          selectedAgentId={appState.selectedAgent?.id}
        />
      </div>
    </div>
  );
};

// Task View Component
const TaskView: React.FC<{
  appState: AppState;
  onTaskSelect: (task: any) => void;
  onViewChange: (view: AppState['currentView']) => void;
}> = ({ appState, onTaskSelect, onViewChange }) => {
  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => onViewChange('dashboard')}
            className="text-blue-400 hover:text-blue-300 mb-4"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-white">Task Management</h1>
        </div>
        <TaskQueueVisualization 
          onTaskSelect={onTaskSelect}
          selectedTaskId={appState.selectedTask?.id}
          showCompleted={true}
        />
      </div>
    </div>
  );
};

// Metrics View Component
const MetricsView: React.FC<{
  appState: AppState;
  onViewChange: (view: AppState['currentView']) => void;
}> = ({ appState, onViewChange }) => {
  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => onViewChange('dashboard')}
            className="text-blue-400 hover:text-blue-300 mb-4"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-white">Performance Metrics</h1>
        </div>
        <PerformanceMetricsDashboard />
      </div>
    </div>
  );
};

// Voice View Component
const VoiceView: React.FC<{
  appState: AppState;
  onVoiceCommand: (command: any) => void;
  onViewChange: (view: AppState['currentView']) => void;
}> = ({ appState, onVoiceCommand, onViewChange }) => {
  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => onViewChange('dashboard')}
            className="text-blue-400 hover:text-blue-300 mb-4"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-white">Voice Commands</h1>
        </div>
        <VoiceCommandInterface onCommandProcessed={onVoiceCommand} />
      </div>
    </div>
  );
};

export default App;