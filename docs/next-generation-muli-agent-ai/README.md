# Redirect stub (case-variant path)

This folder exists only to prevent case-insensitive filesystem confusion. The canonical hub is:

- `docs/next-generation-muli-agent-ai/README.md`

Do not add content here; update the canonical hub instead.
- **Backend mocked integration + frontend Playwright (interactive + a11y)**: [`.github/workflows/integration-tests.yml`](../../.github/workflows/integration-tests.yml)
- **Optional real Postgres lane**: [`.github/workflows/integration-real-db.yml`](../../.github/workflows/integration-real-db.yml)
- **Full-stack compose E2E (backend + frontend together)**: [`.github/workflows/e2e-fullstack-compose.yml`](../../.github/workflows/e2e-fullstack-compose.yml)

## Cursor `wave2-*` → phases → primary slices

| `wave2-*` id | Phases | Primary FE / BE plans |
|--------------|--------|------------------------|
| `wave2-global-engagement-advisor` | F1 | [FE-04](frontend-plans/FE-04-gea-officer-omnipresent.md), [BE-02](backend-plans/BE-02-gea-engagement-advise-orchestrator.md) |
| `wave2-services-capabilities-hub` | F1–F2 | [FE-05](frontend-plans/FE-05-services-catalog-mission-console-sep.md), [BE-03](backend-plans/BE-03-sep-service-registry-openapi.md), [BE-04](backend-plans/BE-04-orchestrator-runevents-team-changes.md) |
| `wave2-backend-run-events` | F3 | [BE-01](backend-plans/BE-01-run-events-persistence-replay-ws.md), [FE-03](frontend-plans/FE-03-run-graph-timeline-hydration.md) |
| `wave2-incidents-remediation-ui` | F4 | [FE-06](frontend-plans/FE-06-incidents-remediation-inline.md) |
| `wave2-pc-layout` | F5 | [FE-07](frontend-plans/FE-07-dockable-panes-debug-keyboard.md) |
| `wave2-visualization-core` | F6 | [FE-08](frontend-plans/FE-08-dag-timeline-filters-explain.md), [BE-05](backend-plans/BE-05-explain-task-orchestrator.md) |
| `wave2-sandbox-topology-jobs` | F7 | [FE-09](frontend-plans/FE-09-sandbox-topology-jobs.md), [BE-08](backend-plans/BE-08-jobs-scheduler-api.md) |
| `wave2-audit-quality-ci` | F8 | [FE-10](frontend-plans/FE-10-audit-a11y-testing.md), [BE-09](backend-plans/BE-09-audit-api-export-crossrefs.md) |
| `wave2-provenance-mcp-integrations-ui` | F9 | [FE-11](frontend-plans/FE-11-provenance-mcp-n8n.md), [BE-10](backend-plans/BE-10-provenance-integrations-health.md) |

---

## Start here

| Order | Document | What it is |
|-------|----------|------------|
| 1 | [PROGRAM-VISION-AND-CONSTITUTION.md](PROGRAM-VISION-AND-CONSTITUTION.md) | Vision, UX constitution (7 items), differentiator, production mandate, no-mock policy, stack alignment, north star. |
| 2 | [PHASED_MASTER_TODO.md](PHASED_MASTER_TODO.md) | **Master phase checklist** (D0, R0–R4, F1–F9) + Cursor `wave2-*` map + mermaid dependencies. |
| 3 | [IMPLEMENTATION-STATUS-A-THROUGH-C.md](IMPLEMENTATION-STATUS-A-THROUGH-C.md) | Honest A1–C6 + Services + GEA + provenance + testing status table. |
| 4 | [MASTER_NEXT_GENERATION_PLAN.md](MASTER_NEXT_GENERATION_PLAN.md) | Consolidated narrative + service matrix (28 rows) + execution order. |
| 5 | [frontend-plans/README.md](frontend-plans/README.md) | Index of **all UI/React** plan documents — implement in dependency order. |
| 6 | [backend-plans/README.md](backend-plans/README.md) | Index of **all API/orchestrator/persistence** plan documents. |

