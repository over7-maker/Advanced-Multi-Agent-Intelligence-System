# 🔐 AMAS Authentication Setup Guide

This guide will help you set up authentication for the AMAS multi-agent system to work properly.

## 📋 Current Status

The multi-agent PR generation system failed because:
- ❌ No valid API keys were configured
- ❌ All 8 agents failed with authentication errors (401)
- ❌ No actual analysis or improvements were generated

## 🚀 Quick Setup (5 minutes)

### Step 1: Get a Free OpenRouter API Key

1. Visit: https://openrouter.ai/keys
2. Sign up for a free account (GitHub/Google login available)
3. Click "Create API Key"
4. Copy your API key (it starts with `sk-or-...`)

### Step 2: Configure Your API Key

Update the `.env` file in the project root:

```bash
# Edit the .env file
OPENROUTER_API_KEY=sk-or-your-actual-key-here
```

### Step 3: Verify Authentication

Run the authentication test:

```bash
python3 test_simple_auth.py
```

You should see:
- ✓ Authentication successful
- ✓ AI providers working
- ✓ Simple agent test passing

## 🤖 Available AI Models (Free Tier)

AMAS uses these free AI models through OpenRouter:

1. **DeepSeek V3.1** - General purpose, good for analysis
2. **GLM 4.5 Air** - Fast responses, good for quick tasks
3. **Grok 4 Fast** - Efficient for code analysis
4. **Kimi K2** - Good for documentation
5. **Qwen3 Coder** - Specialized for code generation
6. **GPT OSS 120B** - Large model for complex tasks

## 🔧 Advanced Configuration

### Using Different API Keys per Model

If you want to use different API keys for each model:

```bash
# In .env file
DEEPSEEK_API_KEY=sk-or-key-for-deepseek
GLM_API_KEY=sk-or-key-for-glm
GROK_API_KEY=sk-or-key-for-grok
# ... etc
```

### Rate Limits and Usage

Free tier limits (per model):
- Requests: ~60 per minute
- Tokens: Varies by model
- Cost: FREE for all models listed

## 🎯 Next Steps After Authentication

Once authentication is working:

### 1. Create a Working Agent Test

```python
# Run a single agent successfully
python3 scripts/test_single_agent.py
```

### 2. Run Multi-Agent Analysis

```python
# Run the multi-agent orchestrator
python3 scripts/run_multi_agent_analysis.py
```

### 3. Generate a Valid PR

```python
# Create PR with actual improvements
python3 scripts/create_improvement_pr.py
```

## 🐛 Troubleshooting

### Authentication Still Failing?

1. **Check API Key Format**
   - Must start with `sk-or-`
   - No spaces or quotes around the key
   - Exact copy from OpenRouter dashboard

2. **Network Issues**
   - Ensure you can reach: https://openrouter.ai
   - Check firewall/proxy settings

3. **Environment Variables**
   ```bash
   # Verify environment variables are loaded
   python3 -c "import os; print(os.getenv('OPENROUTER_API_KEY'))"
   ```

### Common Errors

- **401 Authentication Error**: Invalid or missing API key
- **429 Rate Limit**: Too many requests, wait a minute
- **500 Server Error**: OpenRouter issue, try again later

## 📝 Example: Working Multi-Agent Configuration

Here's what a successful multi-agent run should produce:

```json
{
  "agents_used": [
    "code_analyst",
    "security_expert",
    "performance_optimizer"
  ],
  "improvements": {
    "code_quality": {
      "issues_found": 15,
      "suggestions": ["Add type hints", "Refactor long functions"],
      "agent": "code_analyst"
    },
    "security": {
      "vulnerabilities": 3,
      "fixes": ["Update dependencies", "Add input validation"],
      "agent": "security_expert"
    }
  }
}
```

## 🚀 Ready to Go!

After setting up authentication:

1. ✅ All agents will have valid API access
2. ✅ Multi-agent orchestration will work properly
3. ✅ PRs will contain actual improvements
4. ✅ The system will provide real value

## 📞 Need Help?

- Check the logs in `/workspace/logs/`
- Review error messages carefully
- Ensure all dependencies are installed
- Try the simple test first before complex operations

---

Remember: The key to success is having a valid OpenRouter API key configured in your `.env` file!