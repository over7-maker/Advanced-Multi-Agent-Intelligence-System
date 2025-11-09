"""
Hierarchical Agent Orchestration System

The keystone component for autonomous multi-agent intelligence coordination.
Implements a sophisticated 4-layer agent hierarchy enabling coordinated
specialist teams to work together autonomously on complex tasks.

Architecture Overview:
=====================

The orchestration system implements a 4-layer hierarchical architecture:

1. Executive Layer (Task Coordination & Quality Supervision)
   - Task Coordinator: Receives user requests, decomposes complex tasks into
     specialist workflows, monitors progress across all layers, and makes
     final delivery decisions and approvals.
   - Quality Supervisor: Ensures output quality across all tasks, performs
     multi-layer reviews, validates compliance, and approves final deliverables.

2. Management Layer (Specialist Team Coordinators)
   - Research Lead: Coordinates research specialists (Academic Researcher,
     Web Intelligence, News Analyst, Competitive Intel, Social Monitor)
   - Analysis Lead: Coordinates analysis specialists (Data Analyst, Statistical
     Modeler, Pattern Recognizer, Risk Assessor, Financial Analyzer)
   - Creative Lead: Coordinates creative specialists (Graphics Designer,
     Content Writer, Presentation Formatter, Media Producer, Infographic Creator)
   - QA Lead: Coordinates quality assurance specialists (Fact Checker, Quality
     Controller, Compliance Reviewer, Error Detector, Delivery Approver)
   - Technical Lead: Coordinates technical specialists (Code Reviewer, System
     Architect, Security Analyst, Performance Engineer, DevOps Specialist)
   - Integration Lead: Coordinates integration and automation specialists

3. Specialist Layer (Domain Expert Agents - 20+ Specialists)
   - Research Specialists: Academic Researcher, Web Intelligence Gatherer,
     News Trends Analyzer, Competitive Intelligence, Social Media Monitor
   - Analysis Specialists: Data Analyst, Statistical Modeler, Pattern
     Recognition Expert, Risk Assessment Specialist, Financial Performance
     Analyst
   - Creative Specialists: Graphics Designer, Content Writer/Editor,
     Presentation Formatter, Media/Video Producer, Infographic Creator
   - Technical Specialists: Code Reviewer/Optimizer, System Architect,
     Security Analyst, Performance Engineer, DevOps Specialist
   - Investigation Specialists: Digital Forensics Expert, Network Security
     Analyzer, Reverse Engineering Specialist, Case Investigation Manager,
     Evidence Compilation Expert
   - QA Specialists: Fact Checker/Validator, Output Quality Controller,
     Compliance Reviewer, Error Detection Specialist, Final Delivery Approver

4. Execution Layer (Tool & Utility Agents)
   - Tool Manager: Handles file management, database operations, code execution,
     and media processing
   - Integration Agent: Manages API integration, n8n workflows, OAuth, and
     service coordination
   - Automation Agent: Handles task scheduling, event monitoring, notification
     delivery, and workflow automation

Key Features:
=============

- AI-Powered Task Decomposition: Automatically analyzes task complexity and
  breaks down complex requests into coordinated specialist workflows with
  dependency management and resource estimation.

- Hierarchical Agent Management: Multi-layer hierarchy with dynamic agent
  creation, load balancing, and self-healing capabilities that automatically
  replace failed agents and redistribute workload.

- Inter-Agent Communication: Reliable message routing between all agents with
  help requests, context sharing, and automatic escalation to management for
  critical issues.

- Multi-Agent Workflow Execution: Executes independent tasks in parallel while
  managing dependencies, with multi-stage quality verification at phase
  transitions and real-time progress tracking.

- Configuration Management: Environment-based configuration with validation,
  resource limits, and feature flags for flexible deployment.

- Observability: Comprehensive metrics collection, health monitoring, and
  performance tracking for all orchestration operations.

- Error Handling: Retry mechanisms with exponential backoff, circuit breaker
  pattern, and graceful degradation for resilient operation.

- API Integration: REST API wrapper for web framework integration with
  endpoints for workflow management, metrics, health checks, and configuration.

Usage Example:
==============

    >>> from amas.orchestration import (
    ...     get_task_decomposer,
    ...     get_workflow_executor,
    ...     get_hierarchy_manager,
    ...     get_communication_bus,
    ...     get_api
    ... )
    >>>
    >>> # Decompose a complex task
    >>> decomposer = get_task_decomposer()
    >>> workflow_plan = await decomposer.decompose_task(
    ...     "Research AI market trends and create executive presentation"
    ... )
    >>>
    >>> # Execute the workflow
    >>> executor = get_workflow_executor()
    >>> execution_id = await executor.execute_workflow(
    ...     "Research AI market trends and create executive presentation"
    ... )
    >>>
    >>> # Monitor progress
    >>> status = executor.get_execution_status(execution_id)
    >>> print(f"Progress: {status['progress_percentage']}%")
    >>>
    >>> # Use API for web integration
    >>> api = get_api()
    >>> health = await api.get_health_status()

Module Organization:
===================

- task_decomposer: AI-powered task breakdown and workflow planning
- agent_hierarchy: Multi-layer agent management and coordination
- agent_communication: Inter-agent messaging and collaboration
- workflow_executor: Multi-agent workflow execution engine
- config: Configuration management and environment settings
- utils: Error handling, retries, metrics, and circuit breakers
- health: Health checks and monitoring utilities
- api: REST API integration layer

For detailed documentation on each component, see the individual module
docstrings.
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