## Technology topics (one concern per file)

| Topic | Document |
|-------|----------|
| RunEvent bus, replay, OpenAPI | [TECH-RUNEVENTS-AND-TRACEABILITY.md](TECH-RUNEVENTS-AND-TRACEABILITY.md) |
| GEA + omnipresent Officer | [TECH-GEA-AND-OFFICER.md](TECH-GEA-AND-OFFICER.md) |
| SEP, Service Manager, Mission Console | [TECH-SEP-AND-SERVICES.md](TECH-SEP-AND-SERVICES.md) |
| MCP, n8n, skill hubs, compose / webhooks | [TECH-MCP-N8N-SKILL-HUB-INFRA.md](TECH-MCP-N8N-SKILL-HUB-INFRA.md) |
| Research (`docs/project_improvements`) | [RESEARCH-SYNTHESIS-PROJECT-IMPROVEMENTS.md](RESEARCH-SYNTHESIS-PROJECT-IMPROVEMENTS.md) |
| Prompts + `system-prompts-and-models-of-ai-tools-main` | [PROMPTS-REFERENCE-ATTRIBUTION.md](PROMPTS-REFERENCE-ATTRIBUTION.md) |
| Real data, mocks, CI jobs | [REAL_DATA_AND_CI_STRATEGY.md](REAL_DATA_AND_CI_STRATEGY.md) |
| Prompt distillation log (optional) | [CHANGELOG-PROMPTS.md](CHANGELOG-PROMPTS.md) |

## Repo cross-links (operational scaffolds)

| Artifact | Path |
|----------|------|
| Service module audit (R0; matrix maintained) | [../SERVICE_DATA_AUDIT.md](../SERVICE_DATA_AUDIT.md) |
| SEP `service_id` catalog (scaffold) | [../frontend/SERVICES_CATALOG.md](../frontend/SERVICES_CATALOG.md) |
| Command center IA | [../frontend/COMMAND_CENTER_IA.md](../frontend/COMMAND_CENTER_IA.md) |
| Env / integration | [../frontend/ENV_AND_INTEGRATION.md](../frontend/ENV_AND_INTEGRATION.md) |
| Run events API | [../api/RUN_EVENTS.md](../api/RUN_EVENTS.md) |
| Cursor hub (rules, skills, agents, commands) | [../../.cursor/README.md](../../.cursor/README.md) · [`AGENTS.md`](../../AGENTS.md) · slash **amas-cursor-onboard**, **amas-tech-debt-triage** |
| Cursor Wave 2 YAML todos | `.cursor/plans/frontend_ux_phased_rebuild_91596267.plan.md` |
| Capability matrix | [../CAPABILITY_MATRIX.md](../CAPABILITY_MATRIX.md) |
| Gap audit | [../GAP_AUDIT.md](../GAP_AUDIT.md) |

## How to run the program as a project

0. **Cursor** — Use slash command **amas-operator-roadmap** (repo `.cursor/commands/`) for a single-page index of this folder + matrix + GAP when planning.
1. **Product** — Lock scope per **frontend-plans/FE-*.md** and **backend-plans/BE-*.md** slice; one epic per file is fine.  
2. **Engineering** — For each PR, tick boxes in **PHASED_MASTER_TODO.md** and update **IMPLEMENTATION-STATUS** when user-visible behavior changes.  
3. **No orphan UI** — Any new route or panel must list its **BE-** dependency in the FE plan header.

When docs and code diverge, **update docs in the same PR** as the behavior change.

**Cursor Wave 2 plan:** `.cursor/plans/frontend_ux_phased_rebuild_91596267.plan.md` — its overview and **Documentation hub** section must stay aligned with this folder (see **PR protocol** in that plan).

When this pack and the code diverge, **update the docs in the same PR** as the behavior change.

When this pack and the code diverge, **update the docs in the same PR** as the behavior change.
