# Agent Contracts & Tool Governance Foundation

## Overview

This document describes the Agent Contracts and Tool Governance system implemented for AMAS. This system establishes strict type contracts for all agents and implements tool access control with allowlists, ensuring every agent interaction is predictable, safe, and auditable.

## Components

### 1. Agent Contracts (`src/amas/core/agent_contracts/`)

#### Base Agent Contract (`base_agent_contract.py`)

The foundation for all agent contracts, providing:

- **Type Safety**: JSONSchema validation for inputs and outputs
- **Tool Permissions**: Explicit allowlists of tool capabilities
- **Execution Constraints**: Timeout, iteration limits, and token budgets
- **Quality Gates**: Human approval requirements and output validation

Key classes:
- `AgentContract`: Abstract base class for all agent contracts
- `ExecutionContext`: Execution context with resource limits and audit info
- `AgentExecution`: Record of agent execution with metrics
- `ContractViolationError`: Exception for contract violations

#### Agent Schemas

Concrete implementations for all agent roles with complete JSONSchema validation:

**Research Agent Schema** (`research_agent_schema.py`):
- **Input Schema**: Validates research queries, scope, filters, time ranges
- **Output Schema**: Validates research summaries, findings, sources, confidence assessments
- **Pre-configured Instances**: `WEB_RESEARCH_AGENT`, `ACADEMIC_RESEARCH_AGENT`, `NEWS_RESEARCH_AGENT`

**Analysis Agent Schema** (`analysis_agent_schema.py`):
- **Input Schema**: Validates data sources, analysis types, statistical tests, confidence levels
- **Output Schema**: Validates analysis summaries, insights, statistical results, data quality assessments
- **Pre-configured Instances**: `DATA_ANALYSIS_AGENT`, `STATISTICAL_ANALYSIS_AGENT`

**Synthesis Agent Schema** (`synthesis_agent_schema.py`):
- **Input Schema**: Validates content sources, synthesis objectives, output types, citation styles
- **Output Schema**: Validates synthesized content, structure, sources, citations, quality metrics
- **Pre-configured Instances**: `CONTENT_SYNTHESIS_AGENT`, `DOCUMENT_GENERATION_AGENT`

### 2. Tool Governance (`src/amas/core/tool_governance/`)

#### Tool Registry (`tool_registry.py`)

Centralized tool management system with:

- **Tool Definitions**: Risk levels, approval requirements, rate limits
- **Usage Tracking**: Complete audit trail of all tool usage
- **Statistics**: Usage reports and analytics

Key components:
- `ToolRegistry`: Registry of all available tools
- `ToolPermissionsEngine`: Permission checking and rate limiting
- `ToolExecutionGuard`: Execution guard with safety checks

## Features

### ✅ Safety Features

1. **Tool Allowlists**: Agents can only use explicitly permitted tools
2. **Parameter Validation**: Tool parameters validated against schemas
3. **Rate Limiting**: Per-agent, per-tool rate limits prevent abuse
4. **Approval Workflows**: High-risk tools (file_write, code_execution) require human approval
5. **Audit Logging**: Complete execution records with IDs, timestamps, tool calls

### ✅ Runtime Validation

- Input validation against JSONSchema before execution
- Output validation against JSONSchema after execution
- Tool parameter validation against tool definitions
- Contract violation errors with clear messages

### ✅ Capability Configuration

Per-agent policies defined in `config/agent_capabilities.yaml`:

```yaml
agents:
  research_agent_v1:
    role: "research"
    allowed_tools:
      - "web_search"
      - "api_call"
      - "file_read"
    rate_limits:
      requests_per_minute: 30
      tokens_per_hour: 15000
    quality_gates:
      require_human_approval: false
      output_validation_required: true
```

## Usage

### Creating Agent Contracts

**Research Agent:**
```python
from amas.core.agent_contracts import ResearchAgentContract, AgentRole, ToolCapability

contract = ResearchAgentContract(
    agent_id="my_research_agent",
    role=AgentRole.RESEARCH,
    allowed_tools=[ToolCapability.WEB_SEARCH, ToolCapability.FILE_READ]
)

# Validate input
is_valid, error = contract.validate_input({
    "query": "What is AI?",
    "research_scope": "broad"
})

# Validate output
is_valid, error = contract.validate_output({
    "research_summary": "...",
    "key_findings": [...],
    "sources": [...]
})
```

**Analysis Agent:**
```python
from amas.core.agent_contracts import AnalysisAgentContract, AgentRole, ToolCapability

contract = AnalysisAgentContract(
    agent_id="my_analysis_agent",
    role=AgentRole.ANALYSIS,
    allowed_tools=[ToolCapability.FILE_READ, ToolCapability.DATA_ANALYSIS]
)

# Validate input
is_valid, error = contract.validate_input({
    "data_source": "data/results.csv",
    "analysis_type": "descriptive",
    "variables": ["column1", "column2"]
})
```

**Synthesis Agent:**
```python
from amas.core.agent_contracts import SynthesisAgentContract, AgentRole, ToolCapability

contract = SynthesisAgentContract(
    agent_id="my_synthesis_agent",
    role=AgentRole.SYNTHESIS,
    allowed_tools=[ToolCapability.FILE_READ, ToolCapability.DOCUMENT_GENERATION]
)

# Validate input
is_valid, error = contract.validate_input({
    "content_sources": [{"source_type": "file", "source_path": "data/sources.txt"}],
    "synthesis_objective": "Create comprehensive report"
})
```

### Using Tool Governance

