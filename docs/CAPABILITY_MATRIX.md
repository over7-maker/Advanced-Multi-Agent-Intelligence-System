# AMAS capability matrix (rolling)

Rolling inventory of **what the tree implements** versus aspirational architecture docs. Pair with [`GAP_AUDIT.md`](GAP_AUDIT.md) for deep dives (tiers, hotspots, path corrections).

## What we will do (delivery intent)

Burn-down order, slice IDs, and checkboxes live in [`next-generation-muli-agent-ai/PHASED_MASTER_TODO.md`](next-generation-muli-agent-ai/PHASED_MASTER_TODO.md) (**D0**, **R0–R4**, **F1–F9**, Cursor `wave2-*` where noted). **Narrative + 28-row service matrix:** [`next-generation-muli-agent-ai/MASTER_NEXT_GENERATION_PLAN.md`](next-generation-muli-agent-ai/MASTER_NEXT_GENERATION_PLAN.md). **Real data vs mocks + CI strategy:** [`next-generation-muli-agent-ai/REAL_DATA_AND_CI_STRATEGY.md`](next-generation-muli-agent-ai/REAL_DATA_AND_CI_STRATEGY.md). **Execution slices:** [`next-generation-muli-agent-ai/frontend-plans/README.md`](next-generation-muli-agent-ai/frontend-plans/README.md) (FE-*), [`next-generation-muli-agent-ai/backend-plans/README.md`](next-generation-muli-agent-ai/backend-plans/README.md) (BE-*). When a capability row moves toward **Complete**, tick the matching **F** / **R** phase line items in `PHASED_MASTER_TODO.md` (or record deferral in [`IMPLEMENTATION-STATUS-A-THROUGH-C.md`](next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md)) in the **same PR** as the code.

## Source-of-truth hierarchy

| Priority | Artifact | Role |
|----------|----------|------|
| 1 | [`GAP_AUDIT.md`](GAP_AUDIT.md) | Architecture vs code, service tiers, TODO hotspots |
| 2 | **This file** | Capability × status × CI verification |
| 3 | [`.cursor/README.md`](../.cursor/README.md) | Cursor affordances; links here (no duplicate table) |
| 4 | [`next-generation-muli-agent-ai/README.md`](next-generation-muli-agent-ai/README.md) | **Next-gen operator program** — command center, SEP/GEA, phased master todo, production integrity |
| 5 | [`PRODUCTION_TODO.md`](PRODUCTION_TODO.md) | Historical roadmap only |

## What “100% updated” means here

“100% updated” means the **repository’s claims are 100% consistent** with the tree and CI:

- **No over-claims**: anything marked **Complete** is on the production path (or explicitly flagged as “ops/manual”) and has a stated verification path.
- **No silent drift**: anything **Partial / Scaffold / Planned** must have either (a) a concrete follow-up checklist + verification hook, or (b) an explicit **Deferred / Non-goal** note pointing to the owning doc (typically `GAP_AUDIT.md` or `IMPLEMENTATION-STATUS-A-THROUGH-C.md`).

This is intentionally different from “implement every Planned idea in one PR.”

## Status legend

| Status | Meaning |
|--------|---------|
| **Complete** | On production path; covered by unit/contract tests where noted; env in [`.env.example`](../.env.example) when applicable |
| **Partial** | Subset of paths, feature flags, or mix of real + mock/scaffold |
| **Scaffold** | Module present; not on default API/orchestrator path |
| **Planned** | Described in rules/roadmap; no trustworthy implementation |

## How to update

1. Land code + tests in the same PR when behavior is user-visible or CI-relevant.
2. Change the row’s **Status** and **CI / verification** to match; add a **Owner doc** link if a new subsystem doc exists.
3. If the change is architectural or cross-cutting, also adjust [`GAP_AUDIT.md`](GAP_AUDIT.md) (hotspots, source-of-truth table).
4. If the change is part of the **operator program**, update [`PHASED_MASTER_TODO.md`](next-generation-muli-agent-ai/PHASED_MASTER_TODO.md) checkboxes and [`IMPLEMENTATION-STATUS-A-THROUGH-C.md`](next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md) when user-visible slices advance or slip.

