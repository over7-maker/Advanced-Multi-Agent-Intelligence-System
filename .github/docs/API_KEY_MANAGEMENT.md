# API Key Management & Setup Procedures

**Document Version**: 2.0  
**Last Updated**: December 18, 2025  
**Status**: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [API Key List & Priorities](#api-key-list--priorities)
3. [Setup Procedures](#setup-procedures)
4. [Security Best Practices](#security-best-practices)
5. [Key Rotation Strategy](#key-rotation-strategy)
6. [Troubleshooting](#troubleshooting)
7. [Emergency Procedures](#emergency-procedures)

---

## Overview

The Advanced Multi-Agent Intelligence System (AMAS) integrates **16+ AI API keys** across multiple providers for redundancy, cost optimization, and maximum availability. This document provides complete setup procedures for all services.

### Key Management Goals

✅ **Security**: Encrypted storage in GitHub Secrets  
✅ **Reliability**: Intelligent failover between providers  
✅ **Cost Optimization**: Dynamic model selection based on task complexity  
✅ **Scalability**: Support for 16+ simultaneous API providers  
✅ **Auditability**: Complete logging of API usage and key rotations  

---

## API Key List & Priorities

### Priority 1: Primary Providers (Most Reliable)

| # | Service | Model | Use Case | Setup Difficulty | Status |
|---|---------|-------|----------|-------------------|--------|
| 1 | **DeepSeek** | deepseek-chat | Code analysis, reasoning | ⭐ Easy | ✅ Active |
| 2 | **OpenAI** | GPT-4 Turbo | Advanced reasoning, code review | ⭐⭐ Medium | ✅ Active |
| 3 | **Anthropic** | Claude 3 Opus | Deep analysis, architecture | ⭐ Easy | ✅ Active |
| 4 | **Google** | Gemini Pro | Multi-modal analysis | ⭐ Easy | ✅ Active |

### Priority 2: Secondary Providers (Reliable Fallbacks)

| # | Service | Model | Use Case | Setup Difficulty | Status |
|---|---------|-------|----------|-------------------|--------|
| 5 | **Groq** | Mixtral 8x7B | Fast inference | ⭐ Easy | ✅ Active |
| 6 | **Cohere** | Command R+ | Text generation | ⭐⭐ Medium | ✅ Active |
| 7 | **Mistral** | Mistral Large | Advanced reasoning | ⭐ Easy | ✅ Active |
| 8 | **Meta** | LLaMA 3 | Open-source alternative | ⭐⭐ Medium | ✅ Active |

### Priority 3: Tertiary Providers (Extended Support)

| # | Service | Model | Use Case | Setup Difficulty | Status |
|---|---------|-------|----------|-------------------|--------|
| 9 | **Hugging Face** | Multiple models | Custom fine-tuned | ⭐⭐⭐ Hard | ⚠️ Optional |
| 10 | **Azure OpenAI** | GPT-4/Copilot | Enterprise integration | ⭐⭐⭐ Hard | ⚠️ Optional |
| 11 | **AWS Bedrock** | Multiple models | AWS ecosystem | ⭐⭐⭐ Hard | ⚠️ Optional |
| 12 | **GitHub Models** | 40+ models | Native GitHub | ⭐ Easy | ✅ Active |

### Free/OpenRouter Alternatives

| # | Service | Model | Cost | Setup Difficulty | Status |
|---|---------|-------|------|-------------------|--------|
| 13 | **OpenRouter** (GLM) | GLM-4.5 Air | Free | ⭐ Easy | ✅ Active |
| 14 | **OpenRouter** (Grok) | Grok-4 Fast | Free | ⭐ Easy | ✅ Active |
| 15 | **OpenRouter** (Qwen) | Qwen-2.5 7B | Free | ⭐ Easy | ✅ Active |
| 16 | **OpenRouter** (Kimi) | Moonshot V1 | Free | ⭐ Easy | ✅ Active |

---

## Setup Procedures

### Phase 1: Create GitHub Secrets (5 minutes)

#### Prerequisites

- GitHub repository with admin access
- All API keys obtained from respective providers
- GitHub CLI installed (optional but recommended)

#### Method A: Using GitHub CLI (Recommended)

```bash
# Login to GitHub
gh auth login

# Set your repository
GH_REPO="owner/repo"

# Add all API keys
gh secret set DEEPSEEK_API_KEY --body "sk-xxxxx..." --repo $GH_REPO
gh secret set CLAUDE_API_KEY --body "sk-ant-xxxxx..." --repo $GH_REPO
gh secret set GPT4_API_KEY --body "sk-proj-xxxxx..." --repo $GH_REPO
gh secret set GEMINI_API_KEY --body "AIzaSy..." --repo $GH_REPO
gh secret set GROQ_API_KEY --body "gsk_xxxxx..." --repo $GH_REPO
gh secret set COHERE_API_KEY --body "xxxxx..." --repo $GH_REPO
gh secret set MISTRAL_API_KEY --body "xxxxx..." --repo $GH_REPO
gh secret set LLAMA_API_KEY --body "xxxxx..." --repo $GH_REPO
```

#### Method B: Using GitHub Web UI

1. Navigate to: **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Enter secret name (e.g., `DEEPSEEK_API_KEY`)
4. Paste the API key value
5. Click **Add secret**
6. Repeat for all 16 keys

### Phase 2: Test All Keys

Create a verification workflow to test all API keys work correctly.

---

## Security Best Practices

### ✅ DO

- Use GitHub Secrets for all API keys
- Rotate keys regularly (every 90 days)
- Use least-privilege API keys
- Enable API key expiration where supported
- Monitor API usage regularly
- Use different keys for different environments
- Enable audit logging for API access

### ❌ DON'T

- Never commit API keys to git
- Never log or print API keys
- Never share keys in Slack/Email
- Never use the same key for multiple services
- Never expose keys in error messages

---

## Key Rotation Strategy

**Quarterly Rotation (Every 90 Days)**

1. Generate new key in provider console
2. Test new key thoroughly
3. Update GitHub Secret
4. Monitor for 24 hours
5. Revoke old key

---

## Emergency Procedures

### Compromised API Key

**Immediate Actions**:

1. Revoke compromised key immediately in provider console
2. Generate new replacement key
3. Update GitHub Secret
4. Check usage logs for suspicious activity
5. Notify team members

### Multiple Key Failures

**Escalation Procedure**:

1. Test each provider individually
2. Check provider status pages
3. Verify network connectivity
4. If >3 providers failing: activate emergency protocol
5. Scale back to working providers only

---

## Summary

**Quick Setup (10 minutes)**:

```bash
# 1. Gather all 16 API keys from respective providers
# 2. Run: gh secret set for each key
# 3. Verify: gh secret list
# 4. Test: Run workflow with API calls
# 5. Monitor: Check workflow logs for success
```

**Ongoing Maintenance**:
- Weekly: Monitor API usage and costs
- Monthly: Review documentation
- Quarterly: Rotate API keys
- Always: Keep dependencies updated

---

**For detailed setup instructions for each provider, see the individual setup sections above.**
