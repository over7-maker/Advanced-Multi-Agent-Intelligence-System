"""Real DB: topology-hotspots returns summary when Postgres is available."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

pytestmark = pytest.mark.real_db


def _async_dsn(url: str) -> str:
    u = (url or "").strip()
    if u.startswith("postgresql://"):
        return u.replace("postgresql://", "postgresql+asyncpg://", 1)
    if u.startswith("postgres://"):
        return u.replace("postgres://", "postgresql+asyncpg://", 1)
    return u


@pytest.mark.asyncio
async def test_topology_hotspots_has_summary_with_db() -> None:
    url = (os.getenv("DATABASE_URL") or "").strip().lower()
    if "postgres" not in url:
        pytest.skip("PostgreSQL DATABASE_URL required")

    from src.api.routes.system import get_topology_hotspots

    dsn = _async_dsn(os.environ["DATABASE_URL"].strip())
    engine = create_async_engine(dsn, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with factory() as session:
        body = await get_topology_hotspots(db=session)

    await engine.dispose()

    assert body.get("schema_version") == "topology.v2"
    summ = body.get("summary") or {}
    assert "postgres_counts_available" in summ
    if summ.get("postgres_counts_available"):
        counts = summ.get("postgres_task_counts") or {}
        for k in ("active_tasks", "total_tasks", "completed_tasks", "failed_tasks"):
            assert k in counts
