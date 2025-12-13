// frontend/src/components/Auth/__tests__/Login.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Login } from '../Login';
import { apiService } from '../../../services/api';
import { websocketService } from '../../../services/websocket';

// Mock dependencies
vi.mock('../../../services/api');
vi.mock('../../../services/websocket');
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

describe('Login', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (websocketService.connect as any) = vi.fn();
  });

  it('should render login form', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    expect(screen.getByText(/AMAS Login/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Login/i })).toBeInTheDocument();
  });

  it('should handle form submission', async () => {
    const mockResponse = {
      access_token: 'test_token',
      user: { id: 'user1', username: 'test' },
    };
    (apiService.login as any) = vi.fn().mockResolvedValue(mockResponse);

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const usernameInput = screen.getByLabelText(/Username/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const submitButton = screen.getByRole('button', { name: /Login/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(apiService.login).toHaveBeenCalledWith('testuser', 'testpass');
    });
  });

  it('should display error on login failure', async () => {
    (apiService.login as any) = vi.fn().mockRejectedValue({
      response: { data: { detail: 'Invalid credentials' } },
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const usernameInput = screen.getByLabelText(/Username/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const submitButton = screen.getByRole('button', { name: /Login/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
    });
  });

  it('should connect WebSocket after successful login', async () => {
    const mockResponse = {
      access_token: 'test_token',
      user: { id: 'user1', username: 'test' },
    };
    (apiService.login as any) = vi.fn().mockResolvedValue(mockResponse);

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const usernameInput = screen.getByLabelText(/Username/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const submitButton = screen.getByRole('button', { name: /Login/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(websocketService.connect).toHaveBeenCalled();
    });
  });

  it('should disable form during submission', async () => {
    // Create a promise that we can control
    let resolvePromise: (value: any) => void;
    const loginPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    
    (apiService.login as any) = vi.fn().mockReturnValue(loginPromise);

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const usernameInput = screen.getByLabelText(/Username/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const submitButton = screen.getByRole('button', { name: /Login/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(submitButton);

    // Wait for button to be disabled
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    }, { timeout: 1000 });

    // Resolve the promise to clean up
    resolvePromise!({ access_token: 'test', user: { id: '1' } });
  });
});

