# AMAS AI API Manager - Comprehensive Guide

## Overview

The AMAS AI API Manager is a robust, intelligent system that provides seamless integration with 16 different AI providers, ensuring maximum reliability through automatic fallback mechanisms. This system is designed to eliminate single points of failure and provide consistent AI-powered intelligence operations.

## Supported AI Providers

| Provider | API Key Environment Variable | Capabilities | Priority |
|----------|----------------------------|--------------|----------|
| Cerebras | `CEREBRAS_API_KEY` | Reasoning, Code Generation, Analysis | 1 |
| Codestral | `CODESTRAL_API_KEY` | Code Analysis, Vulnerability Detection | 2 |
| DeepSeek | `DEEPSEEK_API_KEY` | Reasoning, Analysis, Code Generation | 3 |
| Gemini AI | `GEMINIAI_API_KEY` | Reasoning, Analysis, Multimodal | 4 |
| GLM | `GLM_API_KEY` | Reasoning, Analysis, Code Generation | 5 |
| GPTOSS | `GPTOSS_API_KEY` | Reasoning, Analysis, Code Generation | 6 |
| Grok | `GROK_API_KEY` | Reasoning, Analysis, Synthesis | 7 |
| GroqAI | `GROQAI_API_KEY` | Fast Inference, Reasoning, Analysis | 8 |
| Kimi | `KIMI_API_KEY` | Reasoning, Analysis, Chinese Support | 9 |
| NVIDIA | `NVIDIA_API_KEY` | Reasoning, Code Generation, Analysis | 10 |
| Qwen | `QWEN_API_KEY` | Reasoning, Analysis, Chinese Support | 11 |
| Gemini2 | `GEMINI2_API_KEY` | Reasoning, Analysis, Multimodal | 12 |
| NVIDIA2 | `NVIDIA_API_KEY` | Code Generation, Analysis, Technical | 13 |
| Groq2 | `GROQ2_API_KEY` | Fast Inference, Reasoning, Analysis | 14 |
| Cohere | `COHERE_API_KEY` | Reasoning, Analysis, Text Generation | 15 |
| Chutes | `CHUTES_API_KEY` | Reasoning, Analysis, Code Generation | 16 |

## Key Features

### 🚀 Automatic Fallback
- **Intelligent API Selection**: Automatically selects the best API based on task type and availability
- **Seamless Failover**: If one API fails, automatically tries the next available API
- **Health Monitoring**: Continuously monitors API health and performance
- **Rate Limit Handling**: Automatically handles rate limits and quota restrictions

### 🎯 Task-Specific Optimization
- **OSINT Tasks**: Optimized for data gathering and source validation
- **Code Analysis**: Specialized for vulnerability detection and technical assessment
- **Threat Analysis**: Enhanced for pattern recognition and threat assessment
- **Report Generation**: Optimized for synthesis and documentation

### 📊 Performance Monitoring
- **Real-time Health Checks**: Continuous monitoring of all API endpoints
- **Performance Metrics**: Response times, success rates, and error tracking
- **Usage Analytics**: Detailed statistics on API usage and performance
- **Cost Optimization**: Intelligent API selection based on cost and performance

## Quick Start

### 1. Environment Setup

```bash
# Set your API keys
export CEREBRAS_API_KEY="your_cerebras_key"
export CODESTRAL_API_KEY="your_codestral_key"
export DEEPSEEK_API_KEY="your_deepseek_key"
export GEMINIAI_API_KEY="your_gemini_key"
export GLM_API_KEY="your_glm_key"
export GPTOSS_API_KEY="your_gptoss_key"
export GROK_API_KEY="your_grok_key"
export GROQAI_API_KEY="your_groqai_key"
export KIMI_API_KEY="your_kimi_key"
export NVIDIA_API_KEY="your_nvidia_key"
export QWEN_API_KEY="your_qwen_key"
export GEMINI2_API_KEY="your_gemini2_key"
export GROQ2_API_KEY="your_groq2_key"
export COHERE_API_KEY="your_cohere_key"
export CHUTES_API_KEY="your_chutes_key"
```

### 2. Basic Usage

```python
import asyncio
from amas.core.ai_api_manager import get_ai_response

async def main():
    # Simple AI request with automatic fallback
    response = await get_ai_response(
        prompt="Explain artificial intelligence in one paragraph.",
        system_prompt="You are a helpful AI assistant.",
        max_tokens=200,
        temperature=0.7
    )
    
    print(f"Response: {response['content']}")
    print(f"API used: {response['api_used']}")

asyncio.run(main())
```

