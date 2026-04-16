# AMAS gap audit (architecture vs code)

This document tracks mismatches between workspace architecture rules and the current tree, plus agent/tool coverage. Updated as part of the local-first thesis plan.

**Capability completion (rolling status × CI):** see [`CAPABILITY_MATRIX.md`](CAPABILITY_MATRIX.md).

**Interpretation note (“100% updated”):** this repo treats “complete” as **truthful alignment** between code, tests/CI, and docs. It does **not** imply every Tier-4 scaffold or “Planned” roadmap idea is implemented; those items must instead be explicitly labeled **Deferred / Non-goal** with a verification hook when they become in-scope.

**Next-generation operator program (command center, SEP/GEA, RunEvents, production integrity, phased execution):** see [`next-generation-muli-agent-ai/README.md`](next-generation-muli-agent-ai/README.md), [`next-generation-muli-agent-ai/PHASED_MASTER_TODO.md`](next-generation-muli-agent-ai/PHASED_MASTER_TODO.md), [`next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md`](next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md), [`next-generation-muli-agent-ai/TECH-MCP-N8N-SKILL-HUB-INFRA.md`](next-generation-muli-agent-ai/TECH-MCP-N8N-SKILL-HUB-INFRA.md), and backend honesty scaffold [`SERVICE_DATA_AUDIT.md`](SERVICE_DATA_AUDIT.md) (P0 rows filled; non-P0 actions tracked in § CAP-02 evidence index — **maintenance backlog**, not an undocumented blocker for operator delivery). **Frontend IA + routes:** [`frontend/COMMAND_CENTER_IA.md`](frontend/COMMAND_CENTER_IA.md). **Cursor Wave 2 plan:** `frontend_ux_phased_rebuild_91596267.plan.md` under the workspace `.cursor/plans/` (version in-repo if the team shares it).

**What we will do next (delivery intent):** Follow [`next-generation-muli-agent-ai/PHASED_MASTER_TODO.md`](next-generation-muli-agent-ai/PHASED_MASTER_TODO.md) — **D0** (doc hygiene), **R0–R4** (service-data honesty, production API truth, frontend runtime/tests, CI job split, verification), **F1–F9** (SEP/GEA, Mission Console, RunEvents, graph UI, sandbox, jobs, audit, provenance, etc., each mapped to FE-* / BE-* plans). Open items there are **expected** to close with real tests, no silent mocks on claimed-live paths, and doc updates in the same PR unless explicitly deferred in [`IMPLEMENTATION-STATUS-A-THROUGH-C.md`](next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md).

**Production go-live (tests + env + auth):** see [`deployment/PRODUCTION_READINESS_CHECKLIST.md`](deployment/PRODUCTION_READINESS_CHECKLIST.md) (not legacy percentage trackers).

**Repository layout (structure audit):** historical root-level Markdown is under [`docs/archive/`](archive/README.md); machine-readable inventory is [`deployment/REPO_STRUCTURE_INVENTORY.json`](deployment/REPO_STRUCTURE_INVENTORY.md) (regenerate with `python scripts/inventory_repo_structure.py`). Operator CLI: **`amas-doctor`** (`health` / `env` / `structure`) in [`src/amas/tools/diagnostics/cli.py`](../src/amas/tools/diagnostics/cli.py).

## Source-of-truth pointers (avoid phantom modules)

| Topic | Use this in code / docs |
|-------|-------------------------|
| AI routing + fallback | [`enhanced_router_v2.py`](../src/amas/ai/enhanced_router_v2.py), [`enhanced_router_class.py`](../src/amas/ai/enhanced_router_class.py) |
| Predictions + learning | [`predictive_engine.py`](../src/amas/intelligence/predictive_engine.py), [`intelligence_manager.py`](../src/amas/intelligence/intelligence_manager.py) |
| Task orchestration (API + CLI) | [`unified_intelligence_orchestrator.py`](../src/amas/core/unified_intelligence_orchestrator.py); interactive CLI uses [`unified_cli_facade.py`](../src/amas/core/unified_cli_facade.py) |

There is **no** `src/amas/core/ai_provider_router.py` or `src/amas/ml/task_predictor.py` unless added explicitly. Cursor rule [amas-architecture-overview.mdc](../.cursor/rules/amas-architecture-overview.mdc) is aligned to these paths.

## Integrations

| Expected (rules) | Status |
|------------------|--------|
| `src/amas/integrations/github_integration.py` | **Added** in this pass (read-only GitHub REST) |
| Slack, N8N, Notion, Jira, Salesforce | **Implemented** — see `src/amas/integrations/*_integration.py` and [`skywork_reuse_map.md`](skywork_reuse_map.md) for external catalog context |

## Agents vs native `AgentTool` modules

Many agents under `src/amas/agents/` rely on the LLM and optional registry tools. Concrete `AgentTool` implementations live mainly in `src/amas/agents/tools/` (DNS, WHOIS, SSL, scraper, API fetcher, optional security APIs).

