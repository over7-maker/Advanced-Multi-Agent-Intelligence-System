# AMAS AI Integration Guide

## 🤖 Multi-Provider AI Integration

This guide covers the complete integration of 6 AI providers into the AMAS (Advanced Multi-Agent Intelligence System) project with intelligent fallback mechanisms and automated development workflows.

## 🔑 API Keys Setup

### GitHub Secrets Configuration

Add the following secrets to your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add each of the following secrets:

```
DEEPSEEK_API_KEY = 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
GLM_API_KEY = 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
GROK_API_KEY = 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
KIMI_API_KEY = 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
QWEN_API_KEY = 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
GPTOSS_API_KEY = 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
```

### Local Development Setup

For local development, create a `.env` file in the project root:

```bash
# AI Provider API Keys
DEEPSEEK_API_KEY=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
GLM_API_KEY=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
GROK_API_KEY=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
KIMI_API_KEY=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
QWEN_API_KEY=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
GPTOSS_API_KEY=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
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Run the complete environment setup
python scripts/setup_environment.py

# Check environment only
python scripts/setup_environment.py --check-only
```

### 2. AI Integration Setup

```bash
# Test AI integration
python scripts/setup_ai_integration.py

# Validate providers only
python scripts/setup_ai_integration.py --validate-only

# Test capabilities only
python scripts/setup_ai_integration.py --test-only
```

### 3. AI-Powered Development

```bash
# Code analysis
python scripts/ai_code_analyzer.py --directory . --output analysis_report.md

# Code improvement
python scripts/ai_code_improver.py --directory . --output improved_code/ --improvement-type performance

# Test generation
python scripts/ai_test_generator.py --directory . --output tests/generated/

# Continuous development
python scripts/ai_continuous_developer.py --project-path . --mode full_analysis
```

## 🏗️ Architecture Overview

### AI Service Manager

The `AIServiceManager` provides:

- **Multi-Provider Support**: 6 AI providers with intelligent fallback
- **Rate Limiting**: Automatic rate limit management
- **Health Monitoring**: Real-time provider health tracking
- **Load Balancing**: Intelligent provider selection
- **Error Handling**: Robust error recovery mechanisms

### Provider Priority System

1. **DeepSeek V3.1** (Priority 1) - Best for general tasks
2. **GLM 4.5 Air** (Priority 2) - Good for coding tasks
3. **Grok 4 Fast** (Priority 3) - Fast responses
4. **Kimi K2** (Priority 4) - Specialized tasks
5. **Qwen3 Coder** (Priority 5) - Coding specialization
6. **GPT OSS 120B** (Priority 6) - Fallback option

### Fallback Mechanism

```python
# Automatic fallback when primary provider fails
response = await ai_service.generate_response(
    "Your prompt here",
    preferred_provider=AIProvider.DEEPSEEK  # Optional
)
```

## 🔧 GitHub Actions Integration

### Automated AI Development Workflow

The project includes a comprehensive GitHub Actions workflow (`.github/workflows/ai_development.yml`) that provides:

#### Available Workflow Triggers

1. **Code Analysis** - Automatic code quality analysis on push/PR
2. **Code Improvement** - AI-powered code improvements
3. **Test Generation** - Automated test generation
4. **Documentation** - AI-generated documentation
5. **Security Audit** - Security vulnerability analysis
6. **Performance Optimization** - Performance improvement suggestions

#### Manual Workflow Dispatch

```bash
# Trigger manual workflow
gh workflow run ai_development.yml -f task_type=code_improvement -f target_files="main.py,services/"
```

#### Workflow Features

- **Multi-Provider AI**: Uses all 6 AI providers for maximum reliability
- **Automatic PR Creation**: Creates pull requests with AI improvements
- **Comprehensive Reports**: Generates detailed analysis reports
- **Artifact Storage**: Saves all generated content as artifacts

## 📊 AI Capabilities

### Code Generation

```python
# Generate code using AI
response = await ai_service.generate_code(
    task_description="Create a REST API endpoint",
    language="python"
)
```

### Code Analysis

```python
# Analyze code quality
response = await ai_service.analyze_code(
    code="your code here",
    language="python"
)
```

### Code Improvement

```python
# Improve existing code
response = await ai_service.improve_code(
    code="your code here",
    language="python",
    improvement_type="performance"
)
```

### Test Generation

```python
# Generate comprehensive tests
response = await ai_service.generate_tests(
    code="your code here",
    language="python"
)
```

## 🔍 Monitoring and Health Checks

### Provider Health Monitoring

```python
# Check provider health
health_status = await ai_service.health_check()
print(f"Overall health: {health_status['overall_health']}")

# Get provider statistics
stats = ai_service.get_provider_stats()
for provider, data in stats.items():
    print(f"{provider}: {data['health_score']}% health")
```

### Real-time Monitoring

- **Health Scores**: 0-100% health score for each provider
- **Response Times**: Average response time tracking
- **Success Rates**: Request success rate monitoring
- **Rate Limiting**: Automatic rate limit management
- **Error Tracking**: Comprehensive error logging

## 🛠️ Development Tools

### AI Code Analyzer

```bash
# Analyze specific files
python scripts/ai_code_analyzer.py --files main.py services/ai_service_manager.py

# Analyze entire directory
python scripts/ai_code_analyzer.py --directory . --extensions .py .js .ts

# Generate analysis report
python scripts/ai_code_analyzer.py --mode analysis --output analysis_report.md
```

### AI Code Improver

```bash
# Improve specific files
python scripts/ai_code_improver.py --files main.py --improvement-type performance

# Improve entire directory
python scripts/ai_code_improver.py --directory . --output improved_code/ --improvement-type security

# Generate improvement report
python scripts/ai_code_improver.py --report improvement_report.json
```

