// frontend/src/components/Agents/AIProvidersPanel.tsx
import {
  Cancel as CancelIcon,
  CheckCircle as CheckCircleIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  List,
  ListItem,
  ListItemText,
  Typography,
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';

interface AIProvider {
  id: string;
  name: string;
  model: string;
  type: string;
  priority: number;
  enabled: boolean;
  base_url?: string;
  available: boolean;
  models?: string[];
}

export const AIProvidersPanel: React.FC = () => {
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<AIProvider | null>(null);
  const [modelsDialogOpen, setModelsDialogOpen] = useState(false);
  const [enabling, setEnabling] = useState<string | null>(null);

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getAIProviders();
      setProviders(response.providers || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch AI providers');
      console.error('Failed to fetch AI providers:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEnableProvider = async (providerId: string) => {
    try {
      setEnabling(providerId);
      setError(null);
      const result = await apiService.enableAIProvider(providerId);
      // Update provider in local state immediately for better UX
      setProviders((prev) =>
        prev.map((p) =>
          p.id === providerId
            ? { ...p, enabled: true, available: true }
            : p
        )
      );
      // Refresh list to get latest status
      await fetchProviders();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Unknown error';
      setError(`Failed to enable ${providerId}: ${errorMessage}`);
      console.error('Failed to enable provider:', err);
    } finally {
      setEnabling(null);
    }
  };

  const handleViewModels = async (provider: AIProvider) => {
    if (provider.id === 'ollama') {
      try {
        const modelsData = await apiService.getOllamaModels();
        if (modelsData.available && modelsData.models) {
          setSelectedProvider({
            ...provider,
            models: modelsData.models.map((m: any) => m.name),
          });
          setModelsDialogOpen(true);
        } else {
          alert(`❌ Ollama is not available: ${modelsData.error || 'Unknown error'}`);
        }
      } catch (err: any) {
        alert(`❌ Failed to get Ollama models: ${err.message || 'Unknown error'}`);
      }
    } else {
      setSelectedProvider(provider);
      setModelsDialogOpen(true);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">AI Providers</Typography>
        <Button variant="outlined" onClick={fetchProviders} size="small">
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2}>
        {providers.map((provider) => (
          <>
            {/* @ts-ignore Material-UI v7 Grid type issue - item prop not recognized */}
            <Grid item xs={12} sm={6} md={4} key={provider.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <Box>
                    <Typography variant="h6">{provider.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {provider.model}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    {provider.available ? (
                      <CheckCircleIcon color="success" fontSize="small" />
                    ) : (
                      <CancelIcon color="error" fontSize="small" />
                    )}
                    <Chip
                      label={provider.enabled ? 'Enabled' : 'Disabled'}
                      color={provider.enabled ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Type: {provider.type}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Priority: {provider.priority}
                  </Typography>
                  {provider.base_url && (
                    <Typography variant="body2" color="text.secondary" sx={{ wordBreak: 'break-all' }}>
                      URL: {provider.base_url}
                    </Typography>
                  )}
                </Box>

                <Box sx={{ display: 'flex', gap: 1 }}>
                  {!provider.enabled && provider.available && (
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => handleEnableProvider(provider.id)}
                      disabled={enabling === provider.id}
                    >
                      {enabling === provider.id ? <CircularProgress size={16} /> : 'Enable'}
                    </Button>
                  )}
                  {provider.id === 'ollama' && (
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<SettingsIcon />}
                      onClick={() => handleViewModels(provider)}
                    >
                      Models
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
          </>
        ))}
      </Grid>

      {/* Models Dialog */}
      <Dialog open={modelsDialogOpen} onClose={() => setModelsDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedProvider?.name} Models
        </DialogTitle>
        <DialogContent>
          {selectedProvider?.models && selectedProvider.models.length > 0 ? (
            <List>
              {selectedProvider.models.map((model, idx) => (
                <ListItem key={idx}>
                  <ListItemText primary={model} />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No models available
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setModelsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

