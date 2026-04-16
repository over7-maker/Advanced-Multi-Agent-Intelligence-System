// frontend/src/components/Agents/AgentToolConfiguration.tsx
import {
  CheckCircle as CheckCircleIcon,
  Close as CloseIcon,
  Error as ErrorIcon,
  Settings as SettingsIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  FormControlLabel,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Switch,
  Tab,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';

interface ToolConfig {
  tool_name: string;
  description: string;
  category: string;
  enabled: boolean;
  requires_auth: boolean;
  requires_api_key: boolean;
  api_key_configured: boolean;
  config: Record<string, any>;
  execution_mode: string;
  cost_tier: string;
  avg_execution_time: number;
}

interface ToolStatus {
  tool_name: string;
  status: string;
  last_checked: string;
  error_message?: string;
  requires_auth: boolean;
  requires_api_key: boolean;
  api_key_configured: boolean;
  service_url?: string;
  service_available: boolean;
}

interface AgentToolConfigurationProps {
  agentId: string;
  agentName: string;
  open: boolean;
  onClose: () => void;
}

export const AgentToolConfiguration: React.FC<AgentToolConfigurationProps> = ({
  agentId,
  agentName,
  open,
  onClose,
}) => {
  // CRITICAL: Log component initialization to verify it's loaded
  console.log('[AgentToolConfiguration] ========== COMPONENT LOADED - Version 3.0 ==========');
  console.log('[AgentToolConfiguration] agentId:', agentId);
  console.log('[AgentToolConfiguration] agentName:', agentName);
  console.log('[AgentToolConfiguration] open:', open);
  console.log('[AgentToolConfiguration] timestamp:', new Date().toISOString());
  console.log('[AgentToolConfiguration] ====================================================');
  
  // FORCE ALERT TO VERIFY COMPONENT IS LOADING
  if (typeof window !== 'undefined' && open) {
    console.warn('[AgentToolConfiguration] COMPONENT IS RENDERING - If you see this, component is loaded!');
  }

  const [activeTab, setActiveTab] = useState(0);
  const [tools, setTools] = useState<ToolConfig[]>([]);
  const [toolStatuses, setToolStatuses] = useState<Record<string, ToolStatus>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingTool, setTestingTool] = useState<string | null>(null);
  
  // Tool strategy settings
  const [toolStrategy, setToolStrategy] = useState('comprehensive');
  const [maxTools, setMaxTools] = useState(5);
  const [useAISynthesis, setUseAISynthesis] = useState(true);
  
  // Tool configurations
  const [toolConfigs, setToolConfigs] = useState<Record<string, { enabled: boolean; config: Record<string, any>; api_key?: string }>>({});

  useEffect(() => {
    console.log('[AgentToolConfiguration] useEffect triggered, open:', open, 'agentId:', agentId);
    if (open && agentId) {
      console.log('[AgentToolConfiguration] Opening dialog for agent:', agentId, 'agentName:', agentName);
      loadTools();
      loadToolStatuses();
    } else {
      console.log('[AgentToolConfiguration] Dialog closed or no agentId, open:', open, 'agentId:', agentId);
    }
  }, [open, agentId, agentName]);

  const loadTools = async () => {
    if (!agentId) {
      console.error('[AgentToolConfiguration] No agentId provided');
      setTools([]);
      setToolConfigs({});
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      console.log('[AgentToolConfiguration] Loading tools for agent:', agentId);
      console.log('[AgentToolConfiguration] API call: getAgentTools(', agentId, ')');
      
      const response = await apiService.getAgentTools(agentId);
      console.log('[AgentToolConfiguration] API response received:', response);
      console.log('[AgentToolConfiguration] Response type:', typeof response);
      console.log('[AgentToolConfiguration] Response keys:', response ? Object.keys(response) : 'null');
      
      if (!response) {
        console.error('[AgentToolConfiguration] Response is null or undefined');
        setTools([]);
        setToolConfigs({});
        setLoading(false);
        return;
      }
      
      if (!response.tools || response.tools.length === 0) {
        console.warn('[AgentToolConfiguration] No tools in response. Response:', response);
        setTools([]);
        setToolConfigs({});
        setLoading(false);
        return;
      }
      
      console.log('[AgentToolConfiguration] Tools array length:', response.tools.length);
      console.log('[AgentToolConfiguration] First tool:', response.tools[0]);
      
      setTools(response.tools);
      
      // Initialize tool configs
      const configs: Record<string, { enabled: boolean; config: Record<string, any> }> = {};
      response.tools.forEach((tool: any) => {
        configs[tool.tool_name] = {
          enabled: tool.enabled !== undefined ? tool.enabled : true,
          config: tool.config || {},
        };
      });
      setToolConfigs(configs);
      console.log('[AgentToolConfiguration] Initialized', Object.keys(configs).length, 'tool configs');
    } catch (error) {
      console.error('[AgentToolConfiguration] Failed to load tools - ERROR:', error);
      console.error('[AgentToolConfiguration] Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : 'No stack trace',
        name: error instanceof Error ? error.name : 'Unknown',
      });
      setTools([]);
      setToolConfigs({});
    } finally {
      setLoading(false);
      console.log('[AgentToolConfiguration] loadTools completed, loading set to false');
    }
  };

  const loadToolStatuses = async () => {
    if (!agentId) {
      console.error('[AgentToolConfiguration] No agentId for loadToolStatuses');
      return;
    }
    
    try {
      console.log('[AgentToolConfiguration] Loading tool statuses for agent:', agentId);
      console.log('[AgentToolConfiguration] API call: getAllToolsStatus(', agentId, ')');
      
      const response = await apiService.getAllToolsStatus(agentId);
      console.log('[AgentToolConfiguration] Tool statuses response:', response);
      
      if (!response || !response.tools) {
        console.warn('[AgentToolConfiguration] No tool statuses in response. Response:', response);
        setToolStatuses({});
        return;
      }
      
      console.log('[AgentToolConfiguration] Processing', response.tools.length, 'tool statuses');
      const statusMap: Record<string, ToolStatus> = {};
      response.tools.forEach((tool: any) => {
        statusMap[tool.tool_name] = tool;
      });
      setToolStatuses(statusMap);
      console.log('[AgentToolConfiguration] Set', Object.keys(statusMap).length, 'tool statuses');
    } catch (error) {
      console.error('[AgentToolConfiguration] Failed to load tool statuses - ERROR:', error);
      console.error('[AgentToolConfiguration] Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : 'No stack trace',
      });
      setToolStatuses({});
    }
  };

  const handleToolToggle = (toolName: string, enabled: boolean) => {
    setToolConfigs(prev => ({
      ...prev,
      [toolName]: {
        ...prev[toolName],
        enabled,
      },
    }));
  };

  const handleToolConfigChange = (toolName: string, key: string, value: any) => {
    setToolConfigs(prev => ({
      ...prev,
      [toolName]: {
        ...prev[toolName],
        config: {
          ...prev[toolName].config,
          [key]: value,
        },
      },
    }));
  };

  const handleApiKeyChange = (toolName: string, apiKey: string) => {
    setToolConfigs(prev => ({
      ...prev,
      [toolName]: {
        ...prev[toolName],
        api_key: apiKey,
      },
    }));
  };

  const handleTestTool = async (toolName: string) => {
    try {
      setTestingTool(toolName);
      const result = await apiService.testTool(agentId, toolName);
      if (result.success) {
        alert(`Tool ${toolName} test passed!`);
      } else {
        alert(`Tool ${toolName} test failed: ${result.error || result.message}`);
      }
      // Refresh status
      await loadToolStatuses();
    } catch (error) {
      alert(`Failed to test tool: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setTestingTool(null);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Update individual tool configs
      for (const [toolName, config] of Object.entries(toolConfigs)) {
        await apiService.updateToolConfig(agentId, toolName, {
          enabled: config.enabled,
          config: config.config,
          api_key: config.api_key,
        });
      }
      
      // Update agent-level tool settings
      await apiService.updateAgentToolsConfig(agentId, {
        tools: Object.entries(toolConfigs).map(([toolName, config]) => ({
          tool_name: toolName,
          enabled: config.enabled,
          config: config.config,
          api_key: config.api_key,
        })),
        tool_strategy: toolStrategy,
        max_tools: maxTools,
        use_ai_synthesis: useAISynthesis,
      });
      
      alert('Tool configuration saved successfully!');
      onClose();
    } catch (error) {
      alert(`Failed to save configuration: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setSaving(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'success';
      case 'needs_config':
        return 'warning';
      case 'unavailable':
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available':
        return <CheckCircleIcon color="success" fontSize="small" />;
      case 'needs_config':
        return <WarningIcon color="warning" fontSize="small" />;
      case 'unavailable':
      case 'error':
        return <ErrorIcon color="error" fontSize="small" />;
      default:
        return null;
    }
  };

  const groupedTools = tools.reduce((acc, tool) => {
    if (!acc[tool.category]) {
      acc[tool.category] = [];
    }
    acc[tool.category].push(tool);
    return acc;
  }, {} as Record<string, ToolConfig[]>);

  console.log('[AgentToolConfiguration] Render check - open:', open, 'agentId:', agentId);

  if (!open) {
    console.log('[AgentToolConfiguration] Dialog not open, returning null');
    return null;
  }

  if (!agentId) {
    console.error('[AgentToolConfiguration] ERROR: No agentId provided but open is true!');
    return (
      <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
        <DialogTitle>Error</DialogTitle>
        <DialogContent>
          <Typography color="error">No agent ID provided</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  }

  console.log('[AgentToolConfiguration] ========== RENDERING DIALOG ==========');
  console.log('[AgentToolConfiguration] open:', open);
  console.log('[AgentToolConfiguration] agentId:', agentId);
  console.log('[AgentToolConfiguration] agentName:', agentName);
  console.log('[AgentToolConfiguration] tools count:', tools.length);
  console.log('[AgentToolConfiguration] loading:', loading);
  console.log('[AgentToolConfiguration] =====================================');

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: {
          minHeight: '600px',
          maxHeight: '90vh',
        }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsIcon />
            <Typography variant="h6">Configure Tools - {agentName}</Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent sx={{ minHeight: '400px' }}>
        {loading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 4, minHeight: '400px' }}>
            <CircularProgress size={48} />
            <Typography variant="body2" sx={{ mt: 2 }}>Loading tools...</Typography>
          </Box>
        ) : (
          <>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
              <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
                <Tab label={`Tools (${tools.length})`} />
                <Tab label="Settings" />
              </Tabs>
            </Box>

            {activeTab === 0 && (
              <Box sx={{ mt: 2, maxHeight: '60vh', overflowY: 'auto' }}>
                {tools.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 8 }}>
                    <SettingsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2, opacity: 0.5 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      No tools available
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Tools will appear here once they are registered in the system.
                    </Typography>
                    <Button 
                      variant="outlined" 
                      sx={{ mt: 2 }}
                      onClick={() => {
                        loadTools();
                        loadToolStatuses();
                      }}
                    >
                      Refresh Tools
                    </Button>
                  </Box>
                ) : (
                  <>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {tools.length} tools available • {tools.filter(t => toolConfigs[t.tool_name]?.enabled).length} enabled
                    </Typography>
                    {Object.entries(groupedTools).map(([category, categoryTools]) => (
                  <Box key={category} sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom sx={{ textTransform: 'capitalize' }}>
                      {category.replace('_', ' ')}
                    </Typography>
                    <Grid container spacing={2}>
                      {categoryTools.map(tool => {
                        const status = toolStatuses[tool.tool_name];
                        const config = toolConfigs[tool.tool_name] || { enabled: tool.enabled, config: {} };
                        
                        return (
                          <>
                            {/* @ts-ignore Material-UI v7 Grid type issue */}
                            <Grid item xs={12} sm={6} md={4} key={tool.tool_name}>
                            <Box
                              sx={{
                                p: 2,
                                border: 1,
                                borderColor: 'divider',
                                borderRadius: 1,
                                bgcolor: config.enabled ? 'background.paper' : 'action.disabledBackground',
                              }}
                            >
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                                <Box sx={{ flex: 1 }}>
                                  <Typography variant="subtitle2" fontWeight="bold">
                                    {tool.tool_name}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {tool.description}
                                  </Typography>
                                </Box>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                  {status && getStatusIcon(status.status)}
                                  <Switch
                                    size="small"
                                    checked={config.enabled}
                                    onChange={(e) => handleToolToggle(tool.tool_name, e.target.checked)}
                                  />
                                </Box>
                              </Box>

                              {status && (
                                <Box sx={{ mb: 1 }}>
                                  <Chip
                                    label={status.status}
                                    color={getStatusColor(status.status) as any}
                                    size="small"
                                    sx={{ mr: 0.5 }}
                                  />
                                  {tool.requires_api_key && (
                                    <Chip
                                      label={status.api_key_configured ? 'API Key ✓' : 'API Key ✗'}
                                      color={status.api_key_configured ? 'success' : 'warning'}
                                      size="small"
                                    />
                                  )}
                                </Box>
                              )}

                              {status?.error_message && (
                                <Typography variant="caption" color="error" sx={{ display: 'block', mb: 1 }}>
                                  {status.error_message}
                                </Typography>
                              )}

                              {tool.requires_api_key && !status?.api_key_configured && (
                                <TextField
                                  fullWidth
                                  size="small"
                                  type="password"
                                  label="API Key"
                                  value={config.api_key || ''}
                                  onChange={(e) => handleApiKeyChange(tool.tool_name, e.target.value)}
                                  sx={{ mt: 1 }}
                                />
                              )}

                              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                                <Button
                                  size="small"
                                  variant="outlined"
                                  onClick={() => handleTestTool(tool.tool_name)}
                                  disabled={testingTool === tool.tool_name}
                                >
                                  {testingTool === tool.tool_name ? (
                                    <CircularProgress size={16} />
                                  ) : (
                                    'Test'
                                  )}
                                </Button>
                                <Tooltip title={`Cost: ${tool.cost_tier} | Time: ${tool.avg_execution_time}s`}>
                                  <Chip label={tool.cost_tier} size="small" variant="outlined" />
                                </Tooltip>
                              </Box>
                            </Box>
                          </Grid>
                          </>
                        );
                      })}
                    </Grid>
                  </Box>
                    ))}
                    {Object.keys(groupedTools).length === 0 && (
                      <Box sx={{ textAlign: 'center', py: 4 }}>
                        <Typography variant="body2" color="text.secondary">
                          No tools found in any category.
                        </Typography>
                      </Box>
                    )}
                  </>
                )}
              </Box>
            )}

            {activeTab === 1 && (
              <Box sx={{ mt: 2 }}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Tool Strategy</InputLabel>
                  <Select
                    value={toolStrategy}
                    onChange={(e) => setToolStrategy(e.target.value)}
                    label="Tool Strategy"
                  >
                    <MenuItem value="comprehensive">Comprehensive (use all available tools)</MenuItem>
                    <MenuItem value="efficient">Efficient (fastest tools first)</MenuItem>
                    <MenuItem value="reliable">Reliable (most reliable tools)</MenuItem>
                    <MenuItem value="cost_optimized">Cost Optimized (lowest cost tools)</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  fullWidth
                  type="number"
                  label="Max Tools"
                  value={maxTools}
                  onChange={(e) => setMaxTools(parseInt(e.target.value) || 5)}
                  sx={{ mb: 2 }}
                  inputProps={{ min: 1, max: 10 }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={useAISynthesis}
                      onChange={(e) => setUseAISynthesis(e.target.checked)}
                    />
                  }
                  label="Use AI Synthesis (combine results from multiple tools)"
                  sx={{ mb: 2 }}
                />
              </Box>
            )}
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={saving}>
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={saving || loading}
          startIcon={saving ? <CircularProgress size={16} /> : null}
        >
          {saving ? 'Saving...' : 'Save Configuration'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

