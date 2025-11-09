"""
Hierarchical Agent Orchestration System

The keystone component for autonomous multi-agent intelligence coordination.
Implements a sophisticated 4-layer agent hierarchy enabling coordinated
specialist teams to work together autonomously on complex tasks.

Architecture
------------

The system implements a 4-layer hierarchical architecture:

1. **Executive Layer**: Task coordination and quality supervision
   - Task Coordinator: Decomposes tasks, monitors progress, makes decisions
   - Quality Supervisor: Ensures output quality, validates compliance

2. **Management Layer**: Specialist team coordinators
   - Research Lead, Analysis Lead, Creative Lead, QA Lead, Technical Lead,
     Integration Lead

3. **Specialist Layer**: 20+ domain expert agents
   - Research, Analysis, Creative, Technical, Investigation, QA specialists

4. **Execution Layer**: Tool and utility agents
   - Tool Manager, Integration Agent, Automation Agent

Key Features
------------

- AI-powered task decomposition with dependency management
- Hierarchical agent management with self-healing
- Inter-agent communication with message routing
- Multi-agent workflow execution with quality gates
- Configuration management and observability
- Error handling with retries and circuit breakers
- REST API integration layer

Dependencies
------------

This package requires:
- Python 3.8+
- asyncio (standard library)
- typing (standard library)
- dataclasses (standard library)
- enum (standard library)
- datetime (standard library)
- collections (standard library)
- uuid (standard library)
- json (standard library)
- logging (standard library)

Optional dependencies:
- psutil: For system resource monitoring in health checks

Usage Example
-------------

    >>> from amas.orchestration import (
    ...     get_task_decomposer,
    ...     get_workflow_executor,
    ...     get_api
    ... )
    >>>
    >>> # Decompose and execute a task
    >>> decomposer = get_task_decomposer()
    >>> workflow = await decomposer.decompose_task(
    ...     "Research AI market trends and create executive presentation"
    ... )
    >>>
    >>> executor = get_workflow_executor()
    >>> execution_id = await executor.execute_workflow(
    ...     "Research AI market trends and create executive presentation"
    ... )
    >>>
    >>> # Monitor progress
    >>> status = executor.get_execution_status(execution_id)
    >>> print(f"Progress: {status['progress_percentage']}%")

Error Handling
--------------

All public functions raise standard exceptions:
- ValueError: For invalid input parameters
- RuntimeError: For system-level errors (agent failures, resource limits)
- TimeoutError: For operations exceeding configured timeouts

Error handling is built into the system:
- Automatic retries with exponential backoff (configurable)
- Circuit breaker pattern for failure prevention
- Graceful degradation when agents are unavailable
- Comprehensive error logging for debugging

Logging
-------

The orchestration system uses Python's logging module with the logger name
'amas.orchestration'. Configure logging levels via:

    >>> import logging
    >>> logging.getLogger('amas.orchestration').setLevel(logging.INFO)

All operations log at appropriate levels:
- DEBUG: Detailed operation traces
- INFO: Normal operations and state changes
- WARNING: Recoverable issues (retries, agent failures)
- ERROR: Critical failures requiring attention

Security
--------

Security measures implemented:
- Input validation on all public APIs
- Message type validation through enums
- Agent authentication and authorization (via security layer)
- Secure message routing with encryption support
- Resource limits to prevent DoS attacks
- Audit trails for all agent actions

Input validation is performed on:
- Task decomposition requests
- Agent assignments
- Message routing
- Configuration updates

Performance
-----------

Performance optimizations:
- Asynchronous operations throughout
- Efficient data structures (deque, defaultdict, sets)
- Connection pooling for external services
- Caching of task patterns and specialist capabilities
- Parallel task execution where dependencies allow
- Background cleanup of expired messages

Scalability considerations:
- Configurable agent pool sizes
- Resource limits per workflow
- Load balancing across agents
- Horizontal scaling support

Module Organization
-------------------

- task_decomposer: Task breakdown and workflow planning
- agent_hierarchy: Agent management and coordination
- agent_communication: Inter-agent messaging
- workflow_executor: Workflow execution engine
- config: Configuration management
- utils: Error handling, retries, metrics
- health: Health checks and monitoring
- api: REST API integration

For detailed API documentation, see individual module docstrings.
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
