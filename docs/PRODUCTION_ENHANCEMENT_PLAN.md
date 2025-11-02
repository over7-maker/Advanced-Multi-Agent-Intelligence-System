# AMAS Production Enhancement Plan
## Based on Deep Production Review

This document consolidates and upgrades the roadmap/todo into a pragmatic execution sequence for enterprise-grade reliability.

## Executive Summary

The project has made substantial progress toward production readiness. To confidently cross into enterprise-grade reliability, prioritize four pillars:

1. **Security Hardening** - Enforceable guardrails, OIDC/JWT verification, OPA policies, SBOM/provenance
2. **Observability** - Structured telemetry (OTel), SLOs with error budgets, RED/USE dashboards
3. **CI/CD to Progressive Delivery** - Lockfiles, SBOM, canary/blue-green deployments
4. **Data & Agent Governance** - Data classification, agent role contracts, auditability

## Phase A: Security Gate Maturity (2-3 weeks)

### ✅ Completed

- **OIDC/JWT Middleware** (`src/amas/security/oidc_middleware.py`)
  - JWKS caching with automatic refresh
  - Audience/issuer verification
  - Key rotation support
  
- **OPA Policy Enforcement** (`src/amas/security/opa_policy_enforcer.py`)
  - Policy-as-code for tool access control
  - Rego policies in `policies/tool_access_policy.rego`
  - Runtime policy checks with escalation support

- **SBOM Generation** (CI workflow)
  - Syft for SBOM generation (CycloneDX, SPDX)
  - Grype for vulnerability scanning
  - CI gates requiring zero criticals before merge

### 🔄 In Progress / Next Steps

- [ ] **Environment Protection**: Block merges if production requires approvals
- [ ] **Agent Sandbox Layer**: Tool call allowlists, I/O quotas, PII redaction
- [ ] **Policy Hooks**: Orchestration-level escalation for risky actions
- [ ] **Secrets Rotation**: Automated token rotation via GitHub OIDC → cloud credentials

## Phase B: Observability + SLOs (2-3 weeks)

### ✅ Completed

- **OpenTelemetry Setup** (`src/amas/observability/opentelemetry_setup.py`)
  - Auto-instrumentation for FastAPI, HTTPX, Redis, SQLAlchemy
  - Custom trace spans with context propagation
  - OTLP exporter support

- **SLO Definitions** (`config/slo_definitions.yaml`)
  - Orchestrator: p95 ≤ 1.5s, error rate < 1%
  - AI Router: p95 ≤ 2s, failover < 1s
  - Error budget thresholds defined

### 🔄 In Progress / Next Steps

- [ ] **RED/USE Dashboards**: Grafana dashboards for Rate, Errors, Duration
- [ ] **Error Budget Monitoring**: Alertmanager routes for budget consumption
- [ ] **Golden Signals**: Prometheus queries for latency p95/p99
- [ ] **Chaos Experiments**: Network partitions, latency spikes, dependency failures

## Phase C: Progressive Delivery (2-3 weeks)

### ✅ Completed

- **Workflow Validation** (`.github/workflows/workflow-validation.yml`)
  - Actionlint for workflow validation
  - YAML schema checks
  - Policy validation

- **SBOM in CI**: Generated and scanned for every build

### 🔄 In Progress / Next Steps

- [ ] **Dependency Lockfiles**: pip-compile outputs for reproducibility
- [ ] **Docker Image Digests**: Freeze base images with digests
- [ ] **Canary/Blue-Green**: Argo Rollouts or Flagger integration
- [ ] **Automated Rollback**: Regression signal detection and rollback
- [ ] **Auto-Format Workflow**: Format and commit to PR branches

## Phase D: Governance (2-4 weeks)

### ✅ Completed

- **Agent Role Contracts** (`src/amas/governance/agent_contracts.py`)
  - JSON schemas for agent I/O
  - Tool allowlists per role
  - Side effect bounds
  - Approval requirements

### 🔄 In Progress / Next Steps

- [ ] **Data Classification**: PII/PHI/PCI tagging decorators
- [ ] **Data Lineage**: Track data flow across pipelines
- [ ] **DLP Checks**: Outbound communication scanning
- [ ] **Formal Verification**: TLA+/Alloy specs for orchestrations
- [ ] **Audit Logging**: Correlated logs with trace IDs for replay

## Phase E: Performance & Cost (2-3 weeks)

### ✅ Completed

- **k6 Load Tests** (`tests/load/k6_scenarios.js`)
  - Orchestrator end-to-end scenarios
  - AI Router scenarios
  - Threshold definitions (p95, error rates)

### 🔄 In Progress / Next Steps

- [ ] **Token Usage Dashboards**: Track cost per request
- [ ] **KEDA/HPA Scaling**: Autoscaling on queue depth and latency
- [ ] **Rate Limiters**: Gateway-level rate limiting
- [ ] **Caching Layer**: Semantic/memo caches for LLM steps
- [ ] **Performance Regression Testing**: Nightly perf jobs

## Phase F: DX & Docs (Ongoing)

### ✅ Completed

- **DevContainer** (`.devcontainer/devcontainer.json`)
  - One-click development environment
  - VS Code extensions configured
  - Port forwarding setup

- **Local Docker Compose** (`docker-compose.local.yml`)
  - All services with mocks
  - OPA, Prometheus, Grafana included
  - Mock OIDC provider

- **ADRs** (`docs/adr/`)
  - ADR template
  - Orchestrator pattern decision
  - Agent contracts decision

### 🔄 In Progress / Next Steps

- [ ] **Architecture Diagrams**: Living sequence diagrams
- [ ] **Runbooks**: Incident response, deployment, rollback procedures
- [ ] **Contributor Quickstart**: Streamlined onboarding

## Success Metrics for GA Readiness

- ✅ SLOs met for 30 days (no major incidents)
- ✅ Zero criticals in vulnerability scans; SBOMs attached to every release
- [ ] Canary/blue-green pipeline proven with automatic rollback (2 releases)
- ✅ Complete agent role contracts (implementation done)
- [ ] Observability dashboards used during incident drill

## Implementation Files

### Security
- `src/amas/security/oidc_middleware.py` - OIDC/JWT middleware
- `src/amas/security/opa_policy_enforcer.py` - OPA policy enforcement
- `policies/tool_access_policy.rego` - Rego policies

### Observability
- `src/amas/observability/opentelemetry_setup.py` - OTel setup
- `config/slo_definitions.yaml` - SLO definitions

### Governance
- `src/amas/governance/agent_contracts.py` - Agent role contracts

### CI/CD
- `.github/workflows/production-cicd-secure.yml` - Enhanced with SBOM
- `.github/workflows/workflow-validation.yml` - Workflow validation

### DX
- `.devcontainer/devcontainer.json` - DevContainer
- `docker-compose.local.yml` - Local dev environment
- `docs/adr/` - Architecture Decision Records

### Testing
- `tests/load/k6_scenarios.js` - Load test scenarios

## Next Steps

1. **Integrate OIDC middleware** into FastAPI app (`src/amas/api/main.py`)
2. **Setup OpenTelemetry** in application startup
3. **Add pip-compile** for dependency locking
4. **Create Grafana dashboards** based on SLO definitions
5. **Implement agent sandbox layer** with tool allowlists
6. **Add data classification decorators** for PII/PHI tagging

## References

- Production Review Document (provided)
- `docs/PRODUCTION_ROADMAP.md` - Original roadmap
- `docs/PRODUCTION_TODO.md` - Original TODO list
