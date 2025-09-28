/**
 * AMAS Real-time Update Hooks
 * 
 * React hooks for real-time data updates via WebSocket:
 * - System status monitoring
 * - Agent activity tracking
 * - Task progress updates
 * - Live notifications
 * - Connection health monitoring
 * 
 * Provides seamless real-time experience for the AMAS web interface.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { WebSocketService, SystemStatusUpdate, AgentStatusUpdate, TaskUpdate, NotificationMessage } from '../services/websocket';

export interface UseRealTimeSystemProps {
  autoConnect?: boolean;
  reconnectOnError?: boolean;
}

export interface UseRealTimeSystemReturn {
  systemStatus: SystemStatusUpdate | null;
  agents: AgentStatusUpdate[];
  tasks: TaskUpdate[];
  notifications: NotificationMessage[];
  connectionStatus: {
    connected: boolean;
    reconnectAttempts: number;
    lastError?: string;
    latency?: number;
  };
  actions: {
    connect: () => void;
    disconnect: () => void;
    subscribeToTask: (taskId: string) => void;
    unsubscribeFromTask: (taskId: string) => void;
    subscribeToAgent: (agentId: string) => void;
    unsubscribeFromAgent: (agentId: string) => void;
    markNotificationRead: (notificationId: string) => void;
    clearNotifications: () => void;
  };
}

/**
 * Main hook for real-time AMAS system updates
 */
export const useRealTimeSystem = (props: UseRealTimeSystemProps = {}): UseRealTimeSystemReturn => {
  const {
    autoConnect = true,
    reconnectOnError = true
  } = props;

  // State
  const [systemStatus, setSystemStatus] = useState<SystemStatusUpdate | null>(null);
  const [agents, setAgents] = useState<AgentStatusUpdate[]>([]);
  const [tasks, setTasks] = useState<TaskUpdate[]>([]);
  const [notifications, setNotifications] = useState<NotificationMessage[]>([]);
  const [connectionStatus, setConnectionStatus] = useState({
    connected: false,
    reconnectAttempts: 0,
    lastError: undefined as string | undefined,
    latency: undefined as number | undefined
  });

  // WebSocket service ref
  const wsServiceRef = useRef<WebSocketService | null>(null);
  const subscribedTasks = useRef<Set<string>>(new Set());
  const subscribedAgents = useRef<Set<string>>(new Set());

  // Initialize WebSocket service
  useEffect(() => {
    wsServiceRef.current = new WebSocketService();
    
    if (autoConnect) {
      wsServiceRef.current.connect();
    }

    return () => {
      if (wsServiceRef.current) {
        wsServiceRef.current.disconnect();
      }
    };
  }, [autoConnect]);

  // Setup message handlers
  useEffect(() => {
    const wsService = wsServiceRef.current;
    if (!wsService) return;

    // System status handler
    const handleSystemStatus = (status: SystemStatusUpdate) => {
      setSystemStatus(status);
      setConnectionStatus(prev => ({
        ...prev,
        connected: true,
        lastError: undefined
      }));
    };

    // Agent status handler
    const handleAgentStatus = (agentUpdate: AgentStatusUpdate) => {
      setAgents(prev => {
        const updated = [...prev];
        const existingIndex = updated.findIndex(a => a.agent_id === agentUpdate.agent_id);
        
        if (existingIndex >= 0) {
          updated[existingIndex] = agentUpdate;
        } else {
          updated.push(agentUpdate);
        }
        
        return updated;
      });
    };

    // Task update handler
    const handleTaskUpdate = (taskUpdate: TaskUpdate) => {
      setTasks(prev => {
        const updated = [...prev];
        const existingIndex = updated.findIndex(t => t.task_id === taskUpdate.task_id);
        
        if (existingIndex >= 0) {
          updated[existingIndex] = taskUpdate;
        } else {
          updated.push(taskUpdate);
        }
        
        // Remove completed tasks after 5 minutes
        return updated.filter(task => {
          if (task.status === 'completed') {
            const updatedAt = new Date(task.updated_at);
            const now = new Date();
            return (now.getTime() - updatedAt.getTime()) < 300000; // 5 minutes
          }
          return true;
        });
      });
    };

    // Notification handler
    const handleNotification = (notification: NotificationMessage) => {
      setNotifications(prev => [notification, ...prev.slice(0, 49)]); // Keep last 50
    };

    // Connection status handler
    const handleConnectionChange = () => {
      const stats = wsService.getConnectionStats();
      setConnectionStatus({
        connected: stats.connected,
        reconnectAttempts: stats.reconnectAttempts,
        lastError: stats.lastError,
        latency: stats.latency
      });
    };

    // Subscribe to message types
    wsService.onSystemStatus(handleSystemStatus);
    wsService.onAgentStatus(handleAgentStatus);
    wsService.onTaskUpdate(handleTaskUpdate);
    wsService.onNotification(handleNotification);

    // Monitor connection status
    const statusInterval = setInterval(handleConnectionChange, 1000);

    return () => {
      clearInterval(statusInterval);
      wsService.offMessage('system_status', handleSystemStatus);
      wsService.offMessage('agent_status', handleAgentStatus);
      wsService.offMessage('task_update', handleTaskUpdate);
      wsService.offMessage('notification', handleNotification);
    };
  }, []);

  // Actions
  const connect = useCallback(() => {
    wsServiceRef.current?.connect();
  }, []);

  const disconnect = useCallback(() => {
    wsServiceRef.current?.disconnect();
  }, []);

  const subscribeToTask = useCallback((taskId: string) => {
    if (wsServiceRef.current && !subscribedTasks.current.has(taskId)) {
      wsServiceRef.current.subscribeToTask(taskId);
      subscribedTasks.current.add(taskId);
    }
  }, []);

  const unsubscribeFromTask = useCallback((taskId: string) => {
    if (wsServiceRef.current && subscribedTasks.current.has(taskId)) {
      wsServiceRef.current.unsubscribeFromTask(taskId);
      subscribedTasks.current.delete(taskId);
    }
  }, []);

  const subscribeToAgent = useCallback((agentId: string) => {
    if (wsServiceRef.current && !subscribedAgents.current.has(agentId)) {
      wsServiceRef.current.subscribeToAgent(agentId);
      subscribedAgents.current.add(agentId);
    }
  }, []);

  const unsubscribeFromAgent = useCallback((agentId: string) => {
    if (wsServiceRef.current && subscribedAgents.current.has(agentId)) {
      wsServiceRef.current.unsubscribeFromAgent(agentId);
      subscribedAgents.current.delete(agentId);
    }
  }, []);

  const markNotificationRead = useCallback((notificationId: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
    );
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    systemStatus,
    agents,
    tasks,
    notifications,
    connectionStatus,
    actions: {
      connect,
      disconnect,
      subscribeToTask,
      unsubscribeFromTask,
      subscribeToAgent,
      unsubscribeFromAgent,
      markNotificationRead,
      clearNotifications
    }
  };
};

