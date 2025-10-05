"""
AMAS Agent Orchestrator
Core ReAct engine for multi-agent intelligence operations
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent types for intelligence operations"""

    OSINT = "osint"
    INVESTIGATION = "investigation"
    FORENSICS = "forensics"
    DATA_ANALYSIS = "data_analysis"
    REVERSE_ENGINEERING = "reverse_engineering"
    METADATA = "metadata"
    REPORTING = "reporting"
    TECHNOLOGY_MONITOR = "technology_monitor"


class TaskStatus(Enum):
    """Task status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Task data structure"""

    id: str
    type: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    assigned_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class Agent:
    """Agent data structure"""

    id: str
    name: str
    type: AgentType
    capabilities: List[str]
    status: str = "idle"
    current_task: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all intelligence agents"""

    def __init__(self, agent_id: str, name: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.status = "idle"
        self.current_task = None
        self.capabilities = []

    @abstractmethod
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task and return results"""
        pass

    @abstractmethod
    async def can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle the given task"""
        pass

    async def update_status(self, status: str):
        """Update agent status"""
        self.status = status
        logger.info(f"Agent {self.name} status updated to {status}")


class AgentOrchestrator:
    """Core orchestrator for multi-agent intelligence operations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.event_bus = EventBus()
        self.llm_service = LLMService(
            config.get("llm_service_url", "http://localhost:11434")
        )
        self.vector_service = VectorService(
            config.get("vector_service_url", "http://localhost:8001")
        )
        self.knowledge_graph = KnowledgeGraph(
            config.get("graph_service_url", "http://localhost:7474")
        )

    async def register_agent(self, agent: BaseAgent):
        """Register a new agent"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Agent {agent.name} registered with ID {agent.agent_id}")

    async def submit_task(self, task_data: Dict[str, Any]) -> str:
        """Submit a new task to the orchestrator"""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            type=task_data.get("type", "general"),
            description=task_data.get("description", ""),
            priority=TaskPriority(task_data.get("priority", 2)),
            metadata=task_data.get("metadata", {}),
        )

        self.tasks[task_id] = task
        self.task_queue.append(task_id)

        # Sort tasks by priority
        self.task_queue.sort(
            key=lambda tid: self.tasks[tid].priority.value, reverse=True
        )

        logger.info(f"Task {task_id} submitted: {task.description}")
        await self.event_bus.publish(
            "task_submitted", {"task_id": task_id, "task": task}
        )

        return task_id

    async def assign_task_to_agent(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to a specific agent"""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False

        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return False

        task = self.tasks[task_id]
        agent = self.agents[agent_id]

        # Check if agent can handle the task
        if not await agent.can_handle_task(task):
            logger.error(f"Agent {agent_id} cannot handle task {task_id}")
            return False

        # Assign task
        task.assigned_agent = agent_id
        task.status = TaskStatus.IN_PROGRESS
        agent.current_task = task_id
        agent.status = "busy"

        logger.info(f"Task {task_id} assigned to agent {agent_id}")
        await self.event_bus.publish(
            "task_assigned", {"task_id": task_id, "agent_id": agent_id}
        )

        return True

    async def execute_react_cycle(self, task_id: str) -> List[Dict[str, Any]]:
        """Execute ReAct (Reasoning-Acting-Observing) cycle for a task"""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return []

        task = self.tasks[task_id]
        if not task.assigned_agent:
            logger.error(f"Task {task_id} not assigned to any agent")
            return []

        agent = self.agents[task.assigned_agent]
        steps = []

        try:
            # Reasoning phase
            reasoning_prompt = f"""
            You are an intelligence agent tasked with: {task.description}

            Current context:
            - Task type: {task.type}
            - Priority: {task.priority.name}
            - Available data sources: {list(self.config.get('data_sources', []))}

            Please reason about the best approach to complete this task.
            Consider:
            1. What information do you need?
            2. What actions should you take?
            3. What are the potential risks or challenges?
            4. How will you validate your results?

            Provide a step-by-step plan.
            """

            reasoning = await self.llm_service.generate_response(reasoning_prompt)
            steps.append(
                {
                    "phase": "reasoning",
                    "content": reasoning,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Acting phase
            action_prompt = f"""
            Based on your reasoning, execute the following actions:

            {reasoning}

            For each action:
            1. Describe what you're doing
            2. Execute the action
            3. Record the results
            4. Assess if more information is needed

            Be specific and actionable.
            """

            actions = await self.llm_service.generate_response(action_prompt)
            steps.append(
                {
                    "phase": "acting",
                    "content": actions,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Observing phase
            observation_prompt = f"""
            Review the results of your actions:

            {actions}

            Analyze:
            1. What did you learn?
            2. Are there any gaps in your understanding?
            3. Do you need to take additional actions?
            4. What conclusions can you draw?

            Provide a comprehensive analysis.
            """

            observations = await self.llm_service.generate_response(observation_prompt)
            steps.append(
                {
                    "phase": "observing",
                    "content": observations,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Execute the actual task
            result = await agent.execute_task(task)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.now()

            steps.append(
                {
                    "phase": "completion",
                    "content": f"Task completed successfully. Result: {result}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info(f"Task {task_id} completed successfully")
            await self.event_bus.publish(
                "task_completed", {"task_id": task_id, "result": result}
            )

        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.updated_at = datetime.now()

            steps.append(
                {
                    "phase": "error",
                    "content": f"Task failed with error: {e}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            await self.event_bus.publish(
                "task_failed", {"task_id": task_id, "error": str(e)}
            )

        finally:
            # Reset agent status
            agent.status = "idle"
            agent.current_task = None

        return steps

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        return {
            "id": task.id,
            "type": task.type,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_agent": task.assigned_agent,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "result": task.result,
            "error": task.error,
        }

    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific agent"""
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]
        return {
            "id": agent.agent_id,
            "name": agent.name,
            "type": agent.agent_type.value,
            "status": agent.status,
            "current_task": agent.current_task,
            "capabilities": agent.capabilities,
            "created_at": agent.created_at.isoformat(),
        }

    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [
            await self.get_agent_status(agent_id) for agent_id in self.agents.keys()
        ]

    async def list_tasks(
        self, status_filter: Optional[TaskStatus] = None
    ) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered by status"""
        tasks = []
        for task in self.tasks.values():
            if status_filter is None or task.status == status_filter:
                tasks.append(await self.get_task_status(task.id))
        return tasks


class EventBus:
    """Event bus for inter-agent communication"""

    def __init__(self):
        self.subscribers = {}

    async def publish(self, event_type: str, data: Dict[str, Any]):
        """Publish an event"""
        logger.info(f"Publishing event {event_type}: {data}")
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")

    async def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed to event {event_type}")


class LLMService:
    """LLM service for AI operations"""

    def __init__(self, service_url: str):
        self.service_url = service_url

    async def generate_response(self, prompt: str) -> str:
        """Generate a response using the LLM service"""
        # This would integrate with Ollama or other LLM services
        # For now, return a placeholder
        return f"LLM Response to: {prompt[:100]}..."


class VectorService:
    """Vector service for semantic search"""

    def __init__(self, service_url: str):
        self.service_url = service_url

    async def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        # This would integrate with FAISS or other vector services
        return []


class KnowledgeGraph:
    """Knowledge graph service"""

    def __init__(self, service_url: str):
        self.service_url = service_url

    async def query(self, cypher_query: str) -> List[Dict[str, Any]]:
        """Execute a Cypher query on the knowledge graph"""
        # This would integrate with Neo4j
        return []
