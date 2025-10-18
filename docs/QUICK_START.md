# 🚀 AMAS Quick Start Guide

> **Get up and running with Advanced Multi-Agent Intelligence System in 10 minutes**

## 🎯 **What You'll Achieve**

By the end of this guide, you'll have:
- ✅ **Bulletproof AI system** running with real provider validation
- ✅ **GitHub integration** for automated PR analysis
- ✅ **Phase 2 security** with JWT and rate limiting
- ✅ **Production monitoring** with metrics and dashboards
- ✅ **Your first AI-powered code review** completed

---

## 📚 **Prerequisites**

### **System Requirements**
- **OS**: Linux, macOS, or Windows (WSL2)
- **Python**: 3.8+ (3.11+ recommended)
- **Memory**: 4GB RAM minimum, 8GB+ recommended
- **Disk**: 2GB free space
- **Network**: Internet connection for AI providers

### **Required Accounts**
- **GitHub account** (for repository integration)
- **At least 1 AI provider account** (Cerebras, NVIDIA, or OpenAI recommended)
- **Optional**: Redis for production rate limiting

---

## ⚡ **10-Minute Installation**

### **Step 1: Clone & Setup (2 minutes)**

```bash
# Clone the repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Create virtual environment
python -m venv amas-env

# Activate environment
# On Linux/macOS:
source amas-env/bin/activate
# On Windows:
# amas-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Configure AI Providers (3 minutes)**

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
# Minimum setup (choose ONE):

# Option 1: Cerebras (fastest, recommended)
export CEREBRAS_API_KEY="csk-your-key-here"

# Option 2: NVIDIA (GPU-accelerated)
export NVIDIA_API_KEY="nvapi-your-key-here"

# Option 3: OpenAI (reliable fallback)
export OPENAI_API_KEY="sk-your-key-here"

# Load environment
source .env
```

