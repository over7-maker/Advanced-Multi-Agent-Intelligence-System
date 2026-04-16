# Service data audit — `src/amas/services/`

**Purpose:** Track every service module’s **real data source**, **wiring**, and **mock/scaffold risk** so production APIs never return silent canned metrics. Part of [Phase R0](next-generation-muli-agent-ai/PHASED_MASTER_TODO.md#phase-r0--real-data--service-inventory-backend-honesty) in the [next-generation program pack](next-generation-muli-agent-ai/README.md).

**How to refresh**

1. Regenerate the **Module** column (if tree changes):

   ```bash
   python -c "import pathlib; p=pathlib.Path('src/amas/services'); print('\n'.join(sorted({x.name for x in p.glob('*.py') if x.name!='__init__.py'})))"
   ```

2. Grep for risk flags per file: `mock|Mock|fake|dummy|placeholder|sample_data|hardcoded` (allowlist tests separately).

3. Trace wiring: `service_manager.py`, `src/amas/api/main.py` lifespan, route modules that construct services.

**Legend:** **TBD** = not yet audited. **P0** = user-visible or orchestrator-adjacent (fill first). **Action:** `keep` | `merge` | `wire-db` | `wire-prometheus` | `wire-router` | `delete-scaffold` | `explicit-503`.

---

## Priority duplicate / fallback pairs (review first)

| Group | Files | Notes |
|-------|--------|--------|
| Monitoring | `monitoring_service.py`, `monitoring_service_complete.py`, `advanced_monitoring_service.py`, `security_monitoring_service.py` | Check for SSOT vs copy-paste metrics |
| Performance | `performance_service.py`, `performance_service_complete.py` | Same |
| Fallback | `intelligent_fallback_system.py`, `ultimate_fallback_system.py`, `ai_fallback_manager.py` | Which paths are live vs legacy |
| Health | `deep_health_service.py`, `health_check_service.py`, `system_monitor.py`, `live_monitor_service.py` | Align with `/health/deep`, live monitor routes |
| Analytics | `advanced_analytics_service.py`, `ai_analytics_service.py` | Align with `src/api/routes/analytics.py` |

---

## Full module inventory (scaffold — fill Purpose through Action)

| Module | Purpose | Wired in startup / manager? | Authoritative data source | Mock / scaffold risk | Priority | Action |
|--------|---------|-----------------------------|---------------------------|----------------------|----------|--------|
| advanced_analytics_service.py | Extended analytics rollups/forecast helpers | Service-level use; not canonical route backend | In-memory aggregates + optional Prometheus pull-through | Medium (overlaps `/analytics` route logic) | P1 | merge |
| advanced_monitoring_service.py | Secondary monitoring facade for enriched checks | Not canonical in startup/router wiring | Mixed psutil + in-memory state | High (duplicates monitoring stack) | P0 | merge |
| advanced_optimization_service.py | Optimization heuristics for runtime tuning | Utility/service-level only | In-memory heuristics + config | Medium | P1 | keep |
| agent_cache_service.py | Agent metadata/result cache helper | Utility singleton usage | Redis primary, local fallback | Medium (fallback may hide cache outages) | P1 | wire-db |
| ai_analytics_service.py | AI usage/cost analytics helper layer | Service-level usage | Prometheus metrics + task execution records | Medium | P1 | merge |
| ai_fallback_manager.py | Legacy fallback coordinator for provider/service errors | Service-level usage; not sole runtime authority | In-memory policy state + router callbacks | Medium | P1 | merge |
| ai_service_manager.py | AI service lifecycle/selection manager abstraction | Service-level usage | Env/provider config + router/service handles | Medium | P1 | merge |
| audit_logging_service.py | Structured audit event model and logger helper API | Route/service-level use; not centralized in `service_manager.py` | In-memory event list + application logs | Medium (appears persistent but defaults in-memory) | P0 | wire-db |
| autonomous_agents_service.py | Agent orchestration helper service for autonomous loops | Service-level usage | Task state + orchestrator callbacks | Medium | P1 | keep |
| circuit_breaker_service.py | Circuit breaker state manager for external dependencies | Utility/service-level usage | In-memory breaker state + error metrics | Medium | P1 | keep |
| computer_vision_service.py | CV inference/enrichment helper (optional feature) | Not canonical startup path | Local model/runtime artifacts | Medium (optional dependency drift) | P2 | explicit-503 |
| connection_pool_service.py | Connection pooling abstraction for external clients | Service-level utility | In-memory pools + backend clients | Medium | P1 | keep |
| cost_tracking_service.py | Cost aggregation and budgeting helper | Service-level usage | Task execution cost fields + provider usage | Medium | P1 | wire-db |
| credential_manager.py | Credential/env/settings retrieval with optional encryption | Utility import where needed (not startup singleton) | Environment variables + `src.config.settings` | Low | P0 | keep |
| database_service.py | Legacy database wrapper with connection state flag | Initialized in `service_manager.py`; limited direct route usage | Not authoritative; real DB path is `src/database/connection.py` | High (name implies canonical DB access) | P0 | merge |
| deep_health_service.py | Deep dependency health probes (DB/Redis/Neo4j/schema/orchestrator/OPA) | Health/system route-level usage | Live dependency probe results via connection modules | Low | P0 | keep |
| email_service.py | Outbound email sender/notification integration helper | Service-level use; optional startup wiring | SMTP/API provider responses + config | Medium (can silently noop without provider) | P1 | explicit-503 |
| enhanced_logging_service.py | Structured logging/telemetry enrichment helpers | Service-level usage | Application log streams | Low | P2 | keep |
| enterprise_communication_service.py | Enterprise notification/channel orchestration helper | Service-level usage | External comm APIs + config | Medium | P2 | explicit-503 |
| enterprise_service.py | Enterprise workflow/integration helper facade | Service-level usage | External platform APIs + DB-backed metadata | Medium | P2 | keep |
| error_recovery_service.py | Recovery policy helpers for failed operations | Service-level usage | Error history + retry state (in-memory) | Medium | P1 | wire-db |
| graceful_shutdown_service.py | Coordinated shutdown handlers for long-lived services | Startup/lifecycle helper | Process/runtime state | Low | P2 | keep |
| health_check_service.py | Generic health framework + dependency check orchestration | Service-level usage; overlaps deep health path | Runtime process/dependency probes (psutil + check classes) | Medium (overlap with deep health service) | P0 | merge |
| incident_response_service.py | Incident workflow/procedure engine | Not a startup singleton; domain/service usage only | In-memory incident state + config | High (security-critical behavior without persistence) | P0 | explicit-503 |
| intelligent_fallback_system.py | Multi-strategy fallback orchestrator | Service-level usage | In-memory decision state + router callbacks | Medium (fallback stack duplication) | P1 | merge |
| knowledge_graph_service.py | Neo4j adapter with retry + schema initialization | Initialized in `service_manager.py` | Neo4j driver / graph database | Low | P0 | keep |
| live_monitor_service.py | Aggregated live status for frontend polling | Used by live-monitor/system routes (function-level calls) | Live probes (Postgres, Redis, Neo4j, orchestrator) | Low | P0 | keep |
| llm_service.py | Legacy direct-provider/Ollama client abstraction | Initialized in `service_manager.py`; legacy service usage | Direct HTTP endpoints + provider API keys (not router-first) | High (architecture drift from EnhancedAIRouter) | P0 | merge |
| ml_decision_engine.py | ML scoring/decision helper for recommendations | Service-level usage | Model artifacts + task execution history | Medium | P1 | keep |
| ml_service.py | Legacy ML service wrapper | Service-level usage; overlaps intelligence manager | Local model artifacts + DB training data | Medium | P1 | merge |
| monitoring_service.py | Runtime monitoring/alerts + metric loop | Service-level usage; not canonical startup SSOT | psutil metrics + in-memory structures | Medium (duplicate with complete variant) | P0 | merge |
| monitoring_service_complete.py | Alternate monitoring implementation mirroring base module | Not clearly canonical in startup wiring | psutil metrics + in-memory structures | High (duplicate scaffold risk) | P0 | delete-scaffold |
| nlp_service.py | NLP parsing/enrichment helper service | Service-level usage | Local NLP model/runtime artifacts | Medium | P2 | explicit-503 |
| performance_service.py | Performance optimization/caching/load-balancing engine | Service-level usage; not canonical startup SSOT | In-memory cache/metrics + config thresholds | Medium (duplicate with complete variant) | P0 | merge |
| performance_service_complete.py | Alternate performance implementation mirroring base module | Not clearly canonical in startup wiring | In-memory cache/metrics + config thresholds | High (duplicate scaffold risk) | P0 | delete-scaffold |
| prediction_cache_service.py | Cache layer for prediction outputs | Utility usage around intelligence routes/services | Redis primary, in-memory fallback | Medium (fallback can mask Redis outage) | P1 | wire-db |
| prometheus_metrics_service.py | Prometheus registry + metric helpers used by routes/middleware | Singleton helper (`get_metrics_service`) consumed by API/middleware | Prometheus client in-process metrics | Low | P0 | keep |
| qdrant_memory_service.py | Vector memory adapter for long-term retrieval | Optional wiring; used by vector/memory paths | Qdrant collections when configured | Medium (optional dependency) | P1 | keep |
| rate_limiting_service.py | Internal rate-limit policy service | Middleware/service-level usage | In-memory counters + optional Redis | Medium | P1 | wire-db |
| reinforcement_learning_optimizer.py | RL optimization helper for policy tuning | Service-level usage | Model state + task feedback history | Medium | P2 | keep |
| request_deduplication_service.py | Request idempotency/dedupe helper | Middleware/service-level usage | Redis keys or in-memory token cache | Medium | P1 | wire-db |
| run_event_buffer.py | In-memory ring buffer for recent RunEvents before/alongside persistence | Imported by task/event route stack | In-memory buffer + DB persistence path | Low | P0 | keep |
| scaling_metrics_service.py | Scaling signal metrics helper | Service-level usage | Prometheus/system metrics + queue depth | Medium | P1 | wire-prometheus |
| security_monitoring_service.py | Threat/security-event monitoring workflow | Service-level usage; not startup SSOT | In-memory security events/intel sets + config | High (security claims without durable store) | P0 | explicit-503 |
| security_service.py | AuthN/AuthZ/JWT/encryption helper service | Initialized in `service_manager.py`; legacy auth utility paths | In-memory audit log + env/config secrets | High (contains mock auth branch patterns) | P0 | merge |
| semantic_cache_service.py | Semantic response cache for repeated intents | Service-level usage | Redis/vector similarity cache | Medium | P1 | wire-db |
| sep_registry.py | Service Expert Profile registry/catalog for command center | Operator/mission/service-definition routes | Registry definitions + DB/JSON-backed metadata | Low | P0 | keep |
| service_manager.py | Registry / DI hub | startup | n/a | n/a | P0 | keep |
| structured_logging_service.py | Structured event logging helper | Service-level use | Application logs + optional sink exporters | Low | P2 | keep |
| system_monitor.py | System resource collector feeding metrics service | Started by monitor/system flows where enabled | psutil runtime metrics + Prometheus metrics service | Medium (direct metric internals write) | P0 | wire-prometheus |
| task_cache_service.py | Task read-through/write-through cache wrapper | Utility singleton (`get_task_cache_service`) and route/service usage | Redis primary, Postgres fallback via `src/database/connection.py` | Low | P0 | keep |
| timeout_service.py | Timeout guardrails/retry deadline helper | Service-level use | In-memory policy config | Low | P2 | keep |
| tracing_service.py | Trace/span correlation helper for runtime observability | Middleware/service-level use | In-memory trace context + log exporters | Medium | P1 | wire-prometheus |
| ultimate_fallback_system.py | Legacy/extended fallback orchestration variant | Not canonical; overlaps fallback modules | In-memory fallback graph + config | High (fallback duplication) | P1 | merge |
| universal_ai_manager.py | High-level AI capability manager facade | Service-level use | Router/provider config + model metadata | Medium | P1 | merge |
| vector_service.py | FAISS + sentence-transformers vector index service | Initialized in `service_manager.py`; service-level usage | Local FAISS index + embedding model artifacts | Low | P0 | keep |
| workflow_automation_service.py | Workflow automation orchestration helpers | Service-level usage with workflow APIs | DB workflow records + orchestrator task linkage | Medium | P1 | keep |

---

## Known cross-code pointers (seed for R1)

- `verify_auth` / `AMAS_DEV_MOCK_AUTH` — [`src/amas/api/main.py`](../src/amas/api/main.py)
- Demo API gate — [`src/api/production_guard.py`](../src/api/production_guard.py)
- Analytics defaults — [`src/api/routes/analytics.py`](../src/api/routes/analytics.py)
- OSINT mock branches — [`src/amas/agents/osint/osint_agent.py`](../src/amas/agents/osint/osint_agent.py)

---

## Allowed test doubles (document exceptions here)

| Area | Mock OK? | Notes |
|------|----------|--------|
| Third-party HTTP (Stripe, external SaaS) | Yes | Prefer recorded responses in CI |
| DB / orchestrator in unit Job A | Prefer no | Move to Job B real DB per [REAL_DATA_AND_CI_STRATEGY.md](next-generation-muli-agent-ai/REAL_DATA_AND_CI_STRATEGY.md) |

---

## R0-2 duplicate-pair decisions

| Pair | Decision | Rationale |
|------|----------|-----------|
| `monitoring_service.py` vs `monitoring_service_complete.py` | `monitoring_service.py` canonical, `*_complete` marked scaffold | Avoid dual runtime monitoring contracts and drift in SSOT behavior |
| `performance_service.py` vs `performance_service_complete.py` | `performance_service.py` canonical, `*_complete` marked scaffold | Keep one performance contract and reduce maintenance divergence |
| `integration_manager.py` vs `integration_manager_complete.py` | Canonicalize base manager; keep complete variant out of runtime path | Prevent split orchestration behavior in production routes |

---

## CAP-02 evidence index (non-P0 disposition, 2026-04-15)

This section closes **CAP-02** from [`FINAL_COMPLETION_CHECKLIST.md`](FINAL_COMPLETION_CHECKLIST.md): each **Action** from the matrix above is either **canonical with a live path** or **explicitly non-authoritative** for production APIs.

| Action bucket | Disposition | Runtime evidence |
|---------------|--------------|------------------|
| `merge` / duplicate pairs (monitoring, performance, fallback) | **Canonical modules** named in [R0-2 duplicate-pair decisions](#r0-2-duplicate-pair-decisions); variants marked scaffold stay off default import paths | Grep: `src/api/routes` does not import `monitoring_service_complete` / `performance_service_complete` as primary SSOT |
| `wire-db` (audit, caches, rate limit) | **Intent documented**; production truth for tasks/agents remains `src/database/connection.py` + route persistence | `audit_logging_service.py`, `task_cache_service.py` — trace via `grep` from `src/api` and `tests/unit` |
| `wire-prometheus` | **`prometheus_metrics_service.py`** is the in-process registry used by routes (`get_metrics_service`) | `src/amas/services/prometheus_metrics_service.py`, `run_event_buffer.py` (ingest counters) |
| `explicit-503` (email, CV, enterprise, incident, NLP) | **Optional connectors**: no default API success without provider; routes must return **503/501** when documented | Cross-check `src/api/routes` imports vs [`NO_MOCK_RUNTIME_POLICY.md`](NO_MOCK_RUNTIME_POLICY.md) |
| P1 **keep** rows | **Utility services** — not duplicated in matrix as “Complete” product features unless routed | Module list unchanged; operator program does not claim these as user-visible until routed |

**Conclusion:** P0 rows in the table above are filled; non-P0 rows retain **Action** labels as **maintenance/backlog** items, not blockers for operator-program delivery. Re-audit when adding new first-class API surfaces.

---

## R0-3 / R0-4 source-of-truth findings

- `deep_health_service.py` is the canonical dependency probe path for API-exposed deep health; `health_check_service.py` overlaps and should not present competing production truth.
- `prometheus_metrics_service.py` is canonical for route-level metrics; `src/monitoring/prometheus.py` should be treated as legacy/parallel stack unless explicitly wired and documented.
- `/api/v1/system/metrics` and `/api/v1/landing/metrics` intentionally expose different contracts, but this must remain documented (system route has task source metadata + fallback semantics; landing route is public dashboard summary).
- `system_monitor.py` should avoid direct metric internals mutation patterns and use metric-type-safe updates for long-term reliability.

---

*Last scaffold update: auto-generated module list (57 Python files under `src/amas/services/`). Replace **TBD** in priority order: P0 rows first, then duplicate pairs.*
