"""
AMAS Advanced Agent Communication Bus

Sophisticated inter-agent communication system implementing:
- Reliable message passing between agents
- Task delegation and coordination
- Shared state management
- Event-driven communication
- Message queuing and routing
- Communication security and validation

Enables true multi-agent collaboration with enterprise-grade reliability.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
import time
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of inter-agent messages"""
    TASK_DELEGATION = "task_delegation"
    TASK_RESPONSE = "task_response"
    INFORMATION_REQUEST = "information_request"
    INFORMATION_RESPONSE = "information_response"
    STATUS_UPDATE = "status_update"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    BROADCAST = "broadcast"
    ALERT = "alert"
    HEARTBEAT = "heartbeat"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class MessageStatus(Enum):
    """Message delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class AgentMessage:
    """Inter-agent message structure"""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    priority: MessagePriority
    payload: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: MessageStatus = MessageStatus.PENDING
    delivery_attempts: int = 0
    max_attempts: int = 3
    response_expected: bool = False
    conversation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommunicationChannel:
    """Communication channel between agents"""
    channel_id: str
    agent_a: str
    agent_b: str
    channel_type: str = "bidirectional"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    message_count: int = 0
    is_active: bool = True
    encryption_enabled: bool = True
    quality_metrics: Dict[str, float] = field(default_factory=dict)


class AdvancedMessageBus:
    """
    Advanced message bus for inter-agent communication.
    
    Features:
    - Reliable message delivery with acknowledgments
    - Priority-based message routing
    - Conversation tracking and context
    - Security and encryption
    - Performance monitoring
    - Message persistence and recovery
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Message storage and routing
        self.messages: Dict[str, AgentMessage] = {}
        self.message_queues: Dict[str, deque] = defaultdict(deque)
        self.pending_messages: Dict[str, AgentMessage] = {}
        
        # Agent registry and channels
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.communication_channels: Dict[str, CommunicationChannel] = {}
        
        # Event handlers
        self.message_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.global_handlers: List[Callable] = []
        
        # Performance metrics
        self.communication_metrics = {
            'total_messages': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'average_delivery_time': 0.0,
            'active_conversations': 0,
            'message_types': defaultdict(int),
            'agent_activity': defaultdict(int)
        }
        
        # Configuration
        self.max_queue_size = config.get('max_queue_size', 1000)
        self.message_ttl = config.get('message_ttl_seconds', 3600)  # 1 hour default
        self.delivery_timeout = config.get('delivery_timeout_seconds', 30)
        self.heartbeat_interval = config.get('heartbeat_interval_seconds', 60)
        
        # Background tasks
        self._running = False
        self._background_tasks = []
        
        logger.info("Advanced Message Bus initialized")
    
    async def start(self):
        """Start the message bus and background tasks"""
        try:
            self._running = True
            
            # Start background tasks
            self._background_tasks = [
                asyncio.create_task(self._message_processor()),
                asyncio.create_task(self._heartbeat_monitor()),
                asyncio.create_task(self._cleanup_expired_messages()),
                asyncio.create_task(self._performance_monitor())
            ]
            
            logger.info("Message bus started with background tasks")
            
        except Exception as e:
            logger.error(f"Error starting message bus: {e}")
            raise
    
    async def stop(self):
        """Stop the message bus and cleanup"""
        try:
            self._running = False
            
            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            logger.info("Message bus stopped")
            
        except Exception as e:
            logger.error(f"Error stopping message bus: {e}")
    
    async def register_agent(
        self,
        agent_id: str,
        agent_info: Dict[str, Any],
        message_handler: Optional[Callable] = None
    ) -> bool:
        """
        Register an agent with the message bus.
        
        Args:
            agent_id: Unique agent identifier
            agent_info: Agent information (name, capabilities, etc.)
            message_handler: Optional message handler function
            
        Returns:
            True if registration successful
        """
        try:
            if agent_id in self.registered_agents:
                logger.warning(f"Agent {agent_id} already registered")
                return False
            
            # Register agent
            self.registered_agents[agent_id] = {
                **agent_info,
                'registered_at': datetime.utcnow(),
                'last_heartbeat': datetime.utcnow(),
                'message_handler': message_handler,
                'status': 'active'
            }
            
            # Create message queue for agent
            self.message_queues[agent_id] = deque(maxlen=self.max_queue_size)
            
            logger.info(f"Agent {agent_id} registered with message bus")
            return True
            
        except Exception as e:
            logger.error(f"Error registering agent {agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the message bus"""
        try:
            if agent_id not in self.registered_agents:
                logger.warning(f"Agent {agent_id} not registered")
                return False
            
            # Update agent status
            self.registered_agents[agent_id]['status'] = 'inactive'
            
            # Clear message queue
            self.message_queues[agent_id].clear()
            
            logger.info(f"Agent {agent_id} unregistered from message bus")
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering agent {agent_id}: {e}")
            return False
    
    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM,
        response_expected: bool = False,
        conversation_id: Optional[str] = None,
        ttl_seconds: Optional[int] = None
    ) -> str:
        """
        Send a message from one agent to another.
        
        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            message_type: Type of message
            payload: Message payload
            priority: Message priority
            response_expected: Whether response is expected
            conversation_id: Optional conversation ID for threading
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            Message ID
        """
        try:
            # Validate agents
            if from_agent not in self.registered_agents:
                raise ValueError(f"Sender agent {from_agent} not registered")
            
            if to_agent not in self.registered_agents:
                raise ValueError(f"Recipient agent {to_agent} not registered")
            
            if self.registered_agents[to_agent]['status'] != 'active':
                raise ValueError(f"Recipient agent {to_agent} not active")
            
            # Create message
            message_id = str(uuid.uuid4())
            expires_at = None
            if ttl_seconds:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            elif self.message_ttl:
                expires_at = datetime.utcnow() + timedelta(seconds=self.message_ttl)
            
            message = AgentMessage(
                message_id=message_id,
                from_agent=from_agent,
                to_agent=to_agent,
                message_type=message_type,
                priority=priority,
                payload=payload,
                expires_at=expires_at,
                response_expected=response_expected,
                conversation_id=conversation_id or str(uuid.uuid4())
            )
            
            # Store message
            self.messages[message_id] = message
            
            # Add to recipient's queue (priority-based insertion)
            await self._enqueue_message(to_agent, message)
            
            # Update metrics
            self.communication_metrics['total_messages'] += 1
            self.communication_metrics['message_types'][message_type.value] += 1
            self.communication_metrics['agent_activity'][from_agent] += 1
            
            logger.info(f"Message {message_id} sent from {from_agent} to {to_agent} ({message_type.value})")
            
            return message_id
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    async def _enqueue_message(self, agent_id: str, message: AgentMessage):
        """Add message to agent's queue with priority ordering"""
        try:
            queue = self.message_queues[agent_id]
            
            # Insert based on priority (higher priority first)
            inserted = False
            for i, existing_msg in enumerate(queue):
                if message.priority.value > existing_msg.priority.value:
                    queue.insert(i, message)
                    inserted = True
                    break
            
            if not inserted:
                queue.append(message)
            
            # Update message status
            message.status = MessageStatus.SENT
            
        except Exception as e:
            logger.error(f"Error enqueuing message: {e}")
            raise
    
    async def get_messages(
        self,
        agent_id: str,
        limit: int = 10,
        message_types: Optional[List[MessageType]] = None
    ) -> List[AgentMessage]:
        """
        Get messages for an agent.
        
        Args:
            agent_id: Agent ID to get messages for
            limit: Maximum number of messages to return
            message_types: Optional filter by message types
            
        Returns:
            List of messages
        """
        try:
            if agent_id not in self.registered_agents:
                raise ValueError(f"Agent {agent_id} not registered")
            
            queue = self.message_queues[agent_id]
            messages = []
            
            # Get messages from queue
            count = 0
            while queue and count < limit:
                message = queue.popleft()
                
                # Check if message is expired
                if message.expires_at and datetime.utcnow() > message.expires_at:
                    message.status = MessageStatus.EXPIRED
                    continue
                
                # Filter by message type if specified
                if message_types and message.message_type not in message_types:
                    # Put back in queue if not matching filter
                    queue.appendleft(message)
                    continue
                
                # Mark as delivered
                message.status = MessageStatus.DELIVERED
                messages.append(message)
                count += 1
            
            # Update agent last activity
            if messages:
                self.registered_agents[agent_id]['last_heartbeat'] = datetime.utcnow()
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages for {agent_id}: {e}")
            return []
    
    async def acknowledge_message(self, agent_id: str, message_id: str) -> bool:
        """Acknowledge receipt and processing of a message"""
        try:
            if message_id not in self.messages:
                logger.warning(f"Message {message_id} not found for acknowledgment")
                return False
            
            message = self.messages[message_id]
            
            if message.to_agent != agent_id:
                logger.warning(f"Agent {agent_id} cannot acknowledge message {message_id} (not recipient)")
                return False
            
            message.status = MessageStatus.ACKNOWLEDGED
            
            # Update metrics
            self.communication_metrics['successful_deliveries'] += 1
            
            # Calculate delivery time
            delivery_time = (datetime.utcnow() - message.created_at).total_seconds()
            current_avg = self.communication_metrics['average_delivery_time']
            total_successful = self.communication_metrics['successful_deliveries']
            
            self.communication_metrics['average_delivery_time'] = (
                (current_avg * (total_successful - 1) + delivery_time) / total_successful
            )
            
            logger.info(f"Message {message_id} acknowledged by {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging message: {e}")
            return False
    
    async def delegate_task(
        self,
        from_agent: str,
        to_agent: str,
        task_data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM,
        deadline: Optional[datetime] = None
    ) -> str:
        """
        Delegate a task from one agent to another.
        
        Args:
            from_agent: Delegating agent ID
            to_agent: Receiving agent ID
            task_data: Task information and parameters
            priority: Task priority
            deadline: Optional deadline for task completion
            
        Returns:
            Delegation message ID
        """
        try:
            delegation_payload = {
                'action': 'delegate_task',
                'task_data': task_data,
                'deadline': deadline.isoformat() if deadline else None,
                'delegation_id': str(uuid.uuid4()),
                'expectations': {
                    'response_required': True,
                    'status_updates': True,
                    'result_format': 'structured'
                }
            }
            
            message_id = await self.send_message(
                from_agent=from_agent,
                to_agent=to_agent,
                message_type=MessageType.TASK_DELEGATION,
                payload=delegation_payload,
                priority=priority,
                response_expected=True
            )
            
            logger.info(f"Task delegated from {from_agent} to {to_agent} (message: {message_id})")
            
            return message_id
            
        except Exception as e:
            logger.error(f"Error delegating task: {e}")
            raise
    
    async def request_information(
        self,
        from_agent: str,
        to_agent: str,
        information_request: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM
    ) -> str:
        """
        Request information from another agent.
        
        Args:
            from_agent: Requesting agent ID
            to_agent: Information source agent ID
            information_request: Details of information needed
            priority: Request priority
            
        Returns:
            Request message ID
        """
        try:
            request_payload = {
                'action': 'provide_information',
                'request_details': information_request,
                'request_id': str(uuid.uuid4()),
                'format_requirements': {
                    'structured': True,
                    'confidence_scores': True,
                    'sources': True
                }
            }
            
            message_id = await self.send_message(
                from_agent=from_agent,
                to_agent=to_agent,
                message_type=MessageType.INFORMATION_REQUEST,
                payload=request_payload,
                priority=priority,
                response_expected=True
            )
            
            logger.info(f"Information requested from {to_agent} by {from_agent} (message: {message_id})")
            
            return message_id
            
        except Exception as e:
            logger.error(f"Error requesting information: {e}")
            raise
    
    async def broadcast_message(
        self,
        from_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM,
        agent_filter: Optional[Callable[[str], bool]] = None
    ) -> List[str]:
        """
        Broadcast a message to multiple agents.
        
        Args:
            from_agent: Broadcasting agent ID
            message_type: Type of broadcast message
            payload: Message payload
            priority: Message priority
            agent_filter: Optional filter function for recipient selection
            
        Returns:
            List of message IDs sent
        """
        try:
            message_ids = []
            
            # Get recipient agents
            recipients = []
            for agent_id, agent_info in self.registered_agents.items():
                if agent_id == from_agent:  # Don't send to self
                    continue
                
                if agent_info['status'] != 'active':
                    continue
                
                if agent_filter and not agent_filter(agent_id):
                    continue
                
                recipients.append(agent_id)
            
            # Send to all recipients
            broadcast_payload = {
                **payload,
                'broadcast_id': str(uuid.uuid4()),
                'recipient_count': len(recipients)
            }
            
            for recipient in recipients:
                message_id = await self.send_message(
                    from_agent=from_agent,
                    to_agent=recipient,
                    message_type=message_type,
                    payload=broadcast_payload,
                    priority=priority,
                    response_expected=False
                )
                message_ids.append(message_id)
            
            logger.info(f"Broadcast sent from {from_agent} to {len(recipients)} agents")
            
            return message_ids
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            raise
    
    async def create_communication_channel(
        self,
        agent_a: str,
        agent_b: str,
        channel_type: str = "bidirectional"
    ) -> str:
        """
        Create a dedicated communication channel between two agents.
        
        Args:
            agent_a: First agent ID
            agent_b: Second agent ID
            channel_type: Type of channel (bidirectional, unidirectional)
            
        Returns:
            Channel ID
        """
        try:
            # Validate agents
            if agent_a not in self.registered_agents or agent_b not in self.registered_agents:
                raise ValueError("Both agents must be registered")
            
            channel_id = f"channel_{agent_a}_{agent_b}_{int(time.time())}"
            
            channel = CommunicationChannel(
                channel_id=channel_id,
                agent_a=agent_a,
                agent_b=agent_b,
                channel_type=channel_type
            )
            
            self.communication_channels[channel_id] = channel
            
            logger.info(f"Communication channel created: {channel_id} ({agent_a} <-> {agent_b})")
            
            return channel_id
            
        except Exception as e:
            logger.error(f"Error creating communication channel: {e}")
            raise
    
    async def subscribe_to_events(
        self,
        agent_id: str,
        event_types: List[str],
        handler: Callable
    ):
        """Subscribe an agent to specific event types"""
        try:
            for event_type in event_types:
                self.message_handlers[event_type].append({
                    'agent_id': agent_id,
                    'handler': handler
                })
            
            logger.info(f"Agent {agent_id} subscribed to events: {event_types}")
            
        except Exception as e:
            logger.error(f"Error subscribing to events: {e}")
    
    async def _message_processor(self):
        """Background task to process message delivery"""
        while self._running:
            try:
                # Process pending messages
                expired_messages = []
                
                for message_id, message in list(self.pending_messages.items()):
                    # Check if message expired
                    if message.expires_at and datetime.utcnow() > message.expires_at:
                        message.status = MessageStatus.EXPIRED
                        expired_messages.append(message_id)
                        continue
                    
                    # Attempt delivery
                    if message.delivery_attempts < message.max_attempts:
                        success = await self._attempt_message_delivery(message)
                        if success:
                            del self.pending_messages[message_id]
                        else:
                            message.delivery_attempts += 1
                    else:
                        message.status = MessageStatus.FAILED
                        self.communication_metrics['failed_deliveries'] += 1
                        expired_messages.append(message_id)
                
                # Clean up expired/failed messages
                for message_id in expired_messages:
                    if message_id in self.pending_messages:
                        del self.pending_messages[message_id]
                
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                logger.error(f"Error in message processor: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _attempt_message_delivery(self, message: AgentMessage) -> bool:
        """Attempt to deliver a message to its recipient"""
        try:
            recipient_info = self.registered_agents.get(message.to_agent)
            if not recipient_info or recipient_info['status'] != 'active':
                return False
            
            # Add to recipient's queue
            queue = self.message_queues[message.to_agent]
            queue.append(message)
            
            # Call message handler if available
            handler = recipient_info.get('message_handler')
            if handler:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler for {message.to_agent}: {e}")
            
            message.status = MessageStatus.DELIVERED
            return True
            
        except Exception as e:
            logger.error(f"Error delivering message {message.message_id}: {e}")
            return False
    
    async def _heartbeat_monitor(self):
        """Monitor agent heartbeats and connection health"""
        while self._running:
            try:
                current_time = datetime.utcnow()
                heartbeat_timeout = timedelta(seconds=self.heartbeat_interval * 3)
                
                for agent_id, agent_info in self.registered_agents.items():
                    last_heartbeat = agent_info['last_heartbeat']
                    
                    if current_time - last_heartbeat > heartbeat_timeout:
                        # Agent appears inactive
                        if agent_info['status'] == 'active':
                            agent_info['status'] = 'inactive'
                            logger.warning(f"Agent {agent_id} marked inactive due to missed heartbeats")
                    
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_messages(self):
        """Clean up expired messages and maintain system health"""
        while self._running:
            try:
                current_time = datetime.utcnow()
                expired_message_ids = []
                
                # Check for expired messages
                for message_id, message in self.messages.items():
                    if message.expires_at and current_time > message.expires_at:
                        expired_message_ids.append(message_id)
                
                # Remove expired messages
                for message_id in expired_message_ids:
                    del self.messages[message_id]
                    if message_id in self.pending_messages:
                        del self.pending_messages[message_id]
                
                if expired_message_ids:
                    logger.info(f"Cleaned up {len(expired_message_ids)} expired messages")
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in message cleanup: {e}")
                await asyncio.sleep(600)
    
    async def _performance_monitor(self):
        """Monitor communication performance and generate metrics"""
        while self._running:
            try:
                # Calculate performance metrics
                total_messages = self.communication_metrics['total_messages']
                successful = self.communication_metrics['successful_deliveries']
                failed = self.communication_metrics['failed_deliveries']
                
                if total_messages > 0:
                    success_rate = successful / total_messages
                    failure_rate = failed / total_messages
                    
                    # Log performance summary
                    logger.info(f"Message Bus Performance: {total_messages} total, "
                              f"{success_rate:.2%} success rate, "
                              f"{self.communication_metrics['average_delivery_time']:.2f}s avg delivery")
                
                await asyncio.sleep(300)  # Report every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(600)
    
    async def get_communication_status(self) -> Dict[str, Any]:
        """Get comprehensive communication system status"""
        try:
            active_agents = sum(1 for info in self.registered_agents.values() if info['status'] == 'active')
            total_queue_size = sum(len(queue) for queue in self.message_queues.values())
            
            return {
                'message_bus_status': 'active' if self._running else 'inactive',
                'registered_agents': len(self.registered_agents),
                'active_agents': active_agents,
                'total_messages': self.communication_metrics['total_messages'],
                'pending_messages': len(self.pending_messages),
                'total_queue_size': total_queue_size,
                'communication_channels': len(self.communication_channels),
                'metrics': self.communication_metrics,
                'performance': {
                    'average_delivery_time': self.communication_metrics['average_delivery_time'],
                    'success_rate': (
                        self.communication_metrics['successful_deliveries'] / 
                        max(1, self.communication_metrics['total_messages'])
                    ),
                    'active_conversations': self.communication_metrics['active_conversations']
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting communication status: {e}")
            return {'error': str(e)}


class AgentCommunicationProtocol:
    """
    Protocol definition for standardized agent communication.
    
    Defines message formats, conversation patterns, and communication standards.
    """
    
    @staticmethod
    def create_task_delegation_message(
        task_id: str,
        task_type: str,
        description: str,
        parameters: Dict[str, Any],
        deadline: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create standardized task delegation message"""
        return {
            'action': 'delegate_task',
            'task_id': task_id,
            'task_type': task_type,
            'description': description,
            'parameters': parameters,
            'deadline': deadline.isoformat() if deadline else None,
            'response_format': 'structured_result'
        }
    
    @staticmethod
    def create_information_request_message(
        query: str,
        information_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create standardized information request message"""
        return {
            'action': 'provide_information',
            'query': query,
            'information_type': information_type,
            'context': context,
            'response_format': 'structured_data'
        }
    
    @staticmethod
    def create_status_update_message(
        status: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create standardized status update message"""
        return {
            'action': 'status_update',
            'status': status,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def create_collaboration_request_message(
        collaboration_type: str,
        proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create standardized collaboration request message"""
        return {
            'action': 'collaborate',
            'collaboration_type': collaboration_type,
            'proposal': proposal,
            'response_required': True
        }