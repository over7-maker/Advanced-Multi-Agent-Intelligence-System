/**
 * AMAS WebSocket Service
 * 
 * Real-time communication service for the AMAS web interface:
 * - Live system status updates
 * - Real-time agent activity monitoring
 * - Task progress notifications
 * - System alerts and notifications
 * - Bidirectional communication with backend
 * 
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Message queuing during disconnection
 * - Type-safe message handling
 * - Connection health monitoring
 * - Error recovery and resilience
 */

import { io, Socket } from 'socket.io-client';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  id?: string;
}

export interface SystemStatusUpdate {
  status: string;
  agents: number;
  active_tasks: number;
  total_tasks: number;
  timestamp: string;
}

export interface AgentStatusUpdate {
  agent_id: string;
  status: string;
  current_task?: string;
  last_activity: string;
  metrics: {
    tasks_completed: number;
    success_rate: number;
    avg_response_time: number;
  };
}

export interface TaskUpdate {
  task_id: string;
  status: string;
  progress: number;
  result?: any;
  error?: string;
  updated_at: string;
}

export interface NotificationMessage {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  action?: {
    label: string;
    url: string;
  };
}

export type MessageHandler<T = any> = (data: T) => void;

export interface ConnectionStats {
  connected: boolean;
  connectionTime?: Date;
  reconnectAttempts: number;
  lastError?: string;
  messagesReceived: number;
  messagesSent: number;
  latency?: number;
}

export class WebSocketService {
  private socket: Socket | null = null;
  private messageHandlers: Map<string, MessageHandler[]> = new Map();
  private messageQueue: WebSocketMessage[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private connectionStats: ConnectionStats = {
    connected: false,
    reconnectAttempts: 0,
    messagesReceived: 0,
    messagesSent: 0
  };
  private heartbeatInterval?: NodeJS.Timeout;
  private latencyCheckInterval?: NodeJS.Timeout;

  constructor(
    private serverUrl: string = process.env.REACT_APP_WS_URL || 'ws://localhost:8000',
    private authToken?: string
  ) {
    this.setupEventHandlers();
  }

  /**
   * Connect to WebSocket server
   */
  public connect(): void {
    try {
      if (this.socket?.connected) {
        console.log('WebSocket already connected');
        return;
      }

      console.log(`Connecting to WebSocket server: ${this.serverUrl}`);

      // Create socket connection
      this.socket = io(this.serverUrl, {
        transports: ['websocket'],
        auth: {
          token: this.authToken || localStorage.getItem('amas_token')
        },
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectDelay,
        timeout: 10000
      });

      this.setupSocketEventHandlers();

    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      this.connectionStats.lastError = error instanceof Error ? error.message : 'Unknown error';
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  public disconnect(): void {
    try {
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
      }
      
      if (this.latencyCheckInterval) {
        clearInterval(this.latencyCheckInterval);
      }

      if (this.socket) {
        this.socket.disconnect();
        this.socket = null;
      }

      this.connectionStats.connected = false;
      console.log('WebSocket disconnected');

    } catch (error) {
      console.error('Error disconnecting WebSocket:', error);
    }
  }

  /**
   * Set authentication token
   */
  public setAuthToken(token: string): void {
    this.authToken = token;
    
    if (this.socket) {
      this.socket.auth = { token };
      this.socket.connect();
    }
  }

  /**
   * Subscribe to message type with handler
   */
  public onMessage<T = any>(messageType: string, handler: MessageHandler<T>): void {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, []);
    }
    
    this.messageHandlers.get(messageType)!.push(handler);
    console.log(`Subscribed to WebSocket message type: ${messageType}`);
  }

  /**
   * Unsubscribe from message type
   */
  public offMessage(messageType: string, handler?: MessageHandler): void {
    if (!this.messageHandlers.has(messageType)) {
      return;
    }

    if (handler) {
      const handlers = this.messageHandlers.get(messageType)!;
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    } else {
      this.messageHandlers.delete(messageType);
    }

    console.log(`Unsubscribed from WebSocket message type: ${messageType}`);
  }

