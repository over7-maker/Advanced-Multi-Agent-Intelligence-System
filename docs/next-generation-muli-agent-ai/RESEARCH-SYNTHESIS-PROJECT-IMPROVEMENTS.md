# Research synthesis — `docs/project_improvements/`

This folder contains **architecture research**, not runtime dependencies. It informs **Wave 2+** API contracts and UI layout so the shell matches how serious **local multi-agent + automation** stacks are built (2025–2026).

**Canonical sources (three files):**

- [`extra_sources.md`](../project_improvements/extra_sources.md)
- [`Advanced Technologies for Local Multi‑Agent AI (2025–2026).md`](../project_improvements/Advanced%20Technologies%20for%20Local%20Multi%E2%80%91Agent%20AI%20(2025%E2%80%932026).md)
- [`Open‑Source Projects Using n8n as a Core Backend for AI and Automation.md`](../project_improvements/Open%E2%80%91Source%20Projects%20Using%20n8n%20as%20a%20Core%20Backend%20for%20AI%20and%20Automation.md)

**Infra and integration detail** is also centralized in [TECH-MCP-N8N-SKILL-HUB-INFRA.md](./TECH-MCP-N8N-SKILL-HUB-INFRA.md) so this file stays a **synthesis** without duplicating every operational note.

---

## Adoption status (closure)

| Source file (under [`docs/project_improvements/`](../project_improvements/)) | Adoption | Tracking |
|-----------------------------------------------------------------------------|----------|----------|
| [`extra_sources.md`](../project_improvements/extra_sources.md) | **Shipped (Partial)** — IO/automation + MCP patterns reflected in [TECH-MCP-N8N-SKILL-HUB-INFRA.md](./TECH-MCP-N8N-SKILL-HUB-INFRA.md), [ENV_AND_INTEGRATION.md](../frontend/ENV_AND_INTEGRATION.md), FE-11 / BE-10 probes | Ongoing operator copy |
| [Advanced Technologies for Local Multi‑Agent AI (2025–2026)](../project_improvements/Advanced%20Technologies%20for%20Local%20Multi%E2%80%91Agent%20AI%20(2025%E2%80%932026).md) | **Partial** — strict JSON / checkpoint narrative aligns with RunEvents + GEA versioning; not every survey primitive is implemented | [BE-01](backend-plans/BE-01-run-events-persistence-replay-ws.md), **LW-3** DAG depth |
| [Open‑Source Projects Using n8n as a Core Backend…](../project_improvements/Open%E2%80%91Source%20Projects%20Using%20n8n%20as%20a%20Core%20Backend%20for%20AI%20and%20Automation.md) | **Deferred** — n8n as **IO layer** only; core orchestration stays **UnifiedIntelligenceOrchestrator** ([PROGRAM-VISION-AND-CONSTITUTION.md](./PROGRAM-VISION-AND-CONSTITUTION.md)) | Provenance + webhooks, not cognitive core |

**Rule:** These files are **not** imported at runtime. Product changes continue in BE/FE slices and [`PHASED_MASTER_TODO.md`](./PHASED_MASTER_TODO.md).

### Post-CAP roadmap alignment (research → slices)

| Research theme | Where it lands (do not edit research files for product) |
|----------------|--------------------------------------------------------|
| n8n / MCP compose + UI vs webhook hosts | [TECH-MCP-N8N-SKILL-HUB-INFRA.md](./TECH-MCP-N8N-SKILL-HUB-INFRA.md), [FE-11](frontend-plans/FE-11-provenance-mcp-n8n.md), [BE-10](backend-plans/BE-10-provenance-integrations-health.md), [ENV_AND_INTEGRATION.md](../frontend/ENV_AND_INTEGRATION.md) |
| Structured automation health | `GET /api/v1/probes` (`probes.v2`), Live system — **real HTTP or explicit not_configured** |
| Starter-kit / shared network patterns | Deployment docs + env; **no** orchestrator bypass ([PROGRAM-VISION-AND-CONSTITUTION.md](./PROGRAM-VISION-AND-CONSTITUTION.md)) |

---

## Source → takeaway (summary)

