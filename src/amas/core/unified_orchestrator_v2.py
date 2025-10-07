from __future__ import annotations
import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable

from amas.common.models import OrchestratorTask, TaskPriority, TaskStatus, AgentConfig, AgentStatus
from ..services.universal_ai_manager import UniversalAIManager, get_universal_ai_manager
from .message_bus import MessageBus


logger = logging.getLogger(__name__)


class UnifiedOrchestratorV2:
    """
    Unified and enhanced orchestrator for the AMAS Intelligence System.

    This orchestrator combines agent coordination, task distribution, workflow execution,
    multi-API fallback, and intelligent routing.
    """

    def __init__(
        self,
        universal_ai_manager: Optional[UniversalAIManager] = None,
        vector_service: Any = None,
        knowledge_graph: Any = None,
        security_service: Any = None,
    ):
        """
        Initialize the unified orchestrator.

        Args:
            universal_ai_manager: Instance of UniversalAIManager for AI operations.
            vector_service: Vector service for semantic search.
            knowledge_graph: Knowledge graph service.
            security_service: Security service for access control.
        """
        self.universal_ai_manager = universal_ai_manager or get_universal_ai_manager()
        self.vector_service = vector_service
        self.knowledge_graph = knowledge_graph
        self.security_service = security_service

        self.message_bus = MessageBus() # Initialize MessageBus

        self.agents: Dict[str, 'IntelligenceAgent'] = {}
        self.agent_configs: Dict[str, AgentConfig] = {}
        self.tasks: Dict[str, OrchestratorTask] = {}
        self.task_queue = asyncio.PriorityQueue()
        self.active_tasks: Dict[str, OrchestratorTask] = {}

        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_instances: Dict[str, Dict[str, Any]] = {}

        self.metrics = {
            "tasks_processed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_task_time": 0.0,
            "active_agents": 0,
            "active_tasks": 0,
        }

        self.logger = logging.getLogger("amas.unified_orchestrator")

        self._initialize_orchestrator_agents()
        self._initialize_workflow_templates()
        self.logger.info("Unified Orchestrator V2 initialized successfully")
        asyncio.create_task(self._subscribe_to_feedback())

    def _initialize_orchestrator_agents(self):
        """
        Define and register internal orchestrator agents with their capabilities.
        These are logical agent configurations used for task routing, not actual agent instances.
        """
        agent_definitions = [
            AgentConfig(
                agent_id="rag_agent",
                agent_type="RAG Agent",
                config={
                    "name": "RAG Agent",
                    "description": "Retrieval-Augmented Generation agent for knowledge retrieval and synthesis.",
                    "specialization": "Information retrieval, document summarization, knowledge synthesis.",
                    "capabilities": ["information_retrieval", "document_qa", "knowledge_synthesis"],
                    "preferred_models": ["deepseek/deepseek-chat", "openai/gpt-4", "meta-llama/llama-3.1-70b"],
                }
            ),
            AgentConfig(
                agent_id="tool_agent",
                agent_type="Tool Agent",
                config={
                    "name": "Tool Agent",
                    "description": "Agent capable of executing external tools and APIs.",
                    "specialization": "Tool execution, API interaction, external system control.",
                    "capabilities": ["tool_execution", "api_interaction", "external_control"],
                    "preferred_models": ["deepseek/deepseek-chat", "openai/gpt-4"],
                }
            ),
            AgentConfig(
                agent_id="planning_agent",
                agent_type="Planning Agent",
                config={
                    "name": "Planning Agent",
                    "description": "Agent for generating, refining, and optimizing task plans.",
                    "specialization": "Task decomposition, plan generation, resource allocation.",
                    "capabilities": ["task_planning", "plan_refinement", "resource_allocation"],
                    "preferred_models": ["openai/gpt-4", "anthropic/claude-3-opus"],
                }
            ),
            AgentConfig(
                agent_id="code_agent",
                agent_type="Code Agent",
                config={
                    "name": "Code Agent",
                    "description": "Agent for writing, debugging, and executing code.",
                    "specialization": "Code generation, debugging, testing, script execution.",
                    "capabilities": ["code_generation", "code_execution", "code_debugging"],
                    "preferred_models": ["deepseek/deepseek-coder", "openai/gpt-4"],
                }
            ),
            AgentConfig(
                agent_id="data_agent",
                agent_type="Data Agent",
                config={
                    "name": "Data Agent",
                    "description": "Agent for data analysis, processing, and visualization.",
                    "specialization": "Data analysis, statistical modeling, visualization.",
                    "capabilities": ["data_analysis", "data_processing", "data_visualization"],
                    "preferred_models": ["meta-llama/llama-3.1-70b", "deepseek/deepseek-chat"],
                }
            ),
            # Existing logical agents for orchestrator's internal use (e.g., for workflow steps)
            AgentConfig(
                agent_id="code_analyst_agent",
                agent_type="Code Analysis Agent",
                config={
                    "name": "Code Analysis Agent",
                    "description": "Analyzes code quality, architecture, and best practices",
                    "specialization": "Code quality, performance, and architecture analysis",
                    "capabilities": ["code_analysis", "code_review", "performance_analysis", "architecture_assessment"],
                    "preferred_models": ["deepseek/deepseek-chat", "openai/gpt-4", "meta-llama/llama-3.1-70b"],
                }
            ),
            AgentConfig(
                agent_id="security_expert_agent",
                agent_type="Security Expert Agent",
                config={
                    "name": "Security Expert Agent",
                    "description": "Identifies vulnerabilities and security issues",
                    "specialization": "Security scanning, vulnerability assessment, threat analysis",
                    "capabilities": ["security_scan", "vulnerability_assessment", "threat_analysis", "security_recommendations"],
                    "preferred_models": ["openai/gpt-4", "anthropic/claude-3-opus", "deepseek/deepseek-chat"],
                }
            ),
            AgentConfig(
                agent_id="intelligence_gatherer_agent",
                agent_type="Intelligence Gathering Agent",
                config={
                    "name": "Intelligence Gathering Agent",
                    "description": "Collects and analyzes intelligence from various sources",
                    "specialization": "OSINT collection, threat intelligence, information gathering",
                    "capabilities": ["osint_collection", "threat_intelligence", "data_aggregation", "investigation"],
                    "preferred_models": ["deepseek/deepseek-chat", "openai/gpt-3.5-turbo", "meta-llama/llama-3.1-70b"],
                }
            ),
            AgentConfig(
                agent_id="reporting_agent",
                agent_type="Reporting Agent",
                config={
                    "name": "Reporting Agent",
                    "description": "Synthesizes information into clear, actionable reports",
                    "specialization": "Report generation, executive summaries, documentation",
                    "capabilities": ["reporting", "synthesis", "documentation_generation"],
                    "preferred_models": ["grok", "glm", "deepseek", "gemini"],
                }
            ),
            AgentConfig(
                agent_id="forensics_agent",
                agent_type="Forensics Agent",
                config={
                    "name": "Forensics Agent",
                    "description": "Performs digital forensics and evidence analysis",
                    "specialization": "Digital forensics, incident investigation, evidence analysis",
                    "capabilities": ["forensics", "evidence_analysis", "timeline_reconstruction"],
                    "preferred_models": ["deepseek", "nvidia", "codestral", "grok"],
                }
            ),
            AgentConfig(
                agent_id="technology_monitor_agent",
                agent_type="Technology Monitor Agent",
                config={
                    "name": "Technology Monitor Agent",
                    "description": "Monitors technology trends and emerging threats",
                    "specialization": "Technology watch, trend analysis, competitive intelligence",
                    "capabilities": ["technology_monitoring", "trend_analysis", "competitive_intelligence"],
                    "preferred_models": ["deepseek", "glm", "grok"],
                }
            ),
            AgentConfig(
                agent_id="ml_decision_agent",
                agent_type="ML Decision Agent",
                config={
                    "name": "ML Decision Agent",
                    "description": "Uses ML for intelligent task allocation and decision making",
                    "specialization": "Machine learning, task routing, predictive analytics",
                    "capabilities": ["ml_decision", "task_allocation", "predictive_analytics"],
                    "preferred_models": ["deepseek/deepseek-chat", "openai/gpt-4"],
                }
            ),
            AgentConfig(
                agent_id="rl_optimizer_agent",
                agent_type="RL Optimizer Agent",
                config={
                    "name": "RL Optimizer Agent",
                    "description": "Applies reinforcement learning for system optimization",
                    "specialization": "Reinforcement learning, system optimization, adaptive control",
                    "capabilities": ["rl_optimization", "adaptive_learning", "performance_tuning"],
                    "preferred_models": ["openai/gpt-4", "anthropic/claude-3-opus"],
                }
            ),
        ]

        for config in agent_definitions:
            self.agent_configs[config.agent_id] = config
            self.logger.info(f"Defined orchestrator agent: {config.config['name']}")

    def _initialize_workflow_templates(self):
        """
        Initialize workflow templates for common intelligence operations.
        This can be loaded from a configuration file or defined here.
        """
        self.workflows["osint_investigation"] = {
            "name": "OSINT Investigation Workflow",
            "description": "Comprehensive OSINT investigation workflow",
            "steps": [
                {
                    "step_id": "osint_collection",
                    "agent_role": "intelligence_gatherer_agent",
                    "action": "collect_data",
                    "parameters": {"sources": [], "keywords": [], "filters": {}},
                },
                {
                    "step_id": "data_analysis",
                    "agent_role": "data_analysis_agent",
                    "action": "analyze_data",
                    "parameters": {"analysis_type": "correlation", "entities": []},
                },
                {
                    "step_id": "investigation",
                    "agent_role": "intelligence_gatherer_agent",
                    "action": "investigate_entities",
                    "parameters": {"entities": [], "depth": "deep"},
                },
                {
                    "step_id": "reporting",
                    "agent_role": "reporting_agent",
                    "action": "generate_report",
                    "parameters": {"report_type": "intelligence_report", "format": "comprehensive"},
                },
            ],
        }
        self.logger.info("Workflow templates initialized successfully")

    async def register_agent(self, agent: 'IntelligenceAgent') -> bool:
        """
        Register an actual IntelligenceAgent instance with the orchestrator.
        Also registers the agent with the message bus.

        Args:
            agent: Agent to register.

        Returns:
            True if registration successful, False otherwise.
        """
        try:
            agent_id = agent.agent_id
            if agent_id in self.agents:
                self.logger.warning(f"Agent {agent_id} already registered.")
                return False

            # The agent constructor now expects the message_bus
            # This implies that the agent instance passed to register_agent should already be initialized with the orchestrator's message_bus
            # For now, we assume the agent is initialized correctly before being passed here.
            # A more robust solution might involve the orchestrator instantiating agents directly.
            self.agents[agent_id] = agent
            await self.message_bus.register_agent(agent_id, self._handle_agent_message)
            await agent.start()
            self.metrics["active_agents"] = len(self.agents)
            self.logger.info(f"Agent {agent_id} registered successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False

    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the orchestrator and the message bus.

        Args:
            agent_id: ID of agent to unregister.

        Returns:
            True if unregistration successful, False otherwise.
        """
        try:
            if agent_id not in self.agents:
                self.logger.warning(f"Agent {agent_id} not found.")
                return False

            agent = self.agents[agent_id]
            await agent.stop()
            await self.message_bus.unregister_agent(agent_id)
            del self.agents[agent_id]
            self.metrics["active_agents"] = len(self.agents)
            self.logger.info(f"Agent {agent_id} unregistered successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False

    async def _handle_agent_message(self, message: Dict[str, Any]):
        """
        Handles messages received from agents via the message bus.
        This method acts as a central point for orchestrator to react to agent communications.
        """
        sender_id = message.get("sender_id")
        message_type = message.get("type")
        payload = message.get("payload")
        task_id = message.get("task_id")

        self.logger.debug(f"Orchestrator received message from {sender_id}: {message_type} for task {task_id}")

        if message_type == "task_update" and task_id in self.tasks:
            task = self.tasks[task_id]
            new_status = payload.get("status")
            result = payload.get("result")
            error = payload.get("error")

            if new_status:
                task.status = TaskStatus[new_status.upper()]
            if result:
                task.result = result
            if error:
                task.error = error

            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                task.completed_at = datetime.utcnow()
                if task.id in self.active_tasks:
                    del self.active_tasks[task.id]
                if task.status == TaskStatus.COMPLETED:
                    self.metrics["tasks_completed"] += 1
                elif task.status == TaskStatus.FAILED:
                    self.metrics["tasks_failed"] += 1
                self.logger.info(f"Task {task_id} updated to {task.status.value}. Result: {result}, Error: {error}")
            else:
                self.logger.debug(f"Task {task_id} status updated to {task.status.value}.")

        elif message_type == "request_subtask":
            # An agent requests the orchestrator to create a subtask
            subtask_title = payload.get("title", "Subtask")
            subtask_description = payload.get("description", "")
            subtask_type = payload.get("task_type", "general")
            subtask_priority = TaskPriority[payload.get("priority", "MEDIUM").upper()]
            subtask_parameters = payload.get("parameters", {})
            subtask_required_agent_roles = payload.get("required_agent_roles", [])

            parent_task = self.tasks.get(task_id)
            # Extract workflow_id and workflow_step_id from parent_task's metadata
            workflow_id = parent_task.metadata.get("workflow_id") if parent_task else None
            workflow_step_id = parent_task.metadata.get("workflow_step_id") if parent_task else None

            new_task_id = await self.submit_task(
                description=subtask_description,
                task_type=subtask_type,
                priority=subtask_priority,
                metadata={
                    "title": subtask_title,
                    "parameters": subtask_parameters,
                    "required_agent_roles": subtask_required_agent_roles,
                    "workflow_id": workflow_id,
                    "workflow_step_id": workflow_step_id,
                }
            )

            self.logger.info(f"Agent {sender_id} requested subtask {new_task_id} for task {task_id}.")
            # Optionally, send a message back to the requesting agent with the new task ID
            await self.message_bus.send_direct_message(
                sender_id, {"type": "subtask_created", "payload": {"original_task_id": task_id, "new_task_id": new_task_id}}
            )

        elif message_type == "task_feedback":
            await self._handle_feedback_message(message)

        else:
            self.logger.warning(f"Orchestrator received unhandled message type: {message_type} from {sender_id}")

    async def submit_task(
        self,
        description: str,
        task_type: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        # Extract title, required_agent_roles, parameters, workflow_id, workflow_step_id from metadata
        title = metadata.get("title", "Untitled Task") if metadata else "Untitled Task"
        required_agent_roles = metadata.get("required_agent_roles", []) if metadata else []
        parameters = metadata.get("parameters", {}) if metadata else {}
        workflow_id = metadata.get("workflow_id") if metadata else None
        workflow_step_id = metadata.get("workflow_step_id") if metadata else None
        """
        Submits a new task to the orchestrator.

        Args:
            title: A brief title for the task.
            description: Detailed description of the task.
            task_type: The type of task (e.g., 'code_generation', 'data_analysis').
            priority: The priority of the task.
            required_agent_roles: List of agent roles required for this task.
            parameters: Additional parameters for the task.
            workflow_id: Optional ID of the workflow this task belongs to.
            workflow_step_id: Optional ID of the workflow step this task belongs to.

        Returns:
            The ID of the newly created task.
        """
        task_id = str(uuid.uuid4())
        task = OrchestratorTask(
            id=task_id,
            description=description,
            task_type=task_type,
            priority=priority,
            metadata={
                "title": title,
                "required_agent_roles": required_agent_roles or [],
                "parameters": parameters or {},
                "workflow_id": workflow_id,
                "workflow_step_id": workflow_step_id,
            },
        )

        self.tasks[task_id] = task
        await self.task_queue.put((task.priority.value, task.created_at, task_id)) # Use created_at for tie-breaking
        self.metrics["tasks_processed"] += 1
        self.logger.info(f"Task {task_id} '{title}' submitted with priority {priority.name}.")
        asyncio.create_task(self._process_task_queue())
        return task_id

    async def _process_task_queue(self):
        """
        Continuously processes tasks from the priority queue.
        """
        while not self.task_queue.empty():
            _, _, task_id = await self.task_queue.get()
            task = self.tasks.get(task_id)

            if not task or task.status != TaskStatus.PENDING:
                continue

            self.logger.info(f"Attempting to assign task {task.id} '{task.title}'.")
            assigned = await self._assign_task_to_agent(task)

            if not assigned:
                self.logger.warning(f"No suitable agent found for task {task.id}. Re-queueing.")
                # Re-queue with lower priority or after a delay
                await self.task_queue.put((TaskPriority.LOW.value, datetime.utcnow(), task.id))
                task.status = TaskStatus.PENDING # Ensure status is PENDING if re-queued

    async def _assign_task_to_agent(self, task: OrchestratorTask) -> bool:
        """
        Assigns a task to the most suitable available agent.

        Args:
            task: The task to assign.

        Returns:
            True if the task was assigned, False otherwise.
        """
        suitable_agents = []
        for agent_id, agent_instance in self.agents.items():
            agent_config = self.agent_configs.get(agent_id) # Get the logical config
            if agent_instance.status == AgentStatus.IDLE and agent_config:
                # Check if agent has required capabilities
                if all(role in agent_config.capabilities for role in task.required_agent_roles):
                    suitable_agents.append((agent_instance, agent_config))

        if not suitable_agents:
            return False

        # Simple assignment: pick the first available suitable agent
        # TODO: Implement more advanced agent selection logic (e.g., load balancing, performance-based)
        chosen_agent_instance, chosen_agent_config = suitable_agents[0]

        task.assigned_agent_id = chosen_agent_instance.agent_id
        task.status = TaskStatus.ASSIGNED
        task.started_at = datetime.utcnow()
        self.active_tasks[task.id] = task

        # Send task to agent via message bus
        await self.message_bus.publish(
            f"agent_tasks_{chosen_agent_instance.agent_id}",
            {
                "sender_id": "orchestrator",
                "type": "assign_task",
                "task_id": task.id,
                "payload": {"task_data": task.to_dict()}
            }
        )
        self.logger.info(f"Task {task.id} '{task.title}' assigned to agent {chosen_agent_instance.agent_id}.")
        return True

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Retrieves the current status of the orchestrator and all registered agents.
        """
        agent_statuses = []
        for agent_id, agent_instance in self.agents.items():
            agent_statuses.append(await agent_instance.get_status())

        return {
            "orchestrator_status": "active",
            "total_tasks_submitted": self.metrics["tasks_processed"],
            "tasks_completed": self.metrics["tasks_completed"],
            "tasks_failed": self.metrics["tasks_failed"],
            "active_tasks_count": len(self.active_tasks),
            "registered_agents_count": len(self.agents),
            "agent_statuses": agent_statuses,
            "ai_manager_status": await self.universal_ai_manager.get_status(),
            "metrics": self.metrics,
        }

    async def _subscribe_to_feedback(self):
        """
        Subscribes the orchestrator to the feedback channel from agents.
        """
        await self.message_bus.subscribe("orchestrator_feedback", self._handle_feedback_message)
        self.logger.info("Orchestrator subscribed to agent feedback.")

    async def _handle_feedback_message(self, message: Dict[str, Any]):
        """
        Handles feedback messages from agents, triggering adaptation.
        """
        sender_id = message.get("sender_id")
        task_id = message.get("task_id")
        success = message.get("payload", {}).get("success")
        details = message.get("payload", {}).get("details")
        agent_metrics = message.get("payload", {}).get("metrics", {})

        self.logger.info(f"Received feedback for task {task_id} from agent {sender_id}: success={success}")

        agent = self.agents.get(sender_id)
        if agent:
            # Update agent's internal metrics based on feedback
            agent.metrics.update(agent_metrics)
            # Trigger agent's adaptation logic
            await agent.adapt_parameters()
        else:
            self.logger.warning(f"Feedback received from unknown agent: {sender_id}")

    async def execute_workflow(
        self, workflow_name: str, initial_parameters: Dict[str, Any]
    ) -> str:
        """
        Executes a predefined workflow.

        Args:
            workflow_name: The name of the workflow to execute.
            initial_parameters: Initial parameters for the workflow.

        Returns:
            The ID of the initiated workflow instance.
        """
        workflow_template = self.workflows.get(workflow_name)
        if not workflow_template:
            raise ValueError(f"Workflow '{workflow_name}' not found.")

        workflow_instance_id = str(uuid.uuid4())
        self.workflow_instances[workflow_instance_id] = {
            "id": workflow_instance_id,
            "name": workflow_name,
            "status": "in_progress",
            "current_step": 0,
            "parameters": initial_parameters,
            "results": {},
            "created_at": datetime.utcnow(),
            "steps": workflow_template["steps"],
        }
        self.logger.info(f"Workflow '{workflow_name}' started with ID: {workflow_instance_id}")

        # Start the first step of the workflow
        asyncio.create_task(self._process_workflow_step(workflow_instance_id, 0))

        return workflow_instance_id

    async def _process_workflow_step(self, workflow_instance_id: str, step_index: int):
        """
        Processes a single step within a workflow instance.
        """
        workflow_instance = self.workflow_instances.get(workflow_instance_id)
        if not workflow_instance:
            self.logger.error(f"Workflow instance {workflow_instance_id} not found.")
            return

        steps = workflow_instance["steps"]
        if step_index >= len(steps):
            workflow_instance["status"] = "completed"
            workflow_instance["completed_at"] = datetime.utcnow()
            self.logger.info(f"Workflow {workflow_instance_id} completed.")
            return

        step = steps[step_index]
        self.logger.info(f"Processing workflow {workflow_instance_id}, step {step_index}: {step['step_id']}")

        # Prepare task for the agent specified in the workflow step
        task_title = f"Workflow {workflow_instance_id} - Step {step['step_id']}"
        task_description = f"Execute action '{step['action']}' for workflow step '{step['step_id']}'."
        task_type = step.get("action", "general") # Use action as task_type
        task_parameters = {
            **workflow_instance["parameters"], # Pass workflow parameters to task
            **step.get("parameters", {}), # Override with step-specific parameters
            "workflow_instance_id": workflow_instance_id,
            "workflow_step_id": step["step_id"],
        }
        required_agent_roles = [step["agent_role"]]

        # Submit task to orchestrator
        task_id = await self.submit_task(
            title=task_title,
            description=task_description,
            task_type=task_type,
            required_agent_roles=required_agent_roles,
            parameters=task_parameters,
            workflow_id=workflow_instance_id,
            workflow_step_id=step["step_id"],
        )

        # Store task ID in workflow instance for tracking
        workflow_instance["current_task_id"] = task_id
        workflow_instance["current_step"] = step_index

        # The orchestrator will receive feedback for this task and then call _handle_feedback_message
        # which will eventually trigger the next step or mark workflow as complete/failed.
        # For now, we assume a successful task completion will lead to the next step.
        # A more robust workflow engine would have explicit step transition logic.

    async def _on_task_completed_for_workflow(self, task: OrchestratorTask):
        """
        Callback when a task belonging to a workflow is completed.
        """
        workflow_instance_id = task.workflow_id
        workflow_step_id = task.workflow_step_id

        if not workflow_instance_id or not workflow_step_id:
            return # Not a workflow task

        workflow_instance = self.workflow_instances.get(workflow_instance_id)
        if not workflow_instance:
            self.logger.error(f"Workflow instance {workflow_instance_id} not found for completed task {task.id}.")
            return

        # Store result of the step
        workflow_instance["results"][workflow_step_id] = task.result

        # Find the index of the completed step
        current_step_index = -1
        for i, step in enumerate(workflow_instance["steps"]):
            if step["step_id"] == workflow_step_id:
                current_step_index = i
                break

        if current_step_index != -1:
            # Proceed to the next step
            asyncio.create_task(self._process_workflow_step(workflow_instance_id, current_step_index + 1))
        else:
            self.logger.error(f"Completed task {task.id} belongs to unknown workflow step {workflow_step_id} in workflow {workflow_instance_id}.")

    async def _on_task_failed_for_workflow(self, task: OrchestratorTask):
        """
        Callback when a task belonging to a workflow fails.
        """
        workflow_instance_id = task.workflow_id
        if not workflow_instance_id:
            return # Not a workflow task

        workflow_instance = self.workflow_instances.get(workflow_instance_id)
        if workflow_instance:
            workflow_instance["status"] = "failed"
            workflow_instance["completed_at"] = datetime.utcnow()
            workflow_instance["error"] = f"Step {task.workflow_step_id} failed: {task.error}"
            self.logger.error(f"Workflow {workflow_instance_id} failed at step {task.workflow_step_id} due to task {task.id}.")

# --- Singleton instance ---

_unified_orchestrator_instance: Optional[UnifiedOrchestratorV2] = None


def get_unified_orchestrator() -> UnifiedOrchestratorV2:
    """
    Returns a singleton instance of the UnifiedOrchestratorV2.
    """
    global _unified_orchestrator_instance
    if _unified_orchestrator_instance is None:
        _unified_orchestrator_instance = UnifiedOrchestratorV2()
    return _unified_orchestrator_instance