  /**
   * Send message to server
   */
  public sendMessage(messageType: string, data: any): void {
    const message: WebSocketMessage = {
      type: messageType,
      data,
      timestamp: new Date().toISOString(),
      id: this.generateMessageId()
    };

    if (this.socket?.connected) {
      this.socket.emit('message', message);
      this.connectionStats.messagesSent++;
      console.log(`WebSocket message sent: ${messageType}`, data);
    } else {
      // Queue message for when connection is restored
      this.messageQueue.push(message);
      console.log(`WebSocket message queued: ${messageType}`, data);
    }
  }

  /**
   * Subscribe to system status updates
   */
  public onSystemStatus(handler: MessageHandler<SystemStatusUpdate>): void {
    this.onMessage('system_status', handler);
  }

  /**
   * Subscribe to agent status updates
   */
  public onAgentStatus(handler: MessageHandler<AgentStatusUpdate>): void {
    this.onMessage('agent_status', handler);
  }

  /**
   * Subscribe to task updates
   */
  public onTaskUpdate(handler: MessageHandler<TaskUpdate>): void {
    this.onMessage('task_update', handler);
  }

  /**
   * Subscribe to notifications
   */
  public onNotification(handler: MessageHandler<NotificationMessage>): void {
    this.onMessage('notification', handler);
  }

  /**
   * Request real-time task monitoring
   */
  public subscribeToTask(taskId: string): void {
    this.sendMessage('subscribe_task', { task_id: taskId });
  }

  /**
   * Stop monitoring specific task
   */
  public unsubscribeFromTask(taskId: string): void {
    this.sendMessage('unsubscribe_task', { task_id: taskId });
  }

  /**
   * Request real-time agent monitoring
   */
  public subscribeToAgent(agentId: string): void {
    this.sendMessage('subscribe_agent', { agent_id: agentId });
  }

  /**
   * Stop monitoring specific agent
   */
  public unsubscribeFromAgent(agentId: string): void {
    this.sendMessage('unsubscribe_agent', { agent_id: agentId });
  }

  /**
   * Get connection statistics
   */
  public getConnectionStats(): ConnectionStats {
    return { ...this.connectionStats };
  }

  /**
   * Check if WebSocket is connected
   */
  public isConnected(): boolean {
    return this.socket?.connected || false;
  }

  /**
   * Setup socket event handlers
   */
  private setupSocketEventHandlers(): void {
    if (!this.socket) return;

    // Connection events
    this.socket.on('connect', () => {
      console.log('WebSocket connected successfully');
      this.connectionStats.connected = true;
      this.connectionStats.connectionTime = new Date();
      this.reconnectAttempts = 0;
      
      // Send queued messages
      this.processMessageQueue();
      
      // Start heartbeat
      this.startHeartbeat();
      
      // Start latency checking
      this.startLatencyCheck();
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.connectionStats.connected = false;
      this.connectionStats.lastError = reason;
      
      // Clear intervals
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
      }
      if (this.latencyCheckInterval) {
        clearInterval(this.latencyCheckInterval);
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.connectionStats.lastError = error.message;
      this.reconnectAttempts++;
      this.connectionStats.reconnectAttempts = this.reconnectAttempts;
      
      // Exponential backoff for reconnection
      this.reconnectDelay = Math.min(
        this.reconnectDelay * 2,
        this.maxReconnectDelay
      );
    });

    // Message handling
    this.socket.on('message', (message: WebSocketMessage) => {
      this.handleIncomingMessage(message);
    });

    // Specific message types
    this.socket.on('system_status', (data: SystemStatusUpdate) => {
      this.handleIncomingMessage({ type: 'system_status', data, timestamp: new Date().toISOString() });
    });

    this.socket.on('agent_status', (data: AgentStatusUpdate) => {
      this.handleIncomingMessage({ type: 'agent_status', data, timestamp: new Date().toISOString() });
    });

    this.socket.on('task_update', (data: TaskUpdate) => {
      this.handleIncomingMessage({ type: 'task_update', data, timestamp: new Date().toISOString() });
    });

    this.socket.on('notification', (data: NotificationMessage) => {
      this.handleIncomingMessage({ type: 'notification', data, timestamp: new Date().toISOString() });
    });

    // Latency measurement
    this.socket.on('pong', (timestamp: number) => {
      const latency = Date.now() - timestamp;
      this.connectionStats.latency = latency;
    });
  }

