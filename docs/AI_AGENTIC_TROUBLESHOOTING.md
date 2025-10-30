# 🔧 AI Agentic Workflow Troubleshooting Guide

## 🎯 **Comprehensive Problem Resolution**

This troubleshooting guide provides solutions for common issues, errors, and problems that may occur when using the AI Agentic Workflow System. Learn how to diagnose, resolve, and prevent issues for maximum system reliability and performance.

---

## 🚨 **Common Issues and Solutions**

### **1. Workflow Execution Issues**

#### **Issue: Workflow Fails to Start**
**Symptoms**:
- Workflow shows "Queued" status indefinitely
- No workflow runs appear in GitHub Actions
- Error: "Workflow not found"

**Causes**:
- Invalid workflow file syntax
- Missing required permissions
- Incorrect workflow file path
- GitHub Actions disabled

**Solutions**:
```bash
# 1. Check workflow file syntax
gh workflow list
gh workflow view 00-master-ai-orchestrator.yml

# 2. Verify GitHub Actions is enabled
# Go to repository Settings → Actions → General
# Ensure "Allow all actions and reusable workflows" is selected

# 3. Check workflow file permissions
ls -la .github/workflows/
chmod +x .github/workflows/*.yml

# 4. Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/00-master-ai-orchestrator.yml'))"
```

#### **Issue: Workflow Times Out**
**Symptoms**:
- Workflow runs but exceeds timeout limit
- Error: "The job has exceeded the maximum time limit"
- Workflow shows "Cancelled" status

**Causes**:
- Complex operations taking too long
- Network timeouts
- Resource limitations
- Infinite loops in scripts

**Solutions**:
```yaml
# 1. Increase timeout in workflow file
jobs:
  ai_workflow:
    runs-on: ubuntu-latest
    timeout-minutes: 60  # Increase from default 6 hours

# 2. Optimize workflow steps
- name: Optimized Step
  run: |
    # Use parallel processing
    python script.py --parallel --workers 4
    
    # Cache dependencies
    pip install --cache-dir .pip-cache -r requirements.txt
```

#### **Issue: Workflow Fails with Exit Code**
**Symptoms**:
- Workflow shows "Failed" status
- Error: "Process completed with exit code 1"
- Specific step fails

**Causes**:
- Script errors
- Missing dependencies
- Permission issues
- Invalid configuration

**Solutions**:
```bash
# 1. Check workflow logs
gh run view --log

# 2. Add error handling to scripts
set -e  # Exit on any error
set -o pipefail  # Exit on pipe errors

# 3. Debug specific steps
- name: Debug Step
  run: |
    echo "Debug information:"
    echo "Python version: $(python --version)"
    echo "Working directory: $(pwd)"
    echo "Environment variables:"
    env | grep -E "(AI_|GITHUB_)"
```

### **2. AI Provider Issues**

#### **Issue: AI Provider Authentication Fails**
**Symptoms**:
- Error: "Invalid API key"
- Error: "Authentication failed"
- AI provider returns 401/403 errors

**Causes**:
- Invalid or expired API keys
- Incorrect API key format
- Missing API keys in GitHub Secrets
- API key permissions insufficient

**Solutions**:
```bash
# 1. Verify API keys in GitHub Secrets
gh secret list

# 2. Check API key format
echo $DEEPSEEK_API_KEY | wc -c  # Should be reasonable length

# 3. Test API key manually
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     https://api.deepseek.com/v1/models

# 4. Regenerate API keys if needed
# Go to provider dashboard and generate new keys
```

#### **Issue: AI Provider Rate Limiting**
**Symptoms**:
- Error: "Rate limit exceeded"
- Error: "Too many requests"
- AI provider returns 429 errors

**Causes**:
- Exceeding API rate limits
- Too many concurrent requests
- Insufficient API quota

**Solutions**:
```python
# 1. Implement rate limiting
import time
import random

def rate_limited_request(func, *args, **kwargs):
    """Add rate limiting to API requests"""
    time.sleep(random.uniform(0.1, 0.5))  # Random delay
    return func(*args, **kwargs)

# 2. Use exponential backoff
def exponential_backoff_retry(func, max_retries=3):
    """Retry with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise e
```

#### **Issue: AI Provider Unavailable**
**Symptoms**:
- Error: "Service unavailable"
- Error: "Connection timeout"
- AI provider returns 5xx errors

**Causes**:
- Provider service down
- Network connectivity issues
- Provider maintenance

