"""
Operator program API: SEP registry (service-definitions) and Global Engagement Advisor (GEA).

Uses UnifiedIntelligenceOrchestrator (agent selection), Intelligence Manager (ML optimization),
and EnhancedAIRouter (advisory generation) — no browser-side LLM.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.amas.agents.task_type_helpers import recommend_task_types
from src.amas.ai.enhanced_router_class import EnhancedAIRouter
from src.amas.core.unified_intelligence_orchestrator import get_unified_orchestrator
from src.amas.prompts.compose import build_task_creation_assistant_prompt
from src.amas.services.sep_registry import list_service_definitions, service_catalog_text_for_prompt
from src.amas.services.prometheus_metrics_service import get_metrics_service
from src.api.routes import tasks_integrated as tasks_integrated_routes

logger = logging.getLogger(__name__)


async def _optional_db_session():
    """Same pattern as `system._optional_db_session` — avoids importing tasks_integrated from operator."""
    try:
        from src.database.connection import get_session, is_connected

        if await is_connected():
            async for session in get_session():
                yield session
                return
        yield None
    except Exception as e:
        logger.debug("optional DB for operator routes: %s", e)
        yield None

router = APIRouter(tags=["operator"])

_SCHEMA_VERSION = "gea.v1"

_PATTERN_TAG_ORDER = (
    "plan_then_execute",
    "tool_chain",
    "sandbox_isolation",
    "multi_agent_handoff",
)


def _pattern_tags_from_events(events: List[Dict[str, Any]]) -> List[str]:
    """F6-4: tags derived only from persisted/buffer RunEvents — never invented."""
    tags: List[str] = []
    ets = [str(e.get("event_type") or e.get("event") or "").lower() for e in events]
    if any("plan_updated" in x or x.startswith("plan_") for x in ets):
        tags.append("plan_then_execute")
    if any("tool_call" in x for x in ets):
        tags.append("tool_chain")
    if any(x.startswith("sandbox_") for x in ets):
        tags.append("sandbox_isolation")
    agentish = sum(1 for x in ets if "agent_" in x or x in ("team_changed",))
    if agentish >= 2:
        tags.append("multi_agent_handoff")
    return [t for t in _PATTERN_TAG_ORDER if t in tags]


def _health_url_for_probe(kind: str) -> Optional[str]:
    """BE-10 / FE-11: no default localhost — unset env means not_configured (honest UI)."""
    key = "AMAS_N8N_HEALTH_URL" if kind == "n8n" else "AMAS_MCP_HEALTH_URL"
    raw = (os.getenv(key) or "").strip()
    if not raw or raw.lower() in ("0", "false", "off", "skip", "none"):
        return None
    return raw


class OperatorProbeCheckV2(BaseModel):
    """One row in `GET /api/v1/probes` — **probes.v2** (BE-10 / FE-11)."""

    target: str = Field(..., description="Probe target: n8n | mcp")
    url: str = Field("", description="Configured health URL, or empty when not configured")
    configured: bool
    ok: Optional[bool] = Field(None, description="null when not_configured")
    latency_ms: Optional[float] = None
    error_code: Optional[str] = Field(None, description="e.g. http_503, timeout, connect_error")
    detail: str = ""
    status: str = Field(
        ...,
        description="not_configured | healthy | degraded | unavailable",
    )


class OperatorProbesResponseV2(BaseModel):
    """Response envelope for `GET /api/v1/probes` — **probes.v2**."""

    schema_version: Literal["probes.v2"] = "probes.v2"
    checks: List[OperatorProbeCheckV2]


@router.get("/probes", response_model=OperatorProbesResponseV2)
async def get_operator_probes() -> OperatorProbesResponseV2:
    """
    Real probe status for operator-adjacent dependencies (n8n / MCP bridge).

    **probes.v2:** each check includes `configured`, `ok`, `latency_ms`, optional `error_code`.
    When `AMAS_*_HEALTH_URL` is unset, the check is **not_configured** (no HTTP call — avoids fake localhost failures).
    """
    import time as time_module

    checks: List[OperatorProbeCheckV2] = []
    targets = [("n8n", _health_url_for_probe("n8n")), ("mcp", _health_url_for_probe("mcp"))]
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, url in targets:
            if not url:
                checks.append(
                    OperatorProbeCheckV2(
                        target=name,
                        url="",
                        configured=False,
                        ok=None,
                        latency_ms=None,
                        error_code=None,
                        detail="Set AMAS_N8N_HEALTH_URL or AMAS_MCP_HEALTH_URL (see .env.example).",
                        status="not_configured",
                    )
                )
                continue
            t0 = time_module.perf_counter()
            ok = False
            error_code: Optional[str] = None
            detail = ""
            legacy_status = "unavailable"
            try:
                res = await client.get(url)
                elapsed_ms = (time_module.perf_counter() - t0) * 1000.0
                ok = 200 <= res.status_code < 300
                if not ok:
                    error_code = f"http_{res.status_code}"
                detail = f"http {res.status_code}"
                legacy_status = "healthy" if ok else "degraded"
            except Exception as e:
                elapsed_ms = (time_module.perf_counter() - t0) * 1000.0
                detail = str(e)
                err_l = detail.lower()
                if "timeout" in err_l or "timed out" in err_l:
                    error_code = "timeout"
                elif "connect" in err_l or "connection" in err_l:
                    error_code = "connect_error"
                else:
                    error_code = "probe_error"
                legacy_status = "unavailable"
            checks.append(
                OperatorProbeCheckV2(
                    target=name,
                    url=url,
                    configured=True,
                    ok=ok,
                    latency_ms=round(elapsed_ms, 2),
                    error_code=error_code,
                    detail=detail,
                    status=legacy_status,
                )
            )
    return OperatorProbesResponseV2(schema_version="probes.v2", checks=checks)


class EngagementAdviseRequest(BaseModel):
    raw_goal: str = Field(..., min_length=3, max_length=32000)
    source: Optional[str] = Field(
        None,
        description="Analytics only: engage_page | create_task | mission_console | workflow_builder | palette",
    )
    context: Optional[Dict[str, Any]] = None


class RecommendedService(BaseModel):
    service_id: str
    score: float = 0.0
    rationale: str = ""


class JoinedEngagement(BaseModel):
    mode: str = "sequential"
    steps: List[Dict[str, Any]] = Field(default_factory=list)


class EngagementAdviseResponse(BaseModel):
    schema_version: str = _SCHEMA_VERSION
    improved_brief: str = ""
    recommended_services: List[RecommendedService] = Field(default_factory=list)
    joined_engagement: Optional[JoinedEngagement] = None
    suggested_task_template_patch: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    officer_checklist: List[str] = Field(default_factory=list)
    orchestrator_agents_hint: List[str] = Field(
        default_factory=list,
        description="Agents selected by orchestrator path for top inferred task type.",
    )
    checkpoint_ids: List[str] = Field(
        default_factory=list,
        description="F9-4: only real orchestrator checkpoint ids; empty until backend emits them.",
    )


class JoinedEngagementCreateRequest(BaseModel):
    """Persist a joined engagement by creating multiple real tasks."""

    improved_brief: str = Field(..., min_length=3, max_length=32000)
    joined_engagement: JoinedEngagement
    source: Optional[str] = Field(
        None,
        description="Analytics only: engage_page | create_task | mission_console | workflow_builder | palette",
    )
    context: Optional[Dict[str, Any]] = None
    priority: int = Field(5, ge=1, le=10)


class JoinedEngagementCreatedTask(BaseModel):
    task_id: str
    title: str
    service_id: str
    depends_on_task_ids: List[str] = Field(default_factory=list)
    status: str = "pending"


class JoinedEngagementCreateResponse(BaseModel):
    schema_version: str = "gea.joined.v1"
    joined_id: str
    mode: str
    created_tasks: List[JoinedEngagementCreatedTask] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


def _service_to_task_type(service_id: str) -> str:
    sid = (service_id or "").strip().lower()
    mapping = {
        "security_scan": "security_scan",
        "code_analysis": "code_analysis",
        "intelligence_gathering": "intelligence_gathering",
        "performance_analysis": "performance_analysis",
        "documentation": "documentation",
        "testing": "testing",
        "deployment": "deployment",
        "monitoring": "monitoring",
        "data_analysis": "data_analysis",
    }
    return mapping.get(sid, "code_analysis")


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not text or not text.strip():
        return None
    s = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", s, re.IGNORECASE)
    if fence:
        s = fence.group(1).strip()
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    start = s.find("{")
    end = s.rfind("}")
    if start >= 0 and end > start:
        try:
            obj = json.loads(s[start : end + 1])
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _heuristic_services_from_task_types(
    ranked_types: List[Dict[str, Any]],
) -> List[RecommendedService]:
    valid_ids = {s["service_id"] for s in list_service_definitions()}
    out: List[RecommendedService] = []
    mapping = {
        "security_scan": "security_scan",
        "security_audit": "security_scan",
        "code_analysis": "code_analysis",
        "intelligence_gathering": "intelligence_gathering",
        "performance_analysis": "performance_analysis",
        "documentation": "documentation",
        "testing": "testing",
        "deployment": "deployment",
        "monitoring": "monitoring",
        "data_analysis": "data_analysis",
    }
    seen: set[str] = set()
    for item in ranked_types[:5]:
        tt = str(item.get("task_type") or "").strip()
        sid = mapping.get(tt, tt if tt in valid_ids else "")
        if not sid or sid in seen:
            continue
        seen.add(sid)
        conf = float(item.get("confidence") or 0.5)
        out.append(
            RecommendedService(
                service_id=sid,
                score=min(0.99, max(0.1, conf)),
                rationale=str(item.get("reason") or "Inferred from task-type fit."),
            )
        )
    return out[:5]


async def _log_gea_audit(
    *,
    user_hint: str,
    source: Optional[str],
    response_summary: Dict[str, Any],
) -> None:
    try:
        from src.amas.security.audit.audit_logger import (
            AuditEvent,
            AuditEventType,
            AuditStatus,
            get_audit_logger,
        )

        al = get_audit_logger()
        if not al:
            return
        now = datetime.now(timezone.utc).isoformat()
        ev = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=now,
            event_type=AuditEventType.SYSTEM_EVENT,
            status=AuditStatus.SUCCESS,
            action="engagement_advise",
            details={
                "source": source or "unknown",
                "summary": response_summary,
                "raw_goal_prefix": (user_hint[:200] + "…") if len(user_hint) > 200 else user_hint,
            },
        )
        await al.log_event(ev)
    except Exception as e:
        logger.debug("GEA audit log skipped: %s", e)


@router.get("/service-definitions")
async def get_service_definitions() -> Dict[str, Any]:
    """SEP registry for Mission Console and GEA (BE-03 v0)."""
    return {
        "schema_version": "sep.v1",
        "services": list_service_definitions(),
    }


@router.get("/service-definitions/agents/{agent_id}/services")
async def get_agent_service_reverse_index(agent_id: str) -> Dict[str, Any]:
    """
    Reverse index from agent id to SEP services where the agent appears as manager
    or in expert pools.
    """
    aid = (agent_id or "").strip()
    if not aid:
        raise HTTPException(status_code=400, detail="agent_id is required")
    matches: List[Dict[str, Any]] = []
    for svc in list_service_definitions():
        manager = str(svc.get("service_manager") or "")
        default_pool = [str(x) for x in (svc.get("default_expert_pool") or [])]
        allowed_pool = [str(x) for x in (svc.get("allowed_expert_pool") or [])]
        roles: List[str] = []
        if manager == aid:
            roles.append("manager")
        if aid in default_pool:
            roles.append("default_expert")
        if aid in allowed_pool:
            roles.append("allowed_expert")
        if roles:
            matches.append(
                {
                    "service_id": svc.get("service_id"),
                    "title": svc.get("title"),
                    "roles": roles,
                }
            )
    return {
        "schema_version": "sep.v1",
        "agent_id": aid,
        "services": matches,
    }


@router.post("/engagement/advise", response_model=EngagementAdviseResponse)
async def post_engagement_advise(body: EngagementAdviseRequest) -> EngagementAdviseResponse:
    """
    Global Engagement Advisor — orchestrator + intelligence + EnhancedAIRouter.
    """
    raw = (body.raw_goal or "").strip()
    advise_started = time.time()
    ctx = body.context or {}
    target = str(ctx.get("target") or ctx.get("repo") or "operator-goal").strip() or "operator-goal"

    ranked = recommend_task_types(
        None,
        title="",
        description=raw,
        target=target,
        parameters={},
        top_k=5,
    )
    best_type = ranked[0]["task_type"] if ranked else "code_analysis"

    orch_agents: List[str] = []
    try:
        orchestrator = get_unified_orchestrator()
        if orchestrator and hasattr(orchestrator, "select_agents"):
            orch_agents = await orchestrator.select_agents(
                best_type,
                target,
                ctx if isinstance(ctx, dict) else {},
            )
    except Exception as e:
        logger.warning("GEA orchestrator select_agents failed: %s", e)

    heuristic_services = _heuristic_services_from_task_types(ranked)
    warnings: List[str] = []
    if not orch_agents:
        warnings.append("Orchestrator returned no idle agents; execution may queue.")

    user_prompt = (
        "Operator goal (verbatim):\n"
        f"{raw}\n\n"
        "Inferred canonical task types (best first):\n"
        f"{json.dumps(ranked, indent=0)}\n\n"
        "Available SEP services:\n"
        f"{service_catalog_text_for_prompt()}\n\n"
        "Orchestrator-preferred agents for the top type:\n"
        f"{json.dumps(orch_agents)}\n\n"
        'Reply with a single JSON object only, keys: '
        '"improved_brief" (string), '
        '"recommended_services" (array of {service_id, score, rationale}), '
        '"joined_engagement" (optional {mode: sequential|parallel, steps: [{service_id, depends_on?}]}), '
        '"officer_checklist" (optional string array of short imperatives), '
        '"warnings" (optional string array). '
        "Scores are 0-1. Align recommended_services with the SEP list."
    )

    system = (
        build_task_creation_assistant_prompt()
        + "\n\nYou are the Global Engagement Advisor. Output valid JSON only, no markdown."
    )

    parsed: Dict[str, Any] = {}
    try:
        ai_router = EnhancedAIRouter()
        ai_resp = await ai_router.generate_with_fallback(
            prompt=user_prompt,
            system_prompt=system,
            max_tokens=2048,
            temperature=0.35,
            strategy="quality_first",
        )
        parsed = _extract_json_object(ai_resp.content) or {}
    except Exception as e:
        logger.warning("GEA router generation failed: %s", e)
        warnings.append("Advisory model unavailable; using heuristic fit only.")

    improved = str(parsed.get("improved_brief") or "").strip()
    if not improved:
        improved = raw if len(raw) < 2000 else raw[:1997] + "…"

    rec_svcs: List[RecommendedService] = []
    if isinstance(parsed.get("recommended_services"), list):
        for item in parsed["recommended_services"][:8]:
            if not isinstance(item, dict):
                continue
            sid = str(item.get("service_id") or "").strip()
            if not sid:
                continue
            rec_svcs.append(
                RecommendedService(
                    service_id=sid,
                    score=float(item.get("score") or 0.5),
                    rationale=str(item.get("rationale") or ""),
                )
            )
    if not rec_svcs:
        rec_svcs = heuristic_services

    joined: Optional[JoinedEngagement] = None
    je = parsed.get("joined_engagement")
    if isinstance(je, dict):
        mode = str(je.get("mode") or "sequential")
        steps = je.get("steps") if isinstance(je.get("steps"), list) else []
        joined = JoinedEngagement(mode=mode, steps=[s for s in steps if isinstance(s, dict)][:12])

    oc = parsed.get("officer_checklist")
    checklist: List[str] = []
    if isinstance(oc, list):
        checklist = [str(x) for x in oc[:12] if str(x).strip()]
    if not checklist:
        checklist = [
            "Confirm scope and target systems.",
            "Pick a primary service from ranked chips.",
            "Open Mission Console or create a task when ready.",
        ]

    w2 = parsed.get("warnings")
    if isinstance(w2, list):
        warnings.extend(str(x) for x in w2[:8] if str(x).strip())

    patch: Dict[str, Any] = {}
    if best_type:
        patch["task_type"] = best_type
    if target and target != "operator-goal":
        patch["target"] = target

    resp = EngagementAdviseResponse(
        improved_brief=improved,
        recommended_services=rec_svcs,
        joined_engagement=joined,
        suggested_task_template_patch=patch,
        warnings=warnings[:12],
        officer_checklist=checklist,
        orchestrator_agents_hint=orch_agents[:12],
    )

    await _log_gea_audit(
        user_hint=raw,
        source=body.source,
        response_summary={
            "top_task_type": best_type,
            "service_ids": [s.service_id for s in rec_svcs[:5]],
            "orchestrator_agents": orch_agents[:5],
        },
    )
    try:
        ms = get_metrics_service()
        if ms is not None:
            ms.record_engagement_advise(
                source=body.source or "unknown",
                status="success",
                duration=time.time() - advise_started,
            )
    except Exception:
        logger.debug("Failed to record engagement advise metric", exc_info=True)
    return resp


@router.post("/engagement/create-joined", response_model=JoinedEngagementCreateResponse)
async def post_engagement_create_joined(
    body: JoinedEngagementCreateRequest,
    background_tasks: BackgroundTasks,
    db: Optional[AsyncSession] = Depends(_optional_db_session),
    redis=Depends(tasks_integrated_routes.get_redis),
    current_user=Depends(
        tasks_integrated_routes.get_current_user_optional
        if tasks_integrated_routes.AUTH_AVAILABLE
        else tasks_integrated_routes.get_current_user
    ),
) -> JoinedEngagementCreateResponse:
    """
    Durable joined engagement creation (GEA / BE-02):
    creates one real task per step through the integrated task pipeline.
    """
    joined_id = f"joined_{uuid.uuid4().hex[:12]}"
    steps = body.joined_engagement.steps if body.joined_engagement and body.joined_engagement.steps else []
    if not steps:
        raise HTTPException(status_code=400, detail="joined_engagement.steps must contain at least one item")

    improved = (body.improved_brief or "").strip()
    target = str((body.context or {}).get("target") or "operator-goal").strip() or "operator-goal"
    warnings: List[str] = []
    created: List[JoinedEngagementCreatedTask] = []
    service_to_task_id: Dict[str, str] = {}

    for idx, step in enumerate(steps):
        if not isinstance(step, dict):
            warnings.append(f"Step {idx + 1} skipped: invalid object")
            continue
        service_id = str(step.get("service_id") or "").strip()
        if not service_id:
            warnings.append(f"Step {idx + 1} skipped: missing service_id")
            continue

        depends_on = step.get("depends_on")
        depends_on_services = [str(x).strip() for x in depends_on] if isinstance(depends_on, list) else []
        depends_on_task_ids = [
            service_to_task_id[sid] for sid in depends_on_services if sid in service_to_task_id
        ]

        task_type = _service_to_task_type(service_id)
        task_title = f"[Joined] {service_id} ({idx + 1}/{len(steps)})"
        task_desc = improved if len(improved) <= 10000 else improved[:9997] + "..."
        params = {
            "joined_engagement_id": joined_id,
            "joined_mode": body.joined_engagement.mode,
            "joined_step_index": idx,
            "service_id": service_id,
            "depends_on_services": depends_on_services,
            "depends_on_task_ids": depends_on_task_ids,
            "source": body.source or "engage_page",
            "context": body.context or {},
        }

        task_create = tasks_integrated_routes.TaskCreate(
            title=task_title,
            description=task_desc,
            task_type=task_type,
            target=target,
            trigger_source="amas_core",
            parameters=params,
            priority=body.priority,
        )
        tr = await tasks_integrated_routes.run_integrated_task_creation(
            task_create,
            background_tasks,
            db,
            redis,
            current_user,
        )
        tid = str(getattr(tr, "id", "") or getattr(tr, "task_id", "")).strip()
        if not tid:
            warnings.append(f"Step {idx + 1} created without task id for service {service_id}")
            continue
        service_to_task_id[service_id] = tid
        created.append(
            JoinedEngagementCreatedTask(
                task_id=tid,
                title=task_title,
                service_id=service_id,
                depends_on_task_ids=depends_on_task_ids,
                status="pending",
            )
        )

    await _log_gea_audit(
        user_hint=improved,
        source=body.source,
        response_summary={
            "joined_id": joined_id,
            "created_task_ids": [x.task_id for x in created],
            "steps": len(steps),
            "warnings": warnings[:5],
        },
    )
    return JoinedEngagementCreateResponse(
        joined_id=joined_id,
        mode=body.joined_engagement.mode,
        created_tasks=created,
        warnings=warnings[:12],
    )


class TaskExplainRequest(BaseModel):
    focus_node_id: Optional[str] = None
    question: Optional[str] = None


class TaskExplainResponse(BaseModel):
    schema_version: str = "explain.v2"
    task_id: str
    bullets: List[str] = Field(default_factory=list)
    node_anchors: List[str] = Field(default_factory=list)
    pattern_tags: List[str] = Field(
        default_factory=list,
        description="Derived from RunEvents only (F6-4); empty when no events.",
    )
    model_provider: str = ""
    refusal_reason: Optional[str] = None


def _is_sandbox_or_tool_event(event_type: str) -> bool:
    et = str(event_type or "").lower()
    return et.startswith("sandbox") or "tool_call" in et


def _sandbox_event_summary(evt: Dict[str, Any]) -> str:
    """Short operator-facing line from RunEvent payload (no fabricated metrics)."""
    payload = evt.get("payload")
    if isinstance(payload, dict):
        for key in ("tool_name", "name", "command", "sandbox_id", "message"):
            v = payload.get(key)
            if v is not None and str(v).strip():
                return str(v).strip()[:200]
    return str(evt.get("event_type") or "event")[:120]


@router.get("/tasks/{task_id}/sandbox-telemetry")
async def get_task_sandbox_telemetry(
    task_id: str,
    db: Optional[AsyncSession] = Depends(_optional_db_session),
) -> Dict[str, Any]:
    """F7-1 / FE-09: counts + recent RunEvent rows — no synthetic CPU/memory."""
    from collections import Counter

    from src.amas.services import run_event_buffer as reb

    tid = str(task_id).strip()
    events = await reb.list_run_events_merged(tid, db)
    sandbox_n = sum(
        1 for e in events if str(e.get("event_type") or "").lower().startswith("sandbox")
    )
    tool_n = sum(1 for e in events if "tool_call" in str(e.get("event_type") or "").lower())
    filtered = [e for e in events if _is_sandbox_or_tool_event(str(e.get("event_type") or ""))]
    type_counts = Counter(str(e.get("event_type") or "unknown") for e in filtered)
    recent: List[Dict[str, Any]] = []
    for e in filtered[-25:]:
        recent.append(
            {
                "timestamp": str(e.get("timestamp") or ""),
                "event_type": str(e.get("event_type") or "unknown"),
                "summary": _sandbox_event_summary(e),
            }
        )
    ts_list = [str(e.get("timestamp") or "") for e in filtered if e.get("timestamp")]
    first_iso = min(ts_list) if ts_list else None
    last_iso = max(ts_list) if ts_list else None
    return {
        "schema_version": "sandbox_telemetry.v2",
        "task_id": tid,
        "available": sandbox_n > 0 or tool_n > 0,
        "sandbox_event_count": sandbox_n,
        "tool_event_count": tool_n,
        "source": "run_events",
        "event_type_counts": dict(type_counts),
        "first_event_iso": first_iso,
        "last_event_iso": last_iso,
        "recent_sandbox_tool_events": recent,
    }


@router.post("/tasks/{task_id}/explain", response_model=TaskExplainResponse)
async def post_task_explain(
    task_id: str,
    body: TaskExplainRequest = TaskExplainRequest(),
    db: Optional[AsyncSession] = Depends(_optional_db_session),
) -> TaskExplainResponse:
    """
    Orchestrator-backed run explanation via EnhancedAIRouter (no client LLM).
    Uses task status/result from the unified orchestrator when available.
    """
    tid = str(task_id).strip()
    from src.amas.services import run_event_buffer as reb

    run_events = await reb.list_run_events_merged(tid, db)
    pattern_tags = _pattern_tags_from_events(run_events)

    orch = get_unified_orchestrator()
    summary_bits: List[str] = []
    if orch and hasattr(orch, "get_task_status"):
        try:
            st = await orch.get_task_status(tid)
            if isinstance(st, dict):
                summary_bits.append(json.dumps(st, default=str)[:6000])
        except Exception as e:
            logger.debug("explain: orchestrator status failed %s", e)
    user_prompt = (
        f"Task id: {tid}\n"
        f"Focus node: {body.focus_node_id or 'n/a'}\n"
        f"Operator question: {body.question or 'Explain this run at a high level.'}\n"
        f"Task snapshot (JSON fragment):\n{summary_bits[0] if summary_bits else '{}'}\n"
        f"RunEvent-derived pattern_tags (do not contradict): {json.dumps(pattern_tags)}\n\n"
        "Respond with JSON only: {\"bullets\": [string, ...], \"node_anchors\": [string ids]}"
    )
    system = (
        build_task_creation_assistant_prompt()
        + "\n\nYou explain multi-agent runs for operators. Output JSON only."
    )
    try:
        ai_router = EnhancedAIRouter()
        ai_resp = await ai_router.generate_with_fallback(
            prompt=user_prompt,
            system_prompt=system,
            max_tokens=1200,
            temperature=0.3,
            strategy="quality_first",
        )
        parsed = _extract_json_object(ai_resp.content) or {}
        bullets = parsed.get("bullets") if isinstance(parsed.get("bullets"), list) else []
        anchors = (
            parsed.get("node_anchors")
            if isinstance(parsed.get("node_anchors"), list)
            else []
        )
        return TaskExplainResponse(
            task_id=tid,
            bullets=[str(b) for b in bullets[:20] if str(b).strip()],
            node_anchors=[str(a) for a in anchors[:20] if str(a).strip()],
            pattern_tags=pattern_tags,
            model_provider=str(ai_resp.provider or ""),
        )
    except Exception as e:
        logger.warning("task explain failed: %s", e)
        return TaskExplainResponse(
            task_id=tid,
            bullets=[],
            node_anchors=[],
            pattern_tags=pattern_tags,
            refusal_reason="Model unavailable or task snapshot missing.",
        )
