/// <reference types="../vite-env" />
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
    // Use backend URL for WebSocket (not frontend dev server)
    // In development, Vite proxy should handle /ws, but we'll use backend directly
    const backendHost = import.meta.env.VITE_API_URL?.replace('http://', '').replace('https://', '') || 'localhost:8000';
    this.connectionUrl = `${wsProtocol}//${backendHost}/ws`;
  }

  // ========================================================================
  // CONNECTION MANAGEMENT
  // ========================================================================

  connect(): void {
    // Check if already connected or connecting
    if (this.ws) {
      const state = this.ws.readyState;
      if (state === WebSocket.OPEN) {
        console.log('WebSocket already connected');
        return;
      }
      if (state === WebSocket.CONNECTING) {
        console.log('WebSocket already connecting');
        return;
      }
      // If closing or closed, clean up first
      if (state === WebSocket.CLOSING || state === WebSocket.CLOSED) {
        this.ws = null;
      }
    }
    
    if (this.isConnecting) {
      console.log('WebSocket connection already in progress');
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
        console.log('[WebSocket] Connected', { timestamp: new Date().toISOString() });
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
          
          // Log WebSocket message (skip heartbeat for cleaner logs)
          if (message.event !== 'heartbeat' && message.event !== 'pong') {
            console.log(`[WebSocket] ${message.event}`, {
              task_id: message.task_id,
              agent_id: message.agent_id,
              data: message.data,
              timestamp: message.timestamp || new Date().toISOString()
            });
          }

          // Handle heartbeat
          if (message.event === 'heartbeat' || message.event === 'pong') {
            return; // Ignore heartbeat messages
          }

          // Emit to registered handlers
          this.emit(message.event, message.data || message);
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error, {
            raw: event.data,
            timestamp: new Date().toISOString()
          });
        }
      };

      // Connection closed
      this.ws.onclose = (event) => {
        console.log('[WebSocket] Closed', {
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean,
          timestamp: new Date().toISOString()
        });
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
        console.error('[WebSocket] Error', {
          error,
          reconnectAttempts: this.reconnectAttempts,
          timestamp: new Date().toISOString()
        });
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
    this.isConnecting = false;

    if (this.ws) {
      // Remove event handlers before closing to prevent errors
      this.ws.onopen = null;
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.onmessage = null;
      
      try {
        if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
          this.ws.close(1000, 'Client disconnect');
        }
      } catch (e) {
        // Ignore errors when closing
      }
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
      // Silently fail - connection will be established when needed
      // Don't log warnings for expected behavior
      if (this.ws?.readyState === WebSocket.CONNECTING) {
        // Queue message for when connection is ready
        setTimeout(() => {
          if (this.ws?.readyState === WebSocket.OPEN) {
            this.send(command, data);
          }
        }, 100);
      }
    }
  }

  subscribeToTask(taskId: string): void {
    // Only subscribe if connected or connecting
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) {
      this.send('subscribe_task', { task_id: taskId });
    } else {
      // Connect first, then subscribe
      this.connect();
      setTimeout(() => {
        if (this.isConnected()) {
          this.send('subscribe_task', { task_id: taskId });
        }
      }, 500);
    }
  }

  unsubscribeFromTask(taskId: string): void {
    // Only unsubscribe if connected
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send('unsubscribe_task', { task_id: taskId });
    }
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
