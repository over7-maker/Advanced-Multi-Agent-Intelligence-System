# 🤖 GitHub Actions AI Workflows Setup Guide

This guide will help you set up and configure the AI-powered GitHub Actions workflows for your AMAS project.

## 📋 Overview

Your project now has the following AI-powered workflows:

1. **AI Code Analysis** - Analyzes code quality and security
2. **AI Issue Responder** - Automatically responds to GitHub issues
3. **Enhanced AI Integration** - Comprehensive workflow that combines all AI systems
4. **Multi-Agent Workflow** - Uses multiple AI models for intelligence analysis
5. **Workflow Status Monitor** - Monitors and reports on workflow health

## 🔧 Required GitHub Secrets

You need to configure the following secrets in your GitHub repository:

### 1. Go to Repository Settings
- Navigate to your repository on GitHub
- Click on **Settings** tab
- Click on **Secrets and variables** → **Actions**

### 2. Add Required Secrets

Add these secrets with your API keys:

```
GITHUB_TOKEN
```
- **Value**: Your GitHub Personal Access Token
- **Purpose**: Allows workflows to interact with GitHub API
- **How to get**: GitHub → Settings → Developer settings → Personal access tokens → Generate new token (classic)
- **Permissions needed**: `repo`, `workflow`, `write:packages`

