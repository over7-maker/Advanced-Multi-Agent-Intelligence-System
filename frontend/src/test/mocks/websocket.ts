// Mock WebSocket service
import { vi } from 'vitest';

export const mockWebSocketService = {
  connect: vi.fn(),
  disconnect: vi.fn(),
  on: vi.fn(() => vi.fn()), // Returns unsubscribe function
  off: vi.fn(),
  send: vi.fn(),
  subscribeToTask: vi.fn(),
  unsubscribeFromTask: vi.fn(),
  isConnected: vi.fn(() => true),
  getReadyState: vi.fn(() => 1), // WebSocket.OPEN
};

