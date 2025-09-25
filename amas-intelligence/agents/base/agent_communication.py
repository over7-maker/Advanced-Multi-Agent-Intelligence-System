"""
Agent Communication Module

This module handles communication between intelligence agents in the AMAS system.
It provides message passing, event broadcasting, and coordination mechanisms.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import uuid


class MessageType(Enum):
    """Message types for agent communication"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    DATA_SHARE = "data_share"
    STATUS_UPDATE = "status_update"
    COORDINATION = "coordination"
    EVENT = "event"


class AgentCommunication:
    """
    Handles communication between intelligence agents.
    
    This class provides message passing, event broadcasting, and coordination
    mechanisms for the AMAS intelligence system.
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize agent communication.
        
        Args:
            agent_id: Unique identifier for this agent
        """
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"amas.communication.{agent_id}")
        
        # Message queues
        self.incoming_messages = asyncio.Queue()
        self.outgoing_messages = asyncio.Queue()
        
        # Event handlers
        self.event_handlers = {}
        
        # Message history
        self.message_history = []
        
        # Communication status
        self.is_connected = False
        self.connected_agents = set()
    
    async def connect(self, communication_bus: Any = None) -> bool:
        """
        Connect to the communication system.
        
        Args:
            communication_bus: External communication bus (e.g., Redis, RabbitMQ)
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting agent {self.agent_id} to communication system")
            
            # Initialize communication bus if not provided
            if communication_bus is None:
                # Use simple in-memory communication for now
                self.communication_bus = InMemoryCommunicationBus()
            else:
                self.communication_bus = communication_bus
            
            # Connect to bus
            await self.communication_bus.connect(self.agent_id)
            self.is_connected = True
            
            # Start message processing
            asyncio.create_task(self._process_incoming_messages())
            asyncio.create_task(self._process_outgoing_messages())
            
            self.logger.info(f"Agent {self.agent_id} connected successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect agent {self.agent_id}: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the communication system.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            self.logger.info(f"Disconnecting agent {self.agent_id}")
            
            if self.communication_bus:
                await self.communication_bus.disconnect(self.agent_id)
            
            self.is_connected = False
            self.connected_agents.clear()
            
            self.logger.info(f"Agent {self.agent_id} disconnected successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect agent {self.agent_id}: {e}")
            return False
    
    async def send_message(
        self,
        target_agent: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: int = 1
    ) -> bool:
        """
        Send a message to another agent.
        
        Args:
            target_agent: Target agent ID
            message_type: Type of message
            content: Message content
            priority: Message priority (1-10, higher is more important)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            message = {
                'id': str(uuid.uuid4()),
                'from_agent': self.agent_id,
                'to_agent': target_agent,
                'type': message_type.value,
                'content': content,
                'priority': priority,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if self.communication_bus:
                await self.communication_bus.send_message(message)
            
            # Add to outgoing queue
            await self.outgoing_messages.put(message)
            
            self.logger.debug(f"Sent message {message['id']} to {target_agent}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message to {target_agent}: {e}")
            return False
    
    async def broadcast_message(
        self,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: int = 1
    ) -> bool:
        """
        Broadcast a message to all connected agents.
        
        Args:
            message_type: Type of message
            content: Message content
            priority: Message priority (1-10, higher is more important)
            
        Returns:
            True if message broadcast successfully, False otherwise
        """
        try:
            message = {
                'id': str(uuid.uuid4()),
                'from_agent': self.agent_id,
                'to_agent': 'broadcast',
                'type': message_type.value,
                'content': content,
                'priority': priority,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if self.communication_bus:
                await self.communication_bus.broadcast_message(message)
            
            # Add to outgoing queue
            await self.outgoing_messages.put(message)
            
            self.logger.debug(f"Broadcasted message {message['id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to broadcast message: {e}")
            return False
    
    async def receive_message(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Receive a message from the communication system.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Received message or None if timeout
        """
        try:
            message = await asyncio.wait_for(
                self.incoming_messages.get(),
                timeout=timeout
            )
            
            # Add to message history
            self.message_history.append(message)
            
            self.logger.debug(f"Received message {message.get('id', 'unknown')}")
            return message
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return None
    
    async def register_event_handler(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> bool:
        """
        Register an event handler for specific event types.
        
        Args:
            event_type: Type of event to handle
            handler: Handler function
            
        Returns:
            True if handler registered successfully, False otherwise
        """
        try:
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            
            self.event_handlers[event_type].append(handler)
            
            self.logger.debug(f"Registered event handler for {event_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register event handler for {event_type}: {e}")
            return False
    
    async def unregister_event_handler(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> bool:
        """
        Unregister an event handler.
        
        Args:
            event_type: Type of event
            handler: Handler function to remove
            
        Returns:
            True if handler unregistered successfully, False otherwise
        """
        try:
            if event_type in self.event_handlers:
                if handler in self.event_handlers[event_type]:
                    self.event_handlers[event_type].remove(handler)
                    
                    if not self.event_handlers[event_type]:
                        del self.event_handlers[event_type]
            
            self.logger.debug(f"Unregistered event handler for {event_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister event handler for {event_type}: {e}")
            return False
    
    async def get_connected_agents(self) -> List[str]:
        """
        Get list of connected agents.
        
        Returns:
            List of connected agent IDs
        """
        if self.communication_bus:
            return await self.communication_bus.get_connected_agents()
        else:
            return list(self.connected_agents)
    
    async def get_message_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get message history.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of recent messages
        """
        return self.message_history[-limit:] if self.message_history else []
    
    async def _process_incoming_messages(self):
        """Process incoming messages from the communication bus."""
        while self.is_connected:
            try:
                if self.communication_bus:
                    message = await self.communication_bus.receive_message(self.agent_id)
                    if message:
                        await self.incoming_messages.put(message)
                        
                        # Handle event handlers
                        await self._handle_event_handlers(message)
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Error processing incoming messages: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_outgoing_messages(self):
        """Process outgoing messages to the communication bus."""
        while self.is_connected:
            try:
                if not self.outgoing_messages.empty():
                    message = await self.outgoing_messages.get()
                    
                    if self.communication_bus:
                        if message['to_agent'] == 'broadcast':
                            await self.communication_bus.broadcast_message(message)
                        else:
                            await self.communication_bus.send_message(message)
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Error processing outgoing messages: {e}")
                await asyncio.sleep(1.0)
    
    async def _handle_event_handlers(self, message: Dict[str, Any]):
        """Handle event handlers for received messages."""
        try:
            message_type = message.get('type')
            if message_type in self.event_handlers:
                for handler in self.event_handlers[message_type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        self.logger.error(f"Error in event handler: {e}")
        except Exception as e:
            self.logger.error(f"Error handling event handlers: {e}")


class InMemoryCommunicationBus:
    """
    Simple in-memory communication bus for testing and development.
    
    This is a basic implementation that doesn't persist messages
    and is only suitable for single-process scenarios.
    """
    
    def __init__(self):
        self.agents = {}
        self.message_queues = {}
        self.broadcast_queue = asyncio.Queue()
    
    async def connect(self, agent_id: str) -> bool:
        """Connect an agent to the communication bus."""
        try:
            self.agents[agent_id] = {
                'connected': True,
                'connected_at': datetime.utcnow()
            }
            self.message_queues[agent_id] = asyncio.Queue()
            return True
        except Exception:
            return False
    
    async def disconnect(self, agent_id: str) -> bool:
        """Disconnect an agent from the communication bus."""
        try:
            if agent_id in self.agents:
                self.agents[agent_id]['connected'] = False
            if agent_id in self.message_queues:
                del self.message_queues[agent_id]
            return True
        except Exception:
            return False
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send a message to a specific agent."""
        try:
            target_agent = message.get('to_agent')
            if target_agent in self.message_queues:
                await self.message_queues[target_agent].put(message)
                return True
            return False
        except Exception:
            return False
    
    async def broadcast_message(self, message: Dict[str, Any]) -> bool:
        """Broadcast a message to all connected agents."""
        try:
            for agent_id in self.message_queues:
                if agent_id != message.get('from_agent'):
                    await self.message_queues[agent_id].put(message)
            return True
        except Exception:
            return False
    
    async def receive_message(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Receive a message for a specific agent."""
        try:
            if agent_id in self.message_queues:
                return await self.message_queues[agent_id].get()
            return None
        except Exception:
            return None
    
    async def get_connected_agents(self) -> List[str]:
        """Get list of connected agents."""
        return [
            agent_id for agent_id, info in self.agents.items()
            if info.get('connected', False)
        ]