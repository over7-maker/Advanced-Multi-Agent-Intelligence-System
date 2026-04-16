# Integration tests (mocked stack)

- **`test_tasks_integrated_integration.py`** — mocked DB/orchestrator; run in [`.github/workflows/integration-tests.yml`](../../.github/workflows/integration-tests.yml).

# Real Postgres lane (Job B)

- Mark tests with **`@pytest.mark.real_db`** under [`tests/real_db/`](../real_db/).
- CI: [`.github/workflows/integration-real-db.yml`](../../.github/workflows/integration-real-db.yml) (Postgres service + Alembic + `pytest tests/real_db -m real_db`).

No full docker-compose stack in default PR CI — see [`docs/next-generation-muli-agent-ai/REAL_DATA_AND_CI_STRATEGY.md`](../../docs/next-generation-muli-agent-ai/REAL_DATA_AND_CI_STRATEGY.md).
