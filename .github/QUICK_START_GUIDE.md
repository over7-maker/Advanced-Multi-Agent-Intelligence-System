# Quick Start Guide for PR #272
## 5-Minute Setup

**TL;DR**: Execute these commands to get AI Autonomy Initiative running in your repository.

---

## Prerequisites

- GitHub account with admin access to repo
- Node.js 18+
- 16 AI API keys (from OpenAI, Anthropic, Google, Meta, GitHub, etc.)

---

## Installation (5 Minutes)

### 1. Add API Keys to GitHub Secrets (2 min)

```bash
# Get your repository
REPO="https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System"
cd Advanced-Multi-Agent-Intelligence-System

# Add API keys (replace with your actual keys)
gh secret set OPENAI_API_KEY_1 --body "sk-your-key-here"
gh secret set OPENAI_API_KEY_2 --body "sk-your-key-here"
gh secret set OPENAI_API_KEY_3 --body "sk-your-key-here"
gh secret set CLAUDE_API_KEY_1 --body "sk-ant-your-key-here"
gh secret set CLAUDE_API_KEY_2 --body "sk-ant-your-key-here"
gh secret set CLAUDE_API_KEY_3 --body "sk-ant-your-key-here"
gh secret set GEMINI_API_KEY_1 --body "your-key-here"
gh secret set GEMINI_API_KEY_2 --body "your-key-here"
gh secret set LLAMA_API_KEY_1 --body "your-key-here"
gh secret set LLAMA_API_KEY_2 --body "your-key-here"
gh secret set GITHUB_COPILOT_KEY --body "your-key-here"
gh secret set GITHUB_MODELS_KEY --body "your-key-here"
gh secret set COHERE_API_KEY_1 --body "your-key-here"
gh secret set MISTRAL_API_KEY_1 --body "your-key-here"
gh secret set HUGGINGFACE_API_KEY --body "your-key-here"
gh secret set AZURE_OPENAI_KEY --body "your-key-here"

# Verify
gh secret list | grep -E "OPENAI|CLAUDE|GEMINI"
```

### 2. Pull Latest Code (1 min)

```bash
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System
git fetch origin pr-272-implementation
git checkout pr-272-implementation
```

### 3. Install Dependencies (1 min)

```bash
npm install
```

### 4. Test Locally (1 min)

```bash
# Test orchestrator
node .github/ai-agents/orchestrator-agent.js

# Output should show task analysis
```

---

## First Run

### Option A: Trigger via GitHub UI

```
1. Go to: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/actions
2. Select: "🤖 AI Multi-Agent Orchestrator"
3. Click: "Run workflow"
4. Select: pr-272-implementation branch
5. Click: "Run workflow"

✓ Workflow will execute in ~2-3 hours
```

### Option B: Trigger via CLI

```bash
gh workflow run 01-ai-orchestrator.yaml --ref pr-272-implementation

# Check status
gh run list --workflow 01-ai-orchestrator.yaml --limit 1

# View logs
gh run view <run-id> --log
```

### Option C: Trigger via Git Push

```bash
# Make a commit to trigger workflow
git commit --allow-empty -m "test: Trigger AI orchestrator"
git push origin pr-272-implementation

# Monitor
gh run watch
```

---

## What Happens Next

```
┌────────────────────────────────┐
│ Workflow Execution Timeline          │
├────────────────────────────────┤
│ Stage 1: Initialization (5 min)    │
│   ✓ Setup Node.js                  │
│   ✓ Initialize Orchestrator       │
│                                   │
│ Stage 2: Task Analysis (10 min)    │
│   ✓ Analyze requirements          │
│   ✓ Create execution plan         │
│                                   │
│ Stage 3: Code Generation (25 min)  │
│   ✓ Generate code                 │
│   ✓ Create documentation          │
│                                   │
│ Stage 4: Testing (30 min)          │
│   ✓ Run unit tests                │
│   ✓ Check coverage (>85%)        │
│   ✓ Security scan                 │
│                                   │
│ Stage 5: Code Review (15 min)      │
│   ✓ Quality analysis              │
│   ✓ Best practices check          │
│   ✓ Performance review            │
│                                   │
│ Stage 6: Deployment (25 min)       │
│   ✓ Pre-deployment checks         │
│   ✓ Canary deployment (5%)        │
│   ✓ Progressive rollout           │
│                                   │
│ Stage 7: Learning (10 min)         │
│   ✓ Analyze results               │
│   ✓ Generate improvements         │
│   ✓ Update system                 │
│                                   │
│ Total: ~2 hours 20 minutes         │
└────────────────────────────────┘
```