### AI Test Generator

```bash
# Generate tests for specific files
python scripts/ai_test_generator.py --files main.py services/ai_service_manager.py

# Generate tests for entire directory
python scripts/ai_test_generator.py --directory . --output tests/generated/

# Generate comprehensive test suite
python scripts/ai_test_generator.py --test-type comprehensive --report test_generation_report.json
```

### AI Continuous Developer

```bash
# Full project analysis
python scripts/ai_continuous_developer.py --project-path . --mode full_analysis

# Quality analysis only
python scripts/ai_continuous_developer.py --mode quality_only

# Security analysis only
python scripts/ai_continuous_developer.py --mode security_only
```

## 📈 Performance Optimization

### Provider Selection Strategy

1. **Priority-Based**: Higher priority providers are tried first
2. **Health-Based**: Providers with better health scores are preferred
3. **Performance-Based**: Faster providers are selected when available
4. **Load Balancing**: Distribute requests across healthy providers

### Rate Limiting

- **Per-Provider Limits**: Each provider has its own rate limit
- **Automatic Throttling**: Requests are throttled when limits are reached
- **Queue Management**: Requests are queued when all providers are at limit
- **Recovery**: Automatic recovery when rate limits reset

## 🔒 Security Features

### API Key Management

- **Environment Variables**: All API keys stored in environment variables
- **GitHub Secrets**: Secure storage in GitHub repository secrets
- **No Hardcoding**: No API keys in source code
- **Rotation Support**: Easy API key rotation

### Request Security

- **HTTPS Only**: All requests use HTTPS
- **Timeout Protection**: Request timeouts prevent hanging
- **Error Handling**: Comprehensive error handling and logging
- **Audit Trail**: Complete request/response logging

## 📝 Usage Examples

### Basic AI Request

```python
from services.ai_service_manager import AIServiceManager

# Initialize AI service
ai_service = AIServiceManager(config)
await ai_service.initialize()

# Generate response
response = await ai_service.generate_response("Explain quantum computing")
print(response.content)
```

### Code Generation

```python
# Generate Python code
response = await ai_service.generate_code(
    "Create a function to calculate Fibonacci numbers",
    "python"
)
print(response.content)
```

### Code Analysis

```python
# Analyze code quality
code = """
def calculate_factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    return n * calculate_factorial(n-1)
"""

response = await ai_service.analyze_code(code, "python")
print(response.content)
```

### Code Improvement

```python
# Improve code performance
response = await ai_service.improve_code(
    code,
    "python",
    "performance"
)
print(response.content)
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```bash
   # Check if API keys are set
   echo $DEEPSEEK_API_KEY
   ```

2. **Provider Not Responding**
   ```bash
   # Check provider health
   python scripts/setup_ai_integration.py --validate-only
   ```

3. **Rate Limit Exceeded**
   ```bash
   # Wait for rate limit reset (usually 1 minute)
   # Or use a different provider
   ```

4. **Network Issues**
   ```bash
   # Check internet connectivity
   ping openrouter.ai
   ```

### Debug Mode

```bash
# Enable debug logging
export AMAS_LOG_LEVEL=DEBUG
python scripts/ai_code_analyzer.py --files main.py
```

## 📚 API Reference

### AIServiceManager

```python
class AIServiceManager:
    async def generate_response(self, prompt: str, **kwargs) -> AIResponse
    async def generate_code(self, task: str, language: str) -> AIResponse
    async def analyze_code(self, code: str, language: str) -> AIResponse
    async def improve_code(self, code: str, language: str, improvement_type: str) -> AIResponse
    async def generate_tests(self, code: str, language: str) -> AIResponse
    async def health_check(self) -> Dict[str, Any]
    def get_provider_stats(self) -> Dict[str, Any]
```

### AIResponse

```python
@dataclass
class AIResponse:
    content: str
    provider: str
    model: str
    tokens_used: int
    response_time: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None
```

## 🎯 Best Practices

### 1. Provider Selection

- Use specific providers for specific tasks
- Monitor provider health scores
- Implement fallback strategies

### 2. Rate Limiting

- Respect provider rate limits
- Implement request queuing
- Monitor usage patterns

### 3. Error Handling

- Always check response.success
- Implement retry logic
- Log errors for debugging

### 4. Performance

- Cache responses when appropriate
- Use appropriate timeouts
- Monitor response times

## 🔄 Continuous Integration

### Automated Workflows

1. **Code Quality**: Automatic code analysis on every commit
2. **Security Scanning**: Regular security vulnerability checks
3. **Performance Monitoring**: Continuous performance optimization
4. **Documentation**: Auto-generated documentation updates
5. **Testing**: Comprehensive test generation and execution

### Manual Triggers

- **Code Improvement**: Manual code improvement requests
- **Test Generation**: On-demand test generation
- **Documentation**: Manual documentation updates
- **Security Audit**: Regular security assessments

## 📊 Metrics and Monitoring

### Key Metrics

- **Provider Health**: 0-100% health score
- **Response Time**: Average response time per provider
- **Success Rate**: Request success rate
- **Token Usage**: Token consumption tracking
- **Error Rate**: Error frequency monitoring

### Monitoring Dashboard

```python
# Get comprehensive metrics
stats = ai_service.get_provider_stats()
health = await ai_service.health_check()

print(f"Overall Health: {health['overall_health']}")
print(f"Active Providers: {len([p for p in stats.values() if p['enabled']])}")
```

## 🎉 Conclusion

The AMAS AI Integration provides a robust, scalable, and intelligent system for AI-powered development. With 6 providers, intelligent fallback, and comprehensive monitoring, it ensures maximum reliability and performance for all AI operations.

For more information, see the individual script documentation and the main project README.