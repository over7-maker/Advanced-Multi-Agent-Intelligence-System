"""
Diagnostic bootstrap: phased Python/pytest checks with NDJSON logs to debug-c21c30.log
Session: c21c30 — maps steps to hypotheses H1–H5.
"""
# region agent log
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_LOG = _REPO_ROOT / "debug-c21c30.log"
_SESSION = "c21c30"


def _log(message: str, hypothesis_id: str, data: dict | None = None) -> None:
    line = {
        "sessionId": _SESSION,
        "timestamp": int(time.time() * 1000),
        "location": "scripts/debug_session_verify.py",
        "message": message,
        "hypothesisId": hypothesis_id,
        "data": data or {},
    }
    with open(_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


# endregion


def main() -> int:
    # H5: prove Python process runs and can write the log file
    _log("bootstrap_start", "H5", {"argv": sys.argv, "executable": sys.executable, "cwd": str(Path.cwd())})

    # H1: interpreter / version
    _log("python_version_ok", "H1", {"version": sys.version})

    # H2: pytest import
    try:
        import pytest  # noqa: F401

        _log("pytest_import_ok", "H2", {})
    except Exception as e:
        _log("pytest_import_fail", "H2", {"error": repr(e)})
        return 1

    # H3: heavy src import (same path as CI: PYTHONPATH=repo root often; tests use src on path)
    os.environ.setdefault("AMAS_LOCAL_ONLY", "1")
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    try:
        from src.api.routes import operator as _op  # noqa: F401

        _log("import_operator_ok", "H3", {})
    except Exception as e:
        _log("import_operator_fail", "H3", {"error": repr(e)})
        return 1

    # H4: pytest collect + run minimal unit file
    target = str(_REPO_ROOT / "tests" / "unit" / "test_operator_probes_v2.py")
    _log("pytest_collect_start", "H4", {"target": target})
    code_collect = pytest.main([target, "--collect-only", "-q", "--tb=no"])
    _log("pytest_collect_done", "H4", {"exit_code": code_collect})

    _log("pytest_run_start", "H4", {"target": target})
    code_run = pytest.main([target, "-q", "--tb=short", "--strict-markers"])
    _log("pytest_run_done", "H4", {"exit_code": code_run})

    _log("bootstrap_complete", "H4", {"exit_code": code_run})
    return int(code_run or 0)


if __name__ == "__main__":
    raise SystemExit(main())
