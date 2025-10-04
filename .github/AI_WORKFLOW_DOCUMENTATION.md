# 🤖 AMAS AI Workflow System Documentation

## Overview

The AMAS AI Workflow System provides intelligent automation for code analysis, issue management, and security scanning using multiple AI models. This system leverages your three free unlimited APIs to provide comprehensive development assistance.

## 🔑 API Configuration

### Required GitHub Secrets

Add these secrets to your repository settings (`Settings > Secrets and variables > Actions > New repository secret`):

1. **DEEPSEEK_API_KEY**: `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`
2. **GLM_API_KEY**: `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`
3. **GROK_API_KEY**: `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`

### API Model Mapping

| API Key | Provider | Model | Use Case |
|---------|----------|-------|----------|
| DEEPSEEK_API_KEY | DeepSeek Direct | `deepseek-chat` | Primary analysis (most reliable) |
| GLM_API_KEY | OpenRouter | `z-ai/glm-4.5-air:free` | Secondary analysis |
| GROK_API_KEY | OpenRouter | `x-ai/grok-4-fast:free` | Strategic recommendations |

## 🚀 Workflows

### 1. AI-Enhanced Development Workflow (`ai-enhanced-workflow.yml`)

**Triggers:**
- Pull requests (opened, synchronize, reopened)
- Pushes to main/develop branches
- Issues (opened, edited)
- Issue comments
- Manual dispatch
- Daily schedule (2 AM UTC)

**Features:**
- ✅ **AI Code Analysis**: Intelligent code review with multiple AI models
- ✅ **Security Scanning**: Automated vulnerability detection
- ✅ **Issue Response**: AI-powered issue management
- ✅ **Multi-Agent Intelligence**: Daily intelligence reports

### 2. Individual Workflows

#### AI Code Analysis (`ai-code-analysis.yml`)
- Analyzes changed files in PRs
- Provides detailed code review
- Security vulnerability detection
- Performance optimization suggestions

#### AI Issue Responder (`ai-issue-responder.yml`)
- Automatically responds to GitHub issues
- Categorizes issues (bug, feature, question, security)
- Provides contextual help and guidance
- Adds appropriate labels

#### Multi-Agent Workflow (`multi-agent-workflow.yml`)
- Coordinates multiple AI agents
- Generates intelligence reports
- Creates daily summaries
- Strategic analysis and recommendations

## 🛠️ Scripts

### AI Code Analyzer (`ai_code_analyzer.py`)

**Features:**
- Multi-model fallback system
- File type-specific analysis
- Security vulnerability detection
- AMAS architecture integration assessment
- Automated PR commenting

**Usage:**
```bash
python .github/scripts/ai_code_analyzer.py
```

### AI Issue Responder (`ai_issue_responder.py`)

**Features:**
- Issue type classification
- Contextual response generation
- Automatic labeling
- Fallback responses for API failures

**Usage:**
```bash
python .github/scripts/ai_issue_responder.py
```

### AI Security Scanner (`ai_security_scanner.py`)

**Features:**
- Secret detection (API keys, passwords, tokens)
- Vulnerability pattern matching
- AI-powered security analysis
- Risk assessment and remediation

**Usage:**
```bash
python .github/scripts/ai_security_scanner.py
```

### Multi-Agent Orchestrator (`multi_agent_orchestrator.py`)

**Features:**
- Coordinated AI agent workflow
- Intelligence gathering and analysis
- Strategic recommendations
- Comprehensive reporting

**Usage:**
```bash
python .github/scripts/multi_agent_orchestrator.py
```

## 🔧 Configuration

### Environment Variables

All scripts use these environment variables:

```bash
# GitHub Integration
GITHUB_TOKEN=your_github_token
REPO_NAME=your_org/your_repo
PR_NUMBER=123
ISSUE_NUMBER=456

# AI API Keys
DEEPSEEK_API_KEY=your_deepseek_key
GLM_API_KEY=your_glm_key
GROK_API_KEY=your_grok_key

# File Analysis
CHANGED_FILES=file1.py file2.js
```

