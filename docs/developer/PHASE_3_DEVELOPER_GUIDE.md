# 🚀 Phase 3 Developer Guide — Universal AI Router, Bulletproof Validation, Security & Observability

This guide shows developers how to integrate Phase 3 features from AMAS into external projects or standalone services. It covers the Universal AI Router API, configuration, security (JWT/OIDC), observability (Prometheus/Grafana), and CI policy enforcement.

---

## 📦 What You Get (Phase 3)
- 🔄 Universal AI Router (`src/amas/ai/router.py`) — async, multi-provider, zero-fail design
- 🛡️ Bulletproof AI Validation — fake AI detection, policy enforcement
- 🔒 Security — JWT/OIDC, rate limiting, audit logging
- 📈 Observability — Prometheus metrics, health checks, Grafana dashboards
- ⚙️ Hardened CI — `.analysis-policy.yml`, workflows for safe automation

---

## 📥 Installation Options

### 1) Vendor AMAS as a Library
- Copy the `src/amas/ai/router.py` and its minimal dependencies into your project, or
- Package the AMAS `src/amas` directory as an internal module.

Recommended structure in your project:
```
<your_project>/
  src/
    your_app/
      ...
    amas/           # vendored module (if you choose to vendor)
      ai/
        router.py
      ...
```

### 2) Run AMAS as a Sidecar Service
- Deploy AMAS as a microservice and call it via your backend using HTTP/JSON.
- Expose endpoints (e.g., `/ai/generate`, `/health`, `/metrics`).

---

## 🔧 Configuration (Environment)

Minimum for using Universal AI Router:

- Provider API keys (at least one):
  - `CEREBRAS_API_KEY`, `NVIDIA_API_KEY`, `GEMINI2_API_KEY`, `CODESTRAL_API_KEY`,
  - `GROQ2_API_KEY`, `GROQAI_API_KEY`, `COHERE_API_KEY`, `CHUTES_API_KEY`
  - OpenRouter-backed fallbacks: `DEEPSEEK_API_KEY`, `GLM_API_KEY`, `GROK_API_KEY`, `KIMI_API_KEY`, `QWEN_API_KEY`, `GPTOSS_API_KEY`
- Bulletproof validation toggle (optional, recommended):
  - `BULLETPROOF_VALIDATION=true`

Security (optional but recommended for services):
- `JWT_SECRET_KEY`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET`
- `RATE_LIMIT_ENABLED=true`, `AUDIT_LOGGING=true`, `SECURITY_HEADERS_ENABLED=true`

Observability:
- `PROMETHEUS_ENABLED=true` (if exposing metrics)

---

## 🧠 Universal AI Router — Usage

Import path (if using AMAS source layout):
```python
from src.amas.ai.router import generate, get_available_providers, health_check
```

Basic async usage:
```python
result = await generate(
    prompt="Summarize the release notes in 3 bullets.",
    system_prompt="You are a concise technical writer.",
    max_tokens=400,
    timeout=30.0,
)

if result["success"]:
    print(result["content"])              # model response
    print(result["provider_name"])        # selected provider
    print(result["response_time"])        # seconds
else:
    print("Graceful failure:", result["error"])      # workflow continues without crashing
    print("Attempts:", result["attempts"])           # structured failover history
```

Provider discovery and health:
```python
providers = get_available_providers()
print("Available providers:", providers)

health = await health_check()
print("Status:", health["status"])            # e.g., healthy/degraded
print("Healthy:", len(health["healthy"]))
print("Failed:", len(health["failed"]))
```

Notes:
- Router automatically prioritizes providers by speed/quality and fails over on errors.
- Returns structured results and never crashes workflows (graceful degradation).

---

## 🛡️ Bulletproof Validation & Policy

- Policy file: `.analysis-policy.yml` — controls AI analysis behavior (confidence caps, require full context, deterministic checks before AI, etc.)
- Enable validation in environments where AI results must be audited:
  - `BULLETPROOF_VALIDATION=true`

If integrating CI checks:
- Use `.github/workflows/bulletproof-ai-pr-analysis.yml`
- Ensure your runners have at least one provider API key secret configured

---

## 🔒 Security Integration (FastAPI example)

JWT/OIDC (example sketch):
```python
from fastapi import FastAPI, Depends, HTTPException
from your_project.security.jwt import verify_jwt  # implement using PyJWT

app = FastAPI()

@app.get("/secure-endpoint")
async def secure_endpoint(user = Depends(verify_jwt)):
    return {"ok": True, "user": user}
```

Key requirements:
- Validate signature (algorithms pinned)
- Check `exp`, `nbf`, `iss`, `aud`
- Enforce roles/permissions if needed
- Add security headers (CSP, HSTS) and rate limiting in middleware

---

## 📈 Observability (Prometheus/Grafana)

Expose metrics and health endpoints from your service:
- `/metrics` — Prometheus scrape endpoint
- `/health` — JSON status (router health, dependencies)

Example FastAPI wiring:
```python
from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI()
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health")
async def health():
    # include router health summary if using AMAS router
    return {"status": "ok"}
```

Use the provided Grafana dashboards in `docs/OBSERVABILITY_STACK.md` or your own.

---

## 🧪 Testing & Local Dev

- Unit test the router call sites with provider stubs/mocks
- Verify graceful degradation (all providers fail → structured error, no crash)
- Add latency budgets and retry backoff tests
- For security, test JWT invalid/expired/missing claims and role enforcement

---

## 🔗 CI Integration (Optional)

- Reuse the hardened workflows from `.github/workflows/*bulletproof*`
- Configure secrets in CI (provider keys, JWT secrets if needed)
- Use `.analysis-policy.yml` to enforce deterministic checks and limit overconfident AI outputs

---

## ✅ Checklist for External Integration

- [ ] Choose integration mode: vendor library vs. sidecar service
- [ ] Configure at least one provider API key (recommend 3+)
- [ ] (Optional) Enable `BULLETPROOF_VALIDATION`
- [ ] Add JWT/OIDC validation and security headers if exposing endpoints
- [ ] Expose `/metrics` and `/health` for ops
- [ ] Add tests for failover behavior and latency budgets
- [ ] (Optional) Adopt CI workflows and `.analysis-policy.yml`

---

## 📚 References
- Universal AI Router: `docs/UNIVERSAL_AI_ROUTER.md`
- AI Providers Guide: `docs/AI_PROVIDERS.md`
- Security (Phase 2): `docs/PHASE_2_FEATURES.md`
- Monitoring: `docs/MONITORING_GUIDE.md`
- Examples (artifacts):
  - `artifacts/bulletproof_real_ai_analysis_example.md`
  - `artifacts/bulletproof_phase2_fixed_report.md`
