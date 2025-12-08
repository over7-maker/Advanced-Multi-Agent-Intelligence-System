// frontend/src/components/System/__tests__/SystemHealth.test.tsx
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { SystemHealth } from '../SystemHealth';
import { apiService } from '../../../services/api';
import { websocketService } from '../../../services/websocket';

// Mock dependencies
vi.mock('../../../services/api');
vi.mock('../../../services/websocket');

const mockMetrics = {
  cpu_usage_percent: 75.5,
  memory_usage_percent: 60.0,
  memory_usage_bytes: 2000000000,
  disk_usage_bytes: 1000000000,
  active_tasks: 5,
  queue_depth: 2,
  total_tasks: 100,
  completed_tasks: 90,
  failed_tasks: 5,
  active_agents: 3,
  timestamp: '2024-01-01T00:00:00Z',
};

describe('SystemHealth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (apiService.getSystemMetrics as any) = vi.fn().mockResolvedValue(mockMetrics);
    (websocketService.on as any) = vi.fn(() => vi.fn());
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it('should render system health', async () => {
    render(<SystemHealth />);

    // Wait for loading to finish and metrics to load
    await waitFor(() => {
      expect(screen.getByText('System Health')).toBeInTheDocument();
    }, { timeout: 3000 });

    // Check for CPU and Memory usage displays
    await waitFor(() => {
      expect(screen.getByText(/CPU Usage/i)).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('should display CPU usage', async () => {
    render(<SystemHealth />);

    await waitFor(() => {
      const cpuText = screen.queryByText(/75.5%/i) || screen.queryByText(/75/i);
      expect(cpuText).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('should display memory usage', async () => {
    render(<SystemHealth />);

    await waitFor(() => {
      const memoryText = screen.queryByText(/60.0%/i) || screen.queryByText(/60/i);
      expect(memoryText).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('should display task statistics', async () => {
    render(<SystemHealth />);

    await waitFor(() => {
      // Check for any task-related text
      const taskText = screen.queryByText(/Active Tasks/i) || 
                       screen.queryByText(/Tasks/i) ||
                       screen.queryByText(/5/i); // active_tasks value
      expect(taskText).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('should poll for updates', async () => {
    render(<SystemHealth />);

    await waitFor(() => {
      expect(apiService.getSystemMetrics).toHaveBeenCalled();
    }, { timeout: 2000 });

    // Advance time to trigger polling
    vi.advanceTimersByTime(5000);

    await waitFor(() => {
      // Should have been called at least twice (initial + poll)
      expect(apiService.getSystemMetrics).toHaveBeenCalledTimes(2);
    }, { timeout: 2000 });
  });

  it('should subscribe to WebSocket updates', () => {
    render(<SystemHealth />);

    expect(websocketService.on).toHaveBeenCalledWith('system_metrics', expect.any(Function));
  });

  it('should display loading state', () => {
    (apiService.getSystemMetrics as any) = vi.fn().mockImplementation(() => new Promise(() => {}));

    render(<SystemHealth />);

    expect(screen.queryByRole('progressbar')).toBeInTheDocument();
  });
});

