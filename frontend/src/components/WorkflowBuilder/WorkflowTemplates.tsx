import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  Rating,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
  Tabs,
  Tab,
  useTheme,
  alpha,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Edit as EditIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  ContentCopy as CopyIcon,
  Visibility as ViewIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

import { TaskComplexity, AgentSpecialty } from '../../types/agent';

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  
  // Template configuration
  taskTemplate: string;
  suggestedAgents: AgentSpecialty[];
  complexity: TaskComplexity;
  
  // Performance metrics
  successRate: number;
  avgDurationHours: number;
  avgCost: number;
  qualityScore: number;
  usageCount: number;
  
  // Metadata
  tags: string[];
  createdBy: string;
  createdAt: Date;
  lastUsed?: Date;
  
  // User preferences
  isFavorite: boolean;
  isCustom: boolean;
}

const BUILT_IN_TEMPLATES: WorkflowTemplate[] = [
  {
    id: "template_market_research",
    name: "Comprehensive Market Research",
    description: "Deep market analysis with competitive intelligence and trend forecasting",
    category: "Business Intelligence",
    taskTemplate: "Conduct comprehensive market research for {industry/product}, analyze competitive landscape, identify market opportunities, assess risks, and create executive presentation with strategic recommendations",
    suggestedAgents: [
      AgentSpecialty.WEB_INTELLIGENCE,
      AgentSpecialty.COMPETITIVE_INTEL,
      AgentSpecialty.DATA_ANALYST,
      AgentSpecialty.GRAPHICS_DESIGNER,
      AgentSpecialty.CONTENT_WRITER,
      AgentSpecialty.FACT_CHECKER,
      AgentSpecialty.QUALITY_CONTROLLER
    ],
    complexity: TaskComplexity.COMPLEX,
    successRate: 0.94,
    avgDurationHours: 4.2,
    avgCost: 12.50,
    qualityScore: 0.91,
    usageCount: 47,
    tags: ["market", "research", "competitive", "business"],
    createdBy: "system",
    createdAt: new Date('2025-01-15'),
    lastUsed: new Date('2025-11-01'),
    isFavorite: true,
    isCustom: false
  },
  
  {
    id: "template_competitor_analysis",
    name: "Competitor Analysis & Positioning",
    description: "Detailed competitor analysis with pricing intelligence and strategic positioning",
    category: "Competitive Intelligence",
    taskTemplate: "Analyze top competitors in {industry}, compare pricing strategies, feature comparison, market positioning, identify competitive advantages and weaknesses, recommend strategic positioning",
    suggestedAgents: [
      AgentSpecialty.COMPETITIVE_INTEL,
      AgentSpecialty.WEB_INTELLIGENCE,
      AgentSpecialty.FINANCIAL_ANALYZER,
      AgentSpecialty.DATA_ANALYST,
      AgentSpecialty.PRESENTATION_FORMATTER,
      AgentSpecialty.QUALITY_CONTROLLER
    ],
    complexity: TaskComplexity.COMPLEX,
    successRate: 0.89,
    avgDurationHours: 3.8,
    avgCost: 11.20,
    qualityScore: 0.88,
    usageCount: 32,
    tags: ["competitor", "analysis", "pricing", "positioning"],
    createdBy: "system",
    createdAt: new Date('2025-01-20'),
    lastUsed: new Date('2025-10-28'),
    isFavorite: false,
    isCustom: false
  },
  
  {
    id: "template_content_creation",
    name: "Professional Content Creation",
    description: "High-quality content creation with research, writing, and visual design",
    category: "Content & Marketing",
    taskTemplate: "Create professional content for {topic/purpose}, conduct background research, write engaging copy, design supporting visuals, ensure brand consistency and professional quality",
    suggestedAgents: [
      AgentSpecialty.WEB_INTELLIGENCE,
      AgentSpecialty.CONTENT_WRITER,
      AgentSpecialty.GRAPHICS_DESIGNER,
      AgentSpecialty.FACT_CHECKER,
      AgentSpecialty.QUALITY_CONTROLLER
    ],
    complexity: TaskComplexity.MODERATE,
    successRate: 0.92,
    avgDurationHours: 2.5,
    avgCost: 8.75,
    qualityScore: 0.90,
    usageCount: 28,
    tags: ["content", "writing", "design", "marketing"],
    createdBy: "system",
    createdAt: new Date('2025-02-01'),
    lastUsed: new Date('2025-11-03'),
    isFavorite: true,
    isCustom: false
  },
  
  {
    id: "template_technical_audit",
    name: "Technical System Audit",
    description: "Comprehensive technical review with security, performance, and architecture analysis",
    category: "Technical Analysis",
    taskTemplate: "Perform comprehensive technical audit of {system/codebase}, analyze architecture, identify security vulnerabilities, assess performance bottlenecks, review code quality, provide improvement recommendations",
    suggestedAgents: [
      AgentSpecialty.SYSTEM_ARCHITECT,
      AgentSpecialty.SECURITY_ANALYST,
      AgentSpecialty.PERFORMANCE_ENGINEER,
      AgentSpecialty.CODE_REVIEWER,
      AgentSpecialty.CONTENT_WRITER,
      AgentSpecialty.QUALITY_CONTROLLER
    ],
    complexity: TaskComplexity.ENTERPRISE,
    successRate: 0.87,
    avgDurationHours: 6.5,
    avgCost: 18.90,
    qualityScore: 0.93,
    usageCount: 15,
    tags: ["technical", "audit", "security", "performance"],
    createdBy: "system",
    createdAt: new Date('2025-02-10'),
    lastUsed: new Date('2025-10-15'),
    isFavorite: false,
    isCustom: false
  },
  
  {
    id: "template_investigation",
    name: "Digital Investigation",
    description: "Comprehensive digital investigation with evidence compilation and analysis",
    category: "Investigation",
    taskTemplate: "Investigate {subject/case}, gather digital evidence, analyze patterns, correlate data sources, compile comprehensive evidence report with findings and recommendations",
    suggestedAgents: [
      AgentSpecialty.DIGITAL_FORENSICS,
      AgentSpecialty.NETWORK_ANALYZER,
      AgentSpecialty.PATTERN_RECOGNIZER,
      AgentSpecialty.EVIDENCE_COMPILER,
      AgentSpecialty.CASE_INVESTIGATOR,
      AgentSpecialty.COMPLIANCE_REVIEWER
    ],
    complexity: TaskComplexity.INVESTIGATION,
    successRate: 0.91,
    avgDurationHours: 8.2,
    avgCost: 22.40,
    qualityScore: 0.95,
    usageCount: 12,
    tags: ["investigation", "forensics", "evidence", "analysis"],
    createdBy: "system",
    createdAt: new Date('2025-02-15'),
    lastUsed: new Date('2025-10-20'),
    isFavorite: false,
    isCustom: false
  }
];

