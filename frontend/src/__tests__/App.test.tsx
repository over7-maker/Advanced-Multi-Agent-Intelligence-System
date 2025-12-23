// frontend/src/__tests__/App.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';
import { apiService } from '../services/api';
import { websocketService } from '../services/websocket';

// Mock dependencies
vi.mock('../services/api');
vi.mock('../services/websocket');
vi.mock('../components/Dashboard/Dashboard', () => ({
  default: () => <div>Dashboard</div>,
}));
vi.mock('../components/Tasks/TaskList', () => ({
  TaskList: () => <div>TaskList</div>,
}));
vi.mock('../components/Agents/AgentList', () => ({
  AgentList: () => <div>AgentList</div>,
}));
vi.mock('../components/Integrations/IntegrationList', () => ({
  IntegrationList: () => <div>IntegrationList</div>,
}));
vi.mock('../components/System/SystemHealth', () => ({
  SystemHealth: () => <div>SystemHealth</div>,
}));
vi.mock('../components/Auth/Login', () => ({
  Login: () => <div>Login</div>,
}));

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    (apiService.getCurrentUser as any) = vi.fn().mockRejectedValue(new Error('Not authenticated'));
  });

  it('should redirect to login when not authenticated', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Login')).toBeInTheDocument();
    });
  });

  it('should show dashboard when authenticated', async () => {
    (apiService.getCurrentUser as any) = vi.fn().mockResolvedValue({ id: 'user1', username: 'test' });
    localStorage.setItem('access_token', 'test_token');

    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });

  it('should connect WebSocket after authentication', async () => {
    (apiService.getCurrentUser as any) = vi.fn().mockResolvedValue({ id: 'user1', username: 'test' });
    localStorage.setItem('access_token', 'test_token');

    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(websocketService.connect).toHaveBeenCalled();
    });
  });
});

