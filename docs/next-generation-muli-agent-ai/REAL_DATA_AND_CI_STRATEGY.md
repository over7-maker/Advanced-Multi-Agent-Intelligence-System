# Real data and minimal mocking — production + tests

**Goal:** Align the entire program with **production integrity** (see [PROGRAM-VISION-AND-CONSTITUTION.md](PROGRAM-VISION-AND-CONSTITUTION.md) and [MASTER_NEXT_GENERATION_PLAN.md](MASTER_NEXT_GENERATION_PLAN.md)): workspace rules already require real orchestrator, **EnhancedAIRouter**, and persistence—not fabricated HTTP bodies. This document phases the **migration away from misleading mocks** and defines **allowed test doubles**.

**Reality check**

- Gaps are **specific modules** and **dev-only auth**, not “the whole repo ignores rules.”
- Tests today use `MagicMock`, `@patch`, `vi.mock` heavily (`tests/conftest.py`, `tests/api/test_landing_endpoints.py`, `frontend/src/test/mocks/api.ts`, …). Removing all mocks **without replacement** breaks CI until real-service tests exist.
- “Real data” for AI means **billable cloud APIs** or **local models** (`AMAS_LOCAL_ONLY`, `src/amas/ai/enhanced_router_v2.py`); unit-speed tests still need **narrow doubles** for true externals.

## Phase RX evidence update

- `R0` audit closure: `docs/SERVICE_DATA_AUDIT.md` has no remaining `TBD` service rows and includes duplicate-pair + SSOT findings.
- `R3/R4` CI closure:
  - Workflow: `.github/workflows/phase-rx-ci.yml` (Job A/B + optional Job C)
  - Evidence docs: `docs/ci/PHASE_RX_CI_TOPOLOGY.md`, `docs/ci/PHASE_RX_VERIFICATION.md`
- `F` runtime evidence:
  - SEP reverse index endpoint: `GET /api/v1/service-definitions/agents/{agent_id}/services`
  - Real probes endpoint: `GET /api/v1/probes` (mounted on the operator router under `/api/v1`)
  - Rich run events in `tasks_integrated` progress broadcasts (`tool_call_*`, `sandbox_*`, `plan_updated`, `team_changed`)

---

## Phase 1 — Full service analysis (same outputs / mock-like behavior)

**Goal:** Treat “mock data” broadly—canned, identical, or non-store-backed results—including duplicate services that re-implement APIs with static payloads.

### 1a. Catalog every backend service module

- Enumerate Python modules under `src/amas/services/` (~57 files), including pairs like `monitoring_service.py` / `monitoring_service_complete.py`, `performance_service.py` / `performance_service_complete.py`, `intelligent_fallback_system.py` / `ultimate_fallback_system.py`.
- For each file, record in **`docs/SERVICE_DATA_AUDIT.md`** (create in this phase):
  - Purpose (one line from docstring or class name).
  - Wiring: constructed in `src/amas/services/service_manager.py` / startup, or orphan/dead?
  - Authoritative data source: Postgres / Redis / Neo4j / Qdrant / Prometheus / filesystem / **EnhancedAIRouter only** / none (in-memory dict).
  - Risk flags: grep hits for `mock`, `Mock`, `fake`, `dummy`, `placeholder`, `sample_data`, `hardcoded`, `TODO:.*real`, static dict returns, `random` without seed, duplicate bodies across `*_complete` files.

### 1b. Detect duplicate / same-output logic

- Compare `*_complete.py` vs base—diff public APIs and call sites; flag same shapes (likely scaffold).
- Cross-service: metrics/health flows (`deep_health_service.py`, `health_check_service.py`, `system_monitor.py`, `monitoring_service*.py`)—multiple endpoints aggregating the same three numbers without SSOT.

### 1c. Optional runtime spot-check

- With stack up, hit parallel routes (`/api/v1/system/metrics`, landing metrics, Prometheus text); identical JSON across unrelated features when DB differs → investigate stub convergence.

### 1d. Deliverable

- Sortable table: service × data source × mock risk × action (**delete / merge / wire DB / wire router / explicit 503**).
- P0 (user-visible / orchestrator-adjacent) vs P2 (experimental / duplicate `*_complete`).

### 1e. Carry-forward inventory (seed rows in audit doc)

- Dev auth fallback: `verify_auth` in `src/amas/api/main.py` when `auth_manager` missing in dev-like `ENVIRONMENT`.
- Demo API gate: `src/api/production_guard.py`, `require_demo_api`.
- Routes defaulting zeros/empty without DB: e.g. `src/api/routes/analytics.py`.
- Agents with explicit Mock branches: e.g. `src/amas/agents/osint/osint_agent.py`, `src/amas/services/advanced_analytics_service.py`.

### 1f. Define allowed test exceptions

