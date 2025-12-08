// frontend/src/components/Integrations/IntegrationList.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { apiService, Integration } from '../../services/api';

const PLATFORM_ICONS: Record<string, string> = {
  n8n: '⚙️',
  slack: '💬',
  github: '🐙',
  notion: '📝',
  jira: '🎯',
  salesforce: '☁️',
};

export const IntegrationList: React.FC = () => {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [newPlatform, setNewPlatform] = useState('');
  const [newCredentials, setNewCredentials] = useState('{}');

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    try {
      setLoading(true);
      const response = await apiService.listIntegrations();
      setIntegrations(response.integrations);
    } catch (error) {
      console.error('Failed to fetch integrations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      const credentials = JSON.parse(newCredentials);
      await apiService.createIntegration({
        platform: newPlatform,
        credentials,
      });
      setOpenDialog(false);
      setNewPlatform('');
      setNewCredentials('{}');
      fetchIntegrations();
    } catch (error) {
      console.error('Failed to create integration:', error);
      alert('Failed to create integration. Please check your credentials JSON.');
    }
  };

  const handleDelete = async (integrationId: string) => {
    if (!confirm('Are you sure you want to delete this integration?')) return;
    try {
      await apiService.deleteIntegration(integrationId);
      fetchIntegrations();
    } catch (error) {
      console.error('Failed to delete integration:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'error':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Integrations</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Add Integration
        </Button>
      </Box>

      <Grid container spacing={3}>
        {integrations.map((integration) => (
          <Grid item xs={12} sm={6} md={4} key={integration.integration_id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h5">
                      {PLATFORM_ICONS[integration.platform] || '🔌'}
                    </Typography>
                    <Typography variant="h6">{integration.platform}</Typography>
                  </Box>
                  <Chip
                    label={integration.status}
                    color={getStatusColor(integration.status) as any}
                    size="small"
                  />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Sync Count:
                  </Typography>
                  <Typography variant="body2">{integration.sync_count}</Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Error Count:
                  </Typography>
                  <Typography variant="body2" color={integration.error_count > 0 ? 'error' : 'text.primary'}>
                    {integration.error_count}
                  </Typography>
                </Box>

                {integration.last_sync && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Last Sync:
                    </Typography>
                    <Typography variant="body2">
                      {new Date(integration.last_sync).toLocaleString()}
                    </Typography>
                  </Box>
                )}

                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                  <IconButton size="small" onClick={fetchIntegrations}>
                    <RefreshIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDelete(integration.integration_id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Integration</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Platform"
            value={newPlatform}
            onChange={(e) => setNewPlatform(e.target.value)}
            margin="normal"
            select
            SelectProps={{ native: true }}
          >
            <option value="">Select Platform</option>
            <option value="n8n">N8N</option>
            <option value="slack">Slack</option>
            <option value="github">GitHub</option>
            <option value="notion">Notion</option>
            <option value="jira">Jira</option>
            <option value="salesforce">Salesforce</option>
          </TextField>
          <TextField
            fullWidth
            label="Credentials (JSON)"
            value={newCredentials}
            onChange={(e) => setNewCredentials(e.target.value)}
            margin="normal"
            multiline
            rows={4}
            helperText="Enter credentials as JSON object"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

