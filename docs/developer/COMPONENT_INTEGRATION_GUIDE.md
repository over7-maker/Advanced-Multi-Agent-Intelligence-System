# 🧩 Component Integration Guide - Standalone AMAS Components

> **Last Updated**: October 2025 | **Version**: 3.0.0

## Overview

This guide shows how to use individual AMAS components **outside** the full project. Each component can be integrated independently into your existing applications.

---

## 📋 Available Components

| Component | Location | Use Case | Dependencies |
|-----------|----------|----------|--------------|
| **Universal AI Router** | `src/amas/ai/router.py` | Multi-provider AI routing | `aiohttp`, `openai` (optional) |
| **OSINT Agent** | `src/amas/agents/osint/` | Intelligence gathering | Router |
| **Security Agent** | `src/amas/agents/security/` | Security analysis | Router |
| **Unified Intelligence Service** | `src/amas/services/unified_intelligence_service.py` | Multi-agent coordination | Router + Agents |
| **API Server** | `src/amas/api/` | REST API endpoint | Full stack |

---

## 🔄 Universal AI Router (Most Popular)

### Minimal Installation

```python
# Just copy these files to your project:
# - src/amas/ai/router.py
# - (optional) src/amas/config/ai_config.py

# Minimal dependencies
pip install aiohttp openai
```

### Standalone Usage

```python
import os
import asyncio
import sys

# Add router to path (if copied standalone)
sys.path.insert(0, 'path/to/router')

from router import generate, get_available_providers

async def main():
    # Set API keys
    os.environ["CEREBRAS_API_KEY"] = "your-key"
    
    # Use router
    result = await generate("Your prompt here")
    print(result["content"] if result["success"] else result["error"])

asyncio.run(main())
```

### Package Structure (If Creating Standalone Package)

```
my-project/
├── my_ai_router/
│   ├── __init__.py
│   ├── router.py        # Copied from src/amas/ai/router.py
│   └── config.py        # Minimal config
├── requirements.txt
└── setup.py
```

### setup.py Example

```python
from setuptools import setup, find_packages

setup(
    name="my-ai-router",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "openai>=1.0.0",  # Optional, for NVIDIA/Codestral
    ],
)
```

---

## 🔍 OSINT Agent Integration

### Standalone Agent

```python
import sys
sys.path.insert(0, 'path/to/amas/src')

from amas.agents.osint.osint_agent import OSINTAgent
from amas.ai.router import generate

# Configure agent with router
class StandaloneOSINTAgent:
    def __init__(self):
        self.agent = OSINTAgent()
        # Agent uses router internally for AI calls
    
    async def analyze(self, target):
        return await self.agent.analyze(target)

# Usage
agent = StandaloneOSINTAgent()
result = await agent.analyze("example.com")
```

### Minimal OSINT Integration

```python
# Copy only needed files:
# - src/amas/agents/osint/osint_agent.py
# - src/amas/agents/base/base_agent.py (dependency)

from osint_agent import OSINTAgent
from router import generate  # Your router instance

# Configure
agent = OSINTAgent()
agent.set_ai_provider(generate)  # Inject router

# Use
result = await agent.analyze("target.com")
```

---

## 🛡️ Security Agent Integration

```python
from src.amas.agents.security.security_agent import SecurityAgent

# Initialize
security_agent = SecurityAgent()

# Scan target
vulnerabilities = await security_agent.scan(
    target="https://example.com",
    scan_types=["ssl", "headers", "vulnerabilities"]
)

# Process results
for vuln in vulnerabilities:
    print(f"{vuln['severity']}: {vuln['description']}")
```

---

## 🔗 Unified Intelligence Service

### Full Service Integration

```python
from src.amas.services.unified_intelligence_service import UnifiedIntelligenceService
from src.amas.ai.router import generate

# Initialize service
service = UnifiedIntelligenceService()

# Service uses router internally, but you can inject custom
service.set_ai_provider(generate)

# Gather intelligence
result = await service.gather_intelligence(
    target="example.com",
    intelligence_types=["osint", "threat_intelligence", "security"]
)
```