- Mocking **third-party HTTP only** while DB/orchestrator stay real in Job B—or CI cost/flake explodes.

---

## Phase 2 — Production: auth and API responses

- **Auth:** Production/staging never return dev mock user; keep 503 when `AMAS_REQUIRE_AUTH` and no manager. Development: opt-in `AMAS_DEV_MOCK_AUTH=true` (default **false**) for mock user story.
- **Analytics / system metrics:** Extend `src/api/routes/analytics.py` (+ services) so summaries read Postgres (repositories) and/or Prometheus consistently; **503/501** with clear message when store unavailable instead of silent misleading zeros.
- **Demo / legacy:** `require_demo_api` usages → real persistence or **501** unless `AMAS_ALLOW_DEMO_API=true`.
- **Agents (OSINT, analytics):** For every “live” product claim, execution goes through **EnhancedAIRouter** + real tools or structured **`capability_disabled`**—no fabricated mock registrar content.

---

## Phase 3 — Frontend: runtime vs tests

- **Runtime:** Axios `baseURL` + WebSocket host always target real API (`frontend/src/services/api.ts`, `websocket.ts`); document `VITE_*` for Docker vs local.
- **Tests:** Replace Vitest tests that mock the whole API with:
  - Playwright smoke on `docker compose`, and/or
  - RTL against test API + seeded DB (slower, no `vi.mock` of `apiService`).
- Keep a **small** set of sub-second pure UI tests (formatting only) if valuable.

---

## Phase 4 — Backend tests: migration strategy

### CI layout

- **Job A (fast):** narrow unit tests, pure functions, minimal/no mocks.
- **Job B (integration, real DB):** GitHub Actions workflow [`.github/workflows/integration-real-db.yml`](../../.github/workflows/integration-real-db.yml) — **Postgres 15 service**, `alembic upgrade head`, then `pytest tests/real_db -m real_db`. Example tests: `tests/real_db/test_task_run_events_merge.py`, `tests/real_db/test_topology_hotspots_summary.py` (topology `summary` when DB reachable). Uses `DATABASE_URL=postgresql://postgres:amas_password@127.0.0.1:5432/amas`.
- **Job C (optional gated):** full stack + `AMAS_LOCAL_ONLY=1` + Ollama, or cloud keys in GitHub Secrets—never in repo.

### Rewrite pattern

- For each `tests/unit/` file patching orchestrator/DB: move scenario to **Job B** with fixtures **or** delete if superseded by integration test.
- **conftest.py:** evolve toward session-scoped DB fixtures + transaction rollback per test once Job B exists.

Expect large migration; track with checklist column in `docs/SERVICE_DATA_AUDIT.md` or GitHub Project.

### R3-4 legacy lane (current)

- `tests/unit/test_tasks_integrated_edge_cases.py` carries **`@pytest.mark.tasks_integrated_db_mock`** (patches DB / orchestrator / websocket).
- **Job A** runs `pytest tests/unit/ -m "not tasks_integrated_db_mock"` then a **second** step runs that file alone so coverage is retained while honest unit defaults stay mock-light.
- Prefer moving scenarios to **`@pytest.mark.real_db`** (compose Job B). Remove this subsection when the file is empty or fully migrated.

### F8-3 RunEvent fixture gate

- Recorded samples: `tests/fixtures/run_event_normalized_samples.json`
- Validator: `python scripts/validate_run_event_fixtures.py` (unit + integration workflows)
- Optional API contract smoke: `frontend/e2e/smoke-api.spec.ts` when `E2E_API_BASE` is set

---

## Phase 5 — Verification and guardrails

- **DoD per phase:** pytest green for chosen job split; `docker compose up` + smoke script; `npm run build` + Playwright smoke.
- **Optional lint:** CI step fails on new `return {"mock"` / `Mock Registrar` under `src/` (allowlist `tests/` for third-party doubles).

### Target test topology (mermaid)

```mermaid
flowchart LR
  subgraph fast [JobA_fast]
    PureFns[Pure_unit_tests]
  end
  subgraph integ [JobB_integration]
    Compose[Docker_compose_deps]
    PytestDB[pytest_real_DB]
    Compose --> PytestDB
  end
  subgraph e2e [JobC_optional]
    Stack[Full_stack_or_Ollama]
    Playwright[Playwright_smoke]
    Stack --> Playwright
  end
```

---

## Risks and constraints

- **Roadmap alignment:** track post-wave items in [PHASED_MASTER_TODO.md](PHASED_MASTER_TODO.md) `LW-*` so CI and roadmap stay synchronized.
- **Cost / secrets:** Real cloud AI in CI needs budget + Secrets; prefer `AMAS_LOCAL_ONLY` + Ollama for “real stack.”
- **Flake / time:** Real DB/network slower—parallelize by marker/module.
- **Permanent mocks:** True externals (e.g. Stripe webhook signatures) may keep sandboxes/doubles—**document** as explicit exceptions.

