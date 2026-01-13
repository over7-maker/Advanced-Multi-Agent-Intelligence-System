// frontend/src/components/Agents/ToolStatusIndicator.tsx
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { Box, Chip, Tooltip, Typography } from '@mui/material';
import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';

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

interface ToolStatusIndicatorProps {
  agentId: string;
  toolName: string;
  compact?: boolean;
}

export const ToolStatusIndicator: React.FC<ToolStatusIndicatorProps> = ({
  agentId,
  toolName,
  compact = false,
}) => {
  const [status, setStatus] = useState<ToolStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStatus();
    // Refresh status every 30 seconds
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, [agentId, toolName]);

  const loadStatus = async () => {
    try {
      const toolStatus = await apiService.getToolStatus(agentId, toolName);
      setStatus(toolStatus);
    } catch (error) {
      console.error(`Failed to load status for tool ${toolName}:`, error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !status) {
    return null;
  }

  const getStatusIcon = () => {
    switch (status.status) {
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

  const getStatusColor = () => {
    switch (status.status) {
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

  if (compact) {
    return (
      <Tooltip
        title={
          <Box>
            <Typography variant="caption" display="block">
              Status: {status.status}
            </Typography>
            {status.error_message && (
              <Typography variant="caption" display="block" color="error">
                {status.error_message}
              </Typography>
            )}
            {status.requires_api_key && (
              <Typography variant="caption" display="block">
                API Key: {status.api_key_configured ? 'Configured' : 'Not Configured'}
              </Typography>
            )}
          </Box>
        }
      >
        <Box sx={{ display: 'inline-flex', alignItems: 'center' }}>
          {getStatusIcon()}
        </Box>
      </Tooltip>
    );
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {getStatusIcon()}
      <Chip
        label={status.status}
        color={getStatusColor() as any}
        size="small"
      />
      {status.requires_api_key && (
        <Chip
          label={status.api_key_configured ? 'API Key ✓' : 'API Key ✗'}
          color={status.api_key_configured ? 'success' : 'warning'}
          size="small"
          variant="outlined"
        />
      )}
      {status.error_message && (
        <Tooltip title={status.error_message}>
          <Typography variant="caption" color="error">
            {status.error_message}
          </Typography>
        </Tooltip>
      )}
    </Box>
  );
};