### 3. Task-Specific Usage

```python
import asyncio
from amas.core.enhanced_orchestrator import execute_task

async def main():
    # OSINT task with specialized agent
    result = await execute_task(
        task_id="osint_001",
        task_type="osint",
        prompt="Collect intelligence on recent cybersecurity threats.",
        agent_type="osint_agent"
    )
    
    print(f"Success: {result.success}")
    print(f"API used: {result.api_used}")
    print(f"Result: {result.result}")

asyncio.run(main())
```

## Advanced Usage

### 1. Comprehensive Investigation Workflow

```python
import asyncio
from amas.core.enhanced_orchestrator import run_investigation

async def main():
    # Run comprehensive investigation
    investigation = await run_investigation(
        topic="Advanced Persistent Threats targeting software supply chains",
        investigation_type="comprehensive"
    )
    
    print(f"Investigation completed: {len(investigation['phases'])} phases")
    print(f"Final report: {investigation['final_report']}")

asyncio.run(main())
```

### 2. Parallel Task Processing

```python
import asyncio
from amas.core.enhanced_orchestrator import EnhancedOrchestrator

async def main():
    orchestrator = EnhancedOrchestrator()
    
    # Create multiple tasks
    tasks = [
        {
            'task_id': f'parallel_task_{i}',
            'task_type': 'analysis',
            'prompt': f'Analyze threat vector {i} and provide recommendations.',
            'agent_type': 'analysis_agent'
        }
        for i in range(5)
    ]
    
    # Execute tasks in parallel
    results = await orchestrator.execute_parallel_tasks(tasks, max_concurrent=3)
    
    print(f"Completed: {len([r for r in results if r.success])}/{len(results)}")

asyncio.run(main())
```

### 3. Health Monitoring

```python
import asyncio
from amas.core.ai_api_manager import AIAPIManager

async def main():
    api_manager = AIAPIManager()
    
    # Get health status
    health = api_manager.get_health_status()
    print(f"Healthy APIs: {health['healthy_apis']}/{health['total_apis']}")
    
    # Perform health check
    health_results = await api_manager.health_check()
    for api_name, result in health_results.items():
        print(f"{api_name}: {result['status']}")

asyncio.run(main())
```

## API Reference

### Core Classes

#### `AIAPIManager`
The main API manager class that handles all AI provider interactions.

**Methods:**
- `generate_response(prompt, system_prompt=None, task_type=None, **kwargs)`: Generate AI response
- `generate_streaming_response(prompt, system_prompt=None, task_type=None, **kwargs)`: Generate streaming response
- `get_health_status()`: Get comprehensive health status
- `health_check()`: Perform health check on all APIs
- `reset_api_health(api_name=None)`: Reset health status

#### `EnhancedOrchestrator`
Enhanced orchestrator with intelligent task routing and fallback mechanisms.

**Methods:**
- `execute_task(task_id, task_type, prompt, **kwargs)`: Execute single task
- `execute_parallel_tasks(tasks, max_concurrent=5)`: Execute multiple tasks in parallel
- `run_investigation_workflow(topic, investigation_type="comprehensive")`: Run investigation workflow
- `get_performance_stats()`: Get performance statistics

### Configuration

#### API Configuration
Each API can be configured with the following parameters:

```python
@dataclass
class APIConfig:
    name: str                    # API name
    api_key: str                 # API key
    base_url: str                # Base URL
    model: str                   # Model name
    api_type: APIType           # API type
    max_tokens: int = 4000      # Maximum tokens
    temperature: float = 0.7    # Temperature
    timeout: int = 30           # Timeout in seconds
    retry_attempts: int = 3     # Retry attempts
    priority: int = 1           # Priority (lower = higher priority)
    capabilities: List[str]     # Task capabilities
    cost_per_token: float = 0.0 # Cost per token
    rate_limit_per_minute: int = 60  # Rate limit
```

#### Health Monitoring
The system continuously monitors API health with the following metrics:

