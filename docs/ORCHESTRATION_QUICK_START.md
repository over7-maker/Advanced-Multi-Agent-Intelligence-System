# 🚀 Orchestration System Quick Start

**Get started with the Hierarchical Agent Orchestration System in 5 minutes**

## Overview

The Orchestration System enables autonomous coordination of multiple specialist agents working together on complex tasks. It automatically decomposes user requests, assigns tasks to specialists, manages dependencies, and ensures quality through multi-layer review.

## Installation

The orchestration system is included in AMAS. No additional installation required:

```bash
# Already included
pip install -r requirements.txt
```

## Basic Usage

### 1. Decompose a Task

```python
from amas.orchestration import get_task_decomposer

# Get the task decomposer
decomposer = get_task_decomposer()

# Decompose a complex task
workflow = await decomposer.decompose_task(
    "Research AI market trends and create executive presentation"
)

print(f"Complexity: {workflow.complexity.value}")
print(f"Estimated time: {workflow.estimated_total_hours:.1f} hours")
print(f"Required specialists: {len(workflow.required_specialists)}")
print(f"Sub-tasks: {len(workflow.sub_tasks)}")
```

### 2. Execute a Workflow

```python
from amas.orchestration import get_workflow_executor

# Get the workflow executor
executor = get_workflow_executor()

# Execute a complete workflow
execution_id = await executor.execute_workflow(
    "Research competitor pricing strategies and create report"
)

# Monitor progress
status = executor.get_execution_status(execution_id)
print(f"Status: {status['status']}")
print(f"Progress: {status['progress_percentage']:.1f}%")
```

### 3. Monitor in Real-Time

```python
import asyncio

# Monitor execution progress
while True:
    status = executor.get_execution_status(execution_id)
    
    print(f"\nProgress: {status['progress_percentage']:.1f}%")
    print(f"Completed: {status['completed_tasks']}/{status['total_tasks']} tasks")
    print(f"Active agents: {status['active_agents']}")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    await asyncio.sleep(5)  # Check every 5 seconds
```

## Advanced Usage

### Agent Communication

```python
from amas.orchestration import (
    get_communication_bus,
    MessageType,
    Priority
)

bus = get_communication_bus()

# Send a message between agents
message_id = await bus.send_message(
    sender_id="research_agent_1",
    recipient_id="analysis_agent_1",
    message_type=MessageType.SHARE_FINDINGS,
    payload={"data": "competitor pricing analysis"},
    priority=Priority.HIGH
)

# Request help from a specialist
help_id = await bus.request_specialist_help(
    requesting_agent_id="analysis_agent_1",
    required_specialty="statistical_modeler",
    help_context={"task": "regression analysis", "deadline": "1 hour"}
)
```

### Agent Hierarchy Management

```python
from amas.orchestration import get_hierarchy_manager, AgentSpecialty

hierarchy = get_hierarchy_manager()

# Get hierarchy status
status = hierarchy.get_hierarchy_status()
print(f"Total agents: {status['total_agents']}")
print(f"Active workflows: {status['active_workflows']}")

# Create a specialist agent
agent_id = await hierarchy.create_specialist_agent(
    AgentSpecialty.DATA_ANALYST,
    urgency="normal"
)
```

### Configuration

```python
from amas.orchestration import get_config, set_config, OrchestrationConfig

# Get current configuration
config = get_config()
print(f"Max workflows: {config.max_active_workflows}")

# Update configuration
new_config = OrchestrationConfig.from_dict({
    "max_active_workflows": 150,
    "quality_gate_threshold": 0.90
})
set_config(new_config)
```

## Example: Complete Workflow

```python
import asyncio
from amas.orchestration import get_workflow_executor

async def run_complete_workflow():
    executor = get_workflow_executor()
    
    # Execute workflow
    execution_id = await executor.execute_workflow(
        "Research AI automation market trends, analyze competitor pricing, "
        "identify key opportunities, and create executive presentation"
    )
    
    print(f"Execution started: {execution_id}")
    
    # Monitor progress
    while True:
        status = executor.get_execution_status(execution_id)
        
        if status['status'] == 'completed':
            print(f"\n✅ Workflow completed!")
            print(f"Total time: {status['total_execution_time_seconds']:.1f}s")
            print(f"Quality score: {status.get('quality_summary', {}).get('overall_quality', 0):.2f}")
            break
        elif status['status'] == 'failed':
            print(f"\n❌ Workflow failed: {status.get('error_message', 'Unknown error')}")
            break
        else:
            print(f"Progress: {status['progress_percentage']:.1f}% - "
                  f"{status['completed_tasks']}/{status['total_tasks']} tasks")
            await asyncio.sleep(10)

# Run the workflow
asyncio.run(run_complete_workflow())
```

## Environment Variables

Configure the orchestration system via environment variables:

```bash
# Agent Management
export ORCHESTRATION_MAX_AGENTS_PER_POOL=5
export ORCHESTRATION_MAX_TASKS_PER_AGENT=3

# Task Decomposition
export ORCHESTRATION_DECOMPOSITION_TIMEOUT=120.0
export ORCHESTRATION_MAX_SUBTASKS=50

# Communication
export ORCHESTRATION_MESSAGE_TIMEOUT=300.0
export ORCHESTRATION_MESSAGE_RETRIES=3

# Workflow Execution
export ORCHESTRATION_WORKFLOW_TIMEOUT=24.0
export ORCHESTRATION_QUALITY_THRESHOLD=0.85
```

## Health Check

```python
from amas.orchestration import get_health_checker

health_checker = get_health_checker()
health = await health_checker.check_all()

print(f"Overall status: {health['health']['overall_status']}")
print(f"Components: {len(health['health']['components'])}")
```

## Next Steps

- **Full Documentation**: See [Orchestration System Guide](ORCHESTRATION_SYSTEM.md) for complete API reference
- **Architecture**: See [ADR-0004](adr/0004-hierarchical-agent-orchestration.md) for design decisions
- **Examples**: Check `/examples/` directory for more examples
- **API Reference**: See module docstrings for detailed API documentation

## Troubleshooting

**Issue**: "No available agents for specialty"

```python
# Check agent pool status
hierarchy = get_hierarchy_manager()
status = hierarchy.get_hierarchy_status()
print(status['layer_breakdown'])

# Manually create agent
agent_id = await hierarchy.create_specialist_agent(
    AgentSpecialty.DATA_ANALYST,
    urgency="high"
)
```

**Issue**: "Workflow timeout"

```python
# Increase timeout
config = get_config()
config.workflow_execution_timeout_hours = 48.0
set_config(config)
```

For more troubleshooting, see the [Full Documentation](ORCHESTRATION_SYSTEM.md#troubleshooting).
