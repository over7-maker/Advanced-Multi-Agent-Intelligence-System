
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

class MessageBus:
    """
    A central asynchronous message bus for inter-agent communication within AMAS.

    This bus facilitates message passing between agents and the orchestrator,
    supporting both direct messages and topic-based subscriptions.
    """

    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._agent_callbacks: Dict[str, Callable] = {}
        logger.info("MessageBus initialized.")

    async def register_agent(self, agent_id: str, callback: Callable):
        """
        Registers an agent with the message bus, creating a dedicated queue for it
        and storing its callback for direct messages.
        """
        if agent_id in self._queues:
            logger.warning(f"Agent {agent_id} already registered with MessageBus.")
            return
        self._queues[agent_id] = asyncio.Queue()
        self._agent_callbacks[agent_id] = callback
        logger.info(f"Agent {agent_id} registered with MessageBus.")
        asyncio.create_task(self._process_agent_queue(agent_id))

    async def unregister_agent(self, agent_id: str):
        """
        Unregisters an agent and removes its queue and subscriptions.
        """
        if agent_id in self._queues:
            # Signal the queue processor to stop
            await self._queues[agent_id].put(None)
            del self._queues[agent_id]
            del self._agent_callbacks[agent_id]
            logger.info(f"Agent {agent_id} unregistered from MessageBus.")

        # Remove from any topic subscriptions
        for topic in list(self._subscribers.keys()):
            self._subscribers[topic] = [q for q in self._subscribers[topic] if q != self._queues.get(agent_id)]
            if not self._subscribers[topic]:
                del self._subscribers[topic]

    async def subscribe(self, agent_id: str, topic: str):
        """
        Subscribes an agent to a specific topic.
        """
        if agent_id not in self._queues:
            logger.error(f"Agent {agent_id} not registered. Cannot subscribe to topic {topic}.")
            return
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        if self._queues[agent_id] not in self._subscribers[topic]:
            self._subscribers[topic].append(self._queues[agent_id])
            logger.info(f"Agent {agent_id} subscribed to topic \'{topic}\'.")

    async def unsubscribe(self, agent_id: str, topic: str):
        """
        Unsubscribes an agent from a specific topic.
        """
        if topic in self._subscribers and agent_id in self._queues:
            queue = self._queues[agent_id]
            if queue in self._subscribers[topic]:
                self._subscribers[topic].remove(queue)
                if not self._subscribers[topic]:
                    del self._subscribers[topic]
                logger.info(f"Agent {agent_id} unsubscribed from topic \'{topic}\'.")

    async def publish(self, topic: str, message: Dict[str, Any]):
        """
        Publishes a message to all subscribers of a topic.
        """
        logger.debug(f"Publishing message to topic \'{topic}\': {message}")
        if topic in self._subscribers:
            for queue in self._subscribers[topic]:
                await queue.put(message)

    async def send_direct_message(self, recipient_id: str, message: Dict[str, Any]):
        """
        Sends a direct message to a specific agent.
        """
        logger.debug(f"Sending direct message to {recipient_id}: {message}")
        if recipient_id in self._queues:
            await self._queues[recipient_id].put(message)
        else:
            logger.warning(f"Recipient agent {recipient_id} not found. Message not delivered.")

    async def _process_agent_queue(self, agent_id: str):
        """
        Processes messages for a specific agent from its dedicated queue.
        """
        queue = self._queues[agent_id]
        callback = self._agent_callbacks[agent_id]
        logger.info(f"Starting message processing for agent {agent_id}.")
        while True:
            message = await queue.get()
            if message is None:  # Sentinel value for shutdown
                logger.info(f"Stopping message processing for agent {agent_id}.")
                break
            try:
                await callback(message)
            except Exception as e:
                logger.error(f"Error processing message for agent {agent_id}: {e}")
            finally:
                queue.task_done()

    async def close(self):
        """
        Gracefully shuts down the message bus, unregistering all agents.
        """
        logger.info("Closing MessageBus...")
        for agent_id in list(self._queues.keys()):
            await self.unregister_agent(agent_id)
        logger.info("MessageBus closed.")


