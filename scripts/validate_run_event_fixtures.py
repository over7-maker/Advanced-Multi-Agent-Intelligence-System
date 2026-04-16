"""
CI guardrail: validate RunEvent fixture/tooling expectations.

This is intentionally lightweight and side-effect free:
- CI should not fail if optional RunEvent buffering is deferred.
- Avoid importing `src.amas.services` (its `__init__` imports many optional deps).
- Instead, verify (when present) that the module file exists and contains the
  expected public function name.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    candidate = repo_root / "src" / "amas" / "services" / "run_event_buffer.py"

    if not candidate.exists():
        print("[validate_run_event_fixtures] optional: run_event_buffer.py not present; skipping")
        return 0

    text = candidate.read_text(encoding="utf-8", errors="replace")
    if "def list_run_events_merged" not in text:
        print(
            "[validate_run_event_fixtures] run_event_buffer.py present but missing def list_run_events_merged",
            file=sys.stderr,
        )
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

