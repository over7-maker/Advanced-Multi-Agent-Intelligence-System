"""
Hierarchical Agent Orchestration System

The keystone component for autonomous multi-agent intelligence coordination.
Implements a sophisticated 4-layer agent hierarchy enabling coordinated
specialist teams to work together autonomously on complex tasks.

Architecture:
- Executive Layer: Task coordination and quality supervision
- Management Layer: Specialist team coordinators
- Specialist Layer: Domain expert agents (20+ specialists)
- Execution Layer: Tool and utility agents
"""

from .task_decomposer import (
    TaskDecomposer,
    TaskComplexity,
    AgentSpecialty,
    TaskRequirement,
    SubTask,
    WorkflowPlan,
    get_task_decomposer,
)

from .agent_hierarchy import (
    AgentHierarchyManager,
    AgentLayer,
    AgentRole,
    AgentStatus,
    AgentInstance,
    TeamCoordination,
    get_hierarchy_manager,
)

from .agent_communication import (
    AgentCommunicationBus,
    MessageType,
    Priority,
    AgentMessage,
    CommunicationChannel,
    ResearchCoordinator,
    QualityAssuranceCoordinator,
    get_communication_bus,
)

from .workflow_executor import (
    WorkflowExecutor,
    ExecutionStatus,
    TaskStatus,
    ExecutionContext,
    get_workflow_executor,
)

from .config import (
    OrchestrationConfig,
    get_config,
    set_config,
)

from .utils import (
    retry_with_backoff,
    track_metrics,
    with_circuit_breaker,
    MetricsCollector,
    CircuitBreaker,
    RetryStrategy,
    ErrorSeverity,
    get_metrics_collector,
)

from .health import (
    HealthChecker,
    HealthStatus,
    get_health_checker,
)

from .api import (
    OrchestrationAPI,
    get_api,
)

__all__ = [
    # Task Decomposition
    "TaskDecomposer",
    "TaskComplexity",
    "AgentSpecialty",
    "TaskRequirement",
    "SubTask",
    "WorkflowPlan",
    "get_task_decomposer",
    
    # Agent Hierarchy
    "AgentHierarchyManager",
    "AgentLayer",
    "AgentRole",
    "AgentStatus",
    "AgentInstance",
    "TeamCoordination",
    "get_hierarchy_manager",
    
    # Communication
    "AgentCommunicationBus",
    "MessageType",
    "Priority",
    "AgentMessage",
    "CommunicationChannel",
    "ResearchCoordinator",
    "QualityAssuranceCoordinator",
    "get_communication_bus",
    
    # Workflow Execution
    "WorkflowExecutor",
    "ExecutionStatus",
    "TaskStatus",
    "ExecutionContext",
    "get_workflow_executor",
    
    # Configuration
    "OrchestrationConfig",
    "get_config",
    "set_config",
    
    # Utilities
    "retry_with_backoff",
    "track_metrics",
    "with_circuit_breaker",
    "MetricsCollector",
    "CircuitBreaker",
    "RetryStrategy",
    "ErrorSeverity",
    "get_metrics_collector",
    
    # Health & Monitoring
    "HealthChecker",
    "HealthStatus",
    "get_health_checker",
    
    # API Integration
    "OrchestrationAPI",
    "get_api",
]

__version__ = "1.0.0"
