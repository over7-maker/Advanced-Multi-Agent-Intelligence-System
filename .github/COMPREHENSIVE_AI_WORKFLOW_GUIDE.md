# 🤖 AMAS Comprehensive AI Workflow System

## Overview

The AMAS (Advanced Multi-Agent Intelligence System) now features a comprehensive suite of AI-powered workflows leveraging **6 different AI models** with intelligent fallback capabilities. This system provides automated intelligence gathering, threat analysis, incident response, and code analysis.

## 🔑 API Keys Configuration

### Required GitHub Secrets

Add these secrets to your repository settings (`Settings > Secrets and variables > Actions > New repository secret`):

1. **DEEPSEEK_API_KEY**: Your DeepSeek API key
2. **GLM_API_KEY**: Your GLM API key  
3. **GROK_API_KEY**: Your Grok API key
4. **KIMI_API_KEY**: Your Kimi API key
5. **QWEN_API_KEY**: Your Qwen API key
6. **GPTOSS_API_KEY**: Your GPTOSS API key

### AI Model Priority System

The system uses intelligent fallback with the following priority order:

1. **DeepSeek** (Priority 1) - Most reliable for primary analysis
2. **GLM** (Priority 2) - Secondary analysis and threat assessment
3. **Grok** (Priority 3) - Strategic recommendations
4. **Kimi** (Priority 4) - Technical analysis and implementation
5. **Qwen** (Priority 5) - Research and fact-checking
6. **GPTOSS** (Priority 6) - Quality assurance and validation

## 🚀 Available Workflows

### 1. AI Code Analysis (`ai-code-analysis.yml`)
**Triggers:** Pull requests, pushes to main
**Features:**
- ✅ Multi-model code review with 6 AI fallbacks
- ✅ Security vulnerability detection
- ✅ Performance optimization suggestions
- ✅ AMAS architecture integration assessment

### 2. AI Issue Responder (`ai-issue-responder.yml`)
**Triggers:** Issues opened/edited, issue comments
**Features:**
- ✅ Intelligent issue classification
- ✅ Contextual AI responses
- ✅ Automatic labeling
- ✅ Multi-model fallback support

### 3. Multi-Agent Intelligence (`multi-agent-workflow.yml`)
**Triggers:** Manual dispatch, daily schedule (2 AM UTC)
**Features:**
- ✅ Coordinated multi-agent analysis
- ✅ Intelligence report generation
- ✅ Strategic recommendations
- ✅ Daily automated reports

### 4. OSINT Data Collection (`ai-osint-collection.yml`)
**Triggers:** Daily schedule (6 AM UTC), manual dispatch, issues with `osint-request` label
**Features:**
- ✅ Automated intelligence gathering
- ✅ Threat landscape analysis
- ✅ Cybersecurity trend monitoring
- ✅ Multi-agent OSINT coordination

### 5. Threat Intelligence (`ai-threat-intelligence.yml`)
**Triggers:** Daily schedule (12 PM UTC), manual dispatch, issues with `threat-analysis` label
**Features:**
- ✅ Threat actor analysis
- ✅ Strategic threat assessment
- ✅ Technical threat analysis
- ✅ Threat forecasting

### 6. Incident Response (`ai-incident-response.yml`)
**Triggers:** Issues with `security-incident`, `urgent`, `critical` labels, every 6 hours
**Features:**
- ✅ Automated incident triage
- ✅ Severity assessment
- ✅ Response strategy development
- ✅ Technical containment procedures

## 🔧 Scripts Overview

### Core Scripts (Updated with 6-API Support)
- **`ai_code_analyzer.py`** - Enhanced with 6 AI models
- **`ai_issue_responder.py`** - Multi-model issue response
- **`ai_security_scanner.py`** - Advanced security analysis
- **`multi_agent_orchestrator.py`** - Coordinated intelligence gathering

