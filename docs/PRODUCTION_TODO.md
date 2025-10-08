## AMAS Production Audit TODOs (Final)

Scope: High-impact tasks required to reach production readiness. Reference IDs map to our tracked items.

### Deployment & Config
- [ ] pa_01: Ship one-click docker-compose deployment with healthchecks and sane defaults
- [ ] pa_02: Harden Dockerfile using multi-stage, non-root user, slim base
- [ ] pa_03: Centralize configuration via pydantic-settings with env-specific profiles
- [ ] pa_04: Externalize secrets to .env and provide .env.example

### Security & Access
- [ ] pa_05: Replace mock auth with JWT/OIDC and enforce RBAC
- [ ] pa_06: Add API rate limiting, request size limits, and strict CORS
- [ ] pa_12: Add CI security scans: Safety, pip-audit, Bandit, Trivy

### API Quality & Resilience
- [ ] pa_07: Standardize error handling to RFC7807 and strict input validation
- [ ] pa_17: Add timeouts, retries, circuit breakers for external providers
- [ ] pa_18: Enhance AI provider health probes, cooldowns, and backoff
- [ ] pa_19: Implement durable task state store and idempotency keys

### Observability
- [ ] pa_08: Implement structured logging with correlation IDs and log levels
- [ ] pa_09: Expose Prometheus metrics and liveness/readiness health endpoints
- [ ] pa_10: Create Grafana dashboards and Alertmanager alert policies
- [ ] pa_24: Integrate OpenTelemetry tracing and centralize logs to Loki/ELK

### Testing & Quality Gates
- [ ] pa_11: Establish CI: lint, typecheck, tests, coverage gate at 80%+
- [ ] pa_13: Implement E2E API tests with auth and realistic scenarios
- [ ] pa_14: Add load tests and performance thresholds in CI

### Data Safety & Recovery
- [ ] pa_15: Automate backups for Postgres, Neo4j, configs with retention
- [ ] pa_16: Document disaster recovery and validate restore procedures

### UX & Enablement
- [ ] pa_20: Deliver web dashboard MVP: status, agents, tasks, metrics
- [ ] pa_21: Build interactive onboarding wizard and preflight environment checks

### Scalability (Kubernetes)
- [ ] pa_22: Provide Kubernetes manifests with HPA, VPA, and PDB
- [ ] pa_23: Configure resource requests/limits and autoscaling policies

---

Execution notes:
- Prioritize pa_01, pa_05, pa_08, pa_09, pa_10, pa_11 for the first hardening iteration.
- Each task should land with docs, tests (where applicable), and rollback plan.

