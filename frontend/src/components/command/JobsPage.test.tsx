import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { JobsPage } from './JobsPage';
import { apiService } from '../../services/api';

vi.mock('../../services/api', () => ({
  apiService: {
    listWorkflows: vi.fn(),
    listWorkflowExecutions: vi.fn(),
    startWorkflow: vi.fn(),
    cancelWorkflow: vi.fn(),
    getWorkflowSchedule: vi.fn(),
    putWorkflowSchedule: vi.fn(),
    deleteWorkflowSchedule: vi.fn(),
  },
}));

function renderPage() {
  return render(
    <MemoryRouter>
      <JobsPage />
    </MemoryRouter>,
  );
}

describe('JobsPage workflow controls', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(apiService.listWorkflows).mockResolvedValue([
      {
        id: 'wf_1',
        name: 'Workflow One',
        status: 'pending',
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
      },
    ]);
    vi.mocked(apiService.listWorkflowExecutions).mockResolvedValue([
      {
        execution_id: 'ex_1',
        workflow_id: 'wf_1',
        status: 'completed',
        started_at: '2026-01-01T00:05:00Z',
        root_task_id: 'task_123',
      },
    ]);
    vi.mocked(apiService.startWorkflow).mockResolvedValue({
      workflow_id: 'wf_1',
      execution_id: 'ex_2',
      task_id: 'task_200',
      status: 'executing',
    });
    vi.mocked(apiService.cancelWorkflow).mockResolvedValue({
      workflow_id: 'wf_1',
      execution_id: 'ex_3',
      status: 'cancelled',
      message: 'cancelled',
    });
    vi.mocked(apiService.getWorkflowSchedule).mockResolvedValue({
      workflow_id: 'wf_1',
      enabled: true,
      cron: '*/5 * * * *',
      timezone: 'UTC',
      updated_at: '2026-01-01T00:00:00Z',
    });
    vi.mocked(apiService.putWorkflowSchedule).mockResolvedValue({
      workflow_id: 'wf_1',
      enabled: true,
      cron: '*/10 * * * *',
      timezone: 'UTC',
      updated_at: '2026-01-01T00:01:00Z',
    });
    vi.mocked(apiService.deleteWorkflowSchedule).mockResolvedValue({
      workflow_id: 'wf_1',
      enabled: false,
      cron: null,
      timezone: 'UTC',
      updated_at: '2026-01-01T00:02:00Z',
    });
  });

  it('loads execution history and starts workflow', async () => {
    renderPage();

    await screen.findByText('Workflow One');
    fireEvent.click(screen.getByRole('button', { name: /history/i }));

    await waitFor(() => {
      expect(apiService.listWorkflowExecutions).toHaveBeenCalledWith('wf_1');
    });
    expect(await screen.findByText(/ex_1 · completed/i)).toBeInTheDocument();
    const sandboxLink = await screen.findByRole('link', { name: /^sandbox$/i });
    expect(sandboxLink).toHaveAttribute('href', '/sandbox?taskId=task_123');

    fireEvent.click(screen.getByRole('button', { name: /^start$/i }));
    await waitFor(() => {
      expect(apiService.startWorkflow).toHaveBeenCalledWith('wf_1');
    });
    expect(await screen.findByText(/ex_2 · executing/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /^cancel$/i }));
    await waitFor(() => {
      expect(apiService.cancelWorkflow).toHaveBeenCalledWith('wf_1');
    });
    expect(await screen.findByText(/ex_3 · cancelled/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /schedule/i }));
    await waitFor(() => {
      expect(apiService.getWorkflowSchedule).toHaveBeenCalledWith('wf_1');
    });
    expect(await screen.findByDisplayValue('*/5 * * * *')).toBeInTheDocument();
  });
});