```
OPENROUTER_API_KEY
```
- **Value**: Your OpenRouter API key
- **Purpose**: Access to multiple AI models through OpenRouter
- **How to get**: Sign up at [OpenRouter.ai](https://openrouter.ai) and get your API key

```
DEEPSEEK_API_KEY
```
- **Value**: Your DeepSeek API key (optional)
- **Purpose**: Direct access to DeepSeek models
- **How to get**: Sign up at [DeepSeek.com](https://deepseek.com) and get your API key

```
GLM_API_KEY
```
- **Value**: Your GLM API key (optional)
- **Purpose**: Access to GLM models
- **How to get**: Sign up for GLM API access

```
GROK_API_KEY
```
- **Value**: Your Grok API key (optional)
- **Purpose**: Access to Grok models
- **How to get**: Sign up for Grok API access

## 🚀 Workflow Features

### 1. AI Code Analysis (`ai-code-analysis.yml`)
**Triggers**: Pull requests and pushes to main branch

**Features**:
- ✅ Analyzes code quality and best practices
- 🔒 Performs security vulnerability scanning
- 🤖 Uses AI models for intelligent code review
- 📝 Posts detailed analysis as PR comments
- 🏷️ Automatically adds labels to PRs

**What it does**:
- Scans changed files for security issues
- Provides AI-powered code review
- Detects potential secrets and vulnerabilities
- Suggests improvements and best practices

### 2. AI Issue Responder (`ai-issue-responder.yml`)
**Triggers**: When issues are opened or edited

**Features**:
- 🧠 Analyzes issue type automatically
- 💬 Generates intelligent responses
- 🏷️ Adds appropriate labels
- 📊 Categorizes issues (bug, feature, question, etc.)

**What it does**:
- Reads issue title and description
- Determines issue type (bug, feature request, question, security, etc.)
- Generates helpful AI responses
- Adds relevant labels for organization

### 3. Enhanced AI Integration (`enhanced-ai-integration.yml`)
**Triggers**: Issues, pull requests, and manual dispatch

**Features**:
- 🔄 Orchestrates multiple AI workflows
- 📊 Provides comprehensive issue resolution
- 🤖 Multi-agent intelligence analysis
- 📈 Tracks resolution progress

**What it does**:
- Combines all AI analysis results
- Provides resolution status updates
- Coordinates between different AI systems
- Generates comprehensive reports

### 4. Multi-Agent Workflow (`multi-agent-workflow.yml`)
**Triggers**: Daily schedule and manual dispatch

**Features**:
- 🧠 Uses multiple AI models collaboratively
- 📊 Generates intelligence reports
- 🔍 Performs deep analysis
- 📁 Saves reports as artifacts

**What it does**:
- Runs multiple AI models in sequence
- Each model builds on the previous one's output
- Generates comprehensive intelligence reports
- Saves results for review

### 5. Workflow Status Monitor (`workflow-status-monitor.yml`)
**Triggers**: Every 6 hours and on manual dispatch

**Features**:
- 📊 Monitors workflow health
- 📈 Tracks success rates
- ⚠️ Identifies issues and failures
- 📝 Generates status reports

**What it does**:
- Checks all workflow runs
- Analyzes success/failure patterns
- Provides recommendations
- Saves detailed reports

## 🛠️ Setup Instructions

### Step 1: Configure Secrets
1. Go to your repository settings
2. Navigate to Secrets and variables → Actions
3. Add all required secrets listed above

### Step 2: Test Workflows
1. Create a test issue in your repository
2. The AI Issue Responder should automatically respond
3. Create a test pull request
4. The AI Code Analysis should run automatically

### Step 3: Monitor Status
1. Go to the Actions tab in your repository
2. Check that workflows are running successfully
3. Review any error messages and fix issues

## 🔍 Troubleshooting

### Common Issues:

#### 1. Workflows Not Triggering
**Problem**: Workflows don't run when expected
**Solutions**:
- Check that secrets are properly configured
- Verify workflow files are in `.github/workflows/`
- Check repository permissions
- Ensure workflows are not disabled

#### 2. API Key Errors
**Problem**: "API key not found" or authentication errors
**Solutions**:
- Verify all required secrets are set
- Check API key validity
- Ensure API keys have sufficient credits/quota
- Test API keys independently

#### 3. Permission Errors
**Problem**: "Permission denied" or "403 Forbidden"
**Solutions**:
- Check GitHub token permissions
- Verify repository access
- Update token with required scopes

#### 4. Workflow Failures
**Problem**: Workflows fail with errors
**Solutions**:
- Check workflow logs in Actions tab
- Verify Python dependencies
- Check file paths and permissions
- Test scripts locally

### Debugging Steps:

1. **Check Workflow Logs**:
   - Go to Actions tab
   - Click on failed workflow
   - Review step-by-step logs
   - Look for error messages

2. **Test Scripts Locally**:
   ```bash
   # Test AI scripts locally
   python .github/scripts/ai_issue_responder.py
   python .github/scripts/ai_code_analyzer.py
   ```

3. **Verify API Keys**:
   ```bash
   # Test API connectivity
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openrouter.ai/models
   ```

## 📊 Monitoring and Maintenance

### Regular Checks:
- Monitor workflow success rates
- Review AI responses for quality
- Update API keys when needed
- Check for new security vulnerabilities

### Performance Optimization:
- Monitor workflow execution times
- Optimize AI prompts for better results
- Update dependencies regularly
- Scale API usage as needed

## 🎯 Expected Results

After setup, you should see:

1. **Automatic Issue Responses**: New issues get AI-generated responses within minutes
2. **Code Analysis**: Pull requests receive detailed AI code reviews
3. **Security Scanning**: Potential vulnerabilities are automatically detected
4. **Status Monitoring**: Regular reports on workflow health
5. **Intelligence Reports**: Comprehensive analysis from multiple AI models

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review workflow logs in the Actions tab
3. Verify all secrets are properly configured
4. Test individual components
5. Check API quotas and limits

## 🔄 Updates and Maintenance

### Regular Updates:
- Update Python dependencies monthly
- Review and update AI prompts quarterly
- Monitor API usage and costs
- Update workflow configurations as needed

### Scaling:
- Add more AI models as needed
- Increase workflow frequency if required
- Add custom analysis rules
- Integrate with other tools

---

**🎉 Congratulations!** Your AI-powered GitHub Actions workflows are now set up and ready to enhance your development workflow with intelligent automation.