#!/usr/bin/env python3
"""
Test script to verify GitHub Actions workflows are properly configured
"""

import os
import sys
import json
import requests
from pathlib import Path

def check_workflow_files():
    """Check if all workflow files exist"""
    print("🔍 Checking workflow files...")
    
    workflow_dir = Path(".github/workflows")
    required_workflows = [
        "ai-code-analysis.yml",
        "ai-issue-responder.yml", 
        "enhanced-ai-integration.yml",
        "multi-agent-workflow.yml",
        "workflow-status-monitor.yml"
    ]
    
    missing_files = []
    for workflow in required_workflows:
        workflow_path = workflow_dir / workflow
        if workflow_path.exists():
            print(f"  ✅ {workflow}")
        else:
            print(f"  ❌ {workflow} - MISSING")
            missing_files.append(workflow)
    
    return len(missing_files) == 0, missing_files

def check_script_files():
    """Check if all Python scripts exist"""
    print("\n🔍 Checking Python scripts...")
    
    scripts_dir = Path(".github/scripts")
    required_scripts = [
        "ai_code_analyzer.py",
        "ai_issue_responder.py",
        "ai_security_scanner.py",
        "multi_agent_orchestrator.py",
        "issue_resolution_integrator.py",
        "workflow_status_checker.py"
    ]
    
    missing_scripts = []
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script} - MISSING")
            missing_scripts.append(script)
    
    return len(missing_scripts) == 0, missing_scripts

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        "GITHUB_TOKEN",
        "OPENROUTER_API_KEY", 
        "DEEPSEEK_API_KEY"
    ]
    
    optional_vars = [
        "GLM_API_KEY",
        "GROK_API_KEY"
    ]
    
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

def check_workflow_syntax():
    """Check workflow YAML syntax"""
    print("\n🔍 Checking workflow syntax...")
    
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

def check_python_scripts():
    """Check Python script syntax"""
    print("\n🔍 Checking Python script syntax...")
    
    scripts_dir = Path(".github/scripts")
    syntax_errors = []
    
    for script_file in scripts_dir.glob("*.py"):
        try:
            with open(script_file, 'r') as f:
                compile(f.read(), str(script_file), 'exec')
            print(f"  ✅ {script_file.name}")
        except SyntaxError as e:
            print(f"  ❌ {script_file.name} - SYNTAX ERROR: {e}")
            syntax_errors.append(str(script_file))
        except Exception as e:
            print(f"  ❌ {script_file.name} - ERROR: {e}")
            syntax_errors.append(str(script_file))
    
    return len(syntax_errors) == 0, syntax_errors

def test_api_connectivity():
    """Test API connectivity"""
    print("\n🔍 Testing API connectivity...")
    
    # Test OpenRouter API
    openrouter_key = os.environ.get('OPENROUTER_API_KEY')
    if openrouter_key:
        try:
            headers = {
                'Authorization': f'Bearer {openrouter_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get('https://openrouter.ai/api/v1/models', headers=headers, timeout=10)
            if response.status_code == 200:
                print("  ✅ OpenRouter API - Connected")
            else:
                print(f"  ❌ OpenRouter API - Error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ OpenRouter API - Connection failed: {e}")
    else:
        print("  ⚠️ OpenRouter API - No key provided")
    
    # Test DeepSeek API
    deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
    if deepseek_key:
        try:
            headers = {
                'Authorization': f'Bearer {deepseek_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get('https://api.deepseek.com/v1/models', headers=headers, timeout=10)
            if response.status_code == 200:
                print("  ✅ DeepSeek API - Connected")
            else:
                print(f"  ❌ DeepSeek API - Error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ DeepSeek API - Connection failed: {e}")
    else:
        print("  ⚠️ DeepSeek API - No key provided")

def generate_report():
    """Generate comprehensive test report"""
    print("="*60)
    print("🤖 GITHUB ACTIONS WORKFLOW TEST REPORT")
    print("="*60)
    
    # Check workflow files
    workflows_ok, missing_workflows = check_workflow_files()
    
    # Check script files
    scripts_ok, missing_scripts = check_script_files()
    
    # Check environment variables
    env_ok, missing_required, missing_optional = check_environment_variables()
    
    # Check workflow syntax
    workflow_syntax_ok, workflow_errors = check_workflow_syntax()
    
    # Check Python syntax
    python_syntax_ok, python_errors = check_python_scripts()
    
    # Test API connectivity
    test_api_connectivity()
    
    # Generate summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    total_checks = 5
    passed_checks = 0
    
    if workflows_ok:
        print("✅ Workflow files: PASSED")
        passed_checks += 1
    else:
        print(f"❌ Workflow files: FAILED - Missing: {missing_workflows}")
    
    if scripts_ok:
        print("✅ Script files: PASSED")
        passed_checks += 1
    else:
        print(f"❌ Script files: FAILED - Missing: {missing_scripts}")
    
    if env_ok:
        print("✅ Environment variables: PASSED")
        passed_checks += 1
    else:
        print(f"❌ Environment variables: FAILED - Missing: {missing_required}")
    
    if workflow_syntax_ok:
        print("✅ Workflow syntax: PASSED")
        passed_checks += 1
    else:
        print(f"❌ Workflow syntax: FAILED - Errors: {workflow_errors}")
    
    if python_syntax_ok:
        print("✅ Python syntax: PASSED")
        passed_checks += 1
    else:
        print(f"❌ Python syntax: FAILED - Errors: {python_errors}")
    
    print(f"\n🎯 Overall Score: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("🎉 All checks passed! Your workflows are ready to use.")
    else:
        print("⚠️ Some checks failed. Please fix the issues above.")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if missing_optional:
        print(f"- Consider adding optional API keys: {missing_optional}")
    print("- Test workflows by creating a test issue")
    print("- Monitor workflow runs in the Actions tab")
    print("- Review the setup guide for detailed instructions")
    
    return passed_checks == total_checks

if __name__ == "__main__":
    try:
        success = generate_report()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)