### New Advanced Scripts
- **`ai_osint_collector.py`** - OSINT data collection and analysis
- **`ai_threat_intelligence.py`** - Comprehensive threat analysis
- **`ai_incident_response.py`** - Automated incident response

## 📊 Workflow Scheduling

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| Multi-Agent Intelligence | Daily 2 AM UTC | General intelligence gathering |
| OSINT Collection | Daily 6 AM UTC | Open source intelligence |
| Threat Intelligence | Daily 12 PM UTC | Threat analysis and assessment |
| Incident Response | Every 6 hours | Security incident monitoring |
| Code Analysis | On PR/Push | Code quality and security |
| Issue Response | On Issue Events | Automated issue management |

## 🎯 Key Features

### Intelligent Fallback System
- **Primary Model**: DeepSeek (most reliable)
- **Secondary Models**: GLM, Grok (specialized analysis)
- **Tertiary Models**: Kimi, Qwen, GPTOSS (support and validation)
- **Automatic Failover**: If one model fails, system tries the next

### Multi-Agent Collaboration
- **Sequential Analysis**: Each agent builds on previous analysis
- **Specialized Roles**: Each AI model has specific expertise areas
- **Comprehensive Reports**: Detailed analysis from multiple perspectives
- **Quality Assurance**: Final validation by multiple models

### Security Integration
- **Automated Security Scanning**: Detects vulnerabilities and secrets
- **Threat Intelligence**: Continuous threat landscape monitoring
- **Incident Response**: Automated triage and response procedures
- **OSINT Collection**: Open source intelligence gathering

## 📈 Expected Results

### Code Analysis
- **Enhanced Code Quality**: Multi-model code review
- **Security Improvements**: Automated vulnerability detection
- **Performance Optimization**: AI-powered suggestions
- **Architecture Alignment**: AMAS-specific recommendations

### Intelligence Gathering
- **Daily Intelligence Reports**: Automated OSINT collection
- **Threat Assessments**: Regular threat landscape analysis
- **Strategic Recommendations**: AI-powered strategic guidance
- **Incident Response**: Automated security incident handling

### Issue Management
- **Intelligent Responses**: Context-aware issue responses
- **Automatic Classification**: Issue type detection and labeling
- **Multi-Model Analysis**: Comprehensive issue assessment
- **Fallback Support**: Reliable response even if some models fail

## 🛠️ Implementation Tips

### 1. API Key Management
- Store all 6 API keys as GitHub Secrets
- Use consistent naming convention
- Test each API key individually
- Monitor API usage and limits

### 2. Workflow Optimization
- Schedule workflows during off-peak hours
- Use appropriate triggers for each workflow
- Monitor workflow execution times
- Set up notifications for failures

### 3. Report Management
- Review generated reports regularly
- Use artifacts for long-term storage
- Create issues for important findings
- Share insights with team members

### 4. Security Considerations
- Never commit API keys to repository
- Use GitHub Secrets for all sensitive data
- Monitor for exposed credentials
- Regular security audits

## 🔄 Maintenance

### Regular Tasks
1. **Monitor API Usage**: Check rate limits and quotas
2. **Review Reports**: Analyze AI-generated insights
3. **Update Prompts**: Refine AI instructions for better results
4. **Test Fallbacks**: Ensure all models work correctly

### Troubleshooting
1. **API Failures**: Check individual API key status
2. **Workflow Errors**: Review GitHub Actions logs
3. **Model Issues**: Test each AI model separately
4. **Performance**: Optimize workflow scheduling

## 📞 Support

For issues with the AI workflow system:

1. **Check GitHub Actions Logs**: Review workflow execution details
2. **Verify API Keys**: Ensure all 6 keys are properly configured
3. **Test Scripts Locally**: Run scripts with environment variables
4. **Review Documentation**: Check this guide for configuration details

---

*This comprehensive AI workflow system provides enterprise-grade intelligence automation for your AMAS project, leveraging 6 different AI models with intelligent fallback capabilities.*