"""
Hierarchical Agent Management System

Manages multi-layer agent coordination with Executive, Management, 
Specialist, and Execution layers for autonomous operation.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid
import json
from pathlib import Path

from .task_decomposer import AgentSpecialty, SubTask, WorkflowPlan, TaskComplexity

logger = logging.getLogger(__name__)

class AgentLayer(str, Enum):
    EXECUTIVE = "executive"        # Task coordination and quality supervision
    MANAGEMENT = "management"      # Team lead coordination
    SPECIALIST = "specialist"     # Domain expert agents
    EXECUTION = "execution"       # Tool and utility agents

class AgentRole(str, Enum):
    # Executive layer roles
    TASK_COORDINATOR = "task_coordinator"
    QUALITY_SUPERVISOR = "quality_supervisor"
    
    # Management layer roles
    RESEARCH_LEAD = "research_team_lead"
    ANALYSIS_LEAD = "analysis_team_lead"
    CREATIVE_LEAD = "creative_team_lead"
    QA_LEAD = "qa_team_lead"
    TECHNICAL_LEAD = "technical_team_lead"
    INTEGRATION_LEAD = "integration_team_lead"
    
    # Execution layer roles
    TOOL_MANAGER = "tool_manager"
    INTEGRATION_AGENT = "integration_agent"
    AUTOMATION_AGENT = "automation_agent"

class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    OFFLINE = "offline"
    FAILED = "failed"
    MAINTENANCE = "maintenance"

@dataclass
class AgentInstance:
    """Individual agent instance within the hierarchy"""
    id: str
    role: AgentRole
    specialty: Optional[AgentSpecialty] = None
    layer: AgentLayer = AgentLayer.SPECIALIST
    
    # Status and availability
    status: AgentStatus = AgentStatus.AVAILABLE
    current_tasks: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 3
    
    # Performance metrics
    success_rate: float = 0.95
    avg_completion_time: float = 1.0  # hours
    quality_score: float = 0.90
    cost_efficiency: float = 0.85
    
    # Coordination
    managed_agents: List[str] = field(default_factory=list)  # For management layer
    supervisor_id: Optional[str] = None
    
    # Health and reliability
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    failure_count: int = 0
    recovery_time: float = 0.0
    
    # Capabilities
    capabilities: Dict[str, Any] = field(default_factory=dict)
    tools_access: Set[str] = field(default_factory=set)
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks"""
        return (self.status == AgentStatus.AVAILABLE and 
                len(self.current_tasks) < self.max_concurrent_tasks)
    
    def get_load_percentage(self) -> float:
        """Get current load percentage"""
        return (len(self.current_tasks) / self.max_concurrent_tasks) * 100
    
    def is_healthy(self) -> bool:
        """Check agent health status"""
        time_since_heartbeat = (datetime.now(timezone.utc) - self.last_heartbeat).total_seconds()
        return (self.status not in [AgentStatus.FAILED, AgentStatus.OFFLINE] and
                time_since_heartbeat < 300 and  # 5 minutes
                self.failure_count < 3)

@dataclass
class TeamCoordination:
    """Coordination configuration for agent teams"""
    team_lead_id: str
    team_members: List[str]
    coordination_strategy: str = "parallel_with_sync_points"
    communication_frequency: int = 300  # seconds
    escalation_threshold: float = 0.8  # when to escalate to management
    
    # Team performance
    team_success_rate: float = 0.92
    avg_coordination_overhead: float = 0.05  # 5% overhead for coordination
    
