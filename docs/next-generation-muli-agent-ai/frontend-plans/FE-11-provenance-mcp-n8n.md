# FE-11 — Run provenance, MCP + n8n health surfaces

**Depends on:** [BE-10](../backend-plans/BE-10-provenance-integrations-health.md).

## Scope

- **Badges:** AMAS core vs n8n webhook vs scheduled job — only when `trigger_source` (or agreed field) exists.
- **Filters:** runs/tasks by provenance.
- **Live system / Integrations:** MCP connector + n8n reachability chips from **real** health/probe endpoints; disconnected = honest disconnected.

## Infra and contract alignment (from `project_improvements`)

- **Starter-kit parity:** When documenting operator setup, align env copy with official **n8n Self-Hosted AI Starter Kit** patterns (Compose network, predictable internal service names)—UI only claims “stack segment” health when probes exist ([TECH-MCP-N8N-SKILL-HUB-INFRA.md](../TECH-MCP-N8N-SKILL-HUB-INFRA.md)).
- **MCP probes:** Surface MCP status only from **successful** probe responses (or explicit 503 from API)—no green chips on missing config.
- **n8n webhook contract:** Reserve UI space for **versioned JSON** handoff (`schema_version`, `run_id` / `task_id`, `trigger_source`); until BE lands, show skeleton + doc link ([BE-10](../backend-plans/BE-10-provenance-integrations-health.md), [`docs/api/N8N_OUTBOUND_F9-5.md`](../../api/N8N_OUTBOUND_F9-5.md), [PHASED_MASTER_TODO](../PHASED_MASTER_TODO.md) F9-5).
- **UI vs webhook hostname:** Operator docs must distinguish editor URL vs automation endpoint (edge/tunnel pattern)—see [`ENV_AND_INTEGRATION.md`](../../frontend/ENV_AND_INTEGRATION.md) § n8n.

## Checklist

- [x] Probe / env copy: `AMAS_N8N_HEALTH_URL` / `AMAS_MCP_HEALTH_URL` documented in [`.env.example`](../../../.env.example); operator probes **v2** — no green success when unset ([`ENV_AND_INTEGRATION.md`](../../frontend/ENV_AND_INTEGRATION.md) cross-link n8n/MCP sections as needed); contract [`docs/api/OPERATOR_PROBES.md`](../../api/OPERATOR_PROBES.md).
- [ ] GEA `schema_version` display (optional) for support/debug — no fake versioning — still optional polish.

## References

- [RESEARCH-SYNTHESIS-PROJECT-IMPROVEMENTS.md](../RESEARCH-SYNTHESIS-PROJECT-IMPROVEMENTS.md)  
- [TECH-MCP-N8N-SKILL-HUB-INFRA.md](../TECH-MCP-N8N-SKILL-HUB-INFRA.md)
