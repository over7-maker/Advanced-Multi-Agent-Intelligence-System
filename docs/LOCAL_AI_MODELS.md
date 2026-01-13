# Local AI Models Configuration

This document describes how to configure and use local AI models in the AMAS project.

## Overview

The AMAS system supports local AI models through:
- **Ollama** - Local LLM runtime (primary local provider)
- **LocalAI** - OpenAI-compatible local server (optional)

## Detected Models

The system has automatically detected the following local models:

### Ollama Models (3 models available)

1. **deepseek-r1:8b** (5.2 GB)
   - Preferred model (configured as default)
   - High-quality reasoning model
   - Best for: Security analysis, code review, complex tasks

2. **qwen3:4b** (2.5 GB)
   - Lightweight model
   - Fast inference
   - Best for: Quick tasks, simple queries

3. **mistral:latest** (4.4 GB)
   - Balanced performance
   - Good for: General tasks, documentation

## Configuration

### Automatic Setup

Run the setup script to automatically detect and configure local models:

```bash
python scripts/setup_local_ai_models.py
```

This script will:
- Detect all available Ollama models
- Detect LocalAI instances (if available)
- Update `.env` file with detected models
- Create `local_ai_models.json` configuration file

### Manual Configuration

#### Environment Variables

Add to your `.env` file:

```env
# Ollama Configuration
OLLAMA_MODEL=deepseek-r1:8b
OLLAMA_BASE_URL=http://localhost:11434/v1

# LocalAI Configuration (optional)
LOCALAI_BASE_URL=http://localhost:8080
```

#### Model Selection Priority

The system uses models in this order:
1. **Configured model** (`OLLAMA_MODEL` env var) - if available
2. **Available models** - detected from Ollama API
3. **Fallback models** - only if no models are detected

## Usage

### In Code

The system automatically uses local models when:
- No API keys are configured for cloud providers
- Cloud providers fail or are unavailable
- Local models are explicitly requested

### Testing Local Models

Use the Testing Dashboard to test local models:

1. Navigate to `/testing` in the frontend
2. Select "AI Providers Testing"
3. Choose "ollama" provider
4. Enter a test prompt
5. Click "Test"

### Agent Execution

All agents automatically use local models as fallback:

```python
from src.amas.ai.enhanced_router_v2 import generate_with_fallback

response = await generate_with_fallback(
    prompt="Analyze this code for security issues",
    system_prompt="You are a security expert",
    max_tokens=2000
)
```

## Model Information

### deepseek-r1:8b

- **Size**: 5.2 GB
- **Type**: Reasoning model
- **Best for**: 
  - Security analysis
  - Code review
  - Complex reasoning tasks
  - Multi-step problem solving

### qwen3:4b

- **Size**: 2.5 GB
- **Type**: Lightweight model
- **Best for**:
  - Quick responses
  - Simple queries
  - Low-resource environments

### mistral:latest

- **Size**: 4.4 GB
- **Type**: General-purpose model
- **Best for**:
  - General tasks
  - Documentation
  - Balanced performance

## Adding New Models

### Install Ollama Model

```bash
ollama pull <model-name>
```

Common models:
```bash
ollama pull llama3.2
ollama pull llama3.1:8b
ollama pull codellama
ollama pull mistral
```

### Update Configuration

After installing a new model, run:

```bash
python scripts/setup_local_ai_models.py
```

This will automatically detect and configure the new model.

## Troubleshooting

### Models Not Detected

1. **Check Ollama is running**:
   ```bash
   ollama list
   ```

2. **Check Ollama API**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. **Restart Ollama service**:
   ```bash
   # Windows
   net stop ollama
   net start ollama
   ```

### Model Not Found Errors

If you see "Model 'X' not found" errors:

1. **Verify model exists**:
   ```bash
   ollama list
   ```

2. **Update OLLAMA_MODEL** in `.env`:
   ```env
   OLLAMA_MODEL=<actual-model-name>
   ```

3. **Restart the backend**:
   ```bash
   # Restart uvicorn
   ```

### Performance Issues

- **Use smaller models** for faster responses (qwen3:4b)
- **Use larger models** for better quality (deepseek-r1:8b)
- **Check system resources** (CPU, RAM, GPU)

## Configuration Files

### local_ai_models.json

Automatically generated configuration file:

```json
{
  "ollama": {
    "available": true,
    "base_url": "http://localhost:11434/v1",
    "models": [
      "deepseek-r1:8b",
      "qwen3:4b",
      "mistral:latest"
    ],
    "preferred_model": "deepseek-r1:8b"
  }
}
```

### .env

Environment variables for model configuration:

```env
OLLAMA_MODEL=deepseek-r1:8b
OLLAMA_BASE_URL=http://localhost:11434/v1
```

## Best Practices

1. **Use appropriate model for task**:
   - Security/Code: `deepseek-r1:8b`
   - Quick tasks: `qwen3:4b`
   - General: `mistral:latest`

2. **Monitor resource usage**:
   - Larger models use more RAM/GPU
   - Multiple concurrent requests may slow down

3. **Keep models updated**:
   - Regularly pull latest model versions
   - Run setup script after updates

4. **Test before production**:
   - Use Testing Dashboard to verify models
   - Test with sample prompts
   - Monitor response quality

## Integration with Cloud Providers

Local models are used as **fallback** when:
- Cloud providers are unavailable
- API keys are not configured
- Rate limits are exceeded
- Cost optimization is needed

Priority order:
1. Cloud providers (if API keys configured)
2. Local models (Ollama/LocalAI)
3. Error (if no providers available)

## Support

For issues or questions:
- Check `docs/RUNNING_SERVICES.md` for service setup
- Review `scripts/setup_local_ai_models.py` for detection logic
- Check backend logs for model selection details

