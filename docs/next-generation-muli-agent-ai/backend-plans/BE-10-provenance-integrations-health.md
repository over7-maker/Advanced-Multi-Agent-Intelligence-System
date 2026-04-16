# BE-10 — Provenance fields + integration / MCP / n8n health

**Consumers:** [FE-11](../frontend-plans/FE-11-provenance-mcp-n8n.md).

## Scope

- **Task model:** `trigger_source` (or agreed enum): `amas_core` | `n8n_webhook` | `scheduled_job` | `mcp` | …
- **Health probes:** MCP connector status, n8n base URL reachability — **real HTTP** results only; cache TTL documented.
- **Integration list:** reuse existing integration health patterns under `src/amas/integrations/`.

## Infra and contract alignment (from `project_improvements`)

- **Starter-kit parity:** Document expected internal URLs when AMAS and n8n share a Compose network (optional deployment); probes must not assume `localhost` inside containers ([TECH-MCP-N8N-SKILL-HUB-INFRA.md](../TECH-MCP-N8N-SKILL-HUB-INFRA.md)).
- **MCP probe implementation:** Return structured `{ ok, latency_ms, error_code? }` from server-side HTTP checks only; align with FE-11 chips ([FE-11](../frontend-plans/FE-11-provenance-mcp-n8n.md)).
- **Canonical AMAS → n8n webhook JSON (F9-5):** JSON Schema at [`schemas/n8n_webhook_payload.schema.json`](../../../schemas/n8n_webhook_payload.schema.json) — minimum `schema_version`, `trigger_source`, optional `task_id` / `run_id`, `payload`; static doc [`docs/api/N8N_OUTBOUND_F9-5.md`](../../api/N8N_OUTBOUND_F9-5.md); wire into OpenAPI + integration layer when n8n outbound triggers ship.
- **Security posture:** Reference edge/WAF and separate webhook hostname guidance in [`ENV_AND_INTEGRATION.md`](../../frontend/ENV_AND_INTEGRATION.md); rate-limit public webhook entrypoints.

## Checklist

*Slice sync (2026-04-14): F9 probes + UI shipped per PHASED_MASTER; items below are stretch / honest deferrals.*

- [x] **Shipped:** OpenAPI task create/detail contracts now include `trigger_source` provenance (`TaskCreate` + `TaskResponse`), and API persistence/read paths propagate real values (`amas_core` / `scheduled_job` etc.) from embedded task metadata.
- [x] **Shipped:** Real metrics + dashboard panels for advisory latency / RunEvent ingest (`amas_operator_engagement_advise_latency_seconds`, `amas_run_events_ingested_total`; Grafana `monitoring/grafana/dashboards/task-analytics.json`).
- [x] **Shipped (2026-04-16):** `GET /api/v1/probes` **`probes.v2`** — structured `configured`, `ok`, `latency_ms`, `error_code`; **no default localhost** when `AMAS_N8N_HEALTH_URL` / `AMAS_MCP_HEALTH_URL` unset (honest `not_configured`). Live system chips in [`LiveSystemPage.tsx`](../../../frontend/src/components/command/LiveSystemPage.tsx); tests: `tests/unit/test_operator_probes_v2.py`; OpenAPI + static reference: [`docs/api/OPERATOR_PROBES.md`](../../api/OPERATOR_PROBES.md).

## References

- [`docs/api/OPERATOR_PROBES.md`](../../api/OPERATOR_PROBES.md) — probes.v2 static contract (mirrors `/openapi.json`)
- [RESEARCH-SYNTHESIS-PROJECT-IMPROVEMENTS.md](../RESEARCH-SYNTHESIS-PROJECT-IMPROVEMENTS.md)  
- [TECH-MCP-N8N-SKILL-HUB-INFRA.md](../TECH-MCP-N8N-SKILL-HUB-INFRA.md)
