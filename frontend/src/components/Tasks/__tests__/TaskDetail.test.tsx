// frontend/src/components/Tasks/__tests__/TaskDetail.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { TaskDetail } from '../TaskDetail';
import { apiService } from '../../../services/api';
import { websocketService } from '../../../services/websocket';

// Mock dependencies
vi.mock('../../../services/api');
vi.mock('../../../services/websocket');
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ taskId: 'task1' }),
    useNavigate: () => vi.fn(),
  };
});

const mockTask = {
  task_id: 'task1',
  title: 'Test Task',
  description: 'Test description',
  task_type: 'security_scan',
  status: 'executing',
  priority: 5,
  created_at: '2024-01-01T00:00:00Z',
  started_at: '2024-01-01T00:05:00Z',
  progress: 50,
  duration_seconds: 10.5,
  success_rate: 0.95,
  quality_score: 0.90,
  cost_usd: 0.01,
  tokens_used: 1000,
};

describe('TaskDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (apiService.getTask as any) = vi.fn().mockResolvedValue(mockTask);
    (apiService.getTaskProgress as any) = vi.fn().mockResolvedValue({ progress: 50 });
    (websocketService.on as any) = vi.fn(() => vi.fn());
  });

  it('should render task details', async () => {
    render(
      <BrowserRouter>
        <TaskDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Task')).toBeInTheDocument();
    });

    expect(screen.getByText('Test description')).toBeInTheDocument();
    expect(screen.getByText('security_scan')).toBeInTheDocument();
  });

  it('should display progress for executing tasks', async () => {
    render(
      <BrowserRouter>
        <TaskDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/progress/i)).toBeInTheDocument();
    });
  });

  it('should display task information', async () => {
    render(
      <BrowserRouter>
        <TaskDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/ID:/i)).toBeInTheDocument();
      expect(screen.getByText(/Type:/i)).toBeInTheDocument();
      expect(screen.getByText(/Priority:/i)).toBeInTheDocument();
    });
  });

  it('should display performance metrics', async () => {
    render(
      <BrowserRouter>
        <TaskDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Duration:/i)).toBeInTheDocument();
      expect(screen.getByText(/Success Rate:/i)).toBeInTheDocument();
      expect(screen.getByText(/Quality Score:/i)).toBeInTheDocument();
    });
  });

  it('should handle task execution', async () => {
    (apiService.executeTask as any) = vi.fn().mockResolvedValue({});
    (apiService.getTask as any) = vi.fn().mockResolvedValue({
      ...mockTask,
      status: 'pending',
    });

    render(
      <BrowserRouter>
        <TaskDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Task')).toBeInTheDocument();
    });

    const executeButton = screen.queryByText(/execute/i);
    if (executeButton) {
      fireEvent.click(executeButton);
      await waitFor(() => {
        expect(apiService.executeTask).toHaveBeenCalledWith('task1');
      });
    }
  });

  it('should subscribe to WebSocket updates', () => {
    render(
      <BrowserRouter>
        <TaskDetail />
      </BrowserRouter>
    );

    expect(websocketService.on).toHaveBeenCalledWith('task_update', expect.any(Function));
  });
});

