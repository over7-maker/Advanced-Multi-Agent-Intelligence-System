"""
AMAS WebSocket Handler - Real-time Communication Backend

FastAPI WebSocket handler for real-time communication with the web interface:
- Live system status broadcasting
- Real-time agent activity updates
- Task progress notifications
- System alerts and notifications
- Bidirectional communication
- Connection management and health monitoring

Provides enterprise-grade real-time capabilities for the AMAS web interface.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import time
import uuid

from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from fastapi.security import HTTPBearer
import jwt

logger = logging.getLogger(__name__)


@dataclass
class WebSocketConnection:
    """WebSocket connection information"""
    connection_id: str
    websocket: WebSocket
    user_id: str
    user_role: str
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    subscriptions: Set[str] = field(default_factory=set)
    messages_sent: int = 0
    messages_received: int = 0
    is_active: bool = True


@dataclass
class Subscription:
    """Subscription to real-time updates"""
    subscription_id: str
    connection_id: str
    subscription_type: str
    filters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_update: datetime = field(default_factory=datetime.utcnow)
    update_count: int = 0


class WebSocketConnectionManager:
    """
    WebSocket connection manager for real-time communication.
    
    Manages:
    - WebSocket connections and authentication
    - Real-time subscriptions and notifications
    - Connection health monitoring
    - Message broadcasting and routing
    - Performance optimization
    """
    
    def __init__(self, amas_system=None):
        self.amas_system = amas_system
        
        # Connection management
        self.active_connections: Dict[str, WebSocketConnection] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.subscription_index: Dict[str, Set[str]] = {}  # subscription_type -> connection_ids
        
        # Message routing
        self.message_handlers = {
            'get_system_status': self._handle_get_system_status,
            'get_all_agents': self._handle_get_all_agents,
            'get_active_tasks': self._handle_get_active_tasks,
            'subscribe_task': self._handle_subscribe_task,
            'unsubscribe_task': self._handle_unsubscribe_task,
            'subscribe_agent': self._handle_subscribe_agent,
            'unsubscribe_agent': self._handle_unsubscribe_agent,
            'heartbeat': self._handle_heartbeat,
            'ping': self._handle_ping
        }
        
        # Performance metrics
        self.metrics = {
            'total_connections': 0,
            'active_connections': 0,
            'total_messages': 0,
            'messages_per_second': 0.0,
            'average_latency': 0.0,
            'subscription_count': 0,
            'broadcast_count': 0
        }
        
        # Background tasks
        self._running = False
        self._background_tasks = []
        
        logger.info("WebSocket Connection Manager initialized")
    
    async def start(self):
        """Start the WebSocket manager and background tasks"""
        try:
            self._running = True
            
            # Start background tasks
            self._background_tasks = [
                asyncio.create_task(self._connection_monitor()),
                asyncio.create_task(self._subscription_monitor()),
                asyncio.create_task(self._performance_monitor()),
                asyncio.create_task(self._system_status_broadcaster())
            ]
            
            logger.info("WebSocket Connection Manager started")
            
        except Exception as e:
            logger.error(f"Error starting WebSocket manager: {e}")
            raise
    
    async def stop(self):
        """Stop the WebSocket manager and cleanup"""
        try:
            self._running = False
            
            # Disconnect all connections
            for connection in list(self.active_connections.values()):
                await self._disconnect_client(connection.connection_id, "Server shutdown")
            
            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()
            
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            logger.info("WebSocket Connection Manager stopped")
            
        except Exception as e:
            logger.error(f"Error stopping WebSocket manager: {e}")
    
    async def connect_client(
        self,
        websocket: WebSocket,
        auth_token: Optional[str] = None
    ) -> str:
        """
        Connect a new WebSocket client with authentication.
        
        Args:
            websocket: WebSocket connection
            auth_token: Optional authentication token
            
        Returns:
            Connection ID
        """
        try:
            # Accept WebSocket connection
            await websocket.accept()
            
            # Authenticate user
            user_info = await self._authenticate_websocket(auth_token)
            if not user_info:
                await websocket.close(code=4001, reason="Authentication failed")
                raise HTTPException(status_code=401, detail="Authentication failed")
            
            # Create connection
            connection_id = str(uuid.uuid4())
            connection = WebSocketConnection(
                connection_id=connection_id,
                websocket=websocket,
                user_id=user_info['user_id'],
                user_role=user_info['role']
            )
            
            self.active_connections[connection_id] = connection
            
            # Update metrics
            self.metrics['total_connections'] += 1
            self.metrics['active_connections'] = len(self.active_connections)
            
            # Send welcome message
            await self._send_to_connection(connection_id, {
                'type': 'connection_established',
                'data': {
                    'connection_id': connection_id,
                    'user_id': user_info['user_id'],
                    'server_time': datetime.utcnow().isoformat(),
                    'features': ['real_time_updates', 'task_monitoring', 'agent_status']
                }
            })
            
            logger.info(f"WebSocket client connected: {connection_id} (user: {user_info['user_id']})")
            
            return connection_id
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket client: {e}")
            raise
    
    async def disconnect_client(
        self,
        connection_id: str,
        reason: str = "Client disconnect"
    ):
        """Disconnect a WebSocket client"""
        await self._disconnect_client(connection_id, reason)
    
    async def _disconnect_client(
        self,
        connection_id: str,
        reason: str
    ):
        """Internal method to disconnect client"""
        try:
            if connection_id not in self.active_connections:
                return
            
            connection = self.active_connections[connection_id]
            
            # Close WebSocket
            try:
                await connection.websocket.close(code=1000, reason=reason)
            except Exception:
                pass  # Connection might already be closed
            
            # Remove subscriptions
            connection_subscriptions = list(connection.subscriptions)
            for sub_id in connection_subscriptions:
                await self._remove_subscription(sub_id)
            
            # Remove connection
            del self.active_connections[connection_id]
            
            # Update metrics
            self.metrics['active_connections'] = len(self.active_connections)
            
            logger.info(f"WebSocket client disconnected: {connection_id} ({reason})")
            
        except Exception as e:
            logger.error(f"Error disconnecting client {connection_id}: {e}")
    
    async def handle_message(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ):
        """
        Handle incoming message from WebSocket client.
        
        Args:
            connection_id: Connection ID
            message: Message from client
        """
        try:
            if connection_id not in self.active_connections:
                logger.warning(f"Message from unknown connection: {connection_id}")
                return
            
            connection = self.active_connections[connection_id]
            connection.messages_received += 1
            connection.last_heartbeat = datetime.utcnow()
            
            message_type = message.get('type', 'unknown')
            message_data = message.get('data', {})
            
            logger.debug(f"WebSocket message received: {message_type} from {connection_id}")
            
            # Route message to appropriate handler
            handler = self.message_handlers.get(message_type)
            if handler:
                try:
                    response = await handler(connection_id, message_data)
                    if response:
                        await self._send_to_connection(connection_id, response)
                except Exception as e:
                    logger.error(f"Error in message handler {message_type}: {e}")
                    await self._send_error_to_connection(connection_id, f"Handler error: {str(e)}")
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self._send_error_to_connection(connection_id, f"Unknown message type: {message_type}")
            
            # Update metrics
            self.metrics['total_messages'] += 1
            
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def _authenticate_websocket(self, auth_token: Optional[str]) -> Optional[Dict[str, Any]]:
        """Authenticate WebSocket connection"""
        try:
            if not auth_token:
                # Try to get token from query parameters or headers
                return None
            
            # Decode JWT token (simplified - use same logic as REST API)
            try:
                from api.enhanced_main import SECRET_KEY, ALGORITHM
                payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
                
                return {
                    'user_id': payload.get('user_id', 'unknown'),
                    'username': payload.get('sub', 'unknown'),
                    'role': payload.get('role', 'user')
                }
            except jwt.PyJWTError:
                return None
            
        except Exception as e:
            logger.error(f"Error authenticating WebSocket: {e}")
            return None
    
    async def _send_to_connection(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ):
        """Send message to specific connection"""
        try:
            if connection_id not in self.active_connections:
                return
            
            connection = self.active_connections[connection_id]
            
            # Add timestamp if not present
            if 'timestamp' not in message:
                message['timestamp'] = datetime.utcnow().isoformat()
            
            await connection.websocket.send_text(json.dumps(message))
            connection.messages_sent += 1
            
        except WebSocketDisconnect:
            await self._disconnect_client(connection_id, "WebSocket disconnect")
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            await self._disconnect_client(connection_id, f"Send error: {str(e)}")
    
    async def _send_error_to_connection(
        self,
        connection_id: str,
        error_message: str
    ):
        """Send error message to connection"""
        await self._send_to_connection(connection_id, {
            'type': 'error',
            'data': {
                'error': error_message,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
    
    async def broadcast_to_all(
        self,
        message: Dict[str, Any],
        role_filter: Optional[str] = None
    ):
        """Broadcast message to all active connections"""
        try:
            broadcast_tasks = []
            
            for connection in self.active_connections.values():
                # Apply role filter if specified
                if role_filter and connection.user_role != role_filter:
                    continue
                
                broadcast_tasks.append(
                    self._send_to_connection(connection.connection_id, message)
                )
            
            if broadcast_tasks:
                await asyncio.gather(*broadcast_tasks, return_exceptions=True)
                self.metrics['broadcast_count'] += 1
                
                logger.debug(f"Broadcast sent to {len(broadcast_tasks)} connections")
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
    
    async def broadcast_to_subscribers(
        self,
        subscription_type: str,
        message: Dict[str, Any]
    ):
        """Broadcast message to subscribers of specific type"""
        try:
            if subscription_type not in self.subscription_index:
                return
            
            connection_ids = self.subscription_index[subscription_type]
            broadcast_tasks = []
            
            for connection_id in connection_ids:
                if connection_id in self.active_connections:
                    broadcast_tasks.append(
                        self._send_to_connection(connection_id, message)
                    )
            
            if broadcast_tasks:
                await asyncio.gather(*broadcast_tasks, return_exceptions=True)
                logger.debug(f"Broadcast sent to {len(broadcast_tasks)} subscribers of {subscription_type}")
            
        except Exception as e:
            logger.error(f"Error broadcasting to subscribers: {e}")
    
    # Message handlers
    async def _handle_get_system_status(
        self,
        connection_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle system status request"""
        try:
            if self.amas_system:
                status = await self.amas_system.get_system_status()
                return {
                    'type': 'system_status',
                    'data': status
                }
            else:
                return {
                    'type': 'system_status',
                    'data': {
                        'status': 'unavailable',
                        'error': 'AMAS system not available'
                    }
                }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'type': 'error',
                'data': {'error': str(e)}
            }
    
    async def _handle_get_all_agents(
        self,
        connection_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle request for all agent statuses"""
        try:
            if self.amas_system:
                agents = []
                for agent_id, agent in self.amas_system.agents.items():
                    agent_status = await agent.get_status()
                    agents.append({
                        'agent_id': agent_id,
                        'name': agent_status.get('name', ''),
                        'status': agent_status.get('status', 'unknown'),
                        'current_task': agent_status.get('current_task', ''),
                        'last_activity': agent_status.get('last_activity', ''),
                        'metrics': agent_status.get('metrics', {})
                    })
                
                return {
                    'type': 'all_agents',
                    'data': {'agents': agents}
                }
            else:
                return {
                    'type': 'all_agents',
                    'data': {'agents': []}
                }
        except Exception as e:
            logger.error(f"Error getting all agents: {e}")
            return {
                'type': 'error',
                'data': {'error': str(e)}
            }
    
    async def _handle_get_active_tasks(
        self,
        connection_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle request for active tasks"""
        try:
            if self.amas_system:
                tasks = []
                for task_id, task in self.amas_system.orchestrator.active_tasks.items():
                    task_status = await self.amas_system.orchestrator.get_task_status(task_id)
                    if task_status:
                        tasks.append(task_status)
                
                return {
                    'type': 'active_tasks',
                    'data': {'tasks': tasks}
                }
            else:
                return {
                    'type': 'active_tasks',
                    'data': {'tasks': []}
                }
        except Exception as e:
            logger.error(f"Error getting active tasks: {e}")
            return {
                'type': 'error',
                'data': {'error': str(e)}
            }
    
    async def _handle_subscribe_task(
        self,
        connection_id: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle task subscription request"""
        try:
            task_id = data.get('task_id')
            if not task_id:
                return {
                    'type': 'error',
                    'data': {'error': 'task_id required for subscription'}
                }
            
            # Create subscription
            subscription_id = await self._create_subscription(
                connection_id=connection_id,
                subscription_type='task_updates',
                filters={'task_id': task_id}
            )
            
            if subscription_id:
                return {
                    'type': 'subscription_created',
                    'data': {
                        'subscription_id': subscription_id,
                        'subscription_type': 'task_updates',
                        'task_id': task_id
                    }
                }
            else:
                return {
                    'type': 'error',
                    'data': {'error': 'Failed to create subscription'}
                }
                
        except Exception as e:
            logger.error(f"Error handling task subscription: {e}")
            return {
                'type': 'error',
                'data': {'error': str(e)}
            }
    
    async def _handle_subscribe_agent(
        self,
        connection_id: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle agent subscription request"""
        try:
            agent_id = data.get('agent_id')
            if not agent_id:
                return {
                    'type': 'error',
                    'data': {'error': 'agent_id required for subscription'}
                }
            
            # Create subscription
            subscription_id = await self._create_subscription(
                connection_id=connection_id,
                subscription_type='agent_updates',
                filters={'agent_id': agent_id}
            )
            
            if subscription_id:
                return {
                    'type': 'subscription_created',
                    'data': {
                        'subscription_id': subscription_id,
                        'subscription_type': 'agent_updates',
                        'agent_id': agent_id
                    }
                }
            else:
                return {
                    'type': 'error',
                    'data': {'error': 'Failed to create subscription'}
                }
                
        except Exception as e:
            logger.error(f"Error handling agent subscription: {e}")
            return {
                'type': 'error',
                'data': {'error': str(e)}
            }
    
    async def _handle_heartbeat(
        self,
        connection_id: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle heartbeat from client"""
        try:
            if connection_id in self.active_connections:
                connection = self.active_connections[connection_id]
                connection.last_heartbeat = datetime.utcnow()
                
                return {
                    'type': 'heartbeat_ack',
                    'data': {
                        'server_time': datetime.utcnow().isoformat(),
                        'connection_id': connection_id
                    }
                }
            
        except Exception as e:
            logger.error(f"Error handling heartbeat: {e}")
            return None
    
    async def _handle_ping(
        self,
        connection_id: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle ping for latency measurement"""
        try:
            client_timestamp = data.get('timestamp', time.time() * 1000)
            
            return {
                'type': 'pong',
                'data': {
                    'client_timestamp': client_timestamp,
                    'server_timestamp': time.time() * 1000
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling ping: {e}")
            return None
    
    async def _create_subscription(
        self,
        connection_id: str,
        subscription_type: str,
        filters: Dict[str, Any]
    ) -> Optional[str]:
        """Create a new subscription"""
        try:
            if connection_id not in self.active_connections:
                return None
            
            subscription_id = str(uuid.uuid4())
            subscription = Subscription(
                subscription_id=subscription_id,
                connection_id=connection_id,
                subscription_type=subscription_type,
                filters=filters
            )
            
            self.subscriptions[subscription_id] = subscription
            
            # Add to subscription index
            if subscription_type not in self.subscription_index:
                self.subscription_index[subscription_type] = set()
            self.subscription_index[subscription_type].add(connection_id)
            
            # Add to connection subscriptions
            connection = self.active_connections[connection_id]
            connection.subscriptions.add(subscription_id)
            
            # Update metrics
            self.metrics['subscription_count'] = len(self.subscriptions)
            
            logger.info(f"Subscription created: {subscription_id} ({subscription_type})")
            
            return subscription_id
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return None
    
    async def _remove_subscription(self, subscription_id: str):
        """Remove a subscription"""
        try:
            if subscription_id not in self.subscriptions:
                return
            
            subscription = self.subscriptions[subscription_id]
            
            # Remove from subscription index
            if subscription.subscription_type in self.subscription_index:
                self.subscription_index[subscription.subscription_type].discard(subscription.connection_id)
            
            # Remove from connection subscriptions
            if subscription.connection_id in self.active_connections:
                connection = self.active_connections[subscription.connection_id]
                connection.subscriptions.discard(subscription_id)
            
            # Remove subscription
            del self.subscriptions[subscription_id]
            
            # Update metrics
            self.metrics['subscription_count'] = len(self.subscriptions)
            
            logger.info(f"Subscription removed: {subscription_id}")
            
        except Exception as e:
            logger.error(f"Error removing subscription: {e}")
    
    # Background monitoring tasks
    async def _connection_monitor(self):
        """Monitor connection health and cleanup inactive connections"""
        while self._running:
            try:
                current_time = datetime.utcnow()
                inactive_connections = []
                
                for connection_id, connection in self.active_connections.items():
                    # Check for inactive connections (no heartbeat for 5 minutes)
                    if current_time - connection.last_heartbeat > timedelta(minutes=5):
                        inactive_connections.append(connection_id)
                
                # Disconnect inactive connections
                for connection_id in inactive_connections:
                    await self._disconnect_client(connection_id, "Inactive connection timeout")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in connection monitor: {e}")
                await asyncio.sleep(60)
    
    async def _subscription_monitor(self):
        """Monitor subscriptions and send updates"""
        while self._running:
            try:
                # This would integrate with the AMAS system to get real-time updates
                # For now, we'll simulate periodic updates
                
                if self.amas_system:
                    # System status updates
                    if 'system_status' in self.subscription_index:
                        status = await self.amas_system.get_system_status()
                        await self.broadcast_to_subscribers('system_status', {
                            'type': 'system_status',
                            'data': status
                        })
                    
                    # Agent status updates
                    if 'agent_updates' in self.subscription_index:
                        for agent_id, agent in self.amas_system.agents.items():
                            agent_status = await agent.get_status()
                            await self.broadcast_to_subscribers('agent_updates', {
                                'type': 'agent_status',
                                'data': {
                                    'agent_id': agent_id,
                                    **agent_status
                                }
                            })
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in subscription monitor: {e}")
                await asyncio.sleep(60)
    
    async def _performance_monitor(self):
        """Monitor WebSocket performance metrics"""
        while self._running:
            try:
                # Calculate messages per second
                current_time = time.time()
                if hasattr(self, '_last_metric_time'):
                    time_diff = current_time - self._last_metric_time
                    message_diff = self.metrics['total_messages'] - getattr(self, '_last_message_count', 0)
                    
                    if time_diff > 0:
                        self.metrics['messages_per_second'] = message_diff / time_diff
                
                self._last_metric_time = current_time
                self._last_message_count = self.metrics['total_messages']
                
                # Log performance metrics
                logger.info(f"WebSocket Performance: {self.metrics['active_connections']} connections, "
                          f"{self.metrics['messages_per_second']:.2f} msg/sec, "
                          f"{self.metrics['subscription_count']} subscriptions")
                
                await asyncio.sleep(300)  # Report every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(300)
    
    async def _system_status_broadcaster(self):
        """Broadcast system status updates periodically"""
        while self._running:
            try:
                if self.amas_system and 'system_status' in self.subscription_index:
                    status = await self.amas_system.get_system_status()
                    
                    await self.broadcast_to_subscribers('system_status', {
                        'type': 'system_status',
                        'data': status
                    })
                
                await asyncio.sleep(30)  # Broadcast every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in system status broadcaster: {e}")
                await asyncio.sleep(60)
    
    def get_manager_status(self) -> Dict[str, Any]:
        """Get WebSocket manager status"""
        return {
            'manager_status': 'active' if self._running else 'inactive',
            'active_connections': len(self.active_connections),
            'total_subscriptions': len(self.subscriptions),
            'subscription_types': list(self.subscription_index.keys()),
            'metrics': self.metrics,
            'connection_details': [
                {
                    'connection_id': conn.connection_id,
                    'user_id': conn.user_id,
                    'connected_at': conn.connected_at.isoformat(),
                    'messages_sent': conn.messages_sent,
                    'messages_received': conn.messages_received,
                    'subscriptions': len(conn.subscriptions)
                }
                for conn in self.active_connections.values()
            ],
            'timestamp': datetime.utcnow().isoformat()
        }


# Global WebSocket manager instance
websocket_manager = WebSocketConnectionManager()