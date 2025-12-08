// frontend/src/services/__tests__/websocket.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { websocketService } from '../websocket';

// Mock WebSocket
class MockWebSocket {
  readyState: number = 0; // CONNECTING
  url: string;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // Simulate connection
    setTimeout(() => {
      this.readyState = 1; // OPEN
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 10);
  }

  send(_data: string) {
    // Mock send
  }

  close() {
    this.readyState = 3; // CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close'));
    }
  }

  addEventListener(event: string, handler: any) {
    if (event === 'open') this.onopen = handler;
    if (event === 'close') this.onclose = handler;
    if (event === 'error') this.onerror = handler;
    if (event === 'message') this.onmessage = handler;
  }

  removeEventListener(event: string, handler: any) {
    if (event === 'open' && this.onopen === handler) this.onopen = null;
    if (event === 'close' && this.onclose === handler) this.onclose = null;
    if (event === 'error' && this.onerror === handler) this.onerror = null;
    if (event === 'message' && this.onmessage === handler) this.onmessage = null;
  }
}

describe('WebSocketService', () => {
  let originalWebSocket: typeof WebSocket;

  beforeEach(() => {
    originalWebSocket = global.WebSocket as any;
    (global.WebSocket as any) = MockWebSocket;
    vi.useFakeTimers();
    // Set auth token for WebSocket connection
    localStorage.setItem('access_token', 'test_token');
    // Reset service state
    websocketService.disconnect();
    (websocketService as any).ws = null;
    (websocketService as any).reconnectAttempts = 0;
    (websocketService as any).reconnectDelay = 1000;
    (websocketService as any).isConnecting = false;
    (websocketService as any).shouldReconnect = true;
    // Clear event handlers
    (websocketService as any).eventHandlers = new Map();
  });

  afterEach(() => {
    websocketService.disconnect();
    (global.WebSocket as any) = originalWebSocket;
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  describe('Connection Management', () => {
    it('should connect to WebSocket', async () => {
      websocketService.connect();
      
      // Wait for connection
      await vi.advanceTimersByTimeAsync(100);
      
      expect(websocketService.isConnected()).toBe(true);
    });

    it('should disconnect from WebSocket', async () => {
      websocketService.connect();
      
      // Wait for connection
      await vi.advanceTimersByTimeAsync(100);
      
      websocketService.disconnect();
      
      expect(websocketService.isConnected()).toBe(false);
    });

    it('should handle connection errors', async () => {
      const errorHandler = vi.fn();
      websocketService.on('error', errorHandler);
      
      websocketService.connect();
      
      // Wait for connection
      await vi.advanceTimersByTimeAsync(100);
      
      // Simulate error
      if (websocketService['ws']) {
        (websocketService['ws'] as any).onerror(new Event('error'));
      }
      
      // Should trigger error handler
      expect(errorHandler).toHaveBeenCalled();
    });
  });

  describe('Event Handling', () => {
    it('should subscribe to events', () => {
      const handler = vi.fn();
      const unsubscribe = websocketService.on('test_event', handler);
      
      expect(typeof unsubscribe).toBe('function');
    });

    it('should emit events to handlers', () => {
      const handler = vi.fn();
      websocketService.on('test_event', handler);
      
      websocketService['emit']('test_event', { data: 'test' });
      
      expect(handler).toHaveBeenCalledWith({ data: 'test' });
    });

    it('should unsubscribe from events', () => {
      const handler = vi.fn();
      const unsubscribe = websocketService.on('test_event', handler);
      
      unsubscribe();
      websocketService['emit']('test_event', { data: 'test' });
      
      expect(handler).not.toHaveBeenCalled();
    });

    it('should handle multiple handlers for same event', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      
      websocketService.on('test_event', handler1);
      websocketService.on('test_event', handler2);
      
      websocketService['emit']('test_event', { data: 'test' });
      
      expect(handler1).toHaveBeenCalled();
      expect(handler2).toHaveBeenCalled();
    });
  });

  describe('Message Sending', () => {
    it('should send messages', async () => {
      websocketService.connect();
      
      // Wait for connection
      await vi.advanceTimersByTimeAsync(100);
      
      if (websocketService['ws']) {
        const sendSpy = vi.spyOn(websocketService['ws'] as any, 'send');
        websocketService.send('test_command', { data: 'test' });
        
        expect(sendSpy).toHaveBeenCalled();
      }
    });

    it('should subscribe to task updates', async () => {
      websocketService.connect();
      
      // Wait for connection
      await vi.advanceTimersByTimeAsync(100);
      
      if (websocketService['ws']) {
        const sendSpy = vi.spyOn(websocketService['ws'] as any, 'send');
        websocketService.subscribeToTask('task1');
        
        expect(sendSpy).toHaveBeenCalled();
      }
    });

    it('should unsubscribe from task updates', async () => {
      websocketService.connect();
      
      // Wait for connection
      await vi.advanceTimersByTimeAsync(100);
      
      websocketService.subscribeToTask('task1');
      
      if (websocketService['ws']) {
        const sendSpy = vi.spyOn(websocketService['ws'] as any, 'send');
        websocketService.unsubscribeFromTask('task1');
        
        expect(sendSpy).toHaveBeenCalled();
      }
    });
  });

  describe('Reconnection', () => {
    it('should attempt reconnection on disconnect', async () => {
      websocketService.connect();
      
      // Simulate disconnect
      if (websocketService['ws']) {
        (websocketService['ws'] as any).onclose(new CloseEvent('close'));
      }
      
      // Should schedule reconnection
      await vi.advanceTimersByTimeAsync(1000);
      
      // Reconnection should be attempted
      expect(websocketService['reconnectAttempts']).toBeGreaterThan(0);
    });

    it('should use exponential backoff for reconnection', async () => {
      websocketService.connect();
      
      // Simulate multiple disconnects
      for (let i = 0; i < 3; i++) {
        if (websocketService['ws']) {
          (websocketService['ws'] as any).onclose(new CloseEvent('close'));
        }
        await vi.advanceTimersByTimeAsync(1000);
      }
      
      // Delay should increase
      expect(websocketService['reconnectDelay']).toBeGreaterThan(1000);
    });
  });

  describe('Heartbeat', () => {
    it('should send heartbeat messages', async () => {
      websocketService.connect();
      
      const sendSpy = vi.spyOn(websocketService['ws'] as any, 'send');
      
      // Advance time to trigger heartbeat
      await vi.advanceTimersByTimeAsync(30000);
      
      // Heartbeat should be sent
      expect(sendSpy).toHaveBeenCalled();
    });
  });

  describe('Utility Methods', () => {
    it('should check connection status', async () => {
      expect(websocketService.isConnected()).toBe(false);
      
      websocketService.connect();
      
      // Wait for connection
      await vi.advanceTimersByTimeAsync(100);
      
      expect(websocketService.isConnected()).toBe(true);
    });

    it('should get ready state', async () => {
      expect(websocketService.getReadyState()).toBeNull();
      
      websocketService.connect();
      
      // Wait for connection
      await vi.advanceTimersByTimeAsync(100);
      
      // Ready state should be OPEN (1) or CONNECTING (0)
      const readyState = websocketService.getReadyState();
      expect(readyState === 1 || readyState === 0).toBe(true);
    });
  });
});

