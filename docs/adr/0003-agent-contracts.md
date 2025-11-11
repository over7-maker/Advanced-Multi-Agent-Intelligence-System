# ADR-0003: Agent Role Contracts for Governance

## Status
Accepted

## Context
As AMAS grew to include multiple agent roles (code reviewer, security auditor, orchestrator, etc.), we needed a way to:
- Define what each agent can and cannot do
- Enforce access control at the agent level
- Validate agent inputs/outputs
- Prevent unauthorized tool usage
- Enable formal verification of agent behavior

## Decision
We implemented **Agent Role Contracts** as JSON schemas that define:
- **Role name** and description
- **Allowed tools** list (explicit allowlist)
- **Input/output schemas** (JSON Schema for validation)
- **Side effect bounds** (e.g., max file reads, read-only mode)
- **Approval requirements** (tools requiring human approval)

Contracts are validated at runtime and in CI to ensure compliance.

## Consequences

### Positive
- **Security**: Prevents agents from using unauthorized tools
- **Reliability**: Validates inputs/outputs prevent runtime errors
- **Governance**: Clear contracts enable auditing and compliance
- **Formal verification**: Contracts can be used with TLA+/Alloy for verification
- **Documentation**: Contracts serve as living documentation

### Negative
- **Overhead**: Schema validation adds latency
- **Maintenance**: Contracts must be kept in sync with code
- **Rigidity**: Changes require contract updates

### Neutral
- Contracts stored in `src/amas/governance/agent_contracts.py`
- Validation can be disabled in development mode

## Alternatives Considered
1. **Hardcoded permissions**: Rejected - not scalable or auditable
2. **Database-stored policies**: Considered but rejected - contracts belong in code
3. **External policy engine only**: Rejected - need validation at both runtime and CI

## Implementation

### Location
- Base contracts: `src/amas/core/agent_contracts/base_agent_contract.py`
- Agent schemas: `src/amas/core/agent_contracts/*_agent_schema.py`
- Tool governance: `src/amas/core/tool_governance/tool_registry.py`
- Configuration: `config/agent_capabilities.yaml`

### Implemented Agent Contracts
- ✅ `ResearchAgentContract` - Complete with JSONSchema
- ✅ `AnalysisAgentContract` - Complete with JSONSchema
- ✅ `SynthesisAgentContract` - Complete with JSONSchema

### Tool Governance Features
- ✅ Tool registry with risk levels
- ✅ Permission engine with rate limiting
- ✅ `ToolExecutionGuard` with safety checks
- ✅ Approval workflows for high-risk tools
- ✅ Complete audit logging

### Testing
- ✅ Comprehensive unit tests: `tests/unit/test_agent_contracts.py`
- ✅ Tool governance tests: `tests/unit/test_tool_governance.py`
- ✅ All success criteria tested and passing

## Notes
- See `src/amas/core/agent_contracts/` for implementation
- Configuration in `config/agent_capabilities.yaml`
- Future: Consider TLA+/Alloy for formal verification of orchestrations
- CI validates contracts in `.github/workflows/production-cicd-secure.yml`
- Integration with orchestrator is next step
