"""
WebSocket connection manager for real-time updates
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Set

from fastapi import Query, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager for real-time updates
    
    Features:
    • Connection lifecycle management
    • Broadcast to all clients
    • Targeted messaging by user/task
    • Automatic reconnection handling
    • Message queuing for offline clients
    """
    
    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Connections grouped by user ID
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Connections subscribed to specific tasks
        self.task_subscribers: Dict[str, Set[str]] = {}
        
        # Message queue for offline clients (in-memory, can move to Redis)
        self.message_queue: Dict[str, List[Dict]] = {}
        
        logger.info("WebSocket connection manager initialized")
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str = None):
        """Accept and register new WebSocket connection"""
        await websocket.accept()
        
        self.active_connections[connection_id] = websocket
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id} (user: {user_id})")
        
        # Send queued messages if any
        if connection_id in self.message_queue:
            for message in self.message_queue[connection_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send queued message: {e}")
            del self.message_queue[connection_id]
    
    def disconnect(self, connection_id: str):
        """Remove connection from manager"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from user connections
        for user_id, conn_ids in self.user_connections.items():
            if connection_id in conn_ids:
                conn_ids.remove(connection_id)
                break
        
        # Remove from task subscribers
        for task_id, conn_ids in self.task_subscribers.items():
            if connection_id in conn_ids:
                conn_ids.remove(connection_id)
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def broadcast(self, message: Dict):
        """
        Broadcast message to all connected clients
        
        Message format:
        {
            "event": "task_created" | "task_progress" | "agent_update" | ...,
            "data": { ... event-specific data ... },
            "timestamp": "2025-01-19T05:34:00Z"
        }
        """
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        disconnected = []
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"Broadcast failed to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected clients
        for connection_id in disconnected:
            self.disconnect(connection_id)
        
        logger.debug(f"Broadcast to {len(self.active_connections)} clients: {message.get('event', 'unknown')}")
    
    async def send_to_user(self, user_id: str, message: Dict):
        """Send message to all connections for specific user"""
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        if user_id not in self.user_connections:
            logger.warning(f"No connections found for user {user_id}")
            return
        
        connection_ids = list(self.user_connections[user_id])
        
        for connection_id in connection_ids:
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_json(message)
                except Exception as e:
                    logger.error(f"Send to user failed: {e}")
                    self.disconnect(connection_id)
    
    async def send_to_task_subscribers(self, task_id: str, message: Dict):
        """Send message to all clients subscribed to specific task"""
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        if task_id not in self.task_subscribers:
            return
        
        connection_ids = list(self.task_subscribers[task_id])
        
        for connection_id in connection_ids:
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_json(message)
                except Exception as e:
                    logger.error(f"Send to task subscribers failed: {e}")
                    self.disconnect(connection_id)
    
    def subscribe_to_task(self, connection_id: str, task_id: str):
        """Subscribe connection to task updates"""
        if task_id not in self.task_subscribers:
            self.task_subscribers[task_id] = set()
        
        self.task_subscribers[task_id].add(connection_id)
        logger.info(f"Connection {connection_id} subscribed to task {task_id}")
    
    def unsubscribe_from_task(self, connection_id: str, task_id: str):
        """Unsubscribe connection from task updates"""
        if task_id in self.task_subscribers:
            self.task_subscribers[task_id].discard(connection_id)
            logger.info(f"Connection {connection_id} unsubscribed from task {task_id}")
    
    async def heartbeat(self):
        """Send periodic heartbeat to keep connections alive"""
        while True:
            await asyncio.sleep(30)  # Every 30 seconds
            
            message = {
                "event": "heartbeat",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.broadcast(message)


# Global instance
websocket_manager = ConnectionManager()


async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None),  # JWT token for authentication (optional for now)
):
    """
    WebSocket endpoint for real-time updates
    
    Client connection:
    ws://your-domain/ws?token=<JWT_TOKEN>
    
    Events sent to client:
    • task_created - New task created
    • task_progress - Task execution progress
    • task_completed - Task finished
    • task_failed - Task error
    • agent_update - Agent status change
    • system_alert - System notifications
    • heartbeat - Keep-alive ping
    """
    
    # Generate connection ID
    connection_id = f"ws_{uuid.uuid4().hex[:8]}"
    user_id = None
    
    try:
        # Authenticate user from token (if provided)
        if token:
            try:
                # TODO: Implement JWT verification
                # from src.api.auth import verify_jwt_token
                # user = await verify_jwt_token(token)
                # user_id = user.id
                pass
            except Exception as e:
                logger.error(f"WebSocket authentication failed: {e}")
                await websocket.close(code=1008, reason="Authentication failed")
                return
        
        # Connect
        await websocket_manager.connect(websocket, connection_id, user_id)
        
        # Send welcome message
        await websocket.send_json({
            "event": "connected",
            "connection_id": connection_id,
            "message": "WebSocket connection established"
        })
        
        # Listen for client messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                
                # Handle client commands
                if data.get("command") == "subscribe_task":
                    task_id = data.get("task_id")
                    if task_id:
                        websocket_manager.subscribe_to_task(connection_id, task_id)
                        await websocket.send_json({
                            "event": "subscribed",
                            "task_id": task_id
                        })
                
                elif data.get("command") == "unsubscribe_task":
                    task_id = data.get("task_id")
                    if task_id:
                        websocket_manager.unsubscribe_from_task(connection_id, task_id)
                        await websocket.send_json({
                            "event": "unsubscribed",
                            "task_id": task_id
                        })
                
                elif data.get("command") == "ping":
                    await websocket.send_json({
                        "event": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {connection_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    
    finally:
        websocket_manager.disconnect(connection_id)


# Start heartbeat task on startup
async def start_websocket_heartbeat():
    """Start WebSocket heartbeat task"""
    asyncio.create_task(websocket_manager.heartbeat())