  /**
   * Setup event handlers for the service
   */
  private setupEventHandlers(): void {
    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && !this.isConnected()) {
        console.log('Page became visible, reconnecting WebSocket...');
        this.connect();
      }
    });

    // Handle online/offline events
    window.addEventListener('online', () => {
      console.log('Network connection restored, reconnecting WebSocket...');
      this.connect();
    });

    window.addEventListener('offline', () => {
      console.log('Network connection lost');
      this.connectionStats.lastError = 'Network offline';
    });
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleIncomingMessage(message: WebSocketMessage): void {
    try {
      this.connectionStats.messagesReceived++;
      
      console.log(`WebSocket message received: ${message.type}`, message.data);

      // Call registered handlers for this message type
      const handlers = this.messageHandlers.get(message.type);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message.data);
          } catch (error) {
            console.error(`Error in WebSocket message handler for ${message.type}:`, error);
          }
        });
      }

      // Call global handlers
      const globalHandlers = this.messageHandlers.get('*');
      if (globalHandlers) {
        globalHandlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            console.error('Error in global WebSocket message handler:', error);
          }
        });
      }

    } catch (error) {
      console.error('Error handling WebSocket message:', error);
    }
  }

  /**
   * Process queued messages when connection is restored
   */
  private processMessageQueue(): void {
    if (!this.socket?.connected || this.messageQueue.length === 0) {
      return;
    }

    console.log(`Processing ${this.messageQueue.length} queued WebSocket messages`);

    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.socket.emit('message', message);
        this.connectionStats.messagesSent++;
      }
    }
  }

  /**
   * Start heartbeat to maintain connection
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.socket?.connected) {
        this.socket.emit('heartbeat', { timestamp: Date.now() });
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  /**
   * Start latency checking
   */
  private startLatencyCheck(): void {
    this.latencyCheckInterval = setInterval(() => {
      if (this.socket?.connected) {
        this.socket.emit('ping', Date.now());
      }
    }, 60000); // Check latency every minute
  }

  /**
   * Generate unique message ID
   */
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

/**
 * React Hook for WebSocket integration
 */
export const useWebSocket = (serverUrl?: string) => {
  const [wsService] = React.useState(() => new WebSocketService(serverUrl));
  const [connectionStats, setConnectionStats] = React.useState<ConnectionStats>(
    wsService.getConnectionStats()
  );

  React.useEffect(() => {
    // Connect on mount
    wsService.connect();

    // Update connection stats periodically
    const statsInterval = setInterval(() => {
      setConnectionStats(wsService.getConnectionStats());
    }, 1000);

    // Cleanup on unmount
    return () => {
      clearInterval(statsInterval);
      wsService.disconnect();
    };
  }, [wsService]);

  return {
    wsService,
    connectionStats,
    isConnected: wsService.isConnected(),
    connect: () => wsService.connect(),
    disconnect: () => wsService.disconnect(),
    sendMessage: (type: string, data: any) => wsService.sendMessage(type, data),
    onMessage: <T = any>(type: string, handler: MessageHandler<T>) => wsService.onMessage(type, handler),
    offMessage: (type: string, handler?: MessageHandler) => wsService.offMessage(type, handler)
  };
};

/**
 * React Hook for real-time system status
 */
export const useRealTimeSystemStatus = () => {
  const [systemStatus, setSystemStatus] = React.useState<SystemStatusUpdate | null>(null);
  const [lastUpdate, setLastUpdate] = React.useState<Date | null>(null);
  const { wsService, isConnected } = useWebSocket();

  React.useEffect(() => {
    if (!isConnected) return;

    const handleSystemStatus = (status: SystemStatusUpdate) => {
      setSystemStatus(status);
      setLastUpdate(new Date());
    };

    wsService.onSystemStatus(handleSystemStatus);

    // Request initial status
    wsService.sendMessage('get_system_status', {});

    return () => {
      wsService.offMessage('system_status', handleSystemStatus);
    };
  }, [wsService, isConnected]);

  return {
    systemStatus,
    lastUpdate,
    isConnected
  };
};

