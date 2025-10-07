"""
Unified AMAS Intelligence Orchestrator

This module implements the consolidated orchestrator for the AMAS Intelligence System,
combining the best features from all previous orchestrator implementations.
"""

import asyncio
import json
import logging
import os
import traceback
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from ..config.ai_config import AIProvider, AIConfigManager, get_ai_config
from ..services.llm_service import LLMService
from ..services.vector_service import VectorService
from ..services.knowledge_graph_service import KnowledgeGraphService
from ..services.security_service import SecurityService
from ..agents.base.intelligence_agent import AgentStatus, IntelligenceAgent
from ..agents.data_analysis.data_analysis_agent import DataAnalysisAgent
from ..agents.forensics.forensics_agent import ForensicsAgent
from ..agents.investigation.investigation_agent import InvestigationAgent
from ..agents.metadata.metadata_agent import MetadataAgent
from ..agents.osint.osint_agent import OSINTAgent
from ..agents.reporting.reporting_agent import ReportingAgent
from ..agents.reverse_engineering.reverse_engineering_agent import ReverseEngineeringAgent
from ..agents.technology_monitor.technology_monitor_agent import TechnologyMonitorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/unified_orchestrator.log"),
        logging.StreamHandler()
    ],
)
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
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class IntelligenceTask:
    """Intelligence task definition"""
    id: str
    title: str
    description: str
    agent_type: AgentType
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class OrchestrationResult:
    """Result of orchestration operation"""
    success: bool
    task_id: str
    agent_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class ProviderManager:
    """Manages AI providers with fallback and circuit breaker logic"""
    
    def __init__(self, ai_config: AIConfigManager):
        self.ai_config = ai_config
        self.circuit_breakers: Dict[AIProvider, Dict[str, Any]] = {}
        self.provider_stats: Dict[AIProvider, Dict[str, Any]] = {}
        self._initialize_circuit_breakers()
    
    def _initialize_circuit_breakers(self):
        """Initialize circuit breakers for all providers"""
        for provider in AIProvider:
            self.circuit_breakers[provider] = {
                "failures": 0,
                "last_failure": None,
                "state": "closed",  # closed, open, half-open
                "failure_threshold": 5,
                "recovery_timeout": 300,  # 5 minutes
            }
            self.provider_stats[provider] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0,
                "last_used": None,
            }
    
    def get_available_providers(self) -> List[AIProvider]:
        """Get list of available providers in priority order"""
        enabled_providers = self.ai_config.get_enabled_providers()
        available = []
        
        for provider, config in enabled_providers.items():
            if self._is_provider_available(provider):
                available.append(provider)
        
        # Sort by priority
        return sorted(available, key=lambda p: enabled_providers[p].priority)
    
    def _is_provider_available(self, provider: AIProvider) -> bool:
        """Check if provider is available (not circuit-broken)"""
        circuit = self.circuit_breakers[provider]
        
        if circuit["state"] == "closed":
            return True
        elif circuit["state"] == "open":
            # Check if recovery timeout has passed
            if circuit["last_failure"]:
                time_since_failure = (datetime.now() - circuit["last_failure"]).total_seconds()
                if time_since_failure > circuit["recovery_timeout"]:
                    circuit["state"] = "half-open"
                    return True
            return False
        else:  # half-open
            return True
    
    def record_success(self, provider: AIProvider, response_time: float):
        """Record successful request"""
        circuit = self.circuit_breakers[provider]
        stats = self.provider_stats[provider]
        
        # Reset circuit breaker
        circuit["failures"] = 0
        circuit["state"] = "closed"
        circuit["last_failure"] = None
        
        # Update stats
        stats["total_requests"] += 1
        stats["successful_requests"] += 1
        stats["last_used"] = datetime.now()
        
        # Update average response time
        if stats["average_response_time"] == 0:
            stats["average_response_time"] = response_time
        else:
            stats["average_response_time"] = (stats["average_response_time"] + response_time) / 2
    
    def record_failure(self, provider: AIProvider, error: str):
        """Record failed request"""
        circuit = self.circuit_breakers[provider]
        stats = self.provider_stats[provider]
        
        circuit["failures"] += 1
        circuit["last_failure"] = datetime.now()
        stats["total_requests"] += 1
        stats["failed_requests"] += 1
        
        if circuit["failures"] >= circuit["failure_threshold"]:
            circuit["state"] = "open"
            logger.warning(f"Circuit breaker opened for provider {provider.value}")
    
    def get_provider_health(self) -> Dict[str, Any]:
        """Get health status of all providers"""
        health = {}
        for provider in AIProvider:
            config = self.ai_config.get_provider_config(provider)
            circuit = self.circuit_breakers[provider]
            stats = self.provider_stats[provider]
            
            health[provider.value] = {
                "enabled": config.enabled if config else False,
                "circuit_state": circuit["state"],
                "failures": circuit["failures"],
                "available": self._is_provider_available(provider),
                "stats": stats.copy(),
            }
        
        return health


