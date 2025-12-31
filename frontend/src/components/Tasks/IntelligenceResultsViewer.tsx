// frontend/src/components/Tasks/IntelligenceResultsViewer.tsx
import {
  Business as BusinessIcon,
  CheckCircle as CheckCircleIcon,
  Domain as DomainIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  Language as LanguageIcon,
  LocationOn as LocationIcon,
  Public as PublicIcon,
  Security as SecurityIcon,
  Timeline as TimelineIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import React from 'react';

interface IntelligenceResultsViewerProps {
  intelData: any;
}

export const IntelligenceResultsViewer: React.FC<IntelligenceResultsViewerProps> = ({ intelData }) => {
  if (!intelData) return null;

  // Parse intelligence report - handle multiple formats
  const parseIntelReport = (data: any) => {
    if (!data) return null;
    
    // Try to extract from nested structure
    let report = data.intelligence_report || data;
    
    // If it's a string, try to parse JSON
    if (typeof report === 'string') {
      try {
        // Extract JSON from markdown code blocks
        const jsonMatch = report.match(/```json\n([\s\S]*?)\n```/);
        if (jsonMatch) {
          report = JSON.parse(jsonMatch[1]);
        } else {
          report = JSON.parse(report);
        }
      } catch (e) {
        console.error('Failed to parse intelligence report:', e);
        return null;
      }
    }
    
    return report.intelligence_report || report;
  };

  const report = parseIntelReport(intelData);
  if (!report) return null;

  return (
    <Card sx={{ mb: 3, background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%)', backdropFilter: 'blur(10px)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
          <TimelineIcon sx={{ fontSize: 32, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }} />
          <Typography variant="h5" fontWeight="bold" sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Intelligence Gathering Report
          </Typography>
        </Box>

        {/* Executive Summary */}
        {report.executive_summary && (
          <Alert severity="info" sx={{ mb: 3, bgcolor: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Executive Summary
            </Typography>
            <Typography variant="body2">{report.executive_summary}</Typography>
          </Alert>
        )}

        {/* Target Information */}
        <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(148, 163, 184, 0.05)', borderRadius: 2, border: '1px solid rgba(148, 163, 184, 0.1)' }}>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 2 }}>
            <Box>
              <Typography variant="body2" color="text.secondary">Target</Typography>
              <Typography variant="h6" fontWeight="bold">{report.target || 'N/A'}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">Analysis Depth</Typography>
              <Chip label={report.analysis_depth || 'Standard'} size="small" sx={{ mt: 0.5 }} />
            </Box>
            {report.timestamp && (
              <Box>
                <Typography variant="body2" color="text.secondary">Timestamp</Typography>
                <Typography variant="body2">{new Date(report.timestamp).toLocaleString()}</Typography>
              </Box>
            )}
            {report.data_freshness && (
              <Box>
                <Typography variant="body2" color="text.secondary">Data Freshness</Typography>
                <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>{report.data_freshness}</Typography>
              </Box>
            )}
          </Box>
        </Box>

        {/* Domain/IP Information */}
        {report.domain_ip_information && (
          <Accordion defaultExpanded sx={{ mb: 2, bgcolor: 'rgba(30, 41, 59, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'rgba(148, 163, 184, 0.8)' }} />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <DomainIcon sx={{ color: '#667eea' }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  Domain & IP Information
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {report.domain_ip_information.findings && report.domain_ip_information.findings.map((finding: any, idx: number) => (
                <Card key={idx} sx={{ mb: 2, bgcolor: 'rgba(15, 23, 42, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <InfoIcon sx={{ color: '#667eea', fontSize: 20 }} />
                      <Typography variant="subtitle2" fontWeight="bold">{finding.description}</Typography>
                      <Chip label={finding.confidence} size="small" color={finding.confidence === 'High' ? 'success' : 'info'} />
                    </Box>
                    {finding.details && (
                      <Box>
                        {finding.details.ip_addresses && (
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">IP Addresses</Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                              {finding.details.ip_addresses.map((ip: string, i: number) => (
                                <Chip key={i} label={ip} size="small" variant="outlined" />
                              ))}
                            </Box>
                          </Box>
                        )}
                        {finding.details.location && (
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">Location</Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                              <LocationIcon sx={{ fontSize: 16, color: '#667eea' }} />
                              <Typography variant="body2">
                                {finding.details.location.city}, {finding.details.location.region}, {finding.details.location.country}
                              </Typography>
                            </Box>
                          </Box>
                        )}
                        {finding.details.analysis && (
                          <Alert severity="info" sx={{ mt: 1, bgcolor: 'rgba(59, 130, 246, 0.1)' }}>
                            <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>{finding.details.analysis}</Typography>
                          </Alert>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
              {report.domain_ip_information.risks && report.domain_ip_information.risks.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <WarningIcon color="warning" sx={{ fontSize: 18 }} />
                    Risks
                  </Typography>
                  <List dense>
                    {report.domain_ip_information.risks.map((risk: any, idx: number) => (
                      <ListItem key={idx} sx={{ bgcolor: 'rgba(251, 191, 36, 0.1)', borderRadius: 1, mb: 0.5 }}>
                        <ListItemIcon>
                          <WarningIcon color="warning" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary={risk.description}
                          secondary={risk.analysis}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Social Media Presence */}
        {report.social_media_presence && (
          <Accordion sx={{ mb: 2, bgcolor: 'rgba(30, 41, 59, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'rgba(148, 163, 184, 0.8)' }} />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <PublicIcon sx={{ color: '#667eea' }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  Social Media Presence
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {report.social_media_presence.findings && report.social_media_presence.findings.map((finding: any, idx: number) => (
                <Card key={idx} sx={{ mb: 2, bgcolor: 'rgba(15, 23, 42, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
                  <CardContent>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>{finding.description}</Typography>
                    {finding.details && (
                      <Box>
                        {finding.details.platforms && (
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">Platforms</Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                              {finding.details.platforms.map((platform: string, i: number) => (
                                <Chip key={i} label={platform} size="small" variant="outlined" />
                              ))}
                            </Box>
                          </Box>
                        )}
                        {finding.details.analysis && (
                          <Typography variant="body2" sx={{ mt: 1, fontSize: '0.875rem' }}>{finding.details.analysis}</Typography>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Digital Footprint */}
        {report.digital_footprint && (
          <Accordion sx={{ mb: 2, bgcolor: 'rgba(30, 41, 59, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'rgba(148, 163, 184, 0.8)' }} />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <LanguageIcon sx={{ color: '#667eea' }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  Digital Footprint
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {report.digital_footprint.findings && report.digital_footprint.findings.map((finding: any, idx: number) => (
                <Card key={idx} sx={{ mb: 2, bgcolor: 'rgba(15, 23, 42, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
                  <CardContent>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>{finding.description}</Typography>
                    {finding.details && (
                      <Box>
                        {finding.details.technology_stack && (
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">Technology Stack</Typography>
                            <Table size="small" sx={{ mt: 1 }}>
                              <TableBody>
                                {finding.details.frontend && (
                                  <TableRow>
                                    <TableCell><strong>Frontend</strong></TableCell>
                                    <TableCell>
                                      {Array.isArray(finding.details.frontend) ? finding.details.frontend.join(', ') : finding.details.frontend}
                                    </TableCell>
                                  </TableRow>
                                )}
                                {finding.details.backend && (
                                  <TableRow>
                                    <TableCell><strong>Backend</strong></TableCell>
                                    <TableCell>
                                      {Array.isArray(finding.details.backend) ? finding.details.backend.join(', ') : finding.details.backend}
                                    </TableCell>
                                  </TableRow>
                                )}
                                {finding.details.infrastructure && (
                                  <TableRow>
                                    <TableCell><strong>Infrastructure</strong></TableCell>
                                    <TableCell>
                                      {Array.isArray(finding.details.infrastructure) ? finding.details.infrastructure.join(', ') : finding.details.infrastructure}
                                    </TableCell>
                                  </TableRow>
                                )}
                              </TableBody>
                            </Table>
                          </Box>
                        )}
                        {finding.details.analysis && (
                          <Typography variant="body2" sx={{ mt: 1, fontSize: '0.875rem' }}>{finding.details.analysis}</Typography>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Threat Intelligence */}
        {report.threat_intelligence && (
          <Accordion sx={{ mb: 2, bgcolor: 'rgba(30, 41, 59, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'rgba(148, 163, 184, 0.8)' }} />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <SecurityIcon sx={{ color: '#667eea' }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  Threat Intelligence
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {report.threat_intelligence.findings && report.threat_intelligence.findings.map((finding: any, idx: number) => (
                <Card key={idx} sx={{ mb: 2, bgcolor: 'rgba(15, 23, 42, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
                  <CardContent>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>{finding.description}</Typography>
                    {finding.details && (
                      <Box>
                        {finding.details.recent_incidents && (
                          <Alert severity={finding.details.recent_incidents.includes('No major') ? 'success' : 'warning'} sx={{ mt: 1 }}>
                            <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>{finding.details.recent_incidents}</Typography>
                          </Alert>
                        )}
                        {finding.details.analysis && (
                          <Typography variant="body2" sx={{ mt: 1, fontSize: '0.875rem' }}>{finding.details.analysis}</Typography>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
              {report.threat_intelligence.risks && report.threat_intelligence.risks.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <WarningIcon color="error" sx={{ fontSize: 18 }} />
                    Threat Risks
                  </Typography>
                  <List dense>
                    {report.threat_intelligence.risks.map((risk: any, idx: number) => (
                      <ListItem key={idx} sx={{ bgcolor: 'rgba(239, 68, 68, 0.1)', borderRadius: 1, mb: 0.5 }}>
                        <ListItemIcon>
                          <WarningIcon color="error" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary={risk.description}
                          secondary={risk.analysis}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Company Organization Intelligence */}
        {report.company_organization_intelligence && (
          <Accordion sx={{ mb: 2, bgcolor: 'rgba(30, 41, 59, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'rgba(148, 163, 184, 0.8)' }} />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <BusinessIcon sx={{ color: '#667eea' }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  Company & Organization Intelligence
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {report.company_organization_intelligence.findings && report.company_organization_intelligence.findings.map((finding: any, idx: number) => (
                <Card key={idx} sx={{ mb: 2, bgcolor: 'rgba(15, 23, 42, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
                  <CardContent>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>{finding.description}</Typography>
                    {finding.details && (
                      <Table size="small" sx={{ mt: 1 }}>
                        <TableBody>
                          {finding.details.legal_name && (
                            <TableRow>
                              <TableCell><strong>Legal Name</strong></TableCell>
                              <TableCell>{finding.details.legal_name}</TableCell>
                            </TableRow>
                          )}
                          {finding.details.incorporation && (
                            <TableRow>
                              <TableCell><strong>Incorporation</strong></TableCell>
                              <TableCell>{finding.details.incorporation}</TableCell>
                            </TableRow>
                          )}
                          {finding.details.headquarters && (
                            <TableRow>
                              <TableCell><strong>Headquarters</strong></TableCell>
                              <TableCell>{finding.details.headquarters}</TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    )}
                  </CardContent>
                </Card>
              ))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* News Media Coverage */}
        {report.news_media_coverage && (
          <Accordion sx={{ mb: 2, bgcolor: 'rgba(30, 41, 59, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'rgba(148, 163, 184, 0.8)' }} />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <LanguageIcon sx={{ color: '#667eea' }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  News & Media Coverage
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {report.news_media_coverage.findings && report.news_media_coverage.findings.map((finding: any, idx: number) => (
                <Card key={idx} sx={{ mb: 2, bgcolor: 'rgba(15, 23, 42, 0.5)', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
                  <CardContent>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>{finding.description}</Typography>
                    {finding.details && finding.details.topics && (
                      <Box>
                        <Typography variant="caption" color="text.secondary">Topics</Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                          {finding.details.topics.map((topic: string, i: number) => (
                            <Chip key={i} label={topic} size="small" variant="outlined" />
                          ))}
                        </Box>
                        {finding.details.analysis && (
                          <Typography variant="body2" sx={{ mt: 1, fontSize: '0.875rem' }}>{finding.details.analysis}</Typography>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Overall Risks */}
        {report.overall_risks && report.overall_risks.length > 0 && (
          <Alert severity="warning" sx={{ mb: 2, bgcolor: 'rgba(251, 191, 36, 0.1)', border: '1px solid rgba(251, 191, 36, 0.2)' }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Overall Risks
            </Typography>
            <List dense>
              {report.overall_risks.map((risk: any, idx: number) => (
                <ListItem key={idx} sx={{ py: 0.5 }}>
                  <ListItemIcon>
                    <WarningIcon color="warning" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={risk.description}
                    secondary={risk.analysis}
                  />
                </ListItem>
              ))}
            </List>
          </Alert>
        )}

        {/* Actionable Recommendations */}
        {report.actionable_recommendations && report.actionable_recommendations.length > 0 && (
          <Card sx={{ bgcolor: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.2)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <CheckCircleIcon sx={{ color: '#22c55e' }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  Actionable Recommendations
                </Typography>
              </Box>
              <List>
                {report.actionable_recommendations.map((rec: any, idx: number) => (
                  <ListItem key={idx} sx={{ py: 1 }}>
                    <ListItemIcon>
                      <CheckCircleIcon color="success" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={rec.description}
                      secondary={rec.action}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        )}
      </CardContent>
    </Card>
  );
};

