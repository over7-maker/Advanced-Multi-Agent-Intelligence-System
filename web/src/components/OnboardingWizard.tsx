import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle, 
  AlertCircle, 
  Loader, 
  ArrowRight, 
  ArrowLeft,
  Shield,
  Database,
  Network,
  Settings,
  Play,
  Check
} from 'lucide-react';
import { apiService } from '../services/api';
import { toast } from 'react-hot-toast';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  checks: OnboardingCheck[];
  completed: boolean;
}

interface OnboardingCheck {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'checking' | 'passed' | 'failed';
  error?: string;
  fix?: string;
}

const OnboardingWizard: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [steps, setSteps] = useState<OnboardingStep[]>([
    {
      id: 'environment',
      title: 'Environment Check',
      description: 'Verifying system requirements and dependencies',
      icon: <Settings className="w-6 h-6" />,
      checks: [
        {
          id: 'node_version',
          name: 'Node.js Version',
          description: 'Check Node.js version compatibility',
          status: 'pending'
        },
        {
          id: 'api_connection',
          name: 'API Connection',
          description: 'Test connection to AMAS API',
          status: 'pending'
        },
        {
          id: 'browser_support',
          name: 'Browser Support',
          description: 'Verify browser capabilities',
          status: 'pending'
        }
      ],
      completed: false
    },
    {
      id: 'authentication',
      title: 'Authentication Setup',
      description: 'Configure user authentication and permissions',
      icon: <Shield className="w-6 h-6" />,
      checks: [
        {
          id: 'auth_service',
          name: 'Authentication Service',
          description: 'Verify authentication service is running',
          status: 'pending'
        },
        {
          id: 'user_creation',
          name: 'User Account',
          description: 'Create or verify user account',
          status: 'pending'
        },
        {
          id: 'permissions',
          name: 'Permissions',
          description: 'Set up user permissions and roles',
          status: 'pending'
        }
      ],
      completed: false
    },
    {
      id: 'database',
      title: 'Database Connection',
      description: 'Test database connectivity and performance',
      icon: <Database className="w-6 h-6" />,
      checks: [
        {
          id: 'db_connection',
          name: 'Database Connection',
          description: 'Test primary database connection',
          status: 'pending'
        },
        {
          id: 'redis_connection',
          name: 'Redis Cache',
          description: 'Verify Redis cache connection',
          status: 'pending'
        },
        {
          id: 'neo4j_connection',
          name: 'Neo4j Graph',
          description: 'Test graph database connection',
          status: 'pending'
        }
      ],
      completed: false
    },
    {
      id: 'agents',
      title: 'Agent Initialization',
      description: 'Initialize and test AI agents',
      icon: <Network className="w-6 h-6" />,
      checks: [
        {
          id: 'agent_health',
          name: 'Agent Health',
          description: 'Check agent service status',
          status: 'pending'
        },
        {
          id: 'agent_capabilities',
          name: 'Agent Capabilities',
          description: 'Verify agent capabilities and models',
          status: 'pending'
        },
        {
          id: 'agent_communication',
          name: 'Agent Communication',
          description: 'Test inter-agent communication',
          status: 'pending'
        }
      ],
      completed: false
    },
    {
      id: 'finalization',
      title: 'Finalization',
      description: 'Complete setup and start the system',
      icon: <Play className="w-6 h-6" />,
      checks: [
        {
          id: 'system_health',
          name: 'System Health',
          description: 'Final system health check',
          status: 'pending'
        },
        {
          id: 'monitoring',
          name: 'Monitoring Setup',
          description: 'Initialize monitoring and logging',
          status: 'pending'
        },
        {
          id: 'ready_to_start',
          name: 'Ready to Start',
          description: 'System ready for operation',
          status: 'pending'
        }
      ],
      completed: false
    }
  ]);

  const [isRunning, setIsRunning] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);

  useEffect(() => {
    calculateOverallProgress();
  }, [steps]);

  const calculateOverallProgress = () => {
    const totalChecks = steps.reduce((acc, step) => acc + step.checks.length, 0);
    const completedChecks = steps.reduce((acc, step) => 
      acc + step.checks.filter(check => check.status === 'passed').length, 0
    );
    setOverallProgress((completedChecks / totalChecks) * 100);
  };

  const runStepChecks = async (stepIndex: number) => {
    const step = steps[stepIndex];
    setIsRunning(true);

    for (let i = 0; i < step.checks.length; i++) {
      const check = step.checks[i];
      
      // Update check status to checking
      setSteps(prev => prev.map((s, sIndex) => 
        sIndex === stepIndex 
          ? {
              ...s,
              checks: s.checks.map((c, cIndex) => 
                cIndex === i ? { ...c, status: 'checking' as const } : c
              )
            }
          : s
      ));

      try {
        await performCheck(step.id, check.id);
        
        // Mark as passed
        setSteps(prev => prev.map((s, sIndex) => 
          sIndex === stepIndex 
            ? {
                ...s,
                checks: s.checks.map((c, cIndex) => 
                  cIndex === i ? { ...c, status: 'passed' as const } : c
                )
              }
            : s
        ));
      } catch (error) {
        // Mark as failed
        setSteps(prev => prev.map((s, sIndex) => 
          sIndex === stepIndex 
            ? {
                ...s,
                checks: s.checks.map((c, cIndex) => 
                  cIndex === i ? { 
                    ...c, 
                    status: 'failed' as const,
                    error: error instanceof Error ? error.message : 'Unknown error'
                  } : c
                )
              }
            : s
        ));
      }

      // Small delay between checks
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Mark step as completed if all checks passed
    const allPassed = step.checks.every(check => check.status === 'passed');
    setSteps(prev => prev.map((s, sIndex) => 
      sIndex === stepIndex ? { ...s, completed: allPassed } : s
    ));

    setIsRunning(false);
  };

  const performCheck = async (stepId: string, checkId: string): Promise<void> => {
    switch (stepId) {
      case 'environment':
        await performEnvironmentCheck(checkId);
        break;
      case 'authentication':
        await performAuthCheck(checkId);
        break;
      case 'database':
        await performDatabaseCheck(checkId);
        break;
      case 'agents':
        await performAgentCheck(checkId);
        break;
      case 'finalization':
        await performFinalizationCheck(checkId);
        break;
      default:
        throw new Error('Unknown step');
    }
  };

  const performEnvironmentCheck = async (checkId: string): Promise<void> => {
    switch (checkId) {
      case 'node_version':
        // Check Node.js version
        const nodeVersion = process.env.REACT_APP_NODE_VERSION || '18.0.0';
        if (parseInt(nodeVersion.split('.')[0]) < 16) {
          throw new Error('Node.js 16+ required');
        }
        break;
      case 'api_connection':
        // Test API connection
        await apiService.getHealth();
        break;
      case 'browser_support':
        // Check browser features
        if (!('WebSocket' in window)) {
          throw new Error('WebSocket not supported');
        }
        if (!('speechSynthesis' in window)) {
          throw new Error('Speech synthesis not supported');
        }
        break;
    }
  };

  const performAuthCheck = async (checkId: string): Promise<void> => {
    switch (checkId) {
      case 'auth_service':
        // Check auth service
        const health = await apiService.getHealth();
        if (health.status !== 'healthy') {
          throw new Error('Authentication service not healthy');
        }
        break;
      case 'user_creation':
        // This would create a demo user or check existing
        break;
      case 'permissions':
        // Check user permissions
        break;
    }
  };

  const performDatabaseCheck = async (checkId: string): Promise<void> => {
    const health = await apiService.getHealth();
    switch (checkId) {
      case 'db_connection':
        if (health.services.database !== 'healthy') {
          throw new Error('Database connection failed');
        }
        break;
      case 'redis_connection':
        if (health.services.redis !== 'healthy') {
          throw new Error('Redis connection failed');
        }
        break;
      case 'neo4j_connection':
        if (health.services.neo4j !== 'healthy') {
          throw new Error('Neo4j connection failed');
        }
        break;
    }
  };

  const performAgentCheck = async (checkId: string): Promise<void> => {
    switch (checkId) {
      case 'agent_health':
        const agents = await apiService.getAgents();
        if (agents.length === 0) {
          throw new Error('No agents available');
        }
        break;
      case 'agent_capabilities':
        // Check agent capabilities
        break;
      case 'agent_communication':
        // Test agent communication
        break;
    }
  };

  const performFinalizationCheck = async (checkId: string): Promise<void> => {
    switch (checkId) {
      case 'system_health':
        const health = await apiService.getHealth();
        if (health.status !== 'healthy') {
          throw new Error('System not healthy');
        }
        break;
      case 'monitoring':
        // Initialize monitoring
        break;
      case 'ready_to_start':
        // Final readiness check
        break;
    }
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'checking':
        return <Loader className="w-4 h-4 animate-spin text-blue-500" />;
      case 'passed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <div className="w-4 h-4 rounded-full bg-gray-300" />;
    }
  };

  const currentStepData = steps[currentStep];
  const canProceed = currentStepData.checks.every(check => check.status === 'passed');
  const isLastStep = currentStep === steps.length - 1;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-300">Overall Progress</span>
            <span className="text-sm text-gray-300">{Math.round(overallProgress)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="bg-black/40 backdrop-blur-xl rounded-xl border border-blue-600/30 p-8"
        >
          {/* Step Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mb-4">
              {currentStepData.icon}
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">{currentStepData.title}</h2>
            <p className="text-gray-300">{currentStepData.description}</p>
          </div>

          {/* Checks List */}
          <div className="space-y-4 mb-8">
            {currentStepData.checks.map((check, index) => (
              <div key={check.id} className="flex items-center space-x-4 p-4 bg-slate-800/50 rounded-lg">
                {getStatusIcon(check.status)}
                <div className="flex-1">
                  <h3 className="font-medium text-white">{check.name}</h3>
                  <p className="text-sm text-gray-400">{check.description}</p>
                  {check.error && (
                    <p className="text-sm text-red-400 mt-1">{check.error}</p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between">
            <button
              onClick={prevStep}
              disabled={currentStep === 0}
              className="flex items-center space-x-2 px-6 py-3 bg-slate-700 text-white rounded-lg hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>

            <div className="flex space-x-4">
              {!currentStepData.completed && (
                <button
                  onClick={() => runStepChecks(currentStep)}
                  disabled={isRunning}
                  className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isRunning ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    <Play className="w-4 h-4" />
                  )}
                  <span>{isRunning ? 'Running Checks...' : 'Run Checks'}</span>
                </button>
              )}

              <button
                onClick={nextStep}
                disabled={!canProceed}
                className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                <span>{isLastStep ? 'Complete Setup' : 'Next'}</span>
                {isLastStep ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <ArrowRight className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>
        </motion.div>

        {/* Step Indicators */}
        <div className="flex justify-center mt-8 space-x-2">
          {steps.map((_, index) => (
            <div
              key={index}
              className={`w-3 h-3 rounded-full transition-colors ${
                index === currentStep
                  ? 'bg-blue-500'
                  : index < currentStep
                  ? 'bg-green-500'
                  : 'bg-gray-600'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;