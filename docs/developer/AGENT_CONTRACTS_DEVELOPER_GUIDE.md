# Agent Contracts & Tool Governance - Developer Guide

**For:** Developers integrating agent contracts and tool governance  
**Version:** 1.0  
**Last Updated:** 2025-11-04

---

## Overview

This guide helps developers integrate the Agent Contracts and Tool Governance system into their agents and workflows.

---

## Integration Checklist

### ✅ Step 1: Import Required Modules

```python
from amas.core.agent_contracts import (
    ResearchAgentContract,
    AnalysisAgentContract,
    SynthesisAgentContract,
    AgentRole,
    ToolCapability,
    ExecutionContext,
    AgentExecution,
    ContractViolationError
)

from amas.core.tool_governance import (
    get_tool_registry,
    get_permissions_engine,
    get_execution_guard,
    ToolAccessDecision
)
```

### ✅ Step 2: Create Agent Contract

Choose the appropriate contract for your agent:

```python
# For research agents
contract = ResearchAgentContract(
    agent_id="my_research_agent",
    role=AgentRole.RESEARCH,
    allowed_tools=[ToolCapability.WEB_SEARCH, ToolCapability.FILE_READ]
)

# For analysis agents
contract = AnalysisAgentContract(
    agent_id="my_analysis_agent",
    role=AgentRole.ANALYSIS,
    allowed_tools=[ToolCapability.FILE_READ, ToolCapability.DATA_ANALYSIS]
)

# For synthesis agents
contract = SynthesisAgentContract(
    agent_id="my_synthesis_agent",
    role=AgentRole.SYNTHESIS,
    allowed_tools=[ToolCapability.FILE_READ, ToolCapability.DOCUMENT_GENERATION]
)
```

### ✅ Step 3: Validate Inputs

Always validate inputs before processing:

```python
def execute_agent(contract, input_data):
    # Validate input
    is_valid, error = contract.validate_input(input_data)
    if not is_valid:
        raise ContractViolationError(
            contract.agent_id,
            "invalid_input",
            error
        )
    
    # Process input...
```

### ✅ Step 4: Use Tool Execution Guard

Never call tools directly. Always use the execution guard:

```python
guard = get_execution_guard()

# Instead of: result = tool.execute(params)
# Use:
result = await guard.execute_tool(
    agent_id=contract.agent_id,
    tool_name="web_search",
    parameters={"query": "test"},
    user_id=user_id,
    trace_id=trace_id
)

# Handle approval required
if result.get("status") == "pending_approval":
    approval_id = result["approval_id"]
    # Wait for approval...
    # Then re-execute with approval
```

### ✅ Step 5: Validate Outputs

Validate outputs before returning:

```python
def execute_agent(contract, input_data):
    # ... process input ...
    
    output_data = {
        # ... generate output ...
    }
    
    # Validate output
    is_valid, error = contract.validate_output(output_data)
    if not is_valid:
        raise ContractViolationError(
            contract.agent_id,
            "invalid_output",
            error
        )
    
    return output_data
```

### ✅ Step 6: Track Execution

Create execution records for audit:

```python
context = ExecutionContext(
    user_id=user_id,
    trace_id=trace_id,
    priority=5
)

execution = AgentExecution(
    execution_id=generate_id(),
    agent_id=contract.agent_id,
    context=context,
    input_data=input_data
)

# Track tool calls
execution.add_tool_call(
    tool_name="web_search",
    parameters={"query": "test"},
    result=result
)

# Mark completed
execution.mark_completed(output_data, tokens_used=5000)
```

---

## Common Patterns

### Pattern 1: Agent Wrapper

```python
class ContractedAgent:
    def __init__(self, contract: AgentContract):
        self.contract = contract
        self.guard = get_execution_guard()
    
    async def execute(self, input_data: dict, user_id: str = None):
        # Validate input
        is_valid, error = self.contract.validate_input(input_data)
        if not is_valid:
            raise ContractViolationError(
                self.contract.agent_id,
                "invalid_input",
                error
            )
        
        # Execute with tool governance
        # ... agent logic ...
        
        # Validate output
        output_data = self._process(input_data)
        is_valid, error = self.contract.validate_output(output_data)
        if not is_valid:
            raise ContractViolationError(
                self.contract.agent_id,
                "invalid_output",
                error
            )
        
        return output_data
    
    async def _use_tool(self, tool_name: str, parameters: dict):
        return await self.guard.execute_tool(
            agent_id=self.contract.agent_id,
            tool_name=tool_name,
            parameters=parameters
        )
```

### Pattern 2: Error Handling

```python
try:
    result = await guard.execute_tool(...)
except ContractViolationError as e:
    if e.violation_type == "tool_access_denied":
        logger.warning(f"Agent {e.agent_id} denied access to tool")
        # Handle gracefully
    elif e.violation_type == "rate_limit_exceeded":
        logger.warning(f"Rate limit exceeded for {e.agent_id}")
        # Implement backoff
    elif e.violation_type == "invalid_parameters":
        logger.error(f"Invalid parameters: {e.details}")
        # Return error to user
    else:
        logger.error(f"Contract violation: {e}")
        raise
```

### Pattern 3: Approval Workflow

```python
async def execute_with_approval(guard, agent_id, tool_name, parameters):
    result = await guard.execute_tool(
        agent_id=agent_id,
        tool_name=tool_name,
        parameters=parameters
    )
    
    if result["status"] == "pending_approval":
        approval_id = result["approval_id"]
        
        # Notify approvers
        await notify_approvers(approval_id, agent_id, tool_name, parameters)
        
        # Wait for approval (implement your approval system)
        approval = await wait_for_approval(approval_id)
        
        if approval["status"] == "approved":
            # Re-execute with approval
            result = await guard.execute_tool_with_approval(
                approval_id)
            return result
        else:
            raise ContractViolationError(
                agent_id,
                "approval_denied",
                "Tool execution denied by approver"
            )
    
    return result
```

