import {
    Group as GroupIcon,
    Person as PersonIcon,
    Speed as SpeedIcon,
    Star as StarIcon,
} from '@mui/icons-material';
import {
    alpha,
    Box,
    Chip,
    Grid,
    LinearProgress,
    Tooltip,
    Typography,
    useTheme,
} from '@mui/material';
import React from 'react';

import { Agent, AgentSpecialty } from '../../types/agent';

interface AgentStatusGridProps {
  agents: Agent[];
}

export const AgentStatusGrid: React.FC<AgentStatusGridProps> = ({ agents }) => {
  const theme = useTheme();
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return theme.palette.success.main;
      case 'busy': return theme.palette.warning.main;
      case 'offline': return theme.palette.grey[500];
      case 'failed': return theme.palette.error.main;
      default: return theme.palette.grey[500];
    }
  };
  
  const getSpecialtyIcon = (specialty: string) => {
    // Map specialties to appropriate emojis/icons
    const specialtyIcons: Record<string, string> = {
      'academic_researcher': '🎓',
      'web_intelligence_gatherer': '🌐',
      'data_analyst': '📊',
      'graphics_designer': '🎨',
      'content_writer': '✍️',
      'fact_checker_validator': '✅',
      'quality_controller': '🔍',
      // Add more mappings...
    };
    
    return specialtyIcons[specialty] || '🤖';
  };
  
  const getSpecialtyCategory = (specialty: AgentSpecialty) => {
    if (specialty.includes('research') || specialty.includes('intelligence') || specialty.includes('news')) {
      return 'Research';
    }
    if (specialty.includes('analyst') || specialty.includes('modeler') || specialty.includes('pattern')) {
      return 'Analysis';
    }
    if (specialty.includes('graphics') || specialty.includes('content') || specialty.includes('media')) {
      return 'Creative';
    }
    if (specialty.includes('fact') || specialty.includes('quality') || specialty.includes('compliance')) {
      return 'QA';
    }
    return 'Other';
  };

  // Group agents by category
  const agentsByCategory = agents.reduce((acc, agent) => {
    const category = getSpecialtyCategory(agent.specialty);
    if (!acc[category]) acc[category] = [];
    acc[category].push(agent);
    return acc;
  }, {} as Record<string, Agent[]>);

  const AgentCard: React.FC<{ agent: Agent }> = ({ agent }) => (
    <Tooltip 
      title={
        <Box>
          <Typography variant="subtitle2">
            {agent.specialty.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </Typography>
          <Typography variant="caption" display="block">
            Success Rate: {(agent.successRate * 100).toFixed(1)}%
          </Typography>
          <Typography variant="caption" display="block">
            Quality Score: {(agent.qualityScore * 100).toFixed(1)}%
          </Typography>
          <Typography variant="caption" display="block">
            Load: {agent.loadPercentage.toFixed(1)}%
          </Typography>
          <Typography variant="caption" display="block">
            Current Tasks: {agent.currentTasks.length}
          </Typography>
        </Box>
      }
      arrow
    >
      <Box 
        sx={{
          p: 2,
          border: `1px solid ${alpha(getStatusColor(agent.status), 0.3)}`,
          borderRadius: 2,
          backgroundColor: alpha(getStatusColor(agent.status), 0.05),
          cursor: 'pointer',
          transition: 'all 0.2s',
          '&:hover': {
            backgroundColor: alpha(getStatusColor(agent.status), 0.1),
            transform: 'translateY(-2px)',
          }
        }}
      >
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Box display="flex" alignItems="center">
            <Typography fontSize="1.2rem" mr={1}>
              {getSpecialtyIcon(agent.specialty)}
            </Typography>
            <Chip 
              size="small"
              label={agent.status.toUpperCase()}
              color={agent.status === 'available' ? 'success' :
                     agent.status === 'busy' ? 'warning' :
                     agent.status === 'failed' ? 'error' : 'default'}
            />
          </Box>
          <Typography variant="caption" color="textSecondary">
            {agent.id.slice(-3)}
          </Typography>
        </Box>
        
        <Typography variant="body2" mb={1} sx={{ minHeight: 40 }}>
          {agent.specialty.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </Typography>
        
        <Box mb={1}>
          <Box display="flex" justifyContent="space-between" mb={0.5}>
            <Typography variant="caption" color="textSecondary">
              Load
            </Typography>
            <Typography variant="caption" fontWeight="bold">
              {agent.loadPercentage.toFixed(0)}%
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={agent.loadPercentage}
            sx={{ 
              height: 4, 
              borderRadius: 2,
              backgroundColor: alpha(getStatusColor(agent.status), 0.2),
              '& .MuiLinearProgress-bar': {
                backgroundColor: getStatusColor(agent.status),
              }
            }} 
          />
        </Box>
        
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box display="flex" alignItems="center">
            <StarIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
            <Typography variant="caption">
              {(agent.qualityScore * 100).toFixed(0)}%
            </Typography>
          </Box>
          <Box display="flex" alignItems="center">
            <SpeedIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
            <Typography variant="caption">
              {agent.avgCompletionTime.toFixed(1)}h
            </Typography>
          </Box>
        </Box>
      </Box>
    </Tooltip>
  );

  return (
    <Box>
      {Object.entries(agentsByCategory).map(([category, categoryAgents]) => (
        <Box key={category} mb={3}>
          <Typography 
            variant="subtitle2" 
            color="textSecondary" 
            mb={1}
            display="flex"
            alignItems="center"
          >
            <GroupIcon fontSize="small" sx={{ mr: 1 }} />
            {category} Team ({categoryAgents.length})
          </Typography>
          
          <Grid container spacing={1}>
            {categoryAgents.slice(0, 6).map((agent) => (
              <Grid item xs={12} sm={6} key={agent.id}>
                <AgentCard agent={agent} />
              </Grid>
            ))}
          </Grid>
          
          {categoryAgents.length > 6 && (
            <Box mt={1} textAlign="center">
              <Typography variant="caption" color="textSecondary">
                +{categoryAgents.length - 6} more {category.toLowerCase()} agents
              </Typography>
            </Box>
          )}
        </Box>
      ))}
      
      {agents.length === 0 && (
        <Box textAlign="center" py={4} color="text.secondary">
          <PersonIcon sx={{ fontSize: 48, opacity: 0.3, mb: 2 }} />
          <Typography variant="body2">
            No agents currently active
          </Typography>
        </Box>
      )}
    </Box>
  );
};
