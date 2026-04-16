// frontend/src/components/Tasks/CreateTask.tsx
import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiService, TaskPrediction } from '../../services/api';

const toErrorMessage = (err: any): string => {
  const data = err?.response?.data;
  // Pydantic validation errors come as array of {type, msg, ...}
  if (Array.isArray(data)) {
    return data.map((e: any) => e?.msg || JSON.stringify(e)).join(', ');
  }
  if (typeof data === 'object' && data !== null) {
    return data.detail || data.message || JSON.stringify(data);
  }
  if (typeof data === 'string') return data;
  return 'Failed to create task';
};

export const CreateTask: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    task_type: 'security_scan',
    target: '',
    priority: 5,
    parameters: {},
  });
  const [prediction, setPrediction] = useState<TaskPrediction | null>(null);
  const [predicting, setPredicting] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setPrediction(null);
    setError(null);
  };

  const handlePredict = async () => {
    if (!formData.task_type || !formData.target) {
      setError('Please fill in Task Type and Target before predicting');
      return;
    }

    try {
      setPredicting(true);
      setError(null);
      const predictionResult = await apiService.predictTask({
        task_type: formData.task_type,
        target: formData.target,
        parameters: formData.parameters,
      });
      setPrediction(predictionResult);
    } catch (err) {
      setError('Failed to generate prediction');
      console.error('Prediction failed:', err);
    } finally {
      setPredicting(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.title || !formData.description || !formData.task_type || !formData.target) {
      setError('Please fill in all required fields (Title, Description, Task Type, Target)');
      return;
    }

    try {
      setCreating(true);
      setError(null);
      const task = await apiService.createTask(formData);
      setSuccess(true);
      
      // Redirect to task detail page after 1 second
      setTimeout(() => {
        navigate(`/tasks/${task.id || task.task_id}`);
      }, 1000);
    } catch (err: any) {
      setError(toErrorMessage(err));
      console.error('Task creation failed:', err);
    } finally {
      setCreating(false);
    }
  };

  const handleBack = () => {
    navigate('/tasks');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          sx={{ mr: 2 }}
        >
          Back to Tasks
        </Button>
        <Typography variant="h4">Create New Task</Typography>
      </Box>

      <Card>
        <CardContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Task created successfully! Redirecting...
            </Alert>
          )}

          <Grid container spacing={3}>            {/* @ts-expect-error Material-UI v7 Grid type issue - item prop not recognized */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                required
                disabled={creating}
              />
            </Grid>            {/* @ts-expect-error Material-UI v7 Grid type issue - item prop not recognized */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                multiline
                rows={3}
                disabled={creating}
              />
            </Grid>            {/* @ts-expect-error Material-UI v7 Grid type issue - item prop not recognized */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Task Type</InputLabel>
                <Select
                  value={formData.task_type}
                  label="Task Type"
                  onChange={(e) => handleInputChange('task_type', e.target.value)}
                  disabled={creating}
                >
                  <MenuItem value="security_scan">Security Scan</MenuItem>
                  <MenuItem value="security_audit">Security Audit</MenuItem>
                  <MenuItem value="code_analysis">Code Analysis</MenuItem>
                  <MenuItem value="intelligence_gathering">Intelligence Gathering</MenuItem>
                  <MenuItem value="osint_investigation">OSINT Investigation</MenuItem>
                  <MenuItem value="osint_collection">OSINT Collection</MenuItem>
                  <MenuItem value="performance_analysis">Performance Analysis</MenuItem>
                  <MenuItem value="performance_monitoring">Performance Monitoring</MenuItem>
                  <MenuItem value="performance_optimization">Performance Optimization</MenuItem>
                  <MenuItem value="documentation">Documentation</MenuItem>
                  <MenuItem value="documentation_generation">Documentation Generation</MenuItem>
                  <MenuItem value="testing">Testing</MenuItem>
                  <MenuItem value="testing_coordination">Testing Coordination</MenuItem>
                  <MenuItem value="deployment">Deployment</MenuItem>
                  <MenuItem value="monitoring">Monitoring</MenuItem>
                  <MenuItem value="investigation">Investigation</MenuItem>
                  <MenuItem value="forensics">Forensics</MenuItem>
                  <MenuItem value="data_analysis">Data Analysis</MenuItem>
                  <MenuItem value="reverse_engineering">Reverse Engineering</MenuItem>
                  <MenuItem value="metadata_extraction">Metadata Extraction</MenuItem>
                  <MenuItem value="reporting">Reporting</MenuItem>
                  <MenuItem value="threat_analysis">Threat Analysis</MenuItem>
                  <MenuItem value="incident_response">Incident Response</MenuItem>
                  <MenuItem value="compliance_audit">Compliance Audit</MenuItem>
                  <MenuItem value="technology_monitoring">Technology Monitoring</MenuItem>
                  <MenuItem value="social_media_monitoring">Social Media Monitoring</MenuItem>
                  <MenuItem value="threat_intelligence">Threat Intelligence</MenuItem>
                  <MenuItem value="dark_web_monitoring">Dark Web Monitoring</MenuItem>
                </Select>
              </FormControl>
            </Grid>            {/* @ts-expect-error Material-UI v7 Grid type issue - item prop not recognized */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Target"
                value={formData.target}
                onChange={(e) => handleInputChange('target', e.target.value)}
                required
                placeholder="URL, repository, system, etc."
                disabled={creating}
              />
            </Grid>            {/* @ts-expect-error Material-UI v7 Grid type issue - item prop not recognized */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Priority"
                type="number"
                value={formData.priority}
                onChange={(e) => handleInputChange('priority', parseInt(e.target.value, 10) || 5)}
                inputProps={{ min: 1, max: 10 }}
                disabled={creating}
                helperText="1 (lowest) to 10 (highest)"
              />
            </Grid>            {/* @ts-expect-error Material-UI v7 Grid type issue - item prop not recognized */}
            <Grid item xs={12} sm={6}>
              <Button
                fullWidth
                variant="outlined"
                onClick={handlePredict}
                disabled={predicting || creating || !formData.task_type || !formData.target}
                sx={{ height: '56px' }}
              >
                {predicting ? <CircularProgress size={24} /> : 'Predict Task Outcome'}
              </Button>
            </Grid>

            {prediction && (
              <>
                {/* @ts-ignore Material-UI v7 Grid type issue */}
                <Grid item xs={12}>
                  <Card variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Typography variant="h6" gutterBottom>
                      Prediction Results
                    </Typography>
                    <Grid container spacing={2}>
                      {/* @ts-ignore Material-UI v7 Grid type issue */}
                      <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="body2" color="textSecondary">
                          Success Probability
                        </Typography>
                        <Typography variant="h6">
                          {(prediction.success_probability * 100).toFixed(1)}%
                        </Typography>
                      </Grid>
                      {/* @ts-ignore Material-UI v7 Grid type issue */}
                      <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="body2" color="textSecondary">
                          Estimated Duration
                        </Typography>
                        <Typography variant="h6">
                          {prediction.estimated_duration.toFixed(1)}s
                        </Typography>
                      </Grid>
                      {/* @ts-ignore Material-UI v7 Grid type issue */}
                      <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="body2" color="textSecondary">
                          Quality Score
                        </Typography>
                        <Typography variant="h6">
                          {prediction.quality_score_prediction.toFixed(2)}
                        </Typography>
                      </Grid>
                      {/* @ts-ignore Material-UI v7 Grid type issue */}
                      <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="body2" color="textSecondary">
                          Confidence
                        </Typography>
                        <Typography variant="h6">
                          {(prediction.confidence * 100).toFixed(1)}%
                        </Typography>
                      </Grid>
                      {prediction.risk_factors && prediction.risk_factors.length > 0 && (
                        <>
                          {/* @ts-ignore Material-UI v7 Grid type issue */}
                          <Grid item xs={12}>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                              Risk Factors:
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                              {prediction.risk_factors.map((risk, idx) => (
                                <Chip key={idx} label={risk} color="warning" size="small" />
                              ))}
                            </Box>
                          </Grid>
                        </>
                      )}
                      {prediction.optimization_suggestions && prediction.optimization_suggestions.length > 0 && (
                        <>
                          {/* @ts-ignore Material-UI v7 Grid type issue */}
                          <Grid item xs={12}>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                              Optimization Suggestions:
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                              {prediction.optimization_suggestions.map((suggestion, idx) => (
                                <Chip key={idx} label={suggestion} color="info" size="small" />
                              ))}
                            </Box>
                          </Grid>
                        </>
                      )}
                    </Grid>
                  </Card>
                </Grid>
              </>
            )}            {/* @ts-expect-error Material-UI v7 Grid type issue - item prop not recognized */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={handleBack}
                  disabled={creating}
                >
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  onClick={handleCreate}
                  disabled={creating || !formData.title || !formData.task_type || !formData.target}
                >
                  {creating ? <CircularProgress size={24} /> : 'Create Task'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

