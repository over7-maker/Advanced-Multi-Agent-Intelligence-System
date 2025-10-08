"""
Intelligence Orchestrator

This module implements the central orchestrator for the AMAS Intelligence System,
managing agent coordination, task distribution, and workflow execution.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from ..agents.base.intelligence_agent import AgentStatus, IntelligenceAgent
from ..agents.data_analysis.data_analysis_agent import DataAnalysisAgent
from ..agents.forensics.forensics_agent import ForensicsAgent
from ..agents.investigation.investigation_agent import InvestigationAgent
from ..agents.metadata.metadata_agent import MetadataAgent
from ..agents.osint.osint_agent import OSINTAgent
from ..agents.reporting.reporting_agent import ReportingAgent
from ..agents.reverse_engineering.reverse_engineering_agent import (
    ReverseEngineeringAgent,
)


class TaskPriority(Enum):
    """Task priority levels"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task status enumeration"""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class IntelligenceTask:
    """Intelligence task definition"""

    id: str
    type: str
    description: str
    priority: TaskPriority
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parameters: Dict[str, Any] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.parameters is None:
            self.parameters = {}


class IntelligenceOrchestrator:
    """
    Central orchestrator for the AMAS Intelligence System.

    This orchestrator manages agent coordination, task distribution,
    and workflow execution for intelligence operations.
    """

    def __init__(
        self,
        config: Any = None,
        service_manager: Any = None,
        llm_service: Any = None,
        vector_service: Any = None,
        knowledge_graph: Any = None,
        security_service: Any = None,
    ):
        """
        Initialize the intelligence orchestrator.

        Args:
            config: AMAS configuration object
            service_manager: Service manager instance
            llm_service: LLM service for AI operations
            vector_service: Vector service for semantic search
            knowledge_graph: Knowledge graph service
            security_service: Security service for access control
        """
        self.config = config
        self.service_manager = service_manager
        self.llm_service = llm_service or (
            service_manager.get_llm_service() if service_manager else None
        )
        self.vector_service = vector_service or (
            service_manager.get_vector_service() if service_manager else None
        )
        self.knowledge_graph = knowledge_graph or (
            service_manager.get_knowledge_graph_service() if service_manager else None
        )
        self.security_service = security_service

        # Agent registry
        self.agents: Dict[str, IntelligenceAgent] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}

        # Task management
        self.tasks: Dict[str, IntelligenceTask] = {}
        self.task_queue = asyncio.PriorityQueue()
        self.active_tasks: Dict[str, IntelligenceTask] = {}

        # Workflow management
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_instances: Dict[str, Dict[str, Any]] = {}

        # Performance metrics
        self.metrics = {
            "tasks_processed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_task_time": 0.0,
            "active_agents": 0,
            "active_tasks": 0,
        }

        # Logging
        self.logger = logging.getLogger("amas.orchestrator")

        # Initialize core services
        # Note: This will be called in the initialize() method

    async def _initialize_services(self):
        """Initialize core services and agents."""
        try:
            # Initialize specialized agents
            await self._register_specialized_agents()

            # Initialize workflow templates
            self._initialize_workflow_templates()

            self.logger.info("Intelligence orchestrator initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            raise

    async def _register_specialized_agents(self):
        """Register specialized intelligence agents."""
        try:
            # OSINT Agent
            osint_agent = OSINTAgent(
                agent_id="osint_001",
                name="OSINT Collection Agent",
                llm_service=self.llm_service,
                vector_service=self.vector_service,
                knowledge_graph=self.knowledge_graph,
                security_service=self.security_service,
            )
            await self.register_agent(osint_agent)

            # Investigation Agent
            investigation_agent = InvestigationAgent(
                agent_id="investigation_001",
                name="Investigation Agent",
                llm_service=self.llm_service,
                vector_service=self.vector_service,
                knowledge_graph=self.knowledge_graph,
                security_service=self.security_service,
            )
            await self.register_agent(investigation_agent)

            # Forensics Agent
            forensics_agent = ForensicsAgent(
                agent_id="forensics_001",
                name="Forensics Agent",
                llm_service=self.llm_service,
                vector_service=self.vector_service,
                knowledge_graph=self.knowledge_graph,
                security_service=self.security_service,
            )
            await self.register_agent(forensics_agent)

            # Data Analysis Agent
            data_analysis_agent = DataAnalysisAgent(
                agent_id="data_analysis_001",
                name="Data Analysis Agent",
                llm_service=self.llm_service,
                vector_service=self.vector_service,
                knowledge_graph=self.knowledge_graph,
                security_service=self.security_service,
            )
            await self.register_agent(data_analysis_agent)

            # Reverse Engineering Agent
            reverse_engineering_agent = ReverseEngineeringAgent(
                agent_id="reverse_engineering_001",
                name="Reverse Engineering Agent",
                llm_service=self.llm_service,
                vector_service=self.vector_service,
                knowledge_graph=self.knowledge_graph,
                security_service=self.security_service,
            )
            await self.register_agent(reverse_engineering_agent)

            # Metadata Agent
            metadata_agent = MetadataAgent(
                agent_id="metadata_001",
                name="Metadata Agent",
                llm_service=self.llm_service,
                vector_service=self.vector_service,
                knowledge_graph=self.knowledge_graph,
                security_service=self.security_service,
            )
            await self.register_agent(metadata_agent)

            # Reporting Agent
            reporting_agent = ReportingAgent(
                agent_id="reporting_001",
                name="Reporting Agent",
                llm_service=self.llm_service,
                vector_service=self.vector_service,
                knowledge_graph=self.knowledge_graph,
                security_service=self.security_service,
            )
            await self.register_agent(reporting_agent)

            self.logger.info("Specialized agents registered successfully")

        except Exception as e:
            self.logger.error(f"Failed to register specialized agents: {e}")
            raise

    def _initialize_workflow_templates(self):
        """Initialize workflow templates for common intelligence operations."""
        try:
            # OSINT Investigation Workflow
            self.workflows["osint_investigation"] = {
                "name": "OSINT Investigation Workflow",
                "description": "Comprehensive OSINT investigation workflow",
                "steps": [
                    {
                        "step_id": "osint_collection",
                        "agent_type": "osint",
                        "action": "collect_data",
                        "parameters": {"sources": [], "keywords": [], "filters": {}},
                    },
                    {
                        "step_id": "data_analysis",
                        "agent_type": "data_analysis",
                        "action": "analyze_data",
                        "parameters": {"analysis_type": "correlation", "entities": []},
                    },
                    {
                        "step_id": "investigation",
                        "agent_type": "investigation",
                        "action": "investigate_entities",
                        "parameters": {"entities": [], "depth": "deep"},
                    },
                    {
                        "step_id": "reporting",
                        "agent_type": "reporting",
                        "action": "generate_report",
                        "parameters": {
                            "report_type": "intelligence_report",
                            "format": "comprehensive",
                        },
                    },
                ],
            }

            # Digital Forensics Workflow
            self.workflows["digital_forensics"] = {
                "name": "Digital Forensics Workflow",
                "description": "Digital forensics investigation workflow",
                "steps": [
                    {
                        "step_id": "evidence_acquisition",
                        "agent_type": "forensics",
                        "action": "acquire_evidence",
                        "parameters": {"source": "", "acquisition_type": "forensic"},
                    },
                    {
                        "step_id": "metadata_analysis",
                        "agent_type": "metadata",
                        "action": "extract_metadata",
                        "parameters": {"files": [], "analysis_depth": "comprehensive"},
                    },
                    {
                        "step_id": "timeline_reconstruction",
                        "agent_type": "forensics",
                        "action": "reconstruct_timeline",
                        "parameters": {"evidence": [], "timeframe": "all"},
                    },
                    {
                        "step_id": "reporting",
                        "agent_type": "reporting",
                        "action": "generate_report",
                        "parameters": {
                            "report_type": "forensics_report",
                            "format": "detailed",
                        },
                    },
                ],
            }

            # Threat Intelligence Workflow
            self.workflows["threat_intelligence"] = {
                "name": "Threat Intelligence Workflow",
                "description": "Threat intelligence collection and analysis workflow",
                "steps": [
                    {
                        "step_id": "osint_monitoring",
                        "agent_type": "osint",
                        "action": "monitor_sources",
                        "parameters": {
                            "sources": [],
                            "keywords": [],
                            "monitoring_type": "continuous",
                        },
                    },
                    {
                        "step_id": "threat_analysis",
                        "agent_type": "data_analysis",
                        "action": "analyze_threats",
                        "parameters": {
                            "analysis_type": "threat_assessment",
                            "indicators": [],
                        },
                    },
                    {
                        "step_id": "correlation",
                        "agent_type": "investigation",
                        "action": "correlate_threats",
                        "parameters": {
                            "threat_data": [],
                            "correlation_type": "multi_source",
                        },
                    },
                    {
                        "step_id": "reporting",
                        "agent_type": "reporting",
                        "action": "generate_report",
                        "parameters": {
                            "report_type": "threat_intelligence_report",
                            "format": "executive_summary",
                        },
                    },
                ],
            }

            self.logger.info("Workflow templates initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize workflow templates: {e}")
            raise

    async def register_agent(self, agent: IntelligenceAgent) -> bool:
        """
        Register an agent with the orchestrator.

        Args:
            agent: Agent to register

        Returns:
            True if registration successful, False otherwise
        """
        try:
            agent_id = agent.agent_id

            # Check if agent already exists
            if agent_id in self.agents:
                self.logger.warning(f"Agent {agent_id} already registered")
                return False

            # Register agent
            self.agents[agent_id] = agent
            self.agent_capabilities[agent_id] = agent.capabilities

            # Start agent
            await agent.start()

            # Update metrics
            self.metrics["active_agents"] = len(self.agents)

            self.logger.info(f"Agent {agent_id} registered successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False

    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the orchestrator.

        Args:
            agent_id: ID of agent to unregister

        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            if agent_id not in self.agents:
                self.logger.warning(f"Agent {agent_id} not found")
                return False

            # Stop agent
            agent = self.agents[agent_id]
            await agent.stop()

            # Remove from registry
            del self.agents[agent_id]
            del self.agent_capabilities[agent_id]

            # Update metrics
            self.metrics["active_agents"] = len(self.agents)

            self.logger.info(f"Agent {agent_id} unregistered successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False

    async def submit_task(
        self,
        task_type: str,
        description: str,
        parameters: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        workflow_id: Optional[str] = None,
    ) -> str:
        """
        Submit a new intelligence task.

        Args:
            task_type: Type of task (osint, investigation, forensics, etc.)
            description: Task description
            parameters: Task parameters
            priority: Task priority
            workflow_id: Optional workflow ID to execute

        Returns:
            Task ID
        """
        try:
            task_id = str(uuid.uuid4())

            # Create task
            task = IntelligenceTask(
                id=task_id,
                type=task_type,
                description=description,
                priority=priority,
                parameters=parameters,
                workflow_id=workflow_id,
            )

            # Store task
            self.tasks[task_id] = task

            # Add to queue
            await self.task_queue.put((priority.value, task_id, task))

            # Start task processing
            asyncio.create_task(self._process_task_queue())

            self.logger.info(f"Task {task_id} submitted successfully")
            return task_id

        except Exception as e:
            self.logger.error(f"Failed to submit task: {e}")
            raise

    async def _process_task_queue(self):
        """Process tasks from the queue."""
        while not self.task_queue.empty():
            try:
                # Get next task
                priority, task_id, task = await self.task_queue.get()

                # Find suitable agent
                agent_id = await self._find_suitable_agent(task)

                if agent_id:
                    # Assign task to agent
                    await self._assign_task_to_agent(task_id, agent_id)
                else:
                    # No suitable agent found, requeue task
                    await self.task_queue.put((priority, task_id, task))
                    await asyncio.sleep(1)  # Wait before retry

            except Exception as e:
                self.logger.error(f"Error processing task queue: {e}")
                await asyncio.sleep(1)

    async def _find_suitable_agent(self, task: IntelligenceTask) -> Optional[str]:
        """
        Find a suitable agent for the task.

        Args:
            task: Task to find agent for

        Returns:
            Agent ID if found, None otherwise
        """
        try:
            task_type = task.type.lower()

            # Find agents with matching capabilities
            suitable_agents = []
            for agent_id, capabilities in self.agent_capabilities.items():
                if task_type in capabilities or any(
                    task_type in cap.lower() for cap in capabilities
                ):
                    suitable_agents.append(agent_id)

            if not suitable_agents:
                return None

            # Select agent based on availability and workload
            best_agent = None
            best_score = -1

            for agent_id in suitable_agents:
                agent = self.agents[agent_id]

                # Check agent status
                if agent.status != AgentStatus.ACTIVE:
                    continue

                # Calculate score based on availability and workload
                score = await self._calculate_agent_score(agent_id)

                if score > best_score:
                    best_score = score
                    best_agent = agent_id

            return best_agent

        except Exception as e:
            self.logger.error(f"Error finding suitable agent: {e}")
            return None

    async def _calculate_agent_score(self, agent_id: str) -> float:
        """
        Calculate agent score for task assignment.

        Args:
            agent_id: Agent ID to score

        Returns:
            Agent score (higher is better)
        """
        try:
            agent = self.agents[agent_id]

            # Base score
            score = 1.0

            # Adjust based on current workload
            active_tasks = sum(
                1
                for task in self.active_tasks.values()
                if task.assigned_agent == agent_id
            )
            score -= active_tasks * 0.1

            # Adjust based on agent performance
            if hasattr(agent, "metrics"):
                success_rate = agent.metrics.get("tasks_completed", 0) / max(
                    agent.metrics.get("tasks_completed", 0)
                    + agent.metrics.get("tasks_failed", 0),
                    1,
                )
                score += success_rate * 0.5

            return max(score, 0.0)

        except Exception as e:
            self.logger.error(f"Error calculating agent score: {e}")
            return 0.0

    async def _assign_task_to_agent(self, task_id: str, agent_id: str):
        """
        Assign a task to an agent.

        Args:
            task_id: Task ID to assign
            agent_id: Agent ID to assign to
        """
        try:
            task = self.tasks[task_id]
            # agent = self.agents[agent_id]

            # Update task status
            task.assigned_agent = agent_id
            task.status = TaskStatus.ASSIGNED
            task.started_at = datetime.utcnow()

            # Add to active tasks
            self.active_tasks[task_id] = task

            # Execute task
            asyncio.create_task(self._execute_task(task_id, agent_id))

            self.logger.info(f"Task {task_id} assigned to agent {agent_id}")

        except Exception as e:
            self.logger.error(
                f"Failed to assign task {task_id} to agent {agent_id}: {e}"
            )

    async def _execute_task(self, task_id: str, agent_id: str):
        """
        Execute a task with an agent.

        Args:
            task_id: Task ID to execute
            agent_id: Agent ID to execute with
        """
        try:
            task = self.tasks[task_id]
            agent = self.agents[agent_id]

            # Update task status
            task.status = TaskStatus.IN_PROGRESS

            # Execute task
            result = await agent.process_task(
                {
                    "id": task_id,
                    "type": task.type,
                    "description": task.description,
                    "parameters": task.parameters,
                }
            )

            # Update task with result
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()

            # Remove from active tasks
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]

            # Update metrics
            self.metrics["tasks_processed"] += 1
            self.metrics["tasks_completed"] += 1

            execution_time = (task.completed_at - task.started_at).total_seconds()
            self._update_average_task_time(execution_time)

            self.logger.info(f"Task {task_id} completed successfully")

        except Exception as e:
            # Update task with error
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()

            # Remove from active tasks
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]

            # Update metrics
            self.metrics["tasks_processed"] += 1
            self.metrics["tasks_failed"] += 1

            self.logger.error(f"Task {task_id} failed: {e}")

    def _update_average_task_time(self, execution_time: float):
        """Update average task execution time."""
        total_tasks = self.metrics["tasks_processed"]
        if total_tasks > 0:
            current_avg = self.metrics["average_task_time"]
            self.metrics["average_task_time"] = (
                current_avg * (total_tasks - 1) + execution_time
            ) / total_tasks

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task status.

        Args:
            task_id: Task ID to get status for

        Returns:
            Task status information or None if not found
        """
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        return {
            "task_id": task_id,
            "type": task.type,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_agent": task.assigned_agent,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": (
                task.completed_at.isoformat() if task.completed_at else None
            ),
            "result": task.result,
            "error": task.error,
        }

    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent status.

        Args:
            agent_id: Agent ID to get status for

        Returns:
            Agent status information or None if not found
        """
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]
        return await agent.get_status()

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status.

        Returns:
            System status information
        """
        return {
            "orchestrator_status": "active",
            "active_agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "total_tasks": len(self.tasks),
            "metrics": self.metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def execute_workflow(
        self, workflow_id: str, parameters: Dict[str, Any]
    ) -> str:
        """
        Execute a workflow.

        Args:
            workflow_id: Workflow ID to execute
            parameters: Workflow parameters

        Returns:
            Workflow execution ID
        """
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")

            # workflow = self.workflows[workflow_id]
            execution_id = str(uuid.uuid4())

            # Create workflow instance
            self.workflow_instances[execution_id] = {
                "workflow_id": workflow_id,
                "status": "running",
                "current_step": 0,
                "parameters": parameters,
                "results": {},
                "created_at": datetime.utcnow().isoformat(),
            }

            # Execute workflow steps
            asyncio.create_task(self._execute_workflow_steps(execution_id))

            self.logger.info(
                f"Workflow {workflow_id} execution started: {execution_id}"
            )
            return execution_id

        except Exception as e:
            self.logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            raise

    async def _execute_workflow_steps(self, execution_id: str):
        """Execute workflow steps sequentially."""
        try:
            instance = self.workflow_instances[execution_id]
            workflow = self.workflows[instance["workflow_id"]]

            for step in workflow["steps"]:
                # Submit task for this step
                task_id = await self.submit_task(
                    task_type=step["agent_type"],
                    description=f"Workflow step: {step['step_id']}",
                    parameters={**instance["parameters"], **step["parameters"]},
                    priority=TaskPriority.MEDIUM,
                )

                # Wait for task completion
                while True:
                    task_status = await self.get_task_status(task_id)
                    if task_status and task_status["status"] in ["completed", "failed"]:
                        break
                    await asyncio.sleep(1)

                # Store step result
                instance["results"][step["step_id"]] = task_status

                if task_status["status"] == "failed":
                    instance["status"] = "failed"
                    break

            if instance["status"] != "failed":
                instance["status"] = "completed"

            self.logger.info(f"Workflow execution {execution_id} completed")

        except Exception as e:
            self.logger.error(f"Workflow execution {execution_id} failed: {e}")
            instance["status"] = "failed"
            instance["error"] = str(e)

    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """Get task result"""
        if task_id not in self.tasks:
            return {"error": "Task not found", "task_id": task_id}

        task = self.tasks[task_id]
        return {
            "task_id": task_id,
            "type": task.type,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_agent": task.assigned_agent,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": (
                task.completed_at.isoformat() if task.completed_at else None
            ),
            "result": task.result,
            "error": task.error,
        }

    async def initialize(self) -> None:
        """Initialize the orchestrator"""
        try:
            self.logger.info("Initializing Intelligence Orchestrator...")

            # Initialize core services
            await self._initialize_services()

            self.logger.info("Intelligence Orchestrator initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown the orchestrator"""
        try:
            self.logger.info("Shutting down Intelligence Orchestrator...")

            # Stop all agents
            for agent in self.agents.values():
                await agent.stop()

            self.logger.info("Intelligence Orchestrator shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during orchestrator shutdown: {e}")
