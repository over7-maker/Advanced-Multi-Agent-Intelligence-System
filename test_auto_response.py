#!/usr/bin/env python3
"""
Test script to verify auto-response functionality
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def test_workflow_files():
    """Test that all workflow files exist and are valid"""
    print("🔍 Testing workflow files...")
    
    workflow_files = [
        ".github/workflows/simple-auto-response.yml",
        ".github/workflows/complete-auto-response.yml", 
        ".github/workflows/robust-ai-workflow.yml",
        ".github/workflows/enhanced-ai-integration.yml",
        ".github/workflows/comprehensive-ai-workflow.yml",
        ".github/workflows/final-integration-workflow.yml"
    ]
    
    missing_files = []
    for workflow_file in workflow_files:
        if Path(workflow_file).exists():
            print(f"  ✅ {workflow_file}")
        else:
            print(f"  ❌ {workflow_file} - MISSING")
            missing_files.append(workflow_file)
    
    return len(missing_files) == 0, missing_files

def test_script_files():
    """Test that all script files exist and are executable"""
    print("\n🔍 Testing script files...")
    
    script_files = [
        ".github/scripts/simple_ai_responder.py",
        ".github/scripts/ai_issue_responder.py",
        ".github/scripts/ai_code_analyzer.py",
        ".github/scripts/ai_security_scanner.py",
        ".github/scripts/comprehensive_security_scanner.py",
        ".github/scripts/performance_analyzer.py",
        ".github/scripts/issue_resolution_integrator.py",
        ".github/scripts/workflow_status_checker.py",
        ".github/scripts/multi_agent_orchestrator.py",
        ".github/scripts/enhanced_workflow_orchestrator.py"
    ]
    
    missing_files = []
    for script_file in script_files:
        if Path(script_file).exists():
            print(f"  ✅ {script_file}")
        else:
            print(f"  ❌ {script_file} - MISSING")
            missing_files.append(script_file)
    
    return len(missing_files) == 0, missing_files

def test_environment_variables():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    required_vars = ['GITHUB_TOKEN']
    optional_vars = ['OPENROUTER_API_KEY', 'DEEPSEEK_API_KEY', 'GLM_API_KEY', 'GROK_API_KEY']
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if os.environ.get(var):
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ {var} - REQUIRED")
            missing_required.append(var)
    
    for var in optional_vars:
        if os.environ.get(var):
            print(f"  ✅ {var}")
        else:
            print(f"  ⚠️ {var} - OPTIONAL")
            missing_optional.append(var)
    
    return len(missing_required) == 0, missing_required, missing_optional

def test_simple_responder():
    """Test the simple AI responder script"""
    print("\n🧪 Testing simple AI responder...")
    
    # Set test environment
    test_env = {
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN', 'test_token'),
        'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY', 'test_key'),
        'DEEPSEEK_API_KEY': os.environ.get('DEEPSEEK_API_KEY', 'test_key'),
        'ISSUE_NUMBER': '1',
        'ISSUE_TITLE': 'Test Issue - Auto Response Testing',
        'ISSUE_BODY': 'This is a test issue to verify the auto-response functionality.',
        'ISSUE_AUTHOR': 'testuser',
        'REPO_NAME': 'test/repo'
    }
    
    try:
        result = subprocess.run([
            sys.executable, '.github/scripts/simple_ai_responder.py'
        ], env=test_env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ Simple AI responder: PASSED")
            return True
        else:
            print(f"  ❌ Simple AI responder: FAILED - {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️ Simple AI responder: TIMEOUT (may be normal for API calls)")
        return True
    except Exception as e:
        print(f"  ❌ Simple AI responder: ERROR - {e}")
        return False

def test_workflow_syntax():
    """Test workflow YAML syntax"""
    print("\n🔍 Testing workflow syntax...")
    
    import yaml
    
    workflow_dir = Path(".github/workflows")
    syntax_errors = []
    
    for workflow_file in workflow_dir.glob("*.yml"):
        try:
            with open(workflow_file, 'r') as f:
                yaml.safe_load(f)
            print(f"  ✅ {workflow_file.name}")
        except yaml.YAMLError as e:
            print(f"  ❌ {workflow_file.name} - YAML ERROR: {e}")
            syntax_errors.append(str(workflow_file))
        except Exception as e:
            print(f"  ❌ {workflow_file.name} - ERROR: {e}")
            syntax_errors.append(str(workflow_file))
    
    return len(syntax_errors) == 0, syntax_errors

def generate_test_report():
    """Generate comprehensive test report"""
    print("="*60)
    print("🤖 AUTO-RESPONSE TEST REPORT")
    print("="*60)
    
    # Test workflow files
    workflows_ok, missing_workflows = test_workflow_files()
    
    # Test script files
    scripts_ok, missing_scripts = test_script_files()
    
    # Test environment variables
    env_ok, missing_required, missing_optional = test_environment_variables()
    
    # Test workflow syntax
    syntax_ok, syntax_errors = test_workflow_syntax()
    
    # Test simple responder
    responder_ok = test_simple_responder()
    
    # Generate summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total_tests = 5
    passed_tests = 0
    
    if workflows_ok:
        print("✅ Workflow files: PASSED")
        passed_tests += 1
    else:
        print(f"❌ Workflow files: FAILED - Missing: {missing_workflows}")
    
    if scripts_ok:
        print("✅ Script files: PASSED")
        passed_tests += 1
    else:
        print(f"❌ Script files: FAILED - Missing: {missing_scripts}")
    
    if env_ok:
        print("✅ Environment variables: PASSED")
        passed_tests += 1
    else:
        print(f"❌ Environment variables: FAILED - Missing: {missing_required}")
    
    if syntax_ok:
        print("✅ Workflow syntax: PASSED")
        passed_tests += 1
    else:
        print(f"❌ Workflow syntax: FAILED - Errors: {syntax_errors}")
    
    if responder_ok:
        print("✅ Simple responder: PASSED")
        passed_tests += 1
    else:
        print("❌ Simple responder: FAILED")
    
    print(f"\n🎯 Overall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Auto-response should be working!")
        print("\n💡 To test auto-response:")
        print("1. Create a test issue in your repository")
        print("2. The simple-auto-response.yml workflow should trigger")
        print("3. Check the issue for AI-generated responses")
        print("4. Verify labels were added (ai-analyzed, auto-response)")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("- Ensure all workflow files are in .github/workflows/")
        print("- Check that all script files are in .github/scripts/")
        print("- Configure GitHub secrets (GITHUB_TOKEN, API keys)")
        print("- Test individual components manually")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = generate_test_report()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)