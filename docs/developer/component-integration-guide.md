# 🧩 Component Integration Guide - Standalone AMAS Components

> Last Updated: October 2025 | Version: 3.0.0

## NVIDIA NIM Integration

This project supports NVIDIA's OpenAI-compatible Integrate API for model access.

### Requirements
- Python package `openai` (for OpenAI-compatible clients)
- Environment variable: `NVIDIA_API_KEY`

### Example
```python
from src.amas.ai.router import generate

result = await generate(
    prompt="Summarize recent changes.",
    system_prompt="You are a concise assistant.",
    timeout=30.0
)

print(result)
```

Notes:
- The router uses base_url `https://integrate.api.nvidia.com/v1` under the hood when NVIDIA is selected.
- Ensure `NVIDIA_API_KEY` is set in your environment.

---

More component integrations coming soon.