## Matrix

| Capability | Status | CI / verification | Owner doc |
|------------|--------|---------------------|-----------|
| Next-gen operator UI (SRE center, GEA, SEP, RunEvent replay) | **Complete** | FE-09 depth: `sandbox_telemetry.v2` (recent RunEvents + counts), `topology.v2` (`summary` drill-down), Jobs execution → task + `/sandbox?taskId=`; same routes as before (`/engage`, DAG, GEA, jobs, metrics). **`GET /api/v1/probes`** **probes.v2** in OpenAPI + [`api/OPERATOR_PROBES.md`](api/OPERATOR_PROBES.md). Tests: `tests/unit/test_operator_sandbox_telemetry.py`, `tests/unit/test_system_topology_hotspots.py`, `tests/unit/test_operator_probes_v2.py`, Vitest sandbox panel | [next-generation-muli-agent-ai/README.md](next-generation-muli-agent-ai/README.md) |
| Backend service data audit (`src/amas/services`) | **Partial–Complete** | P0 + **CAP-02 evidence index** (non-P0 disposition) in [SERVICE_DATA_AUDIT](SERVICE_DATA_AUDIT.md) § CAP-02 | [SERVICE_DATA_AUDIT.md](SERVICE_DATA_AUDIT.md) |
| Unified orchestrator + task API path | Partial–Complete | `pytest tests/unit/` (task/orchestrator modules); full stack needs integration env | [`GAP_AUDIT.md`](GAP_AUDIT.md) |
| `enhanced_router_v2` local-first (`AMAS_LOCAL_ONLY`) | Complete | `pytest tests/unit/test_local_only_and_models.py` | [`GAP_AUDIT.md`](GAP_AUDIT.md) |
| Per-agent Ollama overrides | Complete | env + `local_model_config`; `test_local_only_and_models` | [`TROUBLESHOOTING_GUIDE.md`](TROUBLESHOOTING_GUIDE.md) |
| AgentTool registry + `tool_profiles` | Complete | `register_tools`, profile resolution in unit tests | [`GAP_AUDIT.md`](GAP_AUDIT.md) |
| Tool governance → AgentTool execution | Complete | `pytest tests/unit/test_tool_governance_agent_dispatch.py` | [`GAP_AUDIT.md`](GAP_AUDIT.md) — Tool governance |
| Tier-3 integrations (GitHub, Slack, n8n, Notion, Jira, Salesforce) | Partial–Complete | `pytest tests/unit/test_platform_integrations.py` (mocked); live needs keys | [`integrations.md`](integrations.md) |
| Signed HTTP webhooks (GitHub, Slack) | Complete | `integration_webhooks` + unit coverage | [`GAP_AUDIT.md`](GAP_AUDIT.md) — HTTP integration webhooks |
| n8n named webhooks + schemas | Complete | `n8n_integration.py`, `n8n_schemas.py`; F9-5 outbound envelope (schema + static doc): [`schemas/n8n_webhook_payload.schema.json`](../schemas/n8n_webhook_payload.schema.json), [`api/N8N_OUTBOUND_F9-5.md`](api/N8N_OUTBOUND_F9-5.md) | [`integrations.md`](integrations.md) |
| Qdrant memory tools (optional) | Partial | Set `QDRANT_URL` before app import; manual / optional unit paths | [`integrations.md`](integrations.md) |
| MCP HTTP bridge (optional) | Partial | `AMAS_MCP_HTTP_BASE_URL`; import order | [`integrations.md`](integrations.md) |
| `docker-compose.local-ai.yml` | Complete (ops) | Manual `docker compose`; not default CI | [`integrations.md`](integrations.md) |
| Unit CI | Complete | [`.github/workflows/unit-tests.yml`](../.github/workflows/unit-tests.yml) | [`GAP_AUDIT.md`](GAP_AUDIT.md) — CI |
| Smoke CI | Complete | [`.github/workflows/smoke-tests.yml`](../.github/workflows/smoke-tests.yml), `pytest -m smoke` | [`GAP_AUDIT.md`](GAP_AUDIT.md) — CI |
| Mocked integration CI | Complete | [`.github/workflows/integration-tests.yml`](../.github/workflows/integration-tests.yml) (pytest + **Playwright interactive + a11y**) | [`GAP_AUDIT.md`](GAP_AUDIT.md) |
| Real DB lane (optional) | **Partial–Complete** | [`.github/workflows/integration-real-db.yml`](../.github/workflows/integration-real-db.yml): Postgres service + **`alembic upgrade head`** + `pytest tests/real_db -m real_db` | [`REAL_DATA_AND_CI_STRATEGY.md`](next-generation-muli-agent-ai/REAL_DATA_AND_CI_STRATEGY.md) |
| Full `tests/integration/` with services | Scaffold / local | No default service-container job | [`GAP_AUDIT.md`](GAP_AUDIT.md) |
| API auth: `verify_auth` + `AMAS_REQUIRE_AUTH` | Partial–Complete | `src/amas/api/main.py`; document in `.env.example` | [`GAP_AUDIT.md`](GAP_AUDIT.md) |
| `critic_hook` | **Deferred (explicit)** | `AMAS_ENABLE_CRITIC_HOOK`; **not** wired from orchestrator — deferral recorded 2026-04-16 in [`IMPLEMENTATION-STATUS-A-THROUGH-C.md`](next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md) | [`GAP_AUDIT.md`](GAP_AUDIT.md) |
| Prometheus / `/api/v1/system/metrics` | Partial | Real when `prometheus_client` installed; `metrics_available` | [`GAP_AUDIT.md`](GAP_AUDIT.md) — Prometheus |
| Many `src/amas/services/*` (ML, CV, analytics, …) | Scaffold | GAP “Service tier” — not default imports from `src/api/` | [`GAP_AUDIT.md`](GAP_AUDIT.md) |
| Frontend + nginx | **Partial–Complete** | `npm run build` + Vitest + Playwright **`e2e:interactive`** + **`e2e:a11y`** in integration workflow | [COMMAND_CENTER_IA.md](frontend/COMMAND_CENTER_IA.md), `.cursor/rules/frontend-*.mdc` |
| pgvector | Planned | Not in tree | [`GAP_AUDIT.md`](GAP_AUDIT.md) |
| Production go-live (operator checklist) | **Partial–Complete** | Manual checklist + **[`.github/workflows/release-candidate-gate.yml`](../.github/workflows/release-candidate-gate.yml)** on tags / `workflow_dispatch` | [`deployment/PRODUCTION_READINESS_CHECKLIST.md`](deployment/PRODUCTION_READINESS_CHECKLIST.md) |
| `amas-doctor` diagnostics CLI | Complete | `amas-doctor structure`; `pytest tests/unit/test_amas_doctor_cli.py`; deep `health` needs DB/Redis/Neo4j env | [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) |

## Related links

- [`next-generation-muli-agent-ai/README.md`](next-generation-muli-agent-ai/README.md) — operator program hub
- [`deployment/PRODUCTION_READINESS_CHECKLIST.md`](deployment/PRODUCTION_READINESS_CHECKLIST.md) — honest go/no-go before deploy
- [`FINAL_COMPLETION_CHECKLIST.md`](FINAL_COMPLETION_CHECKLIST.md) — CAP-01..06 closure record + ongoing discipline
- [`PRODUCTION_CHECKLIST.md`](PRODUCTION_CHECKLIST.md) — infrastructure and secrets
- [`integrations.md`](integrations.md) — env vars, Tier-3, tool registration order
- [`ml_learning.md`](ml_learning.md) — predictive engine filesystem persistence
- [`.cursor/rules/amas-repository-map.mdc`](../.cursor/rules/amas-repository-map.mdc) — path map