| Source | Takeaway for AMAS |
|--------|-------------------|
| [`extra_sources.md`](../project_improvements/extra_sources.md) | **n8n** as IO/automation microservice (webhooks, schedules); **MCP** skill hubs shared with agents; compose-style stacks (Ollama + vector DB + Postgres beside workflows). **UI must show which system owns the run** and link out only via configured integration bases. |
| [Advanced Technologies for Local Multi-Agent AI (2025–2026)](../project_improvements/Advanced%20Technologies%20for%20Local%20Multi%E2%80%91Agent%20AI%20(2025%E2%80%932026).md) | **Strict JSON / grammar-safe** planner outputs; LangGraph-style **state + checkpoint/replay**; MCP as shared tool surface; **observability per agent hop**. RunEvent payloads and GEA JSON should trend **typed + versioned**; timeline/run detail reserve space for **checkpoint resume** when backend exposes IDs. |
| [Open-Source Projects Using n8n as a Core Backend…](../project_improvements/Open%E2%80%91Source%20Projects%20Using%20n8n%20as%20a%20Core%20Backend%20for%20AI%20and%20Automation.md) | React dashboards on **structured pipeline output** (e.g. SOC-CERT); webhook API surface; layered pipelines with retries. **Incidents / Jobs / TI-oriented SEP rows** should mirror **structured feeds** in UI, not prose alone. |

---

## Infra and compose (Self-Hosted AI Starter Kit + peers)

| Research item | What it is | AMAS mapping |
|----------------|------------|--------------|
| **n8n Self-Hosted AI Starter Kit** (official docs + repo) | Docker Compose: **n8n + Ollama + Qdrant + Postgres**; predictable internal hostnames (e.g. `http://qdrant:6333`); curated env for local AI workflows | Align **compose/k8s** docs with “AMAS + same network” so agents and n8n share **Ollama/vector/DB** only where product chooses—not a mandate to merge runtimes. UI: **honest** “stack segment” when n8n base URL unset. |
| **Shared volumes** (e.g. `/data/shared` in starter-kit README patterns) | n8n and tools share filesystem for ingest/export | If AMAS uses shared volumes, document **security boundary** (who writes, redaction); no fake “connected” in UI without mount probe. |
| **Cloudflare / edge starters** (referenced in extra_sources) | n8n behind tunnel; **UI vs webhook** hostname split | Operational guidance: [ENV_AND_INTEGRATION.md](../frontend/ENV_AND_INTEGRATION.md) § n8n / webhooks; [TECH-MCP-N8N-SKILL-HUB-INFRA.md](./TECH-MCP-N8N-SKILL-HUB-INFRA.md). |

---

## n8n product primitives (IO layer, not cognitive core)

| Primitive | Role in ecosystem | AMAS rule |
|-----------|-------------------|-----------|
| **AI Agent node** (LangChain-based) | Visual agent + tools inside n8n | **Automation / IO** only; AMAS **UnifiedIntelligenceOrchestrator** remains source of truth for core operator runs unless a product line explicitly delegates (then **provenance** must show n8n). |
| **Tools Agent** mode | Multi-tool / multi-step in n8n | Same as above; map to **MCP / HTTP tool** boundaries in [TECH-MCP-N8N-SKILL-HUB-INFRA.md](./TECH-MCP-N8N-SKILL-HUB-INFRA.md). |
| **Advanced AI docs index** (n8n docs) | Templates and patterns | Use for **integration design** and operator docs links—not for bypassing **EnhancedAIRouter** in AMAS core paths. |

---

## MCP + skill hubs

| Pattern | Description | AMAS mapping |
|---------|-------------|--------------|
| **`skills_mcp_server` (FastAPI)** | Skills run **outside** n8n in a sandbox; exposed via **MCP**; n8n agents call over MCP/HTTP | **Shared skill layer**: AMAS and n8n can both be **MCP clients** to the same hub; governance (rate limits, egress) stays **server-side**. |
| **n8n MCP community node** | Workflows attach arbitrary MCP servers | Live system / Integrations: **real probe** only—see [BE-10](backend-plans/BE-10-provenance-integrations-health.md). |
| **GitHub / Xebia / tutorial repos** (listed in extra_sources) | Education and comparison | **Reference only**; do not treat as runtime dependencies. |

---

## Planner models and strict JSON (research alignment)

| Item | Idea | AMAS mapping |
|------|------|--------------|
| **Ollama `multiagent-orchestrator`** (library model) | Small model emits **strict JSON** for “next agent/tool” | **Optional** alignment with **grammar-safe JSON** for **GEA** / small planning steps behind **EnhancedAIRouter** + local-only (`AMAS_LOCAL_ONLY`). **Not** a second orchestrator that bypasses [`UnifiedIntelligenceOrchestrator`](../../src/amas/core/unified_intelligence_orchestrator.py). |
| **Local runners** (Ollama, llama.cpp, vLLM) | OpenAI-compatible endpoints, JSON grammars | Already covered by router + workspace skills; research reinforces **contract tests** on JSON shape. |

---