---

## Testing Your Integration

### Unit Test Example

```python
import pytest
from amas.core.agent_contracts import ResearchAgentContract, ContractViolationError
from amas.core.tool_governance import get_execution_guard

@pytest.mark.asyncio
async def test_agent_with_contract():
    contract = ResearchAgentContract(
        agent_id="test_agent",
        role="research",
        allowed_tools=["web_search"]
    )
    
    # Test input validation
    valid_input = {"query": "Test query that is long enough"}
    is_valid, error = contract.validate_input(valid_input)
    assert is_valid
    
    # Test tool execution
    guard = get_execution_guard()
    result = await guard.execute_tool(
        agent_id="test_agent",
        tool_name="web_search",
        parameters={"query": "test"}
    )
    assert result["status"] == "success"
```

### Integration Test Example

```python
@pytest.mark.asyncio
async def test_full_agent_workflow():
    contract = ResearchAgentContract(...)
    guard = get_execution_guard()
    
    # Full workflow
    input_data = {...}
    is_valid, _ = contract.validate_input(input_data)
    assert is_valid
    
    result = await guard.execute_tool(...)
    output_data = process_result(result)
    
    is_valid, _ = contract.validate_output(output_data)
    assert is_valid
```

---

## Configuration

### Adding Agent to YAML

Add your agent to `config/agent_capabilities.yaml`:

```yaml
agents:
  my_custom_agent:
    role: "research"  # or "analysis", "synthesis"
    description: "My custom agent description"
    allowed_tools:
      - "web_search"
      - "file_read"
    constraints:
      max_iterations: 5
      timeout_seconds: 300
      cost_budget_tokens: 10000
    rate_limits:
      requests_per_minute: 15
      tokens_per_hour: 8000
    quality_gates:
      require_human_approval: false
      output_validation_required: true
```

### Creating Custom Agent Schema

If you need a custom agent schema:

```python
from amas.core.agent_contracts import AgentContract, AgentRole, ToolCapability
from typing import Dict, Any

class CustomAgentContract(AgentContract):
    role: AgentRole = AgentRole.RESEARCH  # or create new role
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "custom_field": {"type": "string", "minLength": 1}
            },
            "required": ["custom_field"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            },
            "required": ["result"]
        }
```

---

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Tool governance logs will show:
# - Tool access decisions
# - Rate limit checks
# - Parameter validation
# - Approval requests
```

### Check Agent Permissions

```python
permissions = get_permissions_engine()
tools = permissions.get_agent_tools("agent_id")
print(f"Agent can use: {[t.name for t in tools]}")
```

### Verify Contract Schema

```python
contract = ResearchAgentContract(...)
input_schema = contract.get_input_schema()
output_schema = contract.get_output_schema()

# Print schemas for debugging
import json
print("Input schema:", json.dumps(input_schema, indent=2))
print("Output schema:", json.dumps(output_schema, indent=2))
```

---

## Performance Considerations

### Schema Validation Overhead

Schema validation is fast (JSONSchema is optimized), but for high-throughput scenarios:

- Cache validation results for repeated inputs
- Disable validation in development (not recommended for production)
- Use schema validation only for critical paths

### Rate Limiting

Rate limiting uses in-memory tracking. For distributed systems:

- Consider Redis-based rate limiting
- Implement distributed rate limiting
- Use token bucket algorithm for burst handling

---

## Migration Guide

### Migrating Existing Agents

1. **Identify agent role** (research, analysis, synthesis)
2. **Create contract** using appropriate schema
3. **Wrap tool calls** with execution guard
4. **Add input/output validation**
5. **Test thoroughly** with contract validation enabled
6. **Deploy gradually** (feature flag recommended)

### Example Migration

**Before:**
```python
def my_agent(input_data):
    result = web_search_tool.execute(input_data["query"])
    return {"result": result}
```

**After:**
```python
from amas.core.agent_contracts import ResearchAgentContract
from amas.core.tool_governance import get_execution_guard

contract = ResearchAgentContract(...)
guard = get_execution_guard()

async def my_agent(input_data):
    # Validate input
    is_valid, error = contract.validate_input(input_data)
    if not is_valid:
        raise ValueError(error)
    
    # Use guard for tool execution
    result = await guard.execute_tool(
        agent_id=contract.agent_id,
        tool_name="web_search",
        parameters={"query": input_data["query"]}
    )
    
    output = {"result": result["result"]}
    
    # Validate output
    is_valid, error = contract.validate_output(output)
    if not is_valid:
        raise ValueError(error)
    
    return output
```

---

## Best Practices

1. **Always validate** inputs and outputs
2. **Always use guard** for tool execution
3. **Handle contract violations** gracefully
4. **Track executions** for audit
5. **Configure properly** in YAML
6. **Test thoroughly** with contract validation
7. **Monitor usage** statistics
8. **Document custom schemas**

---

## Resources

- **[Main Documentation](docs/AGENT_CONTRACTS_AND_TOOL_GOVERNANCE.md)**
- **[Usage Guide](docs/AGENT_CONTRACTS_USAGE_GUIDE.md)**
- **[Configuration Guide](docs/CONFIGURATION_AGENT_CAPABILITIES.md)**
- **[ADR-0003](docs/adr/0003-agent-contracts.md)**

---

*Last Updated: 2025-11-04*
