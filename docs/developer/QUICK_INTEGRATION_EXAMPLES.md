# ⚡ Quick Integration Examples - AMAS Phase 5

> **Last Updated**: October 2025 | **Version**: 3.0.0

## 5-Minute Quick Start

### Install & Use Universal AI Router

```bash
# Option 1: Install from source
pip install git+https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git

# Option 2: Clone and use directly
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System
export PYTHONPATH="${PWD}/src:$PYTHONPATH"
```

### Minimal Setup (3 lines)

```python
import os
from src.amas.ai.router import generate

os.environ["CEREBRAS_API_KEY"] = "your-key"
result = await generate("Hello, world!")
print(result["content"] if result["success"] else result["error"])
```

---

## Common Integration Patterns

### 1. **FastAPI Integration**

```python
from fastapi import FastAPI
from src.amas.ai.router import generate, health_check

app = FastAPI()

@app.post("/ai/generate")
async def generate_text(prompt: str):
    result = await generate(
        prompt=prompt,
        system_prompt="You are a helpful assistant.",
        timeout=30.0
    )
    return result

@app.get("/ai/health")
async def health():
    return await health_check()
```

### 2. **Django Integration**

```python
# myapp/services.py
from src.amas.ai.router import generate

class AIService:
    @staticmethod
    async def analyze_code(code: str):
        result = await generate(
            prompt=f"Analyze this code for security issues:\n{code}",
            system_prompt="You are a security expert.",
            max_tokens=1000
        )
        return result["content"] if result["success"] else None

# myapp/views.py
from myapp.services import AIService

async def code_analysis(request):
    code = request.POST.get('code')
    analysis = await AIService.analyze_code(code)
    return JsonResponse({"analysis": analysis})
```

### 3. **Flask Integration**

```python
from flask import Flask, request, jsonify
from src.amas.ai.router import generate

app = Flask(__name__)

@app.route('/ai/chat', methods=['POST'])
async def chat():
    data = request.json
    result = await generate(
        prompt=data['message'],
        timeout=30.0
    )
    return jsonify(result)
```

### 4. **CLI Tool Integration**

```python
#!/usr/bin/env python3
# my_cli_tool.py
import asyncio
import click
from src.amas.ai.router import generate

@click.command()
@click.argument('prompt')
@click.option('--timeout', default=30.0, help='Timeout in seconds')
def ai_cli(prompt, timeout):
    """Simple CLI using AMAS router"""
    result = asyncio.run(generate(prompt, timeout=timeout))
    if result["success"]:
        click.echo(result["content"])
    else:
        click.echo(f"Error: {result['error']}", err=True)

if __name__ == '__main__':
    ai_cli()
```

---

## Component-Specific Integration

### Universal AI Router Only

```python
# Minimal dependency - just the router
import sys
sys.path.insert(0, 'path/to/Advanced-Multi-Agent-Intelligence-System/src')

from amas.ai.router import (
    generate,
    get_available_providers,
    health_check
)

# Use router
result = await generate("Your prompt")
```

### Individual Agent Usage

```python
# Use OSINT agent standalone
from src.amas.agents.osint.osint_agent import OSINTAgent

agent = OSINTAgent()
result = await agent.analyze("example.com")
```

### Service Integration

```python
# Use unified intelligence service
from src.amas.services.unified_intelligence_service import UnifiedIntelligenceService

service = UnifiedIntelligenceService()
intelligence = await service.gather_intelligence(
    target="example.com",
    intelligence_types=["osint"]
)
```

---

## Docker Integration Examples

### Run Router as Microservice

```yaml
# docker-compose.yml
version: '3.8'
services:
  amas-router:
    image: ghcr.io/over7-maker/amas-router:latest
    ports:
      - "8000:8000"
    environment:
      - CEREBRAS_API_KEY=${CEREBRAS_API_KEY}
      - NVIDIA_API_KEY=${NVIDIA_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
```

### Use from Another Container

```python
# In your application container
import requests

response = requests.post(
    "http://amas-router:8000/generate",
    json={"prompt": "Hello"},
    headers={"Content-Type": "application/json"}
)
```

---

## Environment Variables Quick Reference

```bash
# Minimum (1 provider)
export CEREBRAS_API_KEY="csk-your-key"

# Recommended (3+ for failover)
export CEREBRAS_API_KEY="csk-your-key"
export NVIDIA_API_KEY="nvapi-your-key"
export GEMINI2_API_KEY="your-key"

# Optional (OpenRouter free tier)
export DEEPSEEK_API_KEY="sk-or-v1-..."
export GLM_API_KEY="sk-or-v1-..."
```

---

## Error Handling Patterns

### With Retry Logic

```python
import asyncio
from src.amas.ai.router import generate

async def generate_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        result = await generate(prompt, timeout=30.0)
        if result["success"]:
            return result["content"]
        
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    raise Exception(f"All providers failed: {result['error']}")
```

### With Fallback Response

```python
async def generate_safe(prompt):
    result = await generate(prompt, timeout=30.0)
    
    if result["success"]:
        return result["content"]
    else:
        # Fallback to default response
        return f"I apologize, but I'm unable to process your request right now. {result['error']}"
```

---

## Next Steps

- **[Full Integration Guide](PHASE_5_INTEGRATION_GUIDE.md)** - Comprehensive documentation
- **[API Reference](../api/README.md)** - Complete API documentation
- **[Provider Configuration](../AI_PROVIDERS_GUIDE.md)** - Setup all providers

---

**Last Updated**: October 2025 | **Version**: 3.0.0
