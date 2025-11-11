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
- [Observability & Monitoring](#observability--monitoring)
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
- **Enterprise Security:** OIDC/JWT authentication, OPA policy-as-code authorization, comprehensive audit logging with PII redaction
- **🔍 Observability**: Distributed tracing (OpenTelemetry), SLO monitoring with error budget tracking, automatic performance regression detection
- **📊 Operational Dashboards**: Real-time Grafana dashboards for performance and SLO status
- **🚨 Proactive Alerting**: Real-time SLO burn rate monitoring with automated multi-channel notifications

---

## Key PRs

### Foundation Phase (PRs A-F) ✅
Complete enterprise foundation with security, observability, and scaling infrastructure.

### Intelligence Phase (PRs G-K) ✅
Full autonomous multi-agent coordination, learning, and automation capabilities.

### PR #237: Agent Contracts & Tool Governance Foundation ✅
Establishes strict type contracts for all agents and implements tool access control with allowlists, ensuring every agent interaction is predictable, safe, and auditable.

**Key Components:**
- Typed Agent Contracts (JSONSchema) for all agent roles
- Tool Permission System with rate limiting and approval workflow
- Runtime Validation of inputs/outputs against schemas
- Capability Configuration via YAML for per-agent policies
- Complete unit/integration test coverage

**Documentation:**
- [Agent Contracts & Tool Governance Guide](docs/AGENT_CONTRACTS_AND_TOOL_GOVERNANCE.md)
- [Usage Guide](docs/AGENT_CONTRACTS_USAGE_GUIDE.md)
- [Configuration Guide](docs/CONFIGURATION_AGENT_CAPABILITIES.md)
- [ADR-0003](docs/adr/0003-agent-contracts.md)

---

## System Architecture
Refer to the architectural diagram and deep dive in [FEATURES.md](FEATURES.md#system-architecture), and see the illustrations in `/docs/img/`.

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

### Progressive Delivery
AMAS includes a comprehensive Progressive Delivery Pipeline with Argo Rollouts for safe, automated deployments:
- **Canary Deployments**: Progressive traffic shifting (10%→25%→50%→75%→100%)
- **Automatic Rollback**: SLO violations trigger immediate rollback within 2 minutes
- **Zero Downtime**: No service interruption during deployments
- **SLO-based Gates**: Health checks and metrics validation prevent bad deployments

See [Progressive Delivery Quick Start](docs/PROGRESSIVE_DELIVERY_QUICK_START.md) and [Implementation Guide](docs/PROGRESSIVE_DELIVERY_IMPLEMENTATION.md) for details.

---

## Observability & Monitoring

AMAS includes a comprehensive observability framework that transforms the system from a "black box" into a fully observable, proactively monitored platform.

### Key Capabilities

- **📡 Distributed Tracing**: End-to-end request tracing with OpenTelemetry, exported to Jaeger/DataDog
- **📊 SLO Monitoring**: Service Level Objectives with automatic error budget tracking
- **📈 Real-time Dashboards**: Three operational Grafana dashboards (Agent Performance, SLO Monitoring, Resource Utilization)
- **🚨 Proactive Alerting**: Real-time SLO burn rate monitoring with automated multi-channel notifications for violations and error budget depletion
- **🔍 Performance Regression Detection**: Automatic detection of performance degradations

### Quick Links

- **[Observability Framework Guide](docs/OBSERVABILITY_FRAMEWORK.md)**: Complete framework documentation
- **[Observability Setup Guide](docs/OBSERVABILITY_SETUP_GUIDE.md)**: Step-by-step setup instructions
- **[Monitoring Guide](docs/MONITORING_GUIDE.md)**: Monitoring best practices and troubleshooting

### SLO Targets

| SLO | Target | Error Budget |
|-----|--------|--------------|
| Agent Availability | ≥99.5% | 0.5% |
| Latency P95 | ≤1.5s | 10% |
| Tool Call Success | ≥99.0% | 1% |
| Memory Usage | ≤80% | 15% |
| Cost Efficiency | ≤$0.05/req | 20% |

### Getting Started

1. **Setup Monitoring Stack**: Follow [Observability Setup Guide](docs/OBSERVABILITY_SETUP_GUIDE.md)
2. **Configure Environment**: Set `OTLP_ENDPOINT` and `PROMETHEUS_URL` environment variables
3. **Import Dashboards**: Load Grafana dashboards from `config/observability/grafana_dashboards.json`
4. **Verify**: Check traces in Jaeger, metrics in Prometheus, and dashboards in Grafana

For detailed setup instructions, see [docs/OBSERVABILITY_SETUP_GUIDE.md](docs/OBSERVABILITY_SETUP_GUIDE.md).

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
AMAS implements enterprise-grade security with:
- **OIDC/JWT Authentication:** Token-based authentication with JWKS caching and validation
- **Policy-as-Code Authorization:** Open Policy Agent (OPA) for role-based access control
- **Comprehensive Audit Logging:** Automatic PII redaction and structured JSON logging
- **Security Headers:** HSTS, CSP, X-Frame-Options, and more applied to all responses
- **Agent Contract Validation:** Enforced authorization before task execution

See [SECURITY.md](SECURITY.md) for security practices, vulnerability reporting, and compliance standards.  
See [docs/security/AUTHENTICATION_AUTHORIZATION.md](docs/security/AUTHENTICATION_AUTHORIZATION.md) for authentication and authorization details.  
See [docs/security/AUDIT_LOGGING.md](docs/security/AUDIT_LOGGING.md) for audit logging documentation.

**Key Security Features:**
- Tool Allowlists - Agents can only use permitted tools
- Parameter Validation - Tool parameters validated against schemas
- Rate Limiting - Per-agent, per-tool rate limits
- Approval Workflows - High-risk tools require human approval
- Audit Logging - Complete execution records with IDs and timestamps
- Path Restrictions - File operations restricted to sandboxed directories
- PII Detection - Automatic detection and redaction of sensitive data

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
