# Implementation status vs original spec (honest)

Wave 1 landed first, with additional Wave 2 slices now shipped. This table maps **plan IDs** to **Done / Partial / Not done** so remaining work does not over-claim.

| ID | Deliverable | Status | Notes / gap |
|----|-------------|--------|-------------|
| A1 | Env/proxy/CORS/auth matrix | **Done** | `docs/frontend/ENV_AND_INTEGRATION.md`, `.env.example` |
| A2 | Auth UX + 401/503 hints | **Done** | `formatApiErrorWithHints`, Login, ProtectedRoute |
| A3 | Task lifecycle honesty | **Done** | `TaskResponse` exposes optional `parameters`, `started_at`, `updated_at`; live run page shows summary / `created_by` / prediction / parameter keys when present (`TaskExecutionView`) |
| A4 | WS topics run/sandbox/system | **Done** | `tasks_integrated` now emits richer `tool_call_*`, `sandbox_*`, `plan_updated`, `team_changed` run events and topic tags |
| A5 | RunEvent schema + persistence + replay | **Done** | Schema/docs updated and persisted replay path (`GET /tasks/{id}/events`) aligned with enriched event taxonomy; optional `tests/real_db/test_task_run_events_merge.py` |
| A6 | `VITE_AMAS_DEBUG` debug drawer | **Done** | Debug drawer added on run detail behind `VITE_AMAS_DEBUG` |
| B0 | IA map | **Done** | `COMMAND_CENTER_IA.md` |
| B1 | Live system + topology | **Done** | Product scope: **Live strip + hotspots + probes** (no full topology editor). `GET /api/v1/system/topology-hotspots` **`topology.v2`** adds `summary` (queue depth + Postgres task counts when DB reachable). [COMMAND_CENTER_IA](../frontend/COMMAND_CENTER_IA.md) |
| B2 | Incidents inline graph/timeline | **Done** | Incidents drawer embeds `RunGraphView` + `RunTimelineScrubber` from replay events |
| B3 | Remediation dry-run + subgraph | **Done** | Incidents drawer renders remediation dry-run subgraph chips from structured plan payload |
| B4 | Audit grid/filters/export | **Done** | Sticky table + quick + per-column filters + CSV export (`AuditPage`); optional upgrade to MUI X DataGrid later |
| B5 | Dockable panes + per-pane shortcuts | **Done** | Run observability includes pane keyboard model (`Alt+1..4`) and active-pane highlighting + region labels (LW-6) |
| C1 | Run graph mission control (DAG, node panel) | **Done** | Mission + run pages: manager-root + RunEvent states; **lazy `@xyflow/react` DAG** when event slice has nodes (`RunGraphView` / `RunGraphXyFlow`) |
| C2 | Zoomable axis, filters, scrub as-of | **Done** | As-of scrub with runtime filters is wired into run graph/timeline slices, including phase chips from real RunEvents (`phase_started` / `phase_completed`) |
| C3 | Sandbox visualizer | **Done** | `/sandbox?taskId=` global page + run-observability panel share `SandboxVisualizerPanel` + real `GET /tasks/{id}/sandbox-telemetry` |
| C4 | Topology + incident/run hotspots | **Done** | `GET /api/v1/system/topology-hotspots` includes incident overlays from real failed-task rows and **`topology.v2` `summary`** for operator drill-down; Live system renders overlays + Postgres/orchestrator summary line |
| C5 | Jobs first-class | **Done** | Jobs lists workflows, supports start/cancel executions (`POST /workflows/{id}/start`, `POST /workflows/{id}/cancel`), execution history (`GET /workflows/{id}/executions`), schedule lifecycle (`GET/PUT/DELETE /workflows/{id}/schedule`) with admin/operator gating, and API-lifespan `WorkflowScheduleRunner` cron dispatch depth (BE-08); **lineage**: execution history links **task** + **`/sandbox?taskId=`** when `root_task_id` is set |
| C6 | Explain orchestrator-backed + cross-link | **Done** | Explain panel accepts graph-node focus and calls explain API with node-targeted context |
| Testing | Playwright + Vitest fixtures | **Done** | RunEvent fixture validator + optional `E2E_API_BASE`; Vitest (jobs, Engage, `SandboxVisualizerPanel`); CI: **interactive** E2E (`e2e/command-center-interactive.spec.ts`) + **a11y** sweep (`e2e/a11y-command-center.spec.ts`) in [`.github/workflows/integration-tests.yml`](../../.github/workflows/integration-tests.yml) |
| Testing (full-stack) | Compose E2E lane (API + UI) | **Deferred (explicit)** | Acceptance: workflow boots Postgres/Redis/API and runs Playwright against live API (no proxy ECONNREFUSED). Verification hook: [`.github/workflows/e2e-fullstack-compose.yml`](../../.github/workflows/e2e-fullstack-compose.yml) using `docker-compose.e2e.fullstack.yml`. |
| Services catalog | `/services` hub | **Done** | `/services` plus mission deep links and palette synonyms are fully wired |
| SEP + Mission Console | Manager + multi-expert + `/services/:id` | **Done** | Mission Console resolves manager-root and expert DAG from SEP + optional RunEvents hydration |
| GEA | `/engage` + Officer omnipresent | **Done** | `/engage` supports advisory + durable multi-task join via **`POST /engagement/create-joined`** and UI action **Create joined tasks now**; also keeps single-task fallback (`parameters.joined_engagement`) |
| Run provenance | orchestrator vs n8n vs job badges | **Done** | Provenance badges/filters expanded across run observability and operator routes |
| MCP / automation health | Live/Integrations chips | **Done** | Operator probes at `GET /api/v1/probes` — **`probes.v2`** (2026-04-16): `configured` / `ok` / `latency_ms` / `error_code`; unset `AMAS_*_HEALTH_URL` → `not_configured` (no fake localhost) |

