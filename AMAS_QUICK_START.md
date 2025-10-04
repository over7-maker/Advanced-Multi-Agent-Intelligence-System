# 🚀 AMAS Quick Start Guide

## 🔥 Get Started in 5 Minutes

### 1. **Check Your API Setup** (30 seconds)
```bash
python3 scripts/validate_api_config.py
```

### 2. **Test OpenRouter Connection** (1 minute)
```bash
python3 scripts/test_openrouter_direct.py
```

### 3. **Run Multi-Agent Demo** (3 minutes)
```bash
python3 scripts/run_unified_orchestrator.py
```

## 💻 Common Commands

### **Analyze Your Code**
```bash
# Quick code review
python3 -c "
import asyncio
from src.amas.core.unified_orchestrator import get_orchestrator, AgentRole

async def quick_review():
    o = get_orchestrator()
    task = await o.execute_task(
        'Code Review',
        'Review code quality in src/',
        [AgentRole.CODE_ANALYST]
    )
    print(task.results)

asyncio.run(quick_review())
"
```

### **Security Scan**
```bash
# Security vulnerability check
python3 -c "
import asyncio
from src.amas.core.unified_orchestrator import get_orchestrator, AgentRole

async def security_scan():
    o = get_orchestrator()
    task = await o.execute_task(
        'Security Scan',
        'Find security vulnerabilities',
        [AgentRole.SECURITY_EXPERT]
    )
    print(task.results)

asyncio.run(security_scan())
"
```

### **Generate Documentation**
```bash
# Auto-generate docs
python3 -c "
import asyncio
from src.amas.core.unified_orchestrator import get_orchestrator, AgentRole

async def gen_docs():
    o = get_orchestrator()
    task = await o.execute_task(
        'Generate Docs',
        'Create API documentation for main modules',
        [AgentRole.DOCUMENTATION_SPECIALIST]
    )
    print(task.results)

asyncio.run(gen_docs())
"
```

## 🛠️ Fix Common Issues

### **"No valid API keys found"**
```bash
# Add to .env file
echo 'DEEPSEEK_API_KEY=sk-or-v1-your-key-here' >> .env
```

### **"Rate limit exceeded"**
```bash
# Use different API key or wait
export OPENROUTER_API_KEY=sk-or-v1-backup-key
```

### **"Model not available"**
1. Visit https://openrouter.ai/settings/privacy
2. Enable "Zero data retention"
3. Try again

## 🎯 Use Cases

### **1. PR Review Automation**
```python
# Save as review_pr.py
import asyncio
from src.amas.core.unified_orchestrator import get_orchestrator, AgentRole

async def review_changes(file_path):
    orchestrator = get_orchestrator()
    
    with open(file_path, 'r') as f:
        code = f.read()
    
    task = await orchestrator.execute_task(
        title="Review Code Changes",
        description=f"Review this code: {code[:500]}...",
        required_agents=[
            AgentRole.CODE_ANALYST,
            AgentRole.SECURITY_EXPERT
        ]
    )
    
    for agent, result in task.results.items():
        print(f"\n{agent}:\n{result.get('response', 'No response')}")

# Run: python review_pr.py
asyncio.run(review_changes('path/to/file.py'))
```

### **2. Daily Code Health Check**
```bash
# Add to crontab
0 9 * * * cd /workspace && python3 scripts/run_unified_orchestrator.py > daily_report.log
```

### **3. Incident Response**
```python
# Save as respond_to_incident.py
import asyncio
from src.amas.core.unified_orchestrator import get_orchestrator, AgentRole

async def respond_to_incident(description):
    orchestrator = get_orchestrator()
    
    task = await orchestrator.execute_task(
        title="Security Incident Response",
        description=description,
        required_agents=[
            AgentRole.SECURITY_EXPERT,
            AgentRole.INCIDENT_RESPONDER,
            AgentRole.PROJECT_MANAGER
        ]
    )
    
    print("🚨 INCIDENT RESPONSE PLAN 🚨")
    for agent, result in task.results.items():
        print(f"\n{agent}:\n{result.get('response', 'No response')}")

# Usage
asyncio.run(respond_to_incident("Suspicious login attempts detected"))
```

## 📊 Monitor System Health

```bash
# Check agent status
python3 -c "
from src.amas.core.unified_orchestrator import get_orchestrator
o = get_orchestrator()
status = o.get_status()
print(f\"Agents: {status['orchestrator']['registered_agents']}\")
print(f\"Models: {status['ai_router']['available_models']}\")
"
```

## 🔗 Useful Resources

- **API Keys**: https://openrouter.ai/keys
- **Model Pricing**: https://openrouter.ai/models
- **AMAS Docs**: `/workspace/docs/`
- **Logs**: `/workspace/logs/`

## 💡 Remember

1. **Start small** - Test with one agent first
2. **Check costs** - Monitor OpenRouter usage
3. **Save results** - Agents generate valuable insights
4. **Iterate** - Refine prompts for better results

---

**Need help?** Check `AMAS_ACTION_PLAN.md` for detailed instructions! 🚀