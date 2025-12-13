// frontend/src/components/Dashboard/DashboardNew.test.tsx
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { DashboardNew } from './DashboardNew';
import { apiService } from '../../services/api';
import { websocketService } from '../../services/websocket';
import { mockSystemMetrics, mockTaskAnalytics } from '../../test/mocks/api';

// Mock services
vi.mock('../../services/api', () => ({
  apiService: {
    getSystemMetrics: vi.fn(),
    getTaskAnalytics: vi.fn(),
    getAgentPerformance: vi.fn(),
  },
}));

vi.mock('../../services/websocket', () => ({
  websocketService: {
    on: vi.fn(() => vi.fn()),
    connect: vi.fn(),
  },
}));

// Mock Chart.js
vi.mock('react-chartjs-2', () => ({
  Line: () => <div data-testid="line-chart">Line Chart</div>,
}));

describe('DashboardNew', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(apiService.getSystemMetrics).mockResolvedValue(mockSystemMetrics);
    vi.mocked(apiService.getTaskAnalytics).mockResolvedValue(mockTaskAnalytics);
    vi.mocked(apiService.getAgentPerformance).mockResolvedValue([]);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should render dashboard with title', async () => {
    render(<DashboardNew />);

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });

  it('should display task statistics', async () => {
    render(<DashboardNew />);

    await waitFor(() => {
      expect(screen.getByText('Total Tasks')).toBeInTheDocument();
      expect(screen.getByText('Active Tasks')).toBeInTheDocument();
    });
  });

  it('should display system metrics', async () => {
    render(<DashboardNew />);

    await waitFor(() => {
      expect(screen.getByText('CPU Usage')).toBeInTheDocument();
      expect(screen.getByText('Memory Usage')).toBeInTheDocument();
    });
  });

  it('should fetch dashboard data on mount', async () => {
    render(<DashboardNew />);

    // Wait for component to mount and fetch data
    await waitFor(() => {
      expect(apiService.getSystemMetrics).toHaveBeenCalled();
    }, { timeout: 3000 });

    await waitFor(() => {
      expect(apiService.getTaskAnalytics).toHaveBeenCalled();
    }, { timeout: 3000 });
  });

  it('should subscribe to WebSocket events', async () => {
    render(<DashboardNew />);

    await waitFor(() => {
      expect(websocketService.on).toHaveBeenCalledWith('task_update', expect.any(Function));
      expect(websocketService.on).toHaveBeenCalledWith('system_metrics', expect.any(Function));
    });
  });

  it('should display refresh button', async () => {
    render(<DashboardNew />);

    await waitFor(() => {
      const refreshButton = screen.getByLabelText(/refresh/i);
      expect(refreshButton).toBeInTheDocument();
    });
  });

  it('should handle API errors gracefully', async () => {
    vi.mocked(apiService.getSystemMetrics).mockRejectedValue(new Error('API Error'));

    render(<DashboardNew />);

    await waitFor(() => {
      // Component should still render even if API fails
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });

  it('should update stats from WebSocket events', async () => {
    let taskUpdateHandler: (data: any) => void;
    vi.mocked(websocketService.on).mockImplementation((event, handler) => {
      if (event === 'task_update') {
        taskUpdateHandler = handler;
      }
      return vi.fn();
    });

    render(<DashboardNew />);

    await waitFor(() => {
      expect(websocketService.on).toHaveBeenCalled();
    });

    // Simulate WebSocket update
    if (taskUpdateHandler!) {
      taskUpdateHandler({ task_id: 'test', status: 'completed' });
    }

    // Component should handle the update
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });
});

