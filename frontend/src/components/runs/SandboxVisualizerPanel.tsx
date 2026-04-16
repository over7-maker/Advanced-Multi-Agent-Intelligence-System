import React, { useEffect, useMemo, useState } from 'react';
import { Alert, Box, Card, CardContent, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { formatApiErrorDetail } from '../../lib/formatApiError';
import { apiService, type Task } from '../../services/api';

export interface SandboxVisualizerPanelProps {
  task: Task | null;
}

export const SandboxVisualizerPanel: React.FC<SandboxVisualizerPanelProps> = ({ task }) => {
  const [telemetryErr, setTelemetryErr] = useState<string | null>(null);
  const [telemetry, setTelemetry] = useState<Awaited<ReturnType<typeof apiService.getSandboxTelemetry>> | null>(
    null,
  );

  const tid = task?.task_id || task?.id;

  const hints = useMemo(() => {
    const r = task?.result ?? task?.output;
    if (!r || typeof r !== 'object') return null;
    const keys = Object.keys(r).filter((k) => /sandbox|workspace|tool|path/i.test(k));
    return keys.length ? keys : null;
  }, [task]);

  useEffect(() => {
    if (!tid) {
      setTelemetry(null);
      setTelemetryErr(null);
      return;
    }
    let cancelled = false;
    const run = async () => {
      setTelemetryErr(null);
      try {
        const t = await apiService.getSandboxTelemetry(String(tid));
        if (!cancelled) setTelemetry(t);
      } catch (e) {
        if (!cancelled) setTelemetryErr(formatApiErrorDetail(e));
      }
    };
    void run();
    return () => {
      cancelled = true;
    };
  }, [tid]);

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Sandboxes
        </Typography>
        <Alert severity="info" sx={{ mb: 1 }}>
          RunEvent-derived telemetry when available (<code>GET /api/v1/tasks/&#123;id&#125;/sandbox-telemetry</code>).
          No synthetic CPU or disk metrics.
        </Alert>
        {telemetryErr && (
          <Alert severity="warning" sx={{ mb: 1 }}>
            {telemetryErr}
          </Alert>
        )}
        {telemetry && (
          <Box sx={{ mb: 1 }}>
            <Typography variant="body2">
              Source: {telemetry.source} — sandbox events: {telemetry.sandbox_event_count}, tool events:{' '}
              {telemetry.tool_event_count}
            </Typography>
            {(telemetry.first_event_iso || telemetry.last_event_iso) && (
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                First: {telemetry.first_event_iso || '—'} · Last: {telemetry.last_event_iso || '—'}
              </Typography>
            )}
            {telemetry.event_type_counts && Object.keys(telemetry.event_type_counts).length > 0 && (
              <Stack direction="row" flexWrap="wrap" gap={0.5} sx={{ mt: 1 }}>
                {Object.entries(telemetry.event_type_counts).map(([k, v]) => (
                  <Typography key={k} variant="caption" component="span" sx={{ fontFamily: 'monospace' }}>
                    {k}: {v}
                  </Typography>
                ))}
              </Stack>
            )}
            {!telemetry.available && (
              <Typography variant="caption" color="text.secondary" display="block">
                No sandbox/tool RunEvents recorded for this task yet.
              </Typography>
            )}
            {Array.isArray(telemetry.recent_sandbox_tool_events) && telemetry.recent_sandbox_tool_events.length > 0 && (
              <Table size="small" sx={{ mt: 1 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Summary</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {telemetry.recent_sandbox_tool_events.map((row, i) => (
                    <TableRow key={`${row.timestamp}-${row.event_type}-${i}`}>
                      <TableCell sx={{ whiteSpace: 'nowrap', fontFamily: 'monospace', fontSize: 12 }}>
                        {row.timestamp || '—'}
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>{row.event_type}</TableCell>
                      <TableCell sx={{ fontSize: 12 }}>{row.summary}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Box>
        )}
        {hints && (
          <Typography variant="body2" fontFamily="monospace">
            Result keys: {hints.join(', ')}
          </Typography>
        )}
        {!hints && !telemetry?.available && !telemetryErr && (
          <Typography variant="body2" color="text.secondary">
            No sandbox-shaped keys in <code>result</code>/<code>output</code> for this run.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};
