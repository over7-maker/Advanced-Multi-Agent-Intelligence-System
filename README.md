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
- 100+ service/tool integrations with centrally enforced security controls where technically feasible (JWT/OIDC authentication, AES-256 encryption at rest, TLS 1.3 in transit, comprehensive audit logging with automated PII redaction via regex and ML-based detection). Fallback mechanisms (e.g., client-side encryption, proxy-based redaction) used for third-party services with limited control. ⚠️ For integrations lacking native audit or encryption, client-side redaction and encryption are applied, but residual risk remains. Always validate PII handling in staging. All secrets mounted via runtime secret injection (HashiCorp Vault, AWS Secrets Manager), not env vars. Tokens rotated every 6 hours. See [Security Guide](docs/security/SECURITY.md) for per-integration security details, compliance information, high-risk third-party integrations list, and automated policy checks (OPA) at deployment time.
- OpenTelemetry observability and SLO-driven reliability: Exports traces (agent task flow), metrics (RPS, latency), and logs to OTLP endpoint. SLOs defined in Prometheus via SLI: `success_rate = (requests - error_rate) / requests`, alerting via Alertmanager
- Performance Scaling: KEDA-based autoscaling (multi-metric: HTTP RPS, queue depth, p99 latency) with cooldown windows (300s), max replica limits, and cost-aware scaling triggers. Semantic caching improves response latency by 30-60% for highly similar queries (e.g., repeated research requests) with configurable staleness tolerance. Circuit breakers use exponential backoff (initial 1s, max 30s) with jitter; retry budget limited to 3 attempts per 5-minute window. Rate limiting and cost optimization included. See [Performance Benchmarks](docs/performance_benchmarks.md) for detailed metrics and [Performance Scaling Guide](docs/PERFORMANCE_SCALING_GUIDE.md) for complete documentation.

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

---

## Performance & Scaling Infrastructure

AMAS includes performance scaling infrastructure for production workloads. This infrastructure enables multi-metric autoscaling, performance optimization, and cost efficiency. Features are implemented, tested, and documented.

> **📚 Complete Documentation**: See [Performance Scaling Guide](docs/PERFORMANCE_SCALING_GUIDE.md) for comprehensive documentation including configuration, deployment, troubleshooting, and best practices.

### Key Features

- **Autoscaling**: KEDA-based multi-metric scaling (HTTP RPS, queue depth, p99 latency, resource usage)
  - Implementation: `k8s/scaling/keda-scaler.yaml`
  - Scaling Triggers: HTTP RPS >100 sustained over 2m, queue depth >500 messages, p99 latency >1.5s over 5m
  - Configuration: Cooldown windows (300s), min replicas: 3, max replicas: 50 per workload, cost-aware scaling triggers
  - Documentation: [Performance Scaling Guide - KEDA Autoscaling](docs/PERFORMANCE_SCALING_GUIDE.md)
  - Status: ✅ Production Ready

- **Load Testing Framework**: Comprehensive performance testing with SLO validation and regression detection
  - Implementation: `src/amas/performance/benchmarks/load_tester.py`
  - CLI Tool: `scripts/run_load_test.py`
  - Documentation: [Performance Scaling Guide - Load Testing](docs/PERFORMANCE_SCALING_GUIDE.md)
  - Status: ✅ Production Ready

- **Semantic Caching**: Redis-based caching with embedding similarity matching
  - Implementation: `src/amas/services/semantic_cache_service.py`
  - Performance: 30-60% latency improvement for highly similar queries (similarity threshold >0.85) in internal benchmarks with repeated or near-duplicate queries
  - Configuration: Configurable TTL (default 24h), similarity threshold (default 0.85), LRU eviction, max size 10GB
  - Cache Invalidation: Invalidated on agent configuration changes via pub/sub; automated cache health monitoring (hit rate <70% triggers alert)
  - Performance Metrics: [Performance Benchmarks](docs/performance_benchmarks.md)
  - Documentation: [Performance Scaling Guide](docs/PERFORMANCE_SCALING_GUIDE.md)
  - Status: ✅ Production Ready

- **Resilience Patterns**: Circuit breakers, rate limiting, request deduplication
  - Implementation: `src/amas/services/circuit_breaker_service.py`, `rate_limiting_service.py`, `request_deduplication_service.py`
  - Circuit Breaker: Exponential backoff (initial 1s, max 30s) with jitter; retry budget limited to 3 attempts per 5-minute window per agent type
  - Rate Limiting: User-based quotas with sliding window algorithm, multiple time windows (minute, hour, day)
  - Tests: `tests/performance/test_resilience_patterns.py`
  - Documentation: [Performance Scaling Integration](docs/PERFORMANCE_SCALING_INTEGRATION.md)
  - Status: ✅ Production Ready

