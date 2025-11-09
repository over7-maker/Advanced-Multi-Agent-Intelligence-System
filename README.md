# 🎆 Advanced Multi-Agent Intelligence System (AMAS)
## The World's Most Advanced Autonomous AI Agent System

[![Production Ready](https://img.shields.io/badge/Production-Ready-brightgreen)](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System)
[![Development Complete](https://img.shields.io/badge/Development-100%25%20Complete-success)](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pulls)
[![Code Lines](https://img.shields.io/badge/Code-29,350%2B%20lines-blue)](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System)
[![PRs](https://img.shields.io/badge/PRs-11%2F11%20Complete-brightgreen)](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pulls)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents
- [Overview](#overview)
- [Features](FEATURES.md)
- [System Architecture](FEATURES.md#system-architecture)
- [Key PRs](#key-prs)
- [Quick Start](#quick-start)
- [Deployment Guide](DEPLOYMENT.md)
- [Use Cases](USE_CASES.md)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [License](#license)

---

## Overview
AMAS is a fully autonomous, self-healing, multi-specialist AI ecosystem that operates as teams of professional specialists for complex long-term tasks. All 11 PR milestones are complete—development is production-ready and deployment proven.

---

## Features
See [FEATURES.md](FEATURES.md) for the complete, current list of production and intelligence capabilities:
- 4-layer multi-agent hierarchy for end-to-end automation
- 50+ specialist agent types: research, analysis, creative, QA, tools
- Background scheduling, event monitoring, and notification workflows
- Self-healing, persistent, and learning architecture
- Professional React interface and team visual builder
- 100+ service/tool integrations with bulletproof security
- OpenTelemetry observability and SLO-driven reliability

---

## Key PRs

### Foundation Phase (PRs A-F) ✅
Complete enterprise foundation with security, observability, and scaling infrastructure.

### Intelligence Phase (PRs G-K) ✅
Full autonomous multi-agent coordination, learning, and automation capabilities.

### PR #237: Agent Contracts & Tool Governance Foundation ✅
**Status:** ✅ **100% Implemented**

Establishes strict type contracts for all agents and implements tool access control with allowlists, ensuring every agent interaction is predictable, safe, and auditable.

**Key Components:**
- ✅ Typed Agent Contracts (JSONSchema) for all agent roles
  - Research, Analysis, and Synthesis agent schemas with complete input/output validation
- ✅ Tool Permission System with rate limiting and approval workflow
- ✅ Runtime Validation of inputs/outputs against schemas
- ✅ Capability Configuration via YAML for per-agent policies
- ✅ Complete unit/integration test coverage

**Documentation:**
- [Agent Contracts & Tool Governance Guide](docs/AGENT_CONTRACTS_AND_TOOL_GOVERNANCE.md) - Complete system overview
- [Usage Guide](docs/AGENT_CONTRACTS_USAGE_GUIDE.md) - Practical examples and API reference
- [Configuration Guide](docs/CONFIGURATION_AGENT_CAPABILITIES.md) - YAML configuration reference
- [Developer Guide](docs/developer/AGENT_CONTRACTS_DEVELOPER_GUIDE.md) - Integration guide
- [ADR-0003](docs/adr/0003-agent-contracts.md) - Architecture decision record

---

## System Architecture
Refer to the architectural diagram and deep dive in [FEATURES.md](FEATURES.md#system-architecture), and see the illustrations in `/docs/img/`.

### Project Structure

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

## Quick Start

### Local Development
1. Clone, install dependencies, copy `.env.example` to `.env` and set credentials.
2. Run `docker-compose up -d` and access the app at `localhost:3000`.
3. Detailed instructions in [DEPLOYMENT.md](DEPLOYMENT.md).

### Quick Example (Agent Contracts)
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

### Testing
```bash
pip install -r requirements.txt
pytest tests/unit/test_agent_contracts.py -v
pytest tests/unit/test_tool_governance.py -v
```

---

## Deployment Guide
Production cluster, scaling, and infrastructure instructions are fully documented in [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Use Cases
See [USE_CASES.md](USE_CASES.md) for:
- Automated market/competitor research
- Background intelligence gathering
- Technical/QA audits
- Professional report pipelines
- And more, with measurable production ROI

---

## Security
All security practices, vulnerability reporting, dependency audits, and compliance standards are fully explained in [SECURITY.md](SECURITY.md).

**Key Security Features:**
- **Tool Allowlists** - Agents can only use permitted tools
- **Parameter Validation** - Tool parameters validated against schemas
- **Rate Limiting** - Per-agent, per-tool rate limits
- **Approval Workflows** - High-risk tools require human approval
- **Audit Logging** - Complete execution records with IDs and timestamps
- **Path Restrictions** - File operations restricted to sandboxed directories
- **PII Detection** - Automatic detection and redaction of sensitive data

---

## Documentation

### Core Documentation
- **[Agent Contracts & Tool Governance](docs/AGENT_CONTRACTS_AND_TOOL_GOVERNANCE.md)** - System architecture and features
- **[Usage Guide](docs/AGENT_CONTRACTS_USAGE_GUIDE.md)** - Practical examples and troubleshooting
- **[Configuration Guide](docs/CONFIGURATION_AGENT_CAPABILITIES.md)** - YAML configuration reference
- **[Documentation Index](docs/AGENT_CONTRACTS_DOCUMENTATION_INDEX.md)** - Complete documentation guide

### Architecture
- **[Architecture Decision Records](docs/adr/)** - Design decisions and rationale
- **[System Architecture](docs/architecture.md)** - Overall system design

### Development
- **[Developer Guide](docs/developer/README.md)** - Development setup and guidelines
- **[Agent Contracts Developer Guide](docs/developer/AGENT_CONTRACTS_DEVELOPER_GUIDE.md)** - Integration guide
- **[API Documentation](docs/api/README.md)** - API reference

---

## Changelog
Versioning and update history are available in [CHANGELOG.md](CHANGELOG.md).

---

## Contributing
Community contributions are encouraged. See [CONTRIBUTING.md](CONTRIBUTING.md) for standards, coding guidelines, and pull request workflow.

---

## License
Licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact & Community
- Issues: [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- Discussions: [Discussions](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/discussions)
- Docs: [Complete Docs](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/tree/main/docs)

---

## Status
**Current**: All development complete, production ready.
**Roadmap**: Consult [PRODUCTION_ROADMAP.md](docs/PRODUCTION_ROADMAP.md) for deployment and post-v1.x goals.

---

> Built with ❤️ by the AMAS Team | Last Updated: November 9, 2025
