// frontend/src/components/Tasks/TaskListComplete.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { TaskListComplete } from './TaskListComplete';
import { apiService } from '../../services/api';
import { websocketService } from '../../services/websocket';
import { mockTask, mockTaskPrediction } from '../../test/mocks/api';

// Mock services
vi.mock('../../services/api', () => ({
  apiService: {
    listTasks: vi.fn(),
    executeTask: vi.fn(),
    cancelTask: vi.fn(),
    predictTask: vi.fn(),
    createTask: vi.fn(),
  },
}));

vi.mock('../../services/websocket', () => ({
  websocketService: {
    on: vi.fn(() => vi.fn()),
  },
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('TaskListComplete', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(apiService.listTasks).mockResolvedValue({
      tasks: [mockTask],
      total: 1,
    });
  });

  it('should render task list with title', async () => {
    renderWithRouter(<TaskListComplete />);

    await waitFor(() => {
      expect(screen.getByText('Tasks')).toBeInTheDocument();
    });
  });

  it('should fetch tasks on mount', async () => {
    renderWithRouter(<TaskListComplete />);

    await waitFor(() => {
      expect(apiService.listTasks).toHaveBeenCalled();
    });
  });

  it('should display tasks in table', async () => {
    renderWithRouter(<TaskListComplete />);

    await waitFor(() => {
      expect(screen.getByText('Test Task')).toBeInTheDocument();
      expect(screen.getByText('task_1')).toBeInTheDocument();
    });
  });

  it('should open create task dialog', async () => {
    renderWithRouter(<TaskListComplete />);

    await waitFor(() => {
      const createButton = screen.getByText('Create Task');
      fireEvent.click(createButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Create New Task')).toBeInTheDocument();
    });
  });

  it('should filter tasks by status', async () => {
    renderWithRouter(<TaskListComplete />);

    await waitFor(() => {
      expect(apiService.listTasks).toHaveBeenCalled();
    });

    // Find and click status filter - use getAllByRole to find combobox
    await waitFor(() => {
      const comboboxes = screen.getAllByRole('combobox');
      // Find the Status combobox (usually first one)
      const statusFilter = comboboxes[0];
      if (statusFilter) {
        fireEvent.mouseDown(statusFilter);
      }
    });
    
    await waitFor(() => {
      const pendingOption = screen.queryByText('Pending');
      if (pendingOption) {
        fireEvent.click(pendingOption);
      }
    });

    await waitFor(() => {
      expect(apiService.listTasks).toHaveBeenCalledWith(
        expect.objectContaining({ status: 'pending' })
      );
    });
  });

  it('should handle task execution', async () => {
    vi.mocked(apiService.executeTask).mockResolvedValue({
      task_id: 'task_1',
      status: 'executing',
      message: 'Task started',
    });

    renderWithRouter(<TaskListComplete />);

    await waitFor(() => {
      expect(screen.getByText('Test Task')).toBeInTheDocument();
    });

    // Find execute button (play icon)
    const executeButtons = screen.getAllByLabelText(/execute|play/i);
    if (executeButtons.length > 0) {
      fireEvent.click(executeButtons[0]);
    }

    await waitFor(() => {
      expect(apiService.executeTask).toHaveBeenCalled();
    });
  });

  it('should subscribe to WebSocket task updates', async () => {
    renderWithRouter(<TaskListComplete />);

    await waitFor(() => {
      expect(websocketService.on).toHaveBeenCalledWith('task_update', expect.any(Function));
    });
  });

  it('should handle task creation with prediction', async () => {
    vi.mocked(apiService.predictTask).mockResolvedValue(mockTaskPrediction);
    vi.mocked(apiService.createTask).mockResolvedValue(mockTask);

    renderWithRouter(<TaskListComplete />);

    await waitFor(() => {
      const createButton = screen.getByText('Create Task');
      fireEvent.click(createButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Create New Task')).toBeInTheDocument();
    });

    // Fill form - find inputs by their role
    await waitFor(() => {
      const textboxes = screen.getAllByRole('textbox');
      // First textbox should be Title
      if (textboxes.length > 0) {
        fireEvent.change(textboxes[0], { target: { value: 'New Task' } });
      }
      // Find target input by placeholder text
      const targetInput = screen.queryByPlaceholderText(/example\.com/i);
      if (targetInput) {
        fireEvent.change(targetInput, { target: { value: 'https://example.com' } });
      } else if (textboxes.length > 1) {
        fireEvent.change(textboxes[1], { target: { value: 'https://example.com' } });
      }
    });

    // Click predict button
    const predictButton = screen.getByText('Predict');
    fireEvent.click(predictButton);

    await waitFor(() => {
      expect(apiService.predictTask).toHaveBeenCalled();
    });

    // Click create button - there might be multiple "Create Task" buttons, get the one in dialog
    const createSubmitButtons = screen.getAllByText('Create Task');
    const dialogCreateButton = createSubmitButtons.find(btn => 
      btn.closest('[role="dialog"]') !== null
    ) || createSubmitButtons[createSubmitButtons.length - 1];
    
    if (dialogCreateButton) {
      fireEvent.click(dialogCreateButton);
    }

    await waitFor(() => {
      expect(apiService.createTask).toHaveBeenCalled();
    });
  });
});

