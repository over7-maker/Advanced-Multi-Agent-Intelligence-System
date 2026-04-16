# Operator probes — `GET /api/v1/probes` (**probes.v2**)

Static reference for the operator integration health surface (BE-10 / FE-11). **Authoritative runtime contract** is also exposed in OpenAPI/Swagger (`/docs`, `/openapi.json`) via Pydantic `response_model` on the route.

## Request

- **Method:** `GET`
- **Path:** `/api/v1/probes`
- **Auth:** Same as other `/api/v1/*` routes (API key when `AMAS_REQUIRE_AUTH` applies).

## Response envelope

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Always `probes.v2` |
| `checks` | array | One entry per target (`n8n`, `mcp`) in fixed order |

## Check object (`checks[]`)

| Field | Type | Description |
|-------|------|-------------|
| `target` | string | `n8n` or `mcp` |
| `url` | string | Configured health URL, or empty when not configured |
| `configured` | boolean | Whether `AMAS_N8N_HEALTH_URL` / `AMAS_MCP_HEALTH_URL` was set to a non-empty URL |
| `ok` | boolean \| null | `null` when `configured` is false; otherwise HTTP success (2xx) |
| `latency_ms` | number \| null | Round-trip latency when a request was made |
| `error_code` | string \| null | e.g. `http_503`, `timeout`, `connect_error`, `probe_error` |
| `detail` | string | Human-readable detail or setup hint |
| `status` | string | `not_configured` \| `healthy` \| `degraded` \| `unavailable` (legacy-compatible) |

When env URLs are unset, the API returns **`not_configured`** and does **not** call `localhost` placeholders.

## Environment

- `AMAS_N8N_HEALTH_URL` — optional n8n health endpoint
- `AMAS_MCP_HEALTH_URL` — optional MCP HTTP bridge health endpoint

See [`.env.example`](../../.env.example) and [`docs/frontend/ENV_AND_INTEGRATION.md`](../frontend/ENV_AND_INTEGRATION.md).

## Code

- Route: `src/api/routes/operator.py` — `OperatorProbesResponseV2`, `OperatorProbeCheckV2`
- Tests: `tests/unit/test_operator_probes_v2.py`
