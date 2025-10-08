"""
AMAS Agent Coordinator - Intelligent Multi-Agent Orchestration
Advanced Multi-Agent Intelligence System - Interactive Mode

This module provides intelligent coordination and orchestration of multiple
AI agents for complex task execution with dynamic load balancing and
real-time performance monitoring.
"""

import asyncio
import json
import logging
# import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

# Rich for enhanced output
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table


class AgentStatus(Enum):
    """Agent status enumeration"""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class TaskType(Enum):
    """Task type enumeration"""

    SECURITY_SCAN = "security_scan"
    CODE_ANALYSIS = "code_analysis"
    INTELLIGENCE_GATHERING = "intelligence_gathering"
    OSINT_INVESTIGATION = "osint_investigation"
    PERFORMANCE_MONITORING = "performance_monitoring"
    SECURITY_AUDIT = "security_audit"
    DOCUMENTATION_GENERATION = "documentation_generation"
    TESTING_COORDINATION = "testing_coordination"
    THREAT_ANALYSIS = "threat_analysis"
    INCIDENT_RESPONSE = "incident_response"


@dataclass
class Agent:
    """Agent data structure"""

    id: str
    name: str
    type: str
    status: AgentStatus
    capabilities: List[str]
    current_tasks: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 1
    performance_score: float = 1.0
    last_activity: datetime = field(default_factory=datetime.now)
    error_count: int = 0
    success_count: int = 0
    total_runtime: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.error_count
        return self.success_count / total if total > 0 else 1.0

    @property
    def is_available(self) -> bool:
        """Check if agent is available for new tasks"""
        return (
            self.status == AgentStatus.IDLE
            and len(self.current_tasks) < self.max_concurrent_tasks
        )