```python
@dataclass
class APIHealth:
    is_healthy: bool = True                    # Health status
    last_success: Optional[datetime] = None   # Last successful request
    last_failure: Optional[datetime] = None   # Last failed request
    consecutive_failures: int = 0             # Consecutive failures
    total_requests: int = 0                   # Total requests
    successful_requests: int = 0              # Successful requests
    average_response_time: float = 0.0        # Average response time
    error_rate: float = 0.0                  # Error rate
    quota_remaining: Optional[int] = None     # Quota remaining
    rate_limit_until: Optional[datetime] = None  # Rate limit until
```

## Error Handling

### Automatic Fallback
The system automatically handles various error conditions:

1. **API Unavailable**: Automatically switches to next available API
2. **Rate Limiting**: Waits for rate limit to reset and tries again
3. **Quota Exceeded**: Switches to alternative API
4. **Network Errors**: Retries with exponential backoff
5. **Timeout Errors**: Tries next API in priority order

### Error Recovery
- **Exponential Backoff**: Automatic retry with increasing delays
- **Circuit Breaker**: Temporarily disables failing APIs
- **Health Recovery**: Automatic re-enabling of recovered APIs
- **Graceful Degradation**: Continues operation with available APIs

## Performance Optimization

### Intelligent API Selection
The system selects APIs based on:

1. **Task Type**: Matches task requirements with API capabilities
2. **Performance**: Considers response time and success rate
3. **Cost**: Optimizes for cost-effectiveness
4. **Availability**: Prioritizes healthy APIs
5. **Rate Limits**: Avoids rate-limited APIs

### Caching and Optimization
- **Response Caching**: Caches similar requests
- **Connection Pooling**: Reuses HTTP connections
- **Batch Processing**: Groups similar requests
- **Load Balancing**: Distributes load across APIs

## Monitoring and Analytics

### Health Dashboard
```python
# Get comprehensive health status
health = api_manager.get_health_status()
print(f"Total APIs: {health['total_apis']}")
print(f"Healthy APIs: {health['healthy_apis']}")
print(f"Unhealthy APIs: {health['unhealthy_apis']}")
print(f"Rate Limited APIs: {health['rate_limited_apis']}")
```

### Performance Metrics
```python
# Get performance statistics
stats = orchestrator.get_performance_stats()
print(f"Success Rate: {stats['success_rate']:.1f}%")
print(f"Average Execution Time: {stats['average_execution_time']:.2f}s")
print(f"API Usage: {stats['api_usage']}")
```

### Task Analytics
```python
# Get task type statistics
for task_type, stats in stats['task_type_stats'].items():
    success_rate = (stats['successful'] / stats['total']) * 100
    print(f"{task_type}: {success_rate:.1f}% success rate")
```

## Best Practices

### 1. API Key Management
- Store API keys in environment variables
- Use different keys for different environments
- Rotate keys regularly
- Monitor usage and costs

### 2. Error Handling
- Always handle exceptions gracefully
- Implement proper logging
- Use fallback mechanisms
- Monitor error rates

### 3. Performance Optimization
- Use appropriate task types
- Implement caching where possible
- Monitor response times
- Optimize for cost-effectiveness

### 4. Security
- Never expose API keys in code
- Use secure key management
- Implement access controls
- Monitor for suspicious activity

## Troubleshooting

### Common Issues

#### 1. No APIs Available
```python
# Check API key configuration
health = api_manager.get_health_status()
if health['healthy_apis'] == 0:
    print("No healthy APIs available. Check API keys and configuration.")
```

#### 2. High Error Rates
```python
# Check individual API health
for api_name, status in health['apis'].items():
    if status['error_rate'] > 0.5:
        print(f"High error rate for {api_name}: {status['error_rate']:.1%}")
```

#### 3. Rate Limiting
```python
# Check for rate limits
for api_name, status in health['apis'].items():
    if status['rate_limited_until']:
        print(f"{api_name} is rate limited until {status['rate_limited_until']}")
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for detailed information
```

## Examples

See the `examples/api_manager_usage.py` file for comprehensive usage examples including:

- Basic API usage
- Task-specific API selection
- Health monitoring
- Parallel processing
- Investigation workflows
- Streaming responses
- Error handling
- Performance metrics
- Custom agent workflows
- API health checks

## Support

For support and questions:

1. Check the troubleshooting section
2. Review the examples
3. Check the test suite in `tests/test_api_manager.py`
4. Create an issue in the repository

## License

This project is licensed under the MIT License. See the LICENSE file for details.