## Framework concepts (non-vendor lock-in)

| Concept | From research | Maps to AMAS |
|---------|----------------|--------------|
| **LangGraph** typed state, checkpoint, replay | Explicit state machine, resume | **RunEvent stream + GET replay** + future `checkpoint_id` in events ([TECH-RUNEVENTS-AND-TRACEABILITY.md](./TECH-RUNEVENTS-AND-TRACEABILITY.md), [BE-01](backend-plans/BE-01-run-events-persistence-replay-ws.md)). |
| **AutoGen** conversation-first | Every turn logged | **Audit + RunEvent** narrative; “Explain my run” consumes same bus ([BE-05](backend-plans/BE-05-explain-task-orchestrator.md)). |
| **CrewAI / Semantic Kernel / MetaGPT** (survey) | Role teams, planners, skills | **SEP**: Service Manager + default/allowed expert pools ([TECH-SEP-AND-SERVICES.md](./TECH-SEP-AND-SERVICES.md)). |

---

## Awesome-agentic-patterns (catalog → UI / API)

Research cites [awesome-agentic-patterns](https://github.com/nibzard/awesome-agentic-patterns) categories (orchestration, memory, tool use, UX, reliability). Map **selected** patterns to AMAS **without** implying every pattern is implemented.

| Pattern (name) | UI affordance (when backed by data) | API / RunEvent need |
|----------------|-------------------------------------|---------------------|
| **Action-Selector** | Mission Console / timeline shows **who acts next** | `plan_updated` or typed “next_step” in events; GEA ranked `recommended_services` |
| **Plan-then-Execute** | **Phase rail** on run view (plan vs execute) | Distinct event types or `phase` field on `plan_updated` / boundaries |
| **Continuous autonomous task loop** | Jobs page: schedules + backlog + retries | [BE-08](backend-plans/BE-08-jobs-scheduler-api.md); honest empty if no API |
| **Episodic memory retrieval** | “Context used” panel (read-only summary) | Future memory API; until then **unavailable** state |
| **Egress lockdown / VM operator** | Sandbox policy banner, tool allowlist hints | `sandbox_*` events + integration flags |
| **Critic / reflection / evaluator** | Optional “review” lane or Explain bullets | Orchestrator-backed explain only; **no** client-only critique |
| **Governance / constitutions** | Tool governance + audit | AgentTool governance + [BE-09](backend-plans/BE-09-audit-api-export-crossrefs.md) |

---

## Memory, vector stores, RAG

| Research idea | AMAS stance |
|-----------------|-------------|
| Shared **Qdrant / pgvector / Milvus Lite** for long-term memory | **Future**: single store optionally shared by n8n + AMAS containers on same network; document in infra TECH doc. |
| **Episodic memory schemas** | Reserve fields in event/replay design; **UI: explicit not wired** until orchestrator exposes retrieval provenance. |
| **Layered RAG** (deep-research surveys) | Specialist SEPs (Research, Intelligence); **RAG in orchestrator**, not fabricated client “sources”. |

---

## Observability and safety (research → product)

| Research theme | AMAS implementation direction |
|----------------|-------------------------------|
| Log **messages, tool calls, API I/O** per agent hop | **RunEvents** + Prometheus counters; no silent zeros ([BE-06](backend-plans/BE-06-production-truth-analytics-auth.md)). |
| **Evaluators / critic agents** | Optional orchestrator paths; **Explain** API grounded in persisted events ([BE-05](backend-plans/BE-05-explain-task-orchestrator.md)). |
| **LangSmith-class** deep tracing | Optional later; do not block Wave 2 on vendor SaaS—**OpenTelemetry** alignment can follow same bus. |

---

## n8n case studies → AMAS UI / API contracts

Condensed from the n8n OSS report + extra_sources case links.

| Case | Pattern | AMAS mapping |
|------|---------|--------------|
| **Self-Hosted AI Starter Kit** | Compose mesh, AI nodes | Infra parity notes: [TECH-MCP-N8N-SKILL-HUB-INFRA.md](./TECH-MCP-N8N-SKILL-HUB-INFRA.md) |
| **Cloudflare / edge starter** | UI hostname ≠ webhook hostname; tunnel | [ENV_AND_INTEGRATION.md](../frontend/ENV_AND_INTEGRATION.md); provenance badges [FE-11](frontend-plans/FE-11-provenance-mcp-n8n.md) |
| **SOC-CERT** | Layered pipeline, dedup hash, retries, structured JSON to dashboard | Mission Console **staged JSON** layouts; Incidents feed [FE-06](frontend-plans/FE-06-incidents-remediation-inline.md) |
| **n8nDash** | Webhook-first widgets; JSON-driven dashboard config | Operator panels call **real** webhooks only; no mock widget data |
| **Agentic-Archive** | n8n workflow JSON as reusable artifact | Internal **workflow library** versioning (docs + repo discipline), not runtime in browser |
| **skills_mcp_server** | Sub-workflow or MCP = skill | SEP **tool_pack** / integration docs; MCP health [BE-10](backend-plans/BE-10-provenance-integrations-health.md) |

**Cross-cutting:** standardize **JSON** at AMAS ↔ n8n boundaries (`schema_version`, `run_id`, `trigger_source`) — phased in [PHASED_MASTER_TODO.md](./PHASED_MASTER_TODO.md) F9 / BE-10.

---

## Adoption roadmap (external) mapped to AMAS phases

The Advanced Technologies doc §8 lists a **generic** adoption order. Rough alignment:

| External roadmap step | AMAS phase / artifact |
|------------------------|------------------------|
| 1. Stabilize local LLM + orchestrator model | R0–R1 + `AMAS_LOCAL_ONLY` / router docs |
| 2. Multi-agent orchestrator (AutoGen/LangGraph style) | **AMAS orchestrator** (existing)—enrich **RunEvents** F3 |
| 3. Externalize skills via MCP | F9 + [TECH-MCP-N8N-SKILL-HUB-INFRA.md](./TECH-MCP-N8N-SKILL-HUB-INFRA.md) |
| 4. Refactor memory / state | Future epic; honest UI until API exists |
| 5. Observability + safety | F6 Explain, F8 audit/CI, Prometheus |

---

## Plan deltas applied to this program (unchanged intent)

1. **GEA / Officer JSON** — evolve `engagement/advise` toward a **versioned** schema (next-step, service-rank, joined plan) compatible with small-planner strict JSON; document beside RunEvent in OpenAPI.
2. **Run graph + timeline** — when orchestrator emits **plan boundaries** or **checkpoint** metadata, render **plan-then-execute** phases.
3. **Integrations & Live system** — sub-tab or topology badge group for **n8n + MCP** health (**honest empty**); copy aligned with [`docs/frontend/ENV_AND_INTEGRATION.md`](../frontend/ENV_AND_INTEGRATION.md).
4. **`SERVICES_CATALOG.md`** — optional designer column: SEP service → pattern tags (`plan_then_execute`, `io_webhook`, …) — **no new runtime** until backend supports.
5. **Explain API** — optional **pattern_tags** on responses **only** when derivable from persisted events (see [PHASED_MASTER_TODO.md](./PHASED_MASTER_TODO.md) F6 note).

---

## Security / TI layout templates

Threat intelligence, monitoring, CVE-style flows: use **SOC-CERT-style** layered pipeline UX (**collection → normalize → enrich → alert**) as a **Mission Console** layout template when APIs return staged JSON.

---

## Where implemented (docs → code)

| Research theme | Execution plan |
|----------------|----------------|
| n8n / MCP / compose / webhooks | [TECH-MCP-N8N-SKILL-HUB-INFRA.md](./TECH-MCP-N8N-SKILL-HUB-INFRA.md), [frontend-plans/FE-11-provenance-mcp-n8n.md](frontend-plans/FE-11-provenance-mcp-n8n.md), [backend-plans/BE-10-provenance-integrations-health.md](backend-plans/BE-10-provenance-integrations-health.md) |
| Strict JSON / checkpoints | [TECH-RUNEVENTS-AND-TRACEABILITY.md](./TECH-RUNEVENTS-AND-TRACEABILITY.md), [backend-plans/BE-01-run-events-persistence-replay-ws.md](backend-plans/BE-01-run-events-persistence-replay-ws.md) |
| Structured incident feeds | [frontend-plans/FE-06-incidents-remediation-inline.md](frontend-plans/FE-06-incidents-remediation-inline.md) |
| Pattern library ↔ phases | [MASTER_NEXT_GENERATION_PLAN.md](./MASTER_NEXT_GENERATION_PLAN.md) § Pattern library |

**CI / contract hooks (2026 sync):** RunEvent normalized fixtures + `scripts/validate_run_event_fixtures.py`; AMAS→n8n envelope schema [`schemas/n8n_webhook_payload.schema.json`](../../schemas/n8n_webhook_payload.schema.json); GEA `checkpoint_ids` only when orchestrator emits real ids (F9-4).

---

*Constitution reminder: research informs **contracts and UX**; production surfaces remain **orchestrator + router + DB** with **radical honesty** when a capability is absent.*
