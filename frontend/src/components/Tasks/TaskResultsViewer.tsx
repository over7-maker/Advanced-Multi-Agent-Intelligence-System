// frontend/src/components/Tasks/TaskResultsViewer.tsx
import {
    Business as BusinessIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    ExpandMore as ExpandMoreIcon,
    Info as InfoIcon,
    Lock as LockIcon,
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
    Grid,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Typography
} from '@mui/material';
import React from 'react';

interface TaskResultsViewerProps {
  result: any;
  taskType?: string;
}

export const TaskResultsViewer: React.FC<TaskResultsViewerProps> = ({ result, taskType }) => {
  if (!result) {
    return (
      <Alert severity="info">
        <Typography variant="body2">No results available</Typography>
      </Alert>
    );
  }

  // Extract agent results
  const agentResults = result.agent_results || {};
  const securityExpertResult = agentResults.security_expert;
  const intelligenceGatheringResult = agentResults.intelligence_gathering;

  // Parse security scan results
  const parseSecurityData = (data: any) => {
    if (!data) return null;
    
    try {
      // Try to extract from nested structure
      const output = data.output?.data || data.output || data;
      
      // Try to parse JSON if it's a string
      if (typeof output === 'string') {
        // Extract JSON from markdown code blocks
        const jsonMatch = output.match(/```json\n([\s\S]*?)\n```/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[1]);
        }
        // Try direct parse
        try {
          return JSON.parse(output);
        } catch {
          return null;
        }
      }
      
      return output;
    } catch (e) {
      console.error('Failed to parse security data:', e);
      return null;
    }
  };

  const securityData = securityExpertResult ? parseSecurityData(securityExpertResult) : null;
  const intelData = intelligenceGatheringResult?.output?.intelligence_report || null;

  const getSeverityColor = (severity: string): 'error' | 'warning' | 'info' | 'success' => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'success';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high':
        return <ErrorIcon color="error" />;
      case 'medium':
        return <WarningIcon color="warning" />;
      case 'low':
        return <InfoIcon color="info" />;
      default:
        return <CheckCircleIcon color="success" />;
    }
  };

  return (
    <Box>
      {/* Summary Card */}
      <Card sx={{ mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <CheckCircleIcon sx={{ fontSize: 40 }} />
            <Box>
              <Typography variant="h5" fontWeight="bold">
                Task Completed Successfully
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                {result.success ? 'All agents completed execution' : 'Some issues detected'}
              </Typography>
            </Box>
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Quality Score</Typography>
              <Typography variant="h6" fontWeight="bold">
                {((result.quality_score || 0) * 100).toFixed(1)}%
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Execution Time</Typography>
              <Typography variant="h6" fontWeight="bold">
                {(result.execution_time || 0).toFixed(1)}s
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Total Cost</Typography>
              <Typography variant="h6" fontWeight="bold">
                ${(result.total_cost_usd || 0).toFixed(4)}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Security Scan Results */}
      {securityData && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
              <SecurityIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Security Analysis Results
              </Typography>
            </Box>

            {/* Risk Rating */}
            {securityData.risk_rating && (
              <Alert 
                severity={securityData.risk_rating.toLowerCase() === 'low' ? 'success' : 'warning'} 
                sx={{ mb: 3 }}
              >
                <Typography variant="subtitle1" fontWeight="bold">
                  Overall Risk Rating: {securityData.risk_rating}
                </Typography>
              </Alert>
            )}

            {/* Vulnerabilities */}
            {securityData.vulnerabilities && Array.isArray(securityData.vulnerabilities) && securityData.vulnerabilities.length > 0 && (
              <Accordion defaultExpanded sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                    <WarningIcon color="error" />
                    <Typography variant="subtitle1" fontWeight="bold">
                      Vulnerabilities Found ({securityData.vulnerabilities.length})
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>ID</TableCell>
                        <TableCell>Severity</TableCell>
                        <TableCell>Title</TableCell>
                        <TableCell>CVSS Score</TableCell>
                        <TableCell>Location</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {securityData.vulnerabilities.map((vuln: any, idx: number) => (
                        <TableRow key={idx}>
                          <TableCell>{vuln.id || `VULN-${idx + 1}`}</TableCell>
                          <TableCell>
                            <Chip
                              label={vuln.severity || 'Unknown'}
                              color={getSeverityColor(vuln.severity)}
                              size="small"
                              icon={getSeverityIcon(vuln.severity)}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {vuln.title || 'Untitled Vulnerability'}
                            </Typography>
                            {vuln.description && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                                {vuln.description}
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={vuln.cvss_score?.toFixed(1) || 'N/A'}
                              size="small"
                              color={vuln.cvss_score >= 7 ? 'error' : vuln.cvss_score >= 4 ? 'warning' : 'info'}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption" sx={{ wordBreak: 'break-all' }}>
                              {vuln.location || 'N/A'}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  
                  {/* Detailed Vulnerability Info */}
                  {securityData.vulnerabilities.map((vuln: any, idx: number) => (
                    <Accordion key={idx} sx={{ mt: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="body2" fontWeight="medium">
                          {vuln.title || vuln.id} - {vuln.severity}
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box>
                          {vuln.description && (
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" gutterBottom>Description</Typography>
                              <Typography variant="body2">{vuln.description}</Typography>
                            </Box>
                          )}
                          {vuln.cwe && (
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" gutterBottom>CWE</Typography>
                              <Chip label={vuln.cwe} size="small" />
                            </Box>
                          )}
                          {vuln.remediation && (
                            <Box>
                              <Typography variant="subtitle2" gutterBottom>Remediation</Typography>
                              <Alert severity="info">
                                <Typography variant="body2">{vuln.remediation}</Typography>
                              </Alert>
                            </Box>
                          )}
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </AccordionDetails>
              </Accordion>
            )}

            {/* SSL Analysis */}
            {securityData.ssl_analysis && (
              <Accordion sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LockIcon />
                    <Typography variant="subtitle1" fontWeight="bold">SSL/TLS Analysis</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Certificate Status</Typography>
                      <Chip
                        label={securityData.ssl_analysis.valid ? 'Valid' : 'Invalid'}
                        color={securityData.ssl_analysis.valid ? 'success' : 'error'}
                        sx={{ mt: 1 }}
                      />
                    </Grid>
                    {securityData.ssl_analysis.expires && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">Expires</Typography>
                        <Typography variant="body2" fontWeight="medium" sx={{ mt: 1 }}>
                          {new Date(securityData.ssl_analysis.expires).toLocaleDateString()}
                        </Typography>
                      </Grid>
                    )}
                    {securityData.ssl_analysis.issues && securityData.ssl_analysis.issues.length > 0 && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" gutterBottom>Issues Found</Typography>
                        <List dense>
                          {securityData.ssl_analysis.issues.map((issue: string, idx: number) => (
                            <ListItem key={idx}>
                              <ListItemIcon>
                                <WarningIcon color="warning" fontSize="small" />
                              </ListItemIcon>
                              <ListItemText primary={issue} />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Security Headers */}
            {securityData.security_headers && (
              <Accordion sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <PublicIcon />
                    <Typography variant="subtitle1" fontWeight="bold">Security Headers</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {securityData.security_headers.present && securityData.security_headers.present.length > 0 && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" gutterBottom color="success.main">
                          Present Headers
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                          {securityData.security_headers.present.map((header: string, idx: number) => (
                            <Chip key={idx} label={header} size="small" color="success" variant="outlined" />
                          ))}
                        </Box>
                      </Grid>
                    )}
                    {securityData.security_headers.missing && securityData.security_headers.missing.length > 0 && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" gutterBottom color="error.main">
                          Missing Headers
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                          {securityData.security_headers.missing.map((header: string, idx: number) => (
                            <Chip key={idx} label={header} size="small" color="error" variant="outlined" />
                          ))}
                        </Box>
                      </Grid>
                    )}
                    {securityData.security_headers.issues && securityData.security_headers.issues.length > 0 && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" gutterBottom>Issues</Typography>
                        <List dense>
                          {securityData.security_headers.issues.map((issue: string, idx: number) => (
                            <ListItem key={idx}>
                              <ListItemIcon>
                                <WarningIcon color="warning" fontSize="small" />
                              </ListItemIcon>
                              <ListItemText primary={issue} />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Technology Stack */}
            {securityData.technology_stack && (
              <Accordion sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <BusinessIcon />
                    <Typography variant="subtitle1" fontWeight="bold">Technology Stack</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Table size="small">
                    <TableBody>
                      {securityData.technology_stack.server && (
                        <TableRow>
                          <TableCell><strong>Server</strong></TableCell>
                          <TableCell>{securityData.technology_stack.server}</TableCell>
                        </TableRow>
                      )}
                      {securityData.technology_stack.backend && (
                        <TableRow>
                          <TableCell><strong>Backend</strong></TableCell>
                          <TableCell>{securityData.technology_stack.backend}</TableCell>
                        </TableRow>
                      )}
                      {securityData.technology_stack.framework && (
                        <TableRow>
                          <TableCell><strong>Framework</strong></TableCell>
                          <TableCell>{securityData.technology_stack.framework}</TableCell>
                        </TableRow>
                      )}
                      {securityData.technology_stack.known_cves && Array.isArray(securityData.technology_stack.known_cves) && (
                        <TableRow>
                          <TableCell><strong>Known CVEs</strong></TableCell>
                          <TableCell>
                            {securityData.technology_stack.known_cves.length > 0 ? (
                              <List dense>
                                {securityData.technology_stack.known_cves.map((cve: string, idx: number) => (
                                  <ListItem key={idx} sx={{ py: 0 }}>
                                    <Typography variant="caption">{cve}</Typography>
                                  </ListItem>
                                ))}
                              </List>
                            ) : (
                              <Typography variant="body2" color="success.main">None reported</Typography>
                            )}
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Recommendations */}
            {securityData.recommendations && Array.isArray(securityData.recommendations) && securityData.recommendations.length > 0 && (
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <InfoIcon />
                    <Typography variant="subtitle1" fontWeight="bold">
                      Recommendations ({securityData.recommendations.length})
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    {securityData.recommendations.map((rec: string, idx: number) => (
                      <ListItem key={idx}>
                        <ListItemIcon>
                          <CheckCircleIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={rec} />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Summary */}
            {securityData.summary && (
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>Summary</Typography>
                <Typography variant="body2">{securityData.summary}</Typography>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Intelligence Gathering Results */}
      {intelData && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
              <TimelineIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Intelligence Gathering Results
              </Typography>
            </Box>

            {/* Parse intel data if it's in a nested structure */}
            {intelData.intel_gathering_report && (
              <Box>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Intelligence Report
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Comprehensive intelligence gathering completed for the target.
                </Typography>
                {/* Add more detailed intel display here if needed */}
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Agent Performance Summary */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Agent Performance
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(agentResults).map(([agentId, agentResult]: [string, any]) => (
              <Grid item xs={12} sm={6} key={agentId}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                      {agentId.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">Status</Typography>
                        <Chip
                          label={agentResult.success ? 'Success' : 'Failed'}
                          color={agentResult.success ? 'success' : 'error'}
                          size="small"
                        />
                      </Box>
                      {agentResult.duration && (
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2" color="text.secondary">Duration</Typography>
                          <Typography variant="body2">{agentResult.duration.toFixed(2)}s</Typography>
                        </Box>
                      )}
                      {agentResult.quality_score && (
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2" color="text.secondary">Quality</Typography>
                          <Typography variant="body2">
                            {(agentResult.quality_score * 100).toFixed(1)}%
                          </Typography>
                        </Box>
                      )}
                      {agentResult.cost_usd !== undefined && (
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">Cost</Typography>
                          <Typography variant="body2">${agentResult.cost_usd.toFixed(4)}</Typography>
                        </Box>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