| Agent | Default `tool_profile` | Notes |
|-------|------------------------|--------|
| `CodeAnalysisAgent` | `code_heavy` | Workspace read/grep/list + propose patch / command |
| `TestingAgent` | `code_heavy` | Same family as code analysis |
| `SecurityExpertAgent` | `security` | Network-oriented registry tools |
| `ResearchAgent`, `IntelligenceGatheringAgent`, `DataAgent` | `research` | Scraper + fetcher (+ optional APIs) |
| `IntegrationAgent`, `DeploymentAgent`, `ApiAgent` | `integration` | Tier-3 + GitHub helpers |
| `DocumentationAgent` | `documentation_light` | Lighter tool set for docs tasks |
| `MonitoringAgent`, `PerformanceAgent` | `ops` | Operational / metrics-oriented defaults |

## Vector memory (Qdrant vs offline FAISS)

| Mode | Component |
|------|-----------|
| `docker-compose.local-ai.yml` | **Qdrant** + optional tools `qdrant_memory_*` when `QDRANT_URL` is set |
| `docker-compose-offline.yml` | **FAISS** `vector-service` + in-process [`VectorService`](../src/amas/services/vector_service.py) |

Do not treat both as the same logical memory without an explicit sync strategy.

## MCP (optional)

| Item | Location |
|------|----------|
| HTTP bridge client | [`mcp_bridge.McpHttpBridge`](../src/amas/integrations/mcp_bridge.py) |
| Agent tool | `mcp_http_invoke` when `AMAS_MCP_HTTP_BASE_URL` is set |

## Local-only and routing

| Item | Status |
|------|--------|
| `AMAS_LOCAL_ONLY` in compose/scripts | Was present; **now enforced** in `enhanced_router_v2.get_available_providers` |
| `router.py` `get_available_providers` | **Delegates** to v2 when `AMAS_LOCAL_ONLY` or `AMAS_ALLOW_CLOUD` off |
| Per-agent Ollama model | `AMAS_OLLAMA_MODEL_<TYPE>` or `config/local_agent_models.yaml` via `local_model_config.py` |
| Weak local models / tool loop | `AMAS_DISABLE_NATIVE_TOOLS`, `AMAS_OLLAMA_DISABLE_TOOLS_TAGS` on [`BaseAgent`](src/amas/agents/base_agent.py) native tool loop |

## Service tier (API / orchestrator vs scaffold)

Static import pass: modules under `src/amas/services/` **directly referenced** from [`src/api/`](../src/api/) routes/middleware or [`unified_intelligence_orchestrator.py`](../src/amas/core/unified_intelligence_orchestrator.py).

| Tier | Service modules | Used by |
|------|-----------------|---------|
| **Production path** | `prometheus_metrics_service`, `system_monitor`, `tracing_service`, `prediction_cache_service`, `task_cache_service`, `email_service` (landing only) | `routes/system.py`, `tasks_integrated.py`, `landing.py`, `metrics.py`, `analytics.py`, `middleware/metrics_middleware.py` |
| **Orchestrator path** | `tracing_service`, `prometheus_metrics_service` | `unified_intelligence_orchestrator.py` (optional imports) |

Many other files under `src/amas/services/` (e.g. `ml_service`, `computer_vision_service`, `ai_analytics_service`) are **scaffolds or demos** with mock branches unless a route explicitly imports them—treat as **Tier 4 / thesis-out-of-scope** unless wired.

## Tool governance vs AgentTool registry

[`ToolExecutionGuard._execute_tool_implementation`](../src/amas/core/tool_governance/tool_registry.py) dispatches to [`amas.agents.tools.get_tool_registry`](../src/amas/agents/tools/__init__.py) when tool names match registered `AgentTool` names; legacy names `file_read` / `web_search` map to `workspace_read_file` / `web_scraper` when parameters include paths or URLs. If nothing matches, a **demo fallback** remains for unit tests and offline demos.

## Optional follow-ons (project_improvements)

| Item | Notes |
|------|--------|
| **pgvector** | Alternative to Qdrant for vectors entirely in Postgres; not implemented in this tree—see Vector memory section above. |
| **Critic hook** | Stub in [`critic_hook.py`](../src/amas/core/critic_hook.py); enable with `AMAS_ENABLE_CRITIC_HOOK=true` for future wiring from the orchestrator. **Deferral (2026-04-16):** not treated as production-complete until orchestrator wiring lands — see [`IMPLEMENTATION-STATUS-A-THROUGH-C.md`](next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md) Tier 2. |
| **E2E API** | Health checks against a running server: `pytest tests/e2e/ -m smoke` (skips if `AMAS_API_URL` unreachable). |

## Agent tool registry import order

`QDRANT_URL` and `AMAS_MCP_HTTP_BASE_URL` are read when [`register_tools`](../src/amas/agents/tools/register_tools.py) is first imported. Set these env vars **before** worker/app import in long-lived processes so optional tools register correctly (see also [`integrations.md`](integrations.md)).

## CI: smoke vs unit

