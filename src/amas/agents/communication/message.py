"""
Message Models for Agent Communication
Defines message types, priorities, and structures for inter-agent communication
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of messages that can be sent between agents"""
    
    REQUEST = "request"  # Request for action/information
    RESPONSE = "response"  # Response to a request
    EVENT = "event"  # Event notification
    BROADCAST = "broadcast"  # Broadcast to all agents
    QUERY = "query"  # Query for information
    NOTIFICATION = "notification"  # Simple notification
    COMMAND = "command"  # Command to execute


class MessagePriority(str, Enum):
    """Priority levels for messages"""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MessageStatus(str, Enum):
    """Status of a message in its lifecycle"""
    
    PENDING = "pending"  # Created but not sent
    SENT = "sent"  # Sent to recipient
    DELIVERED = "delivered"  # Delivered to recipient
    PROCESSED = "processed"  # Processed by recipient
    FAILED = "failed"  # Failed to deliver/process
    TIMEOUT = "timeout"  # Request timed out
    ACKNOWLEDGED = "acknowledged"  # Acknowledged by recipient


class AgentMessage(BaseModel):
    """
    Message structure for inter-agent communication
    
    Attributes:
        id: Unique message identifier
        sender: Agent ID of sender
        receiver: Agent ID of receiver (None for broadcast)
        type: Type of message
        priority: Priority level
        payload: Message data/content
        metadata: Additional metadata
        status: Current message status
        created_at: Timestamp when message was created
        sent_at: Timestamp when message was sent
        delivered_at: Timestamp when message was delivered
        processed_at: Timestamp when message was processed
        correlation_id: ID to correlate request/response
        reply_to: Message ID this is replying to
        timeout: Timeout in seconds for requests
        retry_count: Number of retry attempts
    """
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    receiver: Optional[str] = None  # None for broadcast
    type: MessageType
    priority: MessagePriority = MessagePriority.NORMAL
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: MessageStatus = MessageStatus.PENDING
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    # Request-response correlation
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    
    # Timeout and retry
    timeout: Optional[float] = None  # seconds
    retry_count: int = 0
    max_retries: int = 3
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
    
    def to_json(self) -> str:
        """Serialize message to JSON string"""
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> "AgentMessage":
        """Deserialize message from JSON string"""
        return cls.model_validate_json(json_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary"""
        return cls.model_validate(data)
    
    def mark_sent(self) -> None:
        """Mark message as sent"""
        self.status = MessageStatus.SENT
        self.sent_at = datetime.utcnow()
    
    def mark_delivered(self) -> None:
        """Mark message as delivered"""
        self.status = MessageStatus.DELIVERED
        self.delivered_at = datetime.utcnow()
    
    def mark_processed(self) -> None:
        """Mark message as processed"""
        self.status = MessageStatus.PROCESSED
        self.processed_at = datetime.utcnow()
    
    def mark_failed(self) -> None:
        """Mark message as failed"""
        self.status = MessageStatus.FAILED
    
    def mark_acknowledged(self) -> None:
        """Mark message as acknowledged"""
        self.status = MessageStatus.ACKNOWLEDGED
    
    def increment_retry(self) -> bool:
        """
        Increment retry count
        
        Returns:
            True if retry should be attempted, False if max retries reached
        """
        self.retry_count += 1
        return self.retry_count <= self.max_retries
    
    def is_request(self) -> bool:
        """Check if message is a request"""
        return self.type == MessageType.REQUEST
    
    def is_response(self) -> bool:
        """Check if message is a response"""
        return self.type == MessageType.RESPONSE
    
    def is_broadcast(self) -> bool:
        """Check if message is a broadcast"""
        return self.type == MessageType.BROADCAST
    
    def create_response(
        self,
        sender: str,
        payload: Dict[str, Any],
        status: MessageStatus = MessageStatus.PROCESSED
    ) -> "AgentMessage":
        """
        Create a response message to this message
        
        Args:
            sender: ID of the responding agent
            payload: Response payload
            status: Status of the response
            
        Returns:
            New AgentMessage as response
        """
        return AgentMessage(
            sender=sender,
            receiver=self.sender,
            type=MessageType.RESPONSE,
            priority=self.priority,
            payload=payload,
            status=status,
            correlation_id=self.correlation_id or self.id,
            reply_to=self.id,
        )
    
    def __repr__(self) -> str:
        return (
            f"AgentMessage(id={self.id[:8]}..., "
            f"sender={self.sender}, receiver={self.receiver}, "
            f"type={self.type}, status={self.status})"
        )


def create_request_message(
    sender: str,
    receiver: str,
    payload: Dict[str, Any],
    priority: MessagePriority = MessagePriority.NORMAL,
    timeout: Optional[float] = 30.0,
    correlation_id: Optional[str] = None,
) -> AgentMessage:
    """
    Helper function to create a request message
    
    Args:
        sender: Agent ID of sender
        receiver: Agent ID of receiver
        payload: Request payload
        priority: Message priority
        timeout: Timeout in seconds
        correlation_id: Correlation ID for tracking
        
    Returns:
        AgentMessage configured as request
    """
    return AgentMessage(
        sender=sender,
        receiver=receiver,
        type=MessageType.REQUEST,
        priority=priority,
        payload=payload,
        timeout=timeout,
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_broadcast_message(
    sender: str,
    payload: Dict[str, Any],
    priority: MessagePriority = MessagePriority.NORMAL,
) -> AgentMessage:
    """
    Helper function to create a broadcast message
    
    Args:
        sender: Agent ID of sender
        payload: Broadcast payload
        priority: Message priority
        
    Returns:
        AgentMessage configured as broadcast
    """
    return AgentMessage(
        sender=sender,
        receiver=None,
        type=MessageType.BROADCAST,
        priority=priority,
        payload=payload,
    )


def create_event_message(
    sender: str,
    event_type: str,
    event_data: Dict[str, Any],
    priority: MessagePriority = MessagePriority.NORMAL,
) -> AgentMessage:
    """
    Helper function to create an event message
    
    Args:
        sender: Agent ID of sender
        event_type: Type of event
        event_data: Event data
        priority: Message priority
        
    Returns:
        AgentMessage configured as event
    """
    return AgentMessage(
        sender=sender,
        receiver=None,
        type=MessageType.EVENT,
        priority=priority,
        payload={"event_type": event_type, "data": event_data},
    )

