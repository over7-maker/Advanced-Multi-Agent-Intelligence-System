// frontend/src/components/Auth/ProtectedRoute.test.tsx
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { apiService } from '../../services/api';
import { mockUser } from '../../test/mocks/api';

// Mock the API service
vi.mock('../../services/api', () => ({
  apiService: {
    getCurrentUser: vi.fn(),
  },
}));

const MockedComponent = () => <div>Protected Content</div>;

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should show loading state initially', () => {
    vi.mocked(apiService.getCurrentUser).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    renderWithRouter(
      <ProtectedRoute>
        <MockedComponent />
      </ProtectedRoute>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('should render children when authenticated', async () => {
    vi.mocked(apiService.getCurrentUser).mockResolvedValue(mockUser);

    renderWithRouter(
      <ProtectedRoute>
        <MockedComponent />
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
  });

  it('should redirect to login when not authenticated', async () => {
    vi.mocked(apiService.getCurrentUser).mockRejectedValue(new Error('Unauthorized'));

    renderWithRouter(
      <ProtectedRoute>
        <MockedComponent />
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(window.location.pathname).toBe('/login');
    });
  });

  it('should handle API errors gracefully', async () => {
    vi.mocked(apiService.getCurrentUser).mockRejectedValue(new Error('Network error'));

    renderWithRouter(
      <ProtectedRoute>
        <MockedComponent />
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(window.location.pathname).toBe('/login');
    });
  });
});