/**
 * React Hook for real-time agent monitoring
 */
export const useRealTimeAgents = () => {
  const [agents, setAgents] = React.useState<Map<string, AgentStatusUpdate>>(new Map());
  const [lastUpdate, setLastUpdate] = React.useState<Date | null>(null);
  const { wsService, isConnected } = useWebSocket();

  React.useEffect(() => {
    if (!isConnected) return;

    const handleAgentStatus = (agentUpdate: AgentStatusUpdate) => {
      setAgents(prev => {
        const updated = new Map(prev);
        updated.set(agentUpdate.agent_id, agentUpdate);
        return updated;
      });
      setLastUpdate(new Date());
    };

    wsService.onAgentStatus(handleAgentStatus);

    // Request initial agent status
    wsService.sendMessage('get_all_agents', {});

    return () => {
      wsService.offMessage('agent_status', handleAgentStatus);
    };
  }, [wsService, isConnected]);

  const subscribeToAgent = (agentId: string) => {
    wsService.subscribeToAgent(agentId);
  };

  const unsubscribeFromAgent = (agentId: string) => {
    wsService.unsubscribeFromAgent(agentId);
  };

  return {
    agents: Array.from(agents.values()),
    agentsMap: agents,
    lastUpdate,
    isConnected,
    subscribeToAgent,
    unsubscribeFromAgent
  };
};

/**
 * React Hook for real-time task monitoring
 */
export const useRealTimeTasks = () => {
  const [tasks, setTasks] = React.useState<Map<string, TaskUpdate>>(new Map());
  const [lastUpdate, setLastUpdate] = React.useState<Date | null>(null);
  const { wsService, isConnected } = useWebSocket();

  React.useEffect(() => {
    if (!isConnected) return;

    const handleTaskUpdate = (taskUpdate: TaskUpdate) => {
      setTasks(prev => {
        const updated = new Map(prev);
        updated.set(taskUpdate.task_id, taskUpdate);
        return updated;
      });
      setLastUpdate(new Date());
    };

    wsService.onTaskUpdate(handleTaskUpdate);

    // Request initial task status
    wsService.sendMessage('get_active_tasks', {});

    return () => {
      wsService.offMessage('task_update', handleTaskUpdate);
    };
  }, [wsService, isConnected]);

  const subscribeToTask = (taskId: string) => {
    wsService.subscribeToTask(taskId);
  };

  const unsubscribeFromTask = (taskId: string) => {
    wsService.unsubscribeFromTask(taskId);
  };

  return {
    tasks: Array.from(tasks.values()),
    tasksMap: tasks,
    lastUpdate,
    isConnected,
    subscribeToTask,
    unsubscribeFromTask
  };
};

/**
 * React Hook for real-time notifications
 */
export const useRealTimeNotifications = () => {
  const [notifications, setNotifications] = React.useState<NotificationMessage[]>([]);
  const [unreadCount, setUnreadCount] = React.useState(0);
  const { wsService, isConnected } = useWebSocket();

  React.useEffect(() => {
    if (!isConnected) return;

    const handleNotification = (notification: NotificationMessage) => {
      setNotifications(prev => [notification, ...prev.slice(0, 49)]); // Keep last 50
      setUnreadCount(prev => prev + 1);
    };

    wsService.onNotification(handleNotification);

    return () => {
      wsService.offMessage('notification', handleNotification);
    };
  }, [wsService, isConnected]);

  const markAsRead = (notificationId: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  };

  const clearNotifications = () => {
    setNotifications([]);
    setUnreadCount(0);
  };

  return {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    markAllAsRead,
    clearNotifications
  };
};

// Re-export React for hooks
import React from 'react';