**Solutions**:
```python
# 1. Implement failover logic
class AIProviderManager:
    def __init__(self):
        self.providers = [
            "deepseek", "claude", "gpt4", "glm", "grok",
            "kimi", "qwen", "gemini", "gptoss", "groqai",
            "cerebras", "geminiai", "cohere", "nvidia",
            "codestral", "gemini2", "groq2", "chutes"
        ]
        self.current_provider = 0
    
    def get_response(self, prompt):
        """Get response with automatic failover"""
        for attempt in range(len(self.providers)):
            try:
                provider = self.providers[self.current_provider]
                return self.call_provider(provider, prompt)
            except Exception as e:
                print(f"Provider {provider} failed: {e}")
                self.current_provider = (self.current_provider + 1) % len(self.providers)
        
        raise Exception("All AI providers failed")
```

### **3. Dependency and Environment Issues**

#### **Issue: Python Dependencies Fail to Install**
**Symptoms**:
- Error: "No module named 'requests'"
- Error: "Failed to install package"
- Import errors in scripts

**Causes**:
- Missing requirements.txt
- Version conflicts
- Platform-specific dependencies
- Network connectivity issues

**Solutions**:
```bash
# 1. Create comprehensive requirements.txt
cat > requirements.txt << EOF
requests>=2.31.0
aiohttp>=3.8.5
openai>=1.3.0
anthropic>=0.7.0
google-generativeai>=0.3.0
groq>=0.4.0
cohere>=4.37
gitpython>=3.1.32
pygit2>=1.12.2
flake8>=6.0.0
bandit>=1.7.5
pytest>=7.4.0
docker>=6.1.3
kubernetes>=28.1.0
boto3>=1.28.0
azure-mgmt-resource>=23.0.0
google-cloud-storage>=2.10.0
cryptography>=41.0.4
pycryptodome>=3.18.0
scapy>=2.5.0
yara-python>=4.3.1
black>=23.7.0
isort>=5.12.0
mypy>=1.5.1
pylint>=2.17.5
EOF

# 2. Use binary wheels to avoid compilation
pip install --prefer-binary -r requirements.txt

# 3. Install with fallback
pip install -r requirements.txt || pip install --no-deps -r requirements.txt
```

#### **Issue: Environment Variables Not Set**
**Symptoms**:
- Error: "Environment variable not found"
- Scripts fail with undefined variables
- Configuration not loaded

**Causes**:
- Missing environment variables
- Incorrect variable names
- Variables not exported
- Scope issues

**Solutions**:
```bash
# 1. Check environment variables
env | grep -E "(AI_|GITHUB_)"

# 2. Set variables explicitly
export DEEPSEEK_API_KEY="your_key_here"
export CLAUDE_API_KEY="your_key_here"

# 3. Use default values in scripts
API_KEY=${DEEPSEEK_API_KEY:-"default_key"}
MODE=${ORCHESTRATION_MODE:-"intelligent"}

# 4. Validate required variables
required_vars=("DEEPSEEK_API_KEY" "CLAUDE_API_KEY" "GITHUB_TOKEN")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set"
        exit 1
    fi
done
```

### **4. GitHub Integration Issues**

#### **Issue: GitHub API Rate Limiting**
**Symptoms**:
- Error: "API rate limit exceeded"
- Error: "Too many requests"
- GitHub API returns 403 errors

**Causes**:
- Exceeding GitHub API rate limits
- Too many concurrent requests
- Unauthenticated requests

**Solutions**:
```python
# 1. Implement GitHub API rate limiting
import time
from github import Github

class RateLimitedGitHub:
    def __init__(self, token):
        self.github = Github(token)
        self.last_request = 0
        self.min_interval = 0.1  # 100ms between requests
    
    def make_request(self, func, *args, **kwargs):
        """Make rate-limited GitHub API request"""
        now = time.time()
        time_since_last = now - self.last_request
        
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        
        self.last_request = time.time()
        return func(*args, **kwargs)

# 2. Use GitHub CLI for better rate limits
gh api repos/owner/repo/actions/workflows
```

#### **Issue: GitHub Token Permissions**
**Symptoms**:
- Error: "Insufficient permissions"
- Error: "Forbidden"
- GitHub API returns 403 errors

**Causes**:
- Token lacks required permissions
- Token expired
- Repository access denied

**Solutions**:
```bash
# 1. Check token permissions
gh auth status

# 2. Refresh token
gh auth refresh

# 3. Check repository permissions
gh repo view owner/repo --json permissions

# 4. Use fine-grained personal access token
# Go to GitHub Settings → Developer settings → Personal access tokens
# Create token with required permissions:
# - repo (full control)
# - workflow (update GitHub Action workflows)
# - write:packages (write packages)
```

