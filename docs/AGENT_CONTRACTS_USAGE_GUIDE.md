# Agent Contracts & Tool Governance - Usage Guide

**Version:** 1.0  
**Last Updated:** 2025-11-04  
**PR:** #237

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Agent Contracts](#agent-contracts)
3. [Tool Governance](#tool-governance)
4. [Configuration](#configuration)
5. [Examples](#examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

The agent contracts and tool governance system is part of the AMAS core. No additional installation required.

### Basic Usage

```python
from amas.core.agent_contracts import ResearchAgentContract
from amas.core.tool_governance import get_execution_guard

# Create a contract
contract = ResearchAgentContract(
    agent_id="my_agent",
    role="research",
    allowed_tools=["web_search", "file_read"]
)

# Use tool governance
guard = get_execution_guard()
result = await guard.execute_tool(
    agent_id="my_agent",
    tool_name="web_search",
    parameters={"query": "test"}
)
```

---

## Agent Contracts

### Available Agent Contracts

The system provides typed contracts for three main agent roles:

1. **ResearchAgentContract** - For research and information gathering
2. **AnalysisAgentContract** - For data analysis and statistical processing
3. **SynthesisAgentContract** - For content synthesis and document generation

### Creating a Contract

```python
from amas.core.agent_contracts import (
    ResearchAgentContract,
    AnalysisAgentContract,
    SynthesisAgentContract,
    AgentRole,
    ToolCapability
)

# Research agent
research_contract = ResearchAgentContract(
    agent_id="research_001",
    role=AgentRole.RESEARCH,
    allowed_tools=[
        ToolCapability.WEB_SEARCH,
        ToolCapability.FILE_READ,
        ToolCapability.VECTOR_SEARCH
    ]
)

# Analysis agent
analysis_contract = AnalysisAgentContract(
    agent_id="analysis_001",
    role=AgentRole.ANALYSIS,
    allowed_tools=[
        ToolCapability.FILE_READ,
        ToolCapability.DATABASE_QUERY,
        ToolCapability.DATA_ANALYSIS
    ]
)

# Synthesis agent
synthesis_contract = SynthesisAgentContract(
    agent_id="synthesis_001",
    role=AgentRole.SYNTHESIS,
    allowed_tools=[
        ToolCapability.FILE_READ,
        ToolCapability.FILE_WRITE,
        ToolCapability.DOCUMENT_GENERATION,
        ToolCapability.TEMPLATE_RENDERING
    ]
)
```

### Input Validation

All contracts validate inputs against JSONSchema:

```python
# Valid input
input_data = {
    "query": "What is machine learning?",
    "research_scope": "broad",
    "max_sources": 10
}
is_valid, error = contract.validate_input(input_data)
if not is_valid:
    print(f"Validation error: {error}")
    return

# Invalid input (too short query)
invalid_input = {
    "query": "AI"  # Too short (minLength: 10)
}
is_valid, error = contract.validate_input(invalid_input)
# is_valid = False
# error = "Input validation failed: 'AI' is too short"
```

### Output Validation

Outputs are validated against the contract's output schema:

```python
output_data = {
    "research_summary": "Machine learning is...",
    "key_findings": [...],
    "sources": [...],
    "confidence_assessment": {...},
    "execution_metrics": {...}
}
is_valid, error = contract.validate_output(output_data)
if not is_valid:
    print(f"Output validation failed: {error}")
```

### Using Pre-configured Agents

The system provides pre-configured agent instances:

```python
from amas.core.agent_contracts import (
    WEB_RESEARCH_AGENT,
    ACADEMIC_RESEARCH_AGENT,
    DATA_ANALYSIS_AGENT,
    STATISTICAL_ANALYSIS_AGENT,
    CONTENT_SYNTHESIS_AGENT,
    DOCUMENT_GENERATION_AGENT
)

# Use pre-configured agent
contract = WEB_RESEARCH_AGENT
# contract is already configured with appropriate defaults
```

---

## Tool Governance

### Tool Registry

The tool registry manages all available tools and their definitions:

```python
from amas.core.tool_governance import get_tool_registry

registry = get_tool_registry()

# Get tool definition
tool = registry.get_tool("web_search")
print(f"Tool: {tool.name}")
print(f"Risk level: {tool.risk_level}")
print(f"Requires approval: {tool.requires_approval}")

# Get tools by capability
web_tools = registry.get_tools_by_capability(ToolCapability.WEB_SEARCH)
```

### Tool Permissions

Check if an agent can use a tool:

```python
from amas.core.tool_governance import get_permissions_engine

permissions = get_permissions_engine()

# Check access
decision = await permissions.check_tool_access(
    agent_id="research_agent_v1",
    tool_name="web_search"
)

if decision == ToolAccessDecision.ALLOW:
    # Tool access granted
    pass
elif decision == ToolAccessDecision.DENY:
    # Access denied
    pass
elif decision == ToolAccessDecision.REQUIRE_APPROVAL:
    # Human approval required
    pass
elif decision == ToolAccessDecision.RATE_LIMITED:
    # Rate limit exceeded
    pass
```

### Executing Tools Safely

Always use the execution guard for tool execution:

```python
from amas.core.tool_governance import get_execution_guard

guard = get_execution_guard()

try:
    result = await guard.execute_tool(
        agent_id="research_agent_v1",
        tool_name="web_search",
        parameters={"query": "test query"},
        user_id="user123",
        trace_id="trace456"
    )
    
    if result["status"] == "success":
        print(f"Tool executed: {result['result']}")
    elif result["status"] == "pending_approval":
        print(f"Approval required: {result['approval_id']}")
        
except ContractViolationError as e:
    print(f"Contract violation: {e}")
```

### Parameter Validation

Tool parameters are automatically validated:

```python
# Valid parameters
valid_params = {
    "file_path": "data/test.txt"
}
is_valid, error = permissions.validate_tool_parameters(
    tool_name="file_read",
    parameters=valid_params
)

# Invalid parameters (forbidden)
invalid_params = {
    "system_path": "/etc/passwd"  # Forbidden for file_write
}
is_valid, error = permissions.validate_tool_parameters(
    tool_name="file_write",
    parameters=invalid_params
)
# is_valid = False
# error = "Forbidden parameters: system_path"
```

### Usage Statistics

Track tool usage:

```python
# Get usage stats
stats = registry.get_usage_stats(
    agent_id="research_agent_v1",
    tool_name="web_search",
    hours=24
)

print(f"Total calls: {stats['total_calls']}")
print(f"Success rate: {stats['success_rate']}")
print(f"Avg duration: {stats['avg_duration_seconds']}s")

# Get comprehensive report
report = permissions.get_usage_report(hours=24)
print(f"Total tool calls: {report['total_tool_calls']}")
print(f"Unique agents: {report['unique_agents']}")
print(f"Success rate: {report['success_rate']}")
```

---

## Configuration

### Agent Capabilities Configuration

Configure agents in `config/agent_capabilities.yaml`:

```yaml
agents:
  research_agent_v1:
    role: "research"
    description: "Web research and information gathering specialist"
    allowed_tools:
      - "web_search"
      - "api_call"
      - "file_read"
      - "vector_search"
      - "document_generation"
    constraints:
      max_iterations: 8
      timeout_seconds: 600
      cost_budget_tokens: 20000
    rate_limits:
      requests_per_minute: 30
      tokens_per_hour: 15000
    quality_gates:
      require_human_approval: false
      output_validation_required: true
      fact_checking_enabled: true
```

### Tool Configurations

Configure tool-specific settings:

```yaml
tool_configurations:
  file_read:
    # Restricted to sandboxed directories only for security
    allowed_paths:
      - "data/input/"
      - "data/shared/"
      - "reports/"
      - "documents/"
    allowed_extensions:
      - ".txt"
      - ".json"
      - ".csv"
      - ".md"
      - ".yaml"
    max_file_size_mb: 100
    blocked_paths:
      - "/etc/*"
      - "/usr/*"
      - "*.env"
      - "*secret*"
      - "*password*"
  
  file_write:
    allowed_directories:
      - "outputs/"
      - "reports/"
      - "documents/"
    blocked_directories:
      - "/"
      - "/etc/"
      - "/usr/"
      - "/var/"
  
  api_call:
    # API call whitelisting for security
    allowed_domains: []  # Configure per environment
    audit_logging_required: true
    allowed_methods: ["GET", "POST"]
    blocked_methods: ["DELETE", "PUT", "PATCH"]
```

### Security Policies

Configure global security policies:

```yaml
security_policies:
  pii_detection:
    enabled: true
    redact_in_logs: true
    block_pii_in_outputs: true
  
  content_safety:
    enabled: true
    scan_inputs: true
    scan_outputs: true
    block_unsafe_content: true
  
  audit_logging:
    enabled: true
    log_all_tool_calls: true
    log_parameters: true
    log_outputs: false  # Outputs may contain sensitive data
    retention_days: 90
```

---

## Examples

### Complete Example: Research Agent Workflow

```python
from amas.core.agent_contracts import ResearchAgentContract, AgentRole, ToolCapability
from amas.core.tool_governance import get_execution_guard, get_permissions_engine
from amas.core.agent_contracts import ExecutionContext, AgentExecution

# 1. Create contract
contract = ResearchAgentContract(
    agent_id="research_001",
    role=AgentRole.RESEARCH,
    allowed_tools=[ToolCapability.WEB_SEARCH, ToolCapability.FILE_READ]
)

# 2. Create execution context
context = ExecutionContext(
    user_id="user123",
    trace_id="trace456",
    priority=7
)

# 3. Create execution record
execution = AgentExecution(
    execution_id="exec_001",
    agent_id="research_001",
    context=context,
    input_data={
        "query": "What is artificial intelligence?",
        "research_scope": "broad",
        "max_sources": 10
    }
)

# 4. Validate input
is_valid, error = contract.validate_input(execution.input_data)
if not is_valid:
    execution.mark_failed(f"Input validation failed: {error}")
    return execution

# 5. Execute tools through guard
guard = get_execution_guard()
try:
    # Execute web search
    search_result = await guard.execute_tool(
        agent_id="research_001",
        tool_name="web_search",
        parameters={"query": execution.input_data["query"]},
        user_id=context.user_id,
        trace_id=context.trace_id
    )
    
    # Record tool call
    execution.add_tool_call(
        tool_name="web_search",
        parameters={"query": execution.input_data["query"]},
        result=search_result
    )
    
    # Process results and generate output
    output_data = {
        "research_summary": "...",
        "key_findings": [...],
        "sources": [...],
        "confidence_assessment": {...},
        "execution_metrics": {...}
    }
    
    # 6. Validate output
    is_valid, error = contract.validate_output(output_data)
    if not is_valid:
        execution.mark_failed(f"Output validation failed: {error}")
        return execution
    
    # 7. Mark completed
    execution.mark_completed(output_data, tokens_used=5000)
    
except ContractViolationError as e:
    execution.mark_failed(str(e))
    
return execution
```

### Example: Handling Approval Workflows

```python
from amas.core.tool_governance import get_execution_guard

guard = get_execution_guard()

# Attempt to execute high-risk tool
result = await guard.execute_tool(
    agent_id="synthesis_agent_v1",
    tool_name="file_write",
    parameters={
        "file_path": "outputs/report.txt",
        "content": "Report content..."
    }
)

if result["status"] == "pending_approval":
    approval_id = result["approval_id"]
    print(f"Approval required: {approval_id}")
    
    # In real implementation, this would:
    # 1. Notify approvers
    # 2. Wait for approval
    # 3. Re-execute with approval
    
    # For now, check approval status
    # approval = guard.get_approval_status(approval_id)
    # if approval["status"] == "approved":
    #     result = await guard.execute_tool_with_approval(approval_id)
```

---

## Best Practices

### 1. Always Use Contracts

✅ **Do:**
```python
contract = ResearchAgentContract(agent_id="agent_001", ...)
is_valid, error = contract.validate_input(input_data)
```

❌ **Don't:**
```python
# Direct execution without validation
result = agent.execute(input_data)
```

### 2. Use Execution Guard for All Tool Calls

✅ **Do:**
```python
guard = get_execution_guard()
result = await guard.execute_tool(agent_id, tool_name, parameters)
```

❌ **Don't:**
```python
# Direct tool execution bypasses security
result = tool.execute(parameters)
```

### 3. Handle Contract Violations

✅ **Do:**
```python
try:
    result = await guard.execute_tool(...)
except ContractViolationError as e:
    logger.error(f"Contract violation: {e}")
    # Handle appropriately
```

### 4. Track Executions

✅ **Do:**
```python
execution = AgentExecution(...)
execution.add_tool_call(tool_name, parameters, result)
execution.mark_completed(output_data, tokens_used)
```

### 5. Configure Agents Properly

✅ **Do:**
- Define all required fields in YAML
- Set appropriate rate limits
- Enable quality gates
- Document tool restrictions

❌ **Don't:**
- Leave agents with default permissions
- Skip rate limiting
- Disable validation in production

---

## Troubleshooting

### Issue: Contract Validation Fails

**Symptom:** `validate_input()` or `validate_output()` returns `False`

**Solution:**
1. Check the error message for specific validation failures
2. Verify input/output matches the schema
3. Check required fields are present
4. Verify field types and constraints

```python
is_valid, error = contract.validate_input(input_data)
if not is_valid:
    print(f"Validation error: {error}")
    # Check schema
    schema = contract.get_input_schema()
    print(f"Required fields: {schema.get('required', [])}")
```

### Issue: Tool Access Denied

**Symptom:** `ToolAccessDecision.DENY` returned

**Solution:**
1. Check agent has tool in `allowed_tools` list
2. Verify YAML configuration is loaded
3. Check tool exists in registry

```python
# Check agent permissions
tools = permissions.get_agent_tools("agent_id")
print(f"Allowed tools: {[t.name for t in tools]}")

# Check tool exists
tool = registry.get_tool("tool_name")
if not tool:
    print("Tool not found in registry")
```

### Issue: Rate Limit Exceeded

**Symptom:** `ToolAccessDecision.RATE_LIMITED` returned

**Solution:**
1. Check current rate limit settings
2. Wait for rate limit window to reset
3. Consider increasing limits if appropriate
4. Implement exponential backoff

```python
# Check usage stats
stats = registry.get_usage_stats(
    agent_id="agent_id",
    tool_name="tool_name",
    hours=1
)
print(f"Recent calls: {stats['total_calls']}")
```

### Issue: Approval Required

**Symptom:** `ToolAccessDecision.REQUIRE_APPROVAL` returned

**Solution:**
1. This is expected for high-risk tools
2. Implement approval workflow
3. Get approval before execution
4. Use `execute_tool_with_approval()` after approval

---

## API Reference

### AgentContract

**Methods:**
- `get_input_schema() -> Dict[str, Any]` - Get JSONSchema for inputs
- `get_output_schema() -> Dict[str, Any]` - Get JSONSchema for outputs
- `validate_input(input_data: Dict) -> Tuple[bool, Optional[str]]` - Validate input
- `validate_output(output_data: Dict) -> Tuple[bool, Optional[str]]` - Validate output
- `can_use_tool(tool: Union[str, ToolCapability]) -> bool` - Check tool permission
- `to_manifest() -> Dict[str, Any]` - Export contract as manifest

### ToolRegistry

**Methods:**
- `get_tool(tool_name: str) -> Optional[ToolDefinition]` - Get tool definition
- `get_tools_by_capability(capability: ToolCapability) -> List[ToolDefinition]` - Get tools by capability
- `register_tool(tool_def: ToolDefinition)` - Register new tool
- `record_usage(record: ToolUsageRecord)` - Record tool usage
- `get_usage_stats(agent_id, tool_name, hours) -> Dict` - Get usage statistics

### ToolPermissionsEngine

**Methods:**
- `check_tool_access(agent_id, tool_name, user_id) -> ToolAccessDecision` - Check access
- `validate_tool_parameters(tool_name, parameters) -> Tuple[bool, Optional[str]]` - Validate parameters
- `get_agent_tools(agent_id) -> List[ToolDefinition]` - Get agent's tools
- `get_usage_report(hours) -> Dict` - Get comprehensive usage report

### ToolExecutionGuard

**Methods:**
- `execute_tool(agent_id, tool_name, parameters, user_id, trace_id) -> Dict` - Execute tool safely

---

## Additional Resources

- **Architecture:** See `docs/AGENT_CONTRACTS_AND_TOOL_GOVERNANCE.md`
- **ADR:** See `docs/adr/0003-agent-contracts.md`
- **Tests:** See `tests/unit/test_agent_contracts.py` and `tests/unit/test_tool_governance.py`
- **Configuration:** See `config/agent_capabilities.yaml`

---

*Last Updated: 2025-11-04*
