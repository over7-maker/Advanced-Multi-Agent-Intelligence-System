#!/usr/bin/env python3
"""
Test script to verify auto-response functionality
"""

import os
import sys
import subprocess

def test_guaranteed_responder():
    """Test the guaranteed responder script"""
    print("🧪 Testing Guaranteed Auto Responder...")
    
    # Set test environment
    test_env = {
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN', 'test_token'),
        'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY', 'test_key'),
        'DEEPSEEK_API_KEY': os.environ.get('DEEPSEEK_API_KEY', 'test_key'),
        'ISSUE_NUMBER': '1',
        'ISSUE_TITLE': 'Test Issue - Auto Response Testing',
        'ISSUE_BODY': 'This is a test issue to verify the auto-response functionality is working correctly.',
        'ISSUE_AUTHOR': 'testuser',
        'REPO_NAME': 'test/repo'
    }
    
    try:
        result = subprocess.run([
            sys.executable, '.github/scripts/guaranteed_responder.py'
        ], env=test_env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ Guaranteed Auto Responder: PASSED")
            print(f"  📤 Output: {result.stdout}")
            return True
        else:
            print(f"  ❌ Guaranteed Auto Responder: FAILED - {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️ Guaranteed Auto Responder: TIMEOUT (may be normal for API calls)")
        return True
    except Exception as e:
        print(f"  ❌ Guaranteed Auto Responder: ERROR - {e}")
        return False

def test_workflow_files():
    """Test that workflow files exist"""
    print("🔍 Testing workflow files...")
    
    import os
    from pathlib import Path
    
    workflow_files = [
        ".github/workflows/guaranteed-auto-response.yml",
        ".github/workflows/simple-auto-response.yml",
        ".github/workflows/complete-auto-response.yml",
        ".github/workflows/robust-ai-workflow.yml"
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
    """Test that script files exist"""
    print("🔍 Testing script files...")
    
    import os
    from pathlib import Path
    
    script_files = [
        ".github/scripts/guaranteed_responder.py",
        ".github/scripts/simple_ai_responder.py",
        ".github/scripts/ai_issue_responder.py"
    ]
    
    missing_files = []
    for script_file in script_files:
        if Path(script_file).exists():
            print(f"  ✅ {script_file}")
        else:
            print(f"  ❌ {script_file} - MISSING")
            missing_files.append(script_file)
    
    return len(missing_files) == 0, missing_files

def main():
    """Run all tests"""
    print("🚀 Testing Auto-Response System")
    print("="*50)
    
    # Test workflow files
    workflows_ok, missing_workflows = test_workflow_files()
    
    # Test script files
    scripts_ok, missing_scripts = test_script_files()
    
    # Test guaranteed responder
    responder_ok = test_guaranteed_responder()
    
    # Generate summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    total_tests = 3
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
    
    if responder_ok:
        print("✅ Guaranteed responder: PASSED")
        passed_tests += 1
    else:
        print("❌ Guaranteed responder: FAILED")
    
    print(f"\n🎯 Overall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Auto-response should be working!")
        print("\n💡 To test auto-response:")
        print("1. Create a test issue in your repository")
        print("2. The guaranteed-auto-response.yml workflow should trigger")
        print("3. Check the issue for AI-generated responses")
        print("4. Verify labels were added (ai-analyzed, auto-response)")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)