import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  Switch,
  FormControlLabel,
  Slider,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  Tooltip,
  IconButton,
  Badge,
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  AttachMoney as CostIcon,
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import { motion, AnimatePresence } from 'framer-motion';

import { 
  AgentSpecialty, 
  TaskComplexity, 
  TeamComposition, 
  Agent 
} from '../../types/agent';

interface AgentTeamBuilderProps {
  taskRequest: string;
  onTeamCompositionChange: (composition: TeamComposition) => void;
  suggestedComplexity?: TaskComplexity;
}

interface SpecialtyInfo {
  specialty: AgentSpecialty;
  name: string;
  description: string;
  category: string;
  icon: string;
  averageDuration: number;
  costPerHour: number;
  qualityScore: number;
  tools: string[];
  compatibleWith: AgentSpecialty[];
}

const SPECIALIST_INFO: Record<AgentSpecialty, SpecialtyInfo> = {
  [AgentSpecialty.ACADEMIC_RESEARCHER]: {
    specialty: AgentSpecialty.ACADEMIC_RESEARCHER,
    name: "Academic Researcher",
    description: "Searches academic databases, analyzes papers, manages citations",
    category: "Research",
    icon: "🎓",
    averageDuration: 1.5,
    costPerHour: 0.15,
    qualityScore: 0.95,
    tools: ["Google Scholar", "ArXiv", "PubMed", "Semantic Scholar"],
    compatibleWith: [AgentSpecialty.DATA_ANALYST, AgentSpecialty.FACT_CHECKER]
  },
  [AgentSpecialty.WEB_INTELLIGENCE]: {
    specialty: AgentSpecialty.WEB_INTELLIGENCE,
    name: "Web Intelligence Gatherer",
    description: "Web scraping, data extraction, trend analysis, source validation",
    category: "Research",
    icon: "🌐",
    averageDuration: 1.0,
    costPerHour: 0.10,
    qualityScore: 0.88,
    tools: ["Web Scraper", "RSS Monitor", "News Aggregator"],
    compatibleWith: [AgentSpecialty.DATA_ANALYST, AgentSpecialty.COMPETITIVE_INTEL]
  },
  [AgentSpecialty.DATA_ANALYST]: {
    specialty: AgentSpecialty.DATA_ANALYST,
    name: "Data Analyst",
    description: "Statistical analysis, data visualization, trend identification",
    category: "Analysis",
    icon: "📊",
    averageDuration: 1.5,
    costPerHour: 0.12,
    qualityScore: 0.93,
    tools: ["Pandas", "NumPy", "Plotly", "SciPy"],
    compatibleWith: [AgentSpecialty.GRAPHICS_DESIGNER, AgentSpecialty.CONTENT_WRITER]
  },
  [AgentSpecialty.GRAPHICS_DESIGNER]: {
    specialty: AgentSpecialty.GRAPHICS_DESIGNER,
    name: "Graphics Designer",
    description: "Infographic design, chart creation, visual storytelling",
    category: "Creative",
    icon: "🎨",
    averageDuration: 1.0,
    costPerHour: 0.08,
    qualityScore: 0.87,
    tools: ["Matplotlib", "Plotly", "Canva API", "SVG Creation"],
    compatibleWith: [AgentSpecialty.CONTENT_WRITER, AgentSpecialty.PRESENTATION_FORMATTER]
  },
  [AgentSpecialty.CONTENT_WRITER]: {
    specialty: AgentSpecialty.CONTENT_WRITER,
    name: "Content Writer",
    description: "Professional writing, technical documentation, executive summaries",
    category: "Creative",
    icon: "✍️",
    averageDuration: 1.5,
    costPerHour: 0.12,
    qualityScore: 0.91,
    tools: ["Grammar Check", "Style Guide", "Citation Formatter"],
    compatibleWith: [AgentSpecialty.GRAPHICS_DESIGNER, AgentSpecialty.FACT_CHECKER]
  },
  [AgentSpecialty.FACT_CHECKER]: {
    specialty: AgentSpecialty.FACT_CHECKER,
    name: "Fact Checker",
    description: "Fact verification, source validation, accuracy assessment",
    category: "QA",
    icon: "✅",
    averageDuration: 0.8,
    costPerHour: 0.10,
    qualityScore: 0.96,
    tools: ["Fact Check APIs", "Source Credibility DB", "Bias Detector"],
    compatibleWith: [AgentSpecialty.QUALITY_CONTROLLER]
  },
  [AgentSpecialty.QUALITY_CONTROLLER]: {
    specialty: AgentSpecialty.QUALITY_CONTROLLER,
    name: "Quality Controller",
    description: "Output validation, format checking, professional standards",
    category: "QA",
    icon: "🔍",
    averageDuration: 0.5,
    costPerHour: 0.08,
    qualityScore: 0.94,
    tools: ["Format Validator", "Completeness Checker", "Style Guide"],
    compatibleWith: [AgentSpecialty.FACT_CHECKER]
  },
  // Add remaining specialties...
} as any;

