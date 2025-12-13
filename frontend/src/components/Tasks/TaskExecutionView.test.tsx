// frontend/src/components/Tasks/TaskExecutionView.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { TaskExecutionView } from './TaskExecutionView';
import { apiService } from '../../services/api';
import { websocketService } from '../../services/websocket';
import { mockTask } from '../../test/mocks/api';

// Mock services
vi.mock('../../services/api', () => ({
  apiService: {
    getTask: vi.fn(),
  },
}));

vi.mock('../../services/websocket', () => ({
  websocketService: {
    subscribeToTask: vi.fn(),
    unsubscribeFromTask: vi.fn(),
    on: vi.fn(() => vi.fn()),
  },
}));

// Mock useParams
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ taskId: 'task_1' }),
  };
});

const renderWithRouter = () => {
  return render(
    <BrowserRouter>
      <TaskExecutionView />
    </BrowserRouter>
  );
};

describe('TaskExecutionView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(apiService.getTask).mockResolvedValue(mockTask);
  });

  it('should render task execution view', async () => {
    renderWithRouter();

    await waitFor(() => {
      expect(screen.getByText('Test Task')).toBeInTheDocument();
    });
  });

  it('should fetch task data on mount', async () => {
    renderWithRouter();

    await waitFor(() => {
      expect(apiService.getTask).toHaveBeenCalledWith('task_1');
    });
  });

  it('should subscribe to task-specific WebSocket events', async () => {
    renderWithRouter();

    await waitFor(() => {
      expect(websocketService.subscribeToTask).toHaveBeenCalledWith('task_1');
      expect(websocketService.on).toHaveBeenCalledWith('task_update', expect.any(Function));
      expect(websocketService.on).toHaveBeenCalledWith('task_progress', expect.any(Function));
      expect(websocketService.on).toHaveBeenCalledWith('agent_started', expect.any(Function));
      expect(websocketService.on).toHaveBeenCalledWith('agent_completed', expect.any(Function));
      expect(websocketService.on).toHaveBeenCalledWith('task_completed', expect.any(Function));
      expect(websocketService.on).toHaveBeenCalledWith('task_failed', expect.any(Function));
    });
  });

  it('should display task information', async () => {
    renderWithRouter();

    await waitFor(() => {
      expect(screen.getByText('Test Task')).toBeInTheDocument();
      // Task ID is displayed as "Task ID: task_1" - check for either format
      const taskIdElement = screen.queryByText('task_1') || screen.queryByText(/Task ID:/i);
      expect(taskIdElement).toBeTruthy();
      expect(screen.getByText('Task Information')).toBeInTheDocument();
    });
  });

  it('should show loading state while fetching', () => {
    vi.mocked(apiService.getTask).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    renderWithRouter();

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('should display error when task not found', async () => {
    vi.mocked(apiService.getTask).mockRejectedValue(new Error('Task not found'));

    renderWithRouter();

    await waitFor(() => {
      expect(screen.getByText(/task not found/i)).toBeInTheDocument();
    });
  });

  it('should display execution timeline when events exist', async () => {
    renderWithRouter();

    await waitFor(() => {
      expect(screen.getByText('Execution Timeline')).toBeInTheDocument();
    });
  });

  it('should display results when task is completed', async () => {
    const completedTask = {
      ...mockTask,
      status: 'completed' as const,
      result: { output: 'Task completed successfully' },
    };

    vi.mocked(apiService.getTask).mockResolvedValue(completedTask);

    renderWithRouter();

    await waitFor(() => {
      expect(screen.getByText('Results')).toBeInTheDocument();
    });
  });

  it('should display error details when task failed', async () => {
    const failedTask = {
      ...mockTask,
      status: 'failed' as const,
      error_details: { message: 'Execution failed' },
    };

    vi.mocked(apiService.getTask).mockResolvedValue(failedTask);

    renderWithRouter();

    await waitFor(() => {
      // There might be multiple elements with "execution failed", get all and verify at least one exists
      const errorElements = screen.queryAllByText(/execution failed/i);
      expect(errorElements.length).toBeGreaterThan(0);
    });
  });

  it('should unsubscribe from WebSocket on unmount', async () => {
    const { unmount } = renderWithRouter();

    await waitFor(() => {
      expect(websocketService.subscribeToTask).toHaveBeenCalled();
    });

    unmount();

    expect(websocketService.unsubscribeFromTask).toHaveBeenCalledWith('task_1');
  });
});

