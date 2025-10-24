#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Policy-aware wrapper to launch the Bulletproof AI Analyzer with guardrails.
- Reads artifacts/validation_receipt.json for deterministic results
- Sets policy environment variables for the analyzer to obey
- Ensures raw-file truth anchoring over diff-only context
"""
import json, os, sys
from pathlib import Path

RECEIPT = Path('artifacts/validation_receipt.json')
POLICY = Path('.analysis-policy.yml')

# Default policy
SYNTAX_CONFIRMED_OK = False
DIFF_ONLY_CAP = 0.4
REQUIRE_FULL_CONTEXT_FOR_BLOCKERS = True
FORBID_SYNTAX_CLAIMS_WHEN_DETERMINISTIC_OK = True

if RECEIPT.exists():
    try:
        data = json.loads(RECEIPT.read_text())
        # If any file fails deterministic checks, we don't set SYNTAX_CONFIRMED_OK
        failures = []
        for f in data.get('files', []):
            det = f.get('deterministic', {})
            if det.get('py_compile') != 'pass' or det.get('ast') != 'pass':
                failures.append(f['file'])
        if not failures:
            SYNTAX_CONFIRMED_OK = True
    except Exception as e:
        print(f"Warning: could not parse receipt: {e}")

# Export to env for downstream analyzer
os.environ['SYNTAX_CONFIRMED_OK'] = 'true' if SYNTAX_CONFIRMED_OK else 'false'
os.environ['DIFF_ONLY_CAP_CONFIDENCE'] = str(DIFF_ONLY_CAP)
os.environ['REQUIRE_FULL_CONTEXT_FOR_BLOCKERS'] = 'true' if REQUIRE_FULL_CONTEXT_FOR_BLOCKERS else 'false'
os.environ['FORBID_SYNTAX_CLAIMS_WHEN_DETERMINISTIC_OK'] = 'true' if FORBID_SYNTAX_CLAIMS_WHEN_DETERMINISTIC_OK else 'false'

# Delegate to analyzer (kept non-fatal for CI demonstration)
code = os.system("python .github/scripts/bulletproof_ai_pr_analyzer.py")
sys.exit(os.WEXITSTATUS(code) if isinstance(code, int) else 0)
