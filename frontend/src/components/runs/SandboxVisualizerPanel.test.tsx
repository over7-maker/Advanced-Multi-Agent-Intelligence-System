import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SandboxVisualizerPanel } from './SandboxVisualizerPanel';
import { apiService } from '../../services/api';
import type { Task } from '../../services/api';

vi.mock('../../services/api', () => ({
  apiService: {
    getSandboxTelemetry: vi.fn(),
  },
}));

const baseTask: Task = {
  id: 't1',
  task_id: 't1',
  title: 'x',
  description: 'd',
  status: 'completed',
  task_type: 'code_analysis',
  target: '.',
  priority: 5,
  assigned_agents: [],
  created_at: '2026-01-01T00:00:00Z',
};

describe('SandboxVisualizerPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders v2 telemetry table when recent events exist', async () => {
    vi.mocked(apiService.getSandboxTelemetry).mockResolvedValue({
      schema_version: 'sandbox_telemetry.v2',
      task_id: 't1',
      available: true,
      sandbox_event_count: 1,
      tool_event_count: 1,
      source: 'run_events',
      event_type_counts: { sandbox_spawned: 1, tool_call_started: 1 },
      first_event_iso: '2026-01-01T00:00:00Z',
      last_event_iso: '2026-01-01T00:00:01Z',
      recent_sandbox_tool_events: [
        { timestamp: '2026-01-01T00:00:00Z', event_type: 'sandbox_spawned', summary: 'sb-1' },
        { timestamp: '2026-01-01T00:00:01Z', event_type: 'tool_call_started', summary: 'bash' },
      ],
    });

    render(<SandboxVisualizerPanel task={baseTask} />);

    expect(await screen.findByText('sb-1')).toBeInTheDocument();
    expect(screen.getByText('sandbox_spawned')).toBeInTheDocument();
    expect(screen.getByText(/First:/)).toBeInTheDocument();
  });
});