class AgentHierarchyManager:
    """Manages multi-layer agent hierarchy and coordination"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInstance] = {}
        self.team_coordinators: Dict[str, TeamCoordination] = {}
        self.active_workflows: Dict[str, WorkflowPlan] = {}
        
        # Initialize hierarchy
        asyncio.create_task(self._initialize_agent_hierarchy())
        
        # Start background health monitoring
        asyncio.create_task(self._monitor_agent_health())
        
        logger.info("Agent Hierarchy Manager initialized")
    
    async def _initialize_agent_hierarchy(self):
        """Initialize the complete agent hierarchy"""
        # Executive layer
        await self._create_executive_agents()
        
        # Management layer
        await self._create_management_agents()
        
        # Specialist layer (create on-demand)
        await self._setup_specialist_pools()
        
        # Execution layer
        await self._create_execution_agents()
        
        logger.info(f"Agent hierarchy initialized with {len(self.agents)} agents")
    
    async def _create_executive_agents(self):
        """Create executive layer agents"""
        # Task Coordinator - receives and manages all user tasks
        task_coordinator = AgentInstance(
            id="exec_task_coordinator_001",
            role=AgentRole.TASK_COORDINATOR,
            layer=AgentLayer.EXECUTIVE,
            max_concurrent_tasks=10,  # Can coordinate many tasks
            capabilities={
                "task_analysis": 0.95,
                "resource_planning": 0.92,
                "workflow_optimization": 0.88,
                "stakeholder_communication": 0.93
            },
            tools_access={"task_decomposer", "resource_planner", "workflow_engine"}
        )
        
        # Quality Supervisor - ensures output quality across all tasks
        quality_supervisor = AgentInstance(
            id="exec_quality_supervisor_001",
            role=AgentRole.QUALITY_SUPERVISOR,
            layer=AgentLayer.EXECUTIVE,
            max_concurrent_tasks=8,
            capabilities={
                "quality_assessment": 0.97,
                "output_validation": 0.95,
                "process_optimization": 0.90,
                "compliance_checking": 0.93
            },
            tools_access={"quality_checker", "compliance_validator", "output_formatter"}
        )
        
        self.agents[task_coordinator.id] = task_coordinator
        self.agents[quality_supervisor.id] = quality_supervisor
    
    async def _create_management_agents(self):
        """Create management layer team leads"""
        management_configs = [
            {
                "id": "mgmt_research_lead_001",
                "role": AgentRole.RESEARCH_LEAD,
                "specialties_managed": [
                    AgentSpecialty.ACADEMIC_RESEARCHER, AgentSpecialty.WEB_INTELLIGENCE,
                    AgentSpecialty.NEWS_ANALYST, AgentSpecialty.COMPETITIVE_INTEL, AgentSpecialty.SOCIAL_MONITOR
                ],
                "capabilities": {
                    "research_planning": 0.93,
                    "source_validation": 0.91,
                    "team_coordination": 0.89,
                    "quality_control": 0.87
                }
            },
            {
                "id": "mgmt_analysis_lead_001",
                "role": AgentRole.ANALYSIS_LEAD,
                "specialties_managed": [
                    AgentSpecialty.DATA_ANALYST, AgentSpecialty.STATISTICAL_MODELER,
                    AgentSpecialty.PATTERN_RECOGNIZER, AgentSpecialty.RISK_ASSESSOR, AgentSpecialty.FINANCIAL_ANALYZER
                ],
                "capabilities": {
                    "analysis_design": 0.94,
                    "model_validation": 0.92,
                    "team_coordination": 0.88,
                    "accuracy_assurance": 0.90
                }
            },
            {
                "id": "mgmt_creative_lead_001",
                "role": AgentRole.CREATIVE_LEAD,
                "specialties_managed": [
                    AgentSpecialty.GRAPHICS_DESIGNER, AgentSpecialty.CONTENT_WRITER,
                    AgentSpecialty.PRESENTATION_FORMATTER, AgentSpecialty.MEDIA_PRODUCER, AgentSpecialty.INFOGRAPHIC_CREATOR
                ],
                "capabilities": {
                    "creative_direction": 0.91,
                    "brand_consistency": 0.93,
                    "team_coordination": 0.87,
                    "output_optimization": 0.89
                }
            },
            {
                "id": "mgmt_qa_lead_001",
                "role": AgentRole.QA_LEAD,
                "specialties_managed": [
                    AgentSpecialty.FACT_CHECKER, AgentSpecialty.QUALITY_CONTROLLER,
                    AgentSpecialty.COMPLIANCE_REVIEWER, AgentSpecialty.ERROR_DETECTOR, AgentSpecialty.DELIVERY_APPROVER
                ],
                "capabilities": {
                    "quality_assurance": 0.96,
                    "process_validation": 0.94,
                    "team_coordination": 0.90,
                    "compliance_expertise": 0.95
                }
            },
            {
                "id": "mgmt_technical_lead_001",
                "role": AgentRole.TECHNICAL_LEAD,
                "specialties_managed": [
                    AgentSpecialty.CODE_REVIEWER, AgentSpecialty.SYSTEM_ARCHITECT,
                    AgentSpecialty.SECURITY_ANALYST, AgentSpecialty.PERFORMANCE_ENGINEER, AgentSpecialty.DEVOPS_SPECIALIST
                ],
                "capabilities": {
                    "technical_architecture": 0.94,
                    "code_review": 0.92,
                    "security_analysis": 0.93,
                    "performance_optimization": 0.91,
                    "team_coordination": 0.88
                }
            },
            {
                "id": "mgmt_integration_lead_001",
                "role": AgentRole.INTEGRATION_LEAD,
                "specialties_managed": [
                    AgentSpecialty.SYSTEM_ARCHITECT, AgentSpecialty.DEVOPS_SPECIALIST
                ],
                "capabilities": {
                    "api_integration": 0.95,
                    "service_coordination": 0.92,
                    "workflow_automation": 0.90,
                    "team_coordination": 0.87,
                    "system_integration": 0.93
                }
            }
        ]
        
        for config in management_configs:
            agent = AgentInstance(
                id=config["id"],
                role=config["role"],
                layer=AgentLayer.MANAGEMENT,
                max_concurrent_tasks=6,
                capabilities=config["capabilities"],
                tools_access={"team_coordinator", "performance_monitor", "quality_gate"}
            )
            
            self.agents[agent.id] = agent
    
    async def _setup_specialist_pools(self):
        """Set up pools of specialist agents (created on-demand)"""
        # This creates the configuration for specialist pools
        # Actual agents created when needed to optimize resource usage
        self.specialist_pools = {
            # Research specialist pool
            "research_pool": {
                "max_agents": 5,
                "specialties": [
                    AgentSpecialty.ACADEMIC_RESEARCHER,
                    AgentSpecialty.WEB_INTELLIGENCE,
                    AgentSpecialty.NEWS_ANALYST,
                    AgentSpecialty.COMPETITIVE_INTEL,
                    AgentSpecialty.SOCIAL_MONITOR
                ],
                "default_config": {
                    "max_concurrent_tasks": 3,
                    "avg_completion_time": 1.5,
                    "quality_threshold": 0.90
                }
            },
            
            # Analysis specialist pool
            "analysis_pool": {
                "max_agents": 4,
                "specialties": [
                    AgentSpecialty.DATA_ANALYST,
                    AgentSpecialty.STATISTICAL_MODELER,
                    AgentSpecialty.PATTERN_RECOGNIZER,
                    AgentSpecialty.RISK_ASSESSOR,
                    AgentSpecialty.FINANCIAL_ANALYZER
                ],
                "default_config": {
                    "max_concurrent_tasks": 2,
                    "avg_completion_time": 2.0,
                    "quality_threshold": 0.93
                }
            },
            
            # Creative specialist pool
            "creative_pool": {
                "max_agents": 4,
                "specialties": [
                    AgentSpecialty.GRAPHICS_DESIGNER,
                    AgentSpecialty.CONTENT_WRITER,
                    AgentSpecialty.PRESENTATION_FORMATTER,
                    AgentSpecialty.MEDIA_PRODUCER,
                    AgentSpecialty.INFOGRAPHIC_CREATOR
                ],
                "default_config": {
                    "max_concurrent_tasks": 3,
                    "avg_completion_time": 1.2,
                    "quality_threshold": 0.88
                }
            },
            
            # QA specialist pool
            "qa_pool": {
                "max_agents": 3,
                "specialties": [
                    AgentSpecialty.FACT_CHECKER,
                    AgentSpecialty.QUALITY_CONTROLLER,
                    AgentSpecialty.COMPLIANCE_REVIEWER,
                    AgentSpecialty.ERROR_DETECTOR,
                    AgentSpecialty.DELIVERY_APPROVER
                ],
                "default_config": {
                    "max_concurrent_tasks": 4,
                    "avg_completion_time": 0.8,
                    "quality_threshold": 0.95
                }
            }
        }
    
    async def _create_execution_agents(self):
        """Create execution layer utility agents"""
        execution_configs = [
            {
                "id": "exec_tool_manager_001",
                "role": AgentRole.TOOL_MANAGER,
                "capabilities": {
                    "file_management": 0.90,
                    "database_operations": 0.88,
                    "code_execution": 0.85,
                    "media_processing": 0.87
                },
                "tools_access": {"file_system", "databases", "code_executor", "media_tools"}
            },
            {
                "id": "exec_integration_agent_001",
                "role": AgentRole.INTEGRATION_AGENT,
                "capabilities": {
                    "api_integration": 0.92,
                    "n8n_workflows": 0.89,
                    "oauth_management": 0.91,
                    "service_coordination": 0.86
                },
                "tools_access": {"api_gateway", "n8n_connector", "oauth_client", "service_registry"}
            },
            {
                "id": "exec_automation_agent_001",
                "role": AgentRole.AUTOMATION_AGENT,
                "capabilities": {
                    "task_scheduling": 0.94,
                    "event_monitoring": 0.88,
                    "notification_delivery": 0.91,
                    "workflow_automation": 0.86
                },
                "tools_access": {"scheduler", "event_monitor", "notification_service", "workflow_engine"}
            }
        ]
        
        for config in execution_configs:
            agent = AgentInstance(
                id=config["id"],
                role=config["role"],
                layer=AgentLayer.EXECUTION,
                max_concurrent_tasks=8,  # Execution agents can handle more
                capabilities=config["capabilities"],
                tools_access=config["tools_access"]
            )
            
            self.agents[agent.id] = agent
    
    async def create_specialist_agent(self, 
                                    specialty: AgentSpecialty, 
                                    urgency: str = "normal") -> str:
        """Create a new specialist agent on-demand"""
        # Find appropriate pool
        pool_name = None
        for pool, config in self.specialist_pools.items():
            if specialty in config["specialties"]:
                pool_name = pool
                break
        
        if not pool_name:
            raise ValueError(f"No pool configured for specialty: {specialty}")
        
        pool_config = self.specialist_pools[pool_name]
        
        # Check if pool has capacity
        existing_agents = [a for a in self.agents.values() 
                          if a.specialty == specialty]
        
        if len(existing_agents) >= pool_config["max_agents"]:
            # Try to find available agent instead of creating new
            available_agent = next((a for a in existing_agents if a.is_available()), None)
            if available_agent:
                return available_agent.id
            else:
                logger.warning(f"Specialist pool for {specialty} is at capacity")
                return None
        
        # Create new specialist agent
        agent_id = f"spec_{specialty.value}_{len(existing_agents)+1:03d}"
        
        from .task_decomposer import TaskDecomposer
        decomposer = TaskDecomposer()
        capabilities_data = decomposer.specialist_capabilities.get(specialty, {})
        
        specialist_agent = AgentInstance(
            id=agent_id,
            role=AgentRole.RESEARCH_LEAD,  # Will be updated based on specialty
            specialty=specialty,
            layer=AgentLayer.SPECIALIST,
            max_concurrent_tasks=capabilities_data.get("max_parallel_tasks", 3),
            avg_completion_time=capabilities_data.get("avg_task_duration", 1.0),
            quality_score=capabilities_data.get("quality_score", 0.90),
            capabilities={
                "domain_expertise": 0.90,
                "task_execution": 0.88,
                "quality_delivery": capabilities_data.get("quality_score", 0.90),
                "collaboration": 0.85
            },
            tools_access=set(capabilities_data.get("tools", []))
        )
        
        # Assign to appropriate team lead
        team_lead_id = await self._find_appropriate_team_lead(specialty)
        if team_lead_id:
            specialist_agent.supervisor_id = team_lead_id
            self.agents[team_lead_id].managed_agents.append(agent_id)
        
        self.agents[agent_id] = specialist_agent
        
        logger.info(f"Created specialist agent {agent_id} for {specialty.value}")
        return agent_id
    
    async def _find_appropriate_team_lead(self, specialty: AgentSpecialty) -> Optional[str]:
        """
        Find the appropriate team lead for a specialty.
        
        Maps specialist agents to their corresponding management layer team leads
        based on domain expertise and organizational structure.
        
        Args:
            specialty: The specialist agent type
            
        Returns:
            Team lead agent ID if found, None otherwise
        """
        specialty_to_lead = {
            # Research specialists -> Research Lead
            AgentSpecialty.ACADEMIC_RESEARCHER: AgentRole.RESEARCH_LEAD,
            AgentSpecialty.WEB_INTELLIGENCE: AgentRole.RESEARCH_LEAD,
            AgentSpecialty.NEWS_ANALYST: AgentRole.RESEARCH_LEAD,
            AgentSpecialty.COMPETITIVE_INTEL: AgentRole.RESEARCH_LEAD,
            AgentSpecialty.SOCIAL_MONITOR: AgentRole.RESEARCH_LEAD,
            
            # Analysis specialists -> Analysis Lead
            AgentSpecialty.DATA_ANALYST: AgentRole.ANALYSIS_LEAD,
            AgentSpecialty.STATISTICAL_MODELER: AgentRole.ANALYSIS_LEAD,
            AgentSpecialty.PATTERN_RECOGNIZER: AgentRole.ANALYSIS_LEAD,
            AgentSpecialty.RISK_ASSESSOR: AgentRole.ANALYSIS_LEAD,
            AgentSpecialty.FINANCIAL_ANALYZER: AgentRole.ANALYSIS_LEAD,
            
            # Creative specialists -> Creative Lead
            AgentSpecialty.GRAPHICS_DESIGNER: AgentRole.CREATIVE_LEAD,
            AgentSpecialty.CONTENT_WRITER: AgentRole.CREATIVE_LEAD,
            AgentSpecialty.PRESENTATION_FORMATTER: AgentRole.CREATIVE_LEAD,
            AgentSpecialty.MEDIA_PRODUCER: AgentRole.CREATIVE_LEAD,
            AgentSpecialty.INFOGRAPHIC_CREATOR: AgentRole.CREATIVE_LEAD,
            
            # QA specialists -> QA Lead
            AgentSpecialty.FACT_CHECKER: AgentRole.QA_LEAD,
            AgentSpecialty.QUALITY_CONTROLLER: AgentRole.QA_LEAD,
            AgentSpecialty.COMPLIANCE_REVIEWER: AgentRole.QA_LEAD,
            AgentSpecialty.ERROR_DETECTOR: AgentRole.QA_LEAD,
            AgentSpecialty.DELIVERY_APPROVER: AgentRole.QA_LEAD,
            
            # Technical specialists -> Technical Lead
            AgentSpecialty.CODE_REVIEWER: AgentRole.TECHNICAL_LEAD,
            AgentSpecialty.SYSTEM_ARCHITECT: AgentRole.TECHNICAL_LEAD,
            AgentSpecialty.SECURITY_ANALYST: AgentRole.TECHNICAL_LEAD,
            AgentSpecialty.PERFORMANCE_ENGINEER: AgentRole.TECHNICAL_LEAD,
            AgentSpecialty.DEVOPS_SPECIALIST: AgentRole.TECHNICAL_LEAD,
            
            # Investigation specialists -> Technical Lead (security/investigation focus)
            AgentSpecialty.DIGITAL_FORENSICS: AgentRole.TECHNICAL_LEAD,
            AgentSpecialty.NETWORK_ANALYZER: AgentRole.TECHNICAL_LEAD,
            AgentSpecialty.REVERSE_ENGINEER: AgentRole.TECHNICAL_LEAD,
            AgentSpecialty.CASE_INVESTIGATOR: AgentRole.TECHNICAL_LEAD,
            AgentSpecialty.EVIDENCE_COMPILER: AgentRole.TECHNICAL_LEAD
        }
        
        target_role = specialty_to_lead.get(specialty)
        if not target_role:
            # Default to Integration Lead for unmapped specialties
            target_role = AgentRole.INTEGRATION_LEAD
        
        # Find team lead with this role
        for agent in self.agents.values():
            if agent.role == target_role and agent.layer == AgentLayer.MANAGEMENT:
                return agent.id
        
        # If no team lead found, return None (will be handled by caller)
        return None
    
    async def assign_workflow_to_agents(self, workflow: WorkflowPlan) -> Dict[str, str]:
        """
        Assign workflow sub-tasks to appropriate agents with load balancing.
        
        This method performs intelligent agent assignment by:
        1. Ensuring all required specialists are available (creating if needed)
        2. Selecting optimal agents based on load, performance, and availability
        3. Distributing tasks to balance workload across agent pool
        4. Handling agent capacity constraints
        
        Args:
            workflow: The workflow plan with sub-tasks to assign
            
        Returns:
            Dictionary mapping task_id -> agent_id
            
        Raises:
            RuntimeError: If unable to assign agents for required specialties
        """
        assignments = {}
        
        logger.info(f"Assigning workflow {workflow.id} with {len(workflow.sub_tasks)} sub-tasks")
        
        # Pre-allocate agents for all required specialties
        specialty_agent_pools = {}
        for specialty in workflow.required_specialists:
            available_agents = await self._get_available_specialists(specialty)
            
            if not available_agents:
                # Create new specialist agent
                agent_id = await self.create_specialist_agent(specialty)
                if agent_id:
                    available_agents = [agent_id]
                    logger.info(f"Created new {specialty.value} agent: {agent_id}")
            
            if not available_agents:
                # Try one more time with high urgency
                agent_id = await self.create_specialist_agent(specialty, urgency="critical")
                if agent_id:
                    available_agents = [agent_id]
            
            if not available_agents:
                raise RuntimeError(
                    f"Unable to assign agent for specialty: {specialty.value}. "
                    f"Pool may be exhausted or agents are unhealthy."
                )
            
            specialty_agent_pools[specialty] = available_agents
        
        # Assign each sub-task to appropriate agent with load balancing
        for sub_task in workflow.sub_tasks:
            # Get available agents for this task's specialty
            available_agents = specialty_agent_pools.get(sub_task.assigned_agent, [])
            
            if not available_agents:
                # Fallback: try to get or create agents
                available_agents = await self._get_available_specialists(sub_task.assigned_agent)
                if not available_agents:
                    agent_id = await self.create_specialist_agent(sub_task.assigned_agent)
                    if agent_id:
                        available_agents = [agent_id]
            
            if available_agents:
                # Choose best available agent based on load and performance
                best_agent_id = await self._select_optimal_agent(available_agents, sub_task)
                
                # Verify agent can accept the task
                agent = self.agents.get(best_agent_id)
                if agent and agent.is_available():
                    # Assign task to agent
                    assignments[sub_task.id] = best_agent_id
                    agent.current_tasks.append(sub_task.id)
                    
                    # Update agent status if needed
                    if len(agent.current_tasks) >= agent.max_concurrent_tasks:
                        agent.status = AgentStatus.BUSY
                    
                    logger.debug(f"Assigned {sub_task.id} to {best_agent_id} "
                              f"(load: {agent.get_load_percentage():.1f}%)")
                else:
                    logger.warning(f"Selected agent {best_agent_id} is no longer available, "
                                 f"selecting alternative...")
                    # Remove unavailable agent and retry
                    available_agents.remove(best_agent_id)
                    if available_agents:
                        best_agent_id = await self._select_optimal_agent(available_agents, sub_task)
                        assignments[sub_task.id] = best_agent_id
                        self.agents[best_agent_id].current_tasks.append(sub_task.id)
                    else:
                        logger.error(f"No available agents for sub-task: {sub_task.id}")
            else:
                logger.error(f"No available agents for sub-task: {sub_task.id} "
                           f"(specialty: {sub_task.assigned_agent.value})")
        
        # Store workflow for tracking
        self.active_workflows[workflow.id] = workflow
        
        # Log assignment summary
        unique_agents = len(set(assignments.values()))
        logger.info(
            f"Workflow assignment complete: {len(assignments)}/{len(workflow.sub_tasks)} tasks assigned "
            f"to {unique_agents} agents"
        )
        
        return assignments
    
    async def _get_available_specialists(self, specialty: AgentSpecialty) -> List[str]:
        """Get list of available agents for a specific specialty"""
        available = []
        
        for agent in self.agents.values():
            if (agent.specialty == specialty and 
                agent.is_available() and 
                agent.is_healthy()):
                available.append(agent.id)
        
        return available
    
    async def _select_optimal_agent(self, 
                                  available_agents: List[str], 
                                  sub_task: SubTask) -> str:
        """Select the optimal agent from available options"""
        if len(available_agents) == 1:
            return available_agents[0]
        
        # Score each agent based on multiple factors
        agent_scores = []
        
        for agent_id in available_agents:
            agent = self.agents[agent_id]
            
            # Calculate composite score
            load_score = 1.0 - (agent.get_load_percentage() / 100)  # Lower load = better
            quality_score = agent.quality_score
            success_rate_score = agent.success_rate
            efficiency_score = 1.0 / agent.avg_completion_time  # Faster = better
            
            composite_score = (
                load_score * 0.3 +
                quality_score * 0.3 +
                success_rate_score * 0.25 +
                efficiency_score * 0.15
            )
            
            agent_scores.append((agent_id, composite_score))
        
        # Return agent with highest score
        best_agent = max(agent_scores, key=lambda x: x[1])
        return best_agent[0]
    
    async def _monitor_agent_health(self):
        """Background task to monitor agent health and handle failures"""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                for agent_id, agent in list(self.agents.items()):
                    # Check heartbeat
                    time_since_heartbeat = (current_time - agent.last_heartbeat).total_seconds()
                    
                    if time_since_heartbeat > 300:  # 5 minutes
                        logger.warning(f"Agent {agent_id} missed heartbeat")
                        await self._handle_agent_failure(agent_id, "missed_heartbeat")
                    
                    # Check failure count
                    if agent.failure_count >= 3:
                        logger.error(f"Agent {agent_id} exceeded failure threshold")
                        await self._handle_agent_failure(agent_id, "failure_threshold")
                    
                    # Update agent status based on health
                    if not agent.is_healthy() and agent.status != AgentStatus.FAILED:
                        agent.status = AgentStatus.FAILED
                        await self._handle_agent_failure(agent_id, "health_check_failed")
                
                # Sleep before next health check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _handle_agent_failure(self, failed_agent_id: str, reason: str):
        """Handle agent failure with automatic recovery"""
        logger.error(f"Handling failure for agent {failed_agent_id}: {reason}")
        
        failed_agent = self.agents.get(failed_agent_id)
        if not failed_agent:
            return
        
        # Mark agent as failed
        failed_agent.status = AgentStatus.FAILED
        
        # Redistribute current tasks
        if failed_agent.current_tasks:
            await self._redistribute_tasks(failed_agent_id, failed_agent.current_tasks)
        
        # For specialist agents, create replacement if needed
        if (failed_agent.layer == AgentLayer.SPECIALIST and 
            failed_agent.specialty):
            
            # Create replacement agent
            replacement_id = await self.create_specialist_agent(
                failed_agent.specialty, urgency="high"
            )
            
            if replacement_id:
                logger.info(f"Created replacement agent {replacement_id} for {failed_agent_id}")
                
                # Update team lead's managed agents
                if failed_agent.supervisor_id:
                    supervisor = self.agents.get(failed_agent.supervisor_id)
                    if supervisor:
                        try:
                            supervisor.managed_agents.remove(failed_agent_id)
                            supervisor.managed_agents.append(replacement_id)
                        except ValueError:
                            pass  # Agent not in managed list
        
        # Remove failed agent after replacement
        if failed_agent.layer == AgentLayer.SPECIALIST:
            del self.agents[failed_agent_id]
        else:
            # For critical agents (executive/management), keep for manual recovery
            failed_agent.status = AgentStatus.OFFLINE
    
    async def _redistribute_tasks(self, failed_agent_id: str, task_ids: List[str]):
        """Redistribute tasks from failed agent to available agents"""
        failed_agent = self.agents.get(failed_agent_id)
        if not failed_agent or not failed_agent.specialty:
            return
        
        # Find available agents with same specialty
        available_agents = await self._get_available_specialists(failed_agent.specialty)
        
        if not available_agents:
            # Create new agent if none available
            new_agent_id = await self.create_specialist_agent(
                failed_agent.specialty, urgency="critical"
            )
            if new_agent_id:
                available_agents = [new_agent_id]
        
        # Redistribute tasks
        for task_id in task_ids:
            if available_agents:
                # Find best agent for redistribution
                target_agent_id = available_agents[0]  # Simple round-robin for now
                
                # Assign task to new agent
                self.agents[target_agent_id].current_tasks.append(task_id)
                
                logger.info(f"Redistributed task {task_id} from {failed_agent_id} to {target_agent_id}")
                
                # Rotate for next task
                available_agents = available_agents[1:] + [available_agents[0]]
        
        # Clear failed agent's tasks
        failed_agent.current_tasks = []
    
    async def get_workflow_progress(self, workflow_id: str) -> Dict[str, Any]:
        """Get current progress of a workflow"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        # Calculate progress
        total_tasks = len(workflow.sub_tasks)
        completed_tasks = sum(1 for task in workflow.sub_tasks 
                             if task.status == "completed")
        in_progress_tasks = sum(1 for task in workflow.sub_tasks 
                               if task.status == "in_progress")
        
        progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Get agent status for each task
        agent_status = {}
        for task in workflow.sub_tasks:
            # Find assigned agent
            assigned_agent_id = None
            for agent_id, agent in self.agents.items():
                if task.id in agent.current_tasks:
                    assigned_agent_id = agent_id
                    break
            
            if assigned_agent_id:
                agent = self.agents[assigned_agent_id]
                agent_status[task.id] = {
                    "agent_id": assigned_agent_id,
                    "agent_status": agent.status.value,
                    "agent_load": agent.get_load_percentage(),
                    "task_status": task.status
                }
        
        # Estimate remaining time
        remaining_tasks = [task for task in workflow.sub_tasks if task.status != "completed"]
        estimated_remaining_hours = sum(task.estimated_duration_hours for task in remaining_tasks)
        
        return {
            "workflow_id": workflow_id,
            "progress_percentage": round(progress_percentage, 1),
            "tasks_completed": completed_tasks,
            "tasks_in_progress": in_progress_tasks,
            "tasks_pending": total_tasks - completed_tasks - in_progress_tasks,
            "estimated_remaining_hours": round(estimated_remaining_hours, 1),
            "agent_status": agent_status,
            "current_phase": self._get_current_phase(workflow),
            "overall_health": self._assess_workflow_health(workflow_id)
        }
    
    def _get_current_phase(self, workflow: WorkflowPlan) -> str:
        """Determine current execution phase of workflow"""
        # Find which phase has active tasks
        for phase in workflow.execution_phases:
            phase_tasks = [task for task in workflow.sub_tasks 
                          if task.parallel_group == phase]
            
            active_tasks = [task for task in phase_tasks 
                           if task.status in ["in_progress", "pending"]]
            
            if active_tasks:
                return phase
        
        # If no active tasks, check if all completed
        all_completed = all(task.status == "completed" for task in workflow.sub_tasks)
        if all_completed:
            return "completed"
        else:
            return "initializing"
    
    def _assess_workflow_health(self, workflow_id: str) -> str:
        """Assess overall health of workflow execution"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return "unknown"
        
        # Check for failed tasks
        failed_tasks = [task for task in workflow.sub_tasks if task.status == "failed"]
        if failed_tasks:
            return "degraded"
        
        # Check for overdue tasks
        current_time = datetime.now(timezone.utc)
        overdue_tasks = []
        for task in workflow.sub_tasks:
            if (task.status == "in_progress" and 
                task.started_at and 
                (current_time - task.started_at).total_seconds() > 
                task.estimated_duration_hours * 3600 * 1.5):  # 50% overtime
                overdue_tasks.append(task)
        
        if overdue_tasks:
            return "warning"
        
        # Check agent health for assigned agents
        unhealthy_agents = 0
        total_agents = 0
        
        for task in workflow.sub_tasks:
            for agent in self.agents.values():
                if task.id in agent.current_tasks:
                    total_agents += 1
                    if not agent.is_healthy():
                        unhealthy_agents += 1
        
        if total_agents > 0 and (unhealthy_agents / total_agents) > 0.2:  # >20% unhealthy
            return "warning"
        
        return "healthy"
    
    async def request_specialist_help(self, 
                                    requesting_agent_id: str,
                                    required_specialty: AgentSpecialty,
                                    help_context: Dict[str, Any]) -> Optional[str]:
        """Route help requests between specialists"""
        logger.info(f"Agent {requesting_agent_id} requesting help from {required_specialty.value}")
        
        # Find available specialist
        available_specialists = await self._get_available_specialists(required_specialty)
        
        if not available_specialists:
            # Try to create new specialist
            new_specialist_id = await self.create_specialist_agent(required_specialty, urgency="high")
            if new_specialist_id:
                available_specialists = [new_specialist_id]
        
        if not available_specialists:
            logger.warning(f"No available specialists for help request: {required_specialty.value}")
            return None
        
        # Select best specialist for help
        helper_agent_id = available_specialists[0]  # Simple selection for now
        
        # Create coordination task
        coordination_task_id = f"coord_{uuid.uuid4().hex[:8]}"
        
        # Log coordination
        logger.info(f"Coordinating help: {requesting_agent_id} <-> {helper_agent_id} for {coordination_task_id}")
        
        return helper_agent_id
    
    def get_hierarchy_status(self) -> Dict[str, Any]:
        """Get complete hierarchy status for monitoring"""
        status = {
            "total_agents": len(self.agents),
            "active_workflows": len(self.active_workflows),
            "layer_breakdown": {},
            "health_summary": {
                "healthy": 0,
                "degraded": 0,
                "failed": 0,
                "offline": 0
            },
            "load_summary": {
                "available": 0,
                "busy": 0,
                "overloaded": 0
            }
        }
        
        # Analyze by layer
        for layer in AgentLayer:
            layer_agents = [a for a in self.agents.values() if a.layer == layer]
            status["layer_breakdown"][layer.value] = {
                "count": len(layer_agents),
                "available": sum(1 for a in layer_agents if a.is_available()),
                "avg_load": sum(a.get_load_percentage() for a in layer_agents) / len(layer_agents) if layer_agents else 0
            }
        
        # Health and load summaries
        for agent in self.agents.values():
            if agent.is_healthy():
                status["health_summary"]["healthy"] += 1
            elif agent.status == AgentStatus.FAILED:
                status["health_summary"]["failed"] += 1
            elif agent.status == AgentStatus.OFFLINE:
                status["health_summary"]["offline"] += 1
            else:
                status["health_summary"]["degraded"] += 1
            
            if agent.is_available():
                status["load_summary"]["available"] += 1
            elif agent.get_load_percentage() > 90:
                status["load_summary"]["overloaded"] += 1
            else:
                status["load_summary"]["busy"] += 1
        
        return status

# Global hierarchy manager
_global_hierarchy_manager: Optional[AgentHierarchyManager] = None

def get_hierarchy_manager() -> AgentHierarchyManager:
    """Get global agent hierarchy manager instance"""
    global _global_hierarchy_manager
    if _global_hierarchy_manager is None:
        _global_hierarchy_manager = AgentHierarchyManager()
    return _global_hierarchy_manager
