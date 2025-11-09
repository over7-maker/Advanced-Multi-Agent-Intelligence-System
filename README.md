# Advanced Multi-Agent Intelligence System (AMAS)

A production-ready multi-agent AI platform with strict type contracts, tool governance, and comprehensive security controls.

---

## 🎯 Recent Features

### PR #237: Agent Contracts & Tool Governance Foundation

**Status:** ✅ **100% Implemented**

This PR establishes strict type contracts for all agents and implements tool access control with allowlists, ensuring every agent interaction is predictable, safe, and auditable.

#### What's Included

- ✅ **Typed Agent Contracts (JSONSchema)** for all agent roles
  - Research, Analysis, and Synthesis agent schemas with complete input/output validation
- ✅ **Tool Permission System** with rate limiting and approval workflow
- ✅ **Runtime Validation** of inputs/outputs against schemas
- ✅ **Capability Configuration** via YAML for per-agent policies
- ✅ **Unit/Integration Tests** with comprehensive coverage

#### Key Components

- `src/amas/core/agent_contracts/` - Agent contract system
- `src/amas/core/tool_governance/` - Tool governance and permissions
- `config/agent_capabilities.yaml` - Agent configuration
- `tests/unit/test_agent_contracts.py` - Contract tests
- `tests/unit/test_tool_governance.py` - Governance tests

#### Documentation

- **[Agent Contracts & Tool Governance Guide](docs/AGENT_CONTRACTS_AND_TOOL_GOVERNANCE.md)** - Complete system overview
- **[Usage Guide](docs/AGENT_CONTRACTS_USAGE_GUIDE.md)** - Practical examples and API reference
- **[Configuration Guide](docs/CONFIGURATION_AGENT_CAPABILITIES.md)** - YAML configuration reference
- **[ADR-0003](docs/adr/0003-agent-contracts.md)** - Architecture decision record

#### Quick Start

```python
from amas.core.agent_contracts import ResearchAgentContract
from amas.core.tool_governance import get_execution_guard

# Create contract
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

#### Testing

```bash
pytest tests/unit/test_agent_contracts.py -v
pytest tests/unit/test_tool_governance.py -v
```

---

## 🚀 Production Readiness (PR #235)

- Improved VS Code dev container for the AMAS project
- Hardened CI/CD workflows with robust security reporting
- Adoption of recommended best practices for security and API key handling

For up-to-date onboarding and dev container usage, see `.devcontainer/README.md`.

---

## 📚 Documentation

### Core Documentation

- **[Agent Contracts & Tool Governance](docs/AGENT_CONTRACTS_AND_TOOL_GOVERNANCE.md)** - System architecture and features
- **[Usage Guide](docs/AGENT_CONTRACTS_USAGE_GUIDE.md)** - Practical examples and troubleshooting
- **[Configuration Guide](docs/CONFIGURATION_AGENT_CAPABILITIES.md)** - YAML configuration reference

### Architecture

- **[Architecture Decision Records](docs/adr/)** - Design decisions and rationale
- **[System Architecture](docs/architecture.md)** - Overall system design

### Development

- **[Developer Guide](docs/developer/README.md)** - Development setup and guidelines
- **[API Documentation](docs/api/README.md)** - API reference

---

## 🏗️ Project Structure

```
src/amas/core/
├── agent_contracts/          # Agent contract system
│   ├── base_agent_contract.py
│   ├── research_agent_schema.py
│   ├── analysis_agent_schema.py
│   └── synthesis_agent_schema.py
└── tool_governance/          # Tool governance system
    └── tool_registry.py

config/
└── agent_capabilities.yaml   # Agent configuration

tests/unit/
├── test_agent_contracts.py
└── test_tool_governance.py
```

---

## 🔒 Security Features

- **Tool Allowlists** - Agents can only use permitted tools
- **Parameter Validation** - Tool parameters validated against schemas
- **Rate Limiting** - Per-agent, per-tool rate limits
- **Approval Workflows** - High-risk tools require human approval
- **Audit Logging** - Complete execution records with IDs and timestamps
- **Path Restrictions** - File operations restricted to sandboxed directories
- **PII Detection** - Automatic detection and redaction of sensitive data

---

## 📖 Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Agents**
   Edit `config/agent_capabilities.yaml` to configure agent policies

3. **Run Tests**
   ```bash
   pytest tests/unit/test_agent_contracts.py -v
   pytest tests/unit/test_tool_governance.py -v
   ```

4. **Use Agent Contracts**
   See [Usage Guide](docs/AGENT_CONTRACTS_USAGE_GUIDE.md) for examples

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## 📄 License

See [LICENSE](LICENSE) for license information.

---

*Last Updated: 2025-11-04*