export const AgentTeamBuilder: React.FC<AgentTeamBuilderProps> = ({
  taskRequest,
  onTeamCompositionChange,
  suggestedComplexity
}) => {
  const [selectedAgents, setSelectedAgents] = useState<AgentSpecialty[]>([]);
  const [teamComposition, setTeamComposition] = useState<TeamComposition | null>(null);
  const [autoMode, setAutoMode] = useState(true);
  const [budgetLimit, setBudgetLimit] = useState(50); // USD
  const [timeLimit, setTimeLimit] = useState(8); // hours
  const [qualityThreshold, setQualityThreshold] = useState(0.85);
  const [loading, setLoading] = useState(false);

  // Auto-suggest agents based on task request
  useEffect(() => {
    if (autoMode && taskRequest) {
      suggestOptimalTeam();
    }
  }, [taskRequest, autoMode, budgetLimit, timeLimit, qualityThreshold]);

  const suggestOptimalTeam = async () => {
    setLoading(true);
    
    try {
      // Simulate AI-powered team suggestion
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Analyze task request for keywords
      const taskLower = taskRequest.toLowerCase();
      const suggestedAgents: AgentSpecialty[] = [];
      
      // Research needs detection
      if (taskLower.includes('research') || taskLower.includes('analyze') || taskLower.includes('investigate')) {
        suggestedAgents.push(AgentSpecialty.WEB_INTELLIGENCE);
        if (taskLower.includes('academic') || taskLower.includes('paper') || taskLower.includes('study')) {
          suggestedAgents.push(AgentSpecialty.ACADEMIC_RESEARCHER);
        }
      }
      
      // Analysis needs detection  
      if (taskLower.includes('data') || taskLower.includes('statistics') || taskLower.includes('trends')) {
        suggestedAgents.push(AgentSpecialty.DATA_ANALYST);
      }
      
      // Creative needs detection
      if (taskLower.includes('presentation') || taskLower.includes('report') || taskLower.includes('document')) {
        suggestedAgents.push(AgentSpecialty.CONTENT_WRITER);
      }
      if (taskLower.includes('chart') || taskLower.includes('visual') || taskLower.includes('graphic')) {
        suggestedAgents.push(AgentSpecialty.GRAPHICS_DESIGNER);
      }
      
      // Always add QA for complex tasks
      if (suggestedComplexity && suggestedComplexity !== TaskComplexity.SIMPLE) {
        suggestedAgents.push(AgentSpecialty.FACT_CHECKER);
        suggestedAgents.push(AgentSpecialty.QUALITY_CONTROLLER);
      }
      
      // Remove duplicates and apply constraints
      const uniqueAgents = Array.from(new Set(suggestedAgents));
      const constrainedTeam = optimizeTeamForConstraints(uniqueAgents);
      
      setSelectedAgents(constrainedTeam);
      updateTeamComposition(constrainedTeam);
      
    } catch (error) {
      console.error('Error suggesting team:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const optimizeTeamForConstraints = (agents: AgentSpecialty[]): AgentSpecialty[] => {
    // Calculate cost and time for current selection
    const { cost, duration, quality } = calculateTeamMetrics(agents);
    
    // If within constraints, return as-is
    if (cost <= budgetLimit && duration <= timeLimit && quality >= qualityThreshold) {
      return agents;
    }
    
    // If over budget or time, remove lowest impact agents
    let optimizedAgents = [...agents];
    
    while (optimizedAgents.length > 1 && 
           (calculateTeamMetrics(optimizedAgents).cost > budgetLimit ||
            calculateTeamMetrics(optimizedAgents).duration > timeLimit)) {
      
      // Remove agent with lowest impact (highest cost/quality ratio)
      const impactScores = optimizedAgents.map(agent => {
        const info = SPECIALIST_INFO[agent];
        return {
          agent,
          impact: info.qualityScore / info.costPerHour
        };
      });
      
      impactScores.sort((a, b) => a.impact - b.impact);
      const toRemove = impactScores[0].agent;
      
      optimizedAgents = optimizedAgents.filter(agent => agent !== toRemove);
    }
    
    return optimizedAgents;
  };
  
  const calculateTeamMetrics = (agents: AgentSpecialty[]) => {
    let totalCost = 0;
    let maxDuration = 0;
    let qualityScores: number[] = [];
    
    // Group agents by category for parallel execution estimation
    const categories = agents.reduce((acc, agent) => {
      const info = SPECIALIST_INFO[agent];
      if (!acc[info.category]) acc[info.category] = [];
      acc[info.category].push(info);
      return acc;
    }, {} as Record<string, SpecialtyInfo[]>);
    
    // Calculate metrics
    Object.values(categories).forEach(categoryAgents => {
      // Parallel execution - use max duration in category
      const categoryMaxDuration = Math.max(...categoryAgents.map(a => a.averageDuration));
      maxDuration += categoryMaxDuration;
      
      // Add all costs (agents work simultaneously but still cost)
      totalCost += categoryAgents.reduce((sum, agent) => 
        sum + (agent.averageDuration * agent.costPerHour), 0);
      
      // Collect quality scores
      qualityScores.push(...categoryAgents.map(a => a.qualityScore));
    });
    
    const avgQuality = qualityScores.length > 0 ? 
      qualityScores.reduce((sum, score) => sum + score, 0) / qualityScores.length : 0;
    
    return {
      cost: totalCost,
      duration: maxDuration,
      quality: avgQuality
    };
  };
  
  const updateTeamComposition = (agents: AgentSpecialty[]) => {
    const metrics = calculateTeamMetrics(agents);
    
    // Group agents by category
    const composition: TeamComposition = {
      researchAgents: agents.filter(a => SPECIALIST_INFO[a]?.category === 'Research'),
      analysisAgents: agents.filter(a => SPECIALIST_INFO[a]?.category === 'Analysis'),
      creativeAgents: agents.filter(a => SPECIALIST_INFO[a]?.category === 'Creative'),
      qaAgents: agents.filter(a => SPECIALIST_INFO[a]?.category === 'QA'),
      estimatedCost: metrics.cost,
      estimatedDuration: metrics.duration,
      qualityScore: metrics.quality,
    };
    
    setTeamComposition(composition);
    onTeamCompositionChange(composition);
  };
  
  const toggleAgent = (specialty: AgentSpecialty) => {
    const newSelection = selectedAgents.includes(specialty)
      ? selectedAgents.filter(a => a !== specialty)
      : [...selectedAgents, specialty];
    
    setSelectedAgents(newSelection);
    updateTeamComposition(newSelection);
  };
  
  const getConstraintStatus = () => {
    if (!teamComposition) return { cost: 'ok', time: 'ok', quality: 'ok' };
    
    return {
      cost: teamComposition.estimatedCost > budgetLimit ? 'over' : 'ok',
      time: teamComposition.estimatedDuration > timeLimit ? 'over' : 'ok',
      quality: teamComposition.qualityScore < qualityThreshold ? 'under' : 'ok'
    };
  };
  
  const constraints = getConstraintStatus();
  
  const SpecialtyCard: React.FC<{ info: SpecialtyInfo; selected: boolean }> = ({ info, selected }) => (
    <motion.div
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
    >
      <Card 
        sx={{
          cursor: 'pointer',
          border: selected ? `2px solid ${theme.palette.primary.main}` : '1px solid',
          borderColor: selected ? 'primary.main' : 'divider',
          backgroundColor: selected ? alpha(theme.palette.primary.main, 0.05) : 'background.paper',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: alpha(theme.palette.primary.main, 0.02),
          }
        }}
        onClick={() => toggleAgent(info.specialty)}
      >
        <CardContent sx={{ p: 2 }}>
          <Box display="flex" alignItems="flex-start" justifyContent="between" mb={1}>
            <Box display="flex" alignItems="center">
              <Typography fontSize="1.5rem" mr={1}>
                {info.icon}
              </Typography>
              <Box>
                <Typography variant="subtitle2" fontWeight="bold">
                  {info.name}
                </Typography>
                <Chip size="small" label={info.category} variant="outlined" />
              </Box>
            </Box>
            {selected && (
              <Chip 
                size="small" 
                label="Selected" 
                color="primary"
                icon={<AddIcon />}
              />
            )}
          </Box>
          
          <Typography variant="caption" color="textSecondary" display="block" mb={1}>
            {info.description}
          </Typography>
          
          <Box display="flex" justifyContent="between" alignItems="center">
            <Box display="flex" alignItems="center" gap={1}>
              <Box display="flex" alignItems="center">
                <ScheduleIcon fontSize="small" color="action" sx={{ mr: 0.25 }} />
                <Typography variant="caption">
                  {info.averageDuration}h
                </Typography>
              </Box>
              <Box display="flex" alignItems="center">
                <CostIcon fontSize="small" color="action" sx={{ mr: 0.25 }} />
                <Typography variant="caption">
                  ${info.costPerHour}/h
                </Typography>
              </Box>
              <Box display="flex" alignItems="center">
                <TrendingUpIcon fontSize="small" color="action" sx={{ mr: 0.25 }} />
                <Typography variant="caption">
                  {(info.qualityScore * 100).toFixed(0)}%
                </Typography>
              </Box>
            </Box>
            
            <Tooltip title={`Tools: ${info.tools.join(', ')}`}>
              <IconButton size="small">
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  // Group specialties by category
  const categorizedSpecialties = Object.values(SPECIALIST_INFO).reduce((acc, info) => {
    if (!acc[info.category]) acc[info.category] = [];
    acc[info.category].push(info);
    return acc;
  }, {} as Record<string, SpecialtyInfo[]>);

  return (
    <Box>
      {/* Header Controls */}
      <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
        <Typography variant="h5" display="flex" alignItems="center">
          <GroupIcon sx={{ mr: 1 }} />
          Agent Team Builder
        </Typography>
        
        <Box display="flex" alignItems="center" gap={2}>
          <FormControlLabel
            control={
              <Switch 
                checked={autoMode} 
                onChange={(e) => setAutoMode(e.target.checked)}
                color="primary"
              />
            }
            label="Auto-suggest team"
          />
          
          {loading && <CircularProgress size={24} />}
        </Box>
      </Box>

      {/* Team Constraints */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" mb={2}>Team Constraints</Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Typography gutterBottom>Budget Limit: ${budgetLimit}</Typography>
            <Slider
              value={budgetLimit}
              onChange={(_, value) => setBudgetLimit(value as number)}
              min={5}
              max={200}
              step={5}
              marks={[
                { value: 25, label: '$25' },
                { value: 100, label: '$100' },
                { value: 200, label: '$200' }
              ]}
              color={constraints.cost === 'over' ? 'error' : 'primary'}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Typography gutterBottom>Time Limit: {timeLimit}h</Typography>
            <Slider
              value={timeLimit}
              onChange={(_, value) => setTimeLimit(value as number)}
              min={1}
              max={24}
              step={0.5}
              marks={[
                { value: 2, label: '2h' },
                { value: 8, label: '8h' },
                { value: 24, label: '24h' }
              ]}
              color={constraints.time === 'over' ? 'error' : 'primary'}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Typography gutterBottom>Quality Threshold: {(qualityThreshold * 100).toFixed(0)}%</Typography>
            <Slider
              value={qualityThreshold}
              onChange={(_, value) => setQualityThreshold(value as number)}
              min={0.5}
              max={1.0}
              step={0.05}
              marks={[
                { value: 0.7, label: '70%' },
                { value: 0.85, label: '85%' },
                { value: 0.95, label: '95%' }
              ]}
              color={constraints.quality === 'under' ? 'error' : 'primary'}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Specialist Selection */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={3}>Available Specialists</Typography>
            
            {Object.entries(categorizedSpecialties).map(([category, specialists]) => (
              <Box key={category} mb={4}>
                <Typography 
                  variant="subtitle1" 
                  color="primary" 
                  mb={2}
                  display="flex"
                  alignItems="center"
                >
                  {category} Team
                  <Badge 
                    badgeContent={specialists.filter(s => selectedAgents.includes(s.specialty)).length}
                    color="primary"
                    sx={{ ml: 1 }}
                  >
                    <GroupIcon fontSize="small" />
                  </Badge>
                </Typography>
                
                <Grid container spacing={2}>
                  {specialists.map((info) => (
                    <Grid item xs={12} sm={6} md={4} key={info.specialty}>
                      <SpecialtyCard 
                        info={info} 
                        selected={selectedAgents.includes(info.specialty)}
                      />
                    </Grid>
                  ))}
                </Grid>
              </Box>
            ))}
          </Paper>
        </Grid>
        
        {/* Team Composition Summary */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, position: 'sticky', top: 20 }}>
            <Typography variant="h6" mb={2}>Team Composition</Typography>
            
            {teamComposition ? (
              <Box>
                {/* Composition Summary */}
                <Box mb={3}>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                    <Typography variant="body2">Total Agents</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {selectedAgents.length}
                    </Typography>
                  </Box>
                  
                  <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                    <Typography variant="body2">Estimated Duration</Typography>
                    <Typography 
                      variant="body2" 
                      fontWeight="bold"
                      color={constraints.time === 'over' ? 'error.main' : 'text.primary'}
                    >
                      {teamComposition.estimatedDuration.toFixed(1)}h
                    </Typography>
                  </Box>
                  
                  <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                    <Typography variant="body2">Estimated Cost</Typography>
                    <Typography 
                      variant="body2" 
                      fontWeight="bold"
                      color={constraints.cost === 'over' ? 'error.main' : 'text.primary'}
                    >
                      ${teamComposition.estimatedCost.toFixed(2)}
                    </Typography>
                  </Box>
                  
                  <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                    <Typography variant="body2">Quality Score</Typography>
                    <Typography 
                      variant="body2" 
                      fontWeight="bold"
                      color={constraints.quality === 'under' ? 'error.main' : 'success.main'}
                    >
                      {(teamComposition.qualityScore * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                </Box>
                
                <Divider sx={{ mb: 2 }} />
                
                {/* Team Breakdown */}
                <Box mb={3}>
                  <Typography variant="subtitle2" mb={1}>Team Breakdown</Typography>
                  
                  {teamComposition.researchAgents.length > 0 && (
                    <Box mb={1}>
                      <Typography variant="caption" color="textSecondary">
                        Research ({teamComposition.researchAgents.length})
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                        {teamComposition.researchAgents.map(agent => (
                          <Chip 
                            key={agent}
                            size="small" 
                            label={SPECIALIST_INFO[agent]?.name || agent}
                            color="info"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                  
                  {teamComposition.analysisAgents.length > 0 && (
                    <Box mb={1}>
                      <Typography variant="caption" color="textSecondary">
                        Analysis ({teamComposition.analysisAgents.length})
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                        {teamComposition.analysisAgents.map(agent => (
                          <Chip 
                            key={agent}
                            size="small" 
                            label={SPECIALIST_INFO[agent]?.name || agent}
                            color="warning"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                  
                  {teamComposition.creativeAgents.length > 0 && (
                    <Box mb={1}>
                      <Typography variant="caption" color="textSecondary">
                        Creative ({teamComposition.creativeAgents.length})
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                        {teamComposition.creativeAgents.map(agent => (
                          <Chip 
                            key={agent}
                            size="small" 
                            label={SPECIALIST_INFO[agent]?.name || agent}
                            color="secondary"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                  
                  {teamComposition.qaAgents.length > 0 && (
                    <Box mb={1}>
                      <Typography variant="caption" color="textSecondary">
                        Quality Assurance ({teamComposition.qaAgents.length})
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                        {teamComposition.qaAgents.map(agent => (
                          <Chip 
                            key={agent}
                            size="small" 
                            label={SPECIALIST_INFO[agent]?.name || agent}
                            color="success"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </Box>
                
                {/* Constraint Warnings */}
                {(constraints.cost === 'over' || constraints.time === 'over' || constraints.quality === 'under') && (
                  <Box mb={2}>
                    {constraints.cost === 'over' && (
                      <Alert severity="warning" size="small" sx={{ mb: 1 }}>
                        Team cost (${teamComposition.estimatedCost.toFixed(2)}) exceeds budget (${budgetLimit})
                      </Alert>
                    )}
                    {constraints.time === 'over' && (
                      <Alert severity="warning" size="small" sx={{ mb: 1 }}>
                        Estimated duration ({teamComposition.estimatedDuration.toFixed(1)}h) exceeds limit ({timeLimit}h)
                      </Alert>
                    )}
                    {constraints.quality === 'under' && (
                      <Alert severity="error" size="small" sx={{ mb: 1 }}>
                        Quality score ({(teamComposition.qualityScore * 100).toFixed(1)}%) below threshold ({(qualityThreshold * 100).toFixed(0)}%)
                      </Alert>
                    )}
                  </Box>
                )}
              </Box>
            ) : (
              <Box textAlign="center" py={4} color="text.secondary">
                <GroupIcon sx={{ fontSize: 48, opacity: 0.3, mb: 2 }} />
                <Typography variant="body2">
                  Select specialists to see team composition
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AgentTeamBuilder;
