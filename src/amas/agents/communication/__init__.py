"""
Agent Communication Module
Provides communication primitives for agent collaboration
"""

from src.amas.agents.communication.message import (
    MessageType,
    MessagePriority,
    MessageStatus,
    AgentMessage,
)

from src.amas.agents.communication.event_bus import (
    EventBus,
    get_event_bus,
)

from src.amas.agents.communication.context import (
    SharedContext,
    get_shared_context,
)

from src.amas.agents.communication.protocol import (
    AgentCommunicationProtocol,
    get_communication_protocol,
)

from src.amas.agents.communication.collaboration import (
    CollaborationPattern,
    CollaborationManager,
    get_collaboration_manager,
)

__all__ = [
    # Message types
    "MessageType",
    "MessagePriority",
    "MessageStatus",
    "AgentMessage",
    # Event Bus
    "EventBus",
    "get_event_bus",
    # Shared Context
    "SharedContext",
    "get_shared_context",
    # Communication Protocol
    "AgentCommunicationProtocol",
    "get_communication_protocol",
    # Collaboration
    "CollaborationPattern",
    "CollaborationManager",
    "get_collaboration_manager",
]