---

## Next hardening cycle (`LW-*` roadmap links)

The following are explicitly mirrored from `PHASED_MASTER_TODO.md` post-wave backlog:

- **LW-1** Frontend typecheck debt cleanup (legacy MUI Grid API + strict TS warnings outside Wave 2 touchpoints).
- **LW-2** API/client type parity fixes (`status_message` vs `message`, `listIntegrations` typing drift including `limit` filter mismatch).
- **LW-3** Visualization upgrade from chip-strip graph to full DAG canvas once backend emits stable edge/node metadata.
- **LW-4** RunEvents replay hardening tests for persistence + dedupe on `GET /api/v1/tasks/{id}/events`.
- **LW-5** Playwright deep flow expansion: login → live system → run detail timeline/node assertions under `E2E_API_BASE` gating.
- **LW-6** WCAG completion pass for command center (focus order, drawer traps, reduced-motion, contrast regressions).

---

## Execution order handoff (`R1` / `R2` / `LW-*`)

Use this sequence for the next PRs so roadmap and CI stay aligned:

1. **R1-1 (auth truthfulness)** *(done)*  
   - **Target files:** `src/amas/api/main.py`, `docs/frontend/ENV_AND_INTEGRATION.md`, `docs/next-generation-muli-agent-ai/PHASED_MASTER_TODO.md`  
   - **Acceptance:** production/staging never return dev mock user; dev mock remains explicit opt-in only.  
   - **Verify:** auth route smoke + env-matrix doc review.

2. **R1-2 (analytics/system truthfulness)** *(done)*  
   - **Target files:** `src/api/routes/analytics.py`, related monitoring services, `docs/SERVICE_DATA_AUDIT.md`  
   - **Acceptance:** metrics endpoints return store-backed values or explicit `503/501` (no silent zeros).  
   - **Verify:** route tests for both “store available” and “store unavailable” paths.

3. **R1-3 / R1-4 (demo gate + agent mock branches)** *(done)*  
   - **Target files:** `src/api/production_guard.py`, `src/api/routes/testing.py`, `src/amas/agents/osint/osint_agent.py`, related service call sites.  
   - **Acceptance:** demo-only behavior gated behind explicit flags; live claims route through orchestrator/router or return structured capability-disabled responses.  
   - **Verify:** unit/integration tests for flag behavior and fallback semantics. *(Current passes add testing route demo-gate coverage plus truthfulness tests for Investigation/Forensics/Metadata/Technology Monitor/Reverse Engineering/Reporting/Data Analysis disabled semantics.)*

4. **No-mock runtime policy (enforced)** *(done)*  
   - **Policy doc:** `docs/NO_MOCK_RUNTIME_POLICY.md`  
   - **CI guard:** `scripts/check_no_mock_runtime.py` in `unit-tests.yml` blocks newly added runtime mock/fake/placeholder patterns under `src/`.  
   - **Acceptance:** runtime routes/agents use real data paths or explicit `501/503` / `capability_disabled` semantics.
5. **R2-1 (frontend runtime env/proxy validation)** *(done)*  
   - **Target files:** `frontend/src/services/api.ts`, `frontend/src/services/websocket.ts`, `docs/frontend/ENV_AND_INTEGRATION.md`.  
   - **Acceptance:** Docker/local env matrix documented and verified against real API targets.  
   - **Verify:** `npm run build`, manual env-switch smoke. *(Implemented host-reachable API URL resolution + WS resolution precedence and documented verification checklist.)*

6. **R2-2 (test realism migration)** *(done — first batch)*  
   - **Target files:** frontend tests replacing full `apiService` mocks; Playwright configs/specs.  
   - **Acceptance:** critical command-center flow validated through API-backed tests; mock-only suites reduced to formatting/pure UI edges.  
   - **Verify:** `npx playwright test`, targeted `vitest` suites. *(Current pass adds `frontend/e2e/tasks-real-api.spec.ts`, uses `TaskList.test.tsx` (canonical list), drops the legacy `TaskListComplete` stub, and keeps `componentSmoke` deterministic.)*

Carryover priority from this block maps to `LW-*`: start with `LW-2`, `LW-4`, and `LW-5` immediately after `R1-1`/`R1-2`.

---

## Relationship to `system-prompts-and-models-of-ai-tools-main`

That tree informs **prompt engineering** via [docs/reference_attribution.md](../reference_attribution.md); it does **not** replace service data audit or CI strategy. Distilled patterns go into `src/amas/prompts/`; **service data** truth comes from **stores and orchestrator**, not from prompt files.

---

*Maintained with [PHASED_MASTER_TODO.md](PHASED_MASTER_TODO.md) Phases R0–R4.*
