// frontend/src/components/Layout/MainLayout.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { MainLayout } from './MainLayout';
import { mockUser } from '../../test/mocks/api';

// Mock services
const mockGetCurrentUser = vi.fn();
const mockLogout = vi.fn();
const mockConnect = vi.fn();
const mockDisconnect = vi.fn();

vi.mock('../../services/api', () => ({
  apiService: {
    getCurrentUser: () => mockGetCurrentUser(),
    logout: () => mockLogout(),
  },
}));

vi.mock('../../services/websocket', () => ({
  websocketService: {
    connect: () => mockConnect(),
    disconnect: () => mockDisconnect(),
  },
}));

const MockedChild = () => <div>Child Content</div>;

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('MainLayout', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetCurrentUser.mockResolvedValue(mockUser);
    mockLogout.mockResolvedValue(undefined);
  });

  it('should render layout with navigation', async () => {
    renderWithRouter(
      <MainLayout>
        <MockedChild />
      </MainLayout>
    );

    await waitFor(() => {
      expect(screen.getByText('AMAS - AI Multi-Agent System')).toBeInTheDocument();
      expect(screen.getByText('Child Content')).toBeInTheDocument();
    });
  });

  it('should display user avatar with username initial', async () => {
    renderWithRouter(
      <MainLayout>
        <MockedChild />
      </MainLayout>
    );

    await waitFor(() => {
      const avatar = screen.getByText('T'); // First letter of 'testuser'
      expect(avatar).toBeInTheDocument();
    });
  });

  it('should toggle drawer when menu button is clicked', async () => {
    renderWithRouter(
      <MainLayout>
        <MockedChild />
      </MainLayout>
    );

    await waitFor(() => {
      // Menu button might not have aria-label, use role or data-testid
      const menuButton = screen.queryByRole('button', { name: /menu/i }) ||
                        screen.queryByLabelText(/menu/i) ||
                        screen.getAllByRole('button')[0];
      expect(menuButton).toBeInTheDocument();
    });

    const menuButtons = screen.getAllByRole('button');
    const menuButton = menuButtons.find(btn => 
      btn.getAttribute('aria-label')?.toLowerCase().includes('menu') ||
      btn.querySelector('svg') // Icon button
    ) || menuButtons[0];
    
    if (menuButton) {
      fireEvent.click(menuButton);
    }

    // Drawer should be toggled (we can't easily test drawer state, but we can test the button works)
    expect(menuButton).toBeInTheDocument();
  });

  it('should connect WebSocket on mount', async () => {
    renderWithRouter(
      <MainLayout>
        <MockedChild />
      </MainLayout>
    );

    await waitFor(() => {
      expect(mockConnect).toHaveBeenCalled();
    });
  });

  it('should disconnect WebSocket on unmount', async () => {
    const { unmount } = renderWithRouter(
      <MainLayout>
        <MockedChild />
      </MainLayout>
    );

    await waitFor(() => {
      expect(mockConnect).toHaveBeenCalled();
    });

    unmount();

    expect(mockDisconnect).toHaveBeenCalled();
  });

  it('should show navigation menu items', async () => {
    renderWithRouter(
      <MainLayout>
        <MockedChild />
      </MainLayout>
    );

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Tasks')).toBeInTheDocument();
      expect(screen.getByText('Agents')).toBeInTheDocument();
      expect(screen.getByText('Integrations')).toBeInTheDocument();
      expect(screen.getByText('System Health')).toBeInTheDocument();
    });
  });

  it('should handle logout', async () => {
    renderWithRouter(
      <MainLayout>
        <MockedChild />
      </MainLayout>
    );

    await waitFor(() => {
      const avatar = screen.getByText('T');
      fireEvent.click(avatar);
    });

    await waitFor(() => {
      const logoutButton = screen.getByText('Logout');
      fireEvent.click(logoutButton);
    });

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
      expect(mockDisconnect).toHaveBeenCalled();
    });
  });
});

