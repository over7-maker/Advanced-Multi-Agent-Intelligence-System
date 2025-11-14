# Hierarchical Agent Orchestration System

This package implements the keystone component for autonomous multi-agent intelligence coordination in AMAS.

## Overview

The orchestration system enables coordinated specialist teams to work together autonomously on complex tasks through a sophisticated 4-layer agent hierarchy.

## Package Structure

```
orchestration/
├── __init__.py              # Package initialization and public API
├── task_decomposer.py       # AI-powered task breakdown (1,132 lines)
├── agent_hierarchy.py       # Multi-layer agent management (999 lines)
├── agent_communication.py   # Inter-agent messaging (1,084 lines)
├── workflow_executor.py     # Multi-agent workflow execution (1,113 lines)
├── config.py                # Configuration management
├── utils.py                 # Utilities (retry, circuit breaker, metrics)
├── health.py                # Health checks and monitoring
└── api.py                   # REST API endpoints
```

## Quick Start

```python
from amas.orchestration import (
    get_task_decomposer,
    get_workflow_executor
)

# Decompose a task
decomposer = get_task_decomposer()
workflow = await decomposer.decompose_task(
    "Research AI trends and create presentation"
)

# Execute workflow
executor = get_workflow_executor()
execution_id = await executor.execute_workflow(
    "Research AI trends and create presentation"
)
```

## Core Components

### Task Decomposer

AI-powered task breakdown with:
- Complexity analysis
- Specialist identification
- Dependency mapping
- Resource estimation

### Agent Hierarchy Manager

Multi-layer agent management with:
- Dynamic agent creation
- Load balancing
- Self-healing
- Hierarchy status tracking

### Agent Communication Bus

Inter-agent messaging with:
- Message routing
- Help requests
- Context sharing
- Escalation support

### Workflow Executor

Multi-agent workflow execution with:
- Parallel coordination
- Quality gates
- Progress monitoring
- Error recovery

## Documentation

- **Full Guide**: [docs/ORCHESTRATION_SYSTEM.md](../../docs/ORCHESTRATION_SYSTEM.md)
- **Quick Start**: [docs/ORCHESTRATION_QUICK_START.md](../../docs/ORCHESTRATION_QUICK_START.md)
- **Architecture Decision**: [docs/adr/0004-hierarchical-agent-orchestration.md](../../docs/adr/0004-hierarchical-agent-orchestration.md)

## API Reference

See module docstrings for detailed API documentation:
- `help(amas.orchestration.TaskDecomposer)`
- `help(amas.orchestration.AgentHierarchyManager)`
- `help(amas.orchestration.AgentCommunicationBus)`
- `help(amas.orchestration.WorkflowExecutor)`

## Configuration

Configure via environment variables or programmatically:

```python
from amas.orchestration import get_config, set_config, OrchestrationConfig

config = get_config()
config.max_active_workflows = 150
set_config(config)
```

See [ORCHESTRATION_SYSTEM.md](../../docs/ORCHESTRATION_SYSTEM.md#configuration) for all options.

## Examples

See `/examples/` directory for complete examples, or check the [Quick Start Guide](../../docs/ORCHESTRATION_QUICK_START.md).

## Performance

- **Concurrent Workflows**: 100+
- **Specialist Agents**: 500+ per workflow type
- **Message Throughput**: 10,000+ messages/minute
- **Task Decomposition**: <2 minutes for complex tasks
- **Failure Recovery**: <30 seconds

## Contributing

When contributing to this package:
1. Follow the existing code style and patterns
2. Add comprehensive docstrings (Google-style)
3. Include type hints for all functions
4. Add tests for new features
5. Update documentation as needed

## License

Part of AMAS - Licensed under MIT License.