**🔑 Get API Keys:**
- **Cerebras**: Visit [cloud.cerebras.ai](https://cloud.cerebras.ai) → Create account → API Keys
- **NVIDIA**: Visit [build.nvidia.com](https://build.nvidia.com) → Sign up → Get API Key
- **OpenAI**: Visit [platform.openai.com](https://platform.openai.com) → API Keys → Create new

### **Step 3: Test Installation (2 minutes)**

```bash
# Test AI providers
python -m amas.cli test-providers

# Expected output:
# ✅ Testing Cerebras... OK (2.1s)
# ✅ Bulletproof validation... PASSED
# ✅ Fake AI detection... ACTIVE
# 🎯 Ready for analysis!

# Test basic analysis
echo "print('Hello, AMAS!')" > test.py
python -m amas.cli analyze-file test.py

# Expected output:
# 🤖 BULLETPROOF REAL AI Analysis
# Status: ✅ REAL AI Verified
# Provider: cerebras
# Response Time: 2.3s
# Validation: Bulletproof validated ✓
# 
# 🔍 Analysis:
# ✅ Code quality: Good
# ✅ No security issues found
# ✅ Performance: Optimal
```

### **Step 4: GitHub Integration (2 minutes)**

```bash
# Configure GitHub token
export GITHUB_TOKEN="ghp_your_github_token_here"

# Test GitHub integration
python -m amas.cli test-github

# Add to your repository's .github/workflows/amas.yml:
```

```yaml
name: 🤖 AMAS AI Analysis

on:
  pull_request:
    types: [opened, synchronize]
  issue_comment:
    types: [created]

jobs:
  ai-analysis:
    if: contains(github.event.comment.body, '@amas') || github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install AMAS
        run: |
          pip install -r requirements.txt
          
      - name: Run AI Analysis
        run: |
          python -m amas.cli analyze-pr --pr-number ${{ github.event.pull_request.number }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CEREBRAS_API_KEY: ${{ secrets.CEREBRAS_API_KEY }}
          BULLETPROOF_VALIDATION: true
```

### **Step 5: First Analysis (1 minute)**

```bash
# Analyze your current repository
python -m amas.cli analyze-repo .

# Or analyze a specific file
python -m amas.cli analyze-file src/main.py --analysis-types security,performance

# Or analyze a GitHub repository
python -m amas.cli analyze-github-repo owner/repo-name
```

**🎉 Congratulations! AMAS is now running with bulletproof AI validation!**

---

## 📚 **First Steps & Examples**

### **Example 1: Analyze Security Issues**

```bash
# Create a file with security issues
cat > vulnerable.py << EOF
import sqlite3
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchone()
EOF

# Analyze with AMAS
python -m amas.cli analyze-file vulnerable.py --analysis-types security
```

**Expected AI Output:**
```markdown
🤖 BULLETPROOF REAL AI Analysis
Status: ✅ REAL AI Verified
Provider: cerebras
Response Time: 3.2s
Validation: Bulletproof validated ✓

🚨 CRITICAL Security Issues Found:

📁 File: vulnerable.py
📍 Line: 5
🚨 Issue: SQL Injection vulnerability
📊 Severity: CRITICAL
🔧 Fix: Use parameterized queries

Recommended fix:
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

🎯 Summary:
- 1 Critical security issue
- 0 Performance issues
- Bulletproof validation: ✅ PASSED
```

### **Example 2: Performance Analysis**

```bash
# Create a performance issue example
cat > slow_code.py << EOF
def process_data(items):
    result = []
    for item in items:
        # Inefficient: multiple database calls
        user = get_user_from_db(item.user_id)
        result.append({
            'item': item,
            'user': user
        })
    return result
EOF

# Analyze performance
python -m amas.cli analyze-file slow_code.py --analysis-types performance
```

**Expected AI Output:**
```markdown
🤖 BULLETPROOF REAL AI Analysis
Status: ✅ REAL AI Verified
Provider: nvidia
Response Time: 2.8s
Validation: Bulletproof validated ✓

⚡ Performance Issues Found:

📁 File: slow_code.py
📍 Line: 4-6
🐌 Issue: N+1 Database Query Problem
📊 Impact: High - O(n) database calls
🔧 Fix: Use bulk query or JOIN

Optimized version:
def process_data(items):
    user_ids = [item.user_id for item in items]
    users = get_users_bulk(user_ids)  # Single query
    user_map = {u.id: u for u in users}
    
    return [{
        'item': item,
        'user': user_map[item.user_id]
    } for item in items]

💰 Estimated Performance Gain: 80-95% faster
```

### **Example 3: GitHub PR Analysis**

```bash
# Comment on any PR to trigger analysis
# Just add this comment to a PR:

@amas analyze security performance code-quality
```

**Expected GitHub Comment:**
```markdown
🤖 BULLETPROOF REAL AI Analysis
Status: ✅ REAL AI Verified
Provider: cerebras
Response Time: 5.2s
Validation: Bulletproof validated ✓

## 🔍 Security Analysis

📁 **File:** `src/auth/login.py`
📍 **Line:** 23
🚨 **Issue:** Missing rate limiting on login endpoint
🔧 **Fix:** Add `@rate_limit('5/minute')` decorator

## ⚡ Performance Analysis

📁 **File:** `src/database/queries.py`
📍 **Line:** 45
🐌 **Issue:** Inefficient database query
🔧 **Fix:** Add database index on `user_id` column

## 🎯 Summary
- 2 Security issues (1 High, 1 Medium)
- 1 Performance issue (Medium)
- 0 Code quality issues
- Analysis time: 5.2s
- Fake AI responses: 0 (100% real)

📊 **Verification:**
✅ Real AI Verified: true
❌ Fake AI Detected: false
✅ Bulletproof Validated: true
```

---

## 🎆 **Advanced Configuration**

### **Multi-Provider Setup (Recommended)**

```bash
# For maximum reliability, configure multiple providers
cat >> .env << EOF
# Primary providers (fast)
CEREBRAS_API_KEY="csk-your-key"
NVIDIA_API_KEY="nvapi-your-key"

# Backup providers (reliable)
OPENAI_API_KEY="sk-your-key"
ANTHROPIC_API_KEY="sk-ant-your-key"

# Strategy: intelligent selection
AMAS_STRATEGY="intelligent"
AMAS_MAX_RETRIES=3
BULLETPROOF_VALIDATION=true
EOF

# Test multi-provider setup
python -m amas.cli test-providers --all
```

### **Phase 2 Security Setup (Production)**

```bash
# Generate secure keys
JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)

# Add to .env
cat >> .env << EOF
# Phase 2 Security
JWT_SECRET_KEY="$JWT_SECRET"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION=3600

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_IP="100/hour"
RATE_LIMIT_PER_USER="1000/hour"

# Encryption
ENCRYPTION_KEY="$ENCRYPTION_KEY"
ENCRYPTION_ENABLED=true

# Audit Logging
AUDIT_LOGGING=true
LOG_LEVEL="INFO"
STRUCTURED_LOGGING=true

# Security Headers
SECURITY_HEADERS_ENABLED=true
CSP_ENABLED=true
HSTS_ENABLED=true
EOF

# Test security features
python -m amas.cli test-security
```

### **Observability Setup (Monitoring)**

```bash
# Install monitoring dependencies
pip install prometheus-client grafana-api

# Add monitoring config
cat >> .env << EOF
# Observability
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
METRICS_ENABLED=true

# Grafana (optional)
GRAFANA_ENABLED=true
GRAFANA_PORT=3000
GRAFANA_API_KEY="your-grafana-key"

# Alerting
SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
EMAIL_ALERTS_ENABLED=true
EOF

# Start monitoring
python -m amas.monitoring start

# View metrics
curl http://localhost:9090/metrics | grep amas
```

---

## 🔍 **Common Use Cases**

### **Use Case 1: Daily Code Review**

```bash
# Create daily code review script
cat > daily_review.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Daily AMAS Code Review..."

# Analyze last 24 hours of changes
git diff --name-only HEAD@{1.day.ago}..HEAD | while read file; do
    if [[ $file =~ \.(py|js|ts|java|cpp|c|go|rs)$ ]]; then
        echo "Analyzing: $file"
        python -m amas.cli analyze-file "$file" --analysis-types security,performance,quality
    fi
done

echo "✅ Daily review complete!"
EOF

chmod +x daily_review.sh
./daily_review.sh
```

### **Use Case 2: Pre-commit Hook**

```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# AMAS pre-commit analysis

echo "🤖 Running AMAS analysis on staged files..."

# Get staged files
staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|ts|java|cpp|c|go|rs)$')

if [ -z "$staged_files" ]; then
    echo "No code files staged for commit."
    exit 0
fi

# Analyze each staged file
for file in $staged_files; do
    echo "Analyzing: $file"
    python -m amas.cli analyze-file "$file" --analysis-types security --fail-on-critical
    
    if [ $? -ne 0 ]; then
        echo "❌ Critical security issues found in $file"
        echo "Commit blocked. Please fix issues and try again."
        exit 1
    fi
done

echo "✅ All files passed AMAS analysis!"
EOF

chmod +x .git/hooks/pre-commit
```

### **Use Case 3: CI/CD Integration**

```yaml
# .github/workflows/security-scan.yml
name: Security Scan with AMAS

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2  # Get previous commit for diff
          
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install AMAS
        run: |
          pip install -r requirements.txt
          
      - name: Security Analysis
        run: |
          # Analyze changed files only
          git diff --name-only HEAD~1 HEAD | \
          grep -E '\.(py|js|ts|java|cpp|c|go|rs)$' | \
          xargs python -m amas.cli analyze-files \
            --analysis-types security,performance \
            --fail-on-critical \
            --output-format github-comment
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CEREBRAS_API_KEY: ${{ secrets.CEREBRAS_API_KEY }}
          BULLETPROOF_VALIDATION: true
          
      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: amas-analysis-results
          path: amas-results.json
```

---

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **❌ "No AI providers configured"**

```bash
Error: No AI providers configured or available

# Solution:
1. Check environment variables are set:
echo $CEREBRAS_API_KEY  # Should show your key
echo $NVIDIA_API_KEY    # Or whichever provider you're using

2. Verify API key format:
# Cerebras: starts with 'csk-'
# NVIDIA: starts with 'nvapi-'
# OpenAI: starts with 'sk-'

3. Test API key validity:
python -m amas.cli test-api-key cerebras

4. Load environment variables:
source .env
```

#### **❌ "Bulletproof validation failed"**

```bash
Error: Fake AI detected - bulletproof validation failed

# This is GOOD! Fake AI was blocked.
# But if you're using real APIs:

# Solution:
1. Verify you're using production API keys (not test/mock)
2. Check API provider status:
curl -s https://status.cerebras.com/api/v2/status.json

3. Test with debug mode:
export AMAS_DEBUG=true
python -m amas.cli analyze-file test.py --debug

4. Check network connectivity:
ping api.cerebras.ai
```

#### **⚡ "Analysis taking too long"**

```bash
Error: Analysis timed out after 300 seconds

# Solutions:
1. Increase timeout:
export AMAS_TIMEOUT=600

2. Use faster provider:
export AMAS_STRATEGY="fastest"

3. Reduce analysis scope:
python -m amas.cli analyze-file large_file.py --max-lines 500

4. Use quick analysis mode:
python -m amas.cli analyze-file file.py --quick
```

#### **🔒 "GitHub integration not working"**

```bash
Error: Failed to post comment to GitHub

# Solutions:
1. Check GitHub token:
echo $GITHUB_TOKEN  # Should start with 'ghp_' or 'github_pat_'

2. Verify token permissions:
# Token needs: repo, write:discussion

3. Test GitHub API access:
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/user

4. Check repository access:
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/repos/your-org/your-repo
```

### **Debug Mode**

```bash
# Enable comprehensive debugging
export AMAS_DEBUG=true
export LOG_LEVEL=DEBUG
export PROVIDER_DEBUG=true
export BULLETPROOF_DEBUG=true

# Run with verbose logging
python -m amas.cli analyze-file test.py --debug --verbose

# Check logs
tail -f logs/amas-debug.log

# Monitor provider calls in real-time
python -m amas.monitoring tail-logs --filter="provider_call"
```

### **Health Checks**

```bash
# Check overall system health
python -m amas.cli health-check

# Check specific components
python -m amas.cli health-check --component providers
python -m amas.cli health-check --component bulletproof
python -m amas.cli health-check --component security
python -m amas.cli health-check --component github

# Check API endpoints (if running as service)
curl -s http://localhost:8080/health | jq
curl -s http://localhost:8080/health/providers | jq
curl -s http://localhost:8080/metrics | grep amas_provider_health
```

---

## 📚 **Next Steps**

### **Level 1: Basic Usage** ✅
- [x] Install and configure AMAS
- [x] Connect to AI provider
- [x] Run first analysis
- [ ] **Next**: Set up GitHub integration

### **Level 2: GitHub Integration** 🚀
- [ ] Add GitHub workflow
- [ ] Configure PR analysis
- [ ] Set up automated comments
- [ ] **Next**: Enable Phase 2 security

### **Level 3: Production Security** 🔒
- [ ] Enable JWT authentication
- [ ] Configure rate limiting
- [ ] Set up audit logging
- [ ] **Next**: Add monitoring & alerts

### **Level 4: Enterprise Monitoring** 📊
- [ ] Set up Prometheus metrics
- [ ] Configure Grafana dashboards
- [ ] Enable alerting
- [ ] **Next**: Scale to multiple repositories

### **Level 5: Organization-wide Deployment** 🌍
- [ ] Deploy to multiple repositories
- [ ] Set up team permissions
- [ ] Configure compliance monitoring
- [ ] **Next**: Custom AI workflows

---

## 📚 **Learning Resources**

### **Documentation**
- **📖 [AI Providers Guide](AI_PROVIDERS.md)** - Complete provider setup
- **🔒 [Phase 2 Security](PHASE_2_FEATURES.md)** - Enterprise security features
- **📊 [Monitoring Guide](MONITORING_GUIDE.md)** - Production observability
- **🤖 [Bulletproof Validation](BULLETPROOF_VALIDATION.md)** - Fake AI detection

### **Video Tutorials**
- **▶️ AMAS in 5 Minutes** - Quick installation and first analysis
- **▶️ GitHub Integration** - Complete CI/CD setup
- **▶️ Security Hardening** - Phase 2 production deployment
- **▶️ Advanced Workflows** - Custom AI analysis pipelines

### **Examples & Templates**
- **📋 [GitHub Workflows](templates/workflows/)** - Ready-to-use CI/CD templates
- **🔧 [Pre-commit Hooks](templates/hooks/)** - Local development integration
- **📊 [Dashboards](templates/dashboards/)** - Grafana monitoring templates
- **⚙️ [Config Files](templates/config/)** - Production configuration examples

### **Community & Support**
- **💬 [Discord Community](https://discord.gg/amas)** - Get help and share tips
- **🐛 [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)** - Bug reports and feature requests
- **📧 [Email Support](mailto:support@amas.ai)** - Direct support
- **📰 [Blog](https://blog.amas.ai)** - Latest updates and tutorials

---

## 🎆 **You're Ready!**

**Congratulations! You now have:**
- ✅ **Bulletproof AI system** that rejects fake responses
- ✅ **Enterprise-grade security** with Phase 2 features
- ✅ **Production monitoring** with metrics and alerts
- ✅ **GitHub integration** for automated code review
- ✅ **Zero-failure guarantee** with intelligent fallback

### **🚀 What's Next?**

1. **📋 Analyze Your First PR**: Comment `@amas analyze security performance` on any PR
2. **🔒 Enable Security**: Set up JWT and rate limiting for production
3. **📊 Add Monitoring**: Configure Prometheus and Grafana dashboards
4. **🌍 Scale Up**: Deploy across your organization's repositories
5. **🤖 Customize**: Create custom AI workflows for your specific needs

### **🎯 Join the AI Revolution**

**AMAS represents the future of software development:**
- **100% Real AI** - Never accept fake responses
- **Enterprise Security** - Ready for production from day one
- **Bulletproof Reliability** - 16 providers with intelligent fallback
- **Zero Configuration** - Works out of the box

**Welcome to bulletproof AI-powered development!** 🚀✨

---

<div align="center">

**🎆 Happy Coding with AMAS! 🎆**

*If you found this guide helpful, please ⭐ star the repository!*

[⭐ Star AMAS](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System) • [💬 Join Discord](https://discord.gg/amas) • [📧 Get Support](mailto:support@amas.ai)

</div>