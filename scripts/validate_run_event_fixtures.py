"""
CI guardrail: validate RunEvent fixture/tooling expectations.

This is intentionally lightweight: it ensures the RunEvent buffer module can be
imported and exposes the entry points used by operator-program tests.
"""

from __future__ import annotations

import importlib
import sys


def main() -> int:
    try:
        mod = importlib.import_module("src.amas.services.run_event_buffer")
    except Exception as e:
        print(f"[validate_run_event_fixtures] import failed: {e}", file=sys.stderr)
        return 2

    required = ["list_run_events_merged"]
    missing = [name for name in required if not hasattr(mod, name)]
    if missing:
        print(
            "[validate_run_event_fixtures] missing attributes: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

