// frontend/src/components/Testing/TestingDashboard.tsx
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Container,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  BugReport as BugReportIcon,
  Psychology as PsychologyIcon,
  Storage as StorageIcon,
  Cached as CachedIcon,
  SettingsEthernet as SettingsEthernetIcon,
  IntegrationInstructions as IntegrationInstructionsIcon,
  AutoAwesome as AutoAwesomeIcon,
  HealthAndSafety as HealthAndSafetyIcon,
} from '@mui/icons-material';
import React, { useState } from 'react';
import { AgentTestingPanel } from './AgentTestingPanel';
import { AIProviderTestingPanel } from './AIProviderTestingPanel';
import { DatabaseTestingPanel } from './DatabaseTestingPanel';
import { CacheTestingPanel } from './CacheTestingPanel';
import { GraphDBTestingPanel } from './GraphDBTestingPanel';
import { WebSocketTestingPanel } from './WebSocketTestingPanel';
import { IntegrationTestingPanel } from './IntegrationTestingPanel';
import { MLTestingPanel } from './MLTestingPanel';
import { ServicesTestingPanel } from './ServicesTestingPanel';
import { SystemTestingPanel } from './SystemTestingPanel';

export const TestingDashboard: React.FC = () => {
  const [expandedSection, setExpandedSection] = useState<string | false>('core-components');

  const handleAccordionChange = (panel: string) => (
    event: React.SyntheticEvent,
    isExpanded: boolean
  ) => {
    setExpandedSection(isExpanded ? panel : false);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <BugReportIcon sx={{ fontSize: 40, color: 'primary.main' }} />
          <Typography variant="h4" component="h1" fontWeight="bold">
            Testing Dashboard
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Comprehensive testing interface for all AMAS system components. Test agents, AI providers,
          database, cache, Neo4j graph database, WebSocket, integrations, ML predictions, core services, and system health.
        </Typography>
      </Box>

      {/* Core Components Section */}
      <Accordion
        expanded={expandedSection === 'core-components'}
        onChange={handleAccordionChange('core-components')}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <PsychologyIcon color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Core Components
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Agents Testing */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Agents Testing
              </Typography>
              <AgentTestingPanel />
            </Box>

            {/* AI Providers Testing */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                AI Providers Testing
              </Typography>
              <AIProviderTestingPanel />
            </Box>

            {/* Database Testing */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Database Testing
              </Typography>
              <DatabaseTestingPanel />
            </Box>

            {/* Cache Testing */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Cache Testing
              </Typography>
              <CacheTestingPanel />
            </Box>

            {/* Graph Database (Neo4j) Testing */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Graph Database (Neo4j) Testing
              </Typography>
              <GraphDBTestingPanel />
            </Box>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Integration Components Section */}
      <Accordion
        expanded={expandedSection === 'integration-components'}
        onChange={handleAccordionChange('integration-components')}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <SettingsEthernetIcon color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Integration Components
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* WebSocket Testing */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                WebSocket Testing
              </Typography>
              <WebSocketTestingPanel />
            </Box>

            {/* Integrations Testing */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Platform Integrations Testing
              </Typography>
              <IntegrationTestingPanel />
            </Box>

            {/* ML Predictions Testing */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                ML Predictions Testing
              </Typography>
              <MLTestingPanel />
            </Box>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* System Components Section */}
      <Accordion
        expanded={expandedSection === 'system-components'}
        onChange={handleAccordionChange('system-components')}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <HealthAndSafetyIcon color="primary" />
            <Typography variant="h6" fontWeight="bold">
              System Components
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Core Services Testing */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Core Services Testing
              </Typography>
              <ServicesTestingPanel />
            </Box>

            {/* System Health Testing */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                System Health Testing
              </Typography>
              <SystemTestingPanel />
            </Box>
          </Box>
        </AccordionDetails>
      </Accordion>
    </Container>
  );
};

