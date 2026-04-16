"""Operator GET /probes — probes.v2 structured checks (BE-10 / FE-11)."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest

from src.api.routes.operator import _health_url_for_probe, get_operator_probes


def test_health_url_empty_means_unset() -> None:
    with patch.dict(os.environ, {"AMAS_N8N_HEALTH_URL": ""}, clear=False):
        assert _health_url_for_probe("n8n") is None
    with patch.dict(os.environ, {"AMAS_MCP_HEALTH_URL": "skip"}, clear=False):
        assert _health_url_for_probe("mcp") is None


@pytest.mark.asyncio
async def test_probes_v2_not_configured_without_env() -> None:
    with patch.dict(os.environ, {"AMAS_N8N_HEALTH_URL": "", "AMAS_MCP_HEALTH_URL": ""}, clear=False):
        body = (await get_operator_probes()).model_dump()
    assert body["schema_version"] == "probes.v2"
    assert len(body["checks"]) == 2
    for c in body["checks"]:
        assert c["configured"] is False
        assert c["status"] == "not_configured"
        assert c["ok"] is None


@pytest.mark.asyncio
async def test_probes_v2_success_path() -> None:
    with patch.dict(
        os.environ,
        {
            "AMAS_N8N_HEALTH_URL": "http://example.test/healthz",
            "AMAS_MCP_HEALTH_URL": "",
        },
        clear=False,
    ):
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        with patch("src.api.routes.operator.httpx.AsyncClient") as client_cls:
            inst = AsyncMock()
            inst.__aenter__.return_value = inst
            inst.__aexit__.return_value = None
            inst.get = AsyncMock(return_value=mock_resp)
            client_cls.return_value = inst
            body = (await get_operator_probes()).model_dump()

    assert body["schema_version"] == "probes.v2"
    n8n = next(x for x in body["checks"] if x["target"] == "n8n")
    assert n8n["configured"] is True
    assert n8n["ok"] is True
    assert n8n["latency_ms"] is not None
    mcp = next(x for x in body["checks"] if x["target"] == "mcp")
    assert mcp["configured"] is False
