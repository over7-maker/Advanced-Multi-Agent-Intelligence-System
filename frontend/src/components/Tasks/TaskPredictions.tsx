/**
 * Task Predictions Component (Phase 6.2)
 * Displays ML predictions when creating tasks
 */

import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { apiService, TaskPrediction } from '../../services/api';

interface TaskPredictionsProps {
  taskType: string;
  target: string;
  parameters?: Record<string, any>;
}

export const TaskPredictions = ({ taskType, target, parameters }: TaskPredictionsProps) => {
  const [prediction, setPrediction] = useState<TaskPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPrediction = async () => {
      if (!taskType || !target) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const data = await apiService.predictTask({
          task_type: taskType,
          target: target,
          parameters: parameters || {},
        });
        setPrediction(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch prediction');
        console.error('Failed to fetch prediction:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
  }, [taskType, target, parameters]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100px">
        <CircularProgress size={24} />
        <Typography variant="body2" sx={{ ml: 2 }}>
          Generating prediction...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="warning">
        Prediction unavailable: {error}
      </Alert>
    );
  }

  if (!prediction) {
    return null;
  }

  const successColor = prediction.success_probability >= 0.8 ? 'success' :
                       prediction.success_probability >= 0.5 ? 'warning' : 'error';

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          ML Prediction
        </Typography>

        <Box sx={{ mt: 2 }}>
          {/* Success Probability */}
          <Box sx={{ mb: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Success Probability
              </Typography>
              <Chip
                label={`${(prediction.success_probability * 100).toFixed(1)}%`}
                color={successColor}
                size="small"
              />
            </Box>
            <LinearProgress
              variant="determinate"
              value={prediction.success_probability * 100}
              color={successColor}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>

          {/* Estimated Duration */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Estimated Duration
            </Typography>
            <Typography variant="h6">
              {prediction.estimated_duration.toFixed(1)} seconds
            </Typography>
          </Box>

          {/* Quality Score Prediction */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Predicted Quality Score
            </Typography>
            <Typography variant="h6">
              {(prediction.quality_score_prediction * 100).toFixed(1)}%
            </Typography>
          </Box>

          {/* Confidence */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Confidence Level
            </Typography>
            <Typography variant="body1">
              {(prediction.confidence * 100).toFixed(1)}%
            </Typography>
          </Box>

          {/* Recommended Agents */}
          {prediction.recommended_agents && prediction.recommended_agents.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Recommended Agents
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {prediction.recommended_agents.map((agent, index) => (
                  <Chip
                    key={index}
                    label={`${agent.agent_name} (${(agent.expertise_score * 100).toFixed(0)}%)`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}

          {/* Risk Factors */}
          {prediction.risk_factors && prediction.risk_factors.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Risk Factors
              </Typography>
              <List dense>
                {prediction.risk_factors.map((risk, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemText
                      primary={risk}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Optimization Suggestions */}
          {prediction.optimization_suggestions && prediction.optimization_suggestions.length > 0 && (
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Optimization Suggestions
              </Typography>
              <List dense>
                {prediction.optimization_suggestions.map((suggestion, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemText
                      primary={suggestion}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

