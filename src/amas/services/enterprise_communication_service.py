"""
Enterprise-Grade Communication Service for AMAS Intelligence System
Provides advanced message queuing, routing, and coordination protocols
"""

import asyncio

# import hashlib
import json
import logging
from json import JSONDecodeError

# import uuid
import zlib

# from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, cast

import aioredis

# import time


# import redis

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Message type enumeration"""

    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    AGENT_COORDINATION = "agent_coordination"
    SYSTEM_EVENT = "system_event"
    HEARTBEAT = "heartbeat"
    BROADCAST = "broadcast"
    PRIORITY_ALERT = "priority_alert"


class MessagePriority(Enum):
    """Message priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class RoutingStrategy(Enum):
    """Message routing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    AFFINITY_BASED = "affinity_based"
    GEOGRAPHIC = "geographic"
    CAPABILITY_BASED = "capability_based"


@dataclass
class Message:
    """Message data structure"""

    id: str
    type: MessageType
    priority: MessagePriority
    sender: str
    recipient: Optional[str]
    content: Dict[str, Any]
    timestamp: datetime
    ttl: Optional[int] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    compressed: bool = False


@dataclass
class AgentCapability:
    """Agent capability definition"""

    agent_id: str
    capabilities: List[str]
    load_factor: float
    last_heartbeat: datetime
    status: str = "active"


@dataclass
class MessageQueue:
    """Message queue configuration"""

    name: str
    priority: MessagePriority
    max_size: int
    ttl: int
    routing_strategy: RoutingStrategy
    consumers: List[str] = field(default_factory=list)


class EnterpriseCommunicationService:
    """
    Enterprise-Grade Communication Service for AMAS Intelligence System

    Provides:
    - Advanced message queuing with Redis
    - Intelligent routing and load balancing
    - Message compression and optimization
    - Dead letter queues and retry mechanisms
    - Agent coordination and discovery
    - Message persistence and replay
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the enterprise communication service"""
        self.config = config
        self.redis_client = None
        self.message_queues = {}
        self.agent_capabilities = {}
        self.message_handlers = {}
        self.routing_engines = {}

        # Message processing
        self.processing_tasks = []
        self.message_stats = {
            "sent": 0,
            "received": 0,
            "processed": 0,
            "failed": 0,
            "retried": 0,
        }

        # Compression settings
        self.compression_threshold = config.get("compression_threshold", 1024)  # bytes
        self.compression_level = config.get("compression_level", 6)

        # Queue configuration
        self.queue_config = {
            "default_ttl": config.get("default_ttl", 3600),
            "max_retries": config.get("max_retries", 3),
            "batch_size": config.get("batch_size", 100),
            "processing_timeout": config.get("processing_timeout", 30),
        }

        logger.info("Enterprise communication service initialized")

    async def initialize(self):
        """Initialize the enterprise communication service"""
        try:
            logger.info("Initializing enterprise communication service...")

            # Initialize Redis connection
            await self._initialize_redis()

            # Initialize message queues
            await self._initialize_queues()

            # Initialize routing engines
            await self._initialize_routing_engines()

            # Start message processing
            await self._start_message_processing()

            # Start agent discovery
            await self._start_agent_discovery()

            logger.info("Enterprise communication service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize enterprise communication service: {e}")
            raise

    async def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            redis_config = self.config.get("redis", {})

            self.redis_client = aioredis.from_url(
                redis_config.get("url", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=False,  # We'll handle binary data
                max_connections=redis_config.get("max_connections", 20),
            )

            # Test connection
            await self.redis_client.ping()

            logger.info("Redis connection established")

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def _initialize_queues(self):
        """Initialize message queues"""
        try:
            # Define standard queues
            queue_definitions = [
                MessageQueue(
                    name="task_requests",
                    priority=MessagePriority.NORMAL,
                    max_size=10000,
                    ttl=3600,
                    routing_strategy=RoutingStrategy.CAPABILITY_BASED,
                ),
                MessageQueue(
                    name="task_responses",
                    priority=MessagePriority.NORMAL,
                    max_size=10000,
                    ttl=3600,
                    routing_strategy=RoutingStrategy.ROUND_ROBIN,
                ),
                MessageQueue(
                    name="agent_coordination",
                    priority=MessagePriority.HIGH,
                    max_size=5000,
                    ttl=1800,
                    routing_strategy=RoutingStrategy.BROADCAST,
                ),
                MessageQueue(
                    name="system_events",
                    priority=MessagePriority.HIGH,
                    max_size=5000,
                    ttl=7200,
                    routing_strategy=RoutingStrategy.BROADCAST,
                ),
                MessageQueue(
                    name="priority_alerts",
                    priority=MessagePriority.EMERGENCY,
                    max_size=1000,
                    ttl=300,
                    routing_strategy=RoutingStrategy.BROADCAST,
                ),
                MessageQueue(
                    name="heartbeats",
                    priority=MessagePriority.LOW,
                    max_size=1000,
                    ttl=60,
                    routing_strategy=RoutingStrategy.ROUND_ROBIN,
                ),
            ]

            for queue_def in queue_definitions:
                self.message_queues[queue_def.name] = queue_def

            logger.info(f"Initialized {len(queue_definitions)} message queues")

        except Exception as e:
            logger.error(f"Failed to initialize queues: {e}")
            raise

    async def _initialize_routing_engines(self):
        """Initialize routing engines"""
        try:
            self.routing_engines = {
                RoutingStrategy.ROUND_ROBIN: self._round_robin_routing,
                RoutingStrategy.LEAST_LOADED: self._least_loaded_routing,
                RoutingStrategy.AFFINITY_BASED: self._affinity_based_routing,
                RoutingStrategy.CAPABILITY_BASED: self._capability_based_routing,
                RoutingStrategy.BROADCAST: self._broadcast_routing,
            }

            logger.info("Routing engines initialized")

        except Exception as e:
            logger.error(f"Failed to initialize routing engines: {e}")
            raise

    async def _start_message_processing(self):
        """Start message processing tasks"""
        try:
            # Start processing tasks for each queue
            for queue_name in self.message_queues.keys():
                task = asyncio.create_task(self._process_queue(queue_name))
                self.processing_tasks.append(task)

            logger.info("Message processing tasks started")

        except Exception as e:
            logger.error(f"Failed to start message processing: {e}")
            raise

    async def _start_agent_discovery(self):
        """Start agent discovery and heartbeat monitoring"""
        try:
            # Start heartbeat monitoring
            heartbeat_task = asyncio.create_task(self._monitor_agent_heartbeats())
            self.processing_tasks.append(heartbeat_task)

            # Start capability updates
            capability_task = asyncio.create_task(self._update_agent_capabilities())
            self.processing_tasks.append(capability_task)

            logger.info("Agent discovery tasks started")

        except Exception as e:
            logger.error(f"Failed to start agent discovery: {e}")
            raise

    async def send_message(self, message: Message, queue_name: str = None) -> bool:
        """Send a message to a queue"""
        try:
            # Determine queue if not specified
            if not queue_name:
                queue_name = self._determine_queue(message.type)

            if queue_name not in self.message_queues:
                logger.error(f"Queue {queue_name} not found")
                return False

            # Compress message if needed
            if self._should_compress(message):
                message = await self._compress_message(message)

            # Serialize message
            message_data = await self._serialize_message(message)

            # Add to queue with priority
            queue_key = f"queue:{queue_name}"
            priority_score = self._calculate_priority_score(message)

            await self.redis_client.zadd(queue_key, {message_data: priority_score})

            # Set TTL
            if message.ttl:
                await self.redis_client.expire(queue_key, message.ttl)

            # Update stats
            self.message_stats["sent"] += 1

            logger.debug(f"Message {message.id} sent to queue {queue_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.message_stats["failed"] += 1
            return False

    async def receive_message(
        self, queue_name: str, timeout: int = 30
    ) -> Optional[Message]:
        """Receive a message from a queue"""
        try:
            queue_key = f"queue:{queue_name}"

            # Get message with highest priority
            result = await self.redis_client.bzpopmax(queue_key, timeout=timeout)

            if not result:
                return None

            _, message_data = result
            message = await self._deserialize_message(message_data)

            # Update stats
            self.message_stats["received"] += 1

            logger.debug(f"Message {message.id} received from queue {queue_name}")
            return message

        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            return None

    async def broadcast_message(
        self, message: Message, target_agents: List[str] = None
    ) -> int:
        """Broadcast a message to multiple agents"""
        try:
            if not target_agents:
                target_agents = list(self.agent_capabilities.keys())

            sent_count = 0

            for agent_id in target_agents:
                if agent_id in self.agent_capabilities:
                    # Create individual message for each agent
                    individual_message = Message(
                        id=f"{message.id}_{agent_id}",
                        type=message.type,
                        priority=message.priority,
                        sender=message.sender,
                        recipient=agent_id,
                        content=message.content,
                        timestamp=message.timestamp,
                        ttl=message.ttl,
                        correlation_id=message.correlation_id,
                        reply_to=message.reply_to,
                        headers=message.headers.copy(),
                    )

                    # Send to agent's personal queue
                    agent_queue = f"agent:{agent_id}"
                    if await self.send_message(individual_message, agent_queue):
                        sent_count += 1

            logger.info(f"Broadcast message {message.id} sent to {sent_count} agents")
            return sent_count

        except Exception as e:
            logger.error(f"Failed to broadcast message: {e}")
            return 0

    async def register_agent(self, agent_id: str, capabilities: List[str]) -> bool:
        """Register an agent with its capabilities"""
        try:
            capability = AgentCapability(
                agent_id=agent_id,
                capabilities=capabilities,
                load_factor=0.0,
                last_heartbeat=datetime.utcnow(),
                status="active",
            )

            self.agent_capabilities[agent_id] = capability

            # Store in Redis for persistence
            capability_data = {
                "capabilities": capabilities,
                "load_factor": 0.0,
                "last_heartbeat": datetime.utcnow().isoformat(),
                "status": "active",
            }

            await self.redis_client.hset(f"agent:{agent_id}", mapping=capability_data)

            logger.info(
                f"Agent {agent_id} registered with capabilities: {capabilities}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False

    async def update_agent_heartbeat(
        self, agent_id: str, load_factor: float = None
    ) -> bool:
        """Update agent heartbeat and load factor"""
        try:
            if agent_id not in self.agent_capabilities:
                logger.warning(f"Agent {agent_id} not registered")
                return False

            capability = self.agent_capabilities[agent_id]
            capability.last_heartbeat = datetime.utcnow()

            if load_factor is not None:
                capability.load_factor = load_factor

            # Update in Redis
            await self.redis_client.hset(
                f"agent:{agent_id}",
                "last_heartbeat",
                capability.last_heartbeat.isoformat(),
            )

            if load_factor is not None:
                await self.redis_client.hset(
                    f"agent:{agent_id}", "load_factor", load_factor
                )

            return True

        except Exception as e:
            logger.error(f"Failed to update heartbeat for agent {agent_id}: {e}")
            return False

    async def _process_queue(self, queue_name: str):
        """Process messages from a queue"""
        try:
            # queue_config = self.message_queues[queue_name]

            while True:
                try:
                    # Get message from queue
                    message = await self.receive_message(queue_name, timeout=1)

                    if not message:
                        continue

                    # Process message
                    await self._process_message(message, queue_name)

                except Exception as e:
                    logger.error(f"Error processing queue {queue_name}: {e}")
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Queue processing failed for {queue_name}: {e}")

    async def _process_message(self, message: Message, queue_name: str):
        """Process a single message"""
        try:
            # Check if message has expired
            if (
                message.ttl
                and (datetime.utcnow() - message.timestamp).seconds > message.ttl
            ):
                logger.warning(f"Message {message.id} expired")
                return

            # Decompress if needed
            if message.compressed:
                message = await self._decompress_message(message)

            # Route message
            target_agent = await self._route_message(message, queue_name)

            if target_agent:
                # Send to target agent
                agent_queue = f"agent:{target_agent}"
                await self.send_message(message, agent_queue)

                # Update stats
                self.message_stats["processed"] += 1

                logger.debug(f"Message {message.id} routed to agent {target_agent}")
            else:
                # No suitable agent found, retry or dead letter
                await self._handle_message_routing_failure(message, queue_name)

        except Exception as e:
            logger.error(f"Failed to process message {message.id}: {e}")
            await self._handle_message_processing_error(message, queue_name)

    async def _route_message(self, message: Message, queue_name: str) -> Optional[str]:
        """Route message to appropriate agent"""
        try:
            queue_config = self.message_queues[queue_name]
            routing_strategy = queue_config.routing_strategy

            if routing_strategy in self.routing_engines:
                return await self.routing_engines[routing_strategy](
                    message, queue_config
                )
            else:
                logger.error(f"Unknown routing strategy: {routing_strategy}")
                return None

        except Exception as e:
            logger.error(f"Failed to route message: {e}")
            return None

    async def _round_robin_routing(
        self, message: Message, queue_config: MessageQueue
    ) -> Optional[str]:
        """Round robin routing strategy"""
        try:
            active_agents = [
                agent_id
                for agent_id, capability in self.agent_capabilities.items()
                if capability.status == "active"
            ]

            if not active_agents:
                return None

            # Simple round robin
            index = hash(message.id) % len(active_agents)
            return active_agents[index]

        except Exception as e:
            logger.error(f"Round robin routing failed: {e}")
            return None

    async def _least_loaded_routing(
        self, message: Message, queue_config: MessageQueue
    ) -> Optional[str]:
        """Least loaded routing strategy"""
        try:
            active_agents = [
                (agent_id, capability.load_factor)
                for agent_id, capability in self.agent_capabilities.items()
                if capability.status == "active"
            ]

            if not active_agents:
                return None

            # Select agent with lowest load
            agent_id, _ = min(active_agents, key=lambda x: x[1])
            return agent_id

        except Exception as e:
            logger.error(f"Least loaded routing failed: {e}")
            return None

    async def _affinity_based_routing(
        self, message: Message, queue_config: MessageQueue
    ) -> Optional[str]:
        """Affinity-based routing strategy"""
        try:
            # Route to same agent if correlation_id exists
            if message.correlation_id:
                correlation_key = f"correlation:{message.correlation_id}"
                previous_agent = await self.redis_client.get(correlation_key)

                if previous_agent:
                    previous_agent = previous_agent.decode("utf-8")
                    if previous_agent in self.agent_capabilities:
                        return previous_agent

            # Fallback to least loaded
            return await self._least_loaded_routing(message, queue_config)

        except Exception as e:
            logger.error(f"Affinity-based routing failed: {e}")
            return None

    async def _capability_based_routing(
        self, message: Message, queue_config: MessageQueue
    ) -> Optional[str]:
        """Capability-based routing strategy"""
        try:
            # Extract required capabilities from message
            required_capabilities = message.content.get("required_capabilities", [])

            if not required_capabilities:
                # Fallback to least loaded
                return await self._least_loaded_routing(message, queue_config)

            # Find agents with required capabilities
            suitable_agents = []
            for agent_id, capability in self.agent_capabilities.items():
                if capability.status == "active":
                    if all(
                        cap in capability.capabilities for cap in required_capabilities
                    ):
                        suitable_agents.append((agent_id, capability.load_factor))

            if not suitable_agents:
                return None

            # Select least loaded suitable agent
            agent_id, _ = min(suitable_agents, key=lambda x: x[1])
            return agent_id

        except Exception as e:
            logger.error(f"Capability-based routing failed: {e}")
            return None

    async def _broadcast_routing(
        self, message: Message, queue_config: MessageQueue
    ) -> Optional[str]:
        """Broadcast routing strategy - returns None to indicate broadcast"""
        return None

    async def _monitor_agent_heartbeats(self):
        """Monitor agent heartbeats and mark inactive agents"""
        while True:
            try:
                current_time = datetime.utcnow()
                inactive_threshold = timedelta(minutes=5)

                inactive_agents = []
                for agent_id, capability in self.agent_capabilities.items():
                    if current_time - capability.last_heartbeat > inactive_threshold:
                        capability.status = "inactive"
                        inactive_agents.append(agent_id)

                if inactive_agents:
                    logger.warning(f"Inactive agents detected: {inactive_agents}")

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Heartbeat monitoring error: {e}")
                await asyncio.sleep(60)

    async def _update_agent_capabilities(self):
        """Update agent capabilities from Redis"""
        while True:
            try:
                # Load agent capabilities from Redis
                agent_keys = await self.redis_client.keys("agent:*")

                for key in agent_keys:
                    agent_id = key.decode("utf-8").replace("agent:", "")

                    if agent_id not in self.agent_capabilities:
                        # Load from Redis
                        capability_data = await self.redis_client.hgetall(key)

                        if capability_data:
                            capability = AgentCapability(
                                agent_id=agent_id,
                                capabilities=json.loads(
                                    capability_data.get(b"capabilities", b"[]")
                                ),
                                load_factor=float(
                                    capability_data.get(b"load_factor", b"0.0")
                                ),
                                last_heartbeat=datetime.fromisoformat(
                                    capability_data.get(b"last_heartbeat", b"").decode(
                                        "utf-8"
                                    )
                                ),
                                status=capability_data.get(b"status", b"active").decode(
                                    "utf-8"
                                ),
                            )

                            self.agent_capabilities[agent_id] = capability

                await asyncio.sleep(60)  # Update every minute

            except Exception as e:
                logger.error(f"Capability update error: {e}")
                await asyncio.sleep(60)

    def _determine_queue(self, message_type: MessageType) -> str:
        """Determine appropriate queue for message type"""
        queue_mapping = {
            MessageType.TASK_REQUEST: "task_requests",
            MessageType.TASK_RESPONSE: "task_responses",
            MessageType.AGENT_COORDINATION: "agent_coordination",
            MessageType.SYSTEM_EVENT: "system_events",
            MessageType.HEARTBEAT: "heartbeats",
            MessageType.PRIORITY_ALERT: "priority_alerts",
            MessageType.BROADCAST: "agent_coordination",
        }

        return queue_mapping.get(message_type, "task_requests")

    def _should_compress(self, message: Message) -> bool:
        """Determine if message should be compressed"""
        message_size = len(json.dumps(message.content).encode("utf-8"))
        return message_size > self.compression_threshold

    async def _compress_message(self, message: Message) -> Message:
        """Compress message content"""
        try:
            # Compress content
            content_json = json.dumps(message.content)
            compressed_content = zlib.compress(
                content_json.encode("utf-8"), level=self.compression_level
            )

            # Create new message with compressed content
            compressed_message = Message(
                id=message.id,
                type=message.type,
                priority=message.priority,
                sender=message.sender,
                recipient=message.recipient,
                content={"compressed_data": compressed_content.hex()},
                timestamp=message.timestamp,
                ttl=message.ttl,
                correlation_id=message.correlation_id,
                reply_to=message.reply_to,
                headers=message.headers,
                retry_count=message.retry_count,
                max_retries=message.max_retries,
                compressed=True,
            )

            return compressed_message

        except Exception as e:
            logger.error(f"Failed to compress message: {e}")
            return message

    async def _decompress_message(self, message: Message) -> Message:
        """Decompress message content"""
        try:
            if not message.compressed:
                return message

            # Decompress content
            compressed_data = bytes.fromhex(message.content["compressed_data"])
            decompressed_content = zlib.decompress(compressed_data)
            original_content = json.loads(decompressed_content.decode("utf-8"))

            # Create new message with decompressed content
            decompressed_message = Message(
                id=message.id,
                type=message.type,
                priority=message.priority,
                sender=message.sender,
                recipient=message.recipient,
                content=original_content,
                timestamp=message.timestamp,
                ttl=message.ttl,
                correlation_id=message.correlation_id,
                reply_to=message.reply_to,
                headers=message.headers,
                retry_count=message.retry_count,
                max_retries=message.max_retries,
                compressed=False,
            )

            return decompressed_message

        except Exception as e:
            logger.error(f"Failed to decompress message: {e}")
            return message

    async def _serialize_message(self, message: Message) -> bytes:
        """Serialize message to bytes"""
        try:
            message_dict = {
                "id": message.id,
                "type": message.type.value,
                "priority": message.priority.value,
                "sender": message.sender,
                "recipient": message.recipient,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "ttl": message.ttl,
                "correlation_id": message.correlation_id,
                "reply_to": message.reply_to,
                "headers": message.headers,
                "retry_count": message.retry_count,
                "max_retries": message.max_retries,
                "compressed": message.compressed,
            }

            # Safe, compact JSON serialization for Redis storage
            return json.dumps(message_dict, separators=(",", ":")).encode("utf-8")

        except Exception as e:
            logger.error(f"Failed to serialize message: {e}")
            raise

    async def _deserialize_message(self, data: bytes) -> Message:
        """Deserialize message from bytes"""
        try:
            try:
                message_dict = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, JSONDecodeError) as e:
                logger.error(f"Failed to decode message JSON: {e}")
                raise

            return Message(
                id=message_dict["id"],
                type=MessageType(message_dict["type"]),
                priority=MessagePriority(message_dict["priority"]),
                sender=message_dict["sender"],
                recipient=message_dict["recipient"],
                content=message_dict["content"],
                timestamp=datetime.fromisoformat(message_dict["timestamp"]),
                ttl=message_dict["ttl"],
                correlation_id=message_dict["correlation_id"],
                reply_to=message_dict["reply_to"],
                headers=message_dict["headers"],
                retry_count=message_dict["retry_count"],
                max_retries=message_dict["max_retries"],
                compressed=message_dict["compressed"],
            )

        except Exception as e:
            logger.error(f"Failed to deserialize message: {e}")
            raise

    def _calculate_priority_score(self, message: Message) -> float:
        """Calculate priority score for message ordering"""
        # Higher priority = higher score
        base_score = message.priority.value * 1000000

        # Add timestamp for ordering within same priority
        timestamp_score = int(message.timestamp.timestamp() * 1000)

        return base_score + timestamp_score

    async def _handle_message_routing_failure(self, message: Message, queue_name: str):
        """Handle message routing failure"""
        try:
            if message.retry_count < message.max_retries:
                # Retry message
                message.retry_count += 1
                await self.send_message(message, queue_name)
                self.message_stats["retried"] += 1

                logger.warning(
                    f"Message {message.id} retried (attempt {message.retry_count})"
                )
            else:
                # Send to dead letter queue
                await self._send_to_dead_letter_queue(message, queue_name)

                logger.error(f"Message {message.id} sent to dead letter queue")

        except Exception as e:
            logger.error(
                f"Failed to handle routing failure for message {message.id}: {e}"
            )

    async def _handle_message_processing_error(self, message: Message, queue_name: str):
        """Handle message processing error"""
        try:
            # Send to error queue for manual inspection
            error_queue = f"error:{queue_name}"
            await self.send_message(message, error_queue)

            self.message_stats["failed"] += 1

            logger.error(f"Message {message.id} sent to error queue")

        except Exception as e:
            logger.error(
                f"Failed to handle processing error for message {message.id}: {e}"
            )

    async def _send_to_dead_letter_queue(self, message: Message, original_queue: str):
        """Send message to dead letter queue"""
        try:
            dead_letter_queue = f"dlq:{original_queue}"
            await self.send_message(message, dead_letter_queue)

        except Exception as e:
            logger.error(f"Failed to send message to dead letter queue: {e}")

    async def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication service statistics"""
        try:
            return {
                "message_stats": self.message_stats,
                "active_agents": len(
                    [
                        agent
                        for agent in self.agent_capabilities.values()
                        if agent.status == "active"
                    ]
                ),
                "total_agents": len(self.agent_capabilities),
                "queue_count": len(self.message_queues),
                "processing_tasks": len(self.processing_tasks),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get communication stats: {e}")
            return {"error": str(e)}

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        try:
            agent_status = {}

            for agent_id, capability in self.agent_capabilities.items():
                agent_status[agent_id] = {
                    "capabilities": capability.capabilities,
                    "load_factor": capability.load_factor,
                    "last_heartbeat": capability.last_heartbeat.isoformat(),
                    "status": capability.status,
                    "is_active": capability.status == "active",
                }

            return agent_status

        except Exception as e:
            logger.error(f"Failed to get agent status: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Shutdown communication service"""
        try:
            logger.info("Shutting down enterprise communication service...")

            # Cancel processing tasks
            for task in self.processing_tasks:
                task.cancel()

            # Wait for tasks to complete
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)

            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()

            logger.info("Enterprise communication service shutdown complete")

        except Exception as e:
            logger.error(f"Error during communication service shutdown: {e}")
