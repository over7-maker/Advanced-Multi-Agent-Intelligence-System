# n8n outbound webhook envelope (F9-5)

**Status:** Schema and docs only until outbound n8n triggers are implemented in the integration layer (see [BE-10](../next-generation-muli-agent-ai/backend-plans/BE-10-provenance-integrations-health.md)).

## JSON Schema

Canonical file (versioned contract):

- [`schemas/n8n_webhook_payload.schema.json`](../../schemas/n8n_webhook_payload.schema.json)

Minimum required properties: `schema_version`, `trigger_source`. Optional: `task_id`, `run_id`, `event_type`, `timestamp`, `payload`.

## OpenAPI

When outbound POST/webhook delivery ships, register the payload as a reusable schema in FastAPI/OpenAPI and reference it from the outbound trigger endpoint. Until then, **`/openapi.json` documents `GET /api/v1/probes`** (probes.v2); F9-5 remains schema + static doc only.

## Related

- [OPERATOR_PROBES.md](OPERATOR_PROBES.md) — live n8n/MCP **health probes** (different concern than outbound JSON body).