@dataclass
class TaskAssignment:
    """Task assignment data structure"""

    task_id: str
    agent_id: str
    assigned_at: datetime
    priority: int
    estimated_duration: float
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentCoordinator:
    """Intelligent Multi-Agent Coordinator"""

    def __init__(self, orchestrator, config: Dict[str, Any]):
        self.orchestrator = orchestrator
        self.config = config
        self.console = Console()
        self.logger = logging.getLogger(__name__)

        # Agent management
        self.agents: Dict[str, Agent] = {}
        self.task_assignments: Dict[str, TaskAssignment] = {}
        self.agent_queues: Dict[str, List[str]] = {}

        # Performance tracking
        self.performance_metrics = {
            "total_tasks_assigned": 0,
            "successful_completions": 0,
            "failed_completions": 0,
            "average_response_time": 0.0,
            "agent_utilization": {},
            "load_balancing_score": 0.0,
        }

        # Load balancing
        self.load_balancer = LoadBalancer()
        self.task_scheduler = TaskScheduler()

        # Initialize agents
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize available agents"""
        agent_configs = self.config.get("agents", {})

        # Security Expert Agent
        self._add_agent(
            Agent(
                id="security_expert",
                name="Security Expert Agent",
                type="security",
                status=AgentStatus.IDLE,
                capabilities=[
                    "vulnerability_scanning",
                    "penetration_testing",
                    "security_audit",
                    "threat_analysis",
                    "compliance_checking",
                    "incident_response",
                ],
                max_concurrent_tasks=3,
                performance_score=0.95,
            )
        )

        # Code Analysis Agent
        self._add_agent(
            Agent(
                id="code_analysis",
                name="Code Analysis Agent",
                type="analysis",
                status=AgentStatus.IDLE,
                capabilities=[
                    "static_code_analysis",
                    "code_quality_assessment",
                    "performance_optimization",
                    "security_vulnerability_detection",
                    "best_practices_review",
                    "technical_debt_analysis",
                ],
                max_concurrent_tasks=4,
                performance_score=0.92,
            )
        )

        # Intelligence Gathering Agent
        self._add_agent(
            Agent(
                id="intelligence_gathering",
                name="Intelligence Gathering Agent",
                type="intelligence",
                status=AgentStatus.IDLE,
                capabilities=[
                    "osint_investigation",
                    "social_media_analysis",
                    "domain_research",
                    "threat_intelligence",
                    "data_collection",
                    "pattern_analysis",
                ],
                max_concurrent_tasks=5,
                performance_score=0.88,
            )
        )

        # Performance Monitor Agent
        self._add_agent(
            Agent(
                id="performance_monitor",
                name="Performance Monitor Agent",
                type="monitoring",
                status=AgentStatus.IDLE,
                capabilities=[
                    "performance_profiling",
                    "resource_monitoring",
                    "bottleneck_identification",
                    "optimization_recommendations",
                    "capacity_planning",
                    "trend_analysis",
                ],
                max_concurrent_tasks=3,
                performance_score=0.90,
            )
        )

        # Documentation Specialist Agent
        self._add_agent(
            Agent(
                id="documentation_specialist",
                name="Documentation Specialist Agent",
                type="documentation",
                status=AgentStatus.IDLE,
                capabilities=[
                    "code_documentation",
                    "api_documentation",
                    "user_guide_generation",
                    "technical_writing",
                    "knowledge_extraction",
                    "document_analysis",
                ],
                max_concurrent_tasks=2,
                performance_score=0.85,
            )
        )

        # Testing Coordinator Agent
        self._add_agent(
            Agent(
                id="testing_coordinator",
                name="Testing Coordinator Agent",
                type="testing",
                status=AgentStatus.IDLE,
                capabilities=[
                    "test_case_generation",
                    "coverage_analysis",
                    "quality_assurance",
                    "automated_testing",
                    "test_strategy_development",
                    "regression_testing",
                ],
                max_concurrent_tasks=3,
                performance_score=0.87,
            )
        )

        # Integration Manager Agent
        self._add_agent(
            Agent(
                id="integration_manager",
                name="Integration Manager Agent",
                type="integration",
                status=AgentStatus.IDLE,
                capabilities=[
                    "service_orchestration",
                    "api_integration",
                    "workflow_coordination",
                    "system_architecture",
                    "microservices_management",
                    "event_driven_architecture",
                ],
                max_concurrent_tasks=2,
                performance_score=0.91,
            )
        )

        # Initialize agent queues
        for agent_id in self.agents:
            self.agent_queues[agent_id] = []

    def _add_agent(self, agent: Agent):
        """Add agent to coordinator"""
        self.agents[agent.id] = agent
        self.performance_metrics["agent_utilization"][agent.id] = 0.0
        self.logger.info(f"Added agent: {agent.name} ({agent.id})")

    async def coordinate_agents(
        self, task_config: Dict[str, Any], all_tasks: Dict[str, Any]
    ) -> List[str]:
        """Coordinate agents for task execution"""
        try:
            task_type = TaskType(task_config.get("intent", "general_analysis"))
            target = task_config.get("target", "general")
            priority = task_config.get("priority", 2)

            # Determine required agents based on task type
            required_agents = self._determine_required_agents(task_type, task_config)

            # Select best available agents
            selected_agents = await self._select_agents(required_agents, priority)

            if not selected_agents:
                raise Exception("No available agents for task execution")

            # Create task assignments
            task_id = task_config.get("metadata", {}).get(
                "task_id", str(uuid.uuid4())[:8]
            )
            assignments = await self._create_task_assignments(
                task_id, selected_agents, task_config
            )

            # Execute coordinated task
            results = await self._execute_coordinated_task(
                task_id, assignments, task_config
            )

            # Update performance metrics
            self._update_performance_metrics(selected_agents, True)

            return [agent.name for agent in selected_agents]

        except Exception as e:
            self.logger.error(f"Agent coordination failed: {e}")
            self._update_performance_metrics([], False)
            raise e

    def _determine_required_agents(
        self, task_type: TaskType, task_config: Dict[str, Any]
    ) -> List[str]:
        """Determine required agents based on task type"""
        agent_mapping = {
            TaskType.SECURITY_SCAN: ["security_expert", "intelligence_gathering"],
            TaskType.CODE_ANALYSIS: ["code_analysis", "security_expert"],
            TaskType.INTELLIGENCE_GATHERING: [
                "intelligence_gathering",
                "security_expert",
            ],
            TaskType.OSINT_INVESTIGATION: ["intelligence_gathering"],
            TaskType.PERFORMANCE_MONITORING: ["performance_monitor", "code_analysis"],
            TaskType.SECURITY_AUDIT: [
                "security_expert",
                "code_analysis",
                "testing_coordinator",
            ],
            TaskType.DOCUMENTATION_GENERATION: [
                "documentation_specialist",
                "code_analysis",
            ],
            TaskType.TESTING_COORDINATION: ["testing_coordinator", "code_analysis"],
            TaskType.THREAT_ANALYSIS: ["security_expert", "intelligence_gathering"],
            TaskType.INCIDENT_RESPONSE: [
                "security_expert",
                "intelligence_gathering",
                "integration_manager",
            ],
        }

        base_agents = agent_mapping.get(task_type, ["code_analysis"])

        # Add additional agents based on target complexity
        target = task_config.get("target", "")
        if "github.com" in target or "repository" in target.lower():
            if "code_analysis" not in base_agents:
                base_agents.append("code_analysis")
            if "documentation_specialist" not in base_agents:
                base_agents.append("documentation_specialist")

        if "security" in task_config.get("intent", "").lower():
            if "security_expert" not in base_agents:
                base_agents.append("security_expert")

        return base_agents

    async def _select_agents(
        self, required_agents: List[str], priority: int
    ) -> List[Agent]:
        """Select best available agents using load balancing"""
        available_agents = []

        for agent_id in required_agents:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                if agent.is_available:
                    available_agents.append(agent)

        if not available_agents:
            # Fallback: select any available agent with similar capabilities
            available_agents = [
                agent for agent in self.agents.values() if agent.is_available
            ]

        if not available_agents:
            return []

        # Use load balancer to select optimal agents
        selected_agents = self.load_balancer.select_agents(available_agents, priority)

        return selected_agents[:3]  # Limit to 3 agents for efficiency

    async def _create_task_assignments(
        self, task_id: str, agents: List[Agent], task_config: Dict[str, Any]
    ) -> List[TaskAssignment]:
        """Create task assignments for selected agents"""
        assignments = []

        for i, agent in enumerate(agents):
            assignment = TaskAssignment(
                task_id=task_id,
                agent_id=agent.id,
                assigned_at=datetime.now(),
                priority=task_config.get("priority", 2),
                estimated_duration=self._estimate_task_duration(agent, task_config),
                metadata={
                    "task_type": task_config.get("intent"),
                    "target": task_config.get("target"),
                    "agent_role": "primary" if i == 0 else "supporting",
                },
            )

            assignments.append(assignment)
            self.task_assignments[f"{task_id}_{agent.id}"] = assignment

            # Update agent status
            agent.current_tasks.append(task_id)
            agent.status = AgentStatus.BUSY
            agent.last_activity = datetime.now()

        return assignments

    def _estimate_task_duration(
        self, agent: Agent, task_config: Dict[str, Any]
    ) -> float:
        """Estimate task duration based on agent and task complexity"""
        base_duration = 30.0  # Base 30 seconds

        # Adjust based on agent performance
        duration = base_duration / agent.performance_score

        # Adjust based on task complexity
        target = task_config.get("target", "")
        if "github.com" in target:
            duration *= 1.5  # Repository analysis takes longer
        if "security" in task_config.get("intent", "").lower():
            duration *= 1.2  # Security tasks are more complex

        return min(duration, 300.0)  # Cap at 5 minutes

    async def _execute_coordinated_task(
        self,
        task_id: str,
        assignments: List[TaskAssignment],
        task_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute coordinated task across multiple agents"""
        try:
            # Create execution plan
            execution_plan = self._create_execution_plan(assignments, task_config)

            # Execute in phases
            results = {}
            for phase in execution_plan:
                phase_results = await self._execute_phase(phase, task_config)
                results.update(phase_results)

            # Consolidate results
            consolidated_results = self._consolidate_results(results, task_config)

            # Update agent status
            for assignment in assignments:
                agent = self.agents[assignment.agent_id]
                agent.current_tasks.remove(task_id)
                agent.status = AgentStatus.IDLE
                agent.success_count += 1
                agent.total_runtime += assignment.estimated_duration

            return consolidated_results

        except Exception as e:
            # Update agent status on failure
            for assignment in assignments:
                agent = self.agents[assignment.agent_id]
                if task_id in agent.current_tasks:
                    agent.current_tasks.remove(task_id)
                agent.status = AgentStatus.IDLE
                agent.error_count += 1

            raise e

    def _create_execution_plan(
        self, assignments: List[TaskAssignment], task_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create execution plan for coordinated task"""
        phases = []

        # Phase 1: Data collection and preparation
        data_collection_agents = [
            a
            for a in assignments
            if a.agent_id in ["intelligence_gathering", "code_analysis"]
        ]
        if data_collection_agents:
            phases.append(
                {
                    "name": "data_collection",
                    "agents": data_collection_agents,
                    "description": "Collecting and preparing data for analysis",
                }
            )

        # Phase 2: Analysis and processing
        analysis_agents = [
            a
            for a in assignments
            if a.agent_id in ["security_expert", "code_analysis", "performance_monitor"]
        ]
        if analysis_agents:
            phases.append(
                {
                    "name": "analysis",
                    "agents": analysis_agents,
                    "description": "Performing detailed analysis",
                }
            )

        # Phase 3: Documentation and reporting
        doc_agents = [
            a
            for a in assignments
            if a.agent_id in ["documentation_specialist", "testing_coordinator"]
        ]
        if doc_agents:
            phases.append(
                {
                    "name": "documentation",
                    "agents": doc_agents,
                    "description": "Generating documentation and reports",
                }
            )

        return phases

    async def _execute_phase(
        self, phase: Dict[str, Any], task_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single phase of the coordinated task"""
        phase_results = {}

        # Simulate parallel execution of agents in this phase
        tasks = []
        for assignment in phase["agents"]:
            task = asyncio.create_task(
                self._execute_agent_task(assignment, task_config)
            )
            tasks.append(task)

        # Wait for all agents in this phase to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(
                    f"Agent {phase['agents'][i].agent_id} failed: {result}"
                )
                phase_results[phase["agents"][i].agent_id] = {"error": str(result)}
            else:
                phase_results[phase["agents"][i].agent_id] = result

        return phase_results

    async def _execute_agent_task(
        self, assignment: TaskAssignment, task_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute individual agent task"""
        agent = self.agents[assignment.agent_id]

        # Simulate task execution
        await asyncio.sleep(
            min(assignment.estimated_duration / 10, 5.0)
        )  # Scale down for demo

        # Generate agent-specific results
        results = {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "task_type": assignment.metadata.get("task_type"),
            "execution_time": assignment.estimated_duration,
            "status": "completed",
        }

        # Add agent-specific analysis
        if agent.type == "security":
            results.update(
                {
                    "security_findings": 3,
                    "vulnerabilities": {"high": 0, "medium": 2, "low": 1},
                    "recommendations": [
                        "Update SSL configuration",
                        "Implement CSP headers",
                    ],
                }
            )
        elif agent.type == "analysis":
            results.update(
                {
                    "code_metrics": {"complexity": 15, "maintainability": 85},
                    "issues_found": 5,
                    "suggestions": ["Refactor complex functions", "Add unit tests"],
                }
            )
        elif agent.type == "intelligence":
            results.update(
                {
                    "sources_checked": 12,
                    "data_points": 45,
                    "confidence": 0.87,
                    "threat_level": "low",
                }
            )

        return results

    def _consolidate_results(
        self, results: Dict[str, Any], task_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Consolidate results from multiple agents"""
        consolidated = {
            "task_id": task_config.get("metadata", {}).get("task_id"),
            "intent": task_config.get("intent"),
            "target": task_config.get("target"),
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "agents_used": list(results.keys()),
            "consolidated_analysis": {},
        }

        # Consolidate security findings
        security_findings = []
        for agent_id, result in results.items():
            if "security_findings" in result:
                security_findings.append(result["security_findings"])

        if security_findings:
            consolidated["consolidated_analysis"]["total_security_findings"] = sum(
                security_findings
            )

        # Consolidate code metrics
        code_metrics = {}
        for agent_id, result in results.items():
            if "code_metrics" in result:
                code_metrics.update(result["code_metrics"])

        if code_metrics:
            consolidated["consolidated_analysis"]["code_quality"] = code_metrics

        # Consolidate intelligence data
        intelligence_data = {}
        for agent_id, result in results.items():
            if "sources_checked" in result:
                intelligence_data.update(
                    {
                        "sources_analyzed": result.get("sources_checked", 0),
                        "data_points": result.get("data_points", 0),
                        "confidence": result.get("confidence", 0.0),
                    }
                )

        if intelligence_data:
            consolidated["consolidated_analysis"]["intelligence"] = intelligence_data

        return consolidated

    def _update_performance_metrics(self, agents: List[Agent], success: bool):
        """Update performance metrics"""
        self.performance_metrics["total_tasks_assigned"] += 1

        if success:
            self.performance_metrics["successful_completions"] += 1
        else:
            self.performance_metrics["failed_completions"] += 1

        # Update agent utilization
        for agent in agents:
            if agent.id in self.performance_metrics["agent_utilization"]:
                self.performance_metrics["agent_utilization"][agent.id] += 1

        # Calculate load balancing score
        self._calculate_load_balancing_score()

    def _calculate_load_balancing_score(self):
        """Calculate load balancing score"""
        if not self.agents:
            return

        # Calculate utilization variance
        utilizations = list(self.performance_metrics["agent_utilization"].values())
        if not utilizations:
            return

        mean_utilization = sum(utilizations) / len(utilizations)
        variance = sum((u - mean_utilization) ** 2 for u in utilizations) / len(
            utilizations
        )

        # Convert variance to score (lower variance = better load balancing)
        self.performance_metrics["load_balancing_score"] = max(0, 1 - (variance / 100))

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        status = {
            "total_agents": len(self.agents),
            "available_agents": len(
                [a for a in self.agents.values() if a.is_available]
            ),
            "busy_agents": len(
                [a for a in self.agents.values() if a.status == AgentStatus.BUSY]
            ),
            "agents": {},
        }

        for agent_id, agent in self.agents.items():
            status["agents"][agent_id] = {
                "name": agent.name,
                "status": agent.status.value,
                "current_tasks": len(agent.current_tasks),
                "max_tasks": agent.max_concurrent_tasks,
                "success_rate": agent.success_rate,
                "performance_score": agent.performance_score,
                "last_activity": agent.last_activity.isoformat(),
            }

        return status

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics.copy()


class LoadBalancer:
    """Intelligent load balancer for agent selection"""

    def select_agents(
        self, available_agents: List[Agent], priority: int
    ) -> List[Agent]:
        """Select optimal agents using load balancing algorithm"""
        if not available_agents:
            return []

        # Sort by performance score and current load
        def agent_score(agent):
            # Higher performance score is better
            performance_score = agent.performance_score

            # Lower current load is better
            load_factor = len(agent.current_tasks) / agent.max_concurrent_tasks

            # Higher success rate is better
            success_rate = agent.success_rate

            # Combine factors (weighted)
            return (
                performance_score * 0.4 + (1 - load_factor) * 0.3 + success_rate * 0.3
            )

        # Sort agents by score (descending)
        sorted_agents = sorted(available_agents, key=agent_score, reverse=True)

        # Select top agents based on priority
        if priority >= 3:  # High priority
            return sorted_agents[:2]
        else:
            return sorted_agents[:1]


class TaskScheduler:
    """Task scheduler for managing task execution"""

    def __init__(self):
        self.scheduled_tasks = {}
        self.task_queue = []

    def schedule_task(
        self, task_id: str, execution_time: datetime, task_func: Callable
    ):
        """Schedule a task for future execution"""
        self.scheduled_tasks[task_id] = {
            "execution_time": execution_time,
            "task_func": task_func,
            "status": "scheduled",
        }

    def cancel_task(self, task_id: str):
        """Cancel a scheduled task"""
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id]["status"] = "cancelled"

    def get_next_tasks(self) -> List[str]:
        """Get tasks ready for execution"""
        now = datetime.now()
        ready_tasks = []

        for task_id, task_info in self.scheduled_tasks.items():
            if (
                task_info["status"] == "scheduled"
                and task_info["execution_time"] <= now
            ):
                ready_tasks.append(task_id)

        return ready_tasks
