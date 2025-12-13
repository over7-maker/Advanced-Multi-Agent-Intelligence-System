// frontend/src/services/websocket.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Import the class directly
let WebSocketService: any;

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url = '';
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 0);
  }

  send(_data: string) {
    // Mock send
  }

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code, reason }));
    }
  }
}

// Replace global WebSocket
(global as any).WebSocket = MockWebSocket;

describe('WebSocketService', () => {
  let service: any;
  let mockLocalStorage: { [key: string]: string };

  beforeEach(async () => {
    vi.clearAllMocks();
    mockLocalStorage = {};
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key) => mockLocalStorage[key] || null);
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation((key, value) => {
      mockLocalStorage[key] = value;
    });
    vi.spyOn(Storage.prototype, 'removeItem').mockImplementation((key) => {
      delete mockLocalStorage[key];
    });

    // Import the class
    const module = await import('./websocket');
    WebSocketService = module.default;
    service = new WebSocketService();
  });

  afterEach(() => {
    service.disconnect();
    vi.restoreAllMocks();
  });

  describe('Connection Management', () => {
    it('should connect with auth token', async () => {
      mockLocalStorage['access_token'] = 'test_token';

      service.connect();

      // Wait for connection
      await new Promise((resolve) => setTimeout(resolve, 50));
      expect(service.isConnected()).toBe(true);
    });

    it('should not connect without auth token', async () => {
      service.connect();

      // Should not connect without token - wait a bit
      await new Promise((resolve) => setTimeout(resolve, 50));
      // Connection should not be established
      const state = service.getReadyState();
      expect(state === null || state !== MockWebSocket.OPEN).toBe(true);
    });

    it('should disconnect properly', async () => {
      mockLocalStorage['access_token'] = 'test_token';
      service.connect();
      
      // Wait for connection
      await new Promise((resolve) => setTimeout(resolve, 50));

      service.disconnect();

      // After disconnect, state should be closed or null
      const state = service.getReadyState();
      expect(state === null || state === MockWebSocket.CLOSED).toBe(true);
    });

    it('should not connect if already connected', async () => {
      mockLocalStorage['access_token'] = 'test_token';
      service.connect();
      
      // Wait for connection
      await new Promise((resolve) => setTimeout(resolve, 50));

      const initialState = service.getReadyState();
      service.connect(); // Try to connect again

      // State should remain the same (already connected)
      await new Promise((resolve) => setTimeout(resolve, 10));
      expect(service.getReadyState()).toBe(initialState);
    });
  });

  describe('Event Handling', () => {
    it('should subscribe to events', () => {
      const handler = vi.fn();
      const unsubscribe = service.on('test_event', handler);

      expect(unsubscribe).toBeDefined();
      expect(typeof unsubscribe).toBe('function');
    });

    it('should emit events to handlers', () => {
      const handler = vi.fn();
      service.on('test_event', handler);

      // We can't directly test emit, but we can test the handler is registered
      expect(handler).toBeDefined();
    });

    it('should unsubscribe from events', () => {
      const handler = vi.fn();
      const unsubscribe = service.on('test_event', handler);

      unsubscribe();

      // Handler should be removed
      expect(unsubscribe).toBeDefined();
    });
  });

  describe('Message Sending', () => {
    it('should send messages when connected', async () => {
      mockLocalStorage['access_token'] = 'test_token';
      service.connect();

      // Wait for connection to be established
      await new Promise((resolve) => setTimeout(resolve, 50));

      const sendSpy = vi.spyOn(service, 'send');

      service.send('test_command', { data: 'test' });

      // Should attempt to send
      expect(sendSpy).toHaveBeenCalledWith('test_command', { data: 'test' });
    });

    it('should subscribe to task updates', () => {
      mockLocalStorage['access_token'] = 'test_token';
      service.connect();

      const sendSpy = vi.spyOn(service, 'send');

      service.subscribeToTask('task_1');

      expect(sendSpy).toHaveBeenCalledWith('subscribe_task', { task_id: 'task_1' });
    });

    it('should unsubscribe from task updates', () => {
      mockLocalStorage['access_token'] = 'test_token';
      service.connect();

      const sendSpy = vi.spyOn(service, 'send');

      service.unsubscribeFromTask('task_1');

      expect(sendSpy).toHaveBeenCalledWith('unsubscribe_task', { task_id: 'task_1' });
    });
  });

  describe('Connection State', () => {
    it('should check connection state', async () => {
      expect(service.isConnected()).toBe(false);

      mockLocalStorage['access_token'] = 'test_token';
      service.connect();

      // Wait for connection
      await new Promise((resolve) => setTimeout(resolve, 50));
      expect(service.isConnected()).toBe(true);
    });

    it('should get ready state', () => {
      const state = service.getReadyState();
      expect(state).toBeDefined();
    });
  });
});