```python
from amas.core.tool_governance import (
    get_tool_registry,
    get_permissions_engine,
    get_execution_guard
)

# Get governance components
registry = get_tool_registry()
permissions = get_permissions_engine()
guard = get_execution_guard()

# Execute tool with full safety checks
result = await guard.execute_tool(
    agent_id="research_agent_v1",
    tool_name="web_search",
    parameters={"query": "test"},
    user_id="user123",
    trace_id="trace456"
)

# Check usage stats
stats = registry.get_usage_stats(
    agent_id="research_agent_v1",
    tool_name="web_search"
)
```

## Success Criteria

All success criteria from the PR are implemented and tested:

- ✅ **Unauthorized tool use → BLOCKED**: `ContractViolationError` raised
- ✅ **Invalid input → REJECTED**: Clear validation errors returned
- ✅ **Existing flows work → NO BREAKING CHANGES**: Backward compatible
- ✅ **Rate limits enforced → PREVENTS ABUSE**: Rate limiting tested
- ✅ **High-risk tools → REQUIRE APPROVAL**: Approval workflow tested

## Testing

Comprehensive test suite:

- `tests/unit/test_agent_contracts.py`: Tests for agent contracts, schemas, validation
- `tests/unit/test_tool_governance.py`: Tests for tool registry, permissions, rate limiting

Run tests:

```bash
pytest tests/unit/test_agent_contracts.py -v
pytest tests/unit/test_tool_governance.py -v
```

## Integration Points

### Orchestrator Integration

The orchestrator should validate agent inputs/outputs against contracts:

```python
from amas.core.agent_contracts import AgentContract

def validate_agent_execution(contract: AgentContract, input_data: dict, output_data: dict):
    # Validate input
    is_valid, error = contract.validate_input(input_data)
    if not is_valid:
        raise ContractViolationError(contract.agent_id, "invalid_input", error)
    
    # Execute agent...
    
    # Validate output
    is_valid, error = contract.validate_output(output_data)
    if not is_valid:
        raise ContractViolationError(contract.agent_id, "invalid_output", error)
```

### Tool Execution Integration

All tool calls should go through the execution guard:

```python
from amas.core.tool_governance import get_execution_guard

guard = get_execution_guard()

# Instead of direct tool calls:
# result = tool.execute(params)

# Use guard:
result = await guard.execute_tool(
    agent_id=agent_id,
    tool_name=tool_name,
    parameters=params,
    user_id=user_id,
    trace_id=trace_id
)
```

## Configuration

### Agent Capabilities (`config/agent_capabilities.yaml`)

Defines per-agent policies:
- Allowed tools
- Rate limits
- Quality gates
- Constraints (timeouts, budgets)

### Tool Definitions (auto-generated)

Tool definitions are created automatically with defaults, or can be loaded from `config/tool_definitions.yaml`.

## Implementation Status

✅ **Completed:**
- Base agent contract system with JSONSchema validation
- Research agent schema with complete input/output schemas
- Analysis agent schema with complete input/output schemas
- Synthesis agent schema with complete input/output schemas
- Tool governance system with permissions, rate limiting, and approval workflows
- Comprehensive YAML configuration for all agents
- Complete test suite covering all success criteria
- Security features (path restrictions, audit logging, PII detection)

📋 **Next Steps:**
1. **Integrate with Orchestrator**: Wire contracts into orchestrator validation path
2. **Approval UI**: Build UI for human approval of high-risk tool usage
3. **Analytics Dashboard**: Build dashboard for usage statistics and monitoring
4. **Integration Tests**: Add end-to-end integration tests with real agents
5. **Additional Agent Schemas**: Create schemas for orchestrator, communication, and validation agents

## Architecture

```
┌─────────────────────────────────────┐
│     Agent Contracts                 │
│  ┌───────────────────────────────┐  │
│  │  BaseAgentContract            │  │
│  │  - Input/Output Schemas      │  │
│  │  - Tool Permissions          │  │
│  │  - Execution Constraints     │  │
│  └───────────────────────────────┘  │
│           ↓                          │
│  ┌───────────────────────────────┐  │
│  │  ResearchAgentContract        │  │
│  │  AnalysisAgentContract        │  │
│  │  SynthesisAgentContract       │  │
│  │  (All with JSONSchema)        │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│     Tool Governance                 │
│  ┌───────────────────────────────┐  │
│  │  ToolRegistry                 │  │
│  │  - Tool Definitions           │  │
│  │  - Usage Tracking             │  │
│  └───────────────────────────────┘  │
│           ↓                          │
│  ┌───────────────────────────────┐  │
│  │  ToolPermissionsEngine        │  │
│  │  - Permission Checking        │  │
│  │  - Rate Limiting              │  │
│  └───────────────────────────────┘  │
│           ↓                          │
│  ┌───────────────────────────────┐  │
│  │  ToolExecutionGuard           │  │
│  │  - Approval Workflows         │  │
│  │  - Parameter Validation       │  │
│  │  - Safety Checks              │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Security Considerations

1. **Principle of Least Privilege**: Agents only get tools they need
2. **Defense in Depth**: Multiple validation layers (schema, permissions, parameters)
3. **Audit Trail**: All tool usage logged with full context
4. **Approval Gates**: High-risk operations require explicit approval
5. **Rate Limiting**: Prevents abuse and DoS attacks

## Performance

- Schema validation is lightweight (JSONSchema is fast)
- Rate limiting uses in-memory tracking (can be upgraded to Redis)
- Usage records stored in memory (can be persisted to database)
- No significant performance impact on tool execution
