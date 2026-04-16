"""Unit tests for sandbox telemetry helpers and RunEvent aggregation (FE-09 / F7-1)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.api.routes.operator import (
    _is_sandbox_or_tool_event,
    _sandbox_event_summary,
    get_task_sandbox_telemetry,
)


def test_is_sandbox_or_tool_event() -> None:
    assert _is_sandbox_or_tool_event("sandbox_spawned") is True
    assert _is_sandbox_or_tool_event("tool_call_started") is True
    assert _is_sandbox_or_tool_event("agent_started") is False


def test_sandbox_event_summary_prefers_payload() -> None:
    assert (
        _sandbox_event_summary(
            {"event_type": "x", "payload": {"tool_name": "pytest"}}
        )
        == "pytest"
    )
    assert _is_sandbox_or_tool_event("tool_call_finished") is True


@pytest.mark.asyncio
async def test_get_task_sandbox_telemetry_v2_shape() -> None:
    fake_events = [
        {
            "event_type": "sandbox_spawned",
            "timestamp": "2020-01-01T00:00:01+00:00",
            "payload": {"sandbox_id": "sb-1"},
        },
        {
            "event_type": "tool_call_started",
            "timestamp": "2020-01-01T00:00:02+00:00",
            "payload": {"tool_name": "bash"},
        },
        {
            "event_type": "agent_started",
            "timestamp": "2020-01-01T00:00:00+00:00",
            "payload": {},
        },
    ]
    with patch(
        "src.amas.services.run_event_buffer.list_run_events_merged",
        new_callable=AsyncMock,
        return_value=fake_events,
    ):
        body = await get_task_sandbox_telemetry("task-a", db=None)

    assert body["schema_version"] == "sandbox_telemetry.v2"
    assert body["task_id"] == "task-a"
    assert body["sandbox_event_count"] == 1
    assert body["tool_event_count"] == 1
    assert body["available"] is True
    assert "sandbox_spawned" in body["event_type_counts"]
    assert "tool_call_started" in body["event_type_counts"]
    assert len(body["recent_sandbox_tool_events"]) == 2
    assert body["first_event_iso"] == "2020-01-01T00:00:01+00:00"
    assert body["last_event_iso"] == "2020-01-01T00:00:02+00:00"