### **5. Performance Issues**

#### **Issue: Slow Workflow Execution**
**Symptoms**:
- Workflows take too long to complete
- Timeout errors
- Resource exhaustion

**Causes**:
- Inefficient scripts
- Large file processing
- Network latency
- Resource constraints

**Solutions**:
```python
# 1. Optimize Python scripts
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

def process_files_parallel(files):
    """Process files in parallel"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_file, files))
    return results

# 2. Use caching
import functools

@functools.lru_cache(maxsize=128)
def expensive_function(param):
    """Cache expensive function results"""
    return complex_calculation(param)

# 3. Optimize API calls
import asyncio
import aiohttp

async def make_async_requests(urls):
    """Make multiple API requests concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
    return responses
```

#### **Issue: Memory Usage Too High**
**Symptoms**:
- Workflow fails with out of memory
- System becomes unresponsive
- GitHub Actions runner issues

**Causes**:
- Large data processing
- Memory leaks
- Inefficient data structures
- Too many concurrent processes

**Solutions**:
```python
# 1. Use generators for large datasets
def process_large_file(filename):
    """Process large file line by line"""
    with open(filename, 'r') as f:
        for line in f:
            yield process_line(line)

# 2. Clear memory periodically
import gc

def process_with_cleanup(data):
    """Process data with memory cleanup"""
    result = process_data(data)
    del data  # Explicitly delete large objects
    gc.collect()  # Force garbage collection
    return result

# 3. Use streaming for large files
import json

def process_json_stream(filename):
    """Process large JSON file as stream"""
    with open(filename, 'r') as f:
        for line in f:
            data = json.loads(line)
            yield process_item(data)
```

---

## 🔍 **Debugging Techniques**

### **1. Enable Debug Mode**
```yaml
# In workflow file
env:
  DEBUG_MODE: true
  LOG_LEVEL: debug
  VERBOSE: true

# In scripts
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_function():
    logger.debug("Debug information")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

### **2. Add Comprehensive Logging**
```python
import logging
import traceback
from datetime import datetime

class WorkflowLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create file handler
        handler = logging.FileHandler(f'workflow_{name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def log_step(self, step_name, success=True, details=None):
        """Log workflow step execution"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Step '{step_name}' {status}"
        
        if details:
            message += f" - {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_error(self, error, context=None):
        """Log error with context"""
        error_msg = f"Error: {str(error)}"
        if context:
            error_msg += f" - Context: {context}"
        
        self.logger.error(error_msg)
        self.logger.error(f"Traceback: {traceback.format_exc()}")
```

### **3. Use GitHub Actions Debugging**
```yaml
# Add debug steps to workflow
- name: Debug Environment
  run: |
    echo "=== Environment Debug ==="
    echo "Python version: $(python --version)"
    echo "Working directory: $(pwd)"
    echo "Available disk space: $(df -h)"
    echo "Memory usage: $(free -h)"
    echo "Environment variables:"
    env | grep -E "(AI_|GITHUB_)" | sort

- name: Debug Dependencies
  run: |
    echo "=== Dependencies Debug ==="
    echo "Installed packages:"
    pip list
    echo "Python path:"
    python -c "import sys; print('\n'.join(sys.path))"

- name: Debug Scripts
  run: |
    echo "=== Scripts Debug ==="
    echo "Script files:"
    find .github/scripts -name "*.py" -exec ls -la {} \;
    echo "Script permissions:"
    find .github/scripts -name "*.py" -exec ls -la {} \;
```

---

## 🛠️ **Prevention Strategies**

### **1. Implement Health Checks**
```python
class WorkflowHealthChecker:
    def __init__(self):
        self.checks = []
    
    def add_check(self, name, check_func):
        """Add health check"""
        self.checks.append((name, check_func))
    
    def run_checks(self):
        """Run all health checks"""
        results = {}
        for name, check_func in self.checks:
            try:
                result = check_func()
                results[name] = {"status": "PASS", "result": result}
            except Exception as e:
                results[name] = {"status": "FAIL", "error": str(e)}
        return results

# Example health checks
def check_api_keys():
    """Check if all required API keys are set"""
    required_keys = ["DEEPSEEK_API_KEY", "CLAUDE_API_KEY", "GITHUB_TOKEN"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        raise Exception(f"Missing API keys: {missing_keys}")
    return "All API keys present"

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = ["requests", "aiohttp", "openai", "anthropic"]
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        raise Exception(f"Missing packages: {missing_packages}")
    return "All dependencies present"
```

### **2. Use Configuration Validation**
```python
import yaml
from jsonschema import validate, ValidationError

class WorkflowConfigValidator:
    def __init__(self):
        self.schema = {
            "type": "object",
            "properties": {
                "orchestration_mode": {
                    "type": "string",
                    "enum": ["intelligent", "full_analysis", "emergency_response", 
                            "performance_optimization", "security_audit", "documentation_update"]
                },
                "target_components": {
                    "type": "string",
                    "pattern": "^(all|[a-zA-Z_,]+)$"
                },
                "priority_level": {
                    "type": "string",
                    "enum": ["low", "normal", "high", "critical"]
                }
            },
            "required": ["orchestration_mode", "priority_level"]
        }
    
    def validate_config(self, config):
        """Validate workflow configuration"""
        try:
            validate(instance=config, schema=self.schema)
            return True, "Configuration is valid"
        except ValidationError as e:
            return False, f"Configuration validation failed: {e.message}"
```

### **3. Implement Monitoring and Alerting**
```python
class WorkflowMonitor:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url
        self.metrics = {}
    
    def record_metric(self, name, value, timestamp=None):
        """Record workflow metric"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            "value": value,
            "timestamp": timestamp
        })
    
    def check_thresholds(self):
        """Check if metrics exceed thresholds"""
        alerts = []
        
        # Check success rate
        if "success_rate" in self.metrics:
            latest_rate = self.metrics["success_rate"][-1]["value"]
            if latest_rate < 0.95:  # 95% threshold
                alerts.append(f"Success rate below threshold: {latest_rate}")
        
        # Check response time
        if "response_time" in self.metrics:
            latest_time = self.metrics["response_time"][-1]["value"]
            if latest_time > 300:  # 5 minutes threshold
                alerts.append(f"Response time above threshold: {latest_time}")
        
        return alerts
    
    def send_alert(self, message):
        """Send alert notification"""
        if self.webhook_url:
            import requests
            requests.post(self.webhook_url, json={"text": message})
