# ADR-0002: Master Orchestrator Pattern for Multi-Agent Coordination

## Status
Accepted

## Context
AMAS requires coordination between multiple AI agents (code reviewers, security auditors, performance analyzers, etc.) to accomplish complex workflows. We needed a pattern that:
- Provides centralized decision-making and workflow management
- Enables agent independence and scalability
- Supports failover and error recovery
- Maintains auditability and observability

## Decision
We adopted a Master Orchestrator pattern with:
- **Central orchestrator** (`unified_orchestrator.py`) that coordinates all agent activities
- **Agent contracts** defining each agent's role, allowed tools, and I/O schemas
- **Policy enforcement** via OPA for tool access control
- **Structured communication** using JSON schemas for agent interactions
- **Distributed tracing** via OpenTelemetry for end-to-end visibility

## Consequences

### Positive
- Clear separation of concerns (orchestration vs. execution)
- Scalable architecture (agents can scale independently)
- Policy-driven access control (OPA enables runtime policy updates)
- Auditability (all agent actions logged with trace IDs)
- Testability (agents can be mocked/stubbed independently)

### Negative
- Single point of coordination (orchestrator bottleneck if not scaled)
- Added complexity (more components to manage)
- Network overhead (agent-to-orchestrator communication)

### Neutral
- Requires careful design of agent contracts
- Distributed tracing adds observability overhead

## Alternatives Considered
1. **Peer-to-peer agent communication**: Rejected due to complexity and lack of centralized control
2. **Event-driven architecture**: Considered but rejected as initial design; may be future enhancement
3. **Pipeline pattern**: Rejected due to inflexibility for dynamic workflows

## Notes
- See `src/amas/core/unified_orchestrator.py` for implementation
- Agent contracts defined in `src/amas/governance/agent_contracts.py`
- OPA policies in `policies/tool_access_policy.rego`
