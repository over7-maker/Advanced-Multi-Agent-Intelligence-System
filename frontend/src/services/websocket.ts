// frontend/src/services/websocket.ts (PRODUCTION-READY WEBSOCKET)
// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface WebSocketMessage {
  event: string;
  data?: any;
  task_id?: string;
  agent_id?: string;
  timestamp: string;
}

export type WebSocketEventHandler = (data: any) => void;

// ============================================================================
// WEBSOCKET SERVICE CLASS
// ============================================================================

class WebSocketService {
  private ws: WebSocket | null = null;
  private eventHandlers: Map<string, Set<WebSocketEventHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private isConnecting = false;
  private shouldReconnect = true;
  private pingInterval: ReturnType<typeof setInterval> | null = null;
  private connectionUrl: string;

  constructor() {
    const wsProtocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Use relative URL to work with any port (recommended)
    // Falls back to environment variable or current host
    const wsHost = import.meta.env.VITE_WS_URL || (typeof window !== 'undefined' ? window.location.host : window.location.hostname + ':8001');
    // Use relative WebSocket URL if on same origin, otherwise use full URL
    if (typeof window !== 'undefined' && !import.meta.env.VITE_WS_URL) {
      this.connectionUrl = `${wsProtocol}//${window.location.host}/ws`;
    } else {
      this.connectionUrl = `${wsProtocol}//${wsHost}/ws`;
    }
  }

  // ========================================================================
  // CONNECTION MANAGEMENT
  // ========================================================================

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      console.log('WebSocket already connected or connecting');
      return;
    }

    this.isConnecting = true;
    this.shouldReconnect = true;

    try {
      // Get auth token
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      if (!token) {
        console.error('No auth token found for WebSocket connection');
        this.isConnecting = false;
        return;
      }

      // Create WebSocket connection with auth token
      const wsUrl = `${this.connectionUrl}?token=${token}`;
      this.ws = new WebSocket(wsUrl);

      // Connection opened
      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.startHeartbeat();

        // Notify connection handlers
        this.emit('connected', { timestamp: new Date().toISOString() });
      };

      // Message received
      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('📨 WebSocket message:', message.event);

          // Handle heartbeat
          if (message.event === 'heartbeat' || message.event === 'pong') {
            return; // Ignore heartbeat messages
          }

          // Emit to registered handlers
          this.emit(message.event, message.data || message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      // Connection closed
      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        this.isConnecting = false;
        this.stopHeartbeat();

        // Notify disconnection handlers
        this.emit('disconnected', { timestamp: new Date().toISOString() });

        // Attempt reconnection
        if (this.shouldReconnect) {
          this.scheduleReconnect();
        }
      };

      // Connection error
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;

        // Notify error handlers
        this.emit('error', { error, timestamp: new Date().toISOString() });
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    this.shouldReconnect = false;
    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max WebSocket reconnection attempts reached');
      this.emit('reconnect_failed', {
        attempts: this.reconnectAttempts,
        timestamp: new Date().toISOString(),
      });
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );

    console.log(`Reconnecting WebSocket in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      if (this.shouldReconnect) {
        console.log('Attempting WebSocket reconnection...');
        this.connect();
      }
    }, delay);
  }

  private startHeartbeat(): void {
    this.pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send('ping', {});
      }
    }, 30000); // Ping every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  // ========================================================================
  // EVENT HANDLING
  // ========================================================================

  on(event: string, handler: WebSocketEventHandler): () => void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }

    this.eventHandlers.get(event)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.off(event, handler);
    };
  }

  off(event: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.eventHandlers.delete(event);
      }
    }
  }

  private emit(event: string, data: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in WebSocket event handler for '${event}':`, error);
        }
      });
    }
  }

  // ========================================================================
  // MESSAGE SENDING
  // ========================================================================

  send(command: string, data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          command,
          ...data,
        })
      );
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  subscribeToTask(taskId: string): void {
    this.send('subscribe_task', { task_id: taskId });
  }

  unsubscribeFromTask(taskId: string): void {
    this.send('unsubscribe_task', { task_id: taskId });
  }

  // ========================================================================
  // UTILITY METHODS
  // ========================================================================

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN || false;
  }

  getReadyState(): number | null {
    return this.ws?.readyState ?? null;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();

// Export class for testing
export default WebSocketService;