---

## Monitoring the Workflow

### Real-Time Logs

```bash
# Watch workflow in real-time
gh run watch

# Or view specific step
gh run view <run-id> --log --step <step-number>
```

### Check Artifacts

```bash
# List generated artifacts
gh run download <run-id>

# View files
ls -la

# Check test results
cat test-results/coverage.json

# Review code review
cat code-review/review.json
```

### Dashboard

```
Actions Dashboard:
https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/actions

Status:
  🟢 = Running
  ✅ = Success
  ❌ = Failed
  ⚠️  = Warning
```

---

## Common Commands

```bash
# List recent runs
gh run list --limit 10

# Get specific run details
gh run view <run-id> --json status,conclusion,duration

# Re-run failed workflow
gh run rerun <run-id> --failed

# Cancel running workflow
gh run cancel <run-id>

# Download artifacts
gh run download <run-id> -D ./artifacts

# Trigger workflow manually
gh workflow run 01-ai-orchestrator.yaml
```

---

## Configuration Quick Reference

### Budget Settings

```yaml
# File: .github/ai-config/safety-guardrails.yaml

daily_budget: 500          # $ per day
hourly_budget: 50          # $ per hour
monthly_budget: 15000      # $ per month
```

### Model Preferences

```yaml
# File: .github/ai-config/model-selection.yaml

# Simple tasks: Use GPT-3.5 (cheapest)
# Standard tasks: Use GPT-4 (balanced)
# Complex tasks: Use Claude Opus (best quality)
```

### Task Complexity

```yaml
# File: .github/ai-config/orchestration-rules.yaml

simple:    # Bugfixes, hotfixes, updates
standard:  # Features, tests, optimizations
complex:   # Architecture, major refactors
```

---

## Troubleshooting

### "API Key Error"

```bash
# Check if keys are set
gh secret list | grep OPENAI

# If missing, add them
gh secret set OPENAI_API_KEY_1 --body "your-key"

# Test connection
node .github/ai-agents/orchestrator-agent.js
```

### "Workflow Failed"

```bash
# View error logs
gh run view <run-id> --log

# Check specific step
gh run view <run-id> --log --step <step-name>

# Debug locally
npm test
```

### "Rate Limit Exceeded"

```bash
# Check current spend
echo "Check spending in GitHub Actions logs"

# Reduce model usage
# Edit .github/ai-config/model-selection.yaml
# Switch to cheaper models

# Or increase budget
gh secret set DAILY_BUDGET --body "750"
```

---

## Next Steps

1. **Monitor First Run**: Watch the workflow execute
2. **Review Results**: Check generated code and test results
3. **Adjust Config**: Fine-tune based on your needs
4. **Schedule Regularly**: Set up recurring tasks
5. **Monitor Costs**: Keep budget in check

---

## Key Files to Know

```
.github/
├── ai-agents/
│   └── orchestrator-agent.js      Main coordinator
├── ai-config/
│   ├── orchestration-rules.yaml    Task routing
│   ├── model-selection.yaml        Model registry
│   └── safety-guardrails.yaml      Safety rules
├── workflows/
│   └── 01-ai-orchestrator.yaml     Main workflow
└── docs/
    ├── AI_SYSTEM_ARCHITECTURE.md   Full docs
    └── SAFETY_MECHANISMS.md        Safety docs
```

---

## Support

- **Issues**: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues
- **PR**: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pull/272
- **Email**: over7-maker@github.com

---

**Ready to go?** 🚀

Execute the commands above and watch your AI system come alive!