class UnifiedIntelligenceOrchestrator:
    """
    Unified Intelligence Orchestrator
    
    Consolidates all orchestrator functionality with:
    - Provider management with circuit breakers
    - Adaptive routing and failover
    - Task queue management
    - Agent lifecycle management
    - Performance monitoring
    """
    
    def __init__(
        self,
        ai_config: Optional[AIConfigManager] = None,
        llm_service: Optional[LLMService] = None,
        vector_service: Optional[VectorService] = None,
        knowledge_graph: Optional[KnowledgeGraphService] = None,
        security_service: Optional[SecurityService] = None,
    ):
        self.ai_config = ai_config or get_ai_config()
        self.provider_manager = ProviderManager(self.ai_config)
        
        # Services
        self.llm_service = llm_service
        self.vector_service = vector_service
        self.knowledge_graph = knowledge_graph
        self.security_service = security_service
        
        # Agent registry
        self.agents: Dict[str, IntelligenceAgent] = {}
        self.agent_types: Dict[AgentType, List[str]] = {
            agent_type: [] for agent_type in AgentType
        }
        
        # Task management
        self.task_queue: List[IntelligenceTask] = []
        self.active_tasks: Dict[str, IntelligenceTask] = {}
        self.completed_tasks: List[IntelligenceTask] = []
        
        # Performance tracking
        self.performance_metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0,
            "agent_utilization": {},
        }
        
        # Configuration
        self.max_concurrent_tasks = int(os.getenv("AMAS_MAX_CONCURRENT_TASKS", "10"))
        self.task_timeout = int(os.getenv("AMAS_TASK_TIMEOUT", "300"))  # 5 minutes
        
        logger.info("Unified Intelligence Orchestrator initialized")
    
    async def initialize(self):
        """Initialize the orchestrator and all agents"""
        try:
            logger.info("Initializing Unified Intelligence Orchestrator...")
            
            # Initialize services
            await self._initialize_services()
            
            # Initialize agents
            await self._initialize_agents()
            
            # Start task processing
            asyncio.create_task(self._process_task_queue())
            
            logger.info("Unified Intelligence Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            logger.error(traceback.format_exc())
            raise
    
    async def _initialize_services(self):
        """Initialize all required services"""
        try:
            # Initialize LLM service with provider manager
            if not self.llm_service:
                self.llm_service = LLMService(self.ai_config, self.provider_manager)
            
            # Initialize other services
            if not self.vector_service:
                self.vector_service = VectorService()
            
            if not self.knowledge_graph:
                self.knowledge_graph = KnowledgeGraphService()
            
            if not self.security_service:
                self.security_service = SecurityService()
            
            logger.info("Services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    async def _initialize_agents(self):
        """Initialize all intelligence agents"""
        try:
            agent_configs = [
                (AgentType.OSINT, OSINTAgent, "OSINT Agent"),
                (AgentType.INVESTIGATION, InvestigationAgent, "Investigation Agent"),
                (AgentType.FORENSICS, ForensicsAgent, "Forensics Agent"),
                (AgentType.DATA_ANALYSIS, DataAnalysisAgent, "Data Analysis Agent"),
                (AgentType.REVERSE_ENGINEERING, ReverseEngineeringAgent, "Reverse Engineering Agent"),
                (AgentType.METADATA, MetadataAgent, "Metadata Agent"),
                (AgentType.REPORTING, ReportingAgent, "Reporting Agent"),
                (AgentType.TECHNOLOGY_MONITOR, TechnologyMonitorAgent, "Technology Monitor Agent"),
            ]
            
            for agent_type, agent_class, name in agent_configs:
                agent_id = f"{agent_type.value}_{uuid.uuid4().hex[:8]}"
                
                agent = agent_class(
                    agent_id=agent_id,
                    name=name,
                    llm_service=self.llm_service,
                    vector_service=self.vector_service,
                    knowledge_graph=self.knowledge_graph,
                    security_service=self.security_service,
                )
                
                await agent.start()
                self.agents[agent_id] = agent
                self.agent_types[agent_type].append(agent_id)
                
                logger.info(f"Initialized {name} (ID: {agent_id})")
            
            logger.info(f"Initialized {len(self.agents)} agents across {len(AgentType)} types")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            logger.error(traceback.format_exc())
            raise
    
    async def submit_task(
        self,
        title: str,
        description: str,
        agent_type: AgentType,
        priority: TaskPriority = TaskPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Submit a new intelligence task"""
        try:
            task_id = str(uuid.uuid4())
            
            task = IntelligenceTask(
                id=task_id,
                title=title,
                description=description,
                agent_type=agent_type,
                priority=priority,
                metadata=metadata or {},
            )
            
            self.task_queue.append(task)
            self.performance_metrics["total_tasks"] += 1
            
            logger.info(f"Submitted task: {title} (ID: {task_id}, Priority: {priority.name})")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise
    
    async def _process_task_queue(self):
        """Process tasks from the queue"""
        while True:
            try:
                # Get available tasks
                available_tasks = [
                    task for task in self.task_queue
                    if task.status == TaskStatus.PENDING
                    and len(self.active_tasks) < self.max_concurrent_tasks
                ]
                
                if not available_tasks:
                    await asyncio.sleep(1)
                    continue
                
                # Sort by priority
                available_tasks.sort(key=lambda t: t.priority.value, reverse=True)
                
                # Process tasks
                for task in available_tasks:
                    asyncio.create_task(self._execute_task(task))
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, task: IntelligenceTask):
        """Execute a single task"""
        try:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            self.active_tasks[task.id] = task
            
            # Find available agent
            agent = await self._find_available_agent(task.agent_type)
            if not agent:
                task.status = TaskStatus.FAILED
                task.error = "No available agent for task type"
                return
            
            task.assigned_agent = agent.agent_id
            
            # Execute task
            start_time = datetime.now()
            result = await agent.execute_task(task.description, task.metadata)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update task with result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            # Update performance metrics
            self._update_performance_metrics(task, execution_time)
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            del self.active_tasks[task.id]
            
            logger.info(f"Completed task: {task.title} (ID: {task.id}) in {execution_time:.2f}s")
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = "Task execution timeout"
            logger.error(f"Task timeout: {task.title} (ID: {task.id})")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"Task failed: {task.title} (ID: {task.id}) - {e}")
            logger.error(traceback.format_exc())
            
        finally:
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
    
    async def _find_available_agent(self, agent_type: AgentType) -> Optional[IntelligenceAgent]:
        """Find an available agent of the specified type"""
        available_agent_ids = self.agent_types.get(agent_type, [])
        
        for agent_id in available_agent_ids:
            agent = self.agents.get(agent_id)
            if agent and agent.status == AgentStatus.AVAILABLE:
                return agent
        
        return None
    
    def _update_performance_metrics(self, task: IntelligenceTask, execution_time: float):
        """Update performance metrics"""
        if task.status == TaskStatus.COMPLETED:
            self.performance_metrics["completed_tasks"] += 1
        else:
            self.performance_metrics["failed_tasks"] += 1
        
        # Update average execution time
        total_completed = self.performance_metrics["completed_tasks"]
        if total_completed > 0:
            current_avg = self.performance_metrics["average_execution_time"]
            self.performance_metrics["average_execution_time"] = (
                (current_avg * (total_completed - 1) + execution_time) / total_completed
            )
        
        # Update agent utilization
        if task.assigned_agent:
            agent_id = task.assigned_agent
            if agent_id not in self.performance_metrics["agent_utilization"]:
                self.performance_metrics["agent_utilization"][agent_id] = 0
            self.performance_metrics["agent_utilization"][agent_id] += 1
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "assigned_agent": task.assigned_agent,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "progress": "in_progress",
            }
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.id == task_id:
                return {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status.value,
                    "assigned_agent": task.assigned_agent,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "result": task.result,
                    "error": task.error,
                }
        
        return None
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "orchestrator_status": "running",
            "total_agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len([t for t in self.task_queue if t.status == TaskStatus.PENDING]),
            "completed_tasks": len(self.completed_tasks),
            "performance_metrics": self.performance_metrics,
            "provider_health": self.provider_manager.get_provider_health(),
            "agent_status": {
                agent_id: agent.status.value for agent_id, agent in self.agents.items()
            },
        }
    
    async def shutdown(self):
        """Shutdown the orchestrator and all agents"""
        try:
            logger.info("Shutting down Unified Intelligence Orchestrator...")
            
            # Stop all agents
            for agent in self.agents.values():
                await agent.stop()
            
            # Clear task queues
            self.task_queue.clear()
            self.active_tasks.clear()
            
            logger.info("Unified Intelligence Orchestrator shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            logger.error(traceback.format_exc())


# Factory function for easy instantiation
async def create_orchestrator(
    ai_config: Optional[AIConfigManager] = None,
    **kwargs
) -> UnifiedIntelligenceOrchestrator:
    """Create and initialize a new orchestrator instance"""
    orchestrator = UnifiedIntelligenceOrchestrator(ai_config=ai_config, **kwargs)
    await orchestrator.initialize()
    return orchestrator
