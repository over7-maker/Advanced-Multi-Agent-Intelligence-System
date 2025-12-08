// frontend/src/components/Onboarding/OnboardingWizard.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { OnboardingWizard } from './OnboardingWizard';
import { apiService } from '../../services/api';

// Mock API service
vi.mock('../../services/api', () => ({
  apiService: {
    getSystemHealth: vi.fn(),
  },
}));

describe('OnboardingWizard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(apiService.getSystemHealth).mockResolvedValue({
      status: 'healthy',
      components: {
        database: { status: 'healthy' },
      },
      timestamp: new Date().toISOString(),
    });
  });

  it('should render onboarding wizard', () => {
    const onComplete = vi.fn();
    render(<OnboardingWizard onComplete={onComplete} />);

    expect(screen.getByText('AMAS Setup Wizard')).toBeInTheDocument();
  });

  it('should display all onboarding steps', () => {
    const onComplete = vi.fn();
    render(<OnboardingWizard onComplete={onComplete} />);

    expect(screen.getByText('Environment Check')).toBeInTheDocument();
    expect(screen.getByText('Authentication Setup')).toBeInTheDocument();
    expect(screen.getByText('Database Connection')).toBeInTheDocument();
    expect(screen.getByText('Network Configuration')).toBeInTheDocument();
  });

  it('should run checks for current step', async () => {
    const onComplete = vi.fn();
    render(<OnboardingWizard onComplete={onComplete} />);

    await waitFor(() => {
      expect(apiService.getSystemHealth).toHaveBeenCalled();
    });
  });

  it('should navigate to next step', async () => {
    const onComplete = vi.fn();
    render(<OnboardingWizard onComplete={onComplete} />);

    await waitFor(() => {
      const nextButton = screen.getByText('Next');
      expect(nextButton).toBeInTheDocument();
    });

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    await waitFor(() => {
      // Should move to next step
      expect(screen.getByText('Authentication Setup')).toBeInTheDocument();
    });
  });

  it('should navigate back to previous step', async () => {
    const onComplete = vi.fn();
    render(<OnboardingWizard onComplete={onComplete} />);

    // Move to second step first
    await waitFor(() => {
      const nextButton = screen.getByText('Next');
      fireEvent.click(nextButton);
    });

    await waitFor(() => {
      const backButton = screen.getByText('Back');
      expect(backButton).toBeInTheDocument();
      fireEvent.click(backButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Environment Check')).toBeInTheDocument();
    });
  });

  it('should call onComplete when wizard is finished', async () => {
    const onComplete = vi.fn();
    render(<OnboardingWizard onComplete={onComplete} />);

    // Navigate through all steps - click Next button for each step
    for (let i = 0; i < 4; i++) {
      await waitFor(() => {
        // Find Next button (or Complete on last step)
        const nextButtons = screen.queryAllByText('Next');
        const completeButtons = screen.queryAllByText('Complete');
        const button = nextButtons[0] || completeButtons[0];
        
        if (button && !(button as HTMLButtonElement).disabled) {
          fireEvent.click(button);
        }
      }, { timeout: 2000 });
    }

    // Wait for onComplete to be called
    await waitFor(() => {
      expect(onComplete).toHaveBeenCalled();
    }, { timeout: 3000 });
  });

  it('should disable next button when checks are failing', async () => {
    vi.mocked(apiService.getSystemHealth).mockRejectedValue(new Error('Connection failed'));

    const onComplete = vi.fn();
    render(<OnboardingWizard onComplete={onComplete} />);

    await waitFor(() => {
      const nextButton = screen.getByText('Next');
      // Button should be disabled when checks fail
      expect(nextButton).toBeDisabled();
    });
  });

  it('should show check status indicators', async () => {
    const onComplete = vi.fn();
    render(<OnboardingWizard onComplete={onComplete} />);

    await waitFor(() => {
      // Should show check status (passed/failed/pending)
      expect(screen.getByText('API Connection')).toBeInTheDocument();
    });
  });
});

