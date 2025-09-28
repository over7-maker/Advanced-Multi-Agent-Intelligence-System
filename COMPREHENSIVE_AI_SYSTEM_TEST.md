# 🧪 COMPREHENSIVE AI SYSTEM TESTING GUIDE

## 🎯 **Complete Testing Protocol for AMAS AI Workflow System**

### **Phase 1: Pre-Testing Verification**

#### **1.1 System Structure Verification**
```bash
# Check all workflow files exist
ls -la .github/workflows/
# Should show 12 workflow files

# Check all AI scripts exist  
ls -la .github/scripts/
# Should show 12 AI script files
```

#### **1.2 Workflow Configuration Check**
- ✅ All workflows have proper triggers
- ✅ All jobs have simplified conditions (no skipped jobs)
- ✅ All 6 API keys configured in workflow files
- ✅ Dependencies properly specified

#### **1.3 API Key Configuration Status**
**Required GitHub Secrets:**
- `DEEPSEEK_API_KEY` - Status: ⚠️ Needs configuration
- `GLM_API_KEY` - Status: ⚠️ Needs configuration  
- `GROK_API_KEY` - Status: ⚠️ Needs configuration
- `KIMI_API_KEY` - Status: ⚠️ Needs configuration
- `QWEN_API_KEY` - Status: ⚠️ Needs configuration
- `GPTOSS_API_KEY` - Status: ⚠️ Needs configuration

### **Phase 2: Local System Testing**

#### **2.1 Python Environment Test**
```bash
# Test Python availability
python3 --version
# Should show Python 3.11 or higher

# Test basic functionality
python3 -c "print('✅ Python environment ready')"
```

#### **2.2 Workflow File Validation**
```bash
# Validate YAML syntax for all workflows
for file in .github/workflows/*.yml; do
    echo "Testing $file..."
    python3 -c "import yaml; yaml.safe_load(open('$file'))" && echo "✅ Valid" || echo "❌ Invalid"
done
```

#### **2.3 AI Script Syntax Check**
```bash
# Check Python syntax for all AI scripts
for file in .github/scripts/*.py; do
    echo "Testing $file..."
    python3 -m py_compile "$file" && echo "✅ Valid" || echo "❌ Invalid"
done
```

### **Phase 3: GitHub Actions Testing**

#### **3.1 Manual Workflow Dispatch Test**
**Steps:**
1. Go to GitHub repository Actions tab
2. Find "Test AI Workflow"
3. Click "Run workflow"
4. Select "main" branch
5. Click "Run workflow"
6. Monitor execution in real-time

**Expected Results:**
- ✅ All steps complete successfully
- ✅ No skipped jobs
- ✅ Test report generated
- ✅ API key status displayed

#### **3.2 AI Enhanced Workflow Test**
**Steps:**
1. Go to Actions tab
2. Find "AI-Enhanced Development Workflow"
3. Click "Run workflow"
4. Monitor all 3 jobs execution

**Expected Results:**
- ✅ `ai-code-analysis` job runs
- ✅ `ai-issue-responder` job runs  
- ✅ `multi-agent-analysis` job runs
- ✅ No jobs skipped
- ✅ Reports generated

#### **3.3 Event-Driven Workflow Test**
**Test Pull Request:**
1. Create new branch: `test-ai-workflow`
2. Make small change to any file
3. Create pull request
4. Check Actions tab for triggered workflows

**Test Issue Creation:**
1. Go to Issues tab
2. Create new issue with title: "Test AI Response"
3. Add description: "Testing automated AI issue response"
4. Submit issue
5. Check for AI-generated response

### **Phase 4: API Integration Testing**

