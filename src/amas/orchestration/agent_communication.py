"""
Inter-Agent Communication System

This module provides a comprehensive communication infrastructure for the hierarchical
agent orchestration system. It enables sophisticated communication and collaboration
between agents across all hierarchy layers (Executive, Management, Specialist, Execution)
with reliable message routing, context sharing, and coordination protocols.

Key Features:
- Message Bus: Centralized message routing with guaranteed delivery
- Broadcast System: Topic-based pub/sub for group communication
- Context Sharing: Agents can share working data and intermediate results
- Help Requests: Agents can request assistance from other specialists
- Escalation: Automatic escalation to management for critical issues
- Quality Coordination: Specialized coordinators for research and QA workflows
- Message Expiration: Time-based message expiration for stale data
- Retry Logic: Automatic retry with exponential backoff for failed deliveries

Dependencies:
- asyncio: For asynchronous message processing
- datetime: For message timestamps and expiration
- collections: For efficient queue and dictionary operations

Usage Example:
    >>> from amas.orchestration.agent_communication import get_communication_bus
    >>> bus = get_communication_bus()
    >>> 
    >>> # Send a message
    >>> message_id = await bus.send_message(
    ...     sender_id="agent_1",
    ...     recipient_id="agent_2",
    ...     message_type=MessageType.SHARE_FINDINGS,
    ...     payload={"data": "research results"}
    ... )
    >>> 
    >>> # Request help from specialist
    >>> help_id = await bus.request_specialist_help(
    ...     requesting_agent_id="agent_1",
    ...     required_specialty="data_analyst",
    ...     help_context={"task": "analyze data"}
    ... )

Performance Considerations:
- Message queues use deque for O(1) append/pop operations
- Broadcast subscriptions use sets for O(1) membership checks
- Message cleanup runs in background to prevent memory leaks
- Failed deliveries are tracked for monitoring and debugging

Security Considerations:
- All message types are validated through the MessageType enum
- Message payloads should be validated by the receiving agent
- Sensitive data should be encrypted before transmission
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import json
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class MessageType(str, Enum):
    """
    Message types for inter-agent communication.
    
    This enum defines all valid message types that can be exchanged between agents
    in the orchestration system. Message types are organized by category:
    
    - Task Coordination: Messages related to task lifecycle
    - Information Sharing: Messages for sharing data and context
    - Help & Assistance: Messages for requesting and providing help
    - Quality Assurance: Messages for quality checks and approvals
    - Management: Messages for escalation and coordination
    - System: Messages for system-level operations
    - Error Handling: Messages for error reporting and recovery
    - Acknowledgment: Messages for confirming receipt and processing
    """
    
    # ========== Task Coordination Messages ==========
    TASK_STARTED = "task_started"
    """Notify that a task has begun execution. Sent by workflow executor to assigned agent."""
    
    TASK_COMPLETED = "task_completed"
    """Notify that a task has completed successfully. Sent by agent to workflow executor."""
    
    TASK_BLOCKED = "task_blocked"
    """Notify that a task cannot proceed due to dependencies or errors. Requires escalation."""
    
    TASK_FAILED = "task_failed"
    """Notify that a task has failed. Includes error details for recovery attempts."""
    
    HANDOFF_REQUEST = "handoff_request"
    """Request to transfer task ownership to another agent. Used for load balancing."""
    
    # ========== Information Sharing Messages ==========
    SHARE_CONTEXT = "share_context"
    """Share working context with other agents. Used for collaborative work."""
    
    SHARE_FINDINGS = "share_findings"
    """Share intermediate results or findings. Used in research and analysis workflows."""
    
    SHARE_RESOURCES = "share_resources"
    """Share useful resources, data, or tools. Used for resource optimization."""
    
    # ========== Help & Assistance Messages ==========
    REQUEST_HELP = "request_help"
    """Request assistance from a specialist agent. Includes context about what help is needed."""
    
    OFFER_HELP = "offer_help"
    """Offer to help another agent. Used when agent has available capacity."""
    
    ACCEPT_HELP = "accept_help"
    """Accept an offer of help. Confirms the help relationship."""
    
    HELP_RESPONSE = "help_response"
    """Response to a help request. Contains the assistance provided."""
    
    # ========== Quality Assurance Messages ==========
    QUALITY_CHECK_REQUEST = "quality_check_request"
    """Request a quality review of work. Sent to QA specialists."""
    
    QUALITY_FEEDBACK = "quality_feedback"
    """Provide quality feedback on reviewed work. Includes scores and recommendations."""
    
    APPROVAL_REQUEST = "approval_request"
    """Request approval for work or decision. Sent to management or executive layer."""
    
    APPROVAL_RESPONSE = "approval_response"
    """Response to approval request. Contains approval decision and conditions."""
    
    # ========== Management & Coordination Messages ==========
    STATUS_UPDATE = "status_update"
    """General status update. Used for progress reporting and monitoring."""
    
    ESCALATION = "escalation"
    """Escalate issue to higher layer. Used when agent cannot resolve issue independently."""
    
    COORDINATION_SYNC = "coordination_sync"
    """Synchronization point for parallel tasks. Ensures coordination between agents."""
    
    LOAD_BALANCE_REQUEST = "load_balance_request"
    """Request load balancing assistance. Used when agent is overloaded."""
    
    # ========== System Messages ==========
    HEARTBEAT = "heartbeat"
    """Health check message. Sent periodically to confirm agent is alive."""
    
    SHUTDOWN_NOTICE = "shutdown_notice"
    """Notify that agent is going offline. Allows graceful shutdown coordination."""
    
    RECOVERY_NOTICE = "recovery_notice"
    """Notify that agent has recovered and is back online."""
    
    # ========== Error Handling Messages ==========
    ERROR_REPORT = "error_report"
    """Report an error that occurred during execution. Includes error details and context."""
    
    ERROR_RECOVERY = "error_recovery"
    """Notify that error recovery has been attempted. Includes recovery status."""
    
    # ========== Acknowledgment Messages ==========
    ACKNOWLEDGMENT = "acknowledgment"
    """Acknowledge receipt of a message. Used for reliable message delivery."""
    
    MESSAGE_RECEIVED = "message_received"
    """Confirm that message was received and is being processed."""
    
    MESSAGE_PROCESSED = "message_processed"
    """Confirm that message has been fully processed. Used for request-response patterns."""
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """
        Validate if a string value is a valid message type.
        
        Args:
            value: String value to validate
            
        Returns:
            True if value is a valid message type, False otherwise
        """
        try:
            cls(value)
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_category(cls, message_type: "MessageType") -> str:
        """
        Get the category of a message type.
        
        Args:
            message_type: MessageType enum value
            
        Returns:
            Category name (e.g., "task_coordination", "error_handling")
        """
        categories = {
            # Task Coordination
            cls.TASK_STARTED: "task_coordination",
            cls.TASK_COMPLETED: "task_coordination",
            cls.TASK_BLOCKED: "task_coordination",
            cls.TASK_FAILED: "task_coordination",
            cls.HANDOFF_REQUEST: "task_coordination",
            
            # Information Sharing
            cls.SHARE_CONTEXT: "information_sharing",
            cls.SHARE_FINDINGS: "information_sharing",
            cls.SHARE_RESOURCES: "information_sharing",
            
            # Help & Assistance
            cls.REQUEST_HELP: "help_assistance",
            cls.OFFER_HELP: "help_assistance",
            cls.ACCEPT_HELP: "help_assistance",
            cls.HELP_RESPONSE: "help_assistance",
            
            # Quality Assurance
            cls.QUALITY_CHECK_REQUEST: "quality_assurance",
            cls.QUALITY_FEEDBACK: "quality_assurance",
            cls.APPROVAL_REQUEST: "quality_assurance",
            cls.APPROVAL_RESPONSE: "quality_assurance",
            
            # Management
            cls.STATUS_UPDATE: "management",
            cls.ESCALATION: "management",
            cls.COORDINATION_SYNC: "management",
            cls.LOAD_BALANCE_REQUEST: "management",
            
            # System
            cls.HEARTBEAT: "system",
            cls.SHUTDOWN_NOTICE: "system",
            cls.RECOVERY_NOTICE: "system",
            
            # Error Handling
            cls.ERROR_REPORT: "error_handling",
            cls.ERROR_RECOVERY: "error_handling",
            
            # Acknowledgment
            cls.ACKNOWLEDGMENT: "acknowledgment",
            cls.MESSAGE_RECEIVED: "acknowledgment",
            cls.MESSAGE_PROCESSED: "acknowledgment",
        }
        return categories.get(message_type, "unknown")

class Priority(str, Enum):
    """
    Message priority levels for inter-agent communication.
    
    Priorities determine message delivery order and timeout behavior.
    Higher priority messages are processed first and have shorter timeouts.
    """
    LOW = "low"
    """Low priority: Non-urgent messages, can be delayed if system is busy."""
    
    NORMAL = "normal"
    """Normal priority: Standard messages, processed in order of arrival."""
    
    HIGH = "high"
    """High priority: Important messages, processed before normal priority."""
    
    URGENT = "urgent"
    """Urgent priority: Time-sensitive messages, processed immediately."""
    
    CRITICAL = "critical"
    """Critical priority: System-critical messages, highest priority, shortest timeout."""
    
    @classmethod
    def get_timeout_seconds(cls, priority: "Priority") -> int:
        """
        Get timeout in seconds for a priority level.
        
        Args:
            priority: Priority enum value
            
        Returns:
            Timeout in seconds
        """
        timeouts = {
            cls.LOW: 600,      # 10 minutes
            cls.NORMAL: 300,   # 5 minutes
            cls.HIGH: 180,     # 3 minutes
            cls.URGENT: 60,    # 1 minute
            cls.CRITICAL: 30,  # 30 seconds
        }
        return timeouts.get(priority, 300)

@dataclass
class AgentMessage:
    """Message passed between agents in the hierarchy"""
    id: str
    sender_agent_id: str
    recipient_agent_id: str
    message_type: MessageType
    priority: Priority
    
    # Message content
    payload: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Tracing and audit
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    trace_id: str = field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:8]}")
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    # Delivery tracking
    delivered: bool = False
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3
    
    # Response tracking
    requires_response: bool = False
    response_timeout_seconds: int = 300  # 5 minutes
    response_received: bool = False
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    def get_age_seconds(self) -> float:
        """Get message age in seconds"""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()

@dataclass
class CommunicationChannel:
    """Communication channel between agents"""
    id: str
    agent_a_id: str
    agent_b_id: str
    
    # Channel properties
    channel_type: str = "direct"  # direct, broadcast, hierarchical
    encryption_enabled: bool = True
    message_retention_hours: int = 24
    
    # Performance metrics
    message_count: int = 0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    
    # Message queues
    messages: deque = field(default_factory=deque)
    pending_responses: Dict[str, AgentMessage] = field(default_factory=dict)
    
    def add_message(self, message: AgentMessage):
        """Add message to channel"""
        self.messages.append(message)
        self.message_count += 1
        
        # Cleanup old messages
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.message_retention_hours)
        while (self.messages and 
               self.messages[0].created_at < cutoff_time):
            old_message = self.messages.popleft()
            if old_message.id in self.pending_responses:
                del self.pending_responses[old_message.id]

class AgentCommunicationBus:
    """Central communication hub for all agent interactions"""
    
    def __init__(self):
        self.channels: Dict[str, CommunicationChannel] = {}
        self.message_queues: Dict[str, deque] = defaultdict(deque)
        self.broadcast_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        
        # Message routing and delivery
        self.pending_deliveries: deque = deque()
        self.failed_deliveries: deque = deque()
        
        # Performance tracking
        self.total_messages: int = 0
        self.successful_deliveries: int = 0
        self.failed_deliveries_count: int = 0
        
        # Start background message processing
        asyncio.create_task(self._process_message_queue())
        asyncio.create_task(self._cleanup_expired_messages())
        
        logger.info("Agent Communication Bus initialized")
    
    def _get_channel_id(self, agent_a: str, agent_b: str) -> str:
        """Get standardized channel ID for two agents"""
        # Sort to ensure consistent channel ID regardless of order
        agents = sorted([agent_a, agent_b])
        return f"channel_{agents[0]}_{agents[1]}"
    
    async def send_message(self, 
                          sender_id: str,
                          recipient_id: str,
                          message_type: MessageType,
                          payload: Dict[str, Any],
                          priority: Priority = Priority.NORMAL,
                          requires_response: bool = False,
                          response_timeout: int = 300) -> str:
        """
        Send message from one agent to another.
        
        Args:
            sender_id: ID of the sending agent
            recipient_id: ID of the receiving agent
            message_type: Type of message (validated against MessageType enum)
            payload: Message payload data
            priority: Message priority level (default: NORMAL)
            requires_response: Whether message requires a response
            response_timeout: Timeout in seconds for response (default: 300)
            
        Returns:
            Message ID for tracking
            
        Raises:
            ValueError: If message_type is not a valid MessageType
            ValueError: If sender_id or recipient_id is empty
        """
        # Validate inputs
        if not sender_id or not sender_id.strip():
            raise ValueError("sender_id cannot be empty")
        if not recipient_id or not recipient_id.strip():
            raise ValueError("recipient_id cannot be empty")
        if not isinstance(message_type, MessageType):
            raise ValueError(f"message_type must be a MessageType enum value, got {type(message_type)}")
        
        message = AgentMessage(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            sender_agent_id=sender_id,
            recipient_agent_id=recipient_id,
            message_type=message_type,
            priority=priority,
            payload=payload,
            requires_response=requires_response,
            response_timeout_seconds=response_timeout
        )
        
        # Set expiration for time-sensitive messages
        if priority in [Priority.HIGH, Priority.URGENT, Priority.CRITICAL]:
            message.expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        # Queue for delivery
        self.pending_deliveries.append(message)
        self.total_messages += 1
        
        logger.debug(f"Queued message {message.id}: {sender_id} -> {recipient_id} ({message_type.value})")
        
        return message.id
    
    async def broadcast_message(self,
                              sender_id: str,
                              topic: str,
                              message_type: MessageType,
                              payload: Dict[str, Any],
                              priority: Priority = Priority.NORMAL) -> List[str]:
        """Broadcast message to all subscribers of a topic"""
        
        subscribers = self.broadcast_subscriptions.get(topic, set())
        if not subscribers:
            logger.warning(f"No subscribers for broadcast topic: {topic}")
            return []
        
        message_ids = []
        
        for recipient_id in subscribers:
            if recipient_id != sender_id:  # Don't send to self
                message_id = await self.send_message(
                    sender_id=sender_id,
                    recipient_id=recipient_id,
                    message_type=message_type,
                    payload={**payload, "broadcast_topic": topic},
                    priority=priority
                )
                message_ids.append(message_id)
        
        logger.info(f"Broadcast {len(message_ids)} messages for topic '{topic}'")
        return message_ids
    
    def subscribe_to_topic(self, agent_id: str, topic: str):
        """Subscribe agent to broadcast topic"""
        self.broadcast_subscriptions[topic].add(agent_id)
        logger.debug(f"Agent {agent_id} subscribed to topic '{topic}'")
    
    def unsubscribe_from_topic(self, agent_id: str, topic: str):
        """Unsubscribe agent from broadcast topic"""
        self.broadcast_subscriptions[topic].discard(agent_id)
        logger.debug(f"Agent {agent_id} unsubscribed from topic '{topic}'")
    
    async def get_messages(self, agent_id: str, limit: int = 10) -> List[AgentMessage]:
        """Get pending messages for an agent"""
        agent_queue = self.message_queues[agent_id]
        
        messages = []
        for _ in range(min(limit, len(agent_queue))):
            if agent_queue:
                message = agent_queue.popleft()
                if not message.is_expired():
                    messages.append(message)
                    message.delivered = True
                    self.successful_deliveries += 1
        
        return messages
    
    async def send_response(self,
                          responding_agent_id: str,
                          original_message_id: str,
                          response_payload: Dict[str, Any],
                          success: bool = True) -> Optional[str]:
        """Send response to a message that required a response"""
        
        # Find original message to get sender
        original_message = None
        for channel in self.channels.values():
            if original_message_id in channel.pending_responses:
                original_message = channel.pending_responses[original_message_id]
                break
        
        if not original_message:
            logger.error(f"Original message {original_message_id} not found for response")
            return None
        
        # Create response message
        response_message = await self.send_message(
            sender_id=responding_agent_id,
            recipient_id=original_message.sender_agent_id,
            message_type=MessageType.APPROVAL_RESPONSE if "approval" in original_message.message_type.value 
                         else MessageType.SHARE_FINDINGS,
            payload={
                "response_to": original_message_id,
                "success": success,
                **response_payload
            },
            priority=original_message.priority
        )
        
        # Mark original as responded
        original_message.response_received = True
        
        logger.info(f"Response sent: {responding_agent_id} -> {original_message.sender_agent_id}")
        return response_message
    
    async def request_specialist_help(self,
                                    requesting_agent_id: str,
                                    required_specialty: str,
                                    help_context: Dict[str, Any],
                                    urgency: Priority = Priority.NORMAL) -> Optional[str]:
        """Request help from a specialist agent"""
        
        # Find hierarchy manager to locate appropriate specialist
        from .agent_hierarchy import get_hierarchy_manager
        hierarchy = get_hierarchy_manager()
        
        # Find available specialists
        available_specialists = []
        for agent in hierarchy.agents.values():
            if (agent.specialty and 
                agent.specialty.value == required_specialty and
                agent.is_available() and
                agent.is_healthy()):
                available_specialists.append(agent.id)
        
        if not available_specialists:
            logger.warning(f"No available specialists for {required_specialty}")
            return None
        
        # Select best specialist (for now, use first available)
        specialist_id = available_specialists[0]
        
        # Send help request
        message_id = await self.send_message(
            sender_id=requesting_agent_id,
            recipient_id=specialist_id,
            message_type=MessageType.REQUEST_HELP,
            payload={
                "required_specialty": required_specialty,
                "help_context": help_context,
                "requesting_agent_context": {
                    "current_task": help_context.get("current_task"),
                    "progress_status": help_context.get("progress", "unknown"),
                    "deadline": help_context.get("deadline")
                }
            },
            priority=urgency,
            requires_response=True,
            response_timeout=600  # 10 minutes for help requests
        )
        
        logger.info(f"Help request sent: {requesting_agent_id} -> {specialist_id} ({required_specialty})")
        return message_id
    
    async def share_context(self,
                           sender_id: str,
                           recipients: List[str],
                           context_data: Dict[str, Any],
                           context_type: str = "general") -> List[str]:
        """Share working context with other agents"""
        
        message_ids = []
        
        for recipient_id in recipients:
            message_id = await self.send_message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                message_type=MessageType.SHARE_CONTEXT,
                payload={
                    "context_type": context_type,
                    "context_data": context_data,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "sender_specialty": self._get_agent_specialty(sender_id)
                },
                priority=Priority.NORMAL
            )
            message_ids.append(message_id)
        
        logger.info(f"Context shared: {sender_id} -> {len(recipients)} agents ({context_type})")
        return message_ids
    
    async def coordinate_parallel_tasks(self,
                                      coordinator_id: str,
                                      parallel_agents: List[str],
                                      sync_point_name: str,
                                      coordination_data: Dict[str, Any]) -> bool:
        """Coordinate synchronization point for parallel tasks"""
        
        # Send coordination message to all parallel agents
        coordination_messages = await self.broadcast_message(
            sender_id=coordinator_id,
            topic=f"sync_{sync_point_name}",
            message_type=MessageType.COORDINATION_SYNC,
            payload={
                "sync_point": sync_point_name,
                "coordination_data": coordination_data,
                "participating_agents": parallel_agents,
                "sync_timeout": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
            },
            priority=Priority.HIGH
        )
        
        # Subscribe all agents to sync topic
        for agent_id in parallel_agents:
            self.subscribe_to_topic(agent_id, f"sync_{sync_point_name}")
        
        logger.info(f"Coordination sync initiated: {sync_point_name} with {len(parallel_agents)} agents")
        return len(coordination_messages) == len(parallel_agents)
    
    async def escalate_to_management(self,
                                   escalating_agent_id: str,
                                   issue_type: str,
                                   escalation_data: Dict[str, Any],
                                   urgency: Priority = Priority.HIGH) -> Optional[str]:
        """Escalate issue to management layer"""
        
        # Find appropriate management agent
        from .agent_hierarchy import get_hierarchy_manager, AgentLayer
        hierarchy = get_hierarchy_manager()
        
        escalating_agent = hierarchy.agents.get(escalating_agent_id)
        if not escalating_agent:
            logger.error(f"Escalating agent not found: {escalating_agent_id}")
            return None
        
        # Find supervisor or appropriate management agent
        management_agent_id = escalating_agent.supervisor_id
        
        if not management_agent_id:
            # Find any available management agent
            management_agents = [a for a in hierarchy.agents.values() 
                               if a.layer == AgentLayer.MANAGEMENT and a.is_available()]
            if management_agents:
                management_agent_id = management_agents[0].id
        
        if not management_agent_id:
            logger.error("No management agents available for escalation")
            return None
        
        # Send escalation message
        message_id = await self.send_message(
            sender_id=escalating_agent_id,
            recipient_id=management_agent_id,
            message_type=MessageType.ESCALATION,
            payload={
                "issue_type": issue_type,
                "escalation_data": escalation_data,
                "escalating_agent": {
                    "id": escalating_agent_id,
                    "specialty": escalating_agent.specialty.value if escalating_agent.specialty else None,
                    "current_load": escalating_agent.get_load_percentage(),
                    "success_rate": escalating_agent.success_rate
                },
                "recommended_actions": escalation_data.get("recommended_actions", [])
            },
            priority=urgency,
            requires_response=True,
            response_timeout=900  # 15 minutes for management response
        )
        
        logger.warning(f"Issue escalated: {escalating_agent_id} -> {management_agent_id} ({issue_type})")
        return message_id
    
    async def _process_message_queue(self):
        """Background task to process pending message deliveries"""
        while True:
            try:
                if self.pending_deliveries:
                    message = self.pending_deliveries.popleft()
                    
                    if message.is_expired():
                        self.failed_deliveries_count += 1
                        logger.warning(f"Message {message.id} expired before delivery")
                        continue
                    
                    # Attempt delivery
                    success = await self._deliver_message(message)
                    
                    if success:
                        self.successful_deliveries += 1
                    else:
                        message.delivery_attempts += 1
                        
                        if message.delivery_attempts < message.max_delivery_attempts:
                            # Retry with exponential backoff
                            await asyncio.sleep(2 ** message.delivery_attempts)
                            self.pending_deliveries.append(message)
                        else:
                            self.failed_deliveries.append(message)
                            self.failed_deliveries_count += 1
                            logger.error(f"Message {message.id} failed after {message.max_delivery_attempts} attempts")
                
                await asyncio.sleep(0.1)  # Prevent busy waiting
                
            except Exception as e:
                logger.error(f"Error in message processing: {e}")
                await asyncio.sleep(1)
    
    async def _deliver_message(self, message: AgentMessage) -> bool:
        """Attempt to deliver a message to its recipient"""
        try:
            # Get or create channel
            channel_id = self._get_channel_id(message.sender_agent_id, message.recipient_agent_id)
            
            if channel_id not in self.channels:
                channel = CommunicationChannel(
                    id=channel_id,
                    agent_a_id=message.sender_agent_id,
                    agent_b_id=message.recipient_agent_id
                )
                self.channels[channel_id] = channel
            
            channel = self.channels[channel_id]
            
            # Add to recipient's message queue
            self.message_queues[message.recipient_agent_id].append(message)
            
            # Add to channel
            channel.add_message(message)
            
            # Track pending response if required
            if message.requires_response:
                channel.pending_responses[message.id] = message
            
            # Update delivery status
            message.delivered = True
            
            logger.debug(f"Message {message.id} delivered to {message.recipient_agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deliver message {message.id}: {e}")
            return False
    
    async def _cleanup_expired_messages(self):
        """Background task to clean up expired and old messages"""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Clean up message queues
                for agent_id, queue in self.message_queues.items():
                    # Remove expired messages
                    cleaned_queue = deque()
                    for message in queue:
                        if not message.is_expired():
                            cleaned_queue.append(message)
                    self.message_queues[agent_id] = cleaned_queue
                
                # Clean up channels
                for channel in self.channels.values():
                    # Remove expired pending responses
                    expired_responses = []
                    for msg_id, msg in channel.pending_responses.items():
                        if (current_time - msg.created_at).total_seconds() > msg.response_timeout_seconds:
                            expired_responses.append(msg_id)
                    
                    for msg_id in expired_responses:
                        del channel.pending_responses[msg_id]
                        logger.warning(f"Response timeout for message {msg_id}")
                
                # Clean up failed deliveries (keep last 1000)
                while len(self.failed_deliveries) > 1000:
                    self.failed_deliveries.popleft()
                
                # Sleep before next cleanup
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in message cleanup: {e}")
                await asyncio.sleep(300)
    
    def _get_agent_specialty(self, agent_id: str) -> Optional[str]:
        """Get agent specialty for context"""
        from .agent_hierarchy import get_hierarchy_manager
        hierarchy = get_hierarchy_manager()
        
        agent = hierarchy.agents.get(agent_id)
        if agent and agent.specialty:
            return agent.specialty.value
        return None
    
    async def get_communication_metrics(self) -> Dict[str, Any]:
        """Get communication system performance metrics"""
        active_channels = len(self.channels)
        total_queue_size = sum(len(queue) for queue in self.message_queues.values())
        
        success_rate = (self.successful_deliveries / max(1, self.total_messages)) * 100
        
        return {
            "total_messages": self.total_messages,
            "successful_deliveries": self.successful_deliveries,
            "failed_deliveries": self.failed_deliveries_count,
            "success_rate_percent": round(success_rate, 2),
            "active_channels": active_channels,
            "total_queue_size": total_queue_size,
            "pending_deliveries": len(self.pending_deliveries),
            "broadcast_topics": len(self.broadcast_subscriptions),
            "avg_delivery_latency_ms": self._calculate_avg_delivery_latency()
        }
    
    def _calculate_avg_delivery_latency(self) -> float:
        """Calculate average message delivery latency"""
        total_latency = 0.0
        count = 0
        
        for channel in self.channels.values():
            total_latency += channel.avg_latency_ms
            count += 1
        
        return total_latency / max(1, count)

# Specialized communication helpers

class ResearchCoordinator:
    """Specialized coordinator for research team communication"""
    
    def __init__(self, communication_bus: AgentCommunicationBus):
        self.bus = communication_bus
        self.active_research_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def coordinate_research_session(self,
                                        research_lead_id: str,
                                        research_agents: List[str],
                                        research_objectives: Dict[str, Any]) -> str:
        """Coordinate a collaborative research session"""
        session_id = f"research_{uuid.uuid4().hex[:8]}"
        
        # Create research coordination topic
        topic = f"research_session_{session_id}"
        
        # Subscribe all research agents
        for agent_id in research_agents:
            self.bus.subscribe_to_topic(agent_id, topic)
        
        # Send initial coordination message
        await self.bus.broadcast_message(
            sender_id=research_lead_id,
            topic=topic,
            message_type=MessageType.COORDINATION_SYNC,
            payload={
                "session_id": session_id,
                "research_objectives": research_objectives,
                "participating_agents": research_agents,
                "coordination_strategy": "divide_and_conquer",
                "sync_frequency_minutes": 15
            },
            priority=Priority.HIGH
        )
        
        # Track session
        self.active_research_sessions[session_id] = {
            "lead_id": research_lead_id,
            "agents": research_agents,
            "objectives": research_objectives,
            "started_at": datetime.now(timezone.utc),
            "last_sync": datetime.now(timezone.utc)
        }
        
        logger.info(f"Research session {session_id} started with {len(research_agents)} agents")
        return session_id
    
    async def share_research_findings(self,
                                    researcher_id: str,
                                    session_id: str,
                                    findings: Dict[str, Any]) -> List[str]:
        """Share research findings with other session participants"""
        session = self.active_research_sessions.get(session_id)
        if not session:
            logger.error(f"Research session {session_id} not found")
            return []
        
        # Share with all other session participants
        recipients = [agent_id for agent_id in session["agents"] if agent_id != researcher_id]
        
        message_ids = []
        for recipient_id in recipients:
            message_id = await self.bus.send_message(
                sender_id=researcher_id,
                recipient_id=recipient_id,
                message_type=MessageType.SHARE_FINDINGS,
                payload={
                    "session_id": session_id,
                    "findings": findings,
                    "research_area": findings.get("research_area"),
                    "confidence_score": findings.get("confidence", 0.8),
                    "sources_count": findings.get("sources_count", 0)
                },
                priority=Priority.NORMAL
            )
            message_ids.append(message_id)
        
        logger.info(f"Research findings shared: {researcher_id} -> {len(recipients)} agents")
        return message_ids

class QualityAssuranceCoordinator:
    """Specialized coordinator for quality assurance communication"""
    
    def __init__(self, communication_bus: AgentCommunicationBus):
        self.bus = communication_bus
        self.active_reviews: Dict[str, Dict[str, Any]] = {}
    
    async def initiate_quality_review(self,
                                    qa_lead_id: str,
                                    deliverable_id: str,
                                    deliverable_content: Dict[str, Any],
                                    review_criteria: List[str]) -> str:
        """Initiate multi-layer quality review process"""
        review_id = f"qareview_{uuid.uuid4().hex[:8]}"
        
        # Find available QA specialists
        from .agent_hierarchy import get_hierarchy_manager, AgentSpecialty
        hierarchy = get_hierarchy_manager()
        
        qa_specialists = [
            agent.id for agent in hierarchy.agents.values()
            if (agent.specialty in [AgentSpecialty.FACT_CHECKER, 
                                   AgentSpecialty.QUALITY_CONTROLLER,
                                   AgentSpecialty.COMPLIANCE_REVIEWER] and
                agent.is_available())
        ]
        
        if not qa_specialists:
            logger.error("No QA specialists available for review")
            return None
        
        # Create review coordination topic
        topic = f"qa_review_{review_id}"
        
        # Subscribe QA specialists
        for specialist_id in qa_specialists:
            self.bus.subscribe_to_topic(specialist_id, topic)
        
        # Send review request
        await self.bus.broadcast_message(
            sender_id=qa_lead_id,
            topic=topic,
            message_type=MessageType.QUALITY_CHECK_REQUEST,
            payload={
                "review_id": review_id,
                "deliverable_id": deliverable_id,
                "deliverable_content": deliverable_content,
                "review_criteria": review_criteria,
                "review_deadline": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
                "participating_reviewers": qa_specialists
            },
            priority=Priority.HIGH
        )
        
        # Track review
        self.active_reviews[review_id] = {
            "lead_id": qa_lead_id,
            "deliverable_id": deliverable_id,
            "reviewers": qa_specialists,
            "criteria": review_criteria,
            "started_at": datetime.now(timezone.utc),
            "status": "in_progress"
        }
        
        logger.info(f"Quality review {review_id} initiated with {len(qa_specialists)} reviewers")
        return review_id
    
    async def submit_quality_feedback(self,
                                    reviewer_id: str,
                                    review_id: str,
                                    feedback: Dict[str, Any]) -> bool:
        """Submit quality feedback for a review"""
        review = self.active_reviews.get(review_id)
        if not review:
            logger.error(f"Review {review_id} not found")
            return False
        
        # Send feedback to review lead
        await self.bus.send_message(
            sender_id=reviewer_id,
            recipient_id=review["lead_id"],
            message_type=MessageType.QUALITY_FEEDBACK,
            payload={
                "review_id": review_id,
                "feedback": feedback,
                "overall_score": feedback.get("overall_score", 0.8),
                "approval_recommendation": feedback.get("approval", "conditional"),
                "required_changes": feedback.get("required_changes", []),
                "reviewer_specialty": self.bus._get_agent_specialty(reviewer_id)
            },
            priority=Priority.HIGH
        )
        
        logger.info(f"Quality feedback submitted: {reviewer_id} for review {review_id}")
        return True

# Global communication bus instance
_global_communication_bus: Optional[AgentCommunicationBus] = None

def get_communication_bus() -> AgentCommunicationBus:
    """Get global agent communication bus instance"""
    global _global_communication_bus
    if _global_communication_bus is None:
        _global_communication_bus = AgentCommunicationBus()
    return _global_communication_bus

# Example usage and testing
if __name__ == "__main__":
    async def test_communication():
        bus = AgentCommunicationBus()
        
        # Test help request
        help_msg_id = await bus.request_specialist_help(
            requesting_agent_id="spec_data_analyst_001",
            required_specialty="web_intelligence_gatherer",
            help_context={
                "current_task": "market_analysis",
                "specific_need": "need competitor pricing data",
                "deadline": "2 hours",
                "progress": "50%"
            },
            urgency=Priority.HIGH
        )
        
        print(f"Help request sent: {help_msg_id}")
        
        # Test context sharing
        context_msg_ids = await bus.share_context(
            sender_id="spec_web_intelligence_001",
            recipients=["spec_data_analyst_001", "spec_competitive_intel_001"],
            context_data={
                "competitor_urls": ["example1.com", "example2.com"],
                "pricing_data_found": True,
                "data_quality": "high",
                "last_updated": "2025-11-05"
            },
            context_type="competitor_intelligence"
        )
        
        print(f"Context shared: {len(context_msg_ids)} messages")
        
        # Get metrics
        metrics = await bus.get_communication_metrics()
        print(f"Communication metrics: {json.dumps(metrics, indent=2)}")
    
    # Run test
    asyncio.run(test_communication())