```

---

## 📞 **Getting Help**

### **1. Check Documentation**
- [AI Agentic Workflow Guide](AI_AGENTIC_WORKFLOW_GUIDE.md)
- [AI Agentic Workflow Showcase](AI_AGENTIC_WORKFLOW_SHOWCASE.md)
- [Integration Examples](AI_AGENTIC_INTEGRATION_EXAMPLES.md)

### **2. Review Logs**
```bash
# GitHub Actions logs
gh run view --log

# Local logs
tail -f workflow_*.log

# System logs
journalctl -u github-actions
```

### **3. Community Support**
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Discussions: [Join discussions](https://github.com/your-repo/discussions)
- Documentation: [Read the docs](https://your-repo.readthedocs.io)

### **4. Professional Support**
- Enterprise Support: [Contact support](mailto:support@your-company.com)
- Consulting Services: [Get help](https://your-company.com/consulting)
- Training: [Learn more](https://your-company.com/training)

---

## 🎯 **Quick Reference**

### **Common Commands**
```bash
# Check workflow status
gh run list
gh run view --log

# Trigger workflow manually
gh workflow run "Master Enhanced AI Orchestrator v3.0"

# Check secrets
gh secret list

# View workflow file
gh workflow view 00-master-ai-orchestrator.yml

# Debug mode
export DEBUG_MODE=true
export LOG_LEVEL=debug
```

### **Useful Environment Variables**
```bash
# Debug mode
export DEBUG_MODE=true
export LOG_LEVEL=debug
export VERBOSE=true

# API configuration
export DEEPSEEK_API_KEY="your_key"
export CLAUDE_API_KEY="your_key"
export GITHUB_TOKEN="your_token"

# Workflow configuration
export ORCHESTRATION_MODE="intelligent"
export TARGET_COMPONENTS="all"
export PRIORITY_LEVEL="normal"
```

### **Emergency Procedures**
```bash
# Stop all workflows
gh run cancel --all

# Disable workflows
gh workflow disable 00-master-ai-orchestrator.yml

# Emergency mode
export ORCHESTRATION_MODE="emergency_response"
export PRIORITY_LEVEL="critical"
```

---

## 🎉 **Conclusion**

This comprehensive troubleshooting guide provides solutions for common issues and best practices for maintaining the AI Agentic Workflow System. By following these guidelines, you can:

- **Diagnose and resolve** common workflow issues
- **Prevent problems** with proactive monitoring
- **Optimize performance** for better efficiency
- **Maintain reliability** with health checks and validation

**Keep your AI Agentic Workflow System running smoothly!** 🚀

---

*🎯 AI Agentic Workflow Troubleshooting Guide - Comprehensive Problem Resolution*