---

**LW backlog (2026-04-15):** [PHASED_MASTER_TODO.md](PHASED_MASTER_TODO.md) — **LW-1 … LW-6** closed in tree (LW-3 lazy DAG; LW-6 command-center a11y patterns).

## CAP closure (2026-04-15)

| CAP | Status | Evidence |
|-----|--------|----------|
| CAP-01 Operator UI depth | **Done** | `sandbox_telemetry.v2`, `topology.v2` + Live UI; Jobs → sandbox lineage; tests: `tests/unit/test_operator_sandbox_telemetry.py`, `tests/unit/test_system_topology_hotspots.py`, `tests/real_db/test_topology_hotspots_summary.py`, `frontend/src/components/runs/SandboxVisualizerPanel.test.tsx` |
| CAP-02 Service audit | **Done (evidence index)** | Non-P0 disposition + wiring anchors in [`../SERVICE_DATA_AUDIT.md`](../SERVICE_DATA_AUDIT.md) § CAP-02 |
| CAP-03 Integration confidence | **Done** | Replaced placeholder `pass` integration tests with export contract test; real_db topology summary test |
| CAP-04 Frontend CI | **Done** | `npm run e2e:interactive` in `integration-tests.yml` |
| CAP-05 Release gate | **Done** | [`.github/workflows/release-candidate-gate.yml`](../../.github/workflows/release-candidate-gate.yml) |
| CAP-06 Docs lockstep | **Done** | This file + `CAPABILITY_MATRIX.md` + `FINAL_COMPLETION_CHECKLIST.md` aligned in same change set |

*Prior “remaining CAP” bullets are satisfied; use [`../FINAL_COMPLETION_CHECKLIST.md`](../FINAL_COMPLETION_CHECKLIST.md) for ongoing release discipline.*

---

## Bounded completeness — Tier 1 (2026-04-16)

| Item | Status | Evidence |
|------|--------|----------|
| Single canonical hub path | **Done** | [`README.md`](README.md) — use lowercase `…-muli-agent-ai/` in all new links (Linux CI / case-sensitive clones) |
| `probes.v2` contract | **Done** | OpenAPI (`OperatorProbesResponseV2` / `OperatorProbeCheckV2` on `GET /api/v1/probes`) + static [`../api/OPERATOR_PROBES.md`](../api/OPERATOR_PROBES.md) |
| F9-5 n8n outbound JSON | **Schema + static doc** | [`schemas/n8n_webhook_payload.schema.json`](../../schemas/n8n_webhook_payload.schema.json), [`../api/N8N_OUTBOUND_F9-5.md`](../api/N8N_OUTBOUND_F9-5.md); OpenAPI component for outbound POST **when** integration ships |
| CI confidence | **Ongoing** | [`.github/workflows/integration-real-db.yml`](../../.github/workflows/integration-real-db.yml), [`.github/workflows/release-candidate-gate.yml`](../../.github/workflows/release-candidate-gate.yml); see [`../deployment/PRODUCTION_READINESS_CHECKLIST.md`](../deployment/PRODUCTION_READINESS_CHECKLIST.md) |

## Tier 2 track picked — `critic_hook` (explicit deferral)

| Item | Status | Notes |
|------|--------|-------|
| `critic_hook` from orchestrator | **Deferred** | `AMAS_ENABLE_CRITIC_HOOK` and related code remain **off the default execution path** until a prioritized wiring pass; tracked as GAP backlog, not hidden “Complete” |

Do not mark [`../CAPABILITY_MATRIX.md`](../CAPABILITY_MATRIX.md) **Complete** for this row until orchestrator integration + tests land.
