
# 🤖 Universal AI Manager Integration Guide

## Overview

The Universal AI Manager provides a centralized, robust fallback system for all 16 AI providers.
It ensures zero workflow failures due to API issues.

## Features

✅ **16 AI Providers** - Support for all your API keys
✅ **Intelligent Fallback** - Automatic provider switching on failure
✅ **4 Selection Strategies** - Priority, Round Robin, Intelligent, Fastest
✅ **Circuit Breaker** - Auto-disable failing providers
✅ **Rate Limit Handling** - Automatic retry after rate limits
✅ **Performance Tracking** - Success rate and response time metrics
✅ **Zero Configuration** - Reads all API keys from environment

## Supported Providers (in priority order)

1. DeepSeek V3.1
2. GLM 4.5 Air
3. xAI Grok Beta
4. MoonshotAI Kimi
5. Qwen Plus
6. GPT OSS
7. Groq AI
8. Cerebras AI
9. Gemini AI
10. Codestral
11. NVIDIA AI
12. Gemini 2 (secondary)
13. Groq 2 (secondary)
14. Cohere
15. Chutes AI

## Quick Start

### 1. Import the Manager

```python
from src.amas.services.universal_ai_manager import get_universal_ai_manager, generate_ai_response

# Get manager instance
manager = get_universal_ai_manager()
```

### 2. Generate Response (Simple)

```python
# Using convenience function
result = await generate_ai_response(
    prompt="Your prompt here",
    system_prompt="Optional system prompt",
    strategy='intelligent'
)

if result['success']:
    print(result['content'])
else:
    print(f"Error: {result['error']}")
```

### 3. Generate Response (Advanced)

```python
# Using manager directly for more control
result = await manager.generate(
    prompt="Your prompt here",
    system_prompt="Optional system prompt",
    strategy='intelligent',  # 'priority' | 'round_robin' | 'fastest'
    max_attempts=5,  # Try up to 5 providers
    max_tokens=4096,
    temperature=0.7
)
```

## Selection Strategies

### Priority Strategy
Uses providers in priority order (1-15). Best for consistent results.

```python
result = await manager.generate(prompt, strategy='priority')
```

### Intelligent Strategy (Recommended)
Weighted selection based on success rate and response time.

```python
result = await manager.generate(prompt, strategy='intelligent')
```

### Round Robin Strategy
Distributes load evenly across all providers.

```python
result = await manager.generate(prompt, strategy='round_robin')
```

### Fastest Strategy
Always uses the fastest responding provider.

```python
result = await manager.generate(prompt, strategy='fastest')
```

## Monitoring & Statistics

### Get Overall Stats

```python
stats = manager.get_stats()
print(f"Success Rate: {stats['success_rate']}")
print(f"Average Response Time: {stats['average_response_time']}")
print(f"Total Fallbacks: {stats['total_fallbacks']}")
```

### Get Provider Health

```python
health = manager.get_provider_health()
for provider_id, info in health.items():
    print(f"{info['name']}: {info['status']} - Success Rate: {info['success_rate']}")
```

### Get Configuration Summary

```python
print(manager.get_config_summary())
```

## Migration from Old Code

### Old Code (Multiple Clients)

```python
# OLD - Don't use this anymore
from openai import OpenAI

deepseek_client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv('DEEPSEEK_API_KEY')
)

try:
    response = deepseek_client.chat.completions.create(...)
except:
    # Manual fallback logic...
    glm_client = OpenAI(...)
```

### New Code (Universal Manager)

```python
# NEW - Use this instead
from src.amas.services.universal_ai_manager import generate_ai_response

# Automatic fallback across all 16 providers
result = await generate_ai_response(
    prompt="Your prompt",
    strategy='intelligent'
)
```

## GitHub Workflows Integration

### Update workflow files to include all API keys:

```yaml
env:
  DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
  GLM_API_KEY: ${{ secrets.GLM_API_KEY }}
  GROK_API_KEY: ${{ secrets.GROK_API_KEY }}
  KIMI_API_KEY: ${{ secrets.KIMI_API_KEY }}
  QWEN_API_KEY: ${{ secrets.QWEN_API_KEY }}
  GPTOSS_API_KEY: ${{ secrets.GPTOSS_API_KEY }}
  GROQAI_API_KEY: ${{ secrets.GROQAI_API_KEY }}
  CEREBRAS_API_KEY: ${{ secrets.CEREBRAS_API_KEY }}
  GEMINIAI_API_KEY: ${{ secrets.GEMINIAI_API_KEY }}
  CODESTRAL_API_KEY: ${{ secrets.CODESTRAL_API_KEY }}
  NVIDIA_API_KEY: ${{ secrets.NVIDIA_API_KEY }}
  GEMINI2_API_KEY: ${{ secrets.GEMINI2_API_KEY }}
  GROQ2_API_KEY: ${{ secrets.GROQ2_API_KEY }}
  COHERE_API_KEY: ${{ secrets.COHERE_API_KEY }}
  CHUTES_API_KEY: ${{ secrets.CHUTES_API_KEY }}
```

## Circuit Breaker

The manager includes a circuit breaker that:
- Disables providers after 5 consecutive failures
- Re-enables them after 10 minutes
- Prevents cascading failures

## Rate Limit Handling

When a provider is rate limited:
- Automatically marked as unavailable for 5 minutes
- Other providers are tried immediately
- No manual intervention needed

## Best Practices

1. **Always use async/await** - The manager is fully async
2. **Use 'intelligent' strategy** - Best balance of performance and reliability
3. **Monitor stats regularly** - Check success rates and adjust if needed
4. **Set appropriate max_attempts** - Default tries all providers, can limit for faster failures
5. **Include system prompts** - Better results with context

## Troubleshooting

### No Providers Available

```python
# Check if any providers are configured
manager = get_universal_ai_manager()
print(manager.get_config_summary())

# Reset failed providers
manager.reset_stats()
```

### All Requests Failing

```python
# Check provider health
health = manager.get_provider_health()
for provider_id, info in health.items():
    if not info['available']:
        print(f"❌ {info['name']}: {info['last_error']}")
```

### Slow Responses

```python
# Use fastest strategy
result = await manager.generate(prompt, strategy='fastest')

# Or check which providers are slow
health = manager.get_provider_health()
for provider_id, info in health.items():
    print(f"{info['name']}: {info['avg_response_time']}")
```

## Support

For issues or questions:
1. Check provider health: `manager.get_provider_health()`
2. Review statistics: `manager.get_stats()`
3. Check logs for detailed error messages

## Testing

Run the built-in test:

```bash
python -m src.amas.services.universal_ai_manager
```

This will test all configured providers and show detailed statistics.
