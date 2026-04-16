from __future__ import annotations

from typing import Any, Dict, List, Optional


def build_task_creation_assistant_prompt(
    *,
    raw_goal: str,
    service_catalog_text: str,
    recommendations: Optional[List[Dict[str, Any]]] = None,
    policy_status: str = "allowed",
    policy_reasons: Optional[List[str]] = None,
) -> str:
    """
    Compose a task-creation assistant prompt for the operator UI.

    Kept dependency-free so `src/api/routes/operator.py` can import it in CI/unit tests.
    """
    rec_lines: List[str] = []
    for rec in recommendations or []:
        tt = str(rec.get("task_type") or "").strip() or "unknown"
        conf = rec.get("confidence")
        reason = str(rec.get("reason") or "").strip()
        conf_str = f"{float(conf):.2f}" if isinstance(conf, (int, float)) else "n/a"
        rec_lines.append(f"- task_type={tt} confidence={conf_str} reason={reason}")

    policy_lines = "\n".join(f"- {r}" for r in (policy_reasons or [])) or "- (none)"

    return "\n".join(
        [
            "You are AMAS Task Creation Assistant.",
            "",
            "## User goal",
            raw_goal.strip() or "(empty)",
            "",
            "## Available services (SEP registry)",
            service_catalog_text.strip() or "(no services available)",
            "",
            "## Recommended task types (heuristic/ML)",
            "\n".join(rec_lines) if rec_lines else "- (none)",
            "",
            "## Policy",
            f"status={policy_status}",
            "reasons:",
            policy_lines,
            "",
            "Return a JSON object with:",
            '- "title": short title',
            '- "description": refined description',
            '- "task_type": one of the recommended task types when possible',
            '- "target": best guess target (URL, repo, file path, host, etc.)',
            '- "parameters": object of optional params',
            "",
        ]
    )

