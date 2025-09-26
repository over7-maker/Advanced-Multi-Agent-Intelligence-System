#!/usr/bin/env python3
"""
Test script to verify AI workflow scripts work correctly
"""

import os
import sys

# Add the scripts directory to the path
sys.path.append('.github/scripts')

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        from openai import OpenAI
        print("✅ openai imported successfully")
    except ImportError as e:
        print(f"❌ openai import failed: {e}")
        return False
    
    try:
        import json
        print("✅ json imported successfully")
    except ImportError as e:
        print(f"❌ json import failed: {e}")
        return False
    
    return True

def test_script_structure():
    """Test if the script files can be loaded"""
    scripts = [
        '.github/scripts/ai_code_analyzer.py',
        '.github/scripts/ai_issue_responder.py', 
        '.github/scripts/ai_security_scanner.py',
        '.github/scripts/multi_agent_orchestrator.py'
    ]
    
    for script in scripts:
        try:
            with open(script, 'r') as f:
                content = f.read()
            print(f"✅ {script} can be read")
        except Exception as e:
            print(f"❌ {script} read failed: {e}")
            return False
    
    return True

def test_environment_variables():
    """Test environment variable handling"""
    # Set test environment variables
    os.environ['DEEPSEEK_API_KEY'] = 'test-key'
    os.environ['GLM_API_KEY'] = 'test-key'
    os.environ['GROK_API_KEY'] = 'test-key'
    os.environ['GITHUB_TOKEN'] = 'test-token'
    os.environ['REPO_NAME'] = 'test/repo'
    os.environ['CHANGED_FILES'] = 'test.py'
    
    try:
        from ai_code_analyzer import AICodeAnalyzer
        analyzer = AICodeAnalyzer()
        print(f"✅ AICodeAnalyzer initialized with {len(analyzer.ai_clients)} clients")
        
        from ai_issue_responder import AIIssueResponder
        responder = AIIssueResponder()
        print(f"✅ AIIssueResponder initialized with {len(responder.ai_clients)} clients")
        
        from ai_security_scanner import AISecurityScanner
        scanner = AISecurityScanner()
        print(f"✅ AISecurityScanner initialized with {len(scanner.ai_clients)} clients")
        
        return True
    except Exception as e:
        print(f"❌ Script initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AI Workflow Scripts...")
    print("=" * 50)
    
    print("\n1. Testing imports...")
    if not test_imports():
        print("❌ Import test failed")
        sys.exit(1)
    
    print("\n2. Testing script structure...")
    if not test_script_structure():
        print("❌ Script structure test failed")
        sys.exit(1)
    
    print("\n3. Testing environment variables...")
    if not test_environment_variables():
        print("❌ Environment variable test failed")
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    print("🎉 AI workflow scripts are ready to use!")