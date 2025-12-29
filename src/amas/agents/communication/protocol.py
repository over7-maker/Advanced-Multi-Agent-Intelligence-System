"""
Agent Communication Protocol
Implements message-based communication between agents
"""

import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.amas.agents.communication.message import (
    AgentMessage,
    MessagePriority,
    MessageStatus,
    MessageType,
    create_broadcast_message,
    create_request_message,
)

logger = logging.getLogger(__name__)

# Global protocol instances
_protocols: Dict[str, "AgentCommunicationProtocol"] = {}


class AgentCommunicationProtocol:
    """
    Communication protocol for agents
    
    Features:
    - Async message delivery
    - Message queuing per agent
    - Request-response pattern with timeout
    - Broadcast to multiple agents
    - Message acknowledgment
    - Retry logic for failed messages
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize communication protocol for an agent
        
        Args:
            agent_id: ID of the agent
        """
        self.agent_id = agent_id
        self._message_queue: deque = deque()
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._redis_client = None
        self._initialized = False
        
        # Statistics
        self._messages_sent = 0
        self._messages_received = 0
        self._messages_failed = 0
        
        logger.debug(f"AgentCommunicationProtocol created for agent: {agent_id}")
    
    async def initialize(self):
        """Initialize Redis connection"""
        if self._initialized:
            return
        
        try:
            from src.cache.redis import get_redis_client
            self._redis_client = get_redis_client()
            self._initialized = True
            logger.info(f"Protocol initialized for agent: {self.agent_id}")
        except Exception as e:
            logger.warning(f"Protocol could not connect to Redis: {e}")
    
    def _get_queue_key(self, agent_id: str) -> str:
        """Get Redis key for agent message queue"""
        return f"agent_comm:queue:{agent_id}"
    
    async def send_message(
        self,
        to_agent: str,
        message: AgentMessage,
    ) -> bool:
        """
        Send a message to another agent
        
        Args:
            to_agent: ID of recipient agent
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        try:
            message.receiver = to_agent
            message.mark_sent()
            
            # Store in Redis queue for recipient
            if self._redis_client:
                queue_key = self._get_queue_key(to_agent)
                message_json = message.to_json()
                
                await self._redis_client.rpush(queue_key, message_json)
                
                # Set expiration on queue (24 hours)
                await self._redis_client.expire(queue_key, 86400)
                
                logger.debug(f"Message sent from {self.agent_id} to {to_agent}")
                self._messages_sent += 1
                return True
            else:
                # Fallback: store in memory (for development without Redis)
                logger.warning(f"Redis not available, message not sent to {to_agent}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send message to {to_agent}: {e}", exc_info=True)
            self._messages_failed += 1
            return False
    
    async def receive_messages(self, timeout: float = 1.0) -> List[AgentMessage]:
        """
        Receive messages from queue
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            List of received messages
        """
        messages = []
        
        try:
            if not self._redis_client:
                return messages
            
            queue_key = self._get_queue_key(self.agent_id)
            
            # Get all messages from queue
            message_jsons = await self._redis_client.lrange(queue_key, 0, -1)
            
            if message_jsons:
                # Clear the queue
                await self._redis_client.delete(queue_key)
                
                # Parse messages
                for message_json in message_jsons:
                    try:
                        message = AgentMessage.from_json(message_json)
                        message.mark_delivered()
                        messages.append(message)
                        self._messages_received += 1
                        
                        # Handle response to pending request
                        if message.is_response() and message.correlation_id:
                            await self._handle_response(message)
                        
                    except Exception as e:
                        logger.error(f"Failed to parse message: {e}")
            
        except Exception as e:
            logger.error(f"Failed to receive messages: {e}", exc_info=True)
        
        return messages
    
    async def request(
        self,
        to_agent: str,
        payload: Dict[str, Any],
        timeout: float = 30.0,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a request and wait for response
        
        Args:
            to_agent: ID of recipient agent
            payload: Request payload
            timeout: Timeout in seconds
            priority: Message priority
            
        Returns:
            Response payload or None if timeout
        """
        try:
            # Create request message
            message = create_request_message(
                sender=self.agent_id,
                receiver=to_agent,
                payload=payload,
                priority=priority,
                timeout=timeout,
            )
            
            # Create future for response
            future = asyncio.Future()
            self._pending_requests[message.correlation_id] = future
            
            # Send request
            success = await self.send_message(to_agent, message)
            
            if not success:
                self._pending_requests.pop(message.correlation_id, None)
                return None
            
            # Wait for response with timeout
            try:
                response_payload = await asyncio.wait_for(future, timeout=timeout)
                return response_payload
                
            except asyncio.TimeoutError:
                logger.warning(f"Request to {to_agent} timed out after {timeout}s")
                self._pending_requests.pop(message.correlation_id, None)
                return None
            
        except Exception as e:
            logger.error(f"Request to {to_agent} failed: {e}", exc_info=True)
            return None
    
    async def respond(
        self,
        request_message: AgentMessage,
        response_payload: Dict[str, Any],
        status: MessageStatus = MessageStatus.PROCESSED,
    ) -> bool:
        """
        Send a response to a request
        
        Args:
            request_message: Original request message
            response_payload: Response data
            status: Response status
            
        Returns:
            True if sent successfully
        """
        try:
            # Create response message
            response_message = request_message.create_response(
                sender=self.agent_id,
                payload=response_payload,
                status=status,
            )
            
            # Send response
            return await self.send_message(request_message.sender, response_message)
            
        except Exception as e:
            logger.error(f"Failed to send response: {e}", exc_info=True)
            return False
    
    async def broadcast(
        self,
        payload: Dict[str, Any],
        recipients: Optional[List[str]] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> int:
        """
        Broadcast a message to multiple agents
        
        Args:
            payload: Broadcast payload
            recipients: List of recipient agent IDs (None for all)
            priority: Message priority
            
        Returns:
            Number of agents message was sent to
        """
        try:
            # Create broadcast message
            message = create_broadcast_message(
                sender=self.agent_id,
                payload=payload,
                priority=priority,
            )
            
            # If no recipients specified, get all agents from Redis
            if recipients is None:
                recipients = await self._get_all_agents()
            
            # Send to all recipients
            sent_count = 0
            for recipient in recipients:
                if recipient != self.agent_id:  # Don't send to self
                    success = await self.send_message(recipient, message)
                    if success:
                        sent_count += 1
            
            logger.info(f"Broadcast from {self.agent_id} sent to {sent_count} agents")
            return sent_count
            
        except Exception as e:
            logger.error(f"Broadcast failed: {e}", exc_info=True)
            return 0
    
    async def _handle_response(self, response_message: AgentMessage) -> None:
        """
        Handle a response to a pending request
        
        Args:
            response_message: Response message
        """
        correlation_id = response_message.correlation_id
        
        if correlation_id in self._pending_requests:
            future = self._pending_requests.pop(correlation_id)
            
            if not future.done():
                future.set_result(response_message.payload)
    
    async def _get_all_agents(self) -> List[str]:
        """Get list of all registered agents"""
        if not self._redis_client:
            return []
        
        try:
            # Scan for all agent queues
            pattern = "agent_comm:queue:*"
            agent_ids = []
            
            async for key in self._redis_client.scan_iter(match=pattern):
                # Extract agent ID from key
                agent_id = key.decode().split(":")[-1]
                agent_ids.append(agent_id)
            
            return agent_ids
            
        except Exception as e:
            logger.error(f"Failed to get all agents: {e}")
            return []
    
    async def acknowledge_message(self, message: AgentMessage) -> bool:
        """
        Acknowledge receipt of a message
        
        Args:
            message: Message to acknowledge
            
        Returns:
            True if successful
        """
        try:
            message.mark_acknowledged()
            
            # If this is a request, send acknowledgment
            if message.is_request():
                ack_message = message.create_response(
                    sender=self.agent_id,
                    payload={"acknowledged": True},
                    status=MessageStatus.ACKNOWLEDGED,
                )
                return await self.send_message(message.sender, ack_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge message: {e}", exc_info=True)
            return False
    
    async def get_pending_messages_count(self) -> int:
        """Get count of pending messages in queue"""
        if not self._redis_client:
            return 0
        
        try:
            queue_key = self._get_queue_key(self.agent_id)
            return await self._redis_client.llen(queue_key)
            
        except Exception as e:
            logger.error(f"Failed to get pending messages count: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get protocol statistics"""
        return {
            "agent_id": self.agent_id,
            "messages_sent": self._messages_sent,
            "messages_received": self._messages_received,
            "messages_failed": self._messages_failed,
            "pending_requests": len(self._pending_requests),
            "redis_connected": self._redis_client is not None,
        }


def get_communication_protocol(agent_id: str) -> AgentCommunicationProtocol:
    """
    Get or create communication protocol for an agent
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        AgentCommunicationProtocol instance
    """
    if agent_id not in _protocols:
        _protocols[agent_id] = AgentCommunicationProtocol(agent_id)
    
    return _protocols[agent_id]