#### **4.1 API Key Validation Test**
```python
# Test script to validate API key format
import os
import re

def validate_api_key(key_name, key_value):
    """Validate API key format"""
    if not key_value:
        return f"❌ {key_name}: Not configured"
    
    # Check for common API key patterns
    if key_name == "DEEPSEEK_API_KEY":
        if key_value.startswith("sk-"):
            return f"✅ {key_name}: Valid format"
        else:
            return f"⚠️ {key_name}: Invalid format"
    
    if "OPENROUTER" in key_name or key_name in ["GLM_API_KEY", "GROK_API_KEY", "KIMI_API_KEY", "QWEN_API_KEY", "GPTOSS_API_KEY"]:
        if key_value.startswith("sk-or-v1-"):
            return f"✅ {key_name}: Valid format"
        else:
            return f"⚠️ {key_name}: Invalid format"
    
    return f"✅ {key_name}: Configured"

# Test all API keys
api_keys = {
    'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
    'GLM_API_KEY': os.getenv('GLM_API_KEY'),
    'GROK_API_KEY': os.getenv('GROK_API_KEY'),
    'KIMI_API_KEY': os.getenv('KIMI_API_KEY'),
    'QWEN_API_KEY': os.getenv('QWEN_API_KEY'),
    'GPTOSS_API_KEY': os.getenv('GPTOSS_API_KEY')
}

for key_name, key_value in api_keys.items():
    print(validate_api_key(key_name, key_value))
```

#### **4.2 AI Client Connection Test**
```python
# Test AI client connections
from openai import OpenAI

def test_ai_client(client_name, base_url, api_key, model):
    """Test AI client connection"""
    try:
        client = OpenAI(base_url=base_url, api_key=api_key)
        # Simple test request
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        return f"✅ {client_name}: Connection successful"
    except Exception as e:
        return f"❌ {client_name}: Connection failed - {str(e)[:50]}"

# Test all AI clients
clients = [
    ("DeepSeek", "https://api.deepseek.com/v1", os.getenv('DEEPSEEK_API_KEY'), "deepseek-chat"),
    ("GLM", "https://openrouter.ai/api/v1", os.getenv('GLM_API_KEY'), "z-ai/glm-4.5-air:free"),
    ("Grok", "https://openrouter.ai/api/v1", os.getenv('GROK_API_KEY'), "x-ai/grok-4-fast:free"),
    ("Kimi", "https://openrouter.ai/api/v1", os.getenv('KIMI_API_KEY'), "moonshot/moonshot-v1-8k:free"),
    ("Qwen", "https://openrouter.ai/api/v1", os.getenv('QWEN_API_KEY'), "qwen/qwen-2.5-7b-instruct:free"),
    ("GPTOSS", "https://openrouter.ai/api/v1", os.getenv('GPTOSS_API_KEY'), "openai/gpt-3.5-turbo:free")
]

for client_name, base_url, api_key, model in clients:
    if api_key:
        print(test_ai_client(client_name, base_url, api_key, model))
    else:
        print(f"⚠️ {client_name}: No API key configured")
```

### **Phase 5: Comprehensive System Test**

#### **5.1 Full Workflow Execution Test**
**Test All 12 Workflows:**

1. **ai-enhanced-workflow** - Main comprehensive workflow
2. **test-ai-workflow** - Testing and verification
3. **ai-code-analysis** - Code analysis workflow
4. **ai-issue-responder** - Issue response workflow
5. **multi-agent-workflow** - Multi-agent intelligence
6. **ai-osint-collection** - OSINT data collection
7. **ai-threat-intelligence** - Threat intelligence
8. **ai-incident-response** - Incident response
9. **ai-adaptive-prompt-improvement** - Prompt optimization
10. **ai-enhanced-code-review** - Enhanced code review
11. **ai-master-orchestrator** - Master coordination
12. **ai-security-response** - Security response

**For each workflow:**
- Trigger manually via GitHub Actions
- Monitor execution in real-time
- Verify all jobs run (no skipped jobs)
- Check for generated reports/artifacts
- Validate AI responses and outputs

#### **5.2 Multi-Agent System Test**
**Test AI Model Fallback:**
1. Configure only 1 API key initially
2. Run workflow - should use available model
3. Add second API key
4. Run workflow - should use primary model
5. Add all 6 API keys
6. Run workflow - should use intelligent fallback

