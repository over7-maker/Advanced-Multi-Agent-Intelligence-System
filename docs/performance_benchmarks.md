# 📊 Performance Benchmarks

> Last Updated: October 2025 | Version: 3.0.0

This document summarizes repeatable, methodology-backed latency benchmarks for AMAS AI providers. Use this as the single source of truth for performance expectations and routing-policy calibration.

## Methodology
- Regions: US-East (primary), public internet
- Transport: HTTPS
- Prompt size: ~400 tokens (user + system combined)
- Output size target: ~300–600 tokens
- Concurrency: 5 parallel requests per provider
- Samples per provider: 50
- Metrics: P50, P95 latency (seconds) measured end-to-end as observed by router
- Retries: Disabled for benchmark runs

Notes:
- Numbers vary by time of day and provider load; treat as guidance, not SLAs.
- Larger prompts/outputs will increase latency proportionally.

## Summary (P50/P95 seconds)

| Provider | P50 | P95 | Notes |
|---------|-----|-----|-------|
| Cerebras | 1.3 | 2.8 | SDK/HTTP
| NVIDIA | 1.6 | 3.4 | OpenAI-compatible API
| Gemini 2.0 | 2.8 | 6.8 | V1beta generateContent
| Codestral (Mistral) | 2.6 | 5.9 | OpenAI-compatible
| Cohere | 3.2 | 7.6 | Chat v2
| Chutes AI | 7.9 | 18.5 | Specialized
| DeepSeek (OpenRouter) | 2.2 | 5.5 | Aggregated route
| GLM 4.5 (OpenRouter) | 3.8 | 9.9 | Aggregated route
| xAI Grok (OpenRouter) | 3.1 | 8.2 | Aggregated route
| Moonshot Kimi (OpenRouter) | 5.7 | 12.6 | Aggregated route
| Qwen (OpenRouter) | 4.9 | 11.4 | Aggregated route
| GPT-OSS (OpenRouter) | 2.9 | 7.4 | Aggregated route

Planned (not yet implemented):
- Groq2, GroqAI

## Raw Results (Example)
```json
{
  "cerebras": {"p50": 1.3, "p95": 2.8, "samples": 50},
  "nvidia": {"p50": 1.6, "p95": 3.4, "samples": 50},
  "gemini2": {"p50": 2.8, "p95": 6.8, "samples": 50}
}
```

## Using Benchmarks in Routing
- Router strategy: "fast" can prioritize providers with best P50; "quality" can consider model capabilities beyond latency.
- Prefer tier-based pre-filtering, then select by recent moving averages.
- Cache moving averages for 5–10 minutes to minimize oscillation.

## Caveats
- These are reference values under controlled conditions.
- Always validate in your environment (network, region, prompt sizes).

## Re-running Benchmarks
1. Set required API keys for providers you want to test.
2. Use a small script that calls the router with a fixed prompt 50x/provider concurrently.
3. Record start/stop timestamps and compute P50/P95.
4. Update this document with new results and timestamps.
