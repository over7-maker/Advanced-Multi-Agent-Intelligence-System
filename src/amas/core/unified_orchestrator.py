"""

Unified Multi-Agent Orchestrator
Combines functionality from all orchestrator implementations
"""

import asyncio
import json
import logging
# import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..agents.base.intelligence_agent import IntelligenceAgent
from ..agents.unified_ai_router import agent_complete, get_ai_router

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Standardized agent roles across the system"""

    CODE_ANALYST = "code_analyst"
    SECURITY_EXPERT = "security_expert"
    INTELLIGENCE_GATHERER = "intelligence_gatherer"
    INCIDENT_RESPONDER = "incident_responder"
    CODE_IMPROVER = "code_improver"
    DOCUMENTATION_SPECIALIST = "documentation_specialist"
    PERFORMANCE_OPTIMIZER = "performance_optimizer"
    QUALITY_ASSURANCE = "quality_assurance"
    PROJECT_MANAGER = "project_manager"
    OSINT_COLLECTOR = "osint_collector"
    FORENSICS_ANALYST = "forensics_analyst"
    DATA_ANALYST = "data_analyst"
    TECHNOLOGY_MONITOR = "technology_monitor"


@dataclass
class AgentConfig:
    """Configuration for an agent"""

    role: AgentRole
    name: str
    description: str
    specialization: str
    priority_models: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 3


@dataclass
class OrchestratorTask:
    """Task to be executed by agents"""

    task_id: str
    title: str
    description: str
    required_agents: List[AgentRole]
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class UnifiedOrchestrator:
    """
    Unified orchestrator that manages all agent coordination
    """

    def __init__(self):
        """Initialize the unified orchestrator"""
        self.ai_router = get_ai_router()
        self.agents: Dict[AgentRole, AgentConfig] = {}
        self.active_tasks: Dict[str, OrchestratorTask] = {}
        self.task_queue = asyncio.Queue()
        self.results_cache: Dict[str, Any] = {}

        # Initialize agent configurations
        self._initialize_agents()

        # Start background workers
        self._start_workers()

        logger.info("Unified Orchestrator initialized")

    def _initialize_agents(self):
        """Initialize all agent configurations"""

        # Define all agents with their configurations
        agent_configs = [
            AgentConfig(
                role=AgentRole.CODE_ANALYST,
                name="Code Analysis Agent",
                description="Analyzes code quality, architecture, and best practices",
                specialization="Code quality, performance, and architecture analysis",
                priority_models=[
                    "deepseek/deepseek-chat",
                    "openai/gpt-4",
                    "meta-llama/llama-3.1-70b",
                ],
                capabilities=[
                    "code_review",
                    "performance_analysis",
                    "architecture_assessment",
                ],
            ),
            AgentConfig(
                role=AgentRole.SECURITY_EXPERT,
                name="Security Expert Agent",
                description="Identifies vulnerabilities and security issues",
                specialization="Security scanning, vulnerability assessment, threat analysis",
                priority_models=[
                    "openai/gpt-4",
                    "anthropic/claude-3-opus",
                    "deepseek/deepseek-chat",
                ],
                capabilities=[
                    "vulnerability_scan",
                    "threat_assessment",
                    "security_recommendations",
                ],
            ),
            AgentConfig(
                role=AgentRole.INTELLIGENCE_GATHERER,
                name="Intelligence Gathering Agent",
                description="Collects and analyzes intelligence from various sources",
                specialization="OSINT collection, threat intelligence, information gathering",
                priority_models=[
                    "deepseek/deepseek-chat",
                    "openai/gpt-3.5-turbo",
                    "meta-llama/llama-3.1-70b",
                ],
                capabilities=[
                    "osint_collection",
                    "threat_intelligence",
                    "data_aggregation",
                ],
            ),
            AgentConfig(
                role=AgentRole.INCIDENT_RESPONDER,
                name="Incident Response Agent",
                description="Handles security incidents and coordinates response",
                specialization="Incident triage, response coordination, emergency handling",
                priority_models=[
                    "openai/gpt-4",
                    "deepseek/deepseek-chat",
                    "anthropic/claude-3-opus",
                ],
                capabilities=[
                    "incident_triage",
                    "response_planning",
                    "mitigation_strategies",
                ],
            ),
            AgentConfig(
                role=AgentRole.CODE_IMPROVER,
                name="Code Improvement Agent",
                description="Suggests code improvements and refactoring",
                specialization="Code refactoring, optimization, and enhancement suggestions",
                priority_models=[
                    "deepseek/deepseek-chat",
                    "openai/gpt-4",
                    "meta-llama/codellama-34b",
                ],
                capabilities=["refactoring", "optimization", "code_enhancement"],
            ),
            AgentConfig(
                role=AgentRole.DOCUMENTATION_SPECIALIST,
                name="Documentation Specialist Agent",
                description="Creates and maintains documentation",
                specialization="Documentation generation, knowledge management, content creation",
                priority_models=[
                    "openai/gpt-4",
                    "anthropic/claude-3-opus",
                    "deepseek/deepseek-chat",
                ],
                capabilities=["documentation_generation", "api_docs", "user_guides"],
            ),
            AgentConfig(
                role=AgentRole.PERFORMANCE_OPTIMIZER,
                name="Performance Optimization Agent",
                description="Optimizes system and code performance",
                specialization="Performance profiling, optimization strategies, bottleneck identification",
                priority_models=[
                    "deepseek/deepseek-chat",
                    "openai/gpt-4",
                    "meta-llama/llama-3.1-70b",
                ],
                capabilities=[
                    "performance_profiling",
                    "optimization_recommendations",
                    "bottleneck_analysis",
                ],
            ),
            AgentConfig(
                role=AgentRole.QUALITY_ASSURANCE,
                name="Quality Assurance Agent",
                description="Ensures code and system quality",
                specialization="Test planning, quality metrics, automated testing strategies",
                priority_models=[
                    "openai/gpt-4",
                    "deepseek/deepseek-chat",
                    "anthropic/claude-3-opus",
                ],
                capabilities=["test_planning", "quality_assessment", "test_generation"],
            ),
            AgentConfig(
                role=AgentRole.PROJECT_MANAGER,
                name="Project Management Agent",
                description="Coordinates project activities and planning",
                specialization="Task coordination, roadmap planning, resource allocation",
                priority_models=[
                    "openai/gpt-4",
                    "anthropic/claude-3-opus",
                    "deepseek/deepseek-chat",
                ],
                capabilities=[
                    "project_planning",
                    "task_coordination",
                    "progress_tracking",
                ],
            ),
        ]

        # Register all agents
        for config in agent_configs:
            self.agents[config.role] = config
            logger.info(f"Registered agent: {config.name}")

    def _start_workers(self):
        """Start background worker tasks"""
        # For now, we'll keep this simple
        # In a production system, this would start async workers
        pass

    async def execute_task(
        self,
        title: str,
        description: str,
        required_agents: List[AgentRole],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> OrchestratorTask:
        """
        Execute a task using specified agents

        Args:
            title: Task title
            description: Task description
            required_agents: List of agent roles required
            parameters: Additional parameters

        Returns:
            Completed task with results
        """
        # Create task
        task = OrchestratorTask(
            task_id=str(uuid.uuid4()),
            title=title,
            description=description,
            required_agents=required_agents,
            parameters=parameters or {},
        )

        self.active_tasks[task.task_id] = task
        logger.info(f"Executing task: {title} (ID: {task.task_id})")

        try:
            # Execute with each required agent
            for agent_role in required_agents:
                if agent_role not in self.agents:
                    logger.warning(f"Agent role not found: {agent_role}")
                    continue

                agent_config = self.agents[agent_role]

                # Prepare agent-specific prompt
                agent_prompt = self._prepare_agent_prompt(
                    agent_config, task, parameters
                )

                # Execute with agent
                try:
                    response, metadata = await agent_complete(
                        agent_name=agent_config.name,
                        messages=[
                            {
                                "role": "system",
                                "content": f"You are {agent_config.name}. {agent_config.description}",
                            },
                            {"role": "user", "content": agent_prompt},
                        ],
                        preferred_models=agent_config.priority_models,
                        max_tokens=2000,
                    )

                    # Store results
                    task.results[agent_role.value] = {
                        "response": response,
                        "metadata": metadata,
                        "timestamp": datetime.now().isoformat(),
                    }

                    logger.info(f"Agent {agent_config.name} completed task")

                except Exception as e:
                    logger.error(f"Agent {agent_config.name} failed: {e}")
                    task.results[agent_role.value] = {
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }

            # Mark task as completed
            task.status = "completed"
            task.completed_at = datetime.now()

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()

        return task

    def _prepare_agent_prompt(
        self,
        agent_config: AgentConfig,
        task: OrchestratorTask,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Prepare agent-specific prompt"""
        prompt_parts = [
            f"Task: {task.title}",
            f"Description: {task.description}",
            f"Your specialization: {agent_config.specialization}",
            f"Focus on your capabilities: {', '.join(agent_config.capabilities)}",
        ]

        if parameters:
            prompt_parts.append(
                f"Additional context: {json.dumps(parameters, indent=2)}"
            )

        if task.results:
            # Include results from other agents if available
            other_results = {
                k: v.get("response", "")[:500] + "..."
                for k, v in task.results.items()
                if "response" in v
            }
            if other_results:
                prompt_parts.append(
                    f"Input from other agents: {json.dumps(other_results, indent=2)}"
                )

        return "\n\n".join(prompt_parts)

    async def analyze_project(
        self, project_path: str, analysis_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive project analysis

        Args:
            project_path: Path to project
            analysis_types: Types of analysis to perform

        Returns:
            Analysis results from all agents
        """
        if analysis_types is None:
            analysis_types = [
                "code_quality",
                "security",
                "performance",
                "documentation",
            ]

        results = {}

        # Map analysis types to agents
        analysis_agent_map = {
            "code_quality": [AgentRole.CODE_ANALYST, AgentRole.CODE_IMPROVER],
            "security": [AgentRole.SECURITY_EXPERT, AgentRole.INCIDENT_RESPONDER],
            "performance": [AgentRole.PERFORMANCE_OPTIMIZER, AgentRole.CODE_ANALYST],
            "documentation": [AgentRole.DOCUMENTATION_SPECIALIST],
            "intelligence": [
                AgentRole.INTELLIGENCE_GATHERER,
                AgentRole.OSINT_COLLECTOR,
            ],
            "quality": [AgentRole.QUALITY_ASSURANCE],
            "planning": [AgentRole.PROJECT_MANAGER],
        }

        # Execute analysis tasks
        for analysis_type in analysis_types:
            if analysis_type not in analysis_agent_map:
                logger.warning(f"Unknown analysis type: {analysis_type}")
                continue

            required_agents = analysis_agent_map[analysis_type]

            task = await self.execute_task(
                title=f"{analysis_type.title()} Analysis",
                description=f"Perform {analysis_type} analysis on the project at {project_path}",
                required_agents=required_agents,
                parameters={
                    "project_path": project_path,
                    "analysis_type": analysis_type,
                },
            )

            results[analysis_type] = task.results

        return results

    async def generate_improvement_report(
        self, analysis_results: Dict[str, Any]
    ) -> str:
        """
        Generate comprehensive improvement report

        Args:
            analysis_results: Results from project analysis

        Returns:
            Formatted improvement report
        """
        # Use project manager to consolidate results
        task = await self.execute_task(
            title="Generate Improvement Report",
            description="Consolidate all analysis results into a comprehensive improvement report",
            required_agents=[
                AgentRole.PROJECT_MANAGER,
                AgentRole.DOCUMENTATION_SPECIALIST,
            ],
            parameters={"analysis_results": analysis_results},
        )

        # Extract report from results
        pm_result = task.results.get(AgentRole.PROJECT_MANAGER.value, {})
        doc_result = task.results.get(AgentRole.DOCUMENTATION_SPECIALIST.value, {})

        report = pm_result.get("response", "") or doc_result.get("response", "")

        return report

    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        ai_status = self.ai_router.get_status()

        return {
            "orchestrator": {
                "active_tasks": len(self.active_tasks),
                "registered_agents": len(self.agents),
                "agent_roles": [role.value for role in self.agents.keys()],
            },
            "ai_router": ai_status,
            "agents": {
                role.value: {
                    "name": config.name,
                    "capabilities": config.capabilities,
                    "priority_models": config.priority_models,
                }
                for role, config in self.agents.items()
            },
        }

    async def test_agents(self) -> Dict[str, bool]:
        """Test all configured agents"""
        results = {}

        test_task = "Respond with 'OK' if you are operational."

        for role, config in self.agents.items():
            try:
                response, metadata = await agent_complete(
                    agent_name=config.name,
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are {config.name}. {config.description}",
                        },
                        {"role": "user", "content": test_task},
                    ],
                    preferred_models=config.priority_models,
                    max_tokens=10,
                )

                results[role.value] = True
                logger.info(f"✓ {config.name} is operational")

            except Exception as e:
                results[role.value] = False
                logger.error(f"✗ {config.name} failed: {e}")

        return results


# Singleton instance
_orchestrator_instance: Optional[UnifiedOrchestrator] = None


def get_orchestrator() -> UnifiedOrchestrator:
    """Get or create the singleton orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = UnifiedOrchestrator()
    return _orchestrator_instance
