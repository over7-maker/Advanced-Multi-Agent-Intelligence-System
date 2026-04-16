import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { formatApiErrorWithHints } from '../../lib/formatApiError';
import { apiService, type DeepHealthResponse, type Integration } from '../../services/api';
import { TopologyStrip } from './TopologyStrip';

export const LiveSystemPage: React.FC = () => {
  const [deep, setDeep] = useState<DeepHealthResponse | null>(null);
  const [live, setLive] = useState<Awaited<ReturnType<typeof apiService.getLiveMonitor>> | null>(null);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [probes, setProbes] = useState<Awaited<ReturnType<typeof apiService.getOperatorProbes>> | null>(null);
  const [topology, setTopology] = useState<Awaited<ReturnType<typeof apiService.getTopologyHotspots>> | null>(
    null,
  );
  const [integNote, setIntegNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    setError(null);
    setIntegNote(null);
    try {
      const [d, l, p, th, integ] = await Promise.all([
        apiService.getDeepHealth({ include_opa: false, http_fail_if_unhealthy: false }),
        apiService.getLiveMonitor(),
        apiService.getOperatorProbes().catch(() => ({ checks: [] })),
        apiService.getTopologyHotspots().catch(() => ({ available: false, hotspots: [] })),
        apiService.listIntegrations({ limit: 50 }).catch((e) => {
          setIntegNote(formatApiErrorWithHints(e));
          return { integrations: [] as Integration[], total: 0 };
        }),
      ]);
      setDeep(d);
      setLive(l);
      setProbes(p);
      setTopology(th);
      setIntegrations(integ.integrations || []);
    } catch (e) {
      setError(formatApiErrorWithHints(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  if (loading && !deep && !live) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>
          Loading live system probes…
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Live system
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Combined deep health and live monitor — operator glass pane. Data is real; empty sections mean the API returned no rows.
        n8n UI vs webhook hosts: <code>docs/frontend/ENV_AND_INTEGRATION.md</code> § n8n (F7-4).
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Topology (template + probe overlay)
          </Typography>
          {topology?.summary?.postgres_counts_available && topology.summary.postgres_task_counts && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Postgres tasks — active {topology.summary.postgres_task_counts.active_tasks}, failed{' '}
              {topology.summary.postgres_task_counts.failed_tasks}, total {topology.summary.postgres_task_counts.total_tasks}
              {topology.summary.orchestrator_queue_depth != null && (
                <> · orchestrator queue {topology.summary.orchestrator_queue_depth}</>
              )}
            </Typography>
          )}
          {topology?.summary && !topology.summary.postgres_counts_available && (
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
              Postgres task counts unavailable (optional DB); hotspots still use orchestrator queue when available.
            </Typography>
          )}
          <TopologyStrip deep={deep} hotspots={topology?.available ? topology.hotspots : undefined} />
          {topology?.available &&
            (topology.hotspots || []).filter((h) => String(h.category || '').toLowerCase() === 'incident').length > 0 && (
              <Alert severity="error" sx={{ mt: 1 }}>
                <Typography variant="body2">
                  Incident overlays active from failed task records. Use Incidents for triage details and remediation.
                </Typography>
              </Alert>
            )}
        </CardContent>
      </Card>

      {topology?.available &&
        (topology.hotspots || []).some((h) => {
          const s = String(h.severity || '').toLowerCase();
          return s === 'critical' || s === 'error' || s === 'high';
        }) && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Elevated topology hotspots — open Incidents to triage failed runs.
            </Typography>
            <Button component={RouterLink} to="/incidents" size="small" variant="outlined">
              Go to Incidents
            </Button>
          </Alert>
        )}

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Operator probes (real endpoints)
          </Typography>
          <Stack direction="row" flexWrap="wrap" gap={1}>
            {(probes?.checks || []).map((c) => {
              const configured = c.configured !== false;
              const label =
                c.status === 'not_configured' || !configured
                  ? `${c.target}: not configured`
                  : `${c.target}: ${c.status}${c.latency_ms != null ? ` · ${c.latency_ms}ms` : ''}`;
              const color =
                c.status === 'not_configured' || !configured
                  ? 'default'
                  : c.ok === true
                    ? 'success'
                    : c.status === 'degraded'
                      ? 'warning'
                      : 'default';
              return (
                <Chip
                  key={c.target}
                  size="small"
                  label={label}
                  color={color}
                  variant="outlined"
                />
              );
            })}
            {!probes?.checks?.length && <Chip size="small" label="No probe checks returned" variant="outlined" />}
          </Stack>
        </CardContent>
      </Card>

      {deep && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="h6">Deep health</Typography>
              <Chip size="small" label={deep.status} color={deep.status === 'healthy' ? 'success' : 'warning'} />
              <Typography variant="caption" color="text.secondary">
                {deep.elapsed_ms} ms
              </Typography>
            </Stack>
            <Stack spacing={0.5}>
              {(deep.checks ?? []).slice(0, 40).map((c) => (
                <Stack key={c.id} direction="row" spacing={1} alignItems="center">
                  <Chip size="small" label={c.status} variant="outlined" />
                  <Typography variant="body2" fontFamily="monospace">
                    {c.id}
                  </Typography>
                  {c.detail && (
                    <Typography variant="caption" color="text.secondary">
                      {c.detail}
                    </Typography>
                  )}
                </Stack>
              ))}
            </Stack>
          </CardContent>
        </Card>
      )}

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Automation & integrations (real registry)
          </Typography>
          {integNote && (
            <Alert severity="info" sx={{ mb: 1 }}>
              {integNote}
            </Alert>
          )}
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            n8n / MCP / Tier-3 connectors appear when configured in <code>/integrations</code>. This is honest
            empty when none exist — no synthetic &quot;connected&quot; badges (F9).
          </Typography>
          <Stack direction="row" flexWrap="wrap" gap={1}>
            {integrations.length === 0 && !integNote ? (
              <Chip size="small" label="No integrations returned" variant="outlined" />
            ) : null}
            {integrations.map((it) => {
              const t = (it.platform || '').toLowerCase();
              const isN8n = t.includes('n8n');
              const isMcp = t.includes('mcp');
              return (
                <Chip
                  key={it.integration_id}
                  size="small"
                  label={`${it.platform} (${it.status})`}
                  color={isN8n || isMcp ? 'primary' : 'default'}
                  variant="outlined"
                />
              );
            })}
          </Stack>
        </CardContent>
      </Card>

      {live && (
        <Card>
          <CardContent>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="h6">Live monitor</Typography>
              <Chip size="small" label={live.status} />
            </Stack>
            <Stack spacing={1}>
              {live.items?.map((item) => (
                <Stack key={item.id} direction="row" spacing={1} alignItems="flex-start">
                  <Chip size="small" label={item.status} />
                  <Box>
                    <Typography variant="body2" fontWeight={600}>
                      {item.label}
                    </Typography>
                    {item.detail && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        {item.detail}
                      </Typography>
                    )}
                  </Box>
                </Stack>
              ))}
            </Stack>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};