Default GitHub Action **Unit tests** runs `pytest tests/unit/` only. Optional workflow **Smoke tests** runs `pytest tests/unit/ -m smoke` for a minimal import/orchestrator sanity check. Integration tests under `tests/integration/` often need Postgres/Redis/etc.; run locally or in a dedicated job with service containers.

## Hotspots (TODO / stubs)

| Location | Issue | Resolution direction |
|----------|--------|----------------------|
| `integration_agent.py` | Webhook dispatch | **`process_integration_event`** extended for slack/n8n/notion/jira/salesforce; Tier-3 clients under `integrations/` |
| `unified_intelligence_orchestrator.py` | Silent `pass` | **Progress/tracing** failures logged at debug; DNS path already logs resolution failure |
| `enhanced_router_class.py` | Health / latency stats | **`last_success` / `last_failure`** + per-call latency accumulation for `avg_latency_ms` |
| `router.py` | Provider TODO comments | Left for legacy universal router; v2 is source of truth for local-first |
| Various agents | bare `pass` in except branches | **Triage**: log at debug or narrow except (documentation/security/base_agent/prometheus stubs) |

## Definition of done (Tier 2)

- Local-only mode works with Ollama only.
- Per-agent model override works.
- Code-heavy + security + research tool profiles wired.
- Workspace tool pack registered.
- GitHub integration module exists and is callable from `IntegrationAgent`.
- Reference attribution doc present under `docs/reference_attribution.md`.
- SkyworkAI reuse matrix: `docs/skywork_reuse_map.md`.

## Prometheus and `metrics_available`

[`prometheus_metrics_service.py`](../src/amas/services/prometheus_metrics_service.py) registers real counters/histograms when `prometheus_client` is installed; otherwise it uses no-op stubs. **`metrics_client_available()`** reports whether exports are live.

- **`amas_task_queue_depth`** is updated from the orchestrator (`set_task_queue_depth`) on submit, dequeue, requeue, and error paths so the gauge tracks the in-process queue.
- **`/api/v1/system/metrics`** (see [`system.py`](../src/api/routes/system.py)) includes **`metrics_available`**, optional **DB-backed task counts** when PostgreSQL is connected, orchestrator agent counts, and (in development or when `AMAS_EXPOSE_AI_DEBUG=true`) provider-oriented fields.

## n8n clients (consolidated)

| Module | Role |
|--------|------|
| `src/amas/integrations/n8n_integration.py` | **Canonical** webhook client: `N8nIntegration.trigger_workflow` / `trigger_flow`, named URLs, `correlation_id` in payloads. |
| `src/amas/integration/n8n_connector.py` | Full connector for Integration Manager (workflows, credentials, webhooks). |
| ~~`src/amas/agents/n8n_integration.py`~~ | **Removed** (was mock). |
| ~~`src/amas/services/n8n_integration.py`~~ | **Removed** (unused duplicate). |

## HTTP integration webhooks

Verified routes (prefix **`/api/v1/webhooks/`**): GitHub (`X-Hub-Signature-256` + `GITHUB_WEBHOOK_SECRET`), Slack (`X-Slack-Signature` + `SLACK_SIGNING_SECRET`, including URL verification `challenge`). Implementation: [`integration_webhooks.py`](../src/api/routes/integration_webhooks.py).

## Current capabilities vs legacy docs

[`PRODUCTION_TODO.md`](PRODUCTION_TODO.md) is a **dated aspirational tracker** (e.g. 2025 percentages and phase claims). Treat it as a historical roadmap, not a live inventory. For **what this tree implements today**, prefer this file, [`integrations.md`](integrations.md), [`TROUBLESHOOTING_GUIDE.md`](TROUBLESHOOTING_GUIDE.md) (Ollama operators), and the source under `src/amas/`.

## CI: unit tests

Run locally (mock-friendly, no Ollama required):

```bash
set AMAS_LOCAL_ONLY=1
pytest tests/unit/ -q --tb=short
```

GitHub Actions: workflow **Unit tests** (`.github/workflows/unit-tests.yml`) runs `pytest tests/unit/` on push and pull request.

## Predictive engine persistence

Training DataFrames are saved under `data/models/training_snapshots/*.pkl`; fitted models and scalers are written to `data/models/*_model.pkl` after retrain. See [`docs/ml_learning.md`](ml_learning.md). This is **filesystem** persistence, not PostgreSQL `ml_training_data`, unless you add a separate sync.

## Integration test workflow

Workflow **Integration tests** (`.github/workflows/integration-tests.yml`) runs a mocked integration file (`tests/integration/test_tasks_integrated_integration.py`) on each push/PR for quick regression signal without service containers.

## Interactive CLI orchestrator

The interactive CLI uses [`unified_cli_facade.py`](../src/amas/core/unified_cli_facade.py) (`AMASOrchestrator` alias) so execution goes through `UnifiedIntelligenceOrchestrator`, matching the API. Legacy [`orchestrator.py`](../src/amas/orchestrator.py) remains for old scripts only.