#### **5.3 Security System Test**
**Test Security Features:**
1. Run security scanner on test files
2. Verify false positive prevention
3. Test security response automation
4. Validate threat intelligence reports
5. Check incident response automation

### **Phase 6: Performance and Reliability Testing**

#### **6.1 Performance Metrics**
- **Workflow Execution Time**: Monitor completion times
- **API Response Time**: Track AI model response times
- **Success Rate**: Monitor successful vs failed executions
- **Resource Usage**: Check CPU and memory usage

#### **6.2 Reliability Testing**
- **Concurrent Execution**: Run multiple workflows simultaneously
- **Error Handling**: Test with invalid inputs
- **Fallback System**: Test with API failures
- **Recovery**: Test system recovery from errors

### **Phase 7: Integration Testing**

#### **7.1 Cross-Workflow Integration**
- **Trigger Chains**: Test workflows triggering other workflows
- **Data Flow**: Verify data passing between workflows
- **State Management**: Check workflow state consistency
- **Dependency Resolution**: Test workflow dependencies

#### **7.2 External Integration**
- **GitHub API**: Test GitHub API interactions
- **AI APIs**: Test all 6 AI model integrations
- **File System**: Test file operations and artifacts
- **Notifications**: Test workflow notifications

## 📊 **Testing Results Documentation**

### **Test Results Template:**
```
# 🧪 AI System Test Results

## Test Date: [DATE]
## Tester: [NAME]
## Repository: [REPO_URL]

### Phase 1: Pre-Testing Verification
- [ ] System structure verified
- [ ] Workflow configuration checked
- [ ] API key status confirmed

### Phase 2: Local System Testing
- [ ] Python environment tested
- [ ] Workflow files validated
- [ ] AI scripts syntax checked

### Phase 3: GitHub Actions Testing
- [ ] Manual workflow dispatch successful
- [ ] AI enhanced workflow tested
- [ ] Event-driven workflows tested

### Phase 4: API Integration Testing
- [ ] API keys validated
- [ ] AI client connections tested
- [ ] Multi-model fallback verified

### Phase 5: Comprehensive System Test
- [ ] All 12 workflows tested
- [ ] Multi-agent system verified
- [ ] Security system tested

### Phase 6: Performance Testing
- [ ] Performance metrics recorded
- [ ] Reliability testing completed
- [ ] Error handling verified

### Phase 7: Integration Testing
- [ ] Cross-workflow integration tested
- [ ] External integrations verified
- [ ] System consistency confirmed

## Overall Result: [PASS/FAIL]
## Issues Found: [LIST]
## Recommendations: [LIST]
```

## 🎯 **Testing Execution Plan**

### **Immediate Actions:**
1. **Configure API Keys** in GitHub Secrets
2. **Run Test AI Workflow** manually
3. **Verify No Skipped Jobs** in execution
4. **Check Generated Reports** and artifacts
5. **Test Event-Driven Workflows** with PR/Issue creation

### **Comprehensive Testing:**
1. **Test All 12 Workflows** individually
2. **Verify Multi-Agent System** with fallback
3. **Test Security Features** and false positive prevention
4. **Monitor Performance** and reliability
5. **Validate Integration** between workflows

### **Success Criteria:**
- ✅ All workflows execute without skipped jobs
- ✅ AI responses are generated and relevant
- ✅ Reports and artifacts are created
- ✅ Multi-agent fallback system works
- ✅ Security features operate correctly
- ✅ Performance meets expectations

## 🚀 **Ready for Testing!**

**Your AMAS AI Workflow System is ready for comprehensive testing!**

**Next Steps:**
1. Configure the 6 API keys in GitHub Secrets
2. Run the testing protocol above
3. Document results and any issues
4. Optimize based on test results

**The system will provide enterprise-grade AI automation once fully tested and configured!** 🎉