// frontend/src/components/Agents/__tests__/AgentList.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { AgentList } from '../AgentList';
import { apiService } from '../../../services/api';
import { websocketService } from '../../../services/websocket';

// Mock dependencies
vi.mock('../../../services/api');
vi.mock('../../../services/websocket');

const mockAgents = {
  agents: [
    {
      agent_id: 'agent1',
      name: 'Security Agent',
      type: 'security',
      status: 'active',
      capabilities: ['security_scan', 'vulnerability_analysis'],
      configuration: {},
      expertise_score: 0.9,
      total_executions: 10,
      successful_executions: 9,
      failed_executions: 1,
      total_duration_seconds: 100,
      total_tokens_used: 1000,
      total_cost_usd: 0.1,
      created_at: '2024-01-01T00:00:00Z',
      performance_metrics: {
        success_rate: 0.9,
        avg_duration: 10.0,
        avg_quality: 0.85,
        total_cost: 0.1,
      },
    },
  ],
  total: 1,
};

describe('AgentList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (apiService.listAgents as any) = vi.fn().mockResolvedValue(mockAgents);
    (websocketService.on as any) = vi.fn(() => vi.fn());
  });

  it('should render agent list', async () => {
    render(<AgentList />);

    await waitFor(() => {
      expect(screen.getByText('Agents')).toBeInTheDocument();
    });

    expect(screen.getByText('Security Agent')).toBeInTheDocument();
  });

  it('should display agent status', async () => {
    render(<AgentList />);

    await waitFor(() => {
      expect(screen.getByText('Security Agent')).toBeInTheDocument();
    });

    expect(screen.getByText('active')).toBeInTheDocument();
  });

  it('should display performance metrics', async () => {
    render(<AgentList />);

    await waitFor(() => {
      expect(screen.getByText(/Success Rate/i)).toBeInTheDocument();
      expect(screen.getByText(/Avg Duration/i)).toBeInTheDocument();
      expect(screen.getByText(/Total Executions/i)).toBeInTheDocument();
    });
  });

  it('should display capabilities', async () => {
    render(<AgentList />);

    await waitFor(() => {
      expect(screen.getByText('Security Agent')).toBeInTheDocument();
    });

    expect(screen.getByText(/Capabilities:/i)).toBeInTheDocument();
  });

  it('should subscribe to WebSocket updates', () => {
    render(<AgentList />);

    expect(websocketService.on).toHaveBeenCalledWith('agent_status_changed', expect.any(Function));
  });

  it('should display loading state', () => {
    (apiService.listAgents as any) = vi.fn().mockImplementation(() => new Promise(() => {}));

    render(<AgentList />);

    // Should show loading indicator
    expect(screen.queryByRole('progressbar')).toBeInTheDocument();
  });
});

