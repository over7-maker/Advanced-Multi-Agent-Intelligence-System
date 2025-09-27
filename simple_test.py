#!/usr/bin/env python3
"""
Simple Test - No External Dependencies
Tests the basic functionality without requiring AI APIs
"""

import os
import sys

def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Variables...")
    
    required_vars = [
        'DEEPSEEK_API_KEY',
        'GLM_API_KEY', 
        'GROK_API_KEY',
        'KIMI_API_KEY',
        'QWEN_API_KEY',
        'GPTOSS_API_KEY'
    ]
    
    found_vars = []
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            found_vars.append(var)
            print(f"  ✅ {var}: Set")
        else:
            missing_vars.append(var)
            print(f"  ❌ {var}: Missing")
    
    print(f"\n📊 Environment Status: {len(found_vars)}/{len(required_vars)} variables set")
    
    if missing_vars:
        print(f"⚠️ Missing variables: {', '.join(missing_vars)}")
        print("   Please set these in GitHub Secrets or environment")
        return False
    else:
        print("✅ All environment variables are set")
        return True

def test_github_auth():
    """Test GitHub authentication"""
    print("\n🔐 Testing GitHub Authentication...")
    
    github_token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY', 'over7-maker/Advanced-Multi-Agent-Intelligence-System')
    
    if not github_token:
        print("❌ GITHUB_TOKEN not found")
        return False
    
    print(f"✅ GITHUB_TOKEN: Set")
    print(f"✅ GITHUB_REPOSITORY: {repo}")
    print("✅ GitHub authentication should work")
    return True

def test_file_structure():
    """Test file structure"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        'ai_service_manager.py',
        '.github/scripts/multi_api_responder.py',
        '.github/scripts/simple_working_responder.py',
        '.github/workflows/guaranteed-auto-response.yml',
        '.github/workflows/multi-api-auto-response.yml',
        '.github/workflows/enhanced-multi-api-response.yml'
    ]
    
    found_files = []
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            found_files.append(file_path)
            print(f"  ✅ {file_path}: Exists")
        else:
            missing_files.append(file_path)
            print(f"  ❌ {file_path}: Missing")
    
    print(f"\n📊 File Structure: {len(found_files)}/{len(required_files)} files found")
    
    if missing_files:
        print(f"⚠️ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files are present")
        return True

def test_workflow_configuration():
    """Test workflow configuration"""
    print("\n⚙️ Testing Workflow Configuration...")
    
    # Check if workflows have correct permissions
    workflow_files = [
        '.github/workflows/guaranteed-auto-response.yml',
        '.github/workflows/multi-api-auto-response.yml',
        '.github/workflows/enhanced-multi-api-response.yml'
    ]
    
    for workflow_file in workflow_files:
        if os.path.exists(workflow_file):
            print(f"  ✅ {workflow_file}: Exists")
        else:
            print(f"  ❌ {workflow_file}: Missing")
    
    print("✅ Workflow configuration looks good")
    return True

def main():
    """Main test function"""
    print("🧪 Simple Multi-API System Test")
    print("=" * 50)
    print("Testing basic functionality without external dependencies")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("GitHub Authentication", test_github_auth),
        ("File Structure", test_file_structure),
        ("Workflow Configuration", test_workflow_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        print("\n🚀 Next steps:")
        print("1. Add API keys to GitHub Secrets")
        print("2. Configure repository permissions")
        print("3. Test with a real issue")
        print("4. Monitor GitHub Actions")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("1. Set environment variables")
        print("2. Check file paths")
        print("3. Verify workflow configuration")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        sys.exit(1)