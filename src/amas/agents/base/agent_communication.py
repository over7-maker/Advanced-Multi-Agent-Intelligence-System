"""
Agent Communication Module

This module handles inter-agent communication and coordination.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AgentCommunication:
    """Handles communication between agents"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue: List[Dict[str, Any]] = []
        
    async def publish(self, event_type: str, data: Dict[str, Any]):
        """Publish an event to subscribers"""
        try:
            message = {
                'event_type': event_type,
                'data': data,
                'sender': self.agent_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.message_queue.append(message)
            
            if event_type in self.subscribers:
                for handler in self.subscribers[event_type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type}: {e}")
                        
            logger.info(f"Published event {event_type} from {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {e}")
    
    async def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.info(f"Agent {self.agent_id} subscribed to {event_type}")
    
    async def send_message(self, target_agent: str, message: Dict[str, Any]):
        """Send a direct message to another agent"""
        try:
            direct_message = {
                'target_agent': target_agent,
                'sender': self.agent_id,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.message_queue.append(direct_message)
            logger.info(f"Sent message to {target_agent} from {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Error sending message to {target_agent}: {e}")
    
    async def get_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent messages"""
        return self.message_queue[-limit:]
    
    async def clear_messages(self):
        """Clear message queue"""
        self.message_queue.clear()
        logger.info(f"Cleared message queue for {self.agent_id}")