/**
 * Hook for monitoring specific agent in real-time
 */
export const useRealTimeAgent = (agentId: string) => {
  const [agentStatus, setAgentStatus] = useState<AgentStatusUpdate | null>(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const { actions } = useRealTimeSystem({ autoConnect: true });

  useEffect(() => {
    if (agentId && !isSubscribed) {
      actions.subscribeToAgent(agentId);
      setIsSubscribed(true);
    }

    return () => {
      if (agentId && isSubscribed) {
        actions.unsubscribeFromAgent(agentId);
        setIsSubscribed(false);
      }
    };
  }, [agentId, isSubscribed, actions]);

  // Update agent status when agents change
  const { agents } = useRealTimeSystem();
  useEffect(() => {
    const agent = agents.find(a => a.agent_id === agentId);
    if (agent) {
      setAgentStatus(agent);
    }
  }, [agents, agentId]);

  return {
    agentStatus,
    isSubscribed,
    subscribe: () => actions.subscribeToAgent(agentId),
    unsubscribe: () => actions.unsubscribeFromAgent(agentId)
  };
};

/**
 * Hook for monitoring specific task in real-time
 */
export const useRealTimeTask = (taskId: string) => {
  const [taskStatus, setTaskStatus] = useState<TaskUpdate | null>(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const { actions } = useRealTimeSystem({ autoConnect: true });

  useEffect(() => {
    if (taskId && !isSubscribed) {
      actions.subscribeToTask(taskId);
      setIsSubscribed(true);
    }

    return () => {
      if (taskId && isSubscribed) {
        actions.unsubscribeFromTask(taskId);
        setIsSubscribed(false);
      }
    };
  }, [taskId, isSubscribed, actions]);

  // Update task status when tasks change
  const { tasks } = useRealTimeSystem();
  useEffect(() => {
    const task = tasks.find(t => t.task_id === taskId);
    if (task) {
      setTaskStatus(task);
    }
  }, [tasks, taskId]);

  return {
    taskStatus,
    isSubscribed,
    subscribe: () => actions.subscribeToTask(taskId),
    unsubscribe: () => actions.unsubscribeFromTask(taskId)
  };
};

/**
 * Hook for connection health monitoring
 */
export const useConnectionHealth = () => {
  const { connectionStatus, actions } = useRealTimeSystem();
  const [connectionHistory, setConnectionHistory] = useState<Array<{
    timestamp: Date;
    connected: boolean;
    latency?: number;
  }>>([]);

  useEffect(() => {
    // Record connection status changes
    setConnectionHistory(prev => [
      {
        timestamp: new Date(),
        connected: connectionStatus.connected,
        latency: connectionStatus.latency
      },
      ...prev.slice(0, 99) // Keep last 100 entries
    ]);
  }, [connectionStatus.connected, connectionStatus.latency]);

  const getConnectionQuality = useCallback(() => {
    if (!connectionStatus.connected) return 'disconnected';
    
    const latency = connectionStatus.latency;
    if (!latency) return 'unknown';
    
    if (latency < 50) return 'excellent';
    if (latency < 100) return 'good';
    if (latency < 200) return 'fair';
    return 'poor';
  }, [connectionStatus]);

  const getUptimePercentage = useCallback(() => {
    if (connectionHistory.length < 2) return 100;
    
    const connectedEntries = connectionHistory.filter(entry => entry.connected);
    return (connectedEntries.length / connectionHistory.length) * 100;
  }, [connectionHistory]);

  return {
    connectionStatus,
    connectionHistory,
    connectionQuality: getConnectionQuality(),
    uptimePercentage: getUptimePercentage(),
    actions: {
      reconnect: actions.connect,
      disconnect: actions.disconnect
    }
  };
};

/**
 * Hook for performance monitoring
 */
export const useRealTimePerformance = () => {
  const [performanceMetrics, setPerformanceMetrics] = useState({
    messagesPerSecond: 0,
    averageLatency: 0,
    connectionStability: 100,
    dataTransferRate: 0
  });

  const { connectionStatus } = useRealTimeSystem();
  const metricsHistory = useRef<Array<{
    timestamp: Date;
    latency: number;
    connected: boolean;
  }>>([]);

  useEffect(() => {
    // Update metrics history
    if (connectionStatus.latency !== undefined) {
      metricsHistory.current.push({
        timestamp: new Date(),
        latency: connectionStatus.latency,
        connected: connectionStatus.connected
      });

      // Keep only last hour of data
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
      metricsHistory.current = metricsHistory.current.filter(
        entry => entry.timestamp > oneHourAgo
      );

      // Calculate performance metrics
      const recent = metricsHistory.current;
      if (recent.length > 0) {
        const avgLatency = recent.reduce((sum, entry) => sum + entry.latency, 0) / recent.length;
        const connectedEntries = recent.filter(entry => entry.connected);
        const stability = (connectedEntries.length / recent.length) * 100;

        setPerformanceMetrics(prev => ({
          ...prev,
          averageLatency: avgLatency,
          connectionStability: stability
        }));
      }
    }
  }, [connectionStatus.latency, connectionStatus.connected]);

  return {
    performanceMetrics,
    metricsHistory: metricsHistory.current
  };
};

/**
 * Hook for managing WebSocket subscriptions
 */
export const useWebSocketSubscriptions = () => {
  const [activeSubscriptions, setActiveSubscriptions] = useState<Set<string>>(new Set());
  const { actions } = useRealTimeSystem();

  const addSubscription = useCallback((type: 'task' | 'agent', id: string) => {
    if (type === 'task') {
      actions.subscribeToTask(id);
    } else {
      actions.subscribeToAgent(id);
    }
    
    setActiveSubscriptions(prev => new Set([...prev, `${type}:${id}`]));
  }, [actions]);

  const removeSubscription = useCallback((type: 'task' | 'agent', id: string) => {
    if (type === 'task') {
      actions.unsubscribeFromTask(id);
    } else {
      actions.unsubscribeFromAgent(id);
    }
    
    setActiveSubscriptions(prev => {
      const updated = new Set(prev);
      updated.delete(`${type}:${id}`);
      return updated;
    });
  }, [actions]);

  const isSubscribed = useCallback((type: 'task' | 'agent', id: string) => {
    return activeSubscriptions.has(`${type}:${id}`);
  }, [activeSubscriptions]);

  const clearAllSubscriptions = useCallback(() => {
    // Unsubscribe from all tasks and agents
    activeSubscriptions.forEach(subscription => {
      const [type, id] = subscription.split(':');
      if (type === 'task') {
        actions.unsubscribeFromTask(id);
      } else if (type === 'agent') {
        actions.unsubscribeFromAgent(id);
      }
    });
    
    setActiveSubscriptions(new Set());
  }, [activeSubscriptions, actions]);

  return {
    activeSubscriptions: Array.from(activeSubscriptions),
    addSubscription,
    removeSubscription,
    isSubscribed,
    clearAllSubscriptions
  };
};