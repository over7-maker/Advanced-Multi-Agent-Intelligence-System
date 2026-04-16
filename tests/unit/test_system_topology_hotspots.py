"""Unit tests for topology-hotspots response shape (FE-09 / F7-2)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_topology_hotspots_v2_includes_summary() -> None:
    mock_db = MagicMock()
    # Keep all patches active for the API call (nested `with` must wrap `await get_topology_hotspots`).
    with patch(
        "src.amas.core.unified_intelligence_orchestrator.get_unified_orchestrator",
    ) as go:
        go.return_value.get_internal_queue_depth.return_value = 1
        with patch(
            "src.api.routes.system._task_counts_from_db",
            new_callable=AsyncMock,
            return_value={
                "active_tasks": 2,
                "total_tasks": 10,
                "completed_tasks": 7,
                "failed_tasks": 1,
            },
        ):
            with patch(
                "src.api.routes.system._recent_failed_task_hotspots",
                new_callable=AsyncMock,
                return_value=[],
            ):
                from src.api.routes.system import get_topology_hotspots

                body = await get_topology_hotspots(db=mock_db)

    assert body["schema_version"] == "topology.v2"
    assert "summary" in body
    assert body["summary"]["orchestrator_queue_depth"] == 1
    assert body["summary"]["postgres_counts_available"] is True
    assert body["summary"]["postgres_task_counts"]["failed_tasks"] == 1
    assert isinstance(body["hotspots"], list)


@pytest.mark.asyncio
async def test_topology_hotspots_summary_without_postgres_counts() -> None:
    with patch(
        "src.amas.core.unified_intelligence_orchestrator.get_unified_orchestrator",
    ) as go:
        go.return_value.get_internal_queue_depth.return_value = 0
        with patch(
            "src.api.routes.system._task_counts_from_db",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with patch(
                "src.api.routes.system._recent_failed_task_hotspots",
                new_callable=AsyncMock,
                return_value=[],
            ):
                from src.api.routes.system import get_topology_hotspots

                body = await get_topology_hotspots(db=None)

    assert body["summary"]["postgres_counts_available"] is False
    assert body["summary"]["postgres_task_counts"] is None
