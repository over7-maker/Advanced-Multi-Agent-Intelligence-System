# Universal AI Router - Bulletproof Multi-Provider Architecture

This document describes the production-ready Universal AI Router that guarantees zero failures for AI-dependent workflows by intelligently failing over across 15+ providers using repository secrets.

## Key Guarantees
- Zero-Fail Guarantee: Never crash workflows due to a single provider
- Intelligent Failover: Tiered, prioritized, and retried calls
- Comprehensive Coverage: 15+ providers integrated out of the box
- Repository Secrets Only: No hardcoded credentials
- Deterministic Guards: Syntax and AST checks prevent false positives

## Architecture Overview

![Architecture](images/universal_ai_router_architecture.png)

## Provider Tiers and Priority
- Tier 1: Premium Speed — Cerebras, NVIDIA Integrate
- Tier 2: High Quality — Gemini 2.0, Codestral
- Tier 3: Commercial — Cohere, Groq2*, GroqAI*
- Tier 4: Specialized — Chutes
- Tier 5: Free Fallbacks (OpenRouter) — DeepSeek, GLM, Grok, Kimi, Qwen, GPT-OSS

\* Placeholders shipped; adapters will be swapped to official SDKs when available.

## Router API (Async)
```python
from src/amas/ai/router import generate

result = await generate(
    prompt="Analyze this code for security issues",
    system_prompt="You are a security expert.",
    max_tokens=1200,
    temperature=0.3,
    timeout=30.0
)

if result["success"]:
    use(result["content"])  # Guaranteed-safe content
else:
    log_failover_attempts(result["attempts"])  # Structured failure, never crashes
```

## Health and Monitoring
```python
from src/amas/ai/router import health_check, get_available_providers

providers = get_available_providers()
health = await health_check()
```

## Integration with Hardened CI & Policy
- .github/workflows/ai-analysis-hardened.yml — Deterministic guards + receipts
- .analysis-policy.yml — Forbid syntax claims when deterministic checks pass, cap confidence for diff-only analysis, require full context for blockers

## Files in This PR
- src/amas/ai/router.py — Universal router (production)
- src/amas/ai/test_router.py — Failover and health test suite
- .github/workflows/test-bulletproof-analyzer.yml — Comprehensive CI tests
- .github/scripts/run_analyzer_with_policy.py — Policy enforcer wrapper
- .analysis-policy.yml — Policy gates and suppressions
