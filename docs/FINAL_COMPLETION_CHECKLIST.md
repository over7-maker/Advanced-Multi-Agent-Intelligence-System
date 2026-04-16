# Final Completion Checklist (Exact Remaining Scope)

## North star (post-CAP roadmap)

| Scope | Meaning |
|-------|---------|
| **A — Operator / next-gen pack** | Shippable command center + constitution-compliant surfaces; phased **F1–F9** slices per [`next-generation-muli-agent-ai/`](next-generation-muli-agent-ai/README.md). |
| **B — Repository / GAP** | Burn down **Partial / Scaffold** in [`CAPABILITY_MATRIX.md`](CAPABILITY_MATRIX.md) and R0 service audit items — ongoing hardening, not a single sprint. |

Post-CAP engineering uses **scope B** as backlog while keeping **scope A** release-ready. Evidence: [`IMPLEMENTATION-STATUS-A-THROUGH-C.md`](next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md).

---

This file tracked **CAP-01..CAP-06** closure for the next-generation operator program. **As of 2026-04-15**, all CAP items are **done** in tree (see evidence in [`next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md`](next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md)).

Use with:
- [`CAPABILITY_MATRIX.md`](CAPABILITY_MATRIX.md)
- [`next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md`](next-generation-muli-agent-ai/IMPLEMENTATION-STATUS-A-THROUGH-C.md)
- [`deployment/PRODUCTION_READINESS_CHECKLIST.md`](deployment/PRODUCTION_READINESS_CHECKLIST.md)

---

## Completion Rules

- A line is complete only when code + tests + docs all land in the same PR.
- No placeholder/mock behavior for production-claimed capabilities.
- Every completed item must update status rows in both capability and implementation docs.

---

## CAP components (closed)

| ID | Component | Definition of done (met) |
|----|-----------|-------------------------|
| CAP-01 | Operator UI parity (sandbox/topology/jobs depth) | `sandbox_telemetry.v2`, `topology.v2` summary, Jobs sandbox lineage + tests |
| CAP-02 | Service audit completion | [`SERVICE_DATA_AUDIT.md`](SERVICE_DATA_AUDIT.md) § CAP-02 evidence index |
| CAP-03 | Integration confidence | Export contract integration test + `tests/real_db/test_topology_hotspots_summary.py` |
| CAP-04 | Frontend production confidence | `e2e:interactive` + `e2e:a11y` in [`.github/workflows/integration-tests.yml`](../.github/workflows/integration-tests.yml) |
| CAP-05 | Production gate execution | [`.github/workflows/release-candidate-gate.yml`](../.github/workflows/release-candidate-gate.yml) |
| CAP-06 | Docs lockstep closure | `IMPLEMENTATION-STATUS`, `CAPABILITY_MATRIX`, this file updated together |

---

## Ongoing release discipline

1. Run [`deployment/PRODUCTION_READINESS_CHECKLIST.md`](deployment/PRODUCTION_READINESS_CHECKLIST.md) on the release candidate commit.
2. Optionally run `workflow_dispatch` on **Release candidate gate** after large changes.
3. Keep [`CAPABILITY_MATRIX.md`](CAPABILITY_MATRIX.md) honest when new routes or services ship.
4. Watch CI lanes on `main` / PRs and investigate failures before tagging a release:
   - **Unit:** [`.github/workflows/unit-tests.yml`](.github/workflows/unit-tests.yml)
   - **Mocked integration + frontend E2E/a11y:** [`.github/workflows/integration-tests.yml`](.github/workflows/integration-tests.yml)
   - **Optional real DB:** [`.github/workflows/integration-real-db.yml`](.github/workflows/integration-real-db.yml) (Postgres + Alembic + `tests/real_db`)

---

## Final Go/No-Go Criteria

Project remains **release-ready** when:
- Automated checks in `PRODUCTION_READINESS_CHECKLIST` pass on the ship commit.
- `CAPABILITY_MATRIX` has no undocumented **Partial** regressions on the production path you are shipping.