- **Cost Optimization**: Automatic cost tracking and optimization recommendations
  - Implementation: `src/amas/services/cost_tracking_service.py`
  - Documentation: [Performance Scaling Guide](docs/PERFORMANCE_SCALING_GUIDE.md)
  - Status: ✅ Production Ready

### Quick Start

```bash
# Deploy KEDA autoscaling
kubectl apply -f k8s/scaling/keda-scaler.yaml

# Verify installation
kubectl get scaledobjects -n amas-prod

# Run load tests
python scripts/run_load_test.py list
python scripts/run_load_test.py run research_agent_baseline

# Test resilience patterns
pytest tests/performance/test_resilience_patterns.py -v
```

### Complete Documentation

- **[Performance Scaling Guide](docs/PERFORMANCE_SCALING_GUIDE.md)** - Complete infrastructure guide with configuration, deployment, and troubleshooting
- **[Performance Scaling Integration](docs/PERFORMANCE_SCALING_INTEGRATION.md)** - Integration examples, code samples, and best practices
- **[Performance Scaling README](docs/PERFORMANCE_SCALING_README.md)** - Quick reference and entry point
- **[Performance Benchmarks](docs/performance_benchmarks.md)** - AI provider performance metrics and latency benchmarks
- **[Performance Scaling Summary](docs/PERFORMANCE_SCALING_SUMMARY.md)** - Implementation summary and file structure

### Implementation Status

| Feature | Implementation | Tests | Documentation | Status |
|---------|----------------|-------|---------------|--------|
| KEDA Autoscaling | `k8s/scaling/keda-scaler.yaml` | ✅ | [Guide](docs/PERFORMANCE_SCALING_GUIDE.md) | ✅ Production Ready |
| Load Testing | `src/amas/performance/benchmarks/load_tester.py` | ✅ | [Guide](docs/PERFORMANCE_SCALING_GUIDE.md) | ✅ Production Ready |
| Semantic Caching | `src/amas/services/semantic_cache_service.py` | ✅ | [Guide](docs/PERFORMANCE_SCALING_GUIDE.md) | ✅ Production Ready |
| Circuit Breakers | `src/amas/services/circuit_breaker_service.py` | ✅ | [Integration](docs/PERFORMANCE_SCALING_INTEGRATION.md) | ✅ Production Ready |
| Rate Limiting | `src/amas/services/rate_limiting_service.py` | ✅ | [Integration](docs/PERFORMANCE_SCALING_INTEGRATION.md) | ✅ Production Ready |
| Request Deduplication | `src/amas/services/request_deduplication_service.py` | ✅ | [Integration](docs/PERFORMANCE_SCALING_INTEGRATION.md) | ✅ Production Ready |
| Cost Tracking | `src/amas/services/cost_tracking_service.py` | ✅ | [Guide](docs/PERFORMANCE_SCALING_GUIDE.md) | ✅ Production Ready |
| Connection Pooling | `src/amas/services/connection_pool_service.py` | ✅ | [Integration](docs/PERFORMANCE_SCALING_INTEGRATION.md) | ✅ Production Ready |
| Scaling Metrics | `src/amas/services/scaling_metrics_service.py` | ✅ | [Guide](docs/PERFORMANCE_SCALING_GUIDE.md) | ✅ Production Ready |

### Verification

All features are:
- ✅ **Fully Implemented**: Production-ready code with error handling and fallbacks
- ✅ **Comprehensively Tested**: See `tests/performance/test_resilience_patterns.py` for test coverage
- ✅ **Fully Documented**: Complete guides, integration examples, and best practices
- ✅ **Verified Working**: Tested in development and staging environments
- ✅ **Production Ready**: All components ready for production deployment
## Observability & Monitoring

AMAS includes a comprehensive observability framework that transforms the system from a "black box" into a fully observable, proactively monitored platform.

### Key Capabilities

- **📡 Distributed Tracing**: End-to-end request tracing with OpenTelemetry, exported to Jaeger/DataDog
- **📊 SLO Monitoring**: Service Level Objectives with automatic error budget tracking
- **📈 Real-time Dashboards**: Three operational Grafana dashboards (Agent Performance, SLO Monitoring, Resource Utilization)
- **🚨 Automated Alerting**: Multi-channel alerts (Slack, PagerDuty, Email) with burn rate detection when SLOs are violated or error budgets depleted
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
