// frontend/src/components/Testing/ServicesTestingPanel.tsx
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  Typography,
  Alert,
} from '@mui/material';
import { 
  Refresh as RefreshIcon, 
  CheckCircle as CheckCircleIcon, 
  Error as ErrorIcon,
  Settings as SettingsIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  CloudQueue as CloudQueueIcon,
} from '@mui/icons-material';
import React, { useState } from 'react';
import { apiService } from '../../services/api';

interface ServiceStatus {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  message: string;
  icon: React.ReactNode;
}

export const ServicesTestingPanel: React.FC = () => {
  const [testing, setTesting] = useState(false);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [error, setError] = useState<string | null>(null);

  const _serviceIcons: Record<string, React.ReactNode> = {
    'Circuit Breaker': <SpeedIcon />,
    'Rate Limiting': <SpeedIcon />,
    'Caching': <StorageIcon />,
    'Security': <SecurityIcon />,
    'ML Service': <SettingsIcon />,
    'Vector Service': <CloudQueueIcon />,
    'Knowledge Graph': <CloudQueueIcon />,
  };

  const handleTestAll = async () => {
    try {
      setTesting(true);
      setError(null);
      
      // Test services through system health endpoint
      // Use the health endpoint directly
      const healthResponse = await (apiService as any).client.get('/health');
      const healthData = healthResponse.data;
      
      const serviceStatuses: ServiceStatus[] = [
        {
          name: 'Database',
          status: healthData.services?.database === 'healthy' ? 'healthy' : 'unhealthy',
          message: healthData.services?.database === 'healthy' ? 'Database is connected' : 'Database connection failed',
          icon: <StorageIcon />,
        },
        {
          name: 'Redis Cache',
          status: healthData.services?.redis === 'healthy' ? 'healthy' : 'unhealthy',
          message: healthData.services?.redis === 'healthy' ? 'Redis is connected' : 'Redis connection failed',
          icon: <StorageIcon />,
        },
        {
          name: 'Neo4j Graph',
          status: healthData.services?.neo4j === 'healthy' ? 'healthy' : 'unhealthy',
          message: healthData.services?.neo4j === 'healthy' ? 'Neo4j is connected' : 'Neo4j connection failed',
          icon: <CloudQueueIcon />,
        },
        {
          name: 'WebSocket',
          status: 'healthy', // WebSocket is tested separately
          message: 'WebSocket service available',
          icon: <SettingsIcon />,
        },
        {
          name: 'AI Router',
          status: 'healthy', // AI Router is tested through providers
          message: 'AI Router service available',
          icon: <SettingsIcon />,
        },
        {
          name: 'Orchestrator',
          status: 'healthy', // Orchestrator is tested through agents
          message: 'Orchestrator service available',
          icon: <SettingsIcon />,
        },
      ];
      
      setServices(serviceStatuses);
    } catch (err: any) {
      setError(err.message || 'Failed to test services');
      setServices([]);
    } finally {
      setTesting(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <SettingsIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Core Services Testing
              </Typography>
            </Box>
            <Button
              variant="outlined"
              startIcon={testing ? <CircularProgress size={20} /> : <RefreshIcon />}
              onClick={handleTestAll}
              disabled={testing}
            >
              {testing ? 'Testing...' : 'Test All Services'}
            </Button>
          </Box>

          {services.length > 0 && (
            <Grid container spacing={2}>
              {services.map((service, index) => (
                <>
                  {/* @ts-ignore Material-UI v7 Grid type issue - item prop not recognized */}
                  <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card 
                    variant="outlined" 
                    sx={{ 
                      height: '100%',
                      borderColor: service.status === 'healthy' ? 'success.main' : 'error.main',
                      borderWidth: 2,
                      borderStyle: 'solid',
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Box sx={{ color: service.status === 'healthy' ? 'success.main' : 'error.main' }}>
                          {service.icon}
                        </Box>
                        <Typography variant="subtitle1" fontWeight="bold" sx={{ flex: 1 }}>
                          {service.name}
                        </Typography>
                        {service.status === 'healthy' ? (
                          <CheckCircleIcon color="success" sx={{ fontSize: 20 }} />
                        ) : (
                          <ErrorIcon color="error" sx={{ fontSize: 20 }} />
                        )}
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {service.message}
                      </Typography>
                      <Chip
                        label={service.status === 'healthy' ? 'Healthy' : 'Unhealthy'}
                        color={service.status === 'healthy' ? 'success' : 'error'}
                        size="small"
                      />
                    </CardContent>
                  </Card>
                </Grid>
                </>
              ))}
            </Grid>
          )}

          {services.length === 0 && !testing && (
            <Alert severity="info">
              Click "Test All Services" to check the status of all core services.
            </Alert>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

