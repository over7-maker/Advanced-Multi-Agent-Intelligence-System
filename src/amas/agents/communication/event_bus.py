"""
Event Bus for Agent Communication
Implements publish-subscribe pattern for asynchronous event handling
"""

import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from src.amas.agents.communication.message import MessagePriority

logger = logging.getLogger(__name__)

# Global event bus instance
_event_bus: Optional["EventBus"] = None


class Event:
    """Event structure"""
    
    def __init__(
        self,
        event_type: str,
        data: Dict[str, Any],
        sender: Optional[str] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.event_type = event_type
        self.data = data
        self.sender = sender
        self.priority = priority
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
        self.id = f"{event_type}_{self.timestamp.timestamp()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "data": self.data,
            "sender": self.sender,
            "priority": self.priority.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create event from dictionary"""
        return cls(
            event_type=data["event_type"],
            data=data["data"],
            sender=data.get("sender"),
            priority=MessagePriority(data.get("priority", "normal")),
            metadata=data.get("metadata", {}),
        )


class EventBus:
    """
    Asynchronous Event Bus for agent communication
    
    Implements publish-subscribe pattern with:
    - Multiple subscribers per event type
    - Priority-based event queue
    - Event history (Redis-backed)
    - Event filtering
    """
    
    def __init__(self):
        # Subscribers: event_type -> set of handlers
        self._subscribers: Dict[str, Set[Callable]] = defaultdict(set)
        
        # Event history (in-memory, limited)
        self._event_history: List[Event] = []
        self._max_history = 1000
        
        # Event queue (priority-based)
        self._event_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
        # Processing flag
        self._processing = False
        self._processing_task: Optional[asyncio.Task] = None
        
        # Redis client (optional)
        self._redis_client = None
        
        # Statistics
        self._events_published = 0
        self._events_processed = 0
        
        logger.info("EventBus initialized")
    
    async def initialize(self):
        """Initialize event bus with Redis connection"""
        try:
            from src.cache.redis import get_redis_client
            self._redis_client = get_redis_client()
            logger.info("EventBus connected to Redis")
        except Exception as e:
            logger.warning(f"EventBus could not connect to Redis: {e}")
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async function to call when event occurs
        """
        self._subscribers[event_type].add(handler)
        logger.debug(f"Handler subscribed to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Unsubscribe from an event type
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].discard(handler)
            logger.debug(f"Handler unsubscribed from event type: {event_type}")
    
    def subscribe_all(self, handler: Callable) -> None:
        """
        Subscribe to all events
        
        Args:
            handler: Handler to call for all events
        """
        self._subscribers["*"].add(handler)
        logger.debug("Handler subscribed to all events")
    
    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        sender: Optional[str] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Publish an event
        
        Args:
            event_type: Type of event
            data: Event data
            sender: ID of sender agent
            priority: Event priority
            metadata: Additional metadata
        """
        event = Event(
            event_type=event_type,
            data=data,
            sender=sender,
            priority=priority,
            metadata=metadata,
        )
        
        # Add to event history
        self._add_to_history(event)
        
        # Store in Redis if available
        await self._store_in_redis(event)
        
        # Add to priority queue
        # Lower priority value = higher priority in queue
        priority_value = self._get_priority_value(priority)
        await self._event_queue.put((priority_value, event))
        
        self._events_published += 1
        
        # Start processing if not already running
        if not self._processing:
            await self.start_processing()
        
        logger.debug(f"Event published: {event_type} from {sender}")
    
    async def start_processing(self) -> None:
        """Start processing events from queue"""
        if self._processing:
            return
        
        self._processing = True
        self._processing_task = asyncio.create_task(self._process_events())
        logger.info("EventBus started processing events")
    
    async def stop_processing(self) -> None:
        """Stop processing events"""
        self._processing = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus stopped processing events")
    
    async def _process_events(self) -> None:
        """Process events from queue"""
        while self._processing:
            try:
                # Get event from queue with timeout
                try:
                    priority_value, event = await asyncio.wait_for(
                        self._event_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Notify subscribers
                await self._notify_subscribers(event)
                
                self._events_processed += 1
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)
    
    async def _notify_subscribers(self, event: Event) -> None:
        """
        Notify all subscribers of an event
        
        Args:
            event: Event to notify subscribers about
        """
        # Get specific subscribers
        handlers = self._subscribers.get(event.event_type, set()).copy()
        
        # Add wildcard subscribers
        handlers.update(self._subscribers.get("*", set()))
        
        if not handlers:
            return
        
        # Call all handlers concurrently
        tasks = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    # Wrap sync function in coroutine
                    tasks.append(asyncio.to_thread(handler, event))
            except Exception as e:
                logger.error(f"Error creating task for handler: {e}")
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Handler error for event {event.event_type}: {result}")
    
    def _add_to_history(self, event: Event) -> None:
        """Add event to history"""
        self._event_history.append(event)
        
        # Trim history if too long
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    async def _store_in_redis(self, event: Event) -> None:
        """Store event in Redis"""
        if not self._redis_client:
            return
        
        try:
            key = f"event_bus:events:{event.event_type}"
            value = json.dumps(event.to_dict())
            
            # Store with TTL (1 hour)
            await self._redis_client.lpush(key, value)
            await self._redis_client.expire(key, 3600)
            
            # Trim list to last 100 events
            await self._redis_client.ltrim(key, 0, 99)
            
        except Exception as e:
            logger.debug(f"Failed to store event in Redis: {e}")
    
    async def get_event_history(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Event]:
        """
        Get event history
        
        Args:
            event_type: Filter by event type (None for all)
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        if event_type:
            events = [e for e in self._event_history if e.event_type == event_type]
        else:
            events = self._event_history.copy()
        
        return events[-limit:]
    
    async def get_event_history_from_redis(
        self,
        event_type: str,
        limit: int = 100,
    ) -> List[Event]:
        """
        Get event history from Redis
        
        Args:
            event_type: Event type to retrieve
            limit: Maximum number of events
            
        Returns:
            List of events
        """
        if not self._redis_client:
            return []
        
        try:
            key = f"event_bus:events:{event_type}"
            values = await self._redis_client.lrange(key, 0, limit - 1)
            
            events = []
            for value in values:
                try:
                    data = json.loads(value)
                    events.append(Event.from_dict(data))
                except Exception as e:
                    logger.debug(f"Failed to parse event from Redis: {e}")
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get event history from Redis: {e}")
            return []
    
    def _get_priority_value(self, priority: MessagePriority) -> int:
        """Get numeric priority value (lower = higher priority)"""
        priority_map = {
            MessagePriority.URGENT: 0,
            MessagePriority.HIGH: 1,
            MessagePriority.NORMAL: 2,
            MessagePriority.LOW: 3,
        }
        return priority_map.get(priority, 2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            "events_published": self._events_published,
            "events_processed": self._events_processed,
            "events_pending": self._event_queue.qsize(),
            "subscribers": {
                event_type: len(handlers)
                for event_type, handlers in self._subscribers.items()
            },
            "event_history_size": len(self._event_history),
            "redis_connected": self._redis_client is not None,
        }


def get_event_bus() -> EventBus:
    """Get or create global event bus instance"""
    global _event_bus
    
    if _event_bus is None:
        _event_bus = EventBus()
    
    return _event_bus