interface WorkflowTemplatesProps {
  onSelectTemplate: (template: WorkflowTemplate) => void;
  selectedCategory?: string;
}

export const WorkflowTemplates: React.FC<WorkflowTemplatesProps> = ({
  onSelectTemplate,
  selectedCategory
}) => {
  const theme = useTheme();
  const [templates, setTemplates] = useState<WorkflowTemplate[]>(BUILT_IN_TEMPLATES);
  const [selectedTab, setSelectedTab] = useState(0);
  const [customizeDialogOpen, setCustomizeDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);
  
  const categories = Array.from(new Set(templates.map(t => t.category)));
  const filteredTemplates = selectedTab === 0 ? templates : 
    templates.filter(t => t.category === categories[selectedTab - 1]);
    
  const toggleFavorite = (templateId: string) => {
    setTemplates(prev => prev.map(template => 
      template.id === templateId 
        ? { ...template, isFavorite: !template.isFavorite }
        : template
    ));
  };
  
  const getComplexityColor = (complexity: TaskComplexity) => {
    switch (complexity) {
      case TaskComplexity.SIMPLE: return theme.palette.success.main;
      case TaskComplexity.MODERATE: return theme.palette.info.main;
      case TaskComplexity.COMPLEX: return theme.palette.warning.main;
      case TaskComplexity.ENTERPRISE: return theme.palette.error.main;
      case TaskComplexity.INVESTIGATION: return theme.palette.secondary.main;
      default: return theme.palette.grey[500];
    }
  };
  
  const formatDuration = (hours: number) => {
    if (hours < 1) return `${Math.round(hours * 60)}m`;
    return `${hours.toFixed(1)}h`;
  };
  
  const TemplateCard: React.FC<{ template: WorkflowTemplate }> = ({ template }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card 
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          border: `1px solid ${alpha(getComplexityColor(template.complexity), 0.3)}`,
          '&:hover': {
            boxShadow: theme.shadows[8],
            borderColor: getComplexityColor(template.complexity),
          }
        }}
      >
        <CardContent sx={{ flexGrow: 1 }}>
          <Box display="flex" justifyContent="between" alignItems="flex-start" mb={2}>
            <Box flex={1}>
              <Typography variant="h6" component="div" mb={1}>
                {template.name}
              </Typography>
              <Typography variant="body2" color="textSecondary" mb={2}>
                {template.description}
              </Typography>
            </Box>
            
            <IconButton 
              size="small" 
              onClick={() => toggleFavorite(template.id)}
              color={template.isFavorite ? "error" : "default"}
            >
              {template.isFavorite ? <FavoriteIcon /> : <FavoriteBorderIcon />}
            </IconButton>
          </Box>
          
          {/* Template Metadata */}
          <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
            <Chip 
              size="small" 
              label={template.complexity.toUpperCase()}
              style={{ backgroundColor: alpha(getComplexityColor(template.complexity), 0.1) }}
            />
            <Chip size="small" label={template.category} variant="outlined" />
            {template.isCustom && (
              <Chip size="small" label="CUSTOM" color="secondary" variant="outlined" />
            )}
          </Box>
          
          {/* Performance Metrics */}
          <Box mb={2}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box display="flex" alignItems="center" mb={1}>
                  <TrendingUpIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
                  <Typography variant="caption" color="textSecondary">
                    Success Rate
                  </Typography>
                </Box>
                <Typography variant="body2" fontWeight="bold" color="success.main">
                  {(template.successRate * 100).toFixed(1)}%
                </Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Box display="flex" alignItems="center" mb={1}>
                  <ScheduleIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
                  <Typography variant="caption" color="textSecondary">
                    Avg Duration
                  </Typography>
                </Box>
                <Typography variant="body2" fontWeight="bold">
                  {formatDuration(template.avgDurationHours)}
                </Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Box display="flex" alignItems="center" mb={1}>
                  <Typography variant="caption" color="textSecondary">
                    Quality Score
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center">
                  <Rating 
                    size="small" 
                    value={template.qualityScore * 5} 
                    precision={0.1} 
                    readOnly 
                  />
                  <Typography variant="caption" ml={1}>
                    {(template.qualityScore * 100).toFixed(0)}%
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box display="flex" alignItems="center" mb={1}>
                  <Typography variant="caption" color="textSecondary">
                    Usage Count
                  </Typography>
                </Box>
                <Typography variant="body2" fontWeight="bold">
                  {template.usageCount} times
                </Typography>
              </Grid>
            </Grid>
          </Box>
          
          {/* Agent Team Preview */}
          <Box mb={2}>
            <Typography variant="caption" color="textSecondary" mb={1} display="block">
              Suggested Team ({template.suggestedAgents.length} specialists)
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={0.5}>
              {template.suggestedAgents.slice(0, 4).map(agent => (
                <Chip 
                  key={agent}
                  size="small" 
                  label={agent.replace('_', ' ').slice(0, 15)}
                  variant="outlined"
                />
              ))}
              {template.suggestedAgents.length > 4 && (
                <Chip 
                  size="small" 
                  label={`+${template.suggestedAgents.length - 4} more`}
                  variant="outlined"
                  color="primary"
                />
              )}
            </Box>
          </Box>
          
          {/* Tags */}
          <Box>
            <Box display="flex" flexWrap="wrap" gap={0.5}>
              {template.tags.slice(0, 3).map(tag => (
                <Chip 
                  key={tag}
                  size="small" 
                  label={`#${tag}`}
                  variant="outlined"
                  sx={{ 
                    fontSize: '0.6rem',
                    backgroundColor: alpha(theme.palette.primary.main, 0.05)
                  }}
                />
              ))}
            </Box>
          </Box>
        </CardContent>
        
        <CardActions sx={{ p: 2, pt: 0 }}>
          <Button 
            size="small" 
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={() => onSelectTemplate(template)}
            fullWidth
          >
            Use Template
          </Button>
          
          <IconButton size="small" onClick={() => {
            setSelectedTemplate(template);
            setCustomizeDialogOpen(true);
          }}>
            <EditIcon />
          </IconButton>
          
          <IconButton size="small">
            <CopyIcon />
          </IconButton>
        </CardActions>
      </Card>
    </motion.div>
  );
  
  return (
    <Box>
      {/* Header */}
      <Typography variant="h5" mb={3} display="flex" alignItems="center">
        <ViewIcon sx={{ mr: 1 }} />
        Workflow Templates
      </Typography>
      
      {/* Category Tabs */}
      <Box mb={3}>
        <Tabs 
          value={selectedTab} 
          onChange={(_, newValue) => setSelectedTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="All Templates" />
          {categories.map((category, index) => (
            <Tab key={category} label={category} />
          ))}
        </Tabs>
      </Box>
      
      {/* Template Grid */}
      <AnimatePresence>
        <Grid container spacing={3}>
          {filteredTemplates.map((template, index) => (
            <Grid item xs={12} md={6} lg={4} key={template.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <TemplateCard template={template} />
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </AnimatePresence>
      
      {filteredTemplates.length === 0 && (
        <Box textAlign="center" py={8} color="text.secondary">
          <ViewIcon sx={{ fontSize: 48, opacity: 0.3, mb: 2 }} />
          <Typography variant="h6" mb={1}>
            No templates found
          </Typography>
          <Typography variant="body2">
            {selectedCategory ? 
              `No templates in ${selectedCategory} category` :
              'No templates available'
            }
          </Typography>
        </Box>
      )}
      
      {/* Template Customization Dialog */}
      <Dialog 
        open={customizeDialogOpen} 
        onClose={() => setCustomizeDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Customize Template: {selectedTemplate?.name}
        </DialogTitle>
        <DialogContent>
          {selectedTemplate && (
            <Box pt={1}>
              <TextField
                fullWidth
                label="Task Template"
                multiline
                rows={4}
                defaultValue={selectedTemplate.taskTemplate}
                margin="normal"
                helperText="Use {placeholders} for dynamic content"
              />
              
              <Typography variant="subtitle2" mt={3} mb={1}>
                Agent Configuration
              </Typography>
              
              {/* Agent selection would go here */}
              <Box>
                {selectedTemplate.suggestedAgents.map(agent => (
                  <FormControlLabel
                    key={agent}
                    control={<Switch defaultChecked />}
                    label={agent.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  />
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCustomizeDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Save Custom Template</Button>
          <Button variant="contained" color="primary">Use Customized</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkflowTemplates;
