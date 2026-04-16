# FE-09 — Sandbox, topology hotspots, Jobs UI

**Depends on:** real APIs only — [BE-08](../backend-plans/BE-08-jobs-scheduler-api.md); sandbox/telemetry routes as implemented; metrics for topology overlays.

## Scope

- **Global sandbox page** (when backend ready): tiles, resources, lifecycle — telemetry honest empty.
- **Topology:** backlog/timeout/failed-run **heat** when metrics exist; no random demo heatmaps.
- **Jobs:** definitions, schedule, history — reuse run graph + timeline components.

## Checklist

- [x] Feature-flag or “not configured” per constitution when API missing (empty RunEvents / unavailable DB counts surfaced honestly).
- [x] Link to ENV docs for enabling integrations/metrics (`docs/frontend/ENV_AND_INTEGRATION.md`).
- [x] Depth: `sandbox_telemetry.v2` (recent RunEvent rows + type counts), `topology.v2` (`summary` drill-down), Jobs execution → task → `/sandbox?taskId=`.
