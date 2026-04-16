# BE-09 — Audit API: filters, export, run/node cross-refs

**Consumers:** [FE-10](../frontend-plans/FE-10-audit-a11y-testing.md).

## Scope

- Evolve `/security/events` (or unified audit route) toward:
  - filterable grid backend (query params),
  - CSV/stream export,
  - optional `run_id`, `node_id`, time-range filters.
- **Never fabricate** audit rows.

## Checklist

*Slice sync (2026-04-16): UI export + filters shipped per F8 / FE-10; backend index/redaction remain incremental hardening.*

- [ ] Index strategy for time + tenant + run_id (scale-out / large tenants).
- [ ] Redaction policy for sensitive payloads in list views.
