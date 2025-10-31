import { EventEmitter } from 'events';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
}

export interface AgentUpdate {
  agent_id: string;
  status: string;
  metrics: {
    cpu_usage: number;
    memory_usage: number;
    response_time: number;
  };
}

export interface TaskUpdate {
  task_id: string;
  status: string;
  progress: number;
  current_step: string;
}

export interface SystemUpdate {
  health_score: number;
  active_agents: number;
  task_queue_length: number;
  throughput_per_second: number;
}

type ConnectionState = 'connecting' | 'connected' | 'reconnecting' | 'closing' | 'disconnected' | 'unknown';

class WebSocketService extends EventEmitter {
  private ws: WebSocket | null = null;
  // Backoff configuration
  private baseReconnectMs: number = 1000; // 1s base
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private isConnecting: boolean = false;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private connectionState: ConnectionState = 'disconnected';

  constructor() {
    super();
    this.connect();
  }

  private connect(): void {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;
    this.setConnectionState(this.reconnectAttempts > 0 ? 'reconnecting' : 'connecting');
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
    
    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventListeners();
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.handleReconnect();
    }
  }

  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      this.setConnectionState('connected');
      this.emit('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.isConnecting = false;
      this.stopHeartbeat();
      this.setConnectionState('disconnected');
      this.emit('disconnected');
      
      if (event.code !== 1000) { // Not a normal closure
        this.handleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.isConnecting = false;
      this.setConnectionState('disconnected');
      this.emit('error', error);
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'agent_update':
        this.emit('agentUpdate', message.data as AgentUpdate);
        break;
      case 'task_update':
        this.emit('taskUpdate', message.data as TaskUpdate);
        break;
      case 'system_update':
        this.emit('systemUpdate', message.data as SystemUpdate);
        break;
      case 'health_update':
        this.emit('healthUpdate', message.data);
        break;
      case 'metrics_update':
        this.emit('metricsUpdate', message.data);
        break;
      case 'notification':
        this.emit('notification', message.data);
        break;
      default:
        console.log('Unknown message type:', message.type);
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    // Exponential backoff with full jitter: sleep = rand(0, min(cap, base * 2^attempt))
    const capMs = 30000; // 30s cap
    const expMs = Math.min(capMs, this.baseReconnectMs * Math.pow(2, this.reconnectAttempts));
    const delayMs = Math.floor(Math.random() * expMs);

    setTimeout(() => {
      this.connect();
    }, delayMs);
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', data: {}, timestamp: Date.now() });
      }
    }, 30000); // Send ping every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  public send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }

  public subscribe(event: string, callback: (...args: any[]) => void): void {
    this.on(event, callback);
  }

  public unsubscribe(event: string, callback: (...args: any[]) => void): void {
    this.off(event, callback);
  }

  public disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.setConnectionState('closing');
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  public getConnectionState(): ConnectionState {
    if (!this.ws) {
      return this.connectionState;
    }

    // Prefer internal state for transitional phases; fall back to ws.readyState
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return this.connectionState === 'reconnecting' ? 'reconnecting' : 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }

  private setConnectionState(state: ConnectionState): void {
    if (this.connectionState !== state) {
      this.connectionState = state;
      this.emit('connectionStateChange', state);
    }
  }
}

// Export singleton instance
export const wsService = new WebSocketService();
export default wsService;