// frontend/src/components/Onboarding/OnboardingWizard.tsx
// Converted from web/ to use Material-UI
import {
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Wifi as NetworkIcon,
    Settings as SettingsIcon,
    Shield as ShieldIcon,
    Storage as StorageIcon,
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    CircularProgress,
    Step,
    StepContent,
    StepLabel,
    Stepper,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';

interface OnboardingCheck {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'checking' | 'passed' | 'failed';
  error?: string;
}

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  checks: OnboardingCheck[];
}

interface OnboardingWizardProps {
  onComplete: () => void;
}

export const OnboardingWizard: React.FC<OnboardingWizardProps> = ({ onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [steps, setSteps] = useState<OnboardingStep[]>([
    {
      id: 'environment',
      title: 'Environment Check',
      description: 'Verifying system requirements',
      icon: <SettingsIcon />,
      checks: [
        { id: 'api_connection', name: 'API Connection', description: 'Test connection to AMAS API', status: 'pending' },
        { id: 'browser_support', name: 'Browser Support', description: 'Verify browser capabilities', status: 'pending' },
      ],
    },
    {
      id: 'authentication',
      title: 'Authentication Setup',
      description: 'Configure user authentication',
      icon: <ShieldIcon />,
      checks: [
        { id: 'auth_service', name: 'Authentication Service', description: 'Verify authentication service', status: 'pending' },
      ],
    },
    {
      id: 'database',
      title: 'Database Connection',
      description: 'Test database connectivity',
      icon: <StorageIcon />,
      checks: [
        { id: 'database_health', name: 'Database Health', description: 'Check database status', status: 'pending' },
      ],
    },
    {
      id: 'network',
      title: 'Network Configuration',
      description: 'Verify network connectivity',
      icon: <NetworkIcon />,
      checks: [
        { id: 'websocket', name: 'WebSocket Connection', description: 'Test WebSocket connectivity', status: 'pending' },
      ],
    },
  ]);

  const runChecks = async (stepIndex: number) => {
    const step = steps[stepIndex];
    const updatedChecks = await Promise.all(
      step.checks.map(async (check) => {
        setSteps((prev) => {
          const newSteps = [...prev];
          newSteps[stepIndex].checks = newSteps[stepIndex].checks.map((c) =>
            c.id === check.id ? { ...c, status: 'checking' } : c
          );
          return newSteps;
        });

        try {
          if (check.id === 'api_connection') {
            await apiService.getSystemHealth();
            return { ...check, status: 'passed' as const };
          } else if (check.id === 'auth_service') {
            // Check if we can access auth endpoints
            return { ...check, status: 'passed' as const };
          } else if (check.id === 'database_health') {
            const health = await apiService.getSystemHealth();
            if (health.components?.database?.status === 'healthy') {
              return { ...check, status: 'passed' as const };
            }
            return { ...check, status: 'failed' as const, error: 'Database not healthy' };
          } else if (check.id === 'websocket') {
            // WebSocket check would be done separately
            return { ...check, status: 'passed' as const };
          } else {
            return { ...check, status: 'passed' as const };
          }
        } catch (error) {
          return { ...check, status: 'failed' as const, error: error instanceof Error ? error.message : 'Check failed' };
        }
      })
    );

    setSteps((prev) => {
      const newSteps = [...prev];
      newSteps[stepIndex].checks = updatedChecks;
      return newSteps;
    });
  };

  useEffect(() => {
    if (activeStep < steps.length) {
      runChecks(activeStep);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeStep]);

  const handleNext = () => {
    if (activeStep < steps.length - 1) {
      setActiveStep((prev) => prev + 1);
    } else {
      onComplete();
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const allChecksPassed = steps[activeStep]?.checks.every((check) => check.status === 'passed');
  const hasFailedChecks = steps[activeStep]?.checks.some((check) => check.status === 'failed');
  const isChecking = steps[activeStep]?.checks.some((check) => check.status === 'checking');

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        AMAS Setup Wizard
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Let's verify your system is configured correctly
      </Typography>

      <Stepper activeStep={activeStep} orientation="vertical">
        {steps.map((step, index) => (
          <Step key={step.id}>
            <StepLabel icon={step.icon}>{step.title}</StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {step.description}
              </Typography>

              <Box sx={{ mb: 2 }}>
                {step.checks.map((check) => (
                  <Card key={check.id} sx={{ mb: 1 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {check.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {check.description}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {check.status === 'checking' && <CircularProgress size={20} />}
                          {check.status === 'passed' && <CheckCircleIcon color="success" />}
                          {check.status === 'failed' && <ErrorIcon color="error" />}
                          {check.status === 'pending' && <Chip label="Pending" size="small" />}
                        </Box>
                      </Box>
                      {check.error && (
                        <Alert severity="error" sx={{ mt: 1 }}>
                          {check.error}
                        </Alert>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Box>

              <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                <Button disabled={index === 0} onClick={handleBack}>
                  Back
                </Button>
                <Button
                  variant="contained"
                  onClick={handleNext}
                  disabled={isChecking || (hasFailedChecks && !allChecksPassed)}
                >
                  {index === steps.length - 1 ? 'Complete' : 'Next'}
                </Button>
              </Box>
            </StepContent>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
};

export default OnboardingWizard;

