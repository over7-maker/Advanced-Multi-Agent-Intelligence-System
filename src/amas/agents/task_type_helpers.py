from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class TaskTypeRecommendation:
    task_type: str
    confidence: float
    reason: str


def recommend_task_types(
    *,
    raw_goal: str,
    context: Optional[Dict[str, Any]] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Lightweight, dependency-free task-type recommender used by operator routes.

    Notes:
    - Kept intentionally simple to avoid pulling in optional ML dependencies during
      FastAPI import time and in CI/unit tests.
    - Returns a JSON-serializable list of dicts; caller may enrich using ML later.
    """
    goal = (raw_goal or "").strip().lower()
    ctx = context or {}

    candidates: List[TaskTypeRecommendation] = []

    def add(tt: str, conf: float, why: str) -> None:
        candidates.append(TaskTypeRecommendation(task_type=tt, confidence=conf, reason=why))

    if any(k in goal for k in ("scan", "cve", "vuln", "penetration", "exploit", "security")):
        add("security_scan", 0.82, "Goal mentions security scanning / vulnerabilities")

    if any(k in goal for k in ("bug", "fix", "refactor", "code", "lint", "build", "typescript", "python")):
        add("code_analysis", 0.76, "Goal mentions code change, analysis, or build/lint issues")

    if any(k in goal for k in ("research", "osint", "investigate", "collect", "intel")):
        add("intelligence_gathering", 0.74, "Goal mentions research / investigation / OSINT")

    if any(k in goal for k in ("deploy", "k8s", "kubernetes", "docker", "compose", "nginx", "prod")):
        add("deployment", 0.72, "Goal mentions deployment / infrastructure keywords")

    if any(k in goal for k in ("test", "pytest", "playwright", "e2e", "ci", "workflow")):
        add("testing", 0.78, "Goal mentions tests / CI / E2E")

    # Context hint from UI (optional)
    ui_source = str(ctx.get("source") or "").lower()
    if ui_source in ("engage_page", "create_task", "palette") and not candidates:
        add("general_assistance", 0.55, "No strong signals; defaulting to general assistance")

    # Dedupe while keeping order, then truncate.
    seen: set[str] = set()
    out: List[Dict[str, Any]] = []
    for rec in sorted(candidates, key=lambda r: r.confidence, reverse=True):
        if rec.task_type in seen:
            continue
        seen.add(rec.task_type)
        out.append({"task_type": rec.task_type, "confidence": rec.confidence, "reason": rec.reason})
        if len(out) >= max(1, int(limit)):
            break

    return out

