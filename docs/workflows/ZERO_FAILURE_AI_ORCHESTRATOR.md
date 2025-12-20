# Zero-Failure AI Orchestrator

## Overview

The Zero-Failure AI Orchestrator is a robust system designed to ensure **zero workflow failures** by implementing a 16-provider fallback chain. If one AI provider fails, the system automatically tries the next provider until success or all providers are exhausted.

**Part of PR #272: Zero-Failure AI Orchestrator System**

## Architecture

```
User Request
    ↓
AI Orchestrator
    ↓
Cache Check (if enabled)
    ↓
Provider Chain Selection (based on task type)
    ↓
Provider 1 → Try → Success? → Return
    ↓ (if failed)
Provider 2 → Try → Success? → Return
    ↓ (if failed)
... (continue through all 16 providers)
    ↓ (if all failed)
Return error (non-blocking)
```

## Supported Providers

The orchestrator supports 16 AI providers with automatic fallback:

1. **DeepSeek** (OpenRouter) - `DEEPSEEK_API_KEY`
2. **GLM** (OpenRouter) - `GLM_API_KEY`
3. **Grok** (OpenRouter) - `GROK_API_KEY`
4. **Kimi** (OpenRouter) - `KIMI_API_KEY`
5. **Qwen** (OpenRouter) - `QWEN_API_KEY`
6. **GPT-OSS** (OpenRouter) - `GPTOSS_API_KEY`
7. **NVIDIA** - `NVIDIA_API_KEY`
8. **Codestral** (Mistral) - `CODESTRAL_API_KEY`
9. **Chutes** - `CHUTES_API_KEY`
10. **Cerebras** - `CEREBRAS_API_KEY`
11. **Gemini** (Google) - `GEMINIAI_API_KEY`
12. **Gemini 2** (Google) - `GEMINI2_API_KEY`
13. **Groq** - `GROQAI_API_KEY`
14. **Groq 2** - `GROQ2_API_KEY`
15. **Cohere** - `COHERE_API_KEY`

## Task Types

The orchestrator supports the following task types:

- `code_review` - Code review and analysis
- `pr_analysis` - Pull request analysis
- `security_scan` - Security vulnerability scanning
- `performance_analysis` - Performance bottleneck analysis
- `documentation` - Documentation generation
- `test_generation` - Test case generation
- `dependency_analysis` - Dependency analysis
- `general` - General purpose AI tasks

## Usage

### As a Reusable Workflow

```yaml
jobs:
  ai-task:
    uses: ./.github/workflows/00-zero-failure-ai-orchestrator.yml
    with:
      task_type: "code_review"
      system_message: "You are an expert code reviewer."
      user_prompt: "Review this code: ..."
      max_tokens: 2000
      temperature: 0.7
      use_cache: true
    secrets: inherit
```

### As a Python Script

```python
from ai_orchestrator import AIOrchestrator

orchestrator = AIOrchestrator(cache_enabled=True)
result = await orchestrator.execute(
    task_type="code_review",
    system_message="You are an expert code reviewer.",
    user_prompt="Review this code: ...",
    max_tokens=2000,
    temperature=0.7
)

if result["success"]:
    print(f"Provider: {result['provider']}")
    print(f"Response: {result['response']}")
else:
    print(f"Error: {result['error']}")
```

### CLI Interface

```bash
python .github/scripts/ai_orchestrator.py \
  --task-type "code_review" \
  --system-message "You are an expert code reviewer." \
  --user-prompt "Review this code: ..." \
  --max-tokens 2000 \
  --temperature 0.7 \
  --output result.json
```

## Outputs

The orchestrator returns a dictionary with the following structure:

```python
{
    "success": bool,           # Whether the task succeeded
    "provider": str,           # Provider that succeeded (or "cache" or "none")
    "response": str,           # AI response text
    "duration_ms": int,        # Execution duration in milliseconds
    "fallback_count": int,     # Number of providers tried before success
    "cached": bool             # Whether response was from cache
}
```

## Caching

The orchestrator includes a file-based caching system:

- **Cache Directory**: `.github/cache/ai_responses`
- **TTL**: 24 hours (configurable)
- **Cache Key**: SHA256 hash of task_type + system_message + user_prompt
- **Automatic Expiry**: Expired cache entries are automatically deleted

### Cache Management

```python
from ai_cache import AICache

cache = AICache()

# Get cache statistics
stats = cache.stats()
print(f"Total files: {stats['total_files']}")
print(f"Valid files: {stats['valid_files']}")

# Clear cache (all or by task type)
deleted = cache.clear()  # Clear all
deleted = cache.clear("code_review")  # Clear specific task type
```

## Safety Features

1. **Non-Blocking Failures**: If all providers fail, the workflow continues with a warning (does not fail the entire workflow)
2. **Timeout Protection**: Each provider has a 60-second timeout (configurable)
3. **Error Handling**: All errors are caught and logged, with graceful fallback
4. **Metrics Logging**: All executions are logged to `.github/data/metrics/`

## Metrics

Metrics are automatically logged to `.github/data/metrics/metrics_YYYYMMDD.jsonl`:

```json
{
  "timestamp": "2025-12-20T18:30:00",
  "provider": "deepseek",
  "task_type": "code_review",
  "success": true,
  "duration_ms": 1234,
  "fallback_count": 0
}
```

## Troubleshooting

### All Providers Fail

**Symptom**: `success: false` with `error: "All X providers failed"`

**Solutions**:
1. Check API keys are set in GitHub Secrets
2. Verify network connectivity
3. Check provider status pages
4. Review error logs in artifacts

### Cache Issues

**Symptom**: Responses not being cached or cache not working

**Solutions**:
1. Check `.github/cache/ai_responses` directory exists and is writable
2. Verify cache is enabled: `use_cache: true`
3. Check cache TTL settings

### Performance Issues

**Symptom**: Slow execution times

**Solutions**:
1. Enable caching to reduce redundant API calls
2. Check provider response times in metrics
3. Consider using faster providers for simple tasks
4. Review fallback_count - high values indicate provider issues

## Best Practices

1. **Always use caching** for repeated queries
2. **Set appropriate timeouts** based on task complexity
3. **Monitor metrics** regularly to identify provider issues
4. **Use task-specific routing** for optimal provider selection
5. **Handle failures gracefully** - the orchestrator is non-blocking by design

## Configuration

### Environment Variables

All API keys should be set as environment variables or GitHub Secrets:

- `DEEPSEEK_API_KEY`
- `GLM_API_KEY`
- `GROK_API_KEY`
- `KIMI_API_KEY`
- `QWEN_API_KEY`
- `GPTOSS_API_KEY`
- `NVIDIA_API_KEY`
- `CODESTRAL_API_KEY`
- `CHUTES_API_KEY`
- `CEREBRAS_API_KEY`
- `GEMINIAI_API_KEY`
- `GEMINI2_API_KEY`
- `GROQAI_API_KEY`
- `GROQ2_API_KEY`
- `COHERE_API_KEY`

### Customization

You can customize provider behavior by modifying `.github/scripts/ai_orchestrator.py`:

- **Provider Timeout**: Change `timeout` in `Provider` dataclass
- **Cache TTL**: Change `ttl_hours` in `AICache` class
- **Provider Priority**: Modify `_provider_chain()` method

## Related Documentation

- [AI Autonomy Agents](./AI_AUTONOMY_AGENTS.md) - Documentation for the 7 autonomous agents
- [Workflow Consolidation Plan](../CONSOLIDATION_IMPLEMENTATION_PLAN.md) - Overall workflow strategy
