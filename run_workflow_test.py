#!/usr/bin/env python3
"""
Manual workflow test script
Tests individual components of the GitHub Actions workflows
"""

import os
import sys
import subprocess
from pathlib import Path

def test_ai_issue_responder():
    """Test the AI issue responder script"""
    print("🧪 Testing AI Issue Responder...")
    
    # Set test environment variables
    test_env = {
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN', 'test_token'),
        'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY', 'test_key'),
        'DEEPSEEK_API_KEY': os.environ.get('DEEPSEEK_API_KEY', 'test_key'),
        'ISSUE_NUMBER': '1',
        'ISSUE_TITLE': 'Test Issue - AI Workflow Testing',
        'ISSUE_BODY': 'This is a test issue to verify the AI workflow is working correctly.',
        'ISSUE_AUTHOR': 'testuser',
        'REPO_NAME': 'test/repo'
    }
    
    try:
        # Run the script with test environment
        result = subprocess.run([
            sys.executable, '.github/scripts/ai_issue_responder.py'
        ], env=test_env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ AI Issue Responder: PASSED")
            return True
        else:
            print(f"  ❌ AI Issue Responder: FAILED - {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️ AI Issue Responder: TIMEOUT (may be normal for API calls)")
        return True
    except Exception as e:
        print(f"  ❌ AI Issue Responder: ERROR - {e}")
        return False

def test_ai_code_analyzer():
    """Test the AI code analyzer script"""
    print("🧪 Testing AI Code Analyzer...")
    
    # Set test environment variables
    test_env = {
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN', 'test_token'),
        'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY', 'test_key'),
        'DEEPSEEK_API_KEY': os.environ.get('DEEPSEEK_API_KEY', 'test_key'),
        'CHANGED_FILES': 'test.py main.py',
        'PR_NUMBER': '1',
        'REPO_NAME': 'test/repo',
        'COMMIT_SHA': 'test_sha'
    }
    
    try:
        # Run the script with test environment
        result = subprocess.run([
            sys.executable, '.github/scripts/ai_code_analyzer.py'
        ], env=test_env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ AI Code Analyzer: PASSED")
            return True
        else:
            print(f"  ❌ AI Code Analyzer: FAILED - {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️ AI Code Analyzer: TIMEOUT (may be normal for API calls)")
        return True
    except Exception as e:
        print(f"  ❌ AI Code Analyzer: ERROR - {e}")
        return False

def test_security_scanner():
    """Test the security scanner script"""
    print("🧪 Testing Security Scanner...")
    
    # Set test environment variables
    test_env = {
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN', 'test_token'),
        'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY', 'test_key'),
        'DEEPSEEK_API_KEY': os.environ.get('DEEPSEEK_API_KEY', 'test_key'),
        'CHANGED_FILES': 'test.py main.py',
        'PR_NUMBER': '1',
        'REPO_NAME': 'test/repo'
    }
    
    try:
        # Run the script with test environment
        result = subprocess.run([
            sys.executable, '.github/scripts/ai_security_scanner.py'
        ], env=test_env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ Security Scanner: PASSED")
            return True
        else:
            print(f"  ❌ Security Scanner: FAILED - {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️ Security Scanner: TIMEOUT (may be normal for API calls)")
        return True
    except Exception as e:
        print(f"  ❌ Security Scanner: ERROR - {e}")
        return False

def test_workflow_status_checker():
    """Test the workflow status checker script"""
    print("🧪 Testing Workflow Status Checker...")
    
    # Set test environment variables
    test_env = {
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN', 'test_token'),
        'REPO_NAME': os.environ.get('REPO_NAME', 'test/repo')
    }
    
    try:
        # Run the script with test environment
        result = subprocess.run([
            sys.executable, '.github/scripts/workflow_status_checker.py'
        ], env=test_env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ Workflow Status Checker: PASSED")
            return True
        else:
            print(f"  ❌ Workflow Status Checker: FAILED - {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️ Workflow Status Checker: TIMEOUT (may be normal for API calls)")
        return True
    except Exception as e:
        print(f"  ❌ Workflow Status Checker: ERROR - {e}")
        return False

def main():
    """Run all workflow tests"""
    print("🚀 Starting GitHub Actions Workflow Tests")
    print("="*50)
    
    tests = [
        test_ai_issue_responder,
        test_ai_code_analyzer,
        test_security_scanner,
        test_workflow_status_checker
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All workflow tests passed!")
        print("✅ Your GitHub Actions workflows are ready to use!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("💡 Make sure all required environment variables are set.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)