### Model Fallback System

The system implements intelligent fallback:

1. **Primary**: DeepSeek (most reliable)
2. **Secondary**: GLM (OpenRouter)
3. **Tertiary**: Grok (OpenRouter)

If one model fails, the system automatically tries the next available model.

## 📊 Output Examples

### Code Analysis Report
```markdown
# 🤖 AI Code Analysis Report

## 🚨 Security Analysis
- **api_key** (Line 15): `sk-or-v1-...`
- **sql_injection** (Line 42): Potential SQL injection vulnerability

## 📊 Detailed Code Review
### 1. main.py
**Overall Assessment**: Needs Improvement
**Security Analysis**: Hardcoded API key detected
**Code Quality**: Good structure, needs security improvements
**AMAS Integration**: Well-integrated with project architecture
**Specific Recommendations**:
1. Move API key to environment variables
2. Add input validation for user data
3. Implement proper error handling
```

### Issue Response
```markdown
Thank you for opening this issue! 🙏

I'm the AMAS AI Assistant, and I've analyzed your request for [feature description].

**Issue Type**: Feature Request
**Priority**: Medium

## Suggested Implementation:
1. [Implementation step 1]
2. [Implementation step 2]
3. [Implementation step 3]

## Related Resources:
- [Documentation link]
- [Example code]

---
🤖 *This response was generated by AMAS AI Assistant*
💡 *Powered by your integrated AI models*
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Not Working**
   - Verify the secret is correctly set in GitHub
   - Check the API key format and validity
   - Ensure the secret name matches exactly

2. **Workflow Not Triggering**
   - Check workflow file syntax
   - Verify trigger conditions
   - Ensure repository has Actions enabled

3. **AI Analysis Failing**
   - Check API rate limits
   - Verify model availability
   - Review error logs in Actions

### Debug Mode

Enable debug logging by adding to workflow:
```yaml
- name: Debug Environment
  run: |
    echo "DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:0:10}..."
    echo "GLM_API_KEY: ${GLM_API_KEY:0:10}..."
    echo "GROK_API_KEY: ${GROK_API_KEY:0:10}..."
```

## 🔄 Maintenance

### Regular Tasks

1. **Monitor API Usage**: Check rate limits and quotas
2. **Update Dependencies**: Keep Python packages current
3. **Review Reports**: Analyze AI-generated insights
4. **Optimize Prompts**: Refine AI instructions for better results

### Performance Optimization

- **Parallel Processing**: Multiple AI models work simultaneously
- **Caching**: Results cached to avoid redundant API calls
- **Error Handling**: Graceful degradation when APIs fail
- **Resource Management**: Efficient token usage

## 📈 Advanced Features

### Custom Prompts

Modify system prompts in scripts for project-specific analysis:

```python
system_prompt = """
You are an expert code reviewer for [YOUR_PROJECT].
Focus on:
- [Specific requirements]
- [Security concerns]
- [Performance criteria]
"""
```

### Integration Extensions

- **Slack Notifications**: Alert teams of critical issues
- **JIRA Integration**: Create tickets for security issues
- **Custom Metrics**: Track AI analysis effectiveness
- **Report Automation**: Schedule regular intelligence reports

## 🛡️ Security Considerations

- **API Key Protection**: Never commit keys to repository
- **Secret Rotation**: Regularly update API keys
- **Access Control**: Limit workflow permissions
- **Audit Logging**: Monitor AI system usage

## 📞 Support

For issues with the AI workflow system:

1. Check the GitHub Actions logs
2. Verify API key configuration
3. Review workflow file syntax
4. Test scripts locally with environment variables

---

*This documentation is maintained by the AMAS AI Workflow System*
*Last updated: $(date)*