### Minimal Service Setup

```python
# Copy only service files needed
# - src/amas/services/unified_intelligence_service.py
# - src/amas/core/orchestrator.py (if needed)

from unified_intelligence_service import UnifiedIntelligenceService

service = UnifiedIntelligenceService()
# Configure minimal dependencies
# service.setup_minimal()
```

---

## 🌐 API Server Integration

### Run API as Standalone Service

```bash
# From AMAS directory
export CEREBRAS_API_KEY="your-key"
uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
```

### Embed API in Existing FastAPI App

```python
from fastapi import FastAPI
from src.amas.api.routes import router as amas_router

app = FastAPI(title="My App")
app.include_router(amas_router, prefix="/amas")
```

### Custom API Endpoints

```python
from fastapi import FastAPI
from src.amas.ai.router import generate

app = FastAPI()

@app.post("/custom/ai")
async def custom_endpoint(prompt: str):
    result = await generate(prompt)
    return {
        "response": result.get("content"),
        "provider": result.get("provider_name"),
        "success": result.get("success")
    }
```

---

## 📦 Dependency Management

### Minimal Dependencies for Router Only

```txt
# requirements-minimal.txt
aiohttp>=3.8.0
```

### Standard Dependencies

```txt
# requirements.txt
aiohttp>=3.8.0
openai>=1.0.0  # For NVIDIA/Codestral support
python-dotenv>=1.0.0  # For .env file support
```

### Full Stack Dependencies

```txt
# requirements-full.txt
# See main requirements.txt in project root
```

---

## 🔧 Configuration Options

### Environment-Based Config

```python
import os
from src.amas.ai.router import generate

# Minimal config
os.environ["CEREBRAS_API_KEY"] = "your-key"

# Extended config
os.environ.update({
    "CEREBRAS_API_KEY": "csk-key",
    "NVIDIA_API_KEY": "nvapi-key",
    "GEMINI2_API_KEY": "gemini-key",
    "ROUTER_TIMEOUT": "45",
    "ROUTER_MAX_RETRIES": "3",
    "ROUTER_STRATEGY": "intelligent"
})
```

### Config File Approach

```python
# config.py
PROVIDER_CONFIG = {
    "cerebras": {
        "api_key": os.getenv("CEREBRAS_API_KEY"),
        "enabled": True
    },
    "nvidia": {
        "api_key": os.getenv("NVIDIA_API_KEY"),
        "enabled": True
    }
}

# Use in router
from router import generate
result = await generate("prompt")
```

---

## 🚀 Performance Optimization

### Connection Pooling

```python
import aiohttp
from src.amas.ai.router import generate

# Reuse session across requests
async with aiohttp.ClientSession() as session:
    for prompt in prompts:
        result = await generate(prompt, session=session)
```

### Batch Processing

```python
import asyncio
from src.amas.ai.router import generate

async def process_batch(prompts):
    tasks = [generate(p) for p in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

---

## 🐛 Troubleshooting

### Import Errors

```python
# If getting import errors, ensure path is correct
import sys
sys.path.insert(0, '/path/to/amas/src')

# Or use PYTHONPATH
# export PYTHONPATH="${PWD}/src:$PYTHONPATH"
```

### Provider Not Found

```python
from src.amas.ai.router import get_available_providers

providers = get_available_providers()
if not providers:
    print("No providers configured. Set at least one API key.")
```

### Timeout Issues

```python
# Increase timeout for complex prompts
result = await generate(
    prompt="Complex analysis...",
    timeout=60.0,  # 60 seconds
    max_tokens=4000
)
```

---

## 📚 Related Documentation

- **[Quick Integration Examples](QUICK_INTEGRATION_EXAMPLES.md)** - 5-minute quick start
- **[Full Integration Guide](PHASE_5_INTEGRATION_GUIDE.md)** - Comprehensive guide
- **[Router API Reference](../UNIVERSAL_AI_ROUTER.md)** - Complete router documentation

---

**Last Updated**: October 2025 | **Version**: 3.0.0
