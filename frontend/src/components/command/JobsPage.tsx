import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { formatApiErrorWithHints } from '../../lib/formatApiError';
import { apiService } from '../../services/api';

/** Jobs surface: workflows API until BE-08 scheduler ships (C5). */
export const JobsPage: React.FC = () => {
  const [workflows, setWorkflows] = useState<Record<string, unknown>[]>([]);
  const [executionsByWorkflow, setExecutionsByWorkflow] = useState<Record<string, Record<string, unknown>[]>>({});
  const [scheduleByWorkflow, setScheduleByWorkflow] = useState<
    Record<string, { enabled: boolean; cron: string; timezone: string }>
  >({});
  const [loadingExecFor, setLoadingExecFor] = useState<string | null>(null);
  const [startingFor, setStartingFor] = useState<string | null>(null);
  const [cancellingFor, setCancellingFor] = useState<string | null>(null);
  const [loadingScheduleFor, setLoadingScheduleFor] = useState<string | null>(null);
  const [savingScheduleFor, setSavingScheduleFor] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const list = await apiService.listWorkflows({ limit: 200 });
        setWorkflows(Array.isArray(list) ? list : []);
      } catch (e) {
        setError(formatApiErrorWithHints(e));
        setWorkflows([]);
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Jobs
      </Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        Unified cron/history API is tracked in <code>BE-08-jobs-scheduler-api.md</code>. Below lists{' '}
        <strong>real workflows</strong> from <code>GET /api/v1/workflows</code> (limit 200) — no synthetic job rows.
      </Alert>
      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {!loading && !error && workflows.length === 0 && (
        <Alert severity="info">No workflows returned — create one or check API auth.</Alert>
      )}
      <Stack spacing={1}>
        {workflows.map((w, i) => {
          const id = String(w.id ?? (w as { workflow_id?: string }).workflow_id ?? i);
          const name = String((w as { name?: string }).name ?? (w as { title?: string }).title ?? id);
          const status = String((w as { status?: string }).status ?? '');
          const updated = String((w as { updated_at?: string }).updated_at ?? '');
          const created = String((w as { created_at?: string }).created_at ?? '');
          return (
            <Card key={id} variant="outlined">
              <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={1}>
                  <Typography variant="subtitle1">{name}</Typography>
                  <Stack direction="row" spacing={1}>
                    <Button size="small" component={RouterLink} to="/workflow-builder" variant="outlined">
                      Builder
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      disabled={loadingExecFor === id}
                      onClick={() => {
                        void (async () => {
                          setLoadingExecFor(id);
                          try {
                            const rows = await apiService.listWorkflowExecutions(id);
                            setExecutionsByWorkflow((prev) => ({ ...prev, [id]: rows as Record<string, unknown>[] }));
                          } catch (e) {
                            setError(formatApiErrorWithHints(e));
                          } finally {
                            setLoadingExecFor(null);
                          }
                        })();
                      }}
                    >
                      {loadingExecFor === id ? 'Loading history…' : 'History'}
                    </Button>
                    <Button
                      size="small"
                      variant="contained"
                      disabled={startingFor === id}
                      onClick={() => {
                        void (async () => {
                          setStartingFor(id);
                          try {
                            const started = await apiService.startWorkflow(id);
                            setExecutionsByWorkflow((prev) => {
                              const current = prev[id] || [];
                              return {
                                ...prev,
                                [id]: [
                                  {
                                    execution_id: started.execution_id,
                                    workflow_id: started.workflow_id,
                                    status: started.status,
                                    root_task_id: started.task_id,
                                    started_at: new Date().toISOString(),
                                  },
                                  ...current,
                                ],
                              };
                            });
                          } catch (e) {
                            setError(formatApiErrorWithHints(e));
                          } finally {
                            setStartingFor(null);
                          }
                        })();
                      }}
                    >
                      {startingFor === id ? 'Starting…' : 'Start'}
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      color="warning"
                      disabled={cancellingFor === id}
                      onClick={() => {
                        void (async () => {
                          setCancellingFor(id);
                          try {
                            const cancelled = await apiService.cancelWorkflow(id);
                            if (cancelled.execution_id) {
                              setExecutionsByWorkflow((prev) => {
                                const current = prev[id] || [];
                                return {
                                  ...prev,
                                  [id]: [
                                    {
                                      execution_id: cancelled.execution_id,
                                      workflow_id: id,
                                      status: 'cancelled',
                                      started_at: new Date().toISOString(),
                                    },
                                    ...current,
                                  ],
                                };
                              });
                            }
                          } catch (e) {
                            setError(formatApiErrorWithHints(e));
                          } finally {
                            setCancellingFor(null);
                          }
                        })();
                      }}
                    >
                      {cancellingFor === id ? 'Cancelling…' : 'Cancel'}
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      disabled={loadingScheduleFor === id}
                      onClick={() => {
                        void (async () => {
                          setLoadingScheduleFor(id);
                          try {
                            const sched = await apiService.getWorkflowSchedule(id);
                            setScheduleByWorkflow((prev) => ({
                              ...prev,
                              [id]: {
                                enabled: Boolean(sched.enabled),
                                cron: String(sched.cron || ''),
                                timezone: String(sched.timezone || 'UTC'),
                              },
                            }));
                          } catch (e) {
                            setError(formatApiErrorWithHints(e));
                          } finally {
                            setLoadingScheduleFor(null);
                          }
                        })();
                      }}
                    >
                      {loadingScheduleFor === id ? 'Loading schedule…' : 'Schedule'}
                    </Button>
                  </Stack>
                </Stack>
                <Typography variant="caption" color="text.secondary" fontFamily="monospace" display="block">
                  {id}
                </Typography>
                {(status || updated || created) && (
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                    {status && <>Status: {status} · </>}
                    {created && <>created {new Date(created).toLocaleString()}</>}
                    {updated && created !== updated && <> · updated {new Date(updated).toLocaleString()}</>}
                  </Typography>
                )}
                {Array.isArray(executionsByWorkflow[id]) && executionsByWorkflow[id].length > 0 && (
                  <Box sx={{ mt: 1, p: 1, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.5 }}>
                      Executions
                    </Typography>
                    <Stack spacing={0.5}>
                      {executionsByWorkflow[id].slice(0, 6).map((ex, idx) => {
                        const executionId = String(
                          (ex as { execution_id?: string }).execution_id ??
                            (ex as { id?: string }).id ??
                            `${id}-${idx}`,
                        );
                        const exStatus = String((ex as { status?: string }).status ?? '');
                        const rootTask = String((ex as { root_task_id?: string }).root_task_id ?? '');
                        const startedAt = String((ex as { started_at?: string }).started_at ?? '');
                        return (
                          <Typography
                            key={executionId}
                            variant="caption"
                            color="text.secondary"
                            sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}
                          >
                            {executionId} · {exStatus || 'unknown'}
                            {startedAt ? ` · ${new Date(startedAt).toLocaleString()}` : ''}
                            {rootTask ? (
                              <>
                                {' '}
                                · <RouterLink to={`/tasks/${encodeURIComponent(rootTask)}`}>task {rootTask}</RouterLink>
                                {' · '}
                                <RouterLink to={`/sandbox?taskId=${encodeURIComponent(rootTask)}`}>sandbox</RouterLink>
                              </>
                            ) : null}
                          </Typography>
                        );
                      })}
                    </Stack>
                  </Box>
                )}
                {scheduleByWorkflow[id] && (
                  <Box sx={{ mt: 1, p: 1, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.5 }}>
                      Schedule (BE-08 incremental)
                    </Typography>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
                      <TextField
                        size="small"
                        label="Cron"
                        value={scheduleByWorkflow[id].cron}
                        onChange={(e) =>
                          setScheduleByWorkflow((prev) => ({
                            ...prev,
                            [id]: { ...prev[id], cron: e.target.value },
                          }))
                        }
                        sx={{ minWidth: 220 }}
                      />
                      <TextField
                        size="small"
                        label="Timezone"
                        value={scheduleByWorkflow[id].timezone}
                        onChange={(e) =>
                          setScheduleByWorkflow((prev) => ({
                            ...prev,
                            [id]: { ...prev[id], timezone: e.target.value },
                          }))
                        }
                        sx={{ minWidth: 120 }}
                      />
                      <Button
                        size="small"
                        variant="contained"
                        disabled={savingScheduleFor === id || !scheduleByWorkflow[id].cron.trim()}
                        onClick={() => {
                          void (async () => {
                            setSavingScheduleFor(id);
                            try {
                              const schedule = scheduleByWorkflow[id];
                              const saved = await apiService.putWorkflowSchedule(id, {
                                enabled: Boolean(schedule.enabled),
                                cron: schedule.cron.trim(),
                                timezone: schedule.timezone || 'UTC',
                              });
                              setScheduleByWorkflow((prev) => ({
                                ...prev,
                                [id]: {
                                  enabled: Boolean(saved.enabled),
                                  cron: String(saved.cron || ''),
                                  timezone: String(saved.timezone || 'UTC'),
                                },
                              }));
                            } catch (e) {
                              setError(formatApiErrorWithHints(e));
                            } finally {
                              setSavingScheduleFor(null);
                            }
                          })();
                        }}
                      >
                        {savingScheduleFor === id ? 'Saving…' : 'Save schedule'}
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        color="warning"
                        disabled={savingScheduleFor === id}
                        onClick={() => {
                          void (async () => {
                            setSavingScheduleFor(id);
                            try {
                              const removed = await apiService.deleteWorkflowSchedule(id);
                              setScheduleByWorkflow((prev) => ({
                                ...prev,
                                [id]: {
                                  enabled: Boolean(removed.enabled),
                                  cron: String(removed.cron || ''),
                                  timezone: String(removed.timezone || 'UTC'),
                                },
                              }));
                            } catch (e) {
                              setError(formatApiErrorWithHints(e));
                            } finally {
                              setSavingScheduleFor(null);
                            }
                          })();
                        }}
                      >
                        Disable schedule
                      </Button>
                    </Stack>
                  </Box>
                )}
              </CardContent>
            </Card>
          );
        })}
      </Stack>
    </Box